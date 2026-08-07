"""
Semantic classifier using Claude Haiku.
Called ONLY when deterministic pre-filter finds candidates AND hash changed.
"""
import json
import os
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

try:
    import anthropic
    _ANTHROPIC_AVAILABLE = True
except ImportError:
    _ANTHROPIC_AVAILABLE = False
    logger.warning("anthropic SDK not installed. Install with: pip install anthropic")

_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "monitoring-rules.yaml"

# Model from env or config default
_MODEL = os.environ.get("CLASSIFIER_MODEL", "claude-haiku-4-5-20251001")

CLASSIFICATION_SCHEMA = {
    "type": "object",
    "required": ["relevant", "competitor", "items"],
    "properties": {
        "relevant": {"type": "boolean"},
        "competitor": {"type": "string"},
        "items": {
            "type": "array",
            "items": {
                "type": "object",
                "required": ["item_type", "data"],
                "properties": {
                    "item_type": {"type": "string", "enum": ["offer", "client", "case"]},
                    "data": {"type": "object"},
                }
            }
        }
    }
}


def _get_client():
    api_key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")
    if not _ANTHROPIC_AVAILABLE:
        raise RuntimeError("anthropic SDK not installed")
    return anthropic.Anthropic(api_key=api_key)


def classify_page_content(
    competitor_id: str,
    competitor_name: str,
    page_url: str,
    page_title: str,
    text_excerpt: str,
    candidate_solutions: list,
    page_type: str = "OFFERS",
) -> dict:
    """
    Send ONLY the relevant excerpt and candidate solutions to Haiku.
    Returns structured JSON or empty result on failure.
    """
    if not text_excerpt.strip():
        return {"relevant": False, "competitor": competitor_id, "items": []}

    # Truncate inputs to minimize tokens
    excerpt = text_excerpt[:3000]
    candidates_str = json.dumps(candidate_solutions[:10], ensure_ascii=False)

    system_prompt = """Você é um analista de inteligência competitiva especializado em cybersecurity e TI.
Analise o trecho de página de um concorrente e extraia informações estruturadas.
Responda SOMENTE com JSON válido, sem texto adicional.
Seja objetivo e conservador: não invente, não infira além da evidência.
Confidence: 0.9-1.0 = evidência explícita; 0.75-0.89 = evidência forte; 0.6-0.74 = inferência razoável. Abaixo de 0.6 não inclua."""

    user_prompt = f"""Concorrente: {competitor_name} ({competitor_id})
URL: {page_url}
Título: {page_title}
Tipo de página: {page_type}
Soluções Tripla candidatas para comparação: {candidates_str}

Trecho do conteúdo:
---
{excerpt}
---

Extraia um JSON com esta estrutura exata:
{{
  "relevant": true,
  "competitor": "{competitor_id}",
  "items": [
    {{
      "item_type": "offer",
      "data": {{
        "competitor_offer": "nome da oferta",
        "competitor_description": "descrição objetiva, máx 2 frases",
        "tripla_solution": "solução Tripla equivalente ou vazia",
        "tripla_pillar": "CONFORMIDADE|DISPONIBILIDADE|PROTEÇÃO|",
        "overlap": "TOTAL|PARCIAL|FORA_DE_PORTFOLIO|INDETERMINADO",
        "delivery_similarity": "descrição breve",
        "reason": "justificativa objetiva, máx 1 frase",
        "source_url": "{page_url}",
        "market_scope": "brazil|global_confirmed_br|global_unconfirmed_br",
        "confidence": 0.0
      }}
    }},
    {{
      "item_type": "client",
      "data": {{
        "name": "nome do cliente",
        "sector": "setor normalizado",
        "source_url": "{page_url}",
        "evidence_type": "case|testimonial|customer_story|logo_with_context",
        "confidence": 0.0
      }}
    }},
    {{
      "item_type": "case",
      "data": {{
        "client": "nome do cliente",
        "case_title": "título do case",
        "competitor_solution": "solução usada no case",
        "case_summary": "resumo objetivo, máx 1 frase",
        "tripla_equivalent_solution": "equivalente Tripla ou vazia",
        "overlap": "TOTAL|PARCIAL|FORA_DE_PORTFOLIO|INDETERMINADO",
        "source_url": "{page_url}",
        "published_at": null,
        "confidence": 0.0
      }}
    }}
  ]
}}

Regras:
- Inclua apenas itens com confidence >= 0.6
- Para Big4 (KPMG, PwC, Deloitte, EY): NÃO classifique consultoria como tecnologia
- Logo sem contexto claro NÃO é cliente confirmado
- Parceiro/fabricante NÃO é cliente
- FABRICANTE DIFERENTE não é motivo para PARCIAL se a capacidade for a mesma (use TOTAL)
- Se não houver nada relevante, retorne: {{"relevant": false, "competitor": "{competitor_id}", "items": []}}"""

    try:
        client = _get_client()
        response = client.messages.create(
            model=_MODEL,
            max_tokens=1024,
            temperature=0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = response.content[0].text.strip()

        # Extract JSON if wrapped in markdown code block
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]

        result = json.loads(raw)
        return result

    except json.JSONDecodeError as e:
        logger.error(f"JSON parse error from classifier: {e}")
        return {"relevant": False, "competitor": competitor_id, "items": [], "error": str(e)}
    except Exception as e:
        logger.error(f"Classifier error for {page_url}: {e}")
        return {"relevant": False, "competitor": competitor_id, "items": [], "error": str(e)}


def classify_change(
    competitor_id: str,
    competitor_name: str,
    page_url: str,
    watcher_type: str,
    diff_excerpt: str,
    baseline_context: str,
    candidate_solutions: list,
) -> dict:
    """
    Classify a detected change (diff). Called only when hash changed.
    Returns structured change analysis.
    """
    if not diff_excerpt.strip():
        return {"relevant": False, "competitor": competitor_id, "severity": "IGNORE"}

    candidates_str = json.dumps(candidate_solutions[:10], ensure_ascii=False)
    diff_trimmed = diff_excerpt[:3000]
    context_trimmed = baseline_context[:500]

    system_prompt = """Você é um analista de inteligência competitiva.
Analise APENAS a mudança detectada e classifique sua relevância competitiva.
Responda somente com JSON válido."""

    user_prompt = f"""Concorrente: {competitor_name}
URL: {page_url}
Watcher: {watcher_type}
Soluções Tripla candidatas: {candidates_str}

Contexto do baseline:
{context_trimmed}

Trecho alterado (diff):
{diff_trimmed}

Retorne:
{{
  "relevant": true,
  "competitor": "{competitor_id}",
  "change_type": "new_client|new_case|new_product|new_solution|new_offer|functional_change|scope_expansion|new_delivery_mode|offer_removed|case_removed|messaging_change|wording_change|layout_change|other",
  "severity": "HIGH|MEDIUM|LOW|IGNORE",
  "confidence": 0.0,
  "field": "campo afetado",
  "operation": "add|remove|modify",
  "tripla_solution": "solução Tripla afetada ou vazia",
  "overlap": "TOTAL|PARCIAL|FORA_DE_PORTFOLIO|INDETERMINADO",
  "previous_value": null,
  "proposed_value": {{}},
  "curator_summary": "resumo objetivo em 1 frase",
  "reason": "justificativa em 1 frase",
  "evidence": [{{"url": "{page_url}", "excerpt": "trecho curto"}}]
}}"""

    try:
        client = _get_client()
        response = client.messages.create(
            model=_MODEL,
            max_tokens=1024,
            temperature=0,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        raw = response.content[0].text.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"):
                raw = raw[4:]
        return json.loads(raw)
    except Exception as e:
        logger.error(f"Change classifier error: {e}")
        return {"relevant": False, "competitor": competitor_id,
                "severity": "IGNORE", "error": str(e)}

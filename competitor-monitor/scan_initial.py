"""
FASE B — Primeira varredura dos 15 concorrentes.
Gera baseline_candidates. NÃO gera alertas, NÃO aprova dados.

Uso:
  python scan_initial.py [--competitor-id <id>]

Pré-requisitos:
  FIRECRAWL_API_KEY=...
  ANTHROPIC_API_KEY=...
"""
import argparse
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

# Resolve project root
ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from src.crawl.fetcher import fetch_page, map_site
from src.crawl.url_filter import (
    is_relevant_url, classify_url_type, deduplicate_urls, is_homepage
)
from src.extract.normalizer import normalize
from src.extract.hasher import compute_hash
from src.extract.snapshot import save_snapshot
from src.classify.matcher import find_candidate_solutions, get_pillar
from src.classify.classifier import classify_page_content

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("scan_initial")

BASELINE_DIR = ROOT / "baseline" / "candidates"
BASELINE_DIR.mkdir(parents=True, exist_ok=True)
REPORTS_DIR = ROOT / "reports"
REPORTS_DIR.mkdir(exist_ok=True)

MAX_PAGES = 30  # per competitor


def load_competitors(competitor_id: str | None = None) -> list:
    data = json.loads((ROOT / "config" / "competitors.json").read_text())
    comps = data["competitors"]
    if competitor_id:
        comps = [c for c in comps if c["id"] == competitor_id]
    return comps


def discover_pages(competitor: dict) -> tuple[list, list]:
    """
    Discover relevant pages for a competitor.
    Returns (relevant_urls, errors).
    Strategy: map → filter → homepage fallback.
    """
    base_url = competitor["base_url"]
    comp_id = competitor["id"]
    errors = []

    logger.info(f"[{comp_id}] Mapping site {base_url}")
    mapped = map_site(base_url, limit=100)

    if not mapped:
        logger.info(f"[{comp_id}] map returned empty — falling back to homepage scrape")
        result = fetch_page(base_url)
        if result.success:
            mapped = result.links
        else:
            errors.append({"url": base_url, "error": result.error, "stage": "map_fallback"})
            return [], errors

    all_urls = [base_url] + mapped
    all_urls = deduplicate_urls(all_urls)

    relevant = [u for u in all_urls
                if is_homepage(u, base_url) or is_relevant_url(u, base_url)]
    relevant = relevant[:MAX_PAGES]

    logger.info(f"[{comp_id}] {len(relevant)} relevant URLs from {len(all_urls)} total")
    return relevant, errors


def process_competitor(competitor: dict) -> dict:
    comp_id = competitor["id"]
    comp_name = competitor["name"]
    comp_type = competitor.get("type", "")

    logger.info(f"{'='*60}")
    logger.info(f"Processing: {comp_name} ({comp_id})")

    result = {
        "competitor_id": comp_id,
        "competitor_name": comp_name,
        "baseline_status": "candidate",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "approved_at": None,
        "clients": [],
        "cases": [],
        "offers": [],
        "monitoring_urls": {"CLIENTS_CASES": [], "OFFERS": [], "NEWS_LAUNCHES": []},
        "collection_errors": [],
        "pages_analyzed": 0,
    }

    relevant_urls, errors = discover_pages(competitor)
    result["collection_errors"].extend(errors)

    if not relevant_urls:
        logger.warning(f"[{comp_id}] No pages to analyze")
        result["collection_errors"].append({
            "url": competitor["base_url"],
            "error": "No relevant pages discovered",
            "stage": "discovery",
        })
        return result

    seen_clients = set()
    seen_cases = set()
    seen_offers = set()

    for url in relevant_urls:
        logger.info(f"[{comp_id}] Fetching: {url}")
        fetch = fetch_page(url)

        if not fetch.success:
            result["collection_errors"].append({
                "url": url,
                "error": fetch.error,
                "stage": "fetch",
                "note": "Fetch failure — NOT treated as content removal",
            })
            continue

        if not fetch.markdown or len(fetch.markdown.strip()) < 100:
            logger.debug(f"[{comp_id}] {url} — too little content, skipping")
            continue

        result["pages_analyzed"] += 1

        # Normalize and snapshot
        normalized = normalize(fetch.markdown)
        content_hash = compute_hash(normalized)
        page_type = classify_url_type(url)

        save_snapshot(
            competitor_id=comp_id,
            url=url,
            content_hash=content_hash,
            normalized_text=normalized,
            title=fetch.title,
            watcher_type=page_type,
        )

        # Register for future monitoring
        mon_entry = {"url": url, "type": page_type, "reason": f"Discovered in initial scan — {fetch.title or url}"}
        existing_urls = [e["url"] for e in result["monitoring_urls"][page_type]]
        if url not in existing_urls:
            result["monitoring_urls"][page_type].append(mon_entry)

        # Deterministic pre-filter: find candidate Tripla solutions
        candidates = find_candidate_solutions(normalized)
        if not candidates and page_type == "OFFERS":
            # No keyword match — skip LLM for this page
            logger.debug(f"[{comp_id}] {url} — no keyword match, skipping LLM")
            continue

        # LLM classification (Haiku)
        classification = classify_page_content(
            competitor_id=comp_id,
            competitor_name=comp_name,
            page_url=url,
            page_title=fetch.title,
            text_excerpt=normalized,
            candidate_solutions=candidates,
            page_type=page_type,
        )

        if not classification.get("relevant"):
            continue

        for item in classification.get("items", []):
            item_type = item.get("item_type")
            data = item.get("data", {})
            confidence = data.get("confidence", 0)

            if confidence < 0.6:
                continue

            if item_type == "client":
                key = data.get("name", "").lower().strip()
                if key and key not in seen_clients:
                    seen_clients.add(key)
                    result["clients"].append(data)

            elif item_type == "case":
                key = f"{data.get('client','').lower()}|{data.get('case_title','').lower()}"
                if key and key not in seen_cases:
                    seen_cases.add(key)
                    # Ensure tripla_pillar is set
                    sol = data.get("tripla_equivalent_solution", "")
                    if sol:
                        data["tripla_pillar"] = get_pillar(sol)
                    result["cases"].append(data)

            elif item_type == "offer":
                key = data.get("competitor_offer", "").lower().strip()
                if key and key not in seen_offers:
                    seen_offers.add(key)
                    # Ensure tripla_pillar
                    sol = data.get("tripla_solution", "")
                    if sol and not data.get("tripla_pillar"):
                        data["tripla_pillar"] = get_pillar(sol)
                    result["offers"].append(data)

    logger.info(
        f"[{comp_id}] Done — pages: {result['pages_analyzed']}, "
        f"clients: {len(result['clients'])}, cases: {len(result['cases'])}, "
        f"offers: {len(result['offers'])}"
    )
    return result


def save_baseline_candidate(result: dict):
    path = BASELINE_DIR / f"{result['competitor_id']}.json"
    path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    logger.info(f"Saved candidate: {path}")


def generate_report(results: list):
    """Generate initial-review.md for human curation."""
    lines = []
    lines.append("# Relatório de Revisão Inicial — Inteligência Competitiva")
    lines.append(f"\nGerado em: {datetime.now(timezone.utc).isoformat()}")
    lines.append("\n> **Status**: Todos os dados são `baseline_status = candidate`.")
    lines.append("> Revise concorrente por concorrente e devolva os dados aprovados.\n")
    lines.append("---\n")

    for r in results:
        comp = r["competitor_name"]
        lines.append(f"## {comp}\n")

        # 1. Resumo
        offers = r.get("offers", [])
        clients = r.get("clients", [])
        cases = r.get("cases", [])
        total_overlaps = sum(1 for o in offers if o.get("overlap") == "TOTAL")
        partial_overlaps = sum(1 for o in offers if o.get("overlap") == "PARCIAL")
        out_of_portfolio = sum(1 for o in offers if o.get("overlap") == "FORA_DE_PORTFOLIO")

        lines.append("### 1. Resumo\n")
        lines.append(f"| Item | Quantidade |")
        lines.append(f"|---|---|")
        lines.append(f"| Páginas relevantes analisadas | {r.get('pages_analyzed', 0)} |")
        lines.append(f"| Clientes identificados | {len(clients)} |")
        lines.append(f"| Cases identificados | {len(cases)} |")
        lines.append(f"| Ofertas identificadas | {len(offers)} |")
        lines.append(f"| Sobreposições TOTAL | {total_overlaps} |")
        lines.append(f"| Sobreposições PARCIAL | {partial_overlaps} |")
        lines.append(f"| Fora de portfólio | {out_of_portfolio} |")
        if r.get("collection_errors"):
            lines.append(f"| Erros de coleta | {len(r['collection_errors'])} |")
        lines.append("")

        # 2. Clientes
        lines.append("### 2. Clientes\n")
        if clients:
            lines.append("| Cliente | Setor | Evidência | Confidence | Fonte |")
            lines.append("|---|---|---|---|---|")
            for c in clients:
                lines.append(
                    f"| {c.get('name','')} | {c.get('sector','')} | "
                    f"{c.get('evidence_type','')} | {c.get('confidence','')} | "
                    f"{c.get('source_url','')} |"
                )
        else:
            lines.append("_Nenhum cliente confirmado encontrado._")
        lines.append("")

        # 3. Cases
        lines.append("### 3. Cases\n")
        if cases:
            lines.append("| Cliente | Case | Oferta do concorrente | Equivalente Tripla | Sobreposição | Fonte |")
            lines.append("|---|---|---|---|---|---|")
            for c in cases:
                lines.append(
                    f"| {c.get('client','')} | {c.get('case_title','')} | "
                    f"{c.get('competitor_solution','')} | {c.get('tripla_equivalent_solution','')} | "
                    f"{c.get('overlap','')} | {c.get('source_url','')} |"
                )
        else:
            lines.append("_Nenhum case confirmado encontrado._")
        lines.append("")

        # 4. Sobreposição de portfólio
        lines.append("### 4. Sobreposição de portfólio\n")
        portfolio_offers = [o for o in offers if o.get("overlap") in ("TOTAL", "PARCIAL")]
        if portfolio_offers:
            lines.append("| Oferta concorrente | Solução Tripla | Pilar | TOTAL/PARCIAL | Motivo | Confidence | Fonte |")
            lines.append("|---|---|---|---|---|---|---|")
            for o in portfolio_offers:
                lines.append(
                    f"| {o.get('competitor_offer','')} | {o.get('tripla_solution','')} | "
                    f"{o.get('tripla_pillar','')} | {o.get('overlap','')} | "
                    f"{o.get('reason','')} | {o.get('confidence','')} | {o.get('source_url','')} |"
                )
        else:
            lines.append("_Nenhuma sobreposição TOTAL ou PARCIAL identificada._")
        lines.append("")

        # 5. Fora de portfólio
        lines.append("### 5. Fora de portfólio\n")
        out_offers = [o for o in offers if o.get("overlap") == "FORA_DE_PORTFOLIO"]
        if out_offers:
            lines.append("| Oferta concorrente | Descrição | Fonte |")
            lines.append("|---|---|---|")
            for o in out_offers:
                lines.append(
                    f"| {o.get('competitor_offer','')} | {o.get('competitor_description','')} | "
                    f"{o.get('source_url','')} |"
                )
        else:
            lines.append("_Nenhuma oferta fora de portfólio identificada._")
        lines.append("")

        # 6. URLs para monitoramento
        lines.append("### 6. URLs sugeridas para monitoramento\n")
        mon = r.get("monitoring_urls", {})
        for wtype in ("CLIENTS_CASES", "OFFERS", "NEWS_LAUNCHES"):
            entries = mon.get(wtype, [])
            if entries:
                lines.append(f"**{wtype}**\n")
                lines.append("| URL | Tipo | Motivo |")
                lines.append("|---|---|---|")
                for e in entries:
                    lines.append(f"| {e['url']} | {e['type']} | {e.get('reason','')} |")
                lines.append("")

        # 7. Itens duvidosos
        lines.append("### 7. Itens duvidosos\n")
        doubtful = []
        for o in offers:
            if o.get("overlap") == "INDETERMINADO":
                doubtful.append(f"- **Oferta**: {o.get('competitor_offer','')} — {o.get('reason','')} ({o.get('source_url','')})")
        for o in offers:
            if 0.6 <= o.get("confidence", 1.0) < 0.75:
                doubtful.append(f"- **Baixa confidence**: {o.get('competitor_offer','')} (confidence={o.get('confidence','')})")
        if r.get("collection_errors"):
            for e in r["collection_errors"]:
                doubtful.append(f"- **Erro de coleta**: {e.get('url','')} — {e.get('error','')}")

        if doubtful:
            lines.extend(doubtful)
        else:
            lines.append("_Nenhum item requer revisão especial._")
        lines.append("\n---\n")

    report_path = REPORTS_DIR / "initial-review.md"
    report_path.write_text("\n".join(lines), encoding="utf-8")
    logger.info(f"Report saved: {report_path}")
    return report_path


def print_summary(results: list):
    total_competitors = len(results)
    successful = sum(1 for r in results if r["pages_analyzed"] > 0)
    total_pages = sum(r["pages_analyzed"] for r in results)
    total_clients = sum(len(r["clients"]) for r in results)
    total_cases = sum(len(r["cases"]) for r in results)
    total_offers = sum(len(r["offers"]) for r in results)
    total_overlaps = sum(
        sum(1 for o in r["offers"] if o.get("overlap") == "TOTAL") for r in results
    )
    partial_overlaps = sum(
        sum(1 for o in r["offers"] if o.get("overlap") == "PARCIAL") for r in results
    )
    out_of_portfolio = sum(
        sum(1 for o in r["offers"] if o.get("overlap") == "FORA_DE_PORTFOLIO") for r in results
    )
    failed = [r["competitor_name"] for r in results if r["pages_analyzed"] == 0]

    print("\n" + "="*60)
    print("RESULTADO DA VARREDURA INICIAL")
    print("="*60)
    print(f"  Concorrentes processados : {total_competitors}")
    print(f"  Com sucesso              : {successful}")
    print(f"  Páginas relevantes       : {total_pages}")
    print(f"  Clientes identificados   : {total_clients}")
    print(f"  Cases identificados      : {total_cases}")
    print(f"  Correspondências TOTAL   : {total_overlaps}")
    print(f"  Correspondências PARCIAL : {partial_overlaps}")
    print(f"  Fora de portfólio        : {out_of_portfolio}")
    print(f"  Relatório               : reports/initial-review.md")
    if failed:
        print(f"\n  ATENÇÃO — Sem dados suficientes:")
        for f in failed:
            print(f"    - {f}")
    print("="*60)
    print("\nTodos os dados são baseline_status=candidate.")
    print("Revise o relatório e devolva os dados aprovados.\n")


def main():
    parser = argparse.ArgumentParser(description="Varredura inicial de concorrentes")
    parser.add_argument("--competitor-id", help="Processar apenas este concorrente")
    args = parser.parse_args()

    competitors = load_competitors(args.competitor_id)
    if not competitors:
        logger.error("Nenhum concorrente encontrado com os critérios especificados")
        sys.exit(1)

    results = []
    for competitor in competitors:
        try:
            result = process_competitor(competitor)
            save_baseline_candidate(result)
            results.append(result)
        except Exception as e:
            logger.error(f"Unexpected error for {competitor['id']}: {e}", exc_info=True)
            results.append({
                "competitor_id": competitor["id"],
                "competitor_name": competitor["name"],
                "baseline_status": "candidate",
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "approved_at": None,
                "clients": [], "cases": [], "offers": [],
                "monitoring_urls": {"CLIENTS_CASES": [], "OFFERS": [], "NEWS_LAUNCHES": []},
                "collection_errors": [{"error": str(e), "stage": "unexpected"}],
                "pages_analyzed": 0,
            })

    generate_report(results)
    print_summary(results)


if __name__ == "__main__":
    main()

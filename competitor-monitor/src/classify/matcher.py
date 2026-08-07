"""
Deterministic keyword matcher for pre-filtering taxonomy candidates.
NO LLM — only used to narrow down which Tripla solutions to send to Haiku.
"""
import json
import re
from pathlib import Path

_ALIASES_PATH = Path(__file__).parent.parent.parent / "taxonomy" / "aliases.json"
_PORTFOLIO_PATH = Path(__file__).parent.parent.parent / "taxonomy" / "tripla-portfolio.json"

_aliases: dict | None = None
_portfolio: dict | None = None


def _load_aliases() -> dict:
    global _aliases
    if _aliases is None:
        _aliases = json.loads(_ALIASES_PATH.read_text(encoding="utf-8"))
    return _aliases


def _load_portfolio() -> dict:
    global _portfolio
    if _portfolio is None:
        _portfolio = json.loads(_PORTFOLIO_PATH.read_text(encoding="utf-8"))
    return _portfolio


def find_candidate_solutions(text: str) -> list:
    """
    Scan text for alias matches. Return list of Tripla solution names
    that are candidates for this page. Used to narrow LLM input.
    """
    aliases = _load_aliases()
    portfolio = _load_portfolio()
    text_lower = text.lower()

    # Build reverse map: alias_key → list of solution names
    matched_keys = set()
    for alias_key, terms in aliases.items():
        if alias_key.startswith("_"):
            continue
        for term in terms:
            pattern = r"\b" + re.escape(term.lower()) + r"\b"
            if re.search(pattern, text_lower):
                matched_keys.add(alias_key)
                break

    # Map alias keys to actual Tripla solution names
    matched_solutions = []
    all_solutions = []
    for pillar, solutions in portfolio["pillars"].items():
        all_solutions.extend(solutions)

    # Best-effort mapping: alias key → solution name substring match
    key_to_solutions = {
        "EDR": ["Endpoint Security EDR/XDR (Sophos)", "Endpoint Security EDR/XDR (Trend)",
                "Endpoint Security OT (TXOne)"],
        "SOC/MDR": ["SOC/MDR – Cyber Watch"],
        "MSS": ["MSS – Cyber Watch"],
        "PAM": ["PAM (BeyondTrust)"],
        "IAM": ["IAM/IGA (Okta)", "Gestão de Acessos (IAM)",
                "Segurança de Dados Centrada em Identidade e Acesso"],
        "WAF": ["Firewall de Aplicações WAF (Cloudflare)"],
        "SASE": ["SASE – ZTNA/SWG (Cloudflare)"],
        "NGFW": ["NGFW (Sophos)"],
        "DLP": ["Classificação e Proteção de Dados DLP (Forcepoint)"],
        "NAC": ["Controle de Acesso à Rede NAC (Forescout)"],
        "PENTEST": ["Pentest"],
        "VULNERABILITY_MANAGEMENT": ["Gestão de Vulnerabilidades (Qualys)",
                                      "Gestão de Vulnerabilidades e CTEM (XMCyber)"],
        "CTI": ["CTI (Axur)"],
        "DRP": ["DRP – Cyber Watch", "Plano de Continuidade de Negócios (PCN)"],
        "GRC": ["Escritório de Compliance", "Escritório de Privacidade",
                "Programa de Compliance", "Programa de Privacidade",
                "Autoritas vDPO", "CISO as a Service", "Adequação à ISO",
                "Programa de Governança (Teramind)"],
        "ASSESSMENT": ["ASSESSMENT", "Cyber Maturity Assessment (CMA)",
                       "Plano Diretor de SI (PDSI)"],
        "CLOUD": ["Cloud Microsoft", "Google Enterprise", "Data Center (IaaS)",
                  "Copilot Microsoft"],
        "MICROSEGMENTATION": ["Microssegmentação de Rede (Illumio)"],
        "NOC": ["Monitoramento de Rede (NOC)"],
        "OT_SECURITY": ["Endpoint Security OT (TXOne)"],
        "AWARENESS": ["Conscientização SI (KnowBe4)", "Conscientização SI (PhishX)",
                      "Conscientização e Cultura"],
        "TPRM": ["TPRM – Gestão de Risco de Terceiros"],
        "CISO_AS_SERVICE": ["CISO as a Service"],
        "DATA_CENTER": ["Data Center (IaaS)"],
        "STORAGE": ["Resiliência de dados (Cohesity)", "Soluções de Armazenamento (Huawei)"],
        "HYPERCONVERGENCE": ["Hiperconvergência"],
        "VIRTUALIZATION": ["Virtualização de servidores", "Licenciamento VMWare (Broadcom)"],
        "FINOPS": ["FinOps"],
        "SOC_BUILD": ["SOC/MDR – Cyber Watch", "ASSESSMENT"],
    }

    seen = set()
    for key in matched_keys:
        for sol in key_to_solutions.get(key, []):
            if sol not in seen:
                matched_solutions.append(sol)
                seen.add(sol)

    return matched_solutions


def get_pillar(solution_name: str) -> str:
    """Return pillar name for a given solution."""
    portfolio = _load_portfolio()
    for pillar, solutions in portfolio["pillars"].items():
        if solution_name in solutions:
            return pillar
    return "INDETERMINADO"

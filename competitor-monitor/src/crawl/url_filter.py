"""
Deterministic URL relevance filter. No LLM involved.
"""
import re
from urllib.parse import urlparse

RELEVANT_TERMS = [
    "soluc", "servic", "produto", "offering", "solution", "portfolio",
    "portfólio", "capability", "cyber", "segurança", "seguranca", "cloud",
    "infraestrut", "data-center", "datacenter", "compliance", "privacidade",
    "privacy", "governance", "governança", "grc", "client", "customer",
    "case", "success", "parceiro", "partner", "alliance", "aliança",
    "press", "noticia", "notícia", "lançamento", "lancamento", "imprensa",
    "iot", "soc", "mdr", "edr", "xdr", "siem", "pam", "iam", "nac",
    "pentest", "firewall", "waf", "sase", "dlp", "ngfw", "mssp",
    "vulnerability", "vulnerabilidad", "assessment", "consultoria",
    "managed", "gerenciado",
]

IGNORE_TERMS = [
    "carreira", "career", "/job", "/vaga", "investor-relation", "investidor",
    "cookies", "termos-de-uso", "privacy-policy", "politica-de-privacidade",
    "politica-cookies", "/contato", "/contact", "sobre-nos", "about-us",
    "nossa-equipe", "/team", "/leadership", "biografia", "executivo",
    "newsletter-unsub", "unsubscribe", "404", "logout", "login",
    "sitemap.xml", "robots.txt", "wp-admin", "wp-content", "wp-json",
    "feed", ".jpg", ".png", ".gif", ".pdf", ".zip", ".svg", "#",
]


def is_relevant_url(url: str, base_domain: str) -> bool:
    """Returns True if URL is worth fetching for competitive intelligence."""
    try:
        parsed = urlparse(url)
    except Exception:
        return False

    # Must be same domain or subdomain
    url_domain = parsed.netloc.replace("www.", "")
    base = base_domain.replace("www.", "").replace("https://", "").replace("http://", "")
    base = base.split("/")[0]
    if not (url_domain == base or url_domain.endswith("." + base)):
        return False

    path_lower = (parsed.path + "?" + parsed.query).lower()

    for term in IGNORE_TERMS:
        if term in path_lower:
            return False

    for term in RELEVANT_TERMS:
        if term in path_lower:
            return True

    return False


def is_homepage(url: str, base_url: str) -> bool:
    parsed = urlparse(url)
    base = urlparse(base_url)
    return parsed.netloc == base.netloc and parsed.path.strip("/") == base.path.strip("/")


def classify_url_type(url: str) -> str:
    """Classify URL into CLIENTS_CASES, OFFERS, or NEWS_LAUNCHES."""
    path = url.lower()

    client_case_terms = [
        "case", "client", "customer", "success", "depoimento",
        "testimonial", "historia", "story", "referencia",
    ]
    news_terms = [
        "blog", "noticia", "press", "imprensa", "lancamento", "news",
        "release", "publicacao", "artigo", "post",
    ]

    for term in client_case_terms:
        if term in path:
            return "CLIENTS_CASES"

    for term in news_terms:
        if term in path:
            return "NEWS_LAUNCHES"

    return "OFFERS"


def deduplicate_urls(urls: list) -> list:
    """Remove duplicates normalizing trailing slashes and fragments."""
    seen = set()
    result = []
    for url in urls:
        normalized = url.split("#")[0].rstrip("/").lower()
        if normalized not in seen:
            seen.add(normalized)
            result.append(url)
    return result

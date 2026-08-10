"""
Page fetcher using Firecrawl SDK v2.
Deterministic — no LLM involved.
"""
import os
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    import firecrawl
    _FC_AVAILABLE = True
except ImportError:
    _FC_AVAILABLE = False
    logger.warning("firecrawl-py not installed. Install with: pip install firecrawl-py")


class FetchResult:
    def __init__(self, url: str, success: bool, markdown: str = "",
                 title: str = "", links: list = None, error: str = ""):
        self.url = url
        self.success = success
        self.markdown = markdown
        self.title = title
        self.links = links or []
        self.error = error


def _get_client():
    api_key = os.environ.get("FIRECRAWL_API_KEY", "")
    if not api_key:
        raise RuntimeError("FIRECRAWL_API_KEY environment variable not set")
    if not _FC_AVAILABLE:
        raise RuntimeError("firecrawl-py not installed")
    return firecrawl.FirecrawlApp(api_key=api_key)


def fetch_page(url: str, retry: int = 2, delay: float = 2.0) -> FetchResult:
    """Fetch a single page and return normalized markdown + links."""
    for attempt in range(retry + 1):
        try:
            app = _get_client()
            doc = app.scrape(
                url,
                formats=["markdown", "links"],
                only_main_content=True,
                timeout=30000,
            )
            markdown = getattr(doc, "markdown", "") or ""
            links_raw = getattr(doc, "links", []) or []
            links = [l if isinstance(l, str) else l.get("url", "") for l in links_raw]
            links = [l for l in links if l]
            metadata = getattr(doc, "metadata", {}) or {}
            if isinstance(metadata, dict):
                title = metadata.get("title", "")
            else:
                title = getattr(metadata, "title", "") or ""
            return FetchResult(url=url, success=True, markdown=markdown,
                               title=title, links=links)
        except Exception as e:
            if attempt < retry:
                time.sleep(delay * (attempt + 1))
            else:
                return FetchResult(url=url, success=False, error=str(e))


def map_site(url: str, limit: int = 50) -> list:
    """Return list of URLs found via Firecrawl map (sitemap-first)."""
    try:
        app = _get_client()
        result = app.map(url, limit=limit)
        links_raw = getattr(result, "links", []) or []
        return [l if isinstance(l, str) else str(l) for l in links_raw]
    except Exception as e:
        logger.warning(f"map_site failed for {url}: {e}")
        return []

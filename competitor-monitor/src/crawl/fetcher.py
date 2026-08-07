"""
Page fetcher using Firecrawl API.
Deterministic — no LLM involved.
"""
import os
import time
import logging
from typing import Optional

logger = logging.getLogger(__name__)

try:
    from firecrawl import FirecrawlApp
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


def get_firecrawl_client():
    api_key = os.environ.get("FIRECRAWL_API_KEY", "")
    if not api_key:
        raise RuntimeError("FIRECRAWL_API_KEY environment variable not set")
    if not _FC_AVAILABLE:
        raise RuntimeError("firecrawl-py not installed")
    return FirecrawlApp(api_key=api_key)


def fetch_page(url: str, retry: int = 2, delay: float = 2.0) -> FetchResult:
    """Fetch a single page and return normalized markdown + links."""
    for attempt in range(retry + 1):
        try:
            app = get_firecrawl_client()
            result = app.scrape_url(
                url,
                formats=["markdown", "links"],
                only_main_content=True,
                timeout=30000,
            )
            markdown = result.get("markdown", "") or ""
            links = [l.get("url", l) if isinstance(l, dict) else l
                     for l in (result.get("links") or [])]
            title = (result.get("metadata") or {}).get("title", "")
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
        app = get_firecrawl_client()
        result = app.map_url(url, params={"limit": limit})
        if isinstance(result, dict):
            links = result.get("links", [])
        elif isinstance(result, list):
            links = result
        else:
            links = []
        return [l.get("url", l) if isinstance(l, dict) else l for l in links]
    except Exception as e:
        logger.warning(f"map_site failed for {url}: {e}")
        return []

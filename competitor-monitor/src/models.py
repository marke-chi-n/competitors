from dataclasses import dataclass, field
from typing import Optional
from datetime import datetime


@dataclass
class PageSnapshot:
    url: str
    competitor_id: str
    content_hash: str
    normalized_text: str
    collected_at: str
    page_title: str = ""
    watcher_type: str = ""


@dataclass
class Client:
    name: str
    sector: str
    source_url: str
    evidence_type: str
    confidence: float


@dataclass
class Case:
    client: str
    case_title: str
    competitor_solution: str
    case_summary: str
    tripla_equivalent_solution: str
    overlap: str
    source_url: str
    published_at: Optional[str]
    confidence: float


@dataclass
class Offer:
    competitor_offer: str
    competitor_description: str
    tripla_solution: str
    tripla_pillar: str
    overlap: str
    delivery_similarity: str
    reason: str
    source_url: str
    market_scope: str
    confidence: float


@dataclass
class CompetitorBaseline:
    competitor_id: str
    competitor_name: str
    baseline_status: str
    generated_at: str
    approved_at: Optional[str]
    clients: list
    cases: list
    offers: list
    monitoring_urls: dict
    collection_errors: list
    pages_analyzed: int

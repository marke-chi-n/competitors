"""
SHA-256 hash of normalized content. Deterministic — no LLM.
"""
import hashlib


def compute_hash(text: str) -> str:
    """Return SHA-256 hex digest of normalized text."""
    return hashlib.sha256(text.encode("utf-8")).digest().hex()


def hashes_equal(hash_a: str, hash_b: str) -> bool:
    return hash_a == hash_b


def change_fingerprint(competitor_id: str, monitored_field: str,
                       change_type: str, normalized_value: str) -> str:
    """Deterministic fingerprint for deduplication of alerts."""
    raw = f"{competitor_id}|{monitored_field}|{change_type}|{normalized_value}"
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()

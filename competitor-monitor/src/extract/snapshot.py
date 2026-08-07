"""
Save and load page snapshots. Deterministic — no LLM.
"""
import json
import os
from datetime import datetime, timezone
from pathlib import Path

SNAPSHOTS_DIR = Path(__file__).parent.parent.parent / "snapshots"


def _snapshot_path(competitor_id: str, url_hash: str) -> Path:
    comp_dir = SNAPSHOTS_DIR / competitor_id
    comp_dir.mkdir(parents=True, exist_ok=True)
    return comp_dir / f"{url_hash}.json"


def save_snapshot(competitor_id: str, url: str, content_hash: str,
                  normalized_text: str, title: str = "",
                  watcher_type: str = "") -> Path:
    from src.extract.hasher import compute_hash
    url_hash = compute_hash(url)[:16]
    path = _snapshot_path(competitor_id, url_hash)
    data = {
        "url": url,
        "competitor_id": competitor_id,
        "content_hash": content_hash,
        "normalized_text": normalized_text,
        "title": title,
        "watcher_type": watcher_type,
        "collected_at": datetime.now(timezone.utc).isoformat(),
    }
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def load_snapshot(competitor_id: str, url: str) -> dict | None:
    from src.extract.hasher import compute_hash
    url_hash = compute_hash(url)[:16]
    path = _snapshot_path(competitor_id, url_hash)
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_snapshots(competitor_id: str) -> list:
    comp_dir = SNAPSHOTS_DIR / competitor_id
    if not comp_dir.exists():
        return []
    return [json.loads(p.read_text(encoding="utf-8"))
            for p in comp_dir.glob("*.json")]

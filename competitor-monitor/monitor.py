"""
Rotina diária de monitoramento. NÃO ATIVAR até aprovação do baseline.

Uso (após aprovação):
  python monitor.py

Fluxo:
  URL → FETCH → NORMALIZE → HASH
  → se hash igual: NO_CHANGE (zero LLM)
  → se hash diferente: DIFF → filtro determinístico → LLM (Haiku) → ALERTA
"""
import json
import logging
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).parent
sys.path.insert(0, str(ROOT))

from src.crawl.fetcher import fetch_page
from src.crawl.url_filter import classify_url_type
from src.extract.normalizer import normalize
from src.extract.hasher import compute_hash, hashes_equal, change_fingerprint
from src.extract.snapshot import load_snapshot, save_snapshot
from src.diff.differ import compute_diff, extract_added_lines, extract_removed_lines, diff_is_substantive
from src.classify.matcher import find_candidate_solutions
from src.classify.classifier import classify_change
from src.notify.alerter import send_alert

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s — %(message)s",
)
logger = logging.getLogger("monitor")

STATE_FILE = ROOT / "state" / "monitoring-state.json"
BASELINE_DIR = ROOT / "baseline" / "approved"


def load_state() -> dict:
    STATE_FILE.parent.mkdir(exist_ok=True)
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_run": {}, "alert_fingerprints": []}


def save_state(state: dict):
    STATE_FILE.write_text(json.dumps(state, ensure_ascii=False, indent=2))


def load_approved_baselines() -> list:
    if not BASELINE_DIR.exists():
        return []
    return [
        json.loads(p.read_text())
        for p in BASELINE_DIR.glob("*.json")
    ]


def should_check(watcher_type: str, last_checked: str | None, state: dict) -> bool:
    """Deterministic schedule check. No LLM."""
    from datetime import timedelta
    if not last_checked:
        return True

    last = datetime.fromisoformat(last_checked)
    now = datetime.now(timezone.utc)
    delta = now - last

    if watcher_type in ("CLIENTS_CASES", "NEWS_LAUNCHES"):
        return delta.total_seconds() >= 86400  # daily
    elif watcher_type == "OFFERS":
        return delta.total_seconds() >= 604800  # weekly
    return True


def process_url(competitor: dict, url_entry: dict, state: dict) -> list:
    """
    Full pipeline for one URL.
    Returns list of change dicts (may be empty).
    """
    url = url_entry["url"]
    watcher_type = url_entry.get("type", classify_url_type(url))
    comp_id = competitor["competitor_id"]
    comp_name = competitor["competitor_name"]

    last_checked_key = f"{comp_id}|{url}"
    last_checked = state.get("last_run", {}).get(last_checked_key)

    if not should_check(watcher_type, last_checked, state):
        logger.debug(f"[{comp_id}] Skipping (not due): {url}")
        return []

    # FETCH
    fetch = fetch_page(url)
    if not fetch.success:
        logger.warning(f"[{comp_id}] Fetch failed (NOT treated as removal): {url} — {fetch.error}")
        return []

    # NORMALIZE
    normalized = normalize(fetch.markdown)

    # HASH
    current_hash = compute_hash(normalized)

    # COMPARE
    snapshot = load_snapshot(comp_id, url)
    if snapshot is None:
        # First run after approval — save and skip
        save_snapshot(comp_id, url, current_hash, normalized, fetch.title, watcher_type)
        state.setdefault("last_run", {})[last_checked_key] = datetime.now(timezone.utc).isoformat()
        return []

    if hashes_equal(current_hash, snapshot["content_hash"]):
        # NO CHANGE — zero LLM calls
        state.setdefault("last_run", {})[last_checked_key] = datetime.now(timezone.utc).isoformat()
        return []

    # HASH CHANGED — compute diff
    diff = compute_diff(snapshot["normalized_text"], normalized)

    if not diff_is_substantive(diff, min_chars=50):
        # Too small — likely noise
        save_snapshot(comp_id, url, current_hash, normalized, fetch.title, watcher_type)
        state.setdefault("last_run", {})[last_checked_key] = datetime.now(timezone.utc).isoformat()
        return []

    # Deterministic pre-filter
    added = extract_added_lines(diff)
    removed = extract_removed_lines(diff)
    candidates = find_candidate_solutions(added + "\n" + removed)

    # Get baseline context (short)
    baseline_context = snapshot["normalized_text"][:500]

    # LLM (Haiku) — only the diff, not the full page
    change = classify_change(
        competitor_id=comp_id,
        competitor_name=comp_name,
        page_url=url,
        watcher_type=watcher_type,
        diff_excerpt=diff[:3000],
        baseline_context=baseline_context,
        candidate_solutions=candidates,
    )

    # Update snapshot
    save_snapshot(comp_id, url, current_hash, normalized, fetch.title, watcher_type)
    state.setdefault("last_run", {})[last_checked_key] = datetime.now(timezone.utc).isoformat()

    if not change.get("relevant"):
        return []

    severity = change.get("severity", "IGNORE")
    if severity in ("IGNORE", "LOW"):
        return []

    # Deduplication
    fp = change_fingerprint(
        comp_id,
        change.get("field", ""),
        change.get("change_type", ""),
        str(change.get("proposed_value", "")),
    )
    if fp in state.get("alert_fingerprints", []):
        logger.info(f"[{comp_id}] Duplicate alert suppressed: {fp[:12]}")
        return []

    state.setdefault("alert_fingerprints", []).append(fp)
    change["competitor"] = comp_id
    return [change]


def main():
    baselines = load_approved_baselines()
    if not baselines:
        logger.error("No approved baselines found in baseline/approved/. "
                     "Run scan_initial.py first and approve the candidates.")
        sys.exit(1)

    state = load_state()
    all_changes = []

    for competitor in baselines:
        comp_id = competitor["competitor_id"]
        mon_urls = competitor.get("monitoring_urls", {})

        for wtype, entries in mon_urls.items():
            for entry in entries:
                changes = process_url(competitor, entry, state)
                all_changes.extend(changes)

    save_state(state)

    if all_changes:
        high_medium = [c for c in all_changes if c.get("severity") in ("HIGH", "MEDIUM")]
        logger.info(f"Run complete. Changes: {len(all_changes)} total, {len(high_medium)} HIGH/MEDIUM")
        send_alert(all_changes)
    else:
        logger.info("Run complete. No significant changes detected.")


if __name__ == "__main__":
    main()

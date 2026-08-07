"""
Text diff computation. Deterministic — no LLM.
"""
import difflib


def compute_diff(old_text: str, new_text: str, context_lines: int = 3) -> str:
    """
    Return unified diff between old and new text.
    Returns empty string if identical.
    """
    if old_text == new_text:
        return ""

    old_lines = old_text.splitlines(keepends=True)
    new_lines = new_text.splitlines(keepends=True)

    diff = difflib.unified_diff(
        old_lines, new_lines,
        fromfile="baseline",
        tofile="current",
        n=context_lines,
    )
    return "".join(diff)


def extract_added_lines(diff_text: str) -> str:
    """Extract only lines added in the diff (lines starting with +)."""
    lines = [l[1:] for l in diff_text.splitlines()
             if l.startswith("+") and not l.startswith("+++")]
    return "\n".join(lines)


def extract_removed_lines(diff_text: str) -> str:
    """Extract only lines removed in the diff (lines starting with -)."""
    lines = [l[1:] for l in diff_text.splitlines()
             if l.startswith("-") and not l.startswith("---")]
    return "\n".join(lines)


def diff_is_substantive(diff_text: str, min_chars: int = 50) -> bool:
    """
    Deterministic pre-filter: returns False if diff is too small to warrant LLM call.
    """
    added = extract_added_lines(diff_text)
    removed = extract_removed_lines(diff_text)
    return len(added) + len(removed) >= min_chars

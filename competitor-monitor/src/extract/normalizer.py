"""
Text normalization — deterministic, no LLM.
Strips boilerplate, whitespace, repeated content.
"""
import re


# Patterns that indicate boilerplate to remove
_BOILERPLATE_PATTERNS = [
    r"(cookie|cookies|GDPR|LGPD|consent|aceitar cookies|política de privacidade)[^\n]{0,200}\n",
    r"(©|copyright|todos os direitos reservados|all rights reserved)[^\n]{0,100}\n",
    r"(linkedin|twitter|facebook|instagram|youtube)\s*(\.com)?[^\n]{0,50}\n",
    r"\[?(skip to|ir para)\s*(main|content|conteúdo)\]?[^\n]{0,50}\n",
    r"(menu|navigation|navbar|nav)[^\n]{0,50}\n",
    r"reCAPTCHA[^\n]{0,200}\n",
]

_BOILERPLATE_RE = re.compile("|".join(_BOILERPLATE_PATTERNS), re.IGNORECASE)


def normalize(text: str) -> str:
    """
    Normalize markdown content for hashing and classification.
    Returns clean plain text with boilerplate removed.
    """
    if not text:
        return ""

    # Remove markdown image tags
    text = re.sub(r"!\[.*?\]\(.*?\)", "", text)

    # Remove markdown links but keep text
    text = re.sub(r"\[(.*?)\]\(.*?\)", r"\1", text)

    # Remove HTML tags if any leaked through
    text = re.sub(r"<[^>]+>", "", text)

    # Remove boilerplate patterns
    text = _BOILERPLATE_RE.sub("", text)

    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Strip leading/trailing whitespace per line
    lines = [l.strip() for l in text.splitlines()]

    # Remove very short lines (menu items, single words)
    lines = [l for l in lines if len(l) > 3 or l == ""]

    # Remove duplicate consecutive lines
    deduped = []
    prev = None
    for line in lines:
        if line != prev:
            deduped.append(line)
        prev = line

    result = "\n".join(deduped).strip()

    # Truncate to max chars to prevent token explosion
    max_chars = int(os.environ.get("MAX_CONTENT_CHARS", "15000"))
    if len(result) > max_chars:
        result = result[:max_chars] + "\n[TRUNCATED]"

    return result


import os  # noqa: E402 — kept at bottom to avoid circular

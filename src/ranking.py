from __future__ import annotations

from urllib.parse import urlparse


BAD_HOST_HINTS = {
    "x.com": -2,
    "twitter.com": -2,
}

PREFERRED_PATH_HINTS = {
    "/article/": 4,
    "/news/": 4,
    "/blog/": 3,
    "/posts/": 3,
    "/docs/": 2,
    "/guide": 2,
    "/help": 1,
}

LOW_QUALITY_PATH_HINTS = {
    "/discussions/": -3,
    "/discussion/": -3,
    "/issues/": -3,
    "/pull/": -3,
    "/search": -4,
    "/explore": -4,
}


def score_candidate(item: dict) -> int:
    url = (item.get("url") or "").strip()
    title = (item.get("title") or "").strip().lower()
    snippet = (item.get("snippet") or "").strip().lower()

    if not url:
        return -999

    parsed = urlparse(url)
    host = parsed.netloc.lower()
    path = parsed.path.lower() or "/"

    score = 0

    # Prefer normal web sources over social by default in topic mode.
    for hint, delta in BAD_HOST_HINTS.items():
        if hint in host:
            score += delta

    for hint, delta in PREFERRED_PATH_HINTS.items():
        if hint in path:
            score += delta

    for hint, delta in LOW_QUALITY_PATH_HINTS.items():
        if hint in path:
            score += delta

    # Homepages are often too broad for topic summaries.
    if path in {"", "/", "/zh/", "/en/"}:
        score -= 2

    if len(snippet) > 80:
        score += 2
    if len(snippet) > 160:
        score += 1

    if any(word in title for word in ["guide", "best practices", "tutorial", "architecture", "memory"]):
        score += 2

    if any(word in title for word in ["discussion", "issue", "pull request"]):
        score -= 2

    if any(word in snippet for word in ["how to", "architecture", "workflow", "best practices"]):
        score += 2

    return score


def rank_candidates(items: list[dict]) -> list[dict]:
    ranked = []
    for item in items:
        enriched = dict(item)
        enriched["score"] = score_candidate(item)
        ranked.append(enriched)
    ranked.sort(key=lambda x: x.get("score", -999), reverse=True)
    return ranked

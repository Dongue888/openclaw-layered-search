import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from ranking import rank_candidates, score_candidate


def test_article_like_page_scores_higher_than_discussion():
    article = {
        "url": "https://example.com/blog/openclaw-layered-search",
        "title": "OpenClaw Layered Search best practices",
        "snippet": "A practical architecture and workflow guide for retrieval orchestration.",
    }
    discussion = {
        "url": "https://github.com/openclaw/openclaw/discussions/17824",
        "title": "Discussion about memory architecture",
        "snippet": "Community discussion thread.",
    }
    assert score_candidate(article) > score_candidate(discussion)


def test_rank_candidates_sorts_best_first():
    items = [
        {
            "url": "https://github.com/openclaw/openclaw/discussions/17824",
            "title": "Discussion about memory architecture",
            "snippet": "Community discussion thread.",
        },
        {
            "url": "https://example.com/blog/openclaw-layered-search",
            "title": "OpenClaw Layered Search best practices",
            "snippet": "A practical architecture and workflow guide for retrieval orchestration.",
        },
    ]
    ranked = rank_candidates(items)
    assert ranked[0]["url"] == "https://example.com/blog/openclaw-layered-search"

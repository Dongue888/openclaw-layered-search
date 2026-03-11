import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from router import detect_site_kind, normalize_task, plan_retrieval


def test_normalize_url():
    task = normalize_task("https://example.com/a")
    assert task.input_type == "url"
    assert task.url == "https://example.com/a"


def test_normalize_topic():
    task = normalize_task("OpenClaw Layered Search")
    assert task.input_type == "topic"
    assert task.topic == "OpenClaw Layered Search"


def test_social_url_has_jina_fallback():
    task = normalize_task("https://x.com/test/status/1")
    assert detect_site_kind(task.url) == "social"
    assert plan_retrieval(task) == ["web_fetch", "r.jina.ai", "browser"]


def test_topic_uses_search_first():
    task = normalize_task("OpenClaw Layered Search")
    assert plan_retrieval(task) == ["web_search", "web_fetch"]


def test_mixed_input_detects_topic_and_urls():
    task = normalize_task("OpenClaw Layered Search https://example.com/a https://x.com/test/status/1")
    assert task.input_type == "mixed"
    assert len(task.urls) == 2
    assert task.topic == "OpenClaw Layered Search"
    assert plan_retrieval(task) == ["web_fetch", "r.jina.ai", "web_search", "browser"]


def test_wechat_url_uses_camoufox_provider():
    task = normalize_task("https://mp.weixin.qq.com/s/abc")
    assert plan_retrieval(task) == ["web_fetch", "wechat_camoufox", "browser"]

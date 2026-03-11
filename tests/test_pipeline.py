import sys
from pathlib import Path

sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from pipeline import _clean_jina_text, _classify_failure, _extract_best_text, _extract_wechat_text, _extract_wechat_title, _extract_x_post_block, _looks_blocked, _looks_like_xhs_shell


HTML_SAMPLE = """
<html>
<head><title>测试文章</title></head>
<body>
<div class="nav">首页 快讯 要闻 评论</div>
<div class="article-content">
  <p>来源：测试站 作者：小明 2026-03-10</p>
  <p>这是第一段正文，讲的是 OpenClaw Layered Search 想解决新手不会选工具的问题。</p>
  <p>这是第二段正文，讲的是链接抓取失败后不要胡编，而是应该优雅 fallback。</p>
  <p>这是第三段正文，讲的是 grounded summary 必须基于实际拿到的证据来写。</p>
</div>
<div class="footer">关于我们 联系我们 Copyright</div>
</body>
</html>
"""


def test_extract_best_text_removes_navigation_noise():
    text = _extract_best_text(HTML_SAMPLE)
    assert "这是第一段正文" in text
    assert "这是第二段正文" in text
    assert "首页 快讯 要闻 评论" not in text
    assert "Copyright" not in text


def test_blocked_placeholder_is_detected():
    text = "JavaScript is not available. Please enable JavaScript to continue using x.com."
    assert _looks_blocked(text) is True
    wechat_verify = "环境异常\n\n当前环境异常，完成验证后即可继续访问。\n\n去验证"
    assert _looks_blocked(wechat_verify) is True


def test_classify_failure_labels():
    assert _classify_failure("blocked placeholder content") == "blocked_placeholder"
    assert _classify_failure("shell page content") == "shell_page"
    assert _classify_failure("weak content") == "weak_content"
    assert _classify_failure("not implemented") == "not_implemented"


def test_clean_jina_text_removes_x_shell():
    raw = """Title: jain on X\n\nURL Source: http://x.com/x\n\nMarkdown Content:\nDon’t miss what’s happening\nPeople on X are the first to know.\n\nPost\n\n真正的正文第一段\n\n真正的正文第二段\n\nLog in\nSign up\nTerms of Service\n"""
    cleaned = _clean_jina_text(raw)
    assert "Don’t miss what’s happening" not in cleaned
    assert "Log in" not in cleaned
    assert "真正的正文第一段" in cleaned


def test_extract_x_post_block_prefers_post_body():
    raw = """
Title: jain on X: \"标题\" / X

[![Image 1](https://pbs.twimg.com/profile.jpg)](http://x.com/jain_web3)

[jain](http://x.com/jain_web3)

[@jain_web3](http://x.com/jain_web3)

这是推文正文第一句 这是推文正文第二句

Translate post

[5:28 AM · Mar 5, 2026](http://x.com/jain_web3/status/1)

Read 13 replies
"""
    extracted = _extract_x_post_block(raw)
    assert extracted == "这是推文正文第一句 这是推文正文第二句"


def test_xhs_shell_page_is_detected():
    text = "创作中心 业务合作 发现 发布 通知 沪ICP备13030189号 行吟信息科技 违法不良信息举报电话"
    assert _looks_like_xhs_shell("http://xhslink.com/o/abc", text) is True


def test_extract_wechat_title_and_body():
    html = """
    <html><head><title>fallback title</title></head><body>
      <h1 id="activity-name">公众号文章标题</h1>
      <div id="js_content">
        <p>第一段内容比较长，足够被识别为正文，而且不是导航壳子。</p>
        <p>第二段继续补充细节，让总长度超过最小阈值，便于测试专用 extractor。</p>
        <p>第三段再补一点文字，确保清洗后仍然像文章，而不是空壳页面。</p>
      </div>
    </body></html>
    """
    assert _extract_wechat_title(html) == "公众号文章标题"
    body = _extract_wechat_text(html)
    assert "第一段内容比较长" in body
    assert len(body) >= 80

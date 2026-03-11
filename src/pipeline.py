from __future__ import annotations

import json
import os
import re
import subprocess
import tempfile
import urllib.request
from html import unescape
from pathlib import Path
from typing import Optional, Tuple

from playwright.sync_api import sync_playwright

from ranking import rank_candidates
from router import normalize_task, plan_retrieval
from schemas import CandidateSource, PipelineResult, SourceRecord
from search_provider import search_topic
from summarize import build_summary


USER_AGENT = (
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/123.0 Safari/537.36"
)

PROJECT_ROOT = Path(__file__).resolve().parents[1]
TOOLS_DIR = PROJECT_ROOT / "tools"
WECHAT_TOOL_DIR = TOOLS_DIR / "wechat-article-for-ai"
WECHAT_TOOL_REPO = "https://github.com/bzd6661/wechat-article-for-ai.git"

NOISE_PATTERNS = [
    r"首页",
    r"快讯",
    r"要闻",
    r"新股",
    r"港美股",
    r"数据",
    r"基金",
    r"评论",
    r"客户端",
    r"您当前的位置",
    r"点赞",
    r"分享",
    r"责任编辑",
    r"网友评论",
    r"暂无评论",
    r"为你推荐",
    r"时报 热榜",
    r"换一换",
    r"Copyright",
    r"备案号",
    r"关于我们",
    r"联系我们",
    r"网站地图",
    r"违法和不良信息举报",
]

BLOCKER_PATTERNS = [
    r"JavaScript is not available",
    r"Please enable JavaScript",
    r"switch to a supported browser",
    r"Something went wrong, but don’t fret",
    r"Some privacy related extensions may cause issues",
    r"Please sign in",
    r"login to continue",
    r"Access denied",
    r"verify you are human",
    r"环境异常",
    r"完成验证后即可继续访问",
    r"去验证",
]

LOGIN_PATTERNS = [
    r"Please sign in",
    r"login to continue",
    r"Log in",
    r"Sign up",
]

XHS_SHELL_PATTERNS = [
    r"行吟信息科技",
    r"沪ICP备13030189号",
    r"违法不良信息举报电话",
    r"创作中心",
    r"业务合作",
    r"发现",
    r"发布",
    r"通知",
    r"个性化推荐算法",
]

WECHAT_CONTENT_SELECTORS = [
    r'id=["\']js_content["\']',
    r'class=["\'][^"\']*rich_media_content[^"\']*["\']',
]


def _clean_text(text: str) -> str:
    text = unescape(text)
    text = re.sub(r"\r", "", text)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    return text.strip()


def _strip_html_basic(html: str) -> str:
    html = re.sub(r"<script[\s\S]*?</script>", " ", html, flags=re.I)
    html = re.sub(r"<style[\s\S]*?</style>", " ", html, flags=re.I)
    html = re.sub(r"<(br|p|div|li|h1|h2|h3|article|section)[^>]*>", "\n", html, flags=re.I)
    text = re.sub(r"<[^>]+>", " ", html)
    return _clean_text(text)


def _extract_title(html: str) -> str:
    m = re.search(r"<title[^>]*>(.*?)</title>", html, flags=re.I | re.S)
    return unescape(m.group(1)).strip() if m else ""


def _is_wechat_url(url: str) -> bool:
    return "mp.weixin.qq.com" in url


def _extract_wechat_title(html: str) -> str:
    patterns = [
        r'<h1[^>]*id=["\']activity-name["\'][^>]*>([\s\S]*?)</h1>',
        r'<h2[^>]*class=["\'][^"\']*rich_media_title[^"\']*["\'][^>]*>([\s\S]*?)</h2>',
    ]
    for pattern in patterns:
        m = re.search(pattern, html, flags=re.I | re.S)
        if m:
            title = _clean_text(re.sub(r"<[^>]+>", " ", m.group(1)))
            if title:
                return title
    return _extract_title(html)


def _extract_wechat_text(html: str) -> str:
    patterns = [
        r'<div[^>]*id=["\']js_content["\'][^>]*>([\s\S]*?)</div>',
        r'<div[^>]*class=["\'][^"\']*rich_media_content[^"\']*["\'][^>]*>([\s\S]*?)</div>',
    ]
    candidates: list[str] = []
    for pattern in patterns:
        for block in re.findall(pattern, html, flags=re.I | re.S):
            text = _strip_html_basic(block)
            text = _post_clean_article(text)
            if len(text) >= 80:
                candidates.append(text)
    if not candidates:
        return ""
    return max(candidates, key=len)


def _extract_candidates(html: str) -> list[str]:
    candidates: list[str] = []

    blocks = re.findall(
        r"<(article|section|div)[^>]*(?:id|class)=[\"'][^\"']*(?:article|content|detail|正文|post|entry|news)[^\"']*[\"'][^>]*>([\s\S]*?)</\1>",
        html,
        flags=re.I,
    )
    for _tag, block in blocks:
        text = _strip_html_basic(block)
        if len(text) >= 200:
            candidates.append(text)

    paragraphs = re.findall(r"<p[^>]*>([\s\S]*?)</p>", html, flags=re.I)
    if paragraphs:
        joined = "\n\n".join(_clean_text(re.sub(r"<[^>]+>", " ", p)) for p in paragraphs)
        joined = _clean_text(joined)
        if len(joined) >= 200:
            candidates.append(joined)

    full_text = _strip_html_basic(html)
    if len(full_text) >= 200:
        candidates.append(full_text)

    return candidates


def _score_candidate(text: str) -> int:
    score = 0
    if len(text) >= 800:
        score += 3
    if len(text) >= 1500:
        score += 2
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    score += min(len(paragraphs), 8)
    for pat in NOISE_PATTERNS:
        if re.search(pat, text):
            score -= 2
    if "来源：" in text or "作者：" in text:
        score += 2
    if "公示期" in text or "征求意见稿" in text:
        score += 1
    return score


def _post_clean_article(text: str) -> str:
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    kept: list[str] = []
    started = False
    for p in paragraphs:
        if any(re.search(pat, p) for pat in NOISE_PATTERNS):
            if started and len(kept) >= 3:
                break
            continue
        if not started:
            if len(p) < 20 and "来源" not in p and "作者" not in p:
                continue
            started = True
        kept.append(p)
    cleaned = "\n\n".join(kept)
    return _clean_text(cleaned)


def _extract_best_text(html: str) -> str:
    candidates = _extract_candidates(html)
    if not candidates:
        return ""
    best = max(candidates, key=_score_candidate)
    return _post_clean_article(best)


def _looks_blocked(text: str) -> bool:
    text = text or ""
    return any(re.search(pat, text, flags=re.I) for pat in BLOCKER_PATTERNS)


def _looks_like_xhs_shell(url: str, text: str) -> bool:
    if "xhslink.com" not in url and "xiaohongshu.com" not in url:
        return False
    hits = sum(1 for pat in XHS_SHELL_PATTERNS if re.search(pat, text, flags=re.I))
    return hits >= 3


def _classify_failure(reason: str) -> str:
    reason = reason or ""
    if "blocked placeholder" in reason:
        return "blocked_placeholder"
    if "shell page" in reason:
        return "shell_page"
    if any(re.search(pat, reason, flags=re.I) for pat in LOGIN_PATTERNS):
        return "login_wall"
    if "weak content" in reason:
        return "weak_content"
    if "not implemented" in reason:
        return "not_implemented"
    if any(x in reason.lower() for x in ["timed out", "temporary failure", "name or service not known", "connection", "http error"]):
        return "network_error"
    return "unknown"


def _extract_x_post_block(text: str) -> str:
    text = text.strip()
    lines = [line.strip() for line in text.splitlines()]

    start = None
    for i, line in enumerate(lines):
        if line.startswith("[@") and "x.com/" in line:
            start = i + 1
            break

    if start is None:
        return text

    body_lines = []
    for line in lines[start:]:
        if not line:
            continue
        if any(re.search(pat, line, flags=re.I) for pat in [
            r"^Translate post$",
            r"^Read \d+ replies$",
            r"^New to X\?$",
            r"^Sign up now",
            r"^By signing up,",
            r"^\[[0-9:APM ·MarGMTa-z ,]+\]\(",
            r"^·$",
            r"^\[\d+(?:\.\d+)?K Views\]\(",
            r"^\d+$",
            r"^Trending now$",
            r"^What’s happening$",
            r"^Trending in ",
        ]):
            break
        if re.match(r"^\[.*\]\(http://x\.com/", line):
            continue
        if re.match(r"^\[!\[Image", line):
            continue
        body_lines.append(line)

    body = " ".join(body_lines)
    body = re.sub(r"\s+", " ", body).strip()
    return body if len(body) >= 10 else text


def _clean_jina_text(text: str) -> str:
    lines = [line.strip() for line in text.splitlines()]
    kept = []
    for line in lines:
        if not line:
            kept.append("")
            continue
        if any(re.search(pat, line, flags=re.I) for pat in [
            r"Don’t miss what’s happening",
            r"People on X are the first to know",
            r"^Log in$",
            r"^Sign up$",
            r"^Terms of Service$",
            r"^Privacy Policy$",
            r"^Cookie Policy$",
            r"^Accessibility$",
            r"^Ads info$",
            r"^More$",
            r"^Post$",
            r"^See new posts$",
            r"^Conversation$",
            r"^URL Source:",
            r"^Markdown Content:",
            r"^===============+$",
            r"^----+$",
            r"^© \d{4} X Corp\.$",
            r"^Trending now$",
            r"^What’s happening$",
            r"^New to X\?$",
            r"^Create account$",
            r"^Sign up with Apple$",
            r"^Read \d+ replies$",
            r"^Translate post$",
            r"^Published Time:",
            r"^\[Log in\]\(",
            r"^\[Sign up\]\(",
            r"^\[Create account\]\(",
            r"^\[Terms of Service\]\(",
            r"^\[Privacy Policy\]\(",
            r"^\[Cookie Policy\]\(",
            r"^\[Accessibility\]\(",
            r"^\[Ads info\]\(",
            r"^\[Show more\]\(",
            r"^\[!\[Image",
            r"^\[jain\]\(",
            r"^\[@",
            r"^\[\]\(http://x.com/\)$",
        ]):
            continue
        kept.append(line)
    cleaned = "\n".join(kept)
    cleaned = re.sub(r"\n\s*\n+", "\n\n", cleaned)
    cleaned = cleaned.strip()
    if " / X" in cleaned or "x.com/" in cleaned:
        extracted = _extract_x_post_block(cleaned)
        if extracted and extracted != cleaned:
            return extracted
    return cleaned.strip()


def _fetch_url(url: str) -> str:
    req = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(req, timeout=20) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        return resp.read().decode(charset, errors="replace")


def _fetch_via_web_fetch(url: str) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    try:
        html = _fetch_url(url)
        title = _extract_wechat_title(html) if _is_wechat_url(url) else _extract_title(html)
        text = _extract_wechat_text(html) if _is_wechat_url(url) else _extract_best_text(html)
        if _looks_blocked(text):
            return False, title, None, "blocked placeholder content"
        if _looks_like_xhs_shell(url, text):
            return False, title, None, "shell page content"
        if len(text) >= 200:
            return True, title, text[:12000], None
        return False, title, None, "weak content"
    except Exception as exc:
        return False, None, None, str(exc)


def _fetch_via_jina(url: str) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    target = f"https://r.jina.ai/http://{url.replace('https://', '').replace('http://', '')}"
    req = urllib.request.Request(target, headers={"User-Agent": USER_AGENT})
    try:
        with urllib.request.urlopen(req, timeout=20) as resp:
            text = resp.read().decode("utf-8", errors="replace").strip()
            text = _clean_text(text)
            if "x.com/" in url or "twitter.com/" in url:
                text = _extract_x_post_block(text)
            else:
                text = _clean_jina_text(text)
            if _looks_blocked(text):
                return False, None, None, "blocked placeholder content"
            if len(text) >= 80:
                return True, None, text[:12000], None
            return False, None, None, "weak content"
    except Exception as exc:
        return False, None, None, str(exc)


def _fetch_via_browser(url: str) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            page = browser.new_page(user_agent=USER_AGENT)
            page.goto(url, wait_until="domcontentloaded", timeout=30000)
            title = page.title() or ""

            if _is_wechat_url(url):
                try:
                    page.wait_for_selector("#js_content, .rich_media_content", timeout=15000)
                except Exception:
                    pass
                try:
                    page.wait_for_load_state("networkidle", timeout=10000)
                except Exception:
                    page.wait_for_timeout(2500)

                html = page.content()
                extracted_title = _extract_wechat_title(html)
                extracted_text = _extract_wechat_text(html)
                body_text = extracted_text or _clean_text(page.locator("body").inner_text(timeout=5000).strip())
                if extracted_title:
                    title = extracted_title
            else:
                page.wait_for_timeout(2500)
                body_text = page.locator("body").inner_text(timeout=5000).strip()

            browser.close()

        body_text = _clean_text(body_text)
        if _looks_blocked(body_text):
            return False, title, None, "blocked placeholder content"
        if _looks_like_xhs_shell(url, body_text):
            return False, title, None, "shell page content"
        if len(body_text) >= 200:
            return True, title, body_text[:12000], None
        return False, title, None, "weak content"
    except Exception as exc:
        return False, None, None, str(exc)


def _ensure_wechat_tool() -> Path:
    WECHAT_TOOL_DIR.parent.mkdir(parents=True, exist_ok=True)
    main_py = WECHAT_TOOL_DIR / "main.py"
    if main_py.exists():
        return WECHAT_TOOL_DIR
    subprocess.run(
        ["git", "clone", WECHAT_TOOL_REPO, str(WECHAT_TOOL_DIR)],
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
    )
    return WECHAT_TOOL_DIR


def _extract_title_from_markdown(md: str) -> str:
    m = re.search(r"^title:\s*(.+)$", md, flags=re.M)
    if m:
        return m.group(1).strip().strip('"')
    m = re.search(r"^#\s+(.+)$", md, flags=re.M)
    return m.group(1).strip() if m else ""


def _fetch_via_wechat_camoufox(url: str) -> Tuple[bool, Optional[str], Optional[str], Optional[str]]:
    try:
        tool_dir = _ensure_wechat_tool()
        with tempfile.TemporaryDirectory(prefix="wechat-camoufox-") as tmpdir:
            env = os.environ.copy()
            for key in ["ALL_PROXY", "all_proxy", "HTTP_PROXY", "HTTPS_PROXY", "http_proxy", "https_proxy"]:
                env.pop(key, None)
            proc = subprocess.run(
                ["python3", "main.py", "--no-images", "-o", tmpdir, url],
                cwd=str(tool_dir),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                timeout=180,
            )
            output = proc.stdout or ""
            md_files = list(Path(tmpdir).glob("*/*.md"))
            if not md_files:
                reason = "blocked placeholder content" if any(x in output for x in ["CaptchaError", "环境异常", "验证"]) else (output.strip().splitlines()[-1] if output.strip() else "weak content")
                return False, None, None, reason
            md = md_files[0].read_text(encoding="utf-8", errors="replace")
            title = _extract_title_from_markdown(md)
            body = re.sub(r"^---[\s\S]*?---\s*", "", md, count=1).strip()
            body = re.sub(r"!\[[^\]]*\]\([^\)]*\)", "", body)
            body = _clean_text(body)
            if _looks_blocked(body):
                return False, title, None, "blocked placeholder content"
            if len(body) >= 200:
                return True, title, body[:12000], None
            return False, title, None, "weak content"
    except subprocess.TimeoutExpired:
        return False, None, None, "network timeout"
    except Exception as exc:
        return False, None, None, str(exc)


def _run_url_mode(url: str, path: list[str], result: PipelineResult) -> PipelineResult:
    for method in path:
        if method == "web_fetch":
            ok, title, content, reason = _fetch_via_web_fetch(url)
        elif method == "r.jina.ai":
            ok, title, content, reason = _fetch_via_jina(url)
        elif method == "wechat_camoufox":
            ok, title, content, reason = _fetch_via_wechat_camoufox(url)
        elif method == "browser":
            ok, title, content, reason = _fetch_via_browser(url)
        else:
            ok, title, content, reason = False, None, None, "not implemented"

        if ok:
            result.sources_retrieved.append(
                SourceRecord(url=url, method=method, status="success", title=title, content=content)
            )
            break

        result.sources_failed.append(
            SourceRecord(
                url=url,
                method=method,
                status="failed",
                reason=reason,
                failure_label=_classify_failure(reason or ""),
            )
        )

    if not result.sources_retrieved:
        result.uncertainties.append("所有已配置抓取路径都未成功获取正文。")
        result.next_actions.append("检查页面是否需要浏览器渲染或登录态。")

    return build_summary(result)


def _build_topic_summary(topic: str, result: PipelineResult) -> str:
    lines = [f"主题：{topic}", "", "核心结论："]
    first = result.sources_retrieved[0]
    lines.append((first.content or "").strip()[:320])
    lines.append("")
    lines.append("主要证据来源：")
    for src in result.sources_retrieved[:3]:
        title = src.title or src.url
        lines.append(f"- {title} ({src.method})")
    if result.sources_failed:
        lines.append("")
        lines.append("未成功获取的来源：")
        for src in result.sources_failed[:3]:
            label = src.failure_label or "unknown"
            lines.append(f"- {src.url} [{label}]")
    lines.append("")
    lines.append("说明：")
    lines.append("- 当前为 MVP，总结基于前 1-2 个成功抓取的候选来源。")
    lines.append("- 若需要更完整研究，可扩展抓取更多候选并做交叉验证。")
    return "\n".join(lines).strip()


def _run_topic_mode(topic: str, result: PipelineResult) -> PipelineResult:
    try:
        candidates = search_topic(topic, limit=8)
        candidates = rank_candidates(candidates)
    except Exception as exc:
        result.uncertainties.append(f"搜索阶段失败：{exc}")
        result.next_actions.append("检查网络或更换搜索后端。")
        return build_summary(result)

    if not candidates:
        result.uncertainties.append("没有找到可用候选来源。")
        result.next_actions.append("尝试换一个更具体的主题关键词。")
        return build_summary(result)

    selected = candidates[:2]
    selected_urls = {item['url'] for item in selected}
    result.candidate_sources = [
        CandidateSource(
            url=item["url"],
            title=item.get("title") or None,
            snippet=item.get("snippet") or None,
            selected=item["url"] in selected_urls,
            note=(f"selected for fetch (score={item.get('score', 0)})" if item["url"] in selected_urls else f"candidate only (score={item.get('score', 0)})"),
        )
        for item in candidates[:5]
    ]

    result.next_actions.append("如果总结质量一般，下一步可扩展抓取更多候选来源。")
    for item in selected:
        url = item["url"]
        sub = PipelineResult(input_type="url", retrieval_path=["web_fetch", "r.jina.ai", "browser"])
        sub = _run_url_mode(url, sub.retrieval_path, sub)
        if sub.sources_retrieved:
            src = sub.sources_retrieved[0]
            src.title = src.title or item.get("title") or None
            result.sources_retrieved.append(src)
        else:
            result.sources_failed.extend(sub.sources_failed)

    if result.sources_retrieved:
        result.summary = _build_topic_summary(topic, result)
        return result

    result.uncertainties.append("搜索到了候选来源，但没有成功抓到足够正文。")
    result.next_actions.append("尝试更具体的关键词，或后续补浏览器 fallback。")
    return build_summary(result)


def _run_multi_url_mode(urls: list[str], result: PipelineResult) -> PipelineResult:
    for url in urls[:3]:
        path = ["web_fetch", "r.jina.ai", "browser"]
        sub = PipelineResult(input_type="url", retrieval_path=path)
        sub = _run_url_mode(url, path, sub)
        if sub.sources_retrieved:
            result.sources_retrieved.extend(sub.sources_retrieved[:1])
        else:
            result.sources_failed.extend(sub.sources_failed)

    if result.sources_retrieved:
        parts = []
        for src in result.sources_retrieved[:3]:
            title = f"标题：{src.title}\n" if src.title else ""
            parts.append(f"{title}{(src.content or '')[:280]}")
        result.summary = "多链接汇总：\n\n" + "\n\n---\n\n".join(parts)
        return result

    return build_summary(result)


def _run_mixed_mode(topic: str | None, urls: list[str], result: PipelineResult) -> PipelineResult:
    # 先吃用户给的 references
    result.next_actions.append("已优先处理你提供的参考链接；如果证据不足，再扩展搜索。")
    ref_result = PipelineResult(input_type="urls", retrieval_path=["web_fetch", "r.jina.ai", "browser"])
    ref_result = _run_multi_url_mode(urls, ref_result)
    result.sources_retrieved.extend(ref_result.sources_retrieved)
    result.sources_failed.extend(ref_result.sources_failed)

    # 如果参考链接已经够了，就直接结构化汇总
    if result.sources_retrieved:
        result.summary = _build_topic_summary(topic or "mixed-input research", result)
        if topic:
            result.next_actions.append("如需更广覆盖，可基于该主题再扩展搜索候选来源。")
        return result

    # 参考链接不够，再补搜索
    if topic:
        result.uncertainties.append("你提供的参考链接未抓到足够正文，已建议扩展搜索。")
        result.next_actions.append("下一步可执行 topic search expansion。")
    return build_summary(result)


def run(raw_input: str) -> PipelineResult:
    task = normalize_task(raw_input)
    path = plan_retrieval(task)
    result = PipelineResult(input_type=task.input_type, retrieval_path=path)

    if task.input_type == "topic" and task.topic:
        return _run_topic_mode(task.topic, result)

    if task.input_type == "urls" and task.urls:
        return _run_multi_url_mode(task.urls, result)

    if task.input_type == "mixed" and task.urls:
        return _run_mixed_mode(task.topic, task.urls, result)

    if task.input_type != "url" or not task.url:
        result.uncertainties.append("当前原型只完整实现了 URL / topic / mixed 的 MVP 子集。")
        result.next_actions.append("后续继续补强 mixed 的搜索扩展和多链接综合。")
        return build_summary(result)

    return _run_url_mode(task.url, path, result)


if __name__ == "__main__":
    import sys

    raw = " ".join(sys.argv[1:]).strip()
    out = run(raw)
    print(json.dumps(out, default=lambda x: x.__dict__, ensure_ascii=False, indent=2))

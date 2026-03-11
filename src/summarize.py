from __future__ import annotations

from schemas import PipelineResult


MIN_CONTENT_CHARS = 200


def _clip(text: str, limit: int = 500) -> str:
    text = (text or "").strip()
    return text[:limit].strip()


def build_summary(result: PipelineResult) -> PipelineResult:
    if result.sources_retrieved:
        source = result.sources_retrieved[0]
        body = (source.content or "").strip()
        title = (source.title or "").strip()
        if len(body) >= MIN_CONTENT_CHARS:
            prefix = f"标题：{title}\n\n" if title else ""
            result.summary = prefix + _clip(body, 700)
        else:
            result.summary = "已获取到部分内容，但正文较短，结论只基于有限文本。"
            result.uncertainties.append("抓取到的正文偏短，可能不是完整原文。")
        return result

    result.summary = "未能获取足够内容，因此不应直接下结论。"
    if not result.uncertainties:
        result.uncertainties.append("当前没有可支撑结论的正文内容。")
    if result.sources_failed:
        label = result.sources_failed[-1].failure_label or "unknown"
        if label == "blocked_placeholder":
            result.uncertainties.append("页面返回的是占位/拦截内容，不是真正文。")
            result.next_actions.append("尝试 r.jina.ai 或浏览器抓取。")
        elif label == "login_wall":
            result.uncertainties.append("页面可能需要登录后才能访问完整内容。")
            result.next_actions.append("尝试登录态浏览器或寻找二手来源。")
        elif label == "weak_content":
            result.uncertainties.append("已抓到内容，但正文强度不足。")
            result.next_actions.append("尝试其他抓取路径或搜索相关报道交叉验证。")
        elif label == "shell_page":
            result.uncertainties.append("当前拿到的是平台壳页，不是真正的文章正文。")
            result.next_actions.append("需要更强的浏览器路径、站点专用提取器或登录态。")
    if not result.next_actions:
        result.next_actions.append("尝试浏览器抓取或搜索二手来源交叉验证。")
    return result

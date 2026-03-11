from __future__ import annotations

import re
from urllib.parse import urlparse

from schemas import Task


SOCIAL_HOSTS = {"x.com", "twitter.com", "www.x.com", "www.twitter.com"}
WECHAT_HOSTS = {"mp.weixin.qq.com", "weixin.qq.com"}
URL_RE = re.compile(r"https?://\S+")


def normalize_task(raw: str) -> Task:
    text = raw.strip()
    urls = URL_RE.findall(text)

    if len(urls) == 1 and text == urls[0]:
        return Task(input_type="url", url=text)

    if len(urls) > 1 and text.replace("\n", " ").strip() == " ".join(urls).strip():
        return Task(input_type="urls", urls=urls)

    if urls:
        topic = text
        for url in urls:
            topic = topic.replace(url, " ")
        topic = re.sub(r"\s+", " ", topic).strip(" ,;\n\t")
        return Task(input_type="mixed", topic=topic or None, urls=urls, references=urls, goal="research")

    return Task(input_type="topic", topic=text, goal="research")


def detect_site_kind(url: str) -> str:
    host = urlparse(url).netloc.lower()
    if host in SOCIAL_HOSTS:
        return "social"
    if host in WECHAT_HOSTS:
        return "wechat"
    return "web"


def plan_retrieval(task: Task) -> list[str]:
    if task.input_type == "url" and task.url:
        kind = detect_site_kind(task.url)
        if kind == "social":
            return ["web_fetch", "r.jina.ai", "browser"]
        if kind == "wechat":
            return ["web_fetch", "wechat_camoufox", "browser"]
        return ["web_fetch", "browser"]

    if task.input_type == "urls":
        return ["web_fetch", "r.jina.ai", "browser"]

    if task.input_type == "mixed":
        return ["web_fetch", "r.jina.ai", "web_search", "browser"]

    if task.input_type == "topic":
        return ["web_search", "web_fetch"]

    return ["web_fetch"]

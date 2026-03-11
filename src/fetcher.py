"""
Fetcher module: integrates multiple retrieval tools
- MediaCrawler for Chinese platforms (XHS, Zhihu, Douyin, Bilibili, Weibo, Tieba, Kuaishou)
- xreach (via Agent-Reach) for Twitter/X
- yt-dlp (via Agent-Reach) for YouTube/Bilibili
- r.jina.ai for JavaScript-heavy pages
- Basic HTTP for simple pages

Credit: This module uses MediaCrawler (https://github.com/NanmiCoder/MediaCrawler)
        for robust Chinese platform support. Thank you to the MediaCrawler team!
"""

from __future__ import annotations

import json
import subprocess
import urllib.request
from dataclasses import dataclass
from typing import Optional
from extractors import smart_extract
from mediacrawler_adapter import fetch_with_mediacrawler, is_chinese_platform


@dataclass
class FetchResult:
    """Result of a fetch operation"""
    success: bool
    content: Optional[str]
    failure_label: Optional[str] = None
    tool_used: Optional[str] = None
    error_message: Optional[str] = None


def fetch_with_xreach(url: str) -> FetchResult:
    """
    Fetch URL using xreach CLI (for Twitter/X)
    
    xreach is installed via Agent-Reach and provides Twitter/X access
    """
    try:
        # Try to read a tweet
        result = subprocess.run(
            ["xreach", "tweet", url, "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        
        if result.returncode == 0:
            data = json.loads(result.stdout)
            # Extract text content from tweet
            content = data.get("text") or data.get("full_text") or ""
            
            if content and len(content.strip()) > 10:
                return FetchResult(
                    success=True,
                    content=content,
                    tool_used="xreach"
                )
        
        return FetchResult(
            success=False,
            content=None,
            failure_label="xreach_failed",
            tool_used="xreach",
            error_message=result.stderr or "No content extracted"
        )
            
    except FileNotFoundError:
        return FetchResult(
            success=False,
            content=None,
            failure_label="not_implemented",
            tool_used="xreach",
            error_message="xreach not installed (install via Agent-Reach)"
        )
    except subprocess.TimeoutExpired:
        return FetchResult(
            success=False,
            content=None,
            failure_label="timeout",
            tool_used="xreach",
            error_message="Request timed out"
        )
    except Exception as e:
        return FetchResult(
            success=False,
            content=None,
            failure_label="unknown",
            tool_used="xreach",
            error_message=str(e)
        )


def fetch_with_jina(url: str) -> FetchResult:
    """
    Fetch URL using r.jina.ai reader API
    
    Good for JavaScript-heavy pages that return placeholder content
    """
    try:
        jina_url = f"https://r.jina.ai/{url}"
        req = urllib.request.Request(
            jina_url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            content = response.read().decode("utf-8", errors="ignore")
            
            if content and len(content.strip()) > 50:
                return FetchResult(
                    success=True,
                    content=content,
                    tool_used="jina_reader"
                )
            else:
                return FetchResult(
                    success=False,
                    content=None,
                    failure_label="weak_content",
                    tool_used="jina_reader",
                    error_message="Content too short"
                )
                
    except Exception as e:
        return FetchResult(
            success=False,
            content=None,
            failure_label="network_error",
            tool_used="jina_reader",
            error_message=str(e)
        )


def fetch_with_basic_http(url: str) -> FetchResult:
    """
    Fetch URL using basic HTTP request
    
    Good for simple HTML pages
    """
    try:
        req = urllib.request.Request(
            url,
            headers={
                "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
            }
        )
        
        with urllib.request.urlopen(req, timeout=30) as response:
            html = response.read().decode("utf-8", errors="ignore")
            
            if not html or len(html.strip()) < 100:
                return FetchResult(
                    success=False,
                    content=None,
                    failure_label="weak_content",
                    tool_used="basic_http",
                    error_message="Content too short"
                )
            
            # Try platform-specific extraction
            extracted = smart_extract(html, url)
            if extracted:
                return FetchResult(
                    success=True,
                    content=extracted,
                    tool_used="basic_http+extractor"
                )
            
            # Return raw HTML if no extractor available
            return FetchResult(
                success=True,
                content=html,
                tool_used="basic_http"
            )
                
    except Exception as e:
        return FetchResult(
            success=False,
            content=None,
            failure_label="network_error",
            tool_used="basic_http",
            error_message=str(e)
        )


def smart_fetch(url: str, strategy: str = "auto") -> FetchResult:
    """
    Intelligently fetch URL with fallback strategy

    Priority:
    1. MediaCrawler for Chinese platforms (XHS, Zhihu, Douyin, etc.)
    2. xreach for Twitter/X
    3. Jina Reader for JavaScript-heavy pages
    4. Basic HTTP for simple pages

    Args:
        url: URL to fetch
        strategy: "auto", "mediacrawler_first", "xreach_first", "jina_first", "basic_only"

    Returns:
        FetchResult with retrieval details
    """
    retrieval_path = []

    if strategy == "auto":
        # Check if it's a Chinese platform supported by MediaCrawler
        if is_chinese_platform(url):
            strategy = "mediacrawler_first"
        # Auto-detect best strategy based on URL
        elif "x.com" in url or "twitter.com" in url:
            strategy = "xreach_first"
        elif "youtube.com" in url or "youtu.be" in url:
            # For YouTube, we would use yt-dlp, but for now fallback to jina
            strategy = "jina_first"
        else:
            strategy = "basic_first"

    if strategy == "mediacrawler_first":
        # Try MediaCrawler first for Chinese platforms
        mc_result = fetch_with_mediacrawler(url)
        retrieval_path.append(("mediacrawler", mc_result.success))

        if mc_result.success:
            return FetchResult(
                success=True,
                content=mc_result.content,
                tool_used="mediacrawler"
            )

        # Fallback to basic HTTP + extractor
        result = fetch_with_basic_http(url)
        retrieval_path.append(("basic_http", result.success))

        if result.success:
            return result

        # Last resort: Jina Reader
        result = fetch_with_jina(url)
        retrieval_path.append(("jina_reader", result.success))

        if result.success:
            return result

    if strategy == "xreach_first":
        # Try xreach first (for Twitter/X)
        result = fetch_with_xreach(url)
        retrieval_path.append(("xreach", result.success))
        
        if result.success:
            return result
        
        # Fallback to Jina
        result = fetch_with_jina(url)
        retrieval_path.append(("jina_reader", result.success))
        
        if result.success:
            return result
            
    elif strategy == "jina_first":
        # Try Jina first
        result = fetch_with_jina(url)
        retrieval_path.append(("jina_reader", result.success))
        
        if result.success:
            return result
            
    elif strategy == "basic_first" or strategy == "basic_only":
        # Try basic HTTP first
        result = fetch_with_basic_http(url)
        retrieval_path.append(("basic_http", result.success))
        
        if result.success:
            return result
        
        if strategy == "basic_only":
            return result
        
        # Fallback to Jina
        result = fetch_with_jina(url)
        retrieval_path.append(("jina_reader", result.success))
        
        if result.success:
            return result
    
    # All methods failed
    return FetchResult(
        success=False,
        content=None,
        failure_label="all_methods_failed",
        tool_used="multiple",
        error_message=f"Tried: {retrieval_path}"
    )

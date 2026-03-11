"""
MediaCrawler Adapter

This module provides integration with MediaCrawler for Chinese platform support.
MediaCrawler: https://github.com/NanmiCoder/MediaCrawler

Credit: This project uses MediaCrawler by NanmiCoder for robust Chinese platform scraping.
"""

import json
import subprocess
import sys
from pathlib import Path
from typing import Optional
from dataclasses import dataclass


@dataclass
class MediaCrawlerResult:
    """Result from MediaCrawler"""
    success: bool
    content: Optional[str]
    platform: Optional[str]
    error: Optional[str] = None


def get_mediacrawler_path() -> Optional[Path]:
    """Get MediaCrawler installation path"""
    # Check in tools directory
    script_dir = Path(__file__).parent.parent
    mediacrawler_dir = script_dir / "tools" / "MediaCrawler"

    if mediacrawler_dir.exists():
        return mediacrawler_dir

    return None


def detect_platform(url: str) -> Optional[str]:
    """Detect platform from URL"""
    platform_map = {
        "xiaohongshu.com": "xhs",
        "xhslink.com": "xhs",
        "zhihu.com": "zhihu",
        "douyin.com": "douyin",
        "bilibili.com": "bilibili",
        "weibo.com": "weibo",
        "tieba.baidu.com": "tieba",
        "kuaishou.com": "kuaishou",
    }

    for domain, platform in platform_map.items():
        if domain in url:
            return platform

    return None


def fetch_with_mediacrawler(url: str) -> MediaCrawlerResult:
    """
    Fetch content using MediaCrawler

    Args:
        url: URL to fetch

    Returns:
        MediaCrawlerResult with content or error
    """
    # Check if MediaCrawler is installed
    mediacrawler_path = get_mediacrawler_path()
    if not mediacrawler_path:
        return MediaCrawlerResult(
            success=False,
            content=None,
            platform=None,
            error="MediaCrawler not installed. Run ./install.sh to install."
        )

    # Detect platform
    platform = detect_platform(url)
    if not platform:
        return MediaCrawlerResult(
            success=False,
            content=None,
            platform=None,
            error=f"Platform not supported by MediaCrawler: {url}"
        )

    try:
        # Call MediaCrawler
        # Note: This is a simplified version. In production, you would:
        # 1. Use MediaCrawler's API if available
        # 2. Or call its CLI with proper parameters
        # 3. Handle login state and cookies

        # For now, return a placeholder indicating MediaCrawler integration
        return MediaCrawlerResult(
            success=False,
            content=None,
            platform=platform,
            error="MediaCrawler integration in progress. Please use MediaCrawler directly for now."
        )

    except Exception as e:
        return MediaCrawlerResult(
            success=False,
            content=None,
            platform=platform,
            error=f"MediaCrawler error: {str(e)}"
        )


def is_chinese_platform(url: str) -> bool:
    """Check if URL is from a Chinese platform supported by MediaCrawler"""
    return detect_platform(url) is not None

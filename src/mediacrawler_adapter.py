"""
MediaCrawler Adapter

This module provides integration with MediaCrawler for Chinese platform support.
MediaCrawler: https://github.com/NanmiCoder/MediaCrawler

Credit: This project uses MediaCrawler by NanmiCoder for robust Chinese platform scraping.
"""

import json
import os
import re
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from typing import Optional, Dict
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
    """
    Detect platform from URL

    Returns MediaCrawler platform code (xhs, dy, ks, bili, wb, tieba, zhihu)
    """
    platform_map = {
        "xiaohongshu.com": "xhs",
        "xhslink.com": "xhs",
        "zhihu.com": "zhihu",
        "douyin.com": "dy",
        "bilibili.com": "bili",
        "weibo.com": "wb",
        "tieba.baidu.com": "tieba",
        "kuaishou.com": "ks",
    }

    for domain, platform in platform_map.items():
        if domain in url:
            return platform

    return None


def extract_note_id(url: str, platform: str) -> Optional[str]:
    """
    Extract note/post ID from URL

    Different platforms have different URL structures:
    - 小红书: /explore/xxxxx or /discovery/item/xxxxx
    - 知乎: /question/xxxxx or /p/xxxxx
    - 抖音: /video/xxxxx
    - B站: /video/BVxxxxx
    - 微博: /xxxxx/xxxxx
    """
    patterns = {
        "xhs": r"(?:explore|discovery/item)/([a-f0-9]+)",
        "zhihu": r"(?:question|p|answer)/(\d+)",
        "dy": r"/video/(\d+)",
        "bili": r"/video/(BV\w+)",
        "wb": r"/(\d+)/(\w+)",
        "tieba": r"/p/(\d+)",
        "ks": r"/video/(\w+)",
    }

    pattern = patterns.get(platform)
    if not pattern:
        return None

    match = re.search(pattern, url)
    if match:
        return match.group(1)

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

    # Extract note ID
    note_id = extract_note_id(url, platform)
    if not note_id:
        return MediaCrawlerResult(
            success=False,
            content=None,
            platform=platform,
            error=f"Could not extract note ID from URL: {url}"
        )

    try:
        # Call MediaCrawler to fetch the specific note
        result = _run_mediacrawler(mediacrawler_path, platform, note_id)
        return result

    except Exception as e:
        return MediaCrawlerResult(
            success=False,
            content=None,
            platform=platform,
            error=f"MediaCrawler error: {str(e)}"
        )


def _run_mediacrawler(mediacrawler_path: Path, platform: str, note_id: str) -> MediaCrawlerResult:
    """
    Run MediaCrawler to fetch specific note content

    MediaCrawler requires:
    1. Browser automation (Playwright)
    2. Login state (cookies or QR code login)
    3. Platform-specific configuration

    Due to these requirements, MediaCrawler is best used as a standalone tool.
    This adapter provides graceful degradation and clear setup instructions.
    """
    import shutil

    # Create temporary directory for this crawl
    temp_dir = Path(tempfile.mkdtemp(prefix="mediacrawler_"))
    output_file = temp_dir / "output.jsonl"

    # Check if MediaCrawler is properly set up
    config_file = mediacrawler_path / "config" / "base_config.py"
    if not config_file.exists():
        return MediaCrawlerResult(
            success=False,
            content=None,
            platform=platform,
            error=(
                f"MediaCrawler not fully installed.\n"
                f"Run: cd {mediacrawler_path} && pip install -r requirements.txt"
            )
        )

    # MediaCrawler requires login state and browser automation
    # For now, we return a helpful message explaining the limitation
    platform_names = {
        "xhs": "小红书 (Xiaohongshu)",
        "zhihu": "知乎 (Zhihu)",
        "dy": "抖音 (Douyin)",
        "bili": "B站 (Bilibili)",
        "wb": "微博 (Weibo)",
        "tieba": "贴吧 (Tieba)",
        "ks": "快手 (Kuaishou)",
    }

    platform_name = platform_names.get(platform, platform)

    return MediaCrawlerResult(
        success=False,
        content=None,
        platform=platform,
        error=(
            f"MediaCrawler requires manual setup for {platform_name}.\n\n"
            f"MediaCrawler uses browser automation and requires login state.\n"
            f"To use MediaCrawler for this platform:\n\n"
            f"1. cd {mediacrawler_path}\n"
            f"2. Edit config/base_config.py:\n"
            f"   PLATFORM = \"{platform}\"\n"
            f"   CRAWLER_TYPE = \"detail\"\n"
            f"   # Add note ID to detail list\n\n"
            f"3. Run: python main.py\n"
            f"   (First run will prompt for login)\n\n"
            f"Note: This skill will fall back to other methods automatically."
        )
    )


def is_chinese_platform(url: str) -> bool:
    """Check if URL is from a Chinese platform supported by MediaCrawler"""
    return detect_platform(url) is not None

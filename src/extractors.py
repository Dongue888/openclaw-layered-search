"""
Content extractors for platform-specific pages
"""

import json
import re
from typing import Optional


def extract_xhs_content(html: str) -> Optional[str]:
    """
    Extract content from Xiaohongshu (小红书) HTML
    
    XHS embeds data in window.__INITIAL_STATE__
    """
    try:
        # Find the __INITIAL_STATE__ data
        pattern = r"window\.__INITIAL_STATE__\s*=\s*(.+?)(?:</script>|;)"
        match = re.search(pattern, html, re.DOTALL)
        
        if not match:
            return None
        
        data_str = match.group(1).strip()
        
        # Remove trailing semicolon if present
        if data_str.endswith(";"):
            data_str = data_str[:-1]
        
        # Parse JSON
        data = json.loads(data_str)
        
        # Extract note content
        # Try different paths in the data structure
        note_detail_map = data.get("note", {}).get("noteDetailMap", {})
        
        if not note_detail_map:
            return None
        
        # Get first note
        note_id = list(note_detail_map.keys())[0]
        note_data = note_detail_map[note_id]
        
        # Extract note object
        note = note_data.get("note", {})
        
        # Extract fields
        title = note.get("title", "")
        desc = note.get("desc", "")
        
        # Get user info
        user = note.get("user", {})
        nickname = user.get("nickname", "")
        
        # Combine content
        parts = []
        if title:
            parts.append(f"标题: {title}")
        if nickname:
            parts.append(f"作者: {nickname}")
        if desc:
            parts.append(f"\n内容:\n{desc}")
        
        content = "\n".join(parts)
        
        return content if content else None
        
    except json.JSONDecodeError as e:
        # Try to find where JSON parsing failed
        print(f"XHS JSON parse error at position {e.pos}: {e.msg}")
        return None
    except Exception as e:
        print(f"XHS extraction error: {e}")
        return None


def smart_extract(html: str, url: str) -> Optional[str]:
    """
    Intelligently extract content based on URL
    """
    if "xiaohongshu.com" in url or "xhslink.com" in url:
        return extract_xhs_content(html)
    
    return None

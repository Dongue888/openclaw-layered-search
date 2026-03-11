#!/usr/bin/env python3
"""
Test MediaCrawler integration
"""
import sys
sys.path.insert(0, 'src')

from mediacrawler_adapter import fetch_with_mediacrawler, detect_platform, extract_note_id

# Test URLs
test_urls = [
    ('https://www.xiaohongshu.com/explore/66f7f5e5000000001e03a1e9', '小红书'),
    ('https://www.zhihu.com/question/19551626/answer/12240320', '知乎'),
    ('https://mp.weixin.qq.com/s/Ky-Aw-8xKdQxLKLLQqJYqA', '微信公众号'),
]

print("="*70)
print("MediaCrawler Integration Test")
print("="*70)

for url, name in test_urls:
    print(f"\n{name}: {url[:60]}...")
    print("-"*70)

    # Detect platform
    platform = detect_platform(url)
    print(f"Platform detected: {platform}")

    if platform:
        # Extract note ID
        note_id = extract_note_id(url, platform)
        print(f"Note ID: {note_id}")

        # Try to fetch
        result = fetch_with_mediacrawler(url)
        print(f"Success: {result.success}")
        if result.content:
            print(f"Content length: {len(result.content)}")
        if result.error:
            # Print first 300 chars of error
            error_preview = result.error[:300] + "..." if len(result.error) > 300 else result.error
            print(f"Error:\n{error_preview}")
    else:
        print("Not a Chinese platform supported by MediaCrawler")

    print()

print("="*70)
print("Test complete")
print("="*70)

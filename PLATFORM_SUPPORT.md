# Platform Support Matrix

## Test Results (2026-03-11)

| Platform | Basic Install | With Agent-Reach | Notes |
|----------|---------------|------------------|-------|
| **微信公众号** | ✅ Full support | ✅ Full support | Works perfectly out of the box |
| **小红书 (XHS)** | ⚠️ Partial | ✅ Full support | Basic: gets HTML but needs extraction<br>Agent-Reach: clean content |
| **知乎 (Zhihu)** | ❌ Blocked | ⚠️ May work | 403 anti-scraping, needs Agent-Reach or proxy |
| **Twitter/X** | ⚠️ Placeholder | ✅ Full support | Basic: JS placeholder<br>Agent-Reach: full tweets |
| **普通网页** | ✅ Full support | ✅ Full support | News, blogs, docs work great |

## Detailed Analysis

### ✅ Works Out of the Box

**微信公众号 (WeChat Official Accounts)**
- Status: ✅ Perfect
- Tool: basic_http
- Content: Full HTML, clean extraction
- No additional setup needed

**普通网页 (Regular Websites)**
- Status: ✅ Excellent
- Tool: basic_http + Jina Reader fallback
- Content: Most news sites, blogs, documentation
- No additional setup needed

### ⚠️ Partial Support (Needs Agent-Reach for Best Results)

**小红书 (Xiaohongshu)**
- Basic Install:
  - ⚠️ Gets HTML (494KB)
  - ⚠️ Content embedded in JS
  - ⚠️ Extraction partially works
- With Agent-Reach:
  - ✅ Clean extracted content
  - ✅ Title, author, description
  - ✅ No HTML noise

**Recommendation:** Install Agent-Reach for production use

### ❌ Requires Agent-Reach

**知乎 (Zhihu)**
- Basic Install:
  - ❌ 403 Forbidden (anti-scraping)
  - ❌ Jina Reader times out
- With Agent-Reach:
  - ⚠️ May work (needs testing)
  - ⚠️ May need proxy

**Recommendation:** Must install Agent-Reach, possibly with proxy

**Twitter/X**
- Basic Install:
  - ⚠️ Gets JavaScript placeholder
  - ⚠️ No actual tweet content
- With Agent-Reach (xreach):
  - ✅ Full tweet text
  - ✅ Metadata
  - ✅ Thread support

**Recommendation:** Must install Agent-Reach for Twitter support

## Installation Guide

### Minimal (Works for 60% of use cases)

```bash
pip install -r requirements.txt
```

**You get:**
- ✅ WeChat Official Accounts
- ✅ Regular websites
- ⚠️ Partial XHS support
- ❌ No Zhihu
- ❌ No Twitter

### Complete (Works for 95% of use cases)

```bash
# Install base
pip install -r requirements.txt

# Install Agent-Reach
pip install https://github.com/Panniantong/agent-reach/archive/main.zip
agent-reach install --env=auto

# Configure platforms (optional, for authenticated access)
agent-reach configure xiaohongshu-cookies "your-cookies"
agent-reach configure twitter-cookies "your-cookies"
```

**You get:**
- ✅ Everything from minimal
- ✅ Full XHS support
- ⚠️ Zhihu (may need proxy)
- ✅ Twitter/X
- ✅ 10+ other platforms

## Quick Decision Guide

**"I just want to try it"**
→ Minimal install
→ Test with WeChat articles and regular websites

**"I need XHS or Twitter"**
→ Complete install
→ Configure Agent-Reach

**"I need Zhihu"**
→ Complete install + proxy
→ May need additional configuration

## Future Improvements

Planned enhancements to reduce dependencies:

- [ ] Better XHS content extraction (without Agent-Reach)
- [ ] Playwright fallback for anti-scraping sites
- [ ] Docker image with everything pre-installed
- [ ] One-command setup script

## Testing

To test platform support on your system:

```bash
cd openclaw-layered-search
python3 test_integration.py
```

This will show which platforms work with your current setup.

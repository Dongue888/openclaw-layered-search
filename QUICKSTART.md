# Quick Start for OpenClaw Users

## What is this?

A skill that helps OpenClaw intelligently fetch content from **any URL** you send it - whether through Feishu, Telegram, or direct chat.

**Supports Chinese platforms out of the box:** 小红书, 知乎, 抖音, B站, 微博, 贴吧, 快手

## Installation (One Command)

```bash
# Clone and install
git clone https://github.com/Dongue888/openclaw-layered-search.git ~/.openclaw/skills/openclaw-layered-search
cd ~/.openclaw/skills/openclaw-layered-search
./install.sh
```

The install script will automatically:
- Install Python dependencies
- Install MediaCrawler for Chinese platform support
- Install Playwright browsers
- Set up everything you need

## Usage

Just send a URL to OpenClaw:

**Example 1: WeChat Article**
```
You: "帮我看看这个链接的内容 https://mp.weixin.qq.com/s/xxx"

OpenClaw: [Automatically fetches and summarizes the content]
```

**Example 2: Xiaohongshu Post**
```
You: "总结一下这个小红书笔记 http://xhslink.com/xxx"

OpenClaw: [Uses MediaCrawler to fetch and summarize]
```

**Example 3: Zhihu Answer**
```
You: "这个知乎回答说了什么？https://www.zhihu.com/question/xxx"

OpenClaw: [Fetches and summarizes the answer]
```

## Supported Platforms

### ✅ Works Out of the Box

**Chinese Platforms (via MediaCrawler):**
- 小红书 (Xiaohongshu)
- 知乎 (Zhihu)
- 抖音 (Douyin)
- B站 (Bilibili)
- 微博 (Weibo)
- 贴吧 (Tieba)
- 快手 (Kuaishou)

**International Platforms:**
- WeChat Official Accounts (微信公众号)
- Regular websites (news, blogs, docs)
- Most HTTP/HTTPS pages

### ⚡ Enhanced with Optional Tools

- Twitter/X (install Agent-Reach)
- YouTube (install Agent-Reach)

## How It Works

1. **Smart Detection**: Automatically detects URL type
2. **Intelligent Routing**:
   - Chinese platforms → MediaCrawler
   - Twitter/X → xreach
   - Others → Basic HTTP + Jina Reader
3. **Graceful Fallback**: If one method fails, tries alternatives
4. **Evidence Tracking**: Records what worked and what didn't

## Troubleshooting

**Q: Installation failed?**
A: Make sure you have Python 3.8+ and Node.js installed

**Q: Chinese platform not working?**
A: MediaCrawler may need login for some platforms. Check MediaCrawler docs for setup.

**Q: How to update?**
```bash
cd ~/.openclaw/skills/openclaw-layered-search
git pull
./install.sh
```

## Credits

This skill uses **[MediaCrawler](https://github.com/NanmiCoder/MediaCrawler)** (45K+ ⭐) by NanmiCoder for Chinese platform support. Thank you to the MediaCrawler team!

## For Developers

See [INTEGRATION.md](INTEGRATION.md) for technical details.

## License

MIT

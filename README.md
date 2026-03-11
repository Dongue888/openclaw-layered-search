# OpenClaw Layered Search

**Intelligent retrieval orchestration for OpenClaw agents.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

> Give any URL to OpenClaw, get intelligent content retrieval with automatic fallback strategies.

## 🎯 For OpenClaw Users

**Just want to use it?** → See [QUICKSTART.md](QUICKSTART.md)

Send any link to OpenClaw (via Feishu, Telegram, or chat), and it will:
- ✅ Automatically detect the best way to fetch content
- ✅ Try multiple methods if one fails
- ✅ Summarize the content for you
- ✅ **Support Chinese platforms out of the box** (小红书, 知乎, 抖音, B站, 微博, 贴吧, 快手)

## 🚀 Quick Install

```bash
git clone https://github.com/Dongue888/openclaw-layered-search.git ~/.openclaw/skills/openclaw-layered-search
cd ~/.openclaw/skills/openclaw-layered-search
./install.sh
```

Then just send a URL to OpenClaw!

## 🙏 Credits

This project integrates **[MediaCrawler](https://github.com/NanmiCoder/MediaCrawler)** (45K+ ⭐) by NanmiCoder for robust Chinese platform support. Thank you to the MediaCrawler team for their excellent work!

---

## Why this exists

New OpenClaw users often hit the same problem:

- they do not know which tool should be used for a link
- the agent sometimes guesses when a page could not really be fetched
- dynamic / social pages return placeholder content
- fallback paths are not obvious

This project tries to solve that with a simple layered pipeline:

1. **Input understanding**
2. **Retrieval planning**
3. **Execution + fallback**
4. **Grounded synthesis**

---

## Architecture: Orchestration Layer, Not Tool Layer

OpenClaw Layered Search sits **above** existing retrieval tools.
We do not replace them — we orchestrate them.

```
┌─────────────────────────────────────────────────────────┐
│ OpenClaw Layered Search (Orchestration Layer)          │
│                                                         │
│  ├─ Input Understanding (URL / Topic / Mixed)          │
│  ├─ Strategy Planning (which tool, in what order)      │
│  ├─ Failure Handling (classify failure + fallback)     │
│  └─ Evidence Tracking (retrieval_path + uncertainties) │
└─────────────────────────────────────────────────────────┘
                         ↓ delegates to
┌─────────────────────────────────────────────────────────┐
│ Tool Layer                                              │
│                                                         │
│  ├─ ask-search (search aggregation via SearxNG)        │
│  ├─ Agent-Reach (platform scraping: X, 小红书, etc)     │
│  └─ web_fetch / r.jina.ai (basic HTTP + reader)        │
└─────────────────────────────────────────────────────────┘
```

**Key insight:**
The hard problem is not "can I scrape this URL?"
The hard problem is "how should I answer this question?"

---

## What makes this different?

### Without OpenClaw Layered Search

User asks: *"小红书上大家怎么评价 iPhone 16？这里有篇测评 [URL]"*

Agent needs to manually:
1. Decide: is this a URL task or a search task? (it's both)
2. Choose: which tool for the URL? (agent-reach? web_fetch? jina?)
3. Handle: URL fetch failed — now what?
4. Decide: do I need to search? or is the URL enough?
5. Choose: which URLs from search results are worth fetching?
6. Combine: how do I merge info from multiple sources?

**Result:** Agent guesses, hallucinates, or gives up.

### With OpenClaw Layered Search

```bash
openclaw-search "小红书上大家怎么评价 iPhone 16？这里有篇测评 [URL]"
```

System automatically:
1. ✅ Detects **mixed mode** (topic + reference URL)
2. ✅ Prioritizes user-provided URL first
3. ✅ Tries `agent-reach` → falls back to `jina` if blocked
4. ✅ Records failure reason: `blocked_placeholder`
5. ✅ Decides: "URL content is weak, expand search"
6. ✅ Calls `ask-search` for candidates
7. ✅ Ranks and selects top sources
8. ✅ Fetches in parallel with failure tracking
9. ✅ Returns structured report with evidence trail

**Result:** Agent knows what happened, why, and what to do next.

---

## Feature comparison

| Capability | Agent-Reach | ask-search | **This Project** |
|------------|-------------|------------|------------------|
| **Input understanding** | ❌ URL only | ❌ Query only | ✅ Auto-detect URL/Topic/Mixed |
| **Strategy planning** | ❌ User specifies tool | ❌ Search only | ✅ Auto-select tool + order |
| **Failure tracking** | ❌ Success/fail only | ❌ No failure handling | ✅ Classify failure + record path |
| **Intelligent fallback** | ❌ None | ❌ None | ✅ Failure-aware fallback |
| **Multi-source fusion** | ❌ Single source per call | ❌ Returns search results | ✅ Mixed mode priority handling |
| **Evidence tracking** | ❌ Black box | ❌ Black box | ✅ `retrieval_path` + `uncertainties` |
| **Explainability** | ❌ No | ❌ No | ✅ Tells agent "what happened" |

**We stand on the shoulders of giants:**
- `ask-search` solves: "give me search results"
- `Agent-Reach` solves: "fetch this URL"
- **This project** solves: "how should I answer this question?"

---

## What works today

### 1. Article links
- direct HTML fetch
- title extraction
- noisy page cleanup
- grounded summary from extracted content

### 2. X / Twitter links
- detect JavaScript placeholder pages
- mark them as blocked placeholder failures
- fallback to `r.jina.ai`
- extract clean post body from the fallback result

### 3. Topic mode (basic MVP)
- search-first flow for topic input
- candidate source discovery
- selected-source fetch
- structured topic summary
- visible candidate source list in CLI output

### 4. Mixed mode (topic + references)
- detect mixed input automatically
- prioritize user-provided reference links first
- summarize from retrieved references before expanding search
- suggest search expansion only when broader coverage is needed

### 5. Failure-aware behavior
The prototype records:
- retrieval path
- candidate sources
- successful sources
- failed sources
- failure labels
- uncertainties
- next actions

---

## Current project structure

```text
openclaw-layered-search/
├── README.md
├── .gitignore
├── skill/
│   └── SKILL.md
├── src/
│   ├── pipeline.py
│   ├── router.py
│   ├── schemas.py
│   └── summarize.py
└── tests/
    ├── test_pipeline.py
    └── test_router.py
```

---

## Quick demo

### Demo 1: normal article page

```bash
cd src
python3 pipeline.py "https://www.stcn.com/article/detail/3666565.html"
```

Expected behavior:
- use `web_fetch`
- extract title + article body
- produce grounded summary

### Demo 2: X/Twitter post

```bash
cd src
python3 pipeline.py "https://x.com/jain_web3/status/2029428696646598883"
```

Expected behavior:
- `web_fetch` sees JavaScript placeholder content
- mark failure as `blocked_placeholder`
- fallback to `r.jina.ai`
- extract the post body only

### Demo 3: topic mode

```bash
cd src
python3 cli.py "OpenClaw Layered Search"
```

Expected behavior:
- search candidate sources first
- show which candidates were selected for fetch
- fetch top sources
- produce a structured topic summary

### Demo 4: mixed mode

```bash
cd src
python3 cli.py "OpenClaw Layered Search https://www.stcn.com/article/detail/3666565.html https://x.com/jain_web3/status/2029428696646598883"
```

Expected behavior:
- detect both topic and reference URLs
- fetch the provided references first
- summarize from those references
- suggest broader search only as a next step

---

## Output shape

The prototype returns structured JSON like this:

```json
{
  "input_type": "url",
  "retrieval_path": ["web_fetch", "r.jina.ai", "browser"],
  "sources_retrieved": [],
  "sources_failed": [],
  "summary": "...",
  "uncertainties": [],
  "next_actions": []
}
```

This is intentional.
The system should first know **what happened during retrieval** before generating polished prose.

---

## Failure labels

Current labels include:
- `blocked_placeholder`
- `weak_content`
- `login_wall`
- `network_error`
- `not_implemented`
- `unknown`

These labels are used to decide fallback behavior and to explain limitations honestly.

---

## Input modes

Current MVP supports:
- **single URL** — best for direct source retrieval
- **topic** — best for candidate discovery + fetch
- **mixed (topic + references)** — best for real research workflows where the user already has a few seed links

---

## Run tests

```bash
cd openclaw-layered-search
pytest -q tests/test_router.py tests/test_pipeline.py
```

Or use the included Makefile:

```bash
make test
make demo-article
make demo-x
make demo-topic
```

---

## Current limitations

This is still an MVP prototype.

Not done yet:
- full integration with ask-search and Agent-Reach
- browser fallback implementation
- topic-mode complete search flow
- multi-link synthesis optimization
- richer output rendering
- OpenClaw-native tool wiring instead of local prototype behavior

---

## Direction

The project goal is not "more scraping".
The goal is:

> **Teach OpenClaw agents how to retrieve information more reliably before they answer.**

That means:
- use the right tool in the right order
- fallback sanely
- do not pretend retrieval succeeded
- ground summaries in retrieved evidence

---

## Installation

### Quick Start (5 minutes)

```bash
git clone <your-repo-url> openclaw-layered-search
cd openclaw-layered-search
pip install -r requirements.txt
```

**This gives you core functionality that works immediately.**

For platform-specific features (Twitter, 小红书, etc), see [FEATURES.md](FEATURES.md) and [INSTALL.md](INSTALL.md).

---

## Dependencies

This project builds on top of excellent open-source tools:

- **[ask-search](https://github.com/ythx-101/ask-search)** — self-hosted web search via SearxNG
- **[Agent-Reach](https://github.com/Panniantong/Agent-Reach)** — platform-specific scraping (Twitter, 小红书, etc)
- **r.jina.ai** — reader API for JavaScript-heavy pages

We orchestrate these tools to provide intelligent retrieval planning.

---

## License

MIT

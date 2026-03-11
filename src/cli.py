from __future__ import annotations

import json
import sys
from pathlib import Path

from pipeline import run


def render(result) -> str:
    lines = []
    lines.append("OpenClaw Layered Search")
    lines.append("=" * 24)
    lines.append(f"input_type: {result.input_type}")
    lines.append(f"retrieval_path: {' -> '.join(result.retrieval_path)}")
    lines.append("")

    if getattr(result, 'candidate_sources', None):
        lines.append("candidate_sources:")
        for src in result.candidate_sources:
            mark = "*" if src.selected else "-"
            title = src.title or src.url
            note = f" ({src.note})" if src.note else ""
            lines.append(f"{mark} {title}{note}")
            lines.append(f"  {src.url}")
        lines.append("")

    if result.sources_retrieved:
        lines.append("retrieved:")
        for src in result.sources_retrieved:
            title = f" | title={src.title}" if src.title else ""
            lines.append(f"- {src.method}: {src.url}{title}")
        lines.append("")

    if result.sources_failed:
        lines.append("failed:")
        for src in result.sources_failed:
            label = f" [{src.failure_label}]" if src.failure_label else ""
            reason = f" — {src.reason}" if src.reason else ""
            lines.append(f"- {src.method}: {src.url}{label}{reason}")
        lines.append("")

    lines.append("summary:")
    lines.append(result.summary.strip() or "(empty)")
    lines.append("")

    if result.uncertainties:
        lines.append("uncertainties:")
        for item in result.uncertainties:
            lines.append(f"- {item}")
        lines.append("")

    if result.next_actions:
        lines.append("next_actions:")
        for item in result.next_actions:
            lines.append(f"- {item}")
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    raw = " ".join(sys.argv[1:]).strip()
    if not raw:
        print("Usage: python3 src/cli.py \"<url-or-topic>\"")
        return 1
    result = run(raw)
    print(render(result))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

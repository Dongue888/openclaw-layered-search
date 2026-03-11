from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Literal, Optional

InputType = Literal["url", "urls", "topic", "mixed"]
GoalType = Literal["summarize", "verify", "research", "ideate"]
SourceStatus = Literal["success", "failed"]
FailureLabel = Literal[
    "weak_content",
    "blocked_placeholder",
    "shell_page",
    "login_wall",
    "dynamic_page",
    "network_error",
    "not_implemented",
    "unknown",
]


@dataclass
class Task:
    input_type: InputType
    goal: GoalType = "summarize"
    url: Optional[str] = None
    urls: List[str] = field(default_factory=list)
    topic: Optional[str] = None
    references: List[str] = field(default_factory=list)


@dataclass
class SourceRecord:
    url: str
    method: str
    status: SourceStatus
    title: Optional[str] = None
    content: Optional[str] = None
    reason: Optional[str] = None
    failure_label: Optional[FailureLabel] = None


@dataclass
class CandidateSource:
    url: str
    title: Optional[str] = None
    snippet: Optional[str] = None
    selected: bool = False
    note: Optional[str] = None


@dataclass
class PipelineResult:
    input_type: InputType
    retrieval_path: List[str] = field(default_factory=list)
    candidate_sources: List[CandidateSource] = field(default_factory=list)
    sources_retrieved: List[SourceRecord] = field(default_factory=list)
    sources_failed: List[SourceRecord] = field(default_factory=list)
    summary: str = ""
    uncertainties: List[str] = field(default_factory=list)
    next_actions: List[str] = field(default_factory=list)

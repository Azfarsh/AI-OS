"""Intelligent model routing by task type."""

from __future__ import annotations

import re
from enum import Enum

from ais_os.config import get_config


class TaskType(str, Enum):
    CHAT = "chat"
    CODE = "code"
    RESEARCH = "research"
    PLANNING = "planning"
    FAST = "fast"
    LOCAL = "local"


_CODE_PATTERNS = re.compile(
    r"\b(code|debug|refactor|implement|function|class|bug|pytest|git diff|compile)\b",
    re.I,
)
_RESEARCH_PATTERNS = re.compile(
    r"\b(research|analyze|compare|summarize|report|market|competitor|paper)\b",
    re.I,
)
_PLAN_PATTERNS = re.compile(
    r"\b(plan|roadmap|strategy|architecture|design|orchestrat|delegate)\b",
    re.I,
)


class ModelRouter:
    """Pick the best model for a user message and optional explicit task type."""

    def __init__(self) -> None:
        cfg = get_config()
        self._routing = cfg.model_routing
        self._default = cfg.default_model

    def classify(self, message: str) -> TaskType:
        if _CODE_PATTERNS.search(message):
            return TaskType.CODE
        if _RESEARCH_PATTERNS.search(message):
            return TaskType.RESEARCH
        if _PLAN_PATTERNS.search(message):
            return TaskType.PLANNING
        if len(message) < 80:
            return TaskType.FAST
        return TaskType.CHAT

    def resolve(
        self,
        message: str,
        *,
        task_type: TaskType | None = None,
        model_override: str | None = None,
    ) -> str:
        if model_override:
            return model_override
        tt = task_type or self.classify(message)
        return self._routing.get(tt.value, self._default)

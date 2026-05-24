"""Canonical lead schema for Agency OS memory files."""

from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from pydantic import BaseModel, Field


def slugify(name: str, company: str) -> str:
    raw = f"{name}-{company}".lower()
    raw = re.sub(r"[^a-z0-9]+", "-", raw).strip("-")
    return raw[:80] or "unknown-lead"


class LeadInput(BaseModel):
    name: str
    email: str
    company: str
    role: str = ""
    phone: str = ""
    linkedin: str = ""
    source: str = "manual"
    industry: str = ""
    company_size: str = ""
    tech_stack: str = ""
    revenue_signals: str = ""
    notes: str = ""

    def slug(self) -> str:
        return slugify(self.name, self.company)

    def to_profile_dict(self) -> dict[str, Any]:
        return self.model_dump()


class LeadScores(BaseModel):
    fit_score: int = 0
    intent_score: int = 0
    rationale: str = ""
    top_signal: str = ""
    risk: str = ""

    @property
    def combined(self) -> float:
        return (self.fit_score + self.intent_score) / 2.0


class LeadRecord(BaseModel):
    lead: LeadInput
    scores: LeadScores
    status: str  # qualified | disqualified
    threshold: int
    qualified_on: str = Field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

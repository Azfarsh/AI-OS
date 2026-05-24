"""Apply qualification threshold."""

from __future__ import annotations

from ais_os.config import get_config
from ais_os.skills.lead_schema import LeadScores


def get_threshold() -> int:
    cfg = get_config()
    agency = cfg.yaml_section("agency") or {}
    return int(agency.get("qualification_threshold", 70))


def qualify_lead(scores: LeadScores, threshold: int | None = None) -> bool:
    t = threshold if threshold is not None else get_threshold()
    return scores.combined >= t

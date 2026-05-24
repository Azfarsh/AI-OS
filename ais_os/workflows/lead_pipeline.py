"""Loop 1 — Lead acquisition pipeline (Phase 0 + Phase 1)."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from ais_os.skills.deduplicate_lead import is_duplicate
from ais_os.skills.lead_schema import LeadInput
from ais_os.skills.qualify_lead import get_threshold, qualify_lead
from ais_os.skills.score_lead import score_lead
from ais_os.skills.write_lead_memory import write_lead_memory

logger = logging.getLogger("ais_os.workflows.lead_pipeline")


@dataclass
class PipelineResult:
    lead: LeadInput
    status: str  # qualified | disqualified | duplicate | error
    scores: Any = None
    memory_path: str | None = None
    message: str = ""


async def run_lead_pipeline(lead: LeadInput, *, threshold: int | None = None) -> PipelineResult:
    dup, existing = is_duplicate(lead.email, lead.company)
    if dup:
        return PipelineResult(
            lead=lead,
            status="duplicate",
            message=f"Already in memory/leads/ ({existing})",
        )

    t = threshold if threshold is not None else get_threshold()
    try:
        scores = await score_lead(lead)
    except Exception as exc:
        logger.exception("score_lead failed")
        return PipelineResult(lead=lead, status="error", message=str(exc))

    qualified = qualify_lead(scores, t)
    status = "qualified" if qualified else "disqualified"
    path = write_lead_memory(lead, scores, status=status, threshold=t)
    _append_pipeline_row(lead, scores, status)

    crm_note = ""
    if qualified:
        crm_note = " Next: wire Freshsales + Instantly (see CREDENTIALS.md)."

    return PipelineResult(
        lead=lead,
        status=status,
        scores=scores,
        memory_path=str(path),
        message=f"Wrote {path.name}. fit={scores.fit_score} intent={scores.intent_score} -> {status}.{crm_note}",
    )


def _append_pipeline_row(lead: LeadInput, scores: Any, status: str) -> None:
    from ais_os.config import get_config

    path = get_config().workspace / "memory" / "context" / "active_pipeline.md"
    if not path.exists():
        return
    line = (
        f"| {lead.slug()}.md | {status} | {scores.fit_score} | {scores.intent_score} "
        f"| Review memory/leads/{lead.slug()}.md |"
    )
    text = path.read_text(encoding="utf-8")
    if "_empty_" in text:
        text = text.replace("| _empty_ | — | — | — | — |", line)
    elif lead.slug() not in text:
        text = text.rstrip() + "\n" + line + "\n"
    path.write_text(text, encoding="utf-8")

"""Write memory/leads/{slug}.md — Agency OS canonical format."""

from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path

from ais_os.skills.deduplicate_lead import leads_dir
from ais_os.skills.lead_schema import LeadInput, LeadRecord, LeadScores


def render_lead_markdown(record: LeadRecord) -> str:
    lead = record.lead
    s = record.scores
    status = record.status
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    return f"""# Lead: {lead.name} @ {lead.company}

## Identity
- Name: {lead.name}
- Email: {lead.email}
- Role: {lead.role or "—"}
- Company: {lead.company}
- LinkedIn: {lead.linkedin or "—"}
- Phone: {lead.phone or "—"}

## Enrichment
- Company size: {lead.company_size or "—"}
- Industry: {lead.industry or "—"}
- Tech stack: {lead.tech_stack or "—"}
- Revenue signals: {lead.revenue_signals or "—"}
- Enriched on: {now}
- Source: {lead.source}
- Notes: {lead.notes or "—"}

## Scoring
- Fit score: {s.fit_score}/100
- Intent score: {s.intent_score}/100
- Combined: {s.combined:.1f}/100
- Rationale: {s.rationale}
- Top signal: {s.top_signal}
- Risk: {s.risk}

## Qualification
- Status: {status}
- Qualified on: {record.qualified_on}
- Threshold applied: {record.threshold}

## Outreach
- Freshsales CRM ID: _not connected — add FRESHSALES_API_KEY in .env_
- Instantly sequence: _not connected_
- Sequence triggered: —
- Last touchpoint: —
- Next action: {"Start outreach sequence" if status == "qualified" else "Archive or nurture"}

## Call intelligence
- tl;dv URL: —
- Call date: —
- Key signals: —
- Next action: —

## Activity log
- {now} Lead processed via AIS-OS lead pipeline
- {now} AI scored: fit={s.fit_score}, intent={s.intent_score}
- {now} Status set to {status} (threshold: {record.threshold})
"""


def write_lead_memory(
    lead: LeadInput,
    scores: LeadScores,
    *,
    status: str,
    threshold: int,
) -> Path:
    directory = leads_dir()
    directory.mkdir(parents=True, exist_ok=True)
    record = LeadRecord(
        lead=lead,
        scores=scores,
        status=status,
        threshold=threshold,
    )
    path = directory / f"{lead.slug()}.md"
    path.write_text(render_lead_markdown(record), encoding="utf-8")
    return path

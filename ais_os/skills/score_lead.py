"""LLM lead scoring using prompts/lead_scoring.md."""

from __future__ import annotations

import json
import logging
import re

from ais_os.config import get_config
from ais_os.models.openrouter import OpenRouterClient
from ais_os.skills.lead_schema import LeadInput, LeadScores

logger = logging.getLogger("ais_os.skills.score_lead")


def _load_prompt() -> str:
    path = get_config().workspace / "prompts" / "lead_scoring.md"
    return path.read_text(encoding="utf-8")


def _parse_json(raw: str) -> dict:
    raw = raw.strip()
    match = re.search(r"\{[\s\S]*\}", raw)
    if match:
        raw = match.group(0)
    return json.loads(raw)


async def score_lead(lead: LeadInput, *, model: str | None = None) -> LeadScores:
    cfg = get_config()
    prompt_template = _load_prompt()
    lead_json = json.dumps(lead.to_profile_dict(), indent=2)
    prompt = prompt_template.replace("{lead_json}", lead_json)
    llm = OpenRouterClient()
    use_model = model or cfg.default_model
    raw = await llm.chat(
        [
            {"role": "system", "content": "Return only valid JSON. No markdown fences."},
            {"role": "user", "content": prompt},
        ],
        model=use_model,
        temperature=0.2,
        max_tokens=800,
        tools=None,
    )
    try:
        data = _parse_json(raw)
        return LeadScores(
            fit_score=int(data.get("fit_score", 0)),
            intent_score=int(data.get("intent_score", 0)),
            rationale=str(data.get("rationale", "")),
            top_signal=str(data.get("top_signal", "")),
            risk=str(data.get("risk", "")),
        )
    except (json.JSONDecodeError, TypeError, ValueError) as exc:
        logger.error("Failed to parse score JSON: %s", raw[:500])
        raise ValueError(f"Could not parse lead score response: {exc}") from exc

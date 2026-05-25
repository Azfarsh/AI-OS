---
name: agency-audit
description: Score Agency OS against the Four Cs. Read-only repo scan. Trigger on "/agency-audit".
---

# /agency-audit

## Trigger

```
/agency-audit
```

## Pre-flight (read-only scan)

- `CLAUDE.md`
- `context/` (all files)
- `connections.md`
- `references/connections-guide.md`
- `.claude/skills/` (every `SKILL.md`)
- `clients/` (folders, briefs, notes, reports)
- `decisions/log.md`
- `references/` (API guides vs claimed connections)

## Steps

1. **Score Context (0–3)** per kickstart rubric in `AGENCY_OS_KICKSTART.md` §5.4.

2. **Score Connections (0–3)** — count wired rows in `connections.md` with matching `references/{tool}-api.md` and `scripts/*.py`.

3. **Score Capabilities (0–3)** — evidence of `/onboard-client`, `/report`, `/proposal` runs in `clients/` and `decisions/log.md`.

4. **Score Cadence (0–3)** — reports across periods, audit recency.

5. **Print report** — use box format from kickstart (bar charts, total /12, top 3 gaps, previous/next audit dates).

6. **Append** summary line to `decisions/log.md`.

## Outputs

- Terminal report
- `decisions/log.md` entry

## Connections required

None

## Failure modes

- Missing critical files: list gaps, still produce partial score.

## Log entry

`{ISO timestamp} | /agency-audit | Score {n}/12 | Context {c} Connections {n} Capabilities {p} Cadence {d}`

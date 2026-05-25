# Agency OS — AI Operating System

CLI-only agency operating system built on [AIS-OS](https://github.com/nateherkai/AIS-OS). No frontend, no backend server, no database. Run skills in **Claude Code** with `/skill-name`. State lives in Markdown under this repo.

## Operator brain — 3Ms

Read `references/3ms-framework.md` for Mindset, Method, Machine. Use with `/level-up` weekly.

> *The Three Ms of AI™ is a trademark of Nate Herk. © 2026 Nate Herk.*

## Base skills (personal AIOS)

- `/onboard` — agency intake + Day-1 scaffold from `aios-intake.md`
- `/audit` — personal Four-Cs gap report (AIS-OS)
- `/level-up` — weekly automation interview

## Agency skills (client workflows)

- `/onboard-client` — new client: ClickUp, Drive, contract, repo folder
- `/report` — performance report from Meta / Google Ads
- `/proposal` — proposal from meeting notes + email
- `/agency-audit` — agency Four-Cs scoreboard

Full build contract: `AGENCY_OS_KICKSTART.md`

## Where things live

| Path | Purpose |
|------|---------|
| `context/` | Agency profile, client registry, quarterly priorities |
| `clients/{slug}/` | Per-client brief, notes, proposals, reports, contracts |
| `references/` | SOPs, report/proposal structure, API guides (read-only at runtime) |
| `templates/` | Parameterized scaffolds skills fill in |
| `scripts/` | Python CLI tools (one file per integration) |
| `connections.md` | Registry of wired services — **check before every external step** |
| `decisions/log.md` | Append-only decisions and skill runs |
| `archives/` | Retired clients, deprecated refs — never delete |

## Connections

Read `connections.md` before calling any script. To add or remove a service without breaking skills, follow `references/connections-guide.md`.

## Knowledge base

- **Agency:** `context/agency-profile.md`
- **Clients:** `context/clients.md` + `clients/{slug}/client-brief.md`
- **Quarter:** `context/priorities.md`

## How you work with me

- Be direct. Lead with action.
- Every agency skill reads context first (non-skippable).
- Script failed → stop; never silently continue.
- Suggest logging decisions in `decisions/log.md`.
- Default Shift: ask how far AI can go before assuming manual work.

## Voice

Casual but professional. Short sentences. Bullet points over paragraphs. Draft external client copy before sending.

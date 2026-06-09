# Agency OS — Bombay Media

CLI-only AI Operating System for Bombay Media FZE. Built on AIS-OS by Nate Herk.
No frontend, no backend server, no database. Run skills in **Claude Code** with `/skill-name`.
All state lives in Markdown files in this repo.

## Agency Identity

- **Name:** Bombay Media FZE
- **Founder:** Farhan Rakhangi — farhan@bombay-media.com
- **Tagline:** AI-Powered Performance Marketing
- **Website:** bmmediagrowth.com
- **Locations:** Dubai, UAE & Mumbai, India
- **ICP:** High-ticket online coaches, US & UK market

## Operator Brain — 3Ms

Read `references/3ms-framework.md` for Mindset, Method, Machine. Use with `/level-up` weekly.

## Brand Rules (Non-Negotiable)

- **Voice:** Proof-First. Founder-Direct. Systems Thinker. Dubai-Global. Never: hype, vague superlatives, engagement bait.
- **Contract:** Always generate from `references/assets/Bombay_Media_Contract_Template.pptx` — never write a plain-text contract
- **Guarantee language:** "3× ROAS in 90 days" — use this exact phrasing in all client-facing copy
- **Colours:** Primary Purple `#320753`, Yellow `#FFDE00`, Black `#111111`, Lavender `#F8F5FF`
- **Fonts:** Arial Black (headings) · Calibri (body)

## Skills

### Base Skills (AIS-OS)
- `/onboard` — agency intake + Day-1 scaffold
- `/audit` — personal Four-Cs gap report
- `/level-up` — weekly automation interview

### Agency Skills (Bombay Media)
- `/onboard-client` — new client: repo folder + contract PPTX + ClickUp + Drive + email
- `/report` — monthly performance report from Meta / Google Ads data
- `/proposal` — proposal from meeting notes + email to prospect
- `/agency-audit` — agency Four-Cs scoreboard

Full build contract: `AGENCY_OS_KICKSTART.md`

## Where Things Live

| Path | Purpose |
|---|---|
| `context/` | Agency profile, client registry, quarterly priorities |
| `clients/{slug}/` | Per-client brief, notes, proposals, reports, contracts |
| `references/` | SOPs, API guides, brand assets — READ-ONLY at runtime |
| `references/assets/` | Contract PPTX template, logo files |
| `templates/` | Parameterized scaffolds skills fill in |
| `scripts/` | Python CLI tools (one file per integration) |
| `connections.md` | Registry of wired services — check before every external step |
| `decisions/log.md` | Append-only decisions and skill runs |
| `archives/` | Retired clients, deprecated refs — never delete |

## Connections

Read `connections.md` before calling any script. Follow `references/connections-guide.md` to add/remove services.

## Knowledge Base

- **Agency:** `context/agency-profile.md`
- **Clients:** `context/clients.md` + `clients/{slug}/client-brief.md`
- **Quarter:** `context/priorities.md`

## How You Work With Me

- Be direct. Lead with action.
- Every agency skill reads context first (non-skippable).
- Script failed → stop; never silently continue.
- Log every decision in `decisions/log.md`.
- Default Shift: ask how far AI can go before assuming manual work.
- Contract generation always uses the branded PPTX — never plain text or markdown.

## Voice

Casual but professional. Short sentences. Bullet points over paragraphs.
Draft external client copy in Bombay Media brand voice (Proof-First, Founder-Direct) before sending.

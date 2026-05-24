# Agency OS — How to test (terminal)

Your **9/9 application tests passed**. That proves the AI OS runtime works.

The **Agency loops** (leads, CRM, onboarding, ads, reports) are built in stages. Below: what works **today** vs what needs API keys.

---

## What works today (no extra APIs)

### Loop 1 — Lead acquisition (Phase 0 + 1 core)

```powershell
cd "c:\Users\Azfar\OneDrive\Desktop\AI OS"
.\.venv\Scripts\Activate.ps1

# Process 2 sample leads: score → qualify → write memory/leads/*.md
ais lead run

# Custom file
ais lead run --file fixtures\sample_leads.json

# List / read leads
ais lead list
ais lead show jane-smith-acme-saas-demo

# Ask the executive agent about your pipeline
ais lead chat "Which leads are qualified and what should we do next?"
```

**What happens internally (architecture Loop 1):**

1. Deduplicate → checks `memory/leads/`
2. Score → LLM + `prompts/lead_scoring.md`
3. Qualify → threshold **70** (`configs/agency.yaml`)
4. Write → `memory/leads/{name-company}.md`
5. Update → `memory/context/active_pipeline.md`

**Not wired yet (need client APIs):** Apollo scrape, LinkedIn, Freshsales, Instantly.

---

### Loops 2–5 — Test with REPL + agents (simulation)

Until integrations ship, use the terminal to **simulate** work the agents will automate:

| Loop | Test command in `ais` REPL |
|------|----------------------------|
| **2 Call intelligence** | `/research Summarize this call transcript and extract buying signals: [paste text]` |
| **3 Deal-won onboarding** | `Create a client onboarding checklist for Acme Corp: ClickUp, Drive, DocuSeal, welcome email` |
| **4 Campaign monitoring** | `/research Given CPL target £28 and spend £1200 CPL £45, flag anomalies` |
| **5 Reporting** | `/research Write a 1-page weekly report for Acme using benchmarks in memory/context` |

Or one-shot:

```powershell
ais chat "Draft weekly report narrative for a B2B SaaS client: Meta spend 4200 CPL 32, Google spend 3800 ROAS 2.8, target CPL 28"
```

---

## What needs client API keys (next build)

| Loop | Integrations | Env / setup |
|------|----------------|-------------|
| 1 full | Apollo, LinkedIn, Freshsales, Instantly | `APOLLO_API_KEY`, `FRESHSALES_*`, `INSTANTLY_*` |
| 2 | tl;dv webhook | `TLDV_*` + webhook server |
| 3 | ClickUp, Google Drive, DocuSeal, Gmail | See `CREDENTIALS.md` |
| 4 | Meta Ads, Google Ads | OAuth + ad account IDs |
| 5 | Gmail delivery, WeasyPrint PDF | Google + optional renderer |

---

## 4-day sprint mapping

| Day | Architecture focus | You can test now |
|-----|-------------------|------------------|
| Day 1 | Repo, memory schema, APIs | `ais lead run`, fill `memory/context/agency_profile.md` |
| Day 2 | Lead intelligence E2E | `ais lead run` + `ais lead list` |
| Day 3 | Onboarding chain | REPL checklist; APIs later |
| Day 4 | Reporting + tl;dv | REPL report draft; APIs later |

---

## Quick demo script for a client (5 min)

```powershell
.\scripts\test-application.ps1
ais lead run
ais lead list
ais lead show jane-smith-acme-saas-demo
ais
```

In REPL:

```
What are our agency 90-day goals?
/memory save Demo client Acme wants reports every Monday
exit
```

---

## Files to inspect after `ais lead run`

- `memory/leads/jane-smith-acme-saas-demo.md` — qualified lead
- `memory/leads/bob-retail-bobs-corner-shop.md` — likely disqualified
- `memory/context/active_pipeline.md` — pipeline table

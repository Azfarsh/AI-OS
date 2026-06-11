# Client Onboarding SOP — Bombay Media

> This file is READ-ONLY at runtime. The `/onboard-client` skill reads this to create ClickUp tasks.

## Phase 1 — Internal Setup (Day 1)
- [ ] Create client folder in repo (`clients/{slug}/`)
- [ ] Write `client-brief.md` with parsed inputs
- [ ] Create ClickUp project under "Clients" space
- [ ] Create ClickUp task lists: Onboarding, Meta Ads, Reporting, Creative
- [ ] Add client entry to `context/clients.md`
- [ ] Create Google Drive folder structure under `Bombay Media / Clients / {Client Name}/`

## Phase 2 — Contract & Legal (Day 1–3)
- [ ] Generate branded contract PPTX from template
- [ ] Convert contract PPTX to PDF
- [ ] Send contract PDF to client email via DocuSeal (or email attachment for demo)
- [ ] Follow up if not signed within 48h
- [ ] File signed contract in `clients/{slug}/contracts/` and Drive > Contracts/

## Phase 3 — Kickoff (Day 3–7)
- [ ] Send onboarding welcome email with Drive folder link + ClickUp access
- [ ] Schedule kickoff call (Farhan direct)
- [ ] Gather brand assets from client (logos, colors, fonts, product info)
- [ ] Audit existing Meta Ads account (request access via Business Manager)
- [ ] Set up reporting access (Meta Business Manager + Google Analytics if applicable)

## Phase 4 — Launch Prep (Day 7–14)
- [ ] Build ad account structure (campaigns, ad sets, audiences)
- [ ] Create initial ad creatives (AI-generated with client brand)
- [ ] Get client approval on creatives (via email or Drive comments)
- [ ] Set up weekly ROAS dashboard
- [ ] Launch campaigns

## Google Drive Folder Structure
```
Bombay Media/
└── Clients/
    └── {Client Name}/
        ├── Reports/
        ├── Assets/
        │   ├── Brand Assets/
        │   └── Ad Creatives/
        ├── Contracts/
        └── Creative/
```

## ClickUp Project Structure
```
Clients Space/
└── {Client Name}/
    ├── Onboarding (list)
    │   └── [Tasks from Phase 1–4 above]
    ├── Meta Ads (list)
    │   ├── Campaign Setup
    │   ├── Creative Testing
    │   └── Weekly Reporting
    ├── Content Marketing (list)
    │   ├── Monthly Content Calendar
    │   └── Ad Creative Production
    └── Strategy (list)
        ├── A/B Test Cycles
        └── Monthly Review
```

## Standard Task Assignments
- All tasks: Assigned to Farhan Rakhangi by default
- Reporting tasks: Due every Monday
- Monthly review: Due last Friday of each month

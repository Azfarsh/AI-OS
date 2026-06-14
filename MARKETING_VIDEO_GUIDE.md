# Marketing Video Guide — Bombay Media Agency OS

Professional demo video for LinkedIn, website hero, and sales calls.  
**Target length:** 90–120 seconds  
**Tone:** Proof-first, founder-direct, systems thinker — no hype

---

## Pre-production checklist

### Environment
- [ ] Clean desktop wallpaper (solid dark or Bombay purple `#320753`)
- [ ] Hide personal notifications (Focus / Do Not Disturb)
- [ ] Browser zoom 100%; close unrelated tabs
- [ ] Terminal font size 14–16pt (readable on mobile)
- [ ] `.env` wired: ElevenLabs + SMTP (for live email moment)
- [ ] Run `python scripts/setup_elevenlabs_agent.py` once before filming

### Files to have open (in order of reveal)
1. `python scripts/jarvis.py` → dashboard at http://127.0.0.1:8765
2. VS Code / Cursor with `clients/demo-corp/` folder visible
3. Optional: Gmail inbox showing report email arrival

### Recording tools (pick one)
| Tool | Platform | Notes |
|------|----------|-------|
| OBS Studio | Mac / Win / Linux | Free, best for screen + mic |
| Loom | All | Fast, good for LinkedIn |
| ScreenFlow | Mac | Polished exports |
| Camtasia | Win | Easy edits + captions |

**Export settings:** 1920×1080, 30fps, H.264, audio 48kHz

---

## Shot list (storyboard)

| Scene | Duration | Visual | Action |
|-------|----------|--------|--------|
| 1 — Hook | 0:00–0:12 | Logo card or dashboard fade-in | None — voiceover only |
| 2 — Problem | 0:12–0:22 | Quick montage: spreadsheets, Slack chaos (optional B-roll) | None |
| 3 — Intro OS | 0:22–0:35 | Run `python scripts/jarvis.py` | Dashboard loads, status panel visible |
| 4 — Voice moment | 0:35–0:55 | Click orb, speak report command | Agent confirms, activity log updates |
| 5 — Report proof | 0:55–1:05 | Open `report-2025-01.pptx` | Scroll 2–3 slides |
| 6 — Onboard | 1:05–1:15 | Voice: onboard command | Show new client folder + contract PPTX |
| 7 — Proposal | 1:15–1:25 | Voice: proposal command | Open proposal PPTX cover slide |
| 8 — Close | 1:25–1:35 | Dashboard + Bombay Media logo | Guarantee line on screen |

---

## Step-by-step filming

### Before rolling
1. Delete or archive old test outputs in `clients/voice-test-co/` if re-filming onboard
2. Run once off-camera to confirm all three workflows succeed:
   ```bash
   python scripts/voice_agent.py --test-all-workflows
   ```
3. Start fresh dashboard session

### Take 1 — Dashboard open (Scene 3)
```bash
python scripts/jarvis.py
```
- Let browser open automatically
- Pause 2 seconds on status panel (clients + integrations)
- Do not click yet — let voiceover introduce the OS

### Take 2 — Voice report (Scene 4–5)
1. Click the **orb**
2. Allow microphone when prompted
3. Say clearly:
   > “Run a report for Demo Corp, period January 2025, use demo data, and email it to the client.”
4. Wait for agent confirmation → say **“Yes, go ahead.”**
5. When activity log shows success, open:
   - `clients/demo-corp/reports/report-2025-01.pptx`
6. Optional: cut to Gmail showing email received

### Take 3 — Voice onboard (Scene 6)
1. Still in voice session (or restart orb)
2. Say:
   > “Onboard a new client called Apex Coaching, email hannanchougle28@gmail.com, services meta and content, budget five thousand.”
3. Confirm when asked
4. Show `clients/apex-coaching/` and contract PPTX

### Take 4 — Voice proposal (Scene 7)
1. Say:
   > “Create a proposal for Jane Doe at Demo Corp, email hannanchougle28@gmail.com.”
2. Confirm
3. Open newest file in `clients/demo-corp/proposals/`

### Take 5 — Closing frame (Scene 8)
- Return to dashboard
- Overlay text (in edit):
  - **Bombay Media FZE**
  - **AI-Powered Performance Marketing**
  - **3× ROAS in 90 days — guaranteed**
  - **bmmediagrowth.com**

---

## Edit guide

### Pacing
- Cut dead air between voice command and tool completion (jump cut when log updates)
- Keep orb “working” animation — it sells the AI feel
- Add subtle whoosh on scene transitions (optional, keep minimal)

### On-screen text (lower thirds)
| Timestamp | Text |
|-----------|------|
| 0:25 | `Agency OS — Voice-controlled operations` |
| 0:40 | `“Run a report… and email it.”` |
| 0:58 | `Branded PPTX — generated in seconds` |
| 1:08 | `Client onboarding — folder, contract, registry` |
| 1:18 | `Proposal from meeting notes` |
| 1:28 | `bmmediagrowth.com` |

### Music
- Low-volume ambient / corporate tech bed (−18 LUFS under voice)
- No trendy TikTok beats — this is B2B / high-ticket coaches
- Sources: Epidemic Sound, Artlist, or YouTube Audio Library (royalty-free)

### Captions
- Always burn in captions (85% of LinkedIn watches muted)
- Highlight command phrases in **yellow** `#FFDE00`

---

## Voiceover script (full — ~110 seconds)

Read at a calm, confident pace. Pause where marked `[pause]`.

---

**[0:00 – Hook]**

> Running a performance agency means the same work, every week.  
> Reports. Onboarding. Proposals.  
> All scattered across tools, tabs, and templates.  
> `[pause]`  
> We built something different.

**[0:12 – Problem → Solution]**

> Bombay Media Agency OS is a voice-controlled operating system for growth teams.  
> No bloated software. No new logins.  
> Just your workflows — reports, client onboarding, and proposals — running from one command center.  
> `[pause]`  
> On Mac. Windows. Or Linux.

**[0:25 – Dashboard]**

> Launch the OS.  
> Your integrations, clients, and system status — live, before you say a word.  
> `[pause]`  
> Tap once. Start talking.

**[0:35 – Report workflow]**

> “Run a report for Demo Corp, January 2025 — demo data — and email it to the client.”  
> `[pause]`  
> The agent confirms. Executes.  
> Meta and Google metrics pulled. Branded performance deck generated.  
> Email sent.  
> `[pause]`  
> Proof, not promises.

**[0:55 – Onboard workflow]**

> New client signed?  
> “Onboard Apex Coaching — meta and content — budget five thousand.”  
> `[pause]`  
> Client folder. Brief. Registry entry. Contract deck — scaffolded automatically.

**[1:08 – Proposal workflow]**

> Discovery call done?  
> “Create a proposal for Jane at Demo Corp.”  
> `[pause]`  
> Meeting notes in. Branded proposal out.  
> Ready to send.

**[1:20 – Close]**

> This is how modern agencies operate.  
> Systems over chaos. Voice over busywork.  
> `[pause]`  
> Bombay Media. AI-powered performance marketing.  
> Three-X ROAS in ninety days — guaranteed.  
> `[pause]`  
> Book your strategy call at bmmediagrowth.com.

---

## Short cut (60-second social version)

Use scenes 1, 3, 4, 5, 8 only. Voiceover:

> Agencies lose hours on reports, onboarding, and proposals.  
> Bombay Media Agency OS fixes that with voice.  
> One command — report generated, deck built, email sent.  
> Onboard clients. Ship proposals. From one dashboard.  
> Mac. Windows. Linux.  
> Three-X ROAS in ninety days. Guaranteed.  
> bmmediagrowth.com

---

## Post-publish checklist

- [ ] Upload 1080p to LinkedIn (native upload, not YouTube link)
- [ ] Pin post on company page
- [ ] Add to website hero or `/demo` page
- [ ] Send to 3 prospects with personal note: *“This is how we run your account behind the scenes.”*
- [ ] Track Calendly clicks for 7 days

---

## Legal / brand reminders

- Use exact guarantee phrasing: **“3× ROAS in 90 days”**
- Do not name specific AI vendors in client-facing copy (video voiceover is internal/marketing — “AI-powered” is fine)
- Brand colors on any graphics: Purple `#320753`, Yellow `#FFDE00`, Black `#111111`

# Proposal SOP — Bombay Media

> READ-ONLY at runtime. Do not modify during skill execution.
> This SOP governs how the /proposal skill fills each slide.

---

## Purpose

This SOP ensures every Bombay Media proposal:
1. Feels personalised to the prospect's actual pain points
2. Stays on-brand (Proof-First, Founder-Direct, no hype)
3. Never fabricates data — all numbers are verified case studies
4. Flows logically: empathy → proof → solution → investment → CTA

---

## Slide-by-Slide Filling Rules

### Slide 1 — Cover

**Dynamic fields:**
- `[CLIENT NAME]` → Replace with prospect's full name
- `[Date]` → Today's date in "D Month YYYY" format
- Company name appears in the email subject, not on the cover slide

**Static fields (never change):**
- Agency branding: BM logo, "BOMBAY MEDIA", "AI-Powered Performance Marketing"
- Case study stats in right panel: 25.6× ROAS, $179,850 revenue, $7,017 spend
- Guarantee tagline: "3× ROAS in 90 Days — Guaranteed"
- Prepared by: "Prepared by Farhan Rakhangi"

**Brand rule:** Cover always uses `#320753` (Primary Purple) background.

---

### Slide 2 — The Proof

**This slide is ALWAYS static.** Never alter the case study numbers.

Numbers displayed:
- Revenue: $179,850 in 90 days
- Ad Spend: $7,017 total invested
- ROAS Achieved: 25.6×
- Best Campaign: 131×
- 18-Month Blended: $263,646 revenue / $26,493 spend = 9.95× ROAS

**Why this rule exists:** These are verified, real numbers. Changing them per prospect would be fabrication. The purpose of this slide is to establish credibility with proof — not to customise.

**Footer text:** "Metrics verified. Identity anonymised by client request."

---

### Slide 3 — What We Deliver For You

**Dynamic: card selection based on services.**

The 6 cards are filled in this priority order:
1. Services the prospect mentioned or needs (from notes.md)
2. Then: Funnel Diagnostic, Weekly Reporting, 90-Day Guarantee (always included)

**Service card assignment rules:**
- If notes mention Meta Ads → Card 01: "AI-Powered Meta Ads"
- If notes mention Google → Card 02 or 03: "Google Ads Management"
- If notes mention content/creatives → "Content Marketing System"
- Cards 04-06 always: Funnel Diagnostic, Weekly Reporting, 90-Day Guarantee

**Body copy rule:** Use the standard descriptions from generate_proposal.py. Do not write custom descriptions per prospect — these are tested, on-brand copy blocks.

---

### Slide 4 — Investment & Next Steps

**Dynamic fields:**
- Setup Fee: Always $1,500 (one-time) — never change
- Monthly Retainer: Use budget from notes.md (default: $3,000/mo)
- Ad Spend: Use range from notes.md (default: $3,000–$10,000/mo)
- "Exclusive client price" callout: sum of retainer + approx. setup amortised

**Static fields:**
- Next 3 Steps copy: always the same (Funnel Leaks → Strategy Call → Launch in 14 days)
- Calendly link: always `calendly.com/bombay_media/complimentary-business-success-call`
- Footer: always `bmmediagrowth.com  |  Bombay Media  |  Dubai & Mumbai`

**Pricing rule:** If the prospect's budget is below $3,000/mo, do not lower the pricing. Flag this in the log. The minimum retainer is $3,000/mo per agency-profile.md.

---

## What Claude Must NOT Do

- ❌ Do not invent case study numbers (the 25.6× ROAS etc. are real and fixed)
- ❌ Do not write custom "Understanding Your Challenge" slide — this is not in the template
- ❌ Do not lower prices below standard rates
- ❌ Do not send proposal if notes.md is empty — always halt and ask
- ❌ Do not use hype language ("amazing", "incredible", "game-changing")
- ❌ Do not name specific AI tools in client-facing copy
- ❌ Do not add extra slides — the 4-slide structure is fixed

---

## Service-to-Notes Keyword Mapping

When parsing notes to determine services, use this mapping:

| Notes contains | Include service |
|---|---|
| "meta", "facebook", "fb ads", "instagram", "ig" | meta |
| "google", "search ads", "ppc", "youtube" | google |
| "content", "creative", "carousel", "copy", "email" | content |
| "seo", "organic", "blog", "ranking" | seo |

Default if no keywords found: `meta,content` (core Bombay Media offering)

---

## Email Body Rules

The email sent with the proposal must:
- Open with the prospect's first name
- Reference something specific from the meeting (use company name at minimum)
- Include the 3 CTAs: Funnel Leaks report → Strategy Call → Proposal attachment
- Close as Farhan, not as "the team"
- Never use: "I hope this email finds you well", "Please find attached", "Dear Sir/Madam"

---

## Notes.md Quality Check

Before generating, Claude should verify notes.md contains at minimum:
- [ ] Company name
- [ ] At least one pain point
- [ ] A budget figure (even approximate)

If any of these are missing, prompt the user to add them before continuing.

# Contract Template — Bombay Media

> This file defines the DATA that fills the contract PPTX.
> The script `scripts/generate_contract.py` reads this structure and populates the branded PPTX template.
> Do NOT edit the PPTX template manually — always go through the script.

## Slide 1 — Cover
- Title: SERVICE AGREEMENT
- Subtitle: Performance Marketing Partnership
- Client: {{CLIENT_NAME}}
- Date: {{DATE}}
- Agreement No: {{AGREEMENT_NUMBER}}

## Slide 2 — Parties & Scope
### Service Provider (static — never changes)
- Company: Bombay Media FZE
- Location: Dubai, United Arab Emirates
- Contact: Farhan Rakhangi, Co-Founder & Director of Growth
- Email: farhan@bombay-media.com
- Website: bmmediagrowth.com

### Client (filled per engagement)
- Company: {{CLIENT_NAME}}
- Location: {{CLIENT_CITY}}, {{CLIENT_COUNTRY}}
- Contact: {{CLIENT_CONTACT_NAME}}, {{CLIENT_TITLE}}
- Email: {{CLIENT_EMAIL}}
- Website: {{CLIENT_WEBSITE}}

### Scope
Bombay Media agrees to deliver AI-powered {{SERVICES}} services as outlined in the attached Statement of Work (SOW). This agreement is governed by the terms below and the 90-day performance guarantee.

## Slide 3 — Deliverables & Fees
### Deliverables (selected based on services)
- Meta Ads Management: Full campaign setup, creative testing, audience optimisation, weekly reporting
- Content Marketing: AI-generated ad creatives, carousel assets, copy, monthly content calendar
- Analytics & Reporting: Weekly ROAS dashboard, monthly performance review call with Farhan directly
- Strategy & Optimisation: A/B test cycles, funnel audits, spend reallocation recommendations

### Investment
| Fee Item | Amount | Payment Terms |
|---|---|---|
| Setup Fee (one-time) | $1,500 | Due on signing |
| Monthly Retainer | {{MONTHLY_RETAINER}} | Due 1st of each month |
| Ad Spend (client-managed) | {{AD_SPEND_RANGE}} | Paid direct to Meta by client |
| Performance Bonus (optional) | 10% of revenue above 3× ROAS | Invoiced monthly in arrears |

## Slide 4 — Terms & Signatures
### Guarantee
If Bombay Media does not deliver a minimum 3× return on ad spend within 90 days of campaign launch, we will continue to manage your campaigns at no additional cost until the guarantee is met.

### Term: 90 days initial. 30 days written notice to terminate after initial term.
### Governing Law: United Arab Emirates (DIFC)
### Agreement No: {{AGREEMENT_NUMBER}}

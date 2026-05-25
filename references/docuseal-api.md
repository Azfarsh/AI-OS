# DocuSeal API — researched once

**Script:** `scripts/docuseal_send_contract.py`  
**Env:** `DOCUSEAL_API_TOKEN`, `DOCUSEAL_TEMPLATE_ID`

## Endpoint

`POST https://api.docuseal.com/submissions`  
Header: `X-Auth-Token: {DOCUSEAL_API_TOKEN}`

## Payload shape

- `template_id` (int)
- `submitters`: `[{ "email", "role": "Client" }]`
- `send_email`: true
- `fields`: map contract markdown into template fields

## Adding / removing

Update `connections.md` and `.env.example`. `/onboard-client` step 6 halts if `docuseal` is required and not connected.

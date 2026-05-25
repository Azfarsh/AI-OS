# Google Ads API — researched once

**Script:** `scripts/google_ads_pull.py`  
**Env:** `GOOGLE_ADS_DEVELOPER_TOKEN`, `GOOGLE_ADS_CLIENT_ID`, `GOOGLE_ADS_CLIENT_SECRET`, `GOOGLE_ADS_REFRESH_TOKEN`

## Local config

Create `scripts/.google-ads.yaml` (gitignored) from `.env`:

```yaml
developer_token: "..."
client_id: "..."
client_secret: "..."
refresh_token: "..."
use_proto_plus: True
```

## Query

GAQL on `campaign` with `segments.date` between period bounds.

## Output

`clients/{slug}/reports/.tmp-google-{period}.json`

## Client brief

```yaml
platforms:
  google:
    customer_id: "1234567890"
```

## Adding / removing

Skip Google pull in `/report` when client has no `google` service or connection is unwired.

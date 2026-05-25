# Meta Ads API — researched once

**Script:** `scripts/meta_ads_pull.py`  
**Env:** `META_APP_ID`, `META_APP_SECRET`, `META_ACCESS_TOKEN`

## SDK

`facebook-business` — `AdAccount(act_{id}).get_insights(...)`

## Period

CLI `--period YYYY-MM` → `time_range.since` / `until` for calendar month.

## Output

`clients/{slug}/reports/.tmp-meta-{period}.json` (deleted after report synthesis).

## Client brief fields

In `client-brief.md`, store:

```yaml
platforms:
  meta:
    account_id: "123456789"
```

## Adding / removing

`/report` only calls this script when `meta` is in client services and `connections.md` shows `meta-ads` as connected.

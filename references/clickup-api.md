# ClickUp API — researched once

**Script:** `scripts/clickup_create_project.py`  
**Env:** `CLICKUP_API_TOKEN`, `CLICKUP_TEAM_ID`, `CLICKUP_SPACE_ID`

## Auth

Personal API token in header: `Authorization: {token}`

## Endpoints used

| Action | Method | Path |
|--------|--------|------|
| Create folder | POST | `/api/v2/space/{space_id}/folder` |
| Create list | POST | `/api/v2/folder/{folder_id}/list` |
| Create task | POST | `/api/v2/list/{list_id}/task` |

## Adding / removing this service

1. Add or remove the row in `connections.md` (id: `clickup`).
2. Add or remove env keys in `.env.example`.
3. Skills that list `clickup` in **Connections required** skip that step when status is `not connected`.
4. Do not delete this file when pausing ClickUp — mark connection `not connected` instead.

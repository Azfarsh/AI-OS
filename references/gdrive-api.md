# Google Drive API — researched once

**Script:** `scripts/gdrive_create_folder.py`  
**Env:** `GOOGLE_SERVICE_ACCOUNT_JSON_PATH`, `GOOGLE_DRIVE_ROOT_FOLDER_ID`, `AGENCY_NAME`

## Auth

Service account JSON with Drive scope. Share the root folder with the service account email.

## Folder layout

`{root}/Clients/{Client Name}/` → `Reports/`, `Assets/`, `Contracts/`, `Creative/`

## Adding / removing this service

1. Update `connections.md` row `google-drive`.
2. Remove `GOOGLE_*` keys from `.env` when unwiring.
3. `/onboard-client` step 5 is optional when Drive is not connected — log skip in `decisions/log.md`.

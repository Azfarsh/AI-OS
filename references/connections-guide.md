# Connections registry — add or remove a service safely

`connections.md` is the single source of truth for what is wired. Skills never assume a service exists — they read the registry first.

## Add a new service

1. Add a row to `connections.md` with a stable **id** (e.g. `hubspot`).
2. Add env keys to `.env.example` and your local `.env`.
3. Create `references/{tool}-api.md` (researched once).
4. Add `scripts/{tool}_{action}.py` — CLI args only, uses `scripts/_common.py`.
5. Update agency skills that should call it (**Connections required** + conditional steps).
6. Run `/agency-audit` to verify Connections score.

## Remove a service

1. Set Mechanism to `not connected` and clear **Last checked** in `connections.md`.
2. Remove secrets from `.env` (keep keys in `.env.example` commented or documented as optional).
3. Do **not** delete `references/{tool}-api.md` — move to `archives/references/` if deprecated.
4. Skills must skip steps that depend on that id (never fail the whole run for an optional integration).

## Required vs optional per skill

| Skill | Required connection ids |
|-------|-------------------------|
| `/onboard-client` | `clickup`, `google-drive`, `docuseal`, `smtp` |
| `/report` | `meta-ads` and/or `google-ads` per client; `smtp` if `--send-email` |
| `/proposal` | `smtp` |
| `/agency-audit` | none |

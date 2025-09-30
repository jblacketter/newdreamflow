# Algolia Migration — Status & Restart Notes

Author: Codex (OpenAI)
Date: 2025-09-30

## Current Status
- Groups: Soft-disabled via feature flag; UI nav removed; routes gated. Group privacy treated as private when disabled.
- Sessions: Switched to signed-cookie sessions (no DB-backed sessions).
- Community Search: Uses Algolia when configured; optional enforcement to avoid DB fallback.
- Database: Still in use for core models (users, dreams, things, stories, etc.). No schema removals yet.
- No destructive changes made; group templates/models remain for later cleanup.

## Feature Flags (in `newdreamflow/settings.py`)
- `FEATURE_GROUPS` (default: `false`):
  - false: hide group routes/UI; treat `privacy == 'groups'` as private.
  - true: restore group routes and behavior.
- `FEATURE_ALGOLIA_ONLY` (default: `false`):
  - true: community pages return 503 if Algolia is not configured (no DB fallback).

## Required Environment Variables (use `.env`)
- `ALGOLIA_APPLICATION_ID`
- `ALGOLIA_API_KEY` (Admin key, server-side)
- `ALGOLIA_SEARCH_API_KEY` (Search-only key for clients)
- Optional/general:
  - `DEBUG=True`
  - `SECRET_KEY=<your-secret>`
  - `ALLOWED_HOSTS=localhost,127.0.0.1`
  - `FEATURE_GROUPS=false`
  - `FEATURE_ALGOLIA_ONLY=false` (set to true once Algolia keys are in place)
  - `DATABASE_URL` (omit in dev to use local SQLite)

Example `.env` snippet:
```
DEBUG=True
SECRET_KEY=dev-secret
ALLOWED_HOSTS=localhost,127.0.0.1
FEATURE_GROUPS=false
FEATURE_ALGOLIA_ONLY=false
ALGOLIA_APPLICATION_ID=
ALGOLIA_API_KEY=
ALGOLIA_SEARCH_API_KEY=
```

## Restart Checklist
1) Open terminal at repo root and activate venv:
- macOS/Linux: `source venv/bin/activate`

2) Ensure dependencies are installed (if needed):
- `pip install -r requirements.txt`

3) Optional NLP (removes warning):
- `python -m spacy download en_core_web_sm`

4) Environment setup:
- Create/update `.env` with the variables above.

5) Sanity checks and DB:
- `python manage.py check` (should pass; spaCy warning is benign if you skip step 3)
- `python manage.py migrate` (dev uses SQLite if `DATABASE_URL` unset)

6) Run the app:
- `python manage.py runserver`

## After You Obtain Algolia Keys
- Add `ALGOLIA_APPLICATION_ID`, `ALGOLIA_API_KEY`, `ALGOLIA_SEARCH_API_KEY` to `.env`.
- Restart the server to load settings.
- Build indices (community items):
  - Dreams: `python manage.py init_algolia_index`
  - Things: A parallel `init_algolia_index` exists under `apps/things`. Because Django command names collide, we will consolidate into a single command in a later PR. For now, community Things update via signals when saved; we can trigger re-indexing manually later if needed.
- Optional: set `FEATURE_ALGOLIA_ONLY=true` to prevent DB fallback on community pages.

## What Changed In Code (files)
- `newdreamflow/settings.py`: added `FEATURE_GROUPS`, `FEATURE_ALGOLIA_ONLY`, and signed-cookie sessions.
- `apps/sharing/urls.py`: group routes only enabled when `FEATURE_GROUPS` is true.
- `templates/base.html`: removed Groups nav link.
- `apps/dreams/views.py`: group privacy fallback; Algolia-only handling; privacy cycle excludes groups when disabled.
- `apps/things/views.py`: group privacy fallback; Algolia-only handling; privacy cycle excludes groups when disabled.
- `apps/dreams/forms.py` and `apps/things/forms.py`: remove `groups` from privacy choices when disabled.
- `templates/dreams/dream_list.html` and `templates/things/thing_list.html`: removed Groups filter option.

No migrations or deletions performed; groups remain documented for later removal per final plan.

## Verify After Restart
- `python manage.py check` → “System check identified no issues” (spaCy model warning is OK if not installed).
- Dreams/Things list/detail work; privacy toggling cycles through private → specific users → community.
- Community pages render Algolia UI when keys present. With `FEATURE_ALGOLIA_ONLY=true` and no keys, they return 503.

## Next Steps (when ready)
- Data Service for Algolia writes (create/update/delete), add idempotency + optimistic concurrency.
- Secured API Key minting for private/user-scoped searches.
- Backfill/export scripts; nightly index exports to object storage as durability measure.
- Post-cutover: full group removal (models, routes, templates, migrations) as outlined in `algolia-only-migration-plan-final.md`.

## Known Notes
- Two `init_algolia_index` commands (Dreams and Things) may collide on name discovery. We will consolidate later; until then, rely on signals or ad-hoc re-index where necessary.
- If you see architecture errors in the venv after reboot, reinstall problematic wheels (pydantic_core, etc.) for your CPU arch or recreate the venv.


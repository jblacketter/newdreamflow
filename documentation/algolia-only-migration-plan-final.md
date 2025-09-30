# NewDreamFlow — Algolia‑Only Migration Plan (Final)

Authors: Codex (OpenAI) and Claude (Anthropic)
Date: 2025-09-29
Status: Draft for team sign‑off (no code changes yet)

## Summary
- Objective: Eliminate the local database and serve all user‑facing content from Algolia indices. Use external object storage for media. Replace DB‑backed sessions/auth with stateless alternatives.
- Core shift: Move from relational, transactional persistence to denormalized, eventually consistent documents with search‑optimized retrieval.
- Guardrails: Strict privacy filters via Secured API Keys, server‑side checks for sensitive reads, and careful key management.

## Scope & Non‑Goals
- In scope: Dreams, Things, Stories, Patterns, Sharing (no groups in MVP), Public Profiles, media links, list/detail views, search, and filters.
- Out of scope: Reintroducing a relational database, deep relational joins, or strong ACID semantics. Any offline queue durable beyond standard app logging.
- Groups: De‑scoped for MVP to simplify rollout. See “Groups De‑scope & Removal Plan”.

## Target Architecture
- Indices
  - `dreams`: `objectID`, `user_id`, `privacy`, `title`, `description`, `tags`, `themes`, `entities`, `mood`, `lucidity_level`, `dream_date`, `created_at`, `updated_at`, `image_urls[]`, `voice_url`, `author{user_id, display_name, avatar_url}`.
  - `things`: Analogous to `dreams`; journaling items with media and metadata.
  - `stories`: Aggregates: `objectID`, `user_id`, `privacy`, `title`, `thing_ids[]`, `things_preview[]` (denormalized subset for fast render).
  - `patterns`: Precomputed summaries: metrics and related IDs in arrays.
  - `profiles_public`: Minimal public profile cards for display: `user_id`, `display_name`, `avatar_url`.
  - Note: No `groups` index in MVP; group membership and `group_ids` are omitted. If reintroduced later, membership resolution will be server‑side to avoid large arrays on content records.
- Read Path
  - Lists: Algolia search with filters/facets/replicas; client uses Secured API Keys with embedded filters.
  - Details: `getObject` by `objectID` + server‑side permission check for any sensitive/private content.
- Write Path
  - Centralized Data Service: validate input, upload media to object storage (store URLs only), write to Algolia (create/update/delete). Generate UUIDv4 `objectID`s. Use batched and partial updates where possible. Include idempotency keys and optimistic concurrency guards (e.g., compare `updated_at`/`version`) to mitigate lost updates.
- Auth & Sessions (DB‑less)
  - Sessions: Django signed‑cookie backend.
  - Identity: External IdP (OIDC/JWT). Middleware/backends populate a request identity without DB persistence. Public profile data lives in Algolia.
- Privacy & Access Control
  - Public/community: Keys restricted to `privacy:community`.
  - Private: Per‑user Secured API Keys with `user_id:<me>`, short expiry; refreshed as needed. Groups are de‑scoped for MVP; group filters will be added when groups return.
  - Sensitive views: Always server‑side fetch + check.
- Media
  - Object storage (e.g., S3/R2) with CDN. Records store public/signed URLs, not blobs. Define retention and max sizes.

## Migration Phases
1) Decisions & Risk Acceptance
- Confirm Algolia‑only scope (no DB fallback). Choose IdP and media backend. Approve eventual consistency and denormalization.

2) Schema Mapping & Index Design
- Map each Django model to target index fields, facets, searchable attributes, ranking, synonyms, and replicas. Define UUID strategy and timestamps.

3) Infrastructure Setup
- Provision Algolia app and indices; configure Admin/Search keys; implement server minting of Secured API Keys. Provision object storage and CDN.

4) Export & Backfill
- Freeze writes or run dual‑write temporarily. Export existing data, transform to schemas, upload media, rewrite URLs, bulk import to Algolia.

5) Feature‑Flag Cutover
- Introduce Data Service and route selected views (community lists first) to Algolia. Expand to private lists and detail views. Retire ORM‑coupled signals.

6) Remove Local DB Dependencies
- Switch sessions to signed cookies. Replace Django auth usage with external identity/JWT. Remove reliance on model queries in request flow. Delete `db.sqlite3` and DB configs after verification.

7) Hardening & Rollout
- Tune attributes for faceting and ranking, add replicas where needed. Implement logging/alerts, rate limiters, and cost guardrails. Security review for key minting and private data exposure.

## Data Mapping Strategy
- Denormalize child/related data into arrays and small preview objects for lists.
- Include `author{}` snippet in each record to avoid joins.
- For Stories and Patterns, precompute summaries and keep full relationship sets as ID arrays.
- Keep records compact to control costs and latency; store large media only as URLs.

## Security & Key Management
- Server uses Admin API key for writes; never exposed to clients.
- Clients receive short‑lived Secured API Keys with embedded filters and optional user hash.
- For private details and any mixed‑visibility pages, perform server‑side fetches with explicit permission checks.
- Key minting discipline: very short TTLs, cache keys per session sparingly, rotate signing secrets regularly, and rate‑limit issuance to avoid quota spikes.
-

## Observability, Reliability, Cost
- Logging: Server logs for all writes and sensitive reads; capture Algolia errors with retries/backoff.
- Metrics: Track index sizes, operation latencies, search success/no‑hits, Insights events.
- Cost: Attribute pruning, replica budgeting, and retention rules for rarely queried data.
- Durability & backup: Nightly exports of all indices (JSON) to object storage; periodic restore drills. Optional lightweight write‑ahead log for extra resilience without a DB.
- Environment isolation: Per‑environment apps or strict index prefixes/keys for dev/staging/prod to prevent cross‑env leakage.
- Outage posture: Graceful degradation (cached pages, minimal lists). Surface status and retry later guidance to users.
- Compliance & RTBF: Ensure deletes remove Algolia records and media; align logs/exports with retention policies.

## Private Indexing Policy (MVP)
- Do not index highly sensitive fields (e.g., full transcripts) for private items. Store them in object storage and serve via server‑checked endpoints. Limit `searchableAttributes` for private records to minimal metadata.

## Groups De‑scope & Removal Plan
- Decision: Groups are removed for MVP to simplify privacy and reduce write amplification.
- Immediate plan: No `groups` index; records omit `group_ids`; minted keys do not include group filters.
- Code removal (future PRs):
  - Remove group UI/routes/templates and any “group” list/detail views.
  - Remove or refactor models and logic tied to groups (`ThingGroup`, `GroupMembership`, group branches in sharing flows). Keep direct user sharing only, or temporarily pause sharing beyond private/community.
  - Simplify permission checks and filters to `user_id` and `privacy` only.
- Data migration: Export group memberships and group shares for archival; convert group‑shared items to private or community per product decision.
- Re‑introduction later: When needed, resolve membership server‑side and reintroduce `group_ids` as computed filters at key‑minting time (not denormalized large arrays on content records).

### Soft‑Disable Now (Docs‑Only Checklist)
- Feature flag: Introduce `FEATURE_GROUPS=false` (default) in settings/env. Use it to gate routes, UI, and template sections related to groups. No code changes in this commit; this documents the intended approach.
- Hide navigation & routes:
  - Routes to gate when flag is false: `apps/sharing/urls.py` → `groups`, `group_things`, `invite_to_group`, and UI entry points linking to them.
  - Templates to hide: `templates/sharing/groups.html`, `templates/sharing/group_dreams.html`, and the group section inside `templates/sharing/share_dream.html`.
- Remove “Groups” privacy option from UI when flag is false:
  - Dreams: UI lists built from `privacy_levels` (see `apps/dreams/views.py`).
  - Things: similar list in `apps/things/views.py`.
  - Do not expose `groups` in forms or dropdowns when soft‑disabled.
- Fallback behavior (runtime): Treat existing `privacy_level == 'groups'` as `private` for reads (documented for implementers):
  - Dreams detail: `apps/dreams/views.py` group branch → fallback to private check.
  - Things detail: `apps/things/views.py` group branch → fallback to private check.
  - Lists/search: exclude group‑only items from public listings unless reclassified.
- Archival/export (no code in this commit): Plan a management command `apps/sharing/management/commands/export_groups.py` to export `ThingGroup`, `GroupMembership`, and group shares to JSON for audit/restore.

### Full Removal Later (Post‑Algolia Cutover)
- Models & fields:
  - Remove `ThingGroup`, `GroupMembership`, and `ShareHistory` group references (`apps/sharing/models.py`).
  - Remove `shared_with_groups` ManyToMany from `apps/things/models.py` and `apps/dreams/models.py` (note: current code references `sharing.DreamGroup`; align or remove in migrations).
  - Update privacy choices to drop `'groups'` across models, forms, and admin.
- Admin & forms:
  - `apps/dreams/admin.py`, `apps/things/admin.py` → remove group fields.
  - `apps/sharing/forms.py` → remove group fields/validation.
- Views/URLs/Templates:
  - `apps/sharing/views.py` and `apps/sharing/urls.py` → delete `groups`, `group_things`, `invite_to_group`, and links.
  - Templates: remove `templates/sharing/groups.html`, `templates/sharing/group_dreams.html`, and group sections in `templates/sharing/share_dream.html`.
- Migrations:
  - Create migrations to drop M2M tables and privacy choice values; data migration to reclassify any remaining `'groups'` items to `private` (or `community` per decision).
- Tests & docs:
  - Update test fixtures and expectations; scrub docs mentioning groups from README and UI guides.

## Rollback Plan
- Pre‑migration dump and media backup. Keep DB artifact read‑only during verification window.
- Feature flags to revert read paths. If needed, restore DB‑backed flows and re‑enable signals.

## Risks & Mitigations
- Privacy leakage via misconfigured filters: enforce server‑side checks for private details; comprehensive tests; short‑lived keys.
- Loss of transactions/constraints: enforce validations application‑side; user messaging on conflicts; idempotent writes.
- Complex graph features (patterns): precompute projections; consider separate compute jobs if needed.
- Record bloat: strict field budgets; move heavy fields to storage URLs.
- Algolia availability: Define degraded modes and clear user messaging; retries/backoff and monitoring.

## Success Criteria
- 0 private record leakage; access tests pass for all roles.
- P50/P95 page loads meet targets with Algolia reads.
- All user‑facing content served without DB; `db.sqlite3` removed.
- Cost within agreed budget envelopes.

## Roles & Timeline (Indicative)
- Infra: Algolia/app keys, storage/CDN (1 sprint).
- Backend: Data Service, key minting, cutover flags (2–3 sprints).
- Frontend: Search/query integration, filters, detail fetches (1–2 sprints).
- Data: Export, transform, backfill, validation (1 sprint).
- Security: Review and pen tests for key flows (ongoing).

## Notes
- This plan consolidates Codex’s phased denormalization/cutover approach and Claude’s emphasis on secured key discipline, minimal client privileges, and precomputed projections for complex relations. No code changes have been made; this document is for alignment and sign‑off.

# NewDreamFlow — Algolia‑Only Migration Plan (Codex)

Author: Codex (OpenAI Codex CLI)
Date: 2025-09-29

## Summary
- Goal: Remove the local relational database and use Algolia as the sole data store for user-facing content in NewDreamFlow.
- Scope: Replace ORM-backed persistence and queries for domain data (Dreams, Things, Stories, Patterns, Sharing) with Algolia indices and APIs. Eliminate DB-backed sessions and minimize/replace DB dependencies for auth and metadata.
- Reality check: Algolia is a search/indexing engine, not a transactional RDBMS. We must denormalize, move to eventual consistency, and enforce permissions via filters and server-side checks. Where Django intrinsically expects a DB (auth/sessions), we will adopt stateless alternatives or a minimal non-persistent layer.

## Current State Snapshot
- Framework: Django app with custom `users.User` model; server-rendered templates.
- Local DB: `db.sqlite3` checked into repo (development default).
- Models present: Dreams, DreamImage, DreamTag, Things, ThingImage, ThingTag, Story, StoryThing, ThingPattern, ThingPatternOccurrence, PatternConnection, ThingGroup, GroupMembership, ShareHistory, User.
- Algolia: Present but optional; index init command (`init_algolia_index`), service wrapper (`apps/things/services/search_service.py`), save/delete signals for Dreams, conditional install via settings.

## Target Architecture
1) Indices (draft)
   - `dreams`: All dreams; fields include `objectID`, `title`, `description`, `privacy`, `user_id`, `group_ids`, `tags`, `themes`, `entities`, `mood`, `lucidity_level`, `dream_date`, `created_at`, `updated_at`, `image_urls`, `voice_url`, denormalized author/profile snippet.
   - `things`: Journaling “things” with analogous structure (privacy, tags, media URLs, author snippet).
   - `stories`: Story aggregates linking `thing_ids` as an array; also store an ordered, denormalized snapshot for display.
   - `patterns`: Pattern and connection summaries (flattened metrics; connection denormalized as arrays of IDs/refs).
   - `groups`: Group records with `member_user_ids` array and display metadata.
   - `profiles_public`: Minimal public profile cards (display_name, avatar URL). Identity itself moves off-DB (see Auth).

2) Write Path
   - Replace ORM writes with a centralized Data Service that writes to Algolia (create/update/delete), uploads media to object storage (e.g., S3/R2), then stores only URLs in records.
   - Generate stable `objectID` (UUIDv4) client- or server-side; avoid DB-sequenced IDs.
   - Enforce validations in application code (no DB constraints), return domain errors to the UI.

3) Read Path
   - Replace list views with Algolia search (query + facet filters + pagination).
   - Replace detail views with `getObject`/`getObjects` by `objectID` and explicit permission checks.
   - Replace aggregates with facet counts, rules, replicas, and/or analytics export.

4) Auth & Sessions (DB‑less)
   - Sessions: Switch to `signed_cookies` session backend to remove DB dependency.
   - Auth: Externalize identity to an IdP (e.g., Auth0 / OIDC). Use RemoteUser or JWT middleware to populate `request.user` without DB persistence. Option B (pragmatic): keep a minimal “virtual user” representation in memory or create a small, non-persistent adapter. Profiles for display live in Algolia.

5) Privacy & Access Control
   - Public/community: Readable via client search with an Algolia Secured API Key restricting filters to `privacy:community`.
   - Private/user: Client receives a Secured API Key scoping to `(user_id:<me> OR (privacy:community))` and relevant `group_ids`.
   - Sensitive reads (e.g., private detail views) may route through server using Admin API key with server-side permission checks.

6) Media
   - Migrate FileFields to external storage. Store only public or signed URLs in Algolia records. Ensure lifecycle, size limits, and CDN.

7) Observability & Reliability
   - Add server-side logging for all writes/reads to Algolia. Implement retry/backoff on writes. Consider a lightweight write-ahead log (WAL) to disk or queue if absolute durability is required during outages (trade-off, given “no local DB”).

## Migration Plan (Phased)
Phase 0 — Decisions & Risk Acceptance
1. Confirm “Algolia-only” scope and acceptance of non-transactional behavior, denormalization, and eventual consistency.
2. Choose Auth path: RemoteUser/JWT + signed-cookie sessions (no DB), or allow ephemeral/in-memory DB solely to satisfy Django internals (still no persisted local DB).
3. Choose media backend and domain/CDN.

Phase 1 — Inventory & Schema Mapping
4. Inventory each Django model and finalize the Algolia record schemas per index (fields, facets, ranking attributes, replicas).
5. Define ID strategy (UUID), timestamp fields, and backfill mapping from existing PKs.
6. Define permission model in filters: `privacy`, `user_id`, `group_ids`, `share_scope`.

Phase 2 — Infrastructure Setup
7. Provision Algolia app, create indices, replicas, synonyms, rules.
8. Configure API keys: Admin, Search, and server-minted Secured API Keys with strict filters and expirations.
9. Provision object storage + bucket policies for media.

Phase 3 — Export & Backfill
10. Freeze writes (maintenance window) or implement dual-write temporarily.
11. Export data with `dumpdata` and custom transforms to target schemas.
12. Upload media to object storage; patch URLs in records.
13. Bulk import into Algolia using batched operations.

Phase 4 — Read/Write Cutover (Feature‑flagged)
14. Introduce Data Service abstraction; behind a flag, route new writes to Algolia and reads to Algolia for selected views (community lists first).
15. Expand cutover to private reads and detail pages; implement server-side permission checks where needed.
16. Retire Django signals that assumed ORM persistence. Remove DB-driven background jobs.

Phase 5 — Remove Local DB
17. Switch session backend to signed cookies; disable DB session engine.
18. Replace auth pipeline to RemoteUser/JWT; stop relying on DB-backed `User` rows at request time.
19. Remove DB migrations/apps for domain models; keep only what’s required for middleware plumbing if any.
20. Remove `db.sqlite3` and database configuration from environments. Use environment checks to ensure no ORM usage remains.

Phase 6 — Hardening & Rollout
21. Performance tuning (attributes for faceting, replicas for ranking, caching headers).
22. Security review (filters, key minting, leakage checks for private data in indices).
23. Cost guardrails (per-index size, attribute pruning, TTLs where acceptable).
24. Monitoring & alerting (Algolia usage, error rates, media CDN).

## Data Model Mapping (Draft)
- Dream/Thing: Denormalize tags, themes, entities as arrays; include computed search-only fields (e.g., text n‑grams) if needed. Store author snippet `{user_id, display_name, avatar_url}`.
- Story: Store ordered `thing_ids` and a denormalized `things_preview` (titles, first image URL) for fast rendering.
- Patterns: Precompute metrics; store references as arrays.
- Sharing: For groups, store `member_user_ids` array; for direct shares, add `shared_with_user_ids` on each record.

## Security Model
- Write: Admin API key only on server.
- Read (public): Public search key with filters locked to `privacy:community` via Secured API Keys minted per request/session.
- Read (private/group): Secured API Key per user embedding `user_id` and allowed `group_ids` with short expiry; refresh on session renew.
- Detail endpoints: Server-side fetch + permission check for high-sensitivity views.

## Testing & Validation
- Unit tests for Data Service (create/update/delete), permission filters, and key minting.
- Snapshot tests on index records for key pages.
- Dry-run backfill in a staging Algolia app; verify record counts and spot-check searches.

## Rollback Plan
- Pre-migration: full `dumpdata` and media backup.
- Keep a read-only copy of the DB artifact post-cutover for a limited window.
- Feature flags to revert reads to legacy paths during early rollout if needed.

## Open Questions for the Team (and for Claude)
1. Are we comfortable moving ALL private content into Algolia, given audit/compliance constraints? If not, we may need a minimal durable store for sensitive data.
2. Which auth approach do we prefer: RemoteUser/JWT (stateless) vs. keeping a minimal, non-persistent DB stub just for Django auth plumbing?
3. What’s the media backend of choice (S3/R2/etc.) and retention policy?
4. Do we need analytics beyond Algolia Insights (e.g., page-level events)?
5. Any features that fundamentally require relational joins we must redesign (e.g., complex pattern graphs)?

## Next Steps
- Team to confirm scope and auth/session approach.
- I can produce finalized index schemas and a concrete field mapping per model.
- After Claude shares their plan, we’ll cross-review, reconcile differences, and lock scope/timeline.


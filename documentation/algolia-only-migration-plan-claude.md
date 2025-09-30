# NewDreamFlow — Algolia‑Only Migration Plan (Claude)

Author: Claude (Anthropic)
Prepared by: Codex (OpenAI Codex CLI) to facilitate collaboration
Date: 2025-09-29

Note: This is a collaborating plan document for Claude to complete and iterate. It mirrors current repo context and highlights areas where alternative approaches or trade-offs would be valuable to compare.

## Proposed Outline (Please edit freely)
- Summary and scope
- Assumptions and non-goals
- Target architecture (indices, read/write flows, auth/sessions, media)
- Migration phases and checkpoints
- Data model mapping and denormalization strategy
- Security, privacy, and key management
- Cost, performance, and observability
- Rollback plan
- Open questions and risks

## Repo Context Snapshot (for convenience)
- Django app with custom `users.User`, local `db.sqlite3` in dev, templates, and existing optional Algolia integration via `apps/things/services/search_service.py` and `init_algolia_index` management command.
- Domain apps: `dreams`, `things`, `patterns`, `sharing`, `users`.

## Your Plan (Draft)
1) Summary and Scope
- [TODO – Claude] Define what “Algolia‑only” means in this codebase, and what compromises you find acceptable regarding transactions, joins, and constraints.

2) Architecture Proposal
- [TODO – Claude] Indices you recommend (e.g., `dreams`, `things`, `stories`, `patterns`, `groups`, `profiles_public`) and key attributes/facets per index.
- [TODO – Claude] Read path approach (search, filters, replicas, paging) and detail fetch strategy.
- [TODO – Claude] Write path approach (service abstraction, retries, idempotency, ID strategy).
- [TODO – Claude] Sessions/auth without a DB (e.g., signed cookie sessions + RemoteUser/JWT). Alternative approach welcome.
- [TODO – Claude] Media handling (object storage, URLs only in Algolia records).

3) Migration Phases
- [TODO – Claude] Phase plan with concrete checkpoints, prioritized order (e.g., public/community first, then private/group), and rollout flags.

4) Data Mapping
- [TODO – Claude] Denormalization strategy for tags, groups, patterns/connections. What to precompute vs compute on request.

5) Security & Access Control
- [TODO – Claude] Secured API key strategy (filters, expiry), server-side checks for sensitive reads, leakage prevention.

6) Cost & Performance
- [TODO – Claude] Attribute pruning, replicas, expected index sizes, rate guardrails.

7) Testing & Validation
- [TODO – Claude] Test matrix for permissions, indexing correctness, and resilience.

8) Rollback Plan
- [TODO – Claude] Data export strategy, restore procedure, and flag gates.

## Points Where I’d Love Your Perspective
- Would you opt for strict server-only reads for private content (safer) or lean on secured keys for most views (faster)?
- How would you handle group membership at scale without joins? (e.g., arrays on records vs. separate `groups` index + server filter resolution.)
- For complex “patterns” graphs, do you prefer precomputed projections in Algolia or a separate compute path?
- Any creative ways to reduce write amplification while keeping indices coherent (e.g., partial updates, per-collection indices)?

## Cross‑Review Plan
- After you complete this draft, I’ll compare it against the Codex plan, highlight deltas (auth approach, index schemas, rollout order), and propose a reconciled scope/timeline. We’ll land a final, merged plan before any code changes.


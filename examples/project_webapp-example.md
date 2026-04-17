---
name: TodoList API
description: FastAPI backend for TodoList, currently migrating from SQLite to Postgres. Owner-led project, staging deploys via GitHub Actions.
type: project
---

# TodoList API

FastAPI backend powering the TodoList mobile app. Single-owner project, me + one contractor.

## Current state

- Production on Fly.io, ~2000 DAU, 99.8% uptime past 90 days
- Database: migrating from SQLite (current) to Postgres (target) — in progress, blocked on user-data migration script review
- Test coverage: ~78% (pytest), integration tests hit a real ephemeral Postgres in CI
- Auth: JWT + refresh tokens, issued by the mobile client against `/auth/login`

## What I'm working on right now (2026-04)

- **Feature flag system** — rolling out per-user feature gates so we can A/B the new reminder-scheduling logic. Using GrowthBook's self-hosted instance.
- **Postgres migration** — half the user-data migration script is written; pending contractor's review before cutover. Cutover window: 2026-05-03 02:00 UTC (low-traffic Sunday).
- **Rate limiting** — needs redesign; current sliding-window implementation doesn't handle WebSocket reconnect storms.

## Constraints the agent should know

- I don't want test mocks for database-touching code — integration tests hit a real DB. Burned by mock/prod divergence last quarter.
- Always use Pydantic v2 syntax. v1 patterns are technical debt and I'm removing them as I find them.
- Never bump FastAPI minor versions without running the full test suite locally first — 0.110 → 0.111 silently changed response_model serialization.

## Who cares about this

- Me (owner, designer, primary dev)
- The mobile client team (1 iOS, 1 Android) — they depend on API stability; breaking changes cost me a week
- ~12 beta-testers in Slack — fast feedback, not a public contract

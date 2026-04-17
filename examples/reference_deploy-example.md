---
name: Deploy to staging
description: Procedure for deploying the TodoList API to staging on Fly.io. Run before every merge to main.
type: reference
---

# Deploy to staging

Stage before prod, always. This doc is the procedure; the agent reads it when I ask "deploy to staging."

## Command

```bash
flyctl deploy --config fly.staging.toml --remote-only
```

## Preconditions

- `main` is clean locally (`git status` returns nothing unexpected)
- Staging DB is not in migration state (`flyctl status -a todolist-staging-db` shows `healthy`)
- My Fly token is valid (`flyctl auth whoami` returns me, not a 401)

## What can go wrong

- **Build cache stale** — if Python dependencies changed in `pyproject.toml` but not `poetry.lock`, the build will use the old lock. Fix: `poetry lock --no-update` before deploy.
- **Port binding race** — Fly's blue-green deploy occasionally fails health checks on cold start. Retry once with `flyctl deploy --strategy immediate` if blocked.
- **Secrets drift** — if a new env var was added to `.env.example` but not `flyctl secrets set`, the container will crash-loop. Check the deploy log for `KeyError` on first start.

## Rollback

```bash
flyctl releases list -a todolist-staging | head
flyctl releases rollback <version> -a todolist-staging
```

Rollback is idempotent; running it twice is fine.

## What NOT to do

- Do not `flyctl deploy` directly from a feature branch. Always `git checkout main && git pull` first. The image tag depends on the git SHA of the working tree.
- Do not skip the `--remote-only` flag. Local Docker builds on my M1 produce ARM images that Fly's x86 hosts reject.

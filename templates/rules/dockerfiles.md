---
paths:
  - "dockerfiles/**"
  - "Dockerfile"
  - "**/Dockerfile"
---

# Dockerfile Conventions

- Multi-stage builds preferred (separate build-time and runtime images)
- Pin base image versions — never use `:latest`
- Run as non-root user
- Minimize layers: combine related `RUN` commands
- Use `.dockerignore` to avoid shipping build artifacts and secrets
- Healthchecks: include `HEALTHCHECK` instruction for services

---
paths:
  - "terraform/**"
---

# Terraform / OpenTofu Conventions

Backend: your state backend (e.g., S3 + DynamoDB, MinIO, Terraform Cloud).

Provider versioning: pin all providers. Use `~>` for minor version flexibility.

Variable definitions: prefer map-based variables over repeated resources for multi-instance deployments.

Module structure: use modules for reusable patterns, keep root module thin.

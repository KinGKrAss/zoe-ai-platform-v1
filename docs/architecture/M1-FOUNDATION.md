# M1 – Foundation

## Purpose

M1 establishes a reproducible baseline for the Zoë AI Platform / Z1 Command Center.

## Components

- PostgreSQL 16 foundation service via Docker Compose
- Deterministic database initialization from `database/migrations`
- Zoë identity seed (`ZOE-CORE`, V1.0)
- Initial memory and audit-log tables
- GitHub Actions CI for container health, connectivity and migration visibility

## Acceptance Criteria

1. `docker compose up -d zoe-postgres` starts PostgreSQL.
2. The PostgreSQL healthcheck reaches `healthy`.
3. `pg_isready` succeeds against database `zoe`.
4. Initialization migrations execute with `ON_ERROR_STOP=1`.
5. CI tears the environment down after every run.
6. No secrets are required for the foundation CI job.

## Security Note

The Compose credentials are development-only defaults. Production credentials must be supplied through a secret manager or deployment environment and must never be committed to the repository.

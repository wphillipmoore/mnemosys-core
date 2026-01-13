# Alembic Schema Change Management Design

**Date**: 2026-01-03
**Status**: Draft (ADR captured; implementation in progress)

## Table of Contents
- [Overview](#overview)
- [Scope](#scope)
- [Non-Goals](#non-goals)
- [Current Repository State](#current-repository-state)
- [Local Alembic Setup](#local-alembic-setup)
  - [Schema configuration](#schema-configuration)
  - [Revision file naming](#revision-file-naming)
  - [Configuration invariants](#configuration-invariants)
- [Deployment Automation Model](#deployment-automation-model)
  - [Branch to environment mapping](#branch-to-environment-mapping)
  - [Startup migration gate](#startup-migration-gate)
  - [Deployment wiring (planned)](#deployment-wiring-planned)
- [Migration Safety and Rollback](#migration-safety-and-rollback)
- [Developer Workflow (Revision Creation and Testing)](#developer-workflow-revision-creation-and-testing)
  - [Required databases](#required-databases)
  - [Recommended database allocation](#recommended-database-allocation)
  - [When a separate database is required](#when-a-separate-database-is-required)
  - [Credentials and access model](#credentials-and-access-model)
  - [Sandbox role isolation (SQL)](#sandbox-role-isolation-sql)
  - [Bootstrap exit checklist (lockdown)](#bootstrap-exit-checklist-lockdown)
  - [Standard revision workflow](#standard-revision-workflow)
  - [Workflow invariants](#workflow-invariants)
- [Testing Strategy](#testing-strategy)
- [Observability and Audit](#observability-and-audit)
- [Migration Runner Contract](#migration-runner-contract)
  - [Inputs](#inputs)
  - [Behavior (Idempotent)](#behavior-idempotent)
  - [Exit Codes](#exit-codes)
  - [Logging Requirements](#logging-requirements)
  - [Security Constraints](#security-constraints)
  - [Integration Expectations](#integration-expectations)
- [Alembic Primary Tooling](#alembic-primary-tooling)
- [Implementation Plan and Sequence (Status)](#implementation-plan-and-sequence-status)
- [Open Questions](#open-questions)

## Overview

This document defines how MNEMOSYS manages PostgreSQL schema changes using Alembic, and how those changes are deployed alongside the REST API. The design favors explicit, deterministic behavior and avoids import-time side effects. A single startup migration gate runs before the API service, validates schema state, and applies pending Alembic revisions.

This is a design and workflow document. It captures current repository setup and the intended automation behavior, but some deployment plumbing (GitHub Actions and cloud service wiring) is still to be implemented.

## Scope

- Alembic configuration in the repo
- Revision naming conventions
- Automated schema deployment on service startup
- Environment mapping (develop, release, main) and sandbox semantics
- Developer workflow for creating and testing revisions
- Migration safety and failure handling

## Non-Goals

- Choosing the final production deployment mechanism (decision pending)
- Expanding deployment automation beyond the current nonprod pipeline
- Building multi-environment or multi-tenant migration tooling (out of scope for v0.1)

## Current Repository State

- Alembic is configured under `alembic/` with `alembic.ini` at the repo root.
- `env.py` loads database settings explicitly from environment variables (including admin credentials).
- Migration runner and validation tooling exist under `alembic/` and `scripts/dev/`.
- Alembic script contents under `alembic/` are generated artifacts and excluded from linting/testing/coverage; validation is handled via migration tooling.
- Nonprod deployment automation is implemented; production automation is pending.

## Local Alembic Setup

### Schema configuration

MNEMOSYS must support a configurable PostgreSQL schema name in SQLAlchemy. The schema should be:

- Overridable via environment variable (e.g., `MNEMOSYS_DB_SCHEMA`).
- Defaulted to the canonical schema used by automated deployments (current default: `mnemosys`).

This enables multiple isolated schemas inside a single development database while preserving one database per environment.

### Revision file naming

To preserve chronological ordering independent of revision hashes, migration filenames should be prefixed with a timestamp:

```
YYYY-MM-DD-HH-MM-<revision_id>-<message>.py
```

Implementation target:
- Configure Alembic `file_template` in `alembic.ini` to use the timestamp prefix.
- Include the Alembic revision ID and a short message slug in the filename for traceability.
- The message slug must be `snake_case` and very short, similar to a branch name (max 60 chars).

### Configuration invariants

- Alembic must use explicit settings loading (no import-time side effects).
- `MNEMOSYS_ENV` is the canonical environment selector.
- `MNEMOSYS_DB_ADMIN_*` is used for Alembic/admin operations (falls back to `MNEMOSYS_DB_*`).
- Component values are sourced from `MNEMOSYS_DB_*` or `MNEMOSYS_DB_ADMIN_*`, with environment defaults as fallback.

## Deployment Automation Model

### Branch to environment mapping

- `develop` -> development
- `release` -> test
- `main` -> production

Each merge into an eternal branch triggers a deployment to its mapped environment.

Sandbox is a pre-PR environment for feature/bugfix/hotfix work and is updated manually.

### Alembic workflow diagram

See `docs/diagrams/alembic-migration-workflow.md` for the Mermaid source.

Notes:
- Sandbox validation runs against a temporary schema and does not deploy.
- Production deployment automation is pending; the runtime migration gate is the target behavior.

### Startup migration gate

The REST API startup sequence must run an explicit migration gate before the API service starts. This gate is the only automatic schema application path. The logic is intentionally minimal and delegates concurrency handling to the database/Alembic.

Required behavior:
1. Read `MNEMOSYS_ENV` and database credentials (`MNEMOSYS_DB_ADMIN_*` with fallback to `MNEMOSYS_DB_*`).
2. Run `alembic current` and `alembic heads` to compare database revisions to head.
3. If current includes all head revisions, start the API service.
4. If current does not include head, run `alembic upgrade heads` (transactional).
5. If upgrade succeeds, re-run `alembic current` and confirm head is present, then start the API service.
6. If upgrade fails, re-run `alembic current`:
   - If current includes head now, assume another process won the race and proceed.
   - If current still does not include head, treat the upgrade failure as fatal and stop startup.

Fail-closed rules:
- If `alembic check` fails after a failed upgrade attempt, stop startup and fail loudly.
- If migrations fail and the database remains out of sync, stop startup and fail loudly.

### Deployment wiring (planned)

When the automation exists, the expected flow is:

1. Merge PR into `develop`, `release`, or `main`.
2. GitHub Actions deploys the REST API to the target environment.
3. Cloud service restarts the app.
4. Startup migration gate runs before API starts.

This design requires deployment automation to pass the correct environment variables and database credentials to the service.

## Migration Safety and Rollback

- All environments use the same automated upgrade/downgrade mechanism.
- Deployments must be reversible; an automated downgrade path is required.
- Manual downgrade commands are forbidden in every environment.
- Downgrades must be validated in non-production as part of the automated upgrade/downgrade process.
- If a migration requires data backfill, include it as explicit Alembic data migration steps.
- Destructive changes must be staged (add column, backfill, switch reads, drop column) to preserve rollback safety.

## Developer Workflow (Revision Creation and Testing)

### Required databases

Development environments use two databases with different access models:

- **Development deployment database** (`mnemosys_dev`): API-only access, mirrors test/production access constraints.
- **Sandbox database** (`mnemosys_sandbox`): admin access for schema testing with multiple schemas.

The sandbox database hosts:
- **Default schema**: used for interactive development and local API runs.
- **Ephemeral schemas**: created per revision test to validate upgrades and downgrades.

The goal is to avoid polluting the default schema when validating schema changes while keeping the deployed
development environment aligned with production access constraints.

Test environment notes:

- **Test database** (`mnemosys_test`): API-only access, updated only by release automation; local environments do not store test credentials.
- During bootstrap, `mnemosys_test` may share the non-production RDS instance with `mnemosys_dev` and `mnemosys_sandbox`.
- Before any external users access test, `mnemosys_test` must move to a dedicated RDS instance with separate network access controls.

### Recommended database allocation

Human developer:
- One local Postgres instance with one development database and multiple schemas.

AI or automated tasks:
- Prefer ephemeral schemas per run or per branch (suffix with a unique ID).
- Avoid long-lived shared schemas across automated agents.

### When a separate database is required

Use a separate development database only when the change cannot be isolated by schema:

- Migrations that touch database-level objects (roles, extensions, databases, or ALTER DATABASE).
- Tests that require database-level configuration (collation, ICU locale, encoding, or default privileges).
- Scenarios that must validate a truly empty database bootstrap (not just an empty schema).

Default position: use the shared development sandbox database with per-branch schemas.

### Credentials and access model

- Alembic tooling uses **admin credentials** to create schemas and apply migrations in the sandbox database.
- Admin credentials are provided via `MNEMOSYS_DB_ADMIN_*`; if unset, the tooling falls back to `MNEMOSYS_DB_*`.
- The REST API uses a **non-admin** database user via `MNEMOSYS_DB_*`; application testing must never use admin credentials.
- The development deployment database remains API-only; direct admin access is not assumed.
- Bootstrap exception: the development RDS instance may be publicly accessible with IP allowlisting, but local environments must store only sandbox credentials and the sandbox role must be denied `CONNECT` on `mnemosys_dev`. Bootstrap ends when end-to-end automation updates `mnemosys_dev` and restarts the REST API service, at which point `mnemosys_dev` must be fully locked down.

### Sandbox role isolation (SQL)

Create sandbox roles for schema management (admin) and application testing (non-admin), and explicitly deny access to the deployment database. Use underscores in role names to avoid quoted identifiers.

```sql
CREATE ROLE mnemosys_sandbox_admin LOGIN PASSWORD 'replace_me';
CREATE ROLE mnemosys_sandbox_user LOGIN PASSWORD 'replace_me';
GRANT ALL PRIVILEGES ON DATABASE mnemosys_sandbox TO mnemosys_sandbox_admin;
GRANT CONNECT ON DATABASE mnemosys_sandbox TO mnemosys_sandbox_user;
REVOKE CONNECT ON DATABASE mnemosys_dev FROM mnemosys_sandbox_admin;
REVOKE CONNECT ON DATABASE mnemosys_dev FROM mnemosys_sandbox_user;
```

Optional hardening for existing roles:

```sql
REVOKE CONNECT ON DATABASE mnemosys_dev FROM PUBLIC;
```

Grant schema and table access for application testing (run as admin):

```sql
GRANT USAGE ON SCHEMA mnemosys TO mnemosys_sandbox_user;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA mnemosys TO mnemosys_sandbox_user;
GRANT USAGE, SELECT, UPDATE ON ALL SEQUENCES IN SCHEMA mnemosys TO mnemosys_sandbox_user;
ALTER DEFAULT PRIVILEGES FOR ROLE mnemosys_sandbox_admin IN SCHEMA mnemosys
    GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO mnemosys_sandbox_user;
ALTER DEFAULT PRIVILEGES FOR ROLE mnemosys_sandbox_admin IN SCHEMA mnemosys
    GRANT USAGE, SELECT, UPDATE ON SEQUENCES TO mnemosys_sandbox_user;
```

### Bootstrap exit checklist (lockdown)

- Disable public access on the development RDS instance.
- Remove any temporary inbound rules (TCP 5432) from security groups.
- Rotate admin credentials and store them outside local `.env`.
- Ensure local environments only reference sandbox credentials.
- Verify `mnemosys_dev` accepts connections only from the REST API runtime role.

### Standard revision workflow

1. Update SQLAlchemy models.
2. Generate a revision:
   ```bash
   python scripts/dev/alembic_revision.py short_snake_case_message
   ```
3. Review the revision and edit by hand if needed.
4. Run automated migration validation (temp schema upgrade/downgrade):
   ```bash
   python scripts/dev/validate_migrations.py
   ```
   Optional seed script:
   ```bash
   python scripts/dev/validate_migrations.py --seed-script <path-to-seed-script>
   ```
5. Commit the revision file and model changes.

### Workflow invariants

- Never generate a revision against production.
- Never run `alembic downgrade` manually against production.
- Upgrade and downgrade processes must be symmetric and automated.
- Always review autogenerate output for unintended drops or renames.
- Table and column renames must be implemented explicitly in revisions; autogenerate treats renames as drop/create by default.
- Upgrade and downgrade validation is mandatory for every revision.

## Testing Strategy

Implemented validation steps (local and CI):

- Integration tests spin up Postgres via Testcontainers.
- `scripts/dev/validate_migrations.py` creates a temporary schema, runs upgrade and downgrade, and cleans up.
- Optional seed scripts can populate minimal data before validation.
- CI runs `pytest -m integration` in a dedicated job to enforce migration safety.

## Observability and Audit

Migration gate logs should include:

- Environment name
- Current revision
- Head revision
- Migration duration
- Success or failure status

This data should be captured in deployment logs for post-mortem debugging.

## Migration Runner Contract

This section defines the required contract for the startup migration runner. Implementation details can vary (shell, Python entrypoint, or init container), but the contract must hold.

### Inputs

- `MNEMOSYS_ENV` (required): `sandbox`, `development`, `test`, `production`
- `MNEMOSYS_DB_ADMIN_*` (required for migrations): database admin credentials (driver, username, password, host, port, database, sslmode)
- `MNEMOSYS_DB_*` (fallback): non-admin database credentials used when admin variables are unset
- `MNEMOSYS_DB_SCHEMA` (optional): target schema name (defaults to canonical schema)
- `ALEMBIC_CONFIG` (optional): path to `alembic.ini` (defaults to repo root)
- `MNEMOSYS_DOWNGRADE_TARGET` (required for downgrade): revision identifier or `base`

### Behavior (Idempotent)

**Upgrade runner**
- Run `alembic current` and `alembic heads`.
- If current does not include head, run `alembic upgrade heads`.
- If upgrade fails, re-run `alembic current`.
- Exit success if current includes head at the end of the sequence.
- Exit failure if current does not include head after a failed upgrade attempt.

**Downgrade runner**
- Run `alembic downgrade <target>`.
- If target is explicit, verify with `alembic current`.
- If target is `base`, skip verification.
- Exit failure if downgrade fails or verification fails.

### Exit Codes

- `0`: schema is at head (either initially or after upgrade).
- `1`: schema is not at head after upgrade attempt.
- `2`: configuration error (missing env var, invalid database settings).

### Logging Requirements

- Emit start/end markers.
- Log environment name and database host (redact credentials).
- Log `alembic current` and `alembic heads` results.
- Log upgrade attempt status and elapsed time.
- On failure, emit a short reason and exit code.

### Security Constraints

- Never log full database URLs with credentials.
- Never run `alembic downgrade` in the startup gate; downgrades require explicit rollback invocation.
- Never run against production unless `MNEMOSYS_ENV=production`.

### Integration Expectations

- Executed before the API service boot.
- Must be the first step in the container or service startup.
- Fail-fast on configuration errors.

## Alembic Primary Tooling

Alembic is the primary and sufficient tooling for schema management and deployment automation. No alternative
migration frameworks are planned. Revisit only if Alembic cannot satisfy operational constraints (see
`docs/decisions/0002-alembic-schema-management.md`).

## Implementation Plan and Sequence (Status)

See `docs/plans/pending/2026-01-06-alembic-release-squash-and-extraction-plan.md` for the
pipeline-only validation flow, release-time squashing policy, and extraction plan.

Phase 0: Formalize the decision (completed)
- Create an ADR under `docs/decisions/` reflecting the Alembic-first decision and revisit triggers. (done: `docs/decisions/0002-alembic-schema-management.md`)

Phase 1: Schema configurability (completed)
- Add `MNEMOSYS_DB_SCHEMA` to settings with a default schema name for automated deployments. (done)
- Update SQLAlchemy metadata/engine/session handling to support a configurable schema without import-time side effects. (done)
- Ensure Alembic uses the same schema (version table schema, autogenerate behavior). (done)

Phase 2: Revision tooling (completed)
- Implement/confirm `alembic.ini` `file_template` to enforce `YYYY-MM-DD-HH-MM-<revision_id>-<message>.py`. (done)
- Add a wrapper script for `alembic revision` that enforces short `snake_case` messages. (done)
- Update developer docs to require the wrapper script. (done)

Phase 3: Migration runner (upgrade and downgrade) (completed)
- Implement a migration runner that follows the `alembic check` / `alembic upgrade heads` flow. (done)
- Implement the symmetric downgrade runner using the same mechanism and logging contract. (done)
- Ensure both runners are environment-agnostic and respect `MNEMOSYS_ENV` and `MNEMOSYS_DB_SCHEMA`. (done)

Phase 4: Ephemeral schema validation harness (in progress)
- Implement tooling to create a temporary schema, apply upgrade, seed minimal data, run smoke tests, run downgrade, and drop schema (see `scripts/dev/validate_migrations.py`).
- Integrate the harness into local validation and CI (non-docs-only changes). (local: done; CI: done)
- TODO: add a minimal seed script (or document a required seed script contract).
- Add a targeted integration test to run the harness in CI. (done: `tests/integration/test_migrations_postgres.py`)

Phase 5: Operational integration (pending)
- Wire the migration runner into the service startup path (init step or pre-start script).
- Document required environment variables and failure modes.
- Add observability hooks (logs/metrics) for migration steps.

Phase 6: End-to-end validation (pending)
- Run full local validation (`python scripts/dev/validate_local.py`) with migration checks included.
- Dry-run the deployment sequence in a non-production environment.

## Open Questions

- Should the migration gate run inside the app container or as a separate deploy step?
- What is the preferred advisory lock strategy for multi-instance startup?
- Do we need a broader migration smoke test beyond the current upgrade/downgrade harness?
- What is the preferred AI-friendly database allocation strategy?

# Alembic Schema Change Management Design

**Date**: 2026-01-03
**Status**: Draft (awaiting AWS tooling comparison and final ADR)

## Overview

This document defines how MNEMOSYS manages PostgreSQL schema changes using Alembic, and how those changes are deployed alongside the REST API. The design favors explicit, deterministic behavior and avoids import-time side effects. A single startup migration gate runs before the API service, validates schema state, and applies pending Alembic revisions.

This is a design and workflow document. It captures current repository setup and the intended automation behavior, but some deployment plumbing (GitHub Actions and cloud service wiring) is still to be implemented.

## Scope

- Alembic configuration in the repo
- Revision naming conventions
- Automated schema deployment on service startup
- Environment mapping (develop, release, main)
- Developer workflow for creating and testing revisions
- Migration safety and failure handling

## Non-Goals

- Choosing the final AWS-native deployment mechanism (decision pending)
- Implementing CI/CD or cloud deploy automation (documented requirements only)
- Building multi-environment or multi-tenant migration tooling (out of scope for v0.1)

## Current Repository State

- Alembic is configured under `src/mnemosys_core/migrations` with `alembic.ini`.
- `env.py` loads database settings explicitly from `MNEMOSYS_ENV` and `DATABASE_URL`.
- There is no migration runner script in the repo yet.
- Deployment automation is not implemented yet.

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
- `DATABASE_URL` always overrides defaults.
- `MNEMOSYS_ENV` is the canonical environment selector.

## Deployment Automation Model

### Branch to environment mapping

- `develop` -> development
- `release` -> test
- `main` -> production

Each merge into an eternal branch triggers a deployment to its mapped environment.

### Startup migration gate

The REST API startup sequence must run an explicit migration gate before the API service starts. This gate is the only automatic schema application path. The logic is intentionally minimal and delegates concurrency handling to the database/Alembic.

Required behavior:
1. Read `MNEMOSYS_ENV` and `DATABASE_URL`.
2. Run `alembic check` to compare database revision to `heads`.
3. If check succeeds, start the API service.
4. If check fails, run `alembic upgrade heads` (transactional).
5. If upgrade succeeds, start the API service.
6. If upgrade fails, re-run `alembic check`:
   - If check succeeds now, assume another process won the race and proceed.
   - If check still fails, treat the upgrade failure as fatal and stop startup.

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
- The REST API should use a **non-admin** database user in all environments; application testing must never use admin credentials.
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
   alembic revision --autogenerate -m "describe change"
   ```
3. Review the revision and edit by hand if needed.
4. Create a temporary schema for validation.
5. Apply upgrades to the temporary schema:
   ```bash
   MNEMOSYS_ENV=development MNEMOSYS_DB_SCHEMA=<temp_schema> DATABASE_URL=<dev_db_url> alembic upgrade head
   ```
6. Validate downgrade safety in the temporary schema:
   ```bash
   MNEMOSYS_ENV=development MNEMOSYS_DB_SCHEMA=<temp_schema> DATABASE_URL=<dev_db_url> alembic downgrade -1
   ```
7. Re-apply upgrade and run tests against the upgraded temporary schema if needed.
8. Drop the temporary schema.
9. Commit the revision file and model changes.

### Workflow invariants

- Never generate a revision against production.
- Never run `alembic downgrade` manually against production.
- Upgrade and downgrade processes must be symmetric and automated.
- Always review autogenerate output for unintended drops or renames.
- Table and column renames must be implemented explicitly in revisions; autogenerate treats renames as drop/create by default.
- Upgrade and downgrade validation is mandatory for every revision.

## Testing Strategy (Planned)

Planned validation steps for CI or local checks:

- Create a temporary schema in the development database.
- Run `alembic upgrade head` against the temporary schema.
- Seed minimal dummy data required by tests (via optional seed script).
- Run a targeted smoke test suite against the upgraded schema.
- Run `alembic downgrade -1` against the temporary schema.
- Drop the temporary schema after validation.

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

- `MNEMOSYS_ENV` (required): `development`, `test`, `production`
- `DATABASE_URL` (required): target database connection string
- `MNEMOSYS_DB_SCHEMA` (optional): target schema name (defaults to canonical schema)
- `ALEMBIC_CONFIG` (optional): path to `alembic.ini` (defaults to repo root)
- `MNEMOSYS_DOWNGRADE_TARGET` (required for downgrade): revision identifier or `base`

### Behavior (Idempotent)

**Upgrade runner**
- Run `alembic check`.
- If check fails, run `alembic upgrade heads`.
- If upgrade fails, re-run `alembic check`.
- Exit success if check succeeds at the end of the sequence.
- Exit failure if check fails after a failed upgrade attempt.

**Downgrade runner**
- Run `alembic downgrade <target>`.
- If target is explicit, verify with `alembic current`.
- If target is `base`, skip verification.
- Exit failure if downgrade fails or verification fails.

### Exit Codes

- `0`: schema is at head (either initially or after upgrade).
- `1`: schema is not at head after upgrade attempt.
- `2`: configuration error (missing env var, invalid URL).

### Logging Requirements

- Emit start/end markers.
- Log environment name and database host (redact credentials).
- Log `alembic check` result.
- Log upgrade attempt status and elapsed time.
- On failure, emit a short reason and exit code.

### Security Constraints

- Never log full database URLs with credentials.
- Never run `alembic downgrade` automatically.
- Never run against production unless `MNEMOSYS_ENV=production`.

### Integration Expectations

- Executed before the API service boot.
- Must be the first step in the container or service startup.
- Fail-fast on configuration errors.

## Decision Checkpoint: AWS Tooling Comparison

Before implementation is finalized, compare this Alembic-first design with AWS-native options. Evaluation criteria:

- Operational safety (locking, failure recovery, rollback support)
- Auditability and traceability
- Integration with RDS operational controls (snapshots, blue/green)
- Automation complexity
- Long-term maintainability for non-authors

The outcome should be captured as an Architecture Decision Record (ADR).

## ADR Draft: Alembic-First vs AWS-Native Schema Tooling

**Status**: Decision made, pending formal ADR

### Context

MNEMOSYS currently uses SQLAlchemy and Alembic for schema management. Deployment automation is not yet implemented. The AWS platform decision explicitly states provider-native tooling should be preferred when it reduces complexity without harming durability.

### Decision Drivers

- Operational safety and recoverability
- Schema change auditability
- Ability to run in all environments consistently
- Automation complexity and survivability without original authors
- Fit with current application startup model

### Options

1. **Alembic-first (current design)**
2. **AWS-native migration tooling** (RDS automation, migration via deployment hooks, or managed workflows)
3. **Hybrid** (AWS-native orchestration, Alembic execution inside a controlled step)

### Pros / Cons (Initial)

**Alembic-first**
- Pros: already in repo; deterministic; portable across environments; supports offline review of revision history.
- Cons: requires custom orchestration; app startup coupling; needs explicit failure handling.

**AWS-native**
- Pros: reduces custom tooling; integrates with RDS operational controls; may simplify deployments.
- Cons: potentially less portable; may require provider-specific workflows; might reduce local parity.

**Hybrid**
- Pros: keep Alembic semantics while delegating orchestration to AWS.
- Cons: risk of split ownership; more moving parts.

### Decision

Adopt Alembic end-to-end for schema management and deployment automation in the near term. Revisit AWS-native tooling after the Alembic workflow is implemented and stabilized.

### Rationale

- Prefer a single tooling path that works across environments and providers.
- Team has existing expertise with Alembic, reducing near-term execution risk.
- Acknowledge tension: provider independence is not a strategic priority, but the practical benefits of Alembic justify the choice for now.

### Revisit Triggers

- AWS-native tooling demonstrably reduces operational risk or complexity.
- Alembic-based automation creates persistent deployment friction.
- Organizational constraints shift toward deeper AWS-specific integration.

## Implementation Plan and Sequence (Status)

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
- Integrate the harness into local validation and CI (non-docs-only changes). (local: done; CI: pending)
- TODO: add a minimal seed script (or document a required seed script contract).
- TODO: add a targeted pytest subset to run against the temp schema.

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
- What is the minimal migration test suite required for CI?
- What is the preferred AI-friendly database allocation strategy?

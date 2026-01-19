# Alembic Release Squash + Extraction Plan

**Status:** Draft

## Table of Contents
- [Context](#context)
- [Goals](#goals)
- [Non-Goals](#non-goals)
- [Invariants](#invariants)
- [End-to-End Pipeline Validation](#end-to-end-pipeline-validation)
- [Release-Time Squash Design](#release-time-squash-design)
- [Stamp Policy](#stamp-policy)
- [Extraction Plan](#extraction-plan)
- [Open Questions](#open-questions)

## Context

Long-lived Alembic revision chains tend to decay as code evolves. The project requires a
reliable "rebuild from scratch" path while minimizing fragile historical migrations.
Release checkpoints are the natural time to squash revisions into a stable baseline.

Development and test database updates must occur only through GitHub Actions pipelines.
Developers hold only sandbox credentials and should not apply migrations to dev/test out of band.

This plan extends `docs/plans/in-progress/2026-01-03-alembic-schema-management-design.md`.

## Goals

- Prove the entire migration pipeline works end to end using a dummy change that flows
  through PRs to `develop` and `release`.
- Ensure the database can always be rebuilt from scratch from the current repository state.
- Establish a release-time squashing workflow that trims fragile revision history.
- Prepare the Alembic design and guidelines for extraction into a reusable repository.

## Non-Goals

- Reconstructing arbitrary historical schema states from the main branch after squashing.
- Allowing local developers to access dev/test database credentials.
- Solving multi-tenant or multi-database migration orchestration.

## Invariants

- No implicit side effects at import time.
- Development/test updates only via GitHub Actions pipelines.
- Sandbox credentials only on developer machines.
- Rebuild-from-scratch must succeed on the current head after each release squash.
- Squashing must fail loudly when the database is not at a known safe revision.

## End-to-End Pipeline Validation

1. Create a reversible dummy model change and generate a revision via
   `python3 scripts/dev/alembic_revision.py <short_snake_case>`.
2. Validate locally in the sandbox only:
   `python3 scripts/dev/validate_migrations.py`.
3. Open PR to `develop` and merge.
   - GitHub Actions deploys to development.
   - Migration gate runs via pipeline (no manual migration).
   - Capture migration runner output from the pipeline logs.
4. Open PR from `develop` to `release` and merge.
   - GitHub Actions deploys to test.
   - Migration gate runs via pipeline (no manual migration).
   - Capture migration runner output from the pipeline logs.
5. Create a cleanup migration to remove the dummy change and repeat the same pipeline flow.

## Release-Time Squash Design

1. At a release checkpoint, create a new baseline revision that fully represents
   the current schema state.
   - The baseline must be a standalone build-from-scratch path.
2. Archive pre-release revisions outside Alembic's active version path
   (example: `alembic/versions_archive/<release>`).
3. Preserve historical reconstruction by keeping release tags that still contain
   the old revision chain.
4. Update the migration gate or pipeline to handle both states:
   - Fresh database: `alembic upgrade head` applies the baseline.
   - Existing database at old head: `alembic stamp <baseline>` then `alembic upgrade head`.
   - Anything else: fail loudly.

## Stamp Policy

`alembic stamp` updates `alembic_version` only and must never be used as a repair tool.
Stamping is only allowed when the current revision is exactly the known old head that
was superseded by the squash. Any other state is a hard failure.

## Extraction Plan

Phase 1: Documentation extraction (post end-to-end validation)
- Create a standalone repository for Alembic design and integration guidelines.
- Migrate and normalize content from:
  - `docs/plans/in-progress/2026-01-03-alembic-schema-management-design.md`
  - This plan (release squash + pipeline validation)
- Provide a repository-agnostic integration contract:
  - Required environment variables
  - Migration runner behavior
  - Validation workflow expectations

Phase 2: Template and tooling (optional)
- Define a minimal, reusable template:
  - `alembic.ini`, `alembic/env.py`, `alembic/script.py.mako`
  - `scripts/dev/alembic_revision.py`, `scripts/dev/validate_migrations.py`
  - Optional migration runner entrypoint
- Identify integration points that must be injected by host projects
  (settings loader, metadata import, schema naming).
- Evaluate feasibility of packaging common tooling without hard-coding
  the host application's config model.

## Open Questions

- Where should the "stamp if old head" logic live: migration runner vs pipeline step?
- Which branch should host the squashed baseline for the next cycle?
- Should archived revisions remain in-repo or move to a separate archive repository?

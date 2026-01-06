# Testcontainers Postgres Evaluation

Context: Evaluate replacing SQLite-based unit tests with Postgres via Testcontainers to align
test semantics with production and eliminate reliance on the sandbox database.

---

## Table of Contents
- [Context](#context)
- [Goal](#goal)
- [Evaluation Summary](#evaluation-summary)
- [Pros](#pros)
- [Cons](#cons)
- [Decision](#decision)
- [Implementation Notes](#implementation-notes)
- [Recommendation](#recommendation)
- [Decision Criteria](#decision-criteria)
- [Risks](#risks)
- [Open Questions](#open-questions)

## Context

Current unit tests run against SQLite. Alembic migration validation now runs against
the sandbox Postgres database using a temporary schema.

## Goal

Capture the tradeoffs of switching unit tests to Postgres via Testcontainers, including
impact on developer workflow, reliability, and fidelity to production behavior.

## Evaluation Summary

Moving all tests to Testcontainers improves correctness for Postgres-specific behavior but
adds runtime cost and operational fragility. The strongest value appears in migration and
integration testing rather than in every unit test.

## Pros

- Fidelity to production: schemas, sequences, enums, JSON, and DDL behavior match deployment.
- Eliminates dependency on a shared sandbox database for testing.
- Surfaces Postgres-specific bugs that SQLite can mask.
- Ephemeral containers provide a clean database state per run.

## Cons

- Slower test runs due to container startup and schema creation overhead.
- Requires Docker installed and running; failures become infrastructure-related.
- Pulling images adds network dependency and increases CI complexity.
- Unit test reliability degrades when Docker is unavailable.
- 100 percent coverage policy becomes harder to guarantee if tests depend on Docker health.

## Decision

Adopt a split strategy:
- Keep SQLite for unit tests.
- Add a new integration test suite that runs Postgres via Testcontainers.

This keeps unit tests fast and deterministic while adding a production-faithful layer for
schema and migration behavior.

## Implementation Notes

- Integration tests should run automatically in GitHub Actions as a separate job or test
  marker, not as a manual step.
- Migration validation should be part of the automated integration suite to prevent human
  error or skipped steps.

## Recommendation

Keep SQLite for unit tests and add Postgres Testcontainers for targeted integration and
Alembic validation. This maximizes correctness where it matters while preserving fast,
reliable unit tests.

## Decision Criteria

- Accept slower test runtime and Docker dependency for all developers.
- Confirm CI supports Docker reliably without special handling.
- Decide whether 100 percent coverage requirements are compatible with Docker availability.
- Verify that integration-only coverage closes the highest-risk gaps.

## Risks

- Testcontainers currently emits a deprecation warning for its internal
  `@wait_container_is_ready` decorator. This is inside the dependency,
  not our code. Track upstream updates and bump when the warning is removed.

## Open Questions

- Do we want to replace the sandbox Postgres validation with Testcontainers, or keep both?
- Should migration validation always run locally, or only in CI?
- What performance budget is acceptable for the full test suite?

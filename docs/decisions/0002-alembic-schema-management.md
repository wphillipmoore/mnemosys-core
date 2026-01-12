# 0002 — Alembic-First Schema Management

## Table of Contents
- [Status](#status)
- [Context](#context)
- [Decision](#decision)
- [Consequences](#consequences)
  - [Positive](#positive)
  - [Negative](#negative)
- [Revisit Triggers](#revisit-triggers)
- [Notes](#notes)

## Status
Accepted

## Context

MNEMOSYS requires a deterministic, automated process for applying database
schema changes across sandbox, development, test, and production environments.

Alembic provides a complete solution for this problem in the current
architecture and is already integrated with SQLAlchemy-based models.

## Decision

Adopt Alembic end-to-end as the primary and sufficient schema management and
deployment automation tooling. This includes:

- Alembic-driven revision generation and migration history
- Automated upgrade and downgrade runners using Alembic commands
- Consistent behavior across sandbox, development, test, and production

## Consequences

### Positive

- Single tooling path across environments
- Leverages existing Alembic experience and reduces initial risk
- Clear, versioned schema history in the repository
- Avoids provider-specific migration coupling in schema automation

### Negative

- Requires custom orchestration for deployments and rollbacks
- Adds migration runner code that must be maintained

## Revisit Triggers

- Alembic-based automation creates persistent deployment friction
- Alembic cannot satisfy reliability, observability, or rollback requirements

## Notes

This decision stands unless operational constraints materially change.

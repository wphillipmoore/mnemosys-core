
# 0001 — Repository Structure

## Status
Accepted (v0.1)

## Context

This document captures the initial repository layout for `mnemosys-core`.
The goal is to establish structural invariants early, while the project is
in a high-risk, high-velocity phase.

The guiding principle is long-term survivability without original authorship.
Boring, explicit structure is preferred over cleverness.

## Decision

The repository adopts a `src/` layout with a single top-level package,
`mnemosys_core`, and clear separation of concerns:

- Configuration semantics (`config/`)
- Database and ORM concerns (`db/`)
- Utilities with explicit contracts (`util/`)
- Tests that mirror source layout (`tests/`)
- CI configuration isolated under `.github/`
- Architectural memory captured under `docs/decisions/`

The database layer is intentionally isolated and minimal. No global engine
state or implicit side effects are permitted at import time.

## Consequences

### Positive

- Prevents import ambiguity
- Encourages small, behavioral tests
- Makes schema evolution explicit and testable
- Supports future extraction of API, CLI, or worker services

### Negative

- Slightly more verbose structure early
- Requires discipline to keep modules small

## Notes

This decision is locked at v0.1. Revisions require a new decision record.

# MNEMOSYS Core

**MNEMOSYS** (pronounced /ˈniːməˌsɪs/, or "NEE-muh-sis")

Core backend for the MNEMOSYS system.

## Table of Contents
- [What It Is](#what-it-is)
- [Quickstart](#quickstart)
- [Development](#development)
- [Where the Rules Live](#where-the-rules-live)

## What It Is

MNEMOSYS Core is a database-first Python backend with explicit structural
invariants designed for long-term maintenance. The system avoids implicit
state and side effects at import time; engines, sessions, and configuration
are created explicitly.

## Quickstart

Requires Python 3.14+.

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -e .
```

Use the virtual environment for all Python invocations and always call
`python3` (never `python`). On macOS, `python` may not exist outside the venv.

## Development

Before starting any new development effort, run the unit tests and confirm they
pass. This avoids inheriting broken local artifacts from prior work.

All commands below assume the `.venv` is active. Always use `python3` for
Python invocations.

```bash
pytest tests/
```

```bash
# Full local validation (tests, coverage, lint, type check)
python3 scripts/dev/validate_local.py

# Run tests only
pytest tests/

# Bootstrap a local database (if needed)
python3 scripts/dev/bootstrap_db.py
```

Note: the validation script uses Poetry under the hood; install Poetry if
you plan to run the full local checks.

## Where the Rules Live

- Canonical standards and conventions: https://github.com/wphillipmoore/standards-and-conventions/tree/develop
- Branching and deployment model: https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/code-management/branching-and-deployment.md
- In-repo standards in development and MNEMOSYS terminology: `docs/standards-and-conventions.md`
- Repository structure ADR: `docs/decisions/0001-repo-structure.md`

If the canonical standards cannot be retrieved, treat it as a fatal exception
and notify the user before proceeding.

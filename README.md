# MNEMOSYS Core

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
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

Use the virtual environment for all Python invocations. On macOS, `python`
may not exist outside the venv.

## Development

Before starting any new development effort, run the unit tests and confirm they
pass. This avoids inheriting broken local artifacts from prior work.

```bash
pytest tests/
```

```bash
# Full local validation (tests, coverage, lint, type check)
python scripts/dev/validate_local.py

# Run tests only
pytest tests/

# Bootstrap a local database (if needed)
python scripts/dev/bootstrap_db.py
```

Note: the validation script uses Poetry under the hood; install Poetry if
you plan to run the full local checks.

## Where the Rules Live

- Canonical standards and conventions: https://github.com/wphillipmoore/standards-and-conventions
- Branching and deployment model: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/code-management/branching-and-deployment.md
- In-repo standards in development and MNEMOSYS terminology: `docs/standards-and-conventions.md`
- Repository structure ADR: `docs/decisions/0001-repo-structure.md`

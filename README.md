# MNEMOSYS Core

Core backend for the MNEMOSYS system.

## What It Is

MNEMOSYS Core is a database-first Python backend with explicit structural
invariants designed for long-term maintenance. The system avoids implicit
state and side effects at import time; engines, sessions, and configuration
are created explicitly.

## Quickstart

Requires Python 3.13+.

```bash
python -m venv .venv
source .venv/bin/activate
pip install -e .
```

## Development

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

- Branching and deployment model: `docs/project/final/Development_Branching_Deployment_Model.md`
- Coding standards and conventions: `docs/standards-and-conventions.md`
- Repository structure ADR: `docs/decisions/0001-repo-structure.md`

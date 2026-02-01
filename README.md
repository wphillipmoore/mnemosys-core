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
python3 -m pip install uv==0.9.26
uv sync --group dev
```

Use the uv-managed environment for all Python invocations and always call
`uv run python3` (never `python`). On macOS, `python` may not exist outside the venv.

## Development

Before starting any new development effort, run the unit tests and confirm they
pass. This avoids inheriting broken local artifacts from prior work.

All commands below use `uv run python3` to ensure the uv environment is active.

```bash
uv run pytest tests/
```

```bash
# Full local validation (tests, coverage, lint, type check)
uv run python3 scripts/dev/validate_local.py

# Run tests only
uv run pytest tests/

# Bootstrap a local database (if needed)
uv run python3 scripts/dev/bootstrap_db.py
```

## Where the Rules Live

- Canonical standards and conventions: https://github.com/wphillipmoore/standards-and-conventions/tree/develop
- Branching and deployment model: https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/code-management/branching-and-deployment.md
- In-repo standards in development and MNEMOSYS terminology: `docs/standards-and-conventions.md`
- Repository structure ADR: `docs/decisions/0001-repo-structure.md`

If the canonical standards cannot be retrieved, treat it as a fatal exception
and notify the user before proceeding.

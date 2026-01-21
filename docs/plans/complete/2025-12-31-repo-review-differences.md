# Repository Review - Notable Differences (Codex)

Scope: high-level scan of docs, config, CI, core modules, and tests. Not every file was read line-by-line.

## Table of Contents
- [Significant Differences I Would Make](#significant-differences-i-would-make)

## Significant Differences I Would Make

1. Remove module-level session state (resolved)
   - Current: dependency state is stored on `app.state` in `src/mnemosys_core/api/dependencies.py`.
   - Status: addressed; no further change required.

2. Strengthen typing for `Exercise.domains`
   - Current: `domains` stored as `list[str]` via JSON.
   - Preferred: enum-backed field or association table to enforce valid values at DB/API boundaries.

3. Replace JSON string type decorators where possible
   - Current: `JSONEncodedList`/`JSONEncodedDict` serialize to strings in SQLite.
   - Preferred: use native JSON/JSONB where supported and keep SQLite compatibility via JSON type or dialect handling; reduces custom type risk.

4. Align API naming with domain naming (resolved)
   - Current: endpoints use `/api/v1/practices` and align with `Practice` models.
   - Status: addressed; no further change required.

5. Keep ruff/mypy/uv sync out of pytest
   - Current: tool checks run in CI as explicit steps; local validation lives in `scripts/dev/validate_local.py`.
   - Preferred: keep pytest behavioral; keep tooling gates explicit and scripted.

6. Prune unused dependencies
   - `requests` appears unused in `src/` and tests.
   - `alembic` and `psycopg2-binary` are required for migration tooling and Postgres integration tests.
   - Preferred: remove `requests` if it remains unused.

7. Expand README beyond a one-liner (resolved)
   - Current: README includes quickstart, development, and rules.
   - Status: addressed; no further change required.

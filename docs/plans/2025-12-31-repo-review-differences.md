# Repository Review - Notable Differences (Codex)

Scope: high-level scan of docs, config, CI, core modules, and tests. Not every file was read line-by-line.

## Significant Differences I Would Make

1. Remove module-level session state
   - Current: global `_session_factory` in `src/mnemosys_core/api/dependencies.py`.
   - Preferred: store on `app.state` or inject via a closure to avoid hidden global state and improve multi-app/test safety.

2. Strengthen typing for `Exercise.domains`
   - Current: `domains` stored as `list[str]` via JSON.
   - Preferred: enum-backed field or association table to enforce valid values at DB/API boundaries.

3. Replace JSON string type decorators where possible
   - Current: `JSONEncodedList`/`JSONEncodedDict` serialize to strings in SQLite.
   - Preferred: use native JSON/JSONB where supported and keep SQLite compatibility via JSON type or dialect handling; reduces custom type risk.

4. Align API naming with domain naming
   - Current: endpoints `/api/v1/sessions` operate on `Practice`.
   - Preferred: rename endpoints or models to remove semantic drift and reduce documentation/test churn.

5. Keep ruff/mypy/poetry sync out of pytest
   - Current: tool checks run in CI as explicit steps; local validation lives in `scripts/dev/validate_local.py`.
   - Preferred: keep pytest behavioral; keep tooling gates explicit and scripted.

6. Prune unused dependencies
   - `requests`, `alembic`, and `psycopg2-binary` appear unused in `src/` now.
   - Preferred: remove until needed to reduce surface area and lockfile churn.

7. Expand README beyond a one-liner
   - Preferred: a short “what it is / how to run / where rules live” to reduce bootstrapping friction.

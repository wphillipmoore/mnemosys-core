# CI Hard-Gates Transition - Next Steps

**Status:** Completed

Context: shift ruff/mypy enforcement out of pytest and into CI, remove
tests/test_code_compliance.py, and add a local validation script.

## Table of Contents
- [Completed Steps](#completed-steps)

## Completed Steps

1. Ensured working branch was `feature/ci-hard-gates` and clean.
2. Deleted `tests/test_code_compliance.py`.
3. Updated `.github/workflows/ci.yml` to add explicit hard-gate steps for:
   - `poetry run ruff check`
   - `poetry run mypy src/`
4. Added a local validation script that runs:
   - `poetry sync --dry-run`
   - `poetry run ruff check`
   - `poetry run mypy src/`
   - `poetry run pytest --cov=mnemosys_core --cov-report=term-missing --cov-branch`
5. Updated docs to remove `test_code_compliance.py` references and point to new gates:
   - `AGENTS.md`
   - `docs/standards-and-conventions.md`
   - `docs/plans/complete/2025-12-31-github-actions-ci-design.md`
   - `docs/plans/complete/2025-12-31-github-actions-ci-implementation.md`
6. Ran full validation and proceeded with PR/merge per checkpoints.

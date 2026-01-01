# CI Hard-Gates Transition - Next Steps

Context: shift ruff/mypy enforcement out of pytest and into CI, remove
tests/test_code_compliance.py, and add a local validation script.

## TODO (in order)

1. Ensure working branch is `feature/ci-hard-gates` and clean.
2. Delete `tests/test_code_compliance.py`.
3. Update `.github/workflows/ci.yml` to add explicit hard-gate steps for:
   - `poetry run ruff check`
   - `poetry run mypy src/`
4. Add a local validation script that runs:
   - `poetry sync --dry-run`
   - `poetry run ruff check`
   - `poetry run mypy src/`
   - `poetry run pytest --cov=mnemosys_core --cov-report=term-missing --cov-branch`
5. Update docs to remove `test_code_compliance.py` references and point to new gates:
   - `AGENTS.md`
   - `docs/standards-and-conventions.md`
   - `docs/plans/2025-12-31-github-actions-ci-design.md`
   - `docs/plans/2025-12-31-github-actions-ci-implementation.md`
6. Run full validation; proceed with PR/merge per checkpoints.

# GitHub Actions CI Implementation Plan

**Status:** Implemented

**Goal:** Implement automated CI/CD pipeline that enforces 100% test coverage, code quality checks, and Python version compatibility on all PRs and eternal branch pushes.

**Architecture:** GitHub Actions workflow with a unit/coverage gate and a separate integration-test job. Unit coverage runs on Python 3.14; integration tests run on Python 3.14.

**Tech Stack:** GitHub Actions, uv, pytest, pytest-cov, ruff, mypy, Testcontainers

---

## Table of Contents
- [Task 1: Implement GitHub Actions Workflow](#task-1-implement-github-actions-workflow)
- [Task 2: Test Workflow Execution](#task-2-test-workflow-execution)
- [Task 3: Update Documentation to Reference Automated CI](#task-3-update-documentation-to-reference-automated-ci)
- [Task 4: Verify Branch Protection Integration](#task-4-verify-branch-protection-integration)
- [Task 5: Final Validation](#task-5-final-validation)
- [Success Criteria](#success-criteria)
- [Notes](#notes)

## Task 1: Implement GitHub Actions Workflow

**Files:**
- Modify: `.github/workflows/ci.yml` (replace placeholder)

**Step 1: Replace placeholder workflow with complete CI configuration**

Replace the entire contents of `.github/workflows/ci.yml`:

```yaml
name: CI - Test and Validate

on:
  pull_request:
  push:
    branches:
      - develop
      - main
      - 'release/**'

permissions:
  contents: read

concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true

jobs:
  test-and-validate:
    name: test-and-validate
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ["3.14"]

    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install uv
        run: python3 -m pip install uv==0.9.26

      - name: Cache uv
        uses: actions/cache@v4
        with:
          path: ~/.cache/uv
          key: uv-${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('uv.lock') }}
          restore-keys: |
            uv-${{ runner.os }}-py${{ matrix.python-version }}-

      - name: Install dependencies
        run: uv sync --frozen --group dev

      - name: Run ruff check
        run: uv run ruff check

      - name: Run mypy
        run: uv run mypy src/

      - name: Run tests with coverage
        run: |
          uv run pytest \
            -m "not integration" \
            --cov=mnemosys_core \
            --cov-report=term-missing \
            --cov-branch \
            --cov-report=xml \
            --cov-fail-under=100

      - name: Upload coverage report
        if: matrix.python-version == '3.14'
        uses: actions/upload-artifact@v4
        with:
          name: coverage-report
          path: coverage.xml

  integration-tests:
    name: integration-tests
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v4

      - name: Set up Python 3.14
        uses: actions/setup-python@v5
        with:
          python-version: "3.14"

      - name: Install uv
        run: python3 -m pip install uv==0.9.26

      - name: Cache uv
        uses: actions/cache@v4
        with:
          path: ~/.cache/uv
          key: uv-${{ runner.os }}-py3.14-${{ hashFiles('uv.lock') }}
          restore-keys: |
            uv-${{ runner.os }}-py3.14-

      - name: Install dependencies
        run: uv sync --frozen --group dev

      - name: Run integration tests
        run: uv run pytest -m integration
```

**Step 2: Verify YAML syntax**

Run: `cat .github/workflows/ci.yml`
Expected: Complete workflow file with proper YAML formatting

**Step 3: Commit workflow**

Create `/tmp/commit-msg.txt` (no heredoc) with:

```
feat: implement automated CI/CD pipeline with GitHub Actions

Replace placeholder CI workflow with full implementation that enforces:
- 100% test coverage (line and branch)
- All tests passing
- Code quality checks (ruff, mypy as explicit CI steps)
- Python 3.14 (required)

Workflow features:
- Triggers on PRs and pushes to eternal branches (develop, main, release/*)
- uv dependency caching for 10-20x speedup
- Single-version testing on Python 3.14
- Concurrency control (cancel stale runs)
- Coverage XML artifact upload for future integrations

Branch protection requires: test-and-validate (3.14) and integration-tests status checks

🤖 Generated with Codex CLI

Co-Authored-By: mnemosys-codex <252598091+mnemosys-codex@users.noreply.github.com>
```

Then run:

```bash
git add .github/workflows/ci.yml
git commit -F /tmp/commit-msg.txt
rm /tmp/commit-msg.txt
```

Expected: Commit created successfully

---

## Task 2: Test Workflow Execution

**Step 1: Push branch to origin**

Run: `git push -u origin feature/github-actions-ci`
Expected: Branch pushed successfully, workflow triggers automatically

**Step 2: Monitor workflow run**

Run: `gh run list --branch feature/github-actions-ci --limit 1`
Expected: See workflow run starting/in-progress

**Step 3: Wait for workflow completion and check status**

Run: `gh run watch`
Expected: `test-and-validate` completes successfully for Python 3.14 and `integration-tests` completes successfully on Python 3.14.

**Step 4: If workflow fails, investigate and fix**

Run: `gh run view --log`
Expected: Review logs, identify issue, fix locally, commit, push again

**Note:** This step may require iteration. Common issues:
- Docker/Testcontainers availability in GitHub Actions runners
- Cache key issues (workflow should fallback gracefully)
- uv installation issues (verify pinned version install)

---

## Task 3: Update Documentation to Reference Automated CI

**Files:**
- Modify: standards-and-conventions repo `docs/code-management/source-control-guidelines.md` (CI/CD constraints)
- Optional: `README.md` (quick reference for `validate_local.py`)

**Step 1: Update standards to describe current CI**
- Document `test-and-validate` and `integration-tests` jobs.
- Note Python 3.14 is required.
- Note integration tests use Testcontainers and require Docker.

**Step 2: Verify Table of Contents entries remain accurate**

**If any test fails:**
1. Fix the issue
2. Commit the fix
3. Re-run the test suite
4. Only proceed when everything passes
```

**Step 2: Verify update**

Run: `rg -n "CI/CD" ../../../github/standards-and-conventions/docs/code-management/source-control-guidelines.md`
Expected: CI/CD section reflects two jobs, Python version policy, and integration tests

**Step 3: Commit documentation update**

- Create a temp commit message file (no heredoc).
- `git add docs/code-management/source-control-guidelines.md` (in standards-and-conventions repo)
- `git commit -F /tmp/commit-msg.txt`

**Step 4: Push documentation update**

Run: `git push`
Expected: Push succeeds, triggers another CI run (should pass)

---

## Task 4: Verify Branch Protection Integration

**Step 1: Check branch protection status**

Run: `gh api repos/:owner/:repo/branches/develop/protection/required_status_checks`
Expected: See existing required status checks for develop branch

**Step 2: Verify test-and-validate (3.14) and integration-tests are available as status checks**

After workflow completes, check:
Run: `gh pr create --base develop --title "Test PR" --body "Testing CI" --draft`
Expected: Draft PR created, shows "test-and-validate (3.14)" and "integration-tests" as pending/required checks

**Step 3: Close draft PR if created**

Run: `gh pr close --delete-branch=false`
Expected: Draft PR closed (keep branch for actual PR creation later)

**Note:** If branch protection doesn't automatically pick up the new status checks, add "test-and-validate (3.14)" and "integration-tests" to required status checks in GitHub UI.

---

## Task 5: Final Validation

**Step 1: Run full test suite locally one final time**

Run: `uv run pytest --cov=mnemosys_core --cov-report=term-missing --cov-branch --cov-fail-under=100`
Expected: All tests pass, 100% coverage achieved

**Step 2: Verify all commits follow conventions**

Run: `git log --oneline feature/github-actions-ci ^develop`
Expected: See 3 commits with proper conventional commit format

**Step 3: Verify workflow file is valid**

Run: `cat .github/workflows/ci.yml | head -20`
Expected: See properly formatted GitHub Actions YAML

**Step 4: Ready for PR creation**

Status check:
- ✅ Workflow implemented and tested
- ✅ Documentation updated
- ✅ All local tests passing
- ✅ CI workflow passing on GitHub

Next: Submit PR following standard process (validation → user approval → push → submit PR → finalize)

---

## Success Criteria

- ✅ GitHub Actions workflow file replaces placeholder
- ✅ Workflow triggers on PRs and eternal branch pushes
- ✅ Unit testing on Python 3.14
- ✅ Python 3.14 failures block PR merges
- ✅ Caching implemented for uv and dependencies
- ✅ Coverage enforcement at 100% (lines and branches)
- ✅ Documentation updated to reference automated CI
- ✅ Workflow runs successfully on feature branch

## Notes

- Python 3.14 must pass for merge readiness
- First workflow run may be slower due to cache misses
- Subsequent runs should be 10-20x faster with caching
- Workflow automatically enforces same standards as manual validation

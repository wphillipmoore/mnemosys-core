# GitHub Actions CI/CD Pipeline Design

**Date**: 2025-12-31
**Status**: Completed

## Table of Contents
- [Overview](#overview)
- [Requirements](#requirements)
- [Workflow Triggers](#workflow-triggers)
- [Job Structure](#job-structure)
- [Python Version Strategy](#python-version-strategy)
- [Execution Steps](#execution-steps)
- [Caching Strategy](#caching-strategy)
- [Concurrency Control](#concurrency-control)
- [Permissions](#permissions)
- [Artifacts](#artifacts)
- [Success Criteria](#success-criteria)
- [Future Enhancements (Not Implemented)](#future-enhancements-not-implemented)
- [Philosophy](#philosophy)

## Overview

Automate enforcement of code quality standards (tests, coverage, linting, type checking) using GitHub Actions. This replaces manual pre-push validation with automated CI checks that block PR merges when standards aren't met.

## Requirements

- **100% code coverage** (line and branch) - strict enforcement
- **All tests passing** - zero tolerance for failures
- **Code quality checks** (ruff, mypy) - enforced via explicit CI steps
- **Python version support** - test on 3.14 only
- **Eternal branch protection** - run on PRs and pushes to develop/main/release/*

## Workflow Triggers

```yaml
on:
  pull_request:
  push:
    branches:
      - develop
      - main
      - 'release/**'
```

**Rationale**:
- PRs provide the main guard rail (block merges until checks pass)
- Eternal branch checks provide sanity verification of merge process
- Feature branches excluded (allows pushing broken code as backups)

## Job Structure

**Three jobs**:
- `dependency-audit` (vulnerability scan)
  - Runs on: `ubuntu-latest`
  - Python 3.14 only
  - Audits `requirements.txt` and `requirements-dev.txt` with pip-audit
- `test-and-validate` (unit coverage gate)
  - Runs on: `ubuntu-latest` (AWS-compatible, deployable to common Linux platforms)
  - Matrix: Python 3.14
  - Excludes integration tests via marker
- `integration-tests` (migration + Postgres fidelity)
  - Runs on: `ubuntu-latest`
  - Python 3.14 only
  - Executes `uv run pytest -m integration` (Testcontainers; Docker required)

## Python Version Strategy

| Version | Status | Behavior |
|---------|--------|----------|
| 3.14 | **Required** | blocks PR merge |

**Branch protection** requires: `dependency-audit`, `test-and-validate (3.14)`, and `integration-tests` status checks

## Execution Steps

**dependency-audit**
1. **Checkout code** (`actions/checkout@v4`)
2. **Set up Python 3.14** (`actions/setup-python@v5`)
3. **Install dependencies** (`uv sync --frozen --group dev`, includes `pip-audit`)
4. **Run pip-audit**:
   ```bash
   uv run pip-audit -r requirements.txt -r requirements-dev.txt
   ```

**test-and-validate**
1. **Checkout code** (`actions/checkout@v4`)
2. **Set up Python** (`actions/setup-python@v5` with matrix version)
3. **Install uv** (pinned version via `python3 -m pip install uv==0.9.26`)
4. **Cache uv** (optional; cache `~/.cache/uv`)
5. **Cache dependencies**
   - Key: `uv-${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('uv.lock') }}`
   - Restores uv cache on cache hit
   - Falls back to fresh install on miss
6. **Install dependencies** (`uv sync --frozen --group dev`)
7. **Run ruff**:
   ```bash
   uv run ruff check
   ```
8. **Run mypy**:
   ```bash
   uv run mypy src/
   ```
9. **Run tests with coverage (exclude integration)**:
   ```bash
   uv run pytest \
     -m "not integration" \
     --cov=mnemosys_core \
     --cov-report=term-missing \
     --cov-branch \
     --cov-report=xml \
     --cov-fail-under=100
   ```
   - Validates: tests pass, 100% coverage
   - Fails if coverage < 100% (lines OR branches)
   - Generates XML report for future integration

**integration-tests**
1. **Checkout code** (`actions/checkout@v4`)
2. **Set up Python 3.14** (`actions/setup-python@v5`)
3. **Install uv** (pinned version via `python3 -m pip install uv==0.9.26`)
4. **Cache uv**
5. **Cache dependencies**
6. **Install dependencies** (`uv sync --frozen --group dev`)
7. **Run integration tests**:
   ```bash
   uv run pytest -m integration
   ```

## Caching Strategy

**Benefits**:
- 10-20x speedup (1-2 minutes → 10 seconds for dependency installation)
- Efficient during active development (multiple PRs reuse cache)
- Reduced PyPI load and GitHub Actions compute time

**Risk mitigation**:
- Cache key includes `uv.lock` hash (critical for cache invalidation)
- Includes Python version and OS in key
- Auto-fallback to fresh install on cache miss

**Cache key format**:
```
uv-${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('uv.lock') }}
```

## Concurrency Control

```yaml
concurrency:
  group: ${{ github.workflow }}-${{ github.ref }}
  cancel-in-progress: true
```

**Rationale**: Cancel stale runs when new commits pushed to same PR (saves compute time during rapid iteration)

## Permissions

```yaml
permissions:
  contents: read
```

**Rationale**: Minimal permissions (security best practice), no write access needed

## Artifacts

- **Coverage XML report** (uploaded for Python 3.14 only)
- Enables future Codecov integration

## Success Criteria

- ✅ Python 3.14 `test-and-validate` passes (blocks merge if fails)
- ✅ `integration-tests` passes (blocks merge if required by branch protection)
- ✅ 100% line and branch coverage achieved in unit suite
- ✅ Ruff and mypy checks pass (explicit CI steps)

## Future Enhancements (Not Implemented)

- Weekly scheduled run bypassing cache (verify fresh installs work)
- Codecov integration for coverage tracking over time

## Philosophy

This implementation supports the project's goal of "AI-assisted code perfection" - maintaining standards (100% coverage, zero warnings) that human teams wanted but couldn't sustain. If strict standards eventually block meaningful progress, they can be relaxed with full context about when and why the bar needed to be lowered.

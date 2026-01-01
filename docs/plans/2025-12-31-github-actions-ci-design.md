# GitHub Actions CI/CD Pipeline Design

**Date**: 2025-12-31
**Status**: Approved for implementation

## Overview

Automate enforcement of code quality standards (tests, coverage, linting, type checking) using GitHub Actions. This replaces manual pre-push validation with automated CI checks that block PR merges when standards aren't met.

## Requirements

- **100% code coverage** (line and branch) - strict enforcement
- **All tests passing** - zero tolerance for failures
- **Code quality checks** (ruff, mypy) - enforced via explicit CI steps
- **Forward-looking Python support** - test on 3.13 (required), 3.14, 3.15 (informational)
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

**Single job**: `test-and-validate`
- Runs on: `ubuntu-latest` (AWS-compatible, deployable to common Linux platforms)
- Matrix: Python 3.13, 3.14, 3.15
- Fail-fast: Disabled (see all Python version results)

## Python Version Strategy

| Version | Status | Behavior |
|---------|--------|----------|
| 3.13 | **Required** | `continue-on-error: false` - blocks PR merge |
| 3.14 | Informational | `continue-on-error: true` - nice to know |
| 3.15 | Informational | `continue-on-error: true` - early warning system |

**Branch protection** requires: `test-and-validate (3.13)` status check

## Execution Steps

1. **Checkout code** (`actions/checkout@v4`)
2. **Set up Python** (`actions/setup-python@v5` with matrix version)
3. **Cache Poetry installation** (cache `~/.local/share/pypoetry`, `~/.local/bin/poetry`)
4. **Install Poetry** (official installer, skip if cached)
5. **Cache dependencies**
   - Key: `poetry-${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('poetry.lock') }}`
   - Restores virtualenv on cache hit
   - Falls back to fresh install on miss
6. **Install dependencies** (`poetry install --no-interaction`)
7. **Run ruff**:
   ```bash
   poetry run ruff check
   ```
8. **Run mypy**:
   ```bash
   poetry run mypy src/
   ```
9. **Run tests with coverage**:
   ```bash
   poetry run pytest \
     --cov=mnemosys_core \
     --cov-report=term-missing \
     --cov-branch \
     --cov-report=xml \
     --cov-fail-under=100
   ```
   - Validates: tests pass, 100% coverage
   - Fails if coverage < 100% (lines OR branches)
   - Generates XML report for future integration

## Caching Strategy

**Benefits**:
- 10-20x speedup (1-2 minutes → 10 seconds for dependency installation)
- Efficient during active development (multiple PRs reuse cache)
- Reduced PyPI load and GitHub Actions compute time

**Risk mitigation**:
- Cache key includes `poetry.lock` hash (critical for cache invalidation)
- Includes Python version and OS in key
- Auto-fallback to fresh install on cache miss

**Cache key format**:
```
poetry-${{ runner.os }}-py${{ matrix.python-version }}-${{ hashFiles('poetry.lock') }}
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

- **Coverage XML report** (uploaded for Python 3.13 only)
- Enables future Codecov integration
- Avoids duplicate uploads from 3.14/3.15

## Success Criteria

- ✅ Python 3.13 job passes (blocks merge if fails)
- ✅ 100% line and branch coverage achieved
- ✅ All tests pass
- ✅ Ruff and mypy checks pass (explicit CI steps)
- ℹ️ Python 3.14/3.15 results visible but don't block

## Future Enhancements (Not Implemented)

- Weekly scheduled run bypassing cache (verify fresh installs work)
- Codecov integration for coverage tracking over time
- Dependency vulnerability scanning (Dependabot, Safety)

## Philosophy

This implementation supports the project's goal of "AI-assisted code perfection" - maintaining standards (100% coverage, zero warnings) that human teams wanted but couldn't sustain. If strict standards eventually block meaningful progress, they can be relaxed with full context about when and why the bar needed to be lowered.

# MNEMOSYS Core

Core backend for the MNEMOSYS system - a database-first Python backend with explicit structural invariants designed for long-term maintainability.

## Architecture Overview

This project follows a **database-first architecture** with explicit structural invariants. The guiding principle is long-term survivability without original authorship - boring, explicit structure is preferred over cleverness.

### Core Principle

**No implicit state or side effects at import time.** The database engine, models, and configuration are isolated and must be explicitly instantiated.

## Before You Act: Consult Documentation First

**CRITICAL**: This project follows a documentation-first methodology. All knowledge required for any AI agent to work effectively is present in the repository. **Always read the relevant documentation BEFORE taking action** - never rely on trial-and-error.

### Required Reading Before Common Operations

**Git Operations (commit, push, branch, merge)**
- **MUST READ**: `docs/project/final/Development_Branching_Deployment_Model.md`
- **Key Rules**:
  - NEVER push directly to develop/main/release (eternal branches)
  - ALL changes to eternal branches MUST go through pull requests
  - ALWAYS create a fresh feature branch from clean develop
  - NEVER reuse old branch names

**Pull Request Operations (creating, submitting, merging)**
- **MUST READ**: `docs/standards-and-conventions.md` → "Pull Request Submission Process"
- **MUST READ**: `docs/standards-and-conventions.md` → "Pull Request Finalization Process"
- **Key Rules**:
  - 100% test success required before PR creation
  - 100% line AND branch coverage required
  - All code quality checks (ruff, mypy) must pass
  - Follow three-step finalization process after merge

**Code Quality and Standards**
- **MUST READ**: `docs/standards-and-conventions.md` → "Python Coding Standards"
- **Key Rules**:
  - PEP-compliant code only
  - Complete type hints for all public functions
  - 100% code coverage (lines and branches)
  - No abbreviations in variable names (minimum 3 characters)

**Database Changes (models, migrations, schema)**
- **MUST READ**: `docs/standards-and-conventions.md` → "Database Conventions"
- **Key Rules**:
  - Table names are singular, not plural
  - Follow model file organization rules
  - One file per database table (with documented exceptions)

### The RTFM Principle

**You should NOT need to be told to read the documentation.** If you find yourself:
- Using trial-and-error to discover workflow rules
- Getting error messages that correct your approach
- Guessing at conventions or standards

**STOP.** You missed reading the relevant documentation. Go back and read it before proceeding.

The 30 seconds spent reading documentation prevents hours of cleanup work.

### User Confirmation Checkpoints

**CRITICAL**: Always pause and request user confirmation at these checkpoints in the workflow. Never proceed automatically.

**Checkpoint: Before Creating Pull Request**

After completing work and committing to your feature branch, **STOP** and ask:

```
Create PR?
```

**What this gives the user:**
- Opportunity to review the work before it becomes a PR
- Chance to decide if the work is actually complete
- Ability to request additional changes before PR creation
- Control over the workflow pace

**Only proceed with PR creation after explicit user approval.**

**Workflow sequence:**
1. Complete work on feature branch
2. Commit changes locally
3. ⏸️ **PAUSE** - Ask: "Create PR?"
4. Wait for user response
5. If approved: Push branch and create PR
6. If not approved: Make requested changes, go back to step 2

**Checkpoint: Before Finalizing Pull Request**

After creating the PR, **STOP** and ask:

```
Finalize PR?
```

**What "Finalize" means** (unless user specifies otherwise):
1. Merge PR with squash merge and delete remote branch
2. Update local develop branch (checkout and pull)
3. Run final validation (tests, coverage, quality checks)
4. Ready for next iteration of changes

**What this checkpoint gives the user:**
- Time to review the PR on GitHub
- Opportunity to check CI/CD results (when implemented)
- Ability to add reviewers or request changes
- Control over when changes land in develop

**Only proceed with PR finalization after explicit user approval.**

**Complete workflow with both checkpoints:**
1. Complete work on feature branch
2. Commit changes locally
3. ⏸️ **PAUSE #1** - Ask: "Create PR?"
4. If approved: Push branch and create PR
5. ⏸️ **PAUSE #2** - Ask: "Finalize PR?"
6. If approved: Execute three-step finalization (merge, update develop, validate)
7. If not approved: Wait for user to review/request changes

## Project Structure

```
mnemosys-core/
├── src/mnemosys_core/          # Main package
│   ├── config/                 # Environment parsing and settings (no side effects)
│   │   ├── settings.py         # Settings loaded explicitly, not at import time
│   │   └── environments.py     # Dev/test/production semantics
│   ├── db/                     # Database engine, base declarations, and ORM models
│   │   ├── base.py             # Declarative base for ORM models
│   │   ├── engine.py           # Engine creation factories
│   │   └── models/             # ORM models (currently empty, awaiting development)
│   ├── migrations/             # Alembic migrations (not yet implemented)
│   └── util/                   # Explicit utilities (e.g., UTC-only time handling)
├── tests/                      # Tests mirror source layout
│   ├── conftest.py             # Shared pytest fixtures
│   ├── db/                     # Database tests
│   │   ├── test_models_smoke.py    # Validate ORM model declarations
│   │   └── test_metadata.py        # Verify schema consistency
│   └── util/                   # Utility tests
├── scripts/dev/                # Development scripts
│   └── bootstrap_db.py         # Local database bootstrapping
├── docs/decisions/             # Architectural Decision Records (ADRs)
│   └── 0001-repo-structure.md  # Repository structure decision
└── .github/                    # CI/CD configuration
    ├── copilot-instructions.md # AI coding agent instructions
    └── workflows/              # GitHub Actions workflows
```

## Technology Stack

- **Python**: 3.13+
- **Database ORM**: SQLAlchemy (no specific version constraint yet)
- **Testing**: pytest
- **Package Layout**: `src/` layout with single top-level package
- **Migrations**: Alembic (planned, not yet implemented)

## Key Dependencies

Currently minimal - avoid adding heavy dependencies without justification.

## Development Workflow

### Setting Up the Environment

```bash
# Clone the repository
git clone <repository-url>
cd mnemosys-core

# Create and activate virtual environment (recommended)
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies
pip install -e .
```

### Database Bootstrapping

For local development:

```bash
python scripts/dev/bootstrap_db.py
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run specific test directory
pytest tests/db/
pytest tests/util/

# Run with coverage (if configured)
pytest --cov=mnemosys_core tests/
```

## Coding Conventions

### 1. No Global State

- Engine creation and session management must be **explicit**
- Configuration is loaded but **not applied globally at import time**
- Utilities have **explicit contracts** (see `util/time.py` for UTC-only pattern)

### 2. Database Layer

- All ORM models **inherit from declarative base** in `db/base.py`
- Engine factories are in `db/engine.py`
- Models live in `db/models/` (currently empty)
- Migrations will use Alembic under `src/mnemosys_core/migrations/`

### 3. Test Structure

- Tests **mirror source layout**: `tests/db/` for database tests, `tests/util/` for utility tests
- Use `tests/conftest.py` for shared pytest fixtures
- **Smoke tests** validate ORM model declarations
- **Metadata invariant tests** verify schema consistency

### 4. Import Policy

- **No wildcard imports** - be explicit
- **No side effects at import time**
- Keep modules small and focused

### 5. Module Documentation

- Empty modules should have minimal comments (see existing files)
- Document assumptions and constraints for utilities

## When Adding New Features

1. **New ORM models**:
   - Add to `src/mnemosys_core/db/models/`
   - Inherit from `db/base.py` declarative base
   - Add smoke tests in `tests/db/`

2. **New utilities**:
   - Create in `src/mnemosys_core/util/`
   - Document explicit contracts (what assumptions/constraints apply)
   - Add tests in `tests/util/`

3. **New configuration**:
   - Extend `src/mnemosys_core/config/settings.py` or `environments.py`
   - **No import-time side effects**

4. **New tests**:
   - Mirror the source directory structure under `tests/`
   - Use appropriate fixtures from `conftest.py`

## Environment Configuration

Use `config/environments.py` to distinguish dev/test/production contexts.

## CI/CD

- CI pipeline defined in `.github/workflows/ci.yml` (currently placeholder)
- EditorConfig enforces LF line endings and final newlines across all files

## Architectural Decisions

See `docs/decisions/` for Architectural Decision Records (ADRs):

- **0001-repo-structure.md**: Why the layout is this way (locked at v0.1)

## Important Notes

- This structure prevents import ambiguity
- Encourages small, behavioral tests
- Makes schema evolution explicit and testable
- Supports future extraction of API, CLI, or worker services
- Requires discipline to keep modules small

## References

- [Repository Structure Decision](docs/decisions/0001-repo-structure.md)
- [AI Coding Agent Instructions](.github/copilot-instructions.md)

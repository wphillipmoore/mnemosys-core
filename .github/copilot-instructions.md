# AI Coding Agent Instructions for mnemosys-core

## Architecture Overview

This is a **database-first Python backend** with explicit structural invariants designed for long-term maintainability. See [docs/decisions/0001-repo-structure.md](docs/decisions/0001-repo-structure.md) for the design rationale.

### Core Principle
No implicit state or side effects at import time. The database engine, models, and configuration are isolated and must be explicitly instantiated.

### Key Components

- **`src/mnemosys_core/config/`** - Environment parsing and settings (no side effects at import)
- **`src/mnemosys_core/db/`** - Database engine, base declarations, and ORM models
- **`src/mnemosys_core/util/`** - Explicit utilities (e.g., UTC-only time handling)
- **`src/mnemosys_core/migrations/`** - Will contain Alembic migrations (not yet implemented)
- **`tests/`** - Test organization mirrors source structure

## Project Conventions

### 1. No Global State
- Engine creation and session management must be explicit
- Configuration is loaded but not applied globally at import time
- Utilities have explicit contracts (see `util/time.py` for UTC-only pattern)

### 2. Test Structure
- Tests mirror source layout: `tests/db/` for database tests, `tests/util/` for utility tests
- Use `tests/conftest.py` for shared pytest fixtures
- Smoke tests (`test_models_smoke.py`) validate ORM model declarations
- Metadata invariant tests (`test_metadata.py`) verify schema consistency

### 3. Database Layer
- All ORM models inherit from declarative base in `db/base.py`
- Engine factories are in `db/engine.py`
- Models live in `db/models/` (currently empty, awaiting development)
- Migrations will use Alembic under `src/mnemosys_core/migrations/`

### 4. Development Workflow
- Local database bootstrapping via `scripts/dev/bootstrap_db.py`
- CI pipeline defined in `.github/workflows/ci.yml` (currently placeholder)
- EditorConfig enforces LF line endings and final newlines across all files

## When Adding New Features

1. **New models**: Add to `src/mnemosys_core/db/models/`, inherit from `db/base.py` declarative base
2. **New utilities**: Create in `src/mnemosys_core/util/` with explicit contracts (document what assumptions or constraints apply)
3. **New configuration**: Extend `src/mnemosys_core/config/settings.py` or `environments.py` (no import-time side effects)
4. **New tests**: Mirror the source directory structure under `tests/`

## Code Style & Patterns

- **Imports**: No wildcard imports; be explicit
- **Module docstrings**: Empty modules should have minimal comments (see existing files)
- **Environment-aware code**: Use `config/environments.py` to distinguish dev/test/production contexts
- **Dependencies**: Currently minimal; avoid adding heavy dependencies without justification

## Useful Commands

```bash
# Run tests
pytest tests/

# Database bootstrap (local development only)
python scripts/dev/bootstrap_db.py

# Type checking (setup if mypy is configured)
# Check .github/workflows/ci.yml for current CI commands
```

## References

- [Repository Structure Decision](docs/decisions/0001-repo-structure.md) - Why the layout is this way
- [src/mnemosys_core/config/](src/mnemosys_core/config/) - Settings and environment handling
- [src/mnemosys_core/db/](src/mnemosys_core/db/) - Database abstractions
- [tests/](tests/) - Test organization and patterns

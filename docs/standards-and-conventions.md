# MNEMOSYS Standards and Conventions

This document captures coding standards, naming conventions, and architectural patterns for the MNEMOSYS project. These conventions ensure consistency, maintainability, and alignment with the project's core principles.

---

## Python Coding Standards

### Philosophy

**Core Principle**: MNEMOSYS code is **PEP-compliant first and foremost**, making it maximally readable and maintainable for any Python developer.

**Enforcement Strategy**:
1. **Strict automated enforcement** via ruff (linting) and mypy (type checking)
2. **All PEP exceptions must be documented** in configuration files (pyproject.toml, mypy.ini, etc.) with rationale
3. **Follow emerging community standards** when PEPs don't specify a convention
4. **Optimize for readability** - if a human can't easily understand it, it's wrong

**Tool Configuration**:
- Ruff: Enabled rule sets documented in `[tool.ruff]` section of pyproject.toml
- Mypy: Strict mode with any relaxations documented in `[tool.mypy]` section
- All exceptions to default rules must include an inline comment explaining why

### Naming Conventions

MNEMOSYS follows **PEP 8 naming conventions** without exception:

- **Variables, functions, methods**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private/internal**: Leading underscore (`_internal_name`)
- **Module-level dunder names**: `__all__`, `__version__`, etc.

**No custom conventions** - if you know PEP 8, you know MNEMOSYS naming.

### Type Hints

**Rule**: All public functions and methods must have complete type hints (enforced by mypy strict mode).

**Rationale**: Type hints are documentation, enable static analysis, and catch bugs at development time.

**Examples**:
```python
# ✅ Correct - full type hints
def create_instrument(name: str, string_count: int) -> Instrument:
    ...

# ❌ Wrong - missing type hints
def create_instrument(name, string_count):
    ...
```

---

## Database Conventions

### Table Naming Convention

**Rule**: Database table names are **singular**, not plural.

**Rationale**: A table name expresses what is represented by a single row, not a collection. A row in the `instrument` table represents one instrument, not multiple instruments.

**Examples**:
- ✅ `instrument` (not `instruments`)
- ✅ `exercise` (not `exercises`)
- ✅ `session` (not `sessions`)
- ✅ `session_block` (not `session_blocks`)
- ✅ `block_log` (not `block_logs`)
- ✅ `exercise_state` (already singular)

**Implementation**: Use `__tablename__` attribute in SQLAlchemy ORM models:
```python
class Instrument(Base):
    __tablename__ = "instrument"
    # ...
```

---

## To Be Organized

Additional standards and conventions will be collected here as the project evolves. This section serves as a staging area before formal organization.

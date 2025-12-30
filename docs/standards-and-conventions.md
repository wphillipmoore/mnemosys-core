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

MNEMOSYS follows **PEP 8 naming conventions** as a foundation:

- **Variables, functions, methods**: `snake_case`
- **Classes**: `PascalCase`
- **Constants**: `UPPER_SNAKE_CASE`
- **Private/internal**: Leading underscore (`_internal_name`)
- **Module-level dunder names**: `__all__`, `__version__`, etc.

#### Variable Naming Rules

These rules are based on Damian Conway's "Perl Best Practices" (2005), adapted for Python and proven effective over 20 years of use.

**1. Class-to-Variable Mapping**

Variables representing a class instance use the `snake_case` version of the class name:

```python
# ✅ Correct
instrument = Instrument(...)
exercise_state = ExerciseState(...)
session_block = SessionBlock(...)

# ❌ Wrong
inst = Instrument(...)
ex_state = ExerciseState(...)
block = SessionBlock(...)
```

**2. Minimum Length: 3+ Characters (Accessibility)**

One and two character variable names are **prohibited** - they make code difficult to read for people with dyslexia and reduce clarity for everyone.

```python
# ✅ Correct
for index in range(10):
    instrument = instruments[index]

for instrument_index, instrument in enumerate(instruments):
    process(instrument)

# ❌ Wrong
for i in range(10):
    x = xs[i]

for i, x in enumerate(xs):
    process(x)
```

**Exception**: Well-established mathematical variables in limited scope (`x`, `y` for coordinates in a 5-line algorithm).

**3. Complete English Words (Verbosity Over Brevity)**

Use complete English words, not abbreviations:

```python
# ✅ Correct
exception = ValueError(...)
configuration = load_config()
database_session = get_session()
instrument_index = 0

# ❌ Wrong
exc = ValueError(...)
config = load_config()  # Use configuration
db = get_session()      # Use db_session (see collision handling)
idx = 0                 # Use index or instrument_index
```

**4. Namespace Collision Handling**

When multiple classes have the same name (e.g., `Session` from SQLAlchemy and requests), disambiguate with descriptive prefixes:

```python
# ✅ Correct - import with prefix, use prefixed snake_case
from sqlalchemy.orm import Session as DBSession
from requests import Session as RESTSession

db_session = DBSession()
rest_session = RESTSession()

# ❌ Wrong
from sqlalchemy.orm import Session
db = Session()  # Too short, unclear
sess = Session()  # Abbreviated, unclear which Session
```

**Note**: Collision prefixes are chosen contextually (e.g., `DB`, `REST`) - there is no automatic rule.

**5. Boolean Variables**

Boolean variables should read like questions using these prefixes:

- `is_*`: State or condition - `is_valid`, `is_empty`, `is_active`
- `has_*`: Possession or presence - `has_permission`, `has_exercises`, `has_error`
- `can_*`: Capability or permission - `can_delete`, `can_write`, `can_edit`

```python
# ✅ Correct
is_valid = validate(instrument)
has_permission = check_access(user)
can_delete = user.is_admin or resource.owner == user

if is_valid and has_permission and can_delete:
    delete(resource)

# ❌ Wrong
valid = validate(instrument)      # Not a question
permission = check_access(user)   # Ambiguous
deletable = ...                   # Use can_delete
```

**6. Collections: Plural vs Singular (Conway's Usage Rule)**

Name collections based on **how they are primarily used**:

**Plural for collective processing:**
```python
# ✅ Correct - processed collectively
instruments = query.all()
for instrument in instruments:
    process(instrument)

exercise_ids = [ex.id for ex in exercises]
```

**Singular for individual access (lookup tables):**
```python
# ✅ Correct - accessed individually by key
instrument_by_id = {inst.id: inst for inst in query.all()}
instrument = instrument_by_id[42]

exercise_by_name = {...}
exercise = exercise_by_name["Chromatic Scale"]
```

**Singular for indexed access:**
```python
# ✅ Correct - random access by index
instrument_lookup = [...]  # Pre-built lookup array
instrument = instrument_lookup[index]
```

**7. Consistency Rules**

- **Syntactic consistency**: If one variable uses `adjective_noun`, all similar variables use `adjective_noun`
- **Semantic consistency**: Names convey what data represents, not just its type
- **Cross-codebase consistency**: Same concept = same name everywhere

```python
# ✅ Correct - consistent naming across functions
def create_instrument(name: str) -> Instrument:
    instrument = Instrument(name=name)
    db_session.add(instrument)
    return instrument

def update_instrument(instrument: Instrument, name: str) -> Instrument:
    instrument.name = name
    db_session.commit()
    return instrument

# ❌ Wrong - inconsistent names for same concept
def create_instrument(name: str) -> Instrument:
    inst = Instrument(name=name)  # Called 'inst' here
    db_session.add(inst)
    return inst

def update_instrument(instrument: Instrument, name: str) -> Instrument:  # Called 'instrument' here
    instrument.name = name
    db_session.commit()
    return instrument
```

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

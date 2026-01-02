# MNEMOSYS Standards and Conventions

This document captures coding standards, naming conventions, and architectural patterns for the MNEMOSYS project. These conventions ensure consistency, maintainability, and alignment with the project's core principles.

---

## Project Terminology

### Official Project Name

**MNEMOSYS** (pronounced "NEE-moss")

This is the canonical name for the project and must be used consistently across all:
- Code (comments, docstrings, API descriptions)
- Documentation (design docs, user guides, README files)
- Repository metadata (package names, project descriptions)
- External communications

### Deprecated Names

The following names are **deprecated** and should not be used in new code or documentation:

- **FSIPS** (Functional Skill Integration & Practice System) - Original working name, replaced by MNEMOSYS
- **RPM** (Recall, Practice, Maintenance) - Originally conceived as a separate extension, now integrated as core MNEMOSYS functionality

### Name Rationale

From the Greek root **μνήμη (mnēmē)** meaning "memory, remembrance."

The name reflects the system's core thesis: **skills are memory structures with half-lives** that require deliberate recall to survive. MNEMOSYS optimizes for long-term retention and memory survival, not short-term acquisition.

See `docs/project/final/Philosophy.md` for complete philosophical foundation.

### Usage in Historical Documents

Early design documents (v0.1 snapshots) may reference deprecated names in their original context. When updating these documents, add a nomenclature note explaining the name evolution while preserving the historical snapshot.

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

### Import-Time Side Effects

**Core Rule**: No implicit state or side effects at import time.

**Explicit Exceptions (Framework-Standard Mechanisms Only):**
- **SQLAlchemy ORM model declarations** (including `Table` definitions and declarative class registration in `Base.metadata`)
- **FastAPI router definitions** (`APIRouter()` creation and decorator-based route registration)

These are allowed **only** because the frameworks require import-time registration. Everything else remains forbidden at import time (engine/session creation, settings loading, network calls, file system writes, or global mutable state).

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

**Exceptions**:
- Well-established mathematical variables in limited scope (`x`, `y` for coordinates in a 5-line algorithm).
- Common domain abbreviations and acronyms **already used in this codebase** are permitted: `id`, `db`, `api`, `env`, `app`. Use these only as clear, explicit tokens (e.g., `instrument_id`, `db_session`, `api_router`, `env_name`, `app_state`), not as single-character loop variables.
- Enum member names may use short domain codes (e.g., `F0`) when those codes are established labels; prefer full words otherwise.

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

**Exception**: The allowed domain abbreviations and acronyms above (`id`, `db`, `api`) may appear as tokens in identifiers. Other acronyms are acceptable only when they are the official name of a domain concept (e.g., `UTC`), and should not be shortened further.

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

### Unit Testing Policy

**Core Principle**: Code coverage should be maintained **as close to 100% as reasonably possible**.

**Default Assumption**: All code is tested unless explicitly documented otherwise.

#### Coverage Target

- **Goal**: 100% code coverage (lines AND branches) across all production code
- **Tool**: pytest with pytest-cov plugin
- **Measurement**: Run `pytest --cov=src --cov-report=html --cov-report=term --cov-branch`
- **CI/CD**: Coverage checks run automatically in test suite
- **Branch Coverage**: Tests all code paths (if/else, try/except, boolean operators, loops, etc.), not just that lines were executed

#### Untestable Code Documentation

When code genuinely cannot be tested (rare but valid cases exist), it **must be clearly documented in the code** so gaps are visible during code review and maintenance.

**Marking untestable code:**

```python
# ✅ Correct - clearly documented untestable code
def handle_database_connection(config: dict) -> Connection:
    """
    Establish database connection with retry logic.

    Note: The connection timeout branch cannot be reliably tested in unit
    tests due to non-deterministic timing behavior. Integration tests
    cover this scenario.
    """
    try:
        return connect(config)
    except TimeoutError:  # pragma: no cover - timing-dependent, covered in integration tests
        logger.warning("Connection timeout, retrying...")
        time.sleep(1)
        return connect(config)

# ❌ Wrong - untested code without documentation
def handle_database_connection(config: dict) -> Connection:
    try:
        return connect(config)
    except TimeoutError:  # No explanation why this isn't tested
        logger.warning("Connection timeout, retrying...")
        time.sleep(1)
        return connect(config)
```

**Valid reasons for untestable code** (document which applies):
- Platform-specific behavior that can't be simulated in test environment
- Timing-dependent race conditions (covered by integration/system tests)
- External service failures that can't be reliably mocked
- Hardware-dependent operations
- Defensive code for "impossible" states (still document why it's impossible)

**Documentation format:**
```python
# pragma: no cover - <brief reason>, <where it IS tested if applicable>
```

**IMPORTANT**: Do not include specific line numbers in docstrings or comments explaining coverage exceptions. Line numbers become stale as code evolves, and developers rarely remember to update them. Instead, describe the code path or branch conceptually (e.g., "the connection timeout branch" rather than "lines 45-48").

#### Coverage Reporting

**Check coverage:**
```bash
# Terminal report with missing lines and branch coverage
pytest --cov=src --cov-report=term-missing --cov-branch

# HTML report (opens in browser) with branch coverage
pytest --cov=src --cov-report=html --cov-branch
open htmlcov/index.html
```

**Coverage expectations:**
- **New code**: Must maintain or improve overall coverage percentage for BOTH lines and branches
- **Pull requests**: Coverage report must be reviewed
- **Declining coverage**: Requires explicit justification and documentation
- **Branch coverage**: Pay special attention to missing branch coverage - it indicates untested code paths

#### Rationale

100% code coverage ensures:
1. **Confidence**: Every code path is exercised and verified
2. **Refactoring safety**: Changes are caught by comprehensive test suite
3. **Documentation**: Tests serve as usage examples
4. **Bug prevention**: Edge cases are explicitly tested
5. **Maintenance**: Clear documentation of any untested gaps

**Note**: 100% coverage is a *necessary* but not *sufficient* condition for quality - tests must also be meaningful and assert correct behavior.

---

## Development Workflow

### Pull Request Submission Process

**Core Principle**: Pull requests must pass **all** automated checks before submission. No exceptions.

**Rationale**: The CI/CD pipeline is a backstop, not a substitute for developer diligence. Submitting failing PRs wastes reviewer time, pollutes the PR history, and undermines confidence in the codebase.

#### Pre-Submission Requirements

Before creating a pull request, **ALL** of the following requirements must be met:

1. **100% unit test success** - ALL tests must pass
2. **100% code coverage** - Coverage of both lines AND branches must not decrease, aspire to 100%
3. **All code quality checks must pass** - ruff and mypy must report no errors

#### Pre-Submission Checklist

Before creating a pull request, **ALL** of the following must pass:

**Shortcut (recommended):**
```bash
# Run all CI hard gates locally
python scripts/dev/validate_local.py
```

**1. Full Test Suite (REQUIRED: 100% Success)**
```bash
# Run complete test suite (not just a subset)
poetry run pytest

# REQUIRED: "=== X passed in Y.YYs ==="
# FORBIDDEN: "=== X passed, Y failed in Z.ZZs ==="
# FORBIDDEN: "=== X passed, Y skipped in Z.ZZs ===" (fix skipped tests)
```

**Critical**:
- Running only a subset (e.g., `pytest tests/db/`) is **not sufficient**. Changes to one area often break tests in another area (as demonstrated by the Session → Practice rename breaking API tests).
- **ALL tests must pass**. Zero failures, zero skips (unless explicitly documented).

**2. Code Quality Checks (REQUIRED: Zero Errors)**
```bash
# Linting
poetry run ruff check

# Type checking
poetry run mypy

# REQUIRED: Both must report "No errors" or "Success: no issues found"
```

**3. Code Coverage (REQUIRED: 100% Line AND Branch Coverage Goal)**
```bash
# Verify line AND branch coverage is at 100% or document exceptions
poetry run pytest --cov=src --cov-report=term-missing --cov-branch

# REQUIRED: Both line AND branch coverage must not decrease from current levels
# GOAL: Maintain or improve toward 100% coverage of lines AND branches
# Any untestable code must be documented with `# pragma: no cover` and explanation
```

**Coverage Requirements:**
- New code must maintain or improve overall coverage percentage for BOTH lines and branches
- Any decrease in line or branch coverage requires explicit justification in the PR description
- Untestable code must be marked with `# pragma: no cover` and documented (see Unit Testing Policy above)
- **Critical**: Branch coverage tests all code paths (if/else, try/except, loops, etc.), not just that lines were executed

#### What to Do When Checks Fail

**If ANY check fails:**

1. ❌ **DO NOT create the PR**
2. ✅ Fix the failing tests/checks
3. ✅ Re-run the full checklist
4. ✅ Only proceed when everything passes

**Common mistakes to avoid:**

- ❌ "I only changed DB code, so I only ran DB tests"
  - **Reality**: Your changes may break API tests, integration tests, etc.

- ❌ "The test failures are pre-existing, not from my changes"
  - **Reality**: Fix them anyway, or create a separate issue to track them

- ❌ "I'll fix it in a follow-up PR"
  - **Reality**: Fix it now, before creating the PR

#### Commit Message Format

Follow conventional commits format:

```
<type>: <short description>

<optional detailed description>

<footer with co-authorship and generation info>
```

**Types**: `feat`, `fix`, `docs`, `style`, `refactor`, `test`, `chore`

**Example**:
```
fix: update API routers for Practice terminology

Updated all API routers and schemas to use Practice, PracticeBlock,
and PracticeBlockLog instead of Session, SessionBlock, BlockLog.

Fixed import order bug in test fixtures where models weren't imported
before Base.metadata.create_all(), causing "no such table" errors.

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: mnemosys-claude <252602472+mnemosys-claude@users.noreply.github.com>
```

#### Commit Authorship and AI Co-Authorship

**Core Rule**: All commits must be authored by a human. The human owns responsibility and accountability for the change.

**Required AI Co-Authorship (When AI Contributed)**:
- If an AI tool materially contributed to the change, include a co-author trailer for that tool.
- If no AI tool contributed, omit AI co-authors.

**Requirements**:
- The commit **author** must be the human operator (your account).
- Do **not** set AI tooling as the author or committer.
- Use these exact AI co-author identities (no vendor noreply emails):
  - `mnemosys-codex <252598091+mnemosys-codex@users.noreply.github.com>`
  - `mnemosys-claude <252602472+mnemosys-claude@users.noreply.github.com>`
- If multiple tools contributed, include multiple co-author trailers.

**Rationale**: AI is a tool. The human drives decisions, validates outcomes, and remains accountable for the code, while the AI contributors are explicitly visible in GitHub history.

#### CI/CD Integration (Future)

**Status**: Not yet implemented

**Planned enforcement**:
- GitHub Actions will run full test suite on every PR
- PRs cannot merge unless all checks pass
- Coverage reports will be posted to PR comments
- Ruff and mypy errors will block merge

**Until CI/CD is implemented**: Developer discipline is the **only** enforcement mechanism.

### Pull Request Finalization Process

**Core Principle**: PRs must be properly finalized after merging to maintain a clean repository state and ensure the main branch remains validated.

**Critical Rule**: **NEVER reuse old branch names**. Always create fresh branches for new work, even if a previous branch with a similar name was already merged and deleted.

#### The Four-Step Finalization Process

After your PR is approved and ready to merge, follow these steps **in order**:

**Step 1: Merge the PR**
```bash
# Merge using squash merge and auto-delete the remote branch
gh pr merge <PR_NUMBER> --squash --delete-branch

# Example:
gh pr merge 14 --squash --delete-branch
```

**Why squash merge?**
- Creates a single, clean commit on the target branch
- Preserves detailed commit history in the PR for reference
- Keeps main branch history readable

**Step 2: Update Local Copy of Target Branch**
```bash
# Switch to the target branch (usually develop)
git checkout develop

# Verify you're up to date
git status

# Expected output: "Your branch is up to date with 'origin/develop'"
```

**Step 3: Verify Virtual Environment is Clean**
```bash
# CRITICAL: Sync .venv with dependency specification
# This prevents test failures from stale or conflicting dependencies
poetry sync

# Expected output: "Installing dependencies from lock file"
# If dependencies are already synced: "No dependencies to install or update"
```

**Why verify .venv?**
- Prevents test failures from stale dependencies
- Catches dependency changes that weren't properly synchronized
- Ensures clean state before validation (tests can "implode" with unhealthy .venv)
- Sanity check that dependency specifications are internally consistent

**Step 4: Clean Up and Run FINAL Validation**
```bash
# Delete local feature branch (if not already deleted)
git branch -d <branch-name>

# Clean up stale remote branch references
git remote prune origin

# Run FINAL validation on target branch
poetry run pytest --cov=mnemosys_core --cov-report=term-missing --cov-branch
poetry run ruff check
poetry run mypy src/

# ALL checks must pass:
# ✅ 100% tests passing
# ✅ 100% line and branch coverage maintained
# ✅ Ruff: All checks passed
# ✅ Mypy: Success, no issues found
```

**Why prune remote references?**
- Removes stale tracking references to deleted remote branches
- Prevents confusion when listing branches (e.g., `git branch -a`)
- Keeps local repository metadata clean and accurate

**Why final validation?**
- Confirms merge was successful
- Verifies no integration issues
- Ensures develop branch is in perfect state
- Catches any problems before starting next feature

#### Complete Workflow: Start to Finish

**Proper workflow for a feature:**

```bash
# 1. Start from clean develop
git checkout develop
git pull origin develop

# 2. Create NEW branch with descriptive name
git checkout -b feat/add-user-authentication

# 3. Do your work, make commits
# ... work, work, work ...
git add .
git commit -m "feat: implement user authentication"

# 4. Push branch
git push -u origin feat/add-user-authentication

# 5. Create PR
gh pr create --title "Add user authentication" --body "..." --base develop

# 6. After approval, merge and finalize (four-step process above)
gh pr merge <PR#> --squash --delete-branch
git checkout develop
# Verify .venv is clean
poetry sync
# Clean up stale remote references
git remote prune origin
# Run final validation
poetry run pytest --cov=mnemosys_core --cov-report=term-missing --cov-branch
poetry run ruff check && poetry run mypy src/

# 7. Start next feature from clean develop (back to step 1)
git checkout develop
git pull origin develop
git checkout -b feat/add-password-reset
```

#### Branch Naming Anti-Patterns

**❌ WRONG - Reusing old branch names:**
```bash
# PR #12 merged from branch "fix/api-issues"
# Later, trying to fix more API issues:
git checkout -b fix/api-issues  # ❌ BAD! Reusing old name

# Problems:
# - Confusing: Is this the old branch or new work?
# - Git history pollution
# - Potential conflicts with stale remote branches
```

**✅ CORRECT - Always use fresh, descriptive names:**
```bash
# PR #12 merged from branch "fix/api-issues"
# Later, fixing more API issues:
git checkout -b fix/api-schema-validation  # ✅ GOOD! New specific name
git checkout -b fix/api-error-handling     # ✅ GOOD! Describes the work
```

#### Common Mistakes

**Mistake 1: Skipping .venv verification and final validation**
```bash
# ❌ WRONG
gh pr merge 14 --squash --delete-branch
git checkout develop
# ... immediately start new work without verifying .venv or validating

# ✅ CORRECT
gh pr merge 14 --squash --delete-branch
git checkout develop
# Verify .venv is clean first!
poetry sync
# Then run full validation!
poetry run pytest --cov=mnemosys_core --cov-report=term-missing --cov-branch
poetry run ruff check && poetry run mypy src/
# NOW start new work
```

**Mistake 2: Reusing branch names**
```bash
# ❌ WRONG
git checkout -b fix/test-failures  # Used this name before

# ✅ CORRECT
git checkout -b fix/test-timeout-in-api-layer  # Fresh, descriptive name
```

**Mistake 3: Not switching to develop before starting new work**
```bash
# ❌ WRONG
# Still on feature branch after PR merge
git checkout -b feat/new-feature  # Branching from wrong base!

# ✅ CORRECT
git checkout develop
git pull origin develop
git checkout -b feat/new-feature  # Branching from clean develop
```

#### Rationale

**Why this process matters:**
1. **Clean history**: Ensures repository state is always known-good
2. **Clean environment**: .venv verification prevents dependency-related test failures
3. **Catch integration issues**: Final validation catches problems before they compound
4. **Prevent confusion**: Fresh branch names make it clear what work is happening
5. **Enable collaboration**: Team members always know develop branch works
6. **Reduce debugging time**: Problems caught immediately, not days later

**The 45-second investment in .venv verification and final validation saves hours of debugging later.**

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

### Model File Organization

**Context**: As the MNEMOSYS data model scales (projected 10-20x growth from current state), maintaining comprehensible file organization is critical. These rules balance "easy to find" (one table = one file) with "easy to understand" (related tables stay together).

**Core Principle**: File organization follows a multi-dimensional namespace (lifecycle coupling, conceptual domains, hierarchy) mapped onto a single-dimensional filesystem. Perfect consistency is impossible - these rules minimize judgment calls while acknowledging exceptions.

#### Rules

**[Rule 1] One File Per Database Table (Default)**

Each database table gets its own Python file named after the table:

```python
# ✅ Correct
models/practice.py              # Practice table
models/exercise_instance.py     # ExerciseInstance table
models/technique.py             # Technique table
```

**[Rule 2] Tightly Coupled 1:1 Tables May Bundle With Parent**

When a table has a 1:1 relationship (enforced by unique foreign key) with a parent and they're always used together, they may be bundled:

```python
# ✅ Correct - ExerciseLog is 1:1 with ExerciseInstance
# models/exercise_instance.py
class ExerciseInstance(Base):
    __tablename__ = "exercise_instance"
    # ...

class ExerciseLog(Base):
    __tablename__ = "exercise_log"
    exercise_instance_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("exercise_instance.id"), unique=True  # 1:1 enforced
    )
```

**[Rule 3] Association Tables Use Alphanumeric Ordering**

Many-to-many association tables are named alphanumerically and placed in the alphabetically-first entity's file:

```python
# ✅ Correct - "exercise" comes before "technique" alphabetically
# models/exercise.py
class ExerciseTechniqueAssociation(Base):
    __tablename__ = "exercise_technique_association"  # Not technique_exercise
    # ...

# ❌ Wrong
# models/technique.py
class TechniqueExerciseAssociation(Base):  # Wrong order and wrong file
    __tablename__ = "technique_exercise_association"
```

**Rationale**: Eliminates arbitrary judgment calls about which entity is "more significant" - alphabetical ordering is objective and discoverable.

**[Rule 4] Gray Areas Require Explicit Discussion**

Any case not obviously covered by Rules 1-3 should be discussed and decided explicitly. Document the decision in code comments if non-obvious.

Examples of gray areas:
- Polymorphic inheritance (separate tables via joined-table inheritance)
- 1:many relationships that are conceptually tightly coupled
- Legacy tables being deprecated together

#### Current Decisions

These are judgment calls made for the current codebase. They may evolve as the model scales.

**Polymorphic Inheritance (Joined-Table Inheritance)**

Subclass tables created by SQLAlchemy's joined-table inheritance are bundled with the parent:

```python
# models/instrument.py
class Instrument(Base):
    __tablename__ = "instrument"
    # ...

class StringedInstrument(Instrument):
    __tablename__ = "stringed_instrument"  # Separate table, same file
    # ...

class KeyboardInstrument(Instrument):
    __tablename__ = "keyboard_instrument"  # Separate table, same file
    # ...
```

**Rationale**: Inheritance hierarchies are read together. If individual subclass files grow large (>500 lines), revisit this decision.

**Tightly Coupled Legacy Pairs**

Tables that will likely be deprecated together may be bundled even if 1:many:

```python
# models/practice_block.py
class PracticeBlock(Base):
    __tablename__ = "practice_block"
    # ...

class PracticeBlockLog(Base):
    __tablename__ = "practice_block_log"  # 1:many, but bundled
    # ...
```

**Rationale**: These are tightly coupled conceptually. Bundling makes their relationship obvious and future removal easier.

#### Revisiting These Rules

**When to revisit:**
- Individual files exceed ~500 lines (split per Rule 1)
- Constantly jumping between files that should be together (bundle per Rule 2)
- Outsider feedback indicates confusion (test: comprehensibility to non-authors)

**Test for success**: Can someone unfamiliar with the codebase find what they're looking for without deep system knowledge?

---

## To Be Organized

Additional standards and conventions will be collected here as the project evolves. This section serves as a staging area before formal organization.

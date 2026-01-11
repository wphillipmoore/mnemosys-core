# MNEMOSYS Standards and Conventions

This repository follows the canonical standards in the Standards and
Conventions repository:
https://github.com/wphillipmoore/standards-and-conventions

This file records MNEMOSYS-specific terminology and any local deviations.

## Table of Contents
- [Canonical standards](#canonical-standards)
- [Project terminology](#project-terminology)
  - [Official project name](#official-project-name)
  - [Deprecated names](#deprecated-names)
  - [Name rationale](#name-rationale)
  - [Usage in historical documents](#usage-in-historical-documents)
- [Local deviations](#local-deviations)

## Canonical standards

Start with these sources of truth:

- Code management overview: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/code-management/overview.md
- Pull request workflow: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/code-management/pull-request-workflow.md
- Commit messages and authorship: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/code-management/commit-messages-and-authorship.md
- Branching and deployment: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/code-management/branching-and-deployment.md
- Release versioning: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/code-management/release-versioning.md
- Hotfix policy: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/code-management/hotfix-policy.md
- Development overview: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/development/overview.md
- Environment and tooling: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/development/environment-and-tooling.md
- Python standards overview: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/development/python/overview.md
- Python naming conventions: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/development/python/naming-conventions.md
- Python import-time side effects: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/development/python/import-time-side-effects.md
- Python type hints: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/development/python/type-hints.md
- Python testing and coverage: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/development/python/testing-and-coverage.md
- Database conventions: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/development/database/conventions.md
- Repository standards overview: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/repository/overview.md
- Markdown standards: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/foundation/markdown-standards.md
- Architecture standards: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/foundation/architecture-standards.md
- AI code review guidelines: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/foundation/ai-code-review-guidelines.md
- AI-assisted development loop: https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/foundation/ai-assisted-development-loop.md

## Project terminology

### Official project name

**MNEMOSYS** (pronounced "NEE-moss")

This is the canonical name for the project and must be used consistently across
all:
- Code (comments, docstrings, API descriptions)
- Documentation (design docs, user guides, README files)
- Repository metadata (package names, project descriptions)
- External communications

### Deprecated names

The following names are deprecated and should not be used in new code or
documentation:

- **FSIPS** (Functional Skill Integration & Practice System) - original working
  name, replaced by MNEMOSYS
- **RPM** (Recall, Practice, Maintenance) - originally conceived as a separate
  extension, now integrated as core MNEMOSYS functionality

### Name rationale

From the Greek root "mneme" meaning "memory, remembrance."

The name reflects the system's core thesis: skills are memory structures with
half-lives that require deliberate recall to survive. MNEMOSYS optimizes for
long-term retention and memory survival, not short-term acquisition.

See `docs/project/final/Philosophy.md` for the complete philosophical
foundation.

### Usage in historical documents

Early design documents (v0.1 snapshots) may reference deprecated names in their
original context. When updating these documents, add a nomenclature note
explaining the name evolution while preserving the historical snapshot.

## Local deviations

None. Add project-specific overrides here if this repository diverges from the
canonical standards.

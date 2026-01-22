# MNEMOSYS Standards and Conventions

This repository follows the canonical standards in the Standards and
Conventions repository:
https://github.com/wphillipmoore/standards-and-conventions/tree/develop

This file records MNEMOSYS-specific terminology and any canonical standards
incubated here before extraction to the Standards and Conventions repository.
The Standards and Conventions repository remains the canonical source of truth,
but MNEMOSYS Core is used to develop new standards that are finalized and
merged upstream once stable. Differences between this repository and the
Standards and Conventions repository should be treated as in-progress standards
unless explicitly documented here as conventions.

## Table of Contents
- [Canonical references](#canonical-references)
  - [Access requirements](#access-requirements)
  - [Core references (always required)](#core-references-always-required)
  - [Repository-type references (required for the declared type)](#repository-type-references-required-for-the-declared-type)
  - [Additional required references](#additional-required-references)
- [Project terminology](#project-terminology)
  - [Official project name](#official-project-name)
  - [Deprecated names](#deprecated-names)
  - [Name rationale](#name-rationale)
  - [Usage in historical documents](#usage-in-historical-documents)
  - [CI gates](#ci-gates)
- [Project-specific overlay](#project-specific-overlay)
  - [Repository profile](#repository-profile)
  - [Local development preflight](#local-development-preflight)
  - [AI co-author identities](#ai-co-author-identities)

## Canonical references

### Access requirements

When reading canonical standards, use the raw GitHub content endpoint for
deterministic access:
`https://raw.githubusercontent.com/wphillipmoore/standards-and-conventions/develop/<path>`

If the canonical docs cannot be retrieved (network failure, access failure, or
missing file), treat it as a fatal exception: stop and notify the user. Do not
proceed with assumptions or alternate sources.

### Core references (always required)
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/foundation/markdown-standards.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/code-management/repository-types-and-attributes.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/code-management/commit-messages-and-authorship.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/code-management/github-issues.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/code-management/pull-request-workflow.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/code-management/source-control-guidelines.md

### Repository-type references (required for the declared type)
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/code-management/branching-and-deployment.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/code-management/application-versioning-scheme.md

### Additional required references
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/code-management/overview.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/code-management/release-versioning.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/code-management/hotfix-policy.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/development/overview.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/development/environment-and-tooling.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/development/python/overview.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/dependencies/dependency-update-workflow.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/development/python/naming-conventions.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/development/python/import-time-side-effects.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/development/python/type-hints.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/development/python/testing-and-coverage.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/development/database/conventions.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/repository/overview.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/foundation/architecture-standards.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/foundation/ai-code-review-guidelines.md
- https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/foundation/ai-assisted-development-loop.md

## Project terminology

### Official project name

**MNEMOSYS** (pronounced /ˈniːməˌsɪs/, or "NEE-muh-sis")

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

### CI gates

CI gate definitions follow the canonical standards.

Hard gates (all are required status checks):
- `test-and-validate (3.14)`
- `integration-tests`
- `dependency-audit`

Soft gates:
- None.

Branch applicability:
- develop: all hard gates required
- release: all hard gates required
- main: all hard gates required

## Project-specific overlay

These entries supply project-specific values required by the canonical
standards.

### Repository profile

- repository_type: application
- versioning_scheme: application
- branching_model: application-promotion
- release_model: environment-promotion
- supported_release_lines: single

### Local development preflight

Before starting any new development effort, run the unit tests and confirm they
pass. This guards against inheriting broken local artifacts from prior work.

All Python commands must run inside the project venv (use `uv run ...` or the
`.venv/bin/python3` interpreter). Do not rely on a system `python` binary; use
`python3` for all Python invocations.

Use one of:
- `pytest tests/`
- `python3 scripts/dev/validate_local.py`
- Docs-only changes: `python3 scripts/dev/validate_docs.py`

Docs-only validation requires `markdownlint` `0.41.0` on the PATH. If it is not
available, `npx` must be installed so the validation script can run the pinned
version.

Tooling requirement:
- `uv` `0.9.26` (install with `python3 -m pip install uv==0.9.26`).

### AI co-author identities

Approved AI co-author trailers for this repository:

```
Co-Authored-By: mnemosys-codex <252598091+mnemosys-codex@users.noreply.github.com>
Co-Authored-By: mnemosys-claude <252602472+mnemosys-claude@users.noreply.github.com>
```

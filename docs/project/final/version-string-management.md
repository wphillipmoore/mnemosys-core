# Version string management

This document is maintained in the Standards and Conventions repository:
https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/code-management/application-versioning-scheme.md

## Table of Contents
- [Source of truth](#source-of-truth)
- [Local deviations](#local-deviations)

## Source of truth

The canonical versioning scheme lives at:
https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/code-management/application-versioning-scheme.md

If the canonical document cannot be retrieved, treat it as a fatal exception
and notify the user.

## Local deviations

- The canonical version string for MNEMOSYS Core lives in `pyproject.toml` under
  `project.version`.
- Use the local helper scripts when available:
  - `python scripts/dev/submit_develop_pr.py`
  - `python scripts/dev/submit_release_prs.py`
  - `python scripts/dev/submit_main_pr.py`

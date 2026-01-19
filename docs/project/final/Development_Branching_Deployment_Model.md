# Development Branching and Deployment Model

This document is maintained in the Standards and Conventions repository:
https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/code-management/branching-and-deployment.md

## Table of Contents
- [Source of truth](#source-of-truth)
- [Local deviations](#local-deviations)

## Source of truth

The canonical version lives at:
https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/code-management/branching-and-deployment.md
If the canonical document cannot be retrieved, treat it as a fatal exception
and notify the user.

## Local deviations

- Short-lived branch prefixes allow `promotion/` in addition to
  `feature/`, `bugfix/`, and `hotfix/`.
- Promotion branches for environment promotions use the `promotion/` prefix
  with these names: `promotion/release-<version>-<yyyymmddhhmmss>` for
  develop->release and `promotion/main-<version>-<yyyymmddhhmmss>` for
  release->main.

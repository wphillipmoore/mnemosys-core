# Source Code Management Guidelines

This document is maintained in the Standards and Conventions repository:
https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/code-management/source-control-guidelines.md

## Table of Contents
- [Source of truth](#source-of-truth)
- [Local deviations](#local-deviations)

## Source of truth

The canonical version lives at:
https://github.com/wphillipmoore/standards-and-conventions/blob/main/docs/code-management/source-control-guidelines.md

## Local deviations

- Pull requests that resolve a tracked issue must include a closing keyword in
  the PR description (for example, `Fixes #123`) so the issue auto-closes on
  merge. If auto-close is not possible, the PR must still reference the issue
  and the issue must be closed manually after merge. Work is not complete until
  the issue is closed.

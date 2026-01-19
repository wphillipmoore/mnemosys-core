# Dependency Update Workflow

This document is maintained in the Standards and Conventions repository:
https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/development/dependency-update-workflow.md

## Table of Contents
- [Source of truth](#source-of-truth)
- [Local deviations](#local-deviations)

## Source of truth

The canonical version lives at:
https://github.com/wphillipmoore/standards-and-conventions/blob/develop/docs/development/dependency-update-workflow.md

If the canonical document cannot be retrieved, treat it as a fatal exception
and notify the user.

## Local deviations

- Review Dependabot alerts during `MAJOR` and `MINOR` releases and incorporate
  remediation into the dependency update process.
- If an attempted upgrade fails, create a GitHub issue describing the failure,
  pin the dependency to the last known good version, and add a pin comment that
  references the issue.

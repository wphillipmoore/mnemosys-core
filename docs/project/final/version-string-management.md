# Version string management

Define how MNEMOSYS Core assigns and maintains version strings for all deployed
artifacts and environments.

## Table of Contents
- [Purpose](#purpose)
- [Invariants](#invariants)
- [Version format](#version-format)
- [Source of truth](#source-of-truth)
- [Increment rules](#increment-rules)
- [Pull request preparation tool](#pull-request-preparation-tool)
- [Develop merge workflow](#develop-merge-workflow)
- [Release workflow](#release-workflow)
- [Main promotion workflow](#main-promotion-workflow)
- [Validation and failure modes](#validation-and-failure-modes)

## Purpose
Ensure every deployed artifact has a unique, human-readable version identifier
that is stable, auditable, and compatible with release governance.

## Invariants
- Every deployed artifact in any environment maps to a unique version string.
- The rightmost component (`BUILD`) auto-increments on every merge to `develop`.
- `PATCH` increments when a `develop` to `release` PR is opened.
- Major and minor changes are explicit human decisions.
- Version numbers are never reused or mutated after deployment.
- The format is simple, explicit, and does not rely on implicit state.

## Version format
Use a four-part numeric version string:

```
MAJOR.MINOR.PATCH.BUILD
```

Rules:
- Each component is a non-negative integer with no leading zeros (except `0`).
- `BUILD` is the rightmost component and is auto-incremented.
- No suffixes or build metadata are used in this repository version string.

## Source of truth
- The canonical version string lives in `pyproject.toml` under
  `project.version`.
- All other references must derive from this value; do not duplicate the string
  in code.
- Runtime reads should use package metadata (for example,
  `importlib.metadata.version("mnemosys-core")`) rather than hard-coded values.

## Increment rules
- `BUILD` increments by exactly 1 on every merge to `develop`.
- `PATCH` increments by exactly 1 when a `develop` to `release` PR is opened and
  resets `BUILD` to `0`.
- `MAJOR` and `MINOR` are updated manually and reset `PATCH` and `BUILD` to `0`.
- Version changes must be part of the merge PR; direct commits to `develop` are
  forbidden.
- If `develop` advances before merge, rebase and reapply the next `BUILD` value
  to avoid collisions.

## Pull request preparation tool
Use the canonical script to prepare feature PRs into `develop`:

```
python scripts/dev/submit_develop_pr.py
```

The script:
- Verifies a clean working tree and a non-eternal feature branch.
- Ensures the branch is based on current `develop`.
- Bumps `BUILD` to `develop` + 1, commits the bump, and runs validation.
- Pushes the branch and opens the pull request via `gh`.
- Applies the docs-only exception only when the changes are documentation plus
  the version bump in `pyproject.toml`.

If the script is unavailable, replicate its checks manually and ensure the
version bump matches the current `develop` build.

## Develop merge workflow
1. Determine the current `develop` version from `pyproject.toml`.
2. Increment `BUILD` by 1 in the PR branch (use
   `python scripts/dev/submit_develop_pr.py`).
3. Ensure the version bump is included in the merge PR to `develop`.
4. If `develop` advances before merge, rebase and bump `BUILD` again.

This policy requires automation or discipline to avoid skipped or duplicate
build numbers; the CI gate must enforce the rule.
The PR author (human or AI) owns the bump; CI must reject missing increments.

## Release workflow
1. Create a promotion branch from `develop` and open a PR from that branch to
   `release`.
2. If `release` has diverged, merge `release` into the promotion branch and
   resolve conflicts in the promotion branch before PR merge.
3. For `MAJOR` or `MINOR` releases, review Dependabot alerts and address them
   as part of the dependency update process before the release PR is merged.
4. Immediately open a separate PR to `develop` that increments `PATCH` by 1 and
   resets `BUILD` to `0`.
5. Merge the promotion PR after validation using a merge commit (no squash).
6. Merge the `PATCH` bump PR to `develop` before the next feature merge.

Promotion branch naming:
- `promotion/release-<version>-<yyyymmddhhmmss>`

If automation exists (for example, a `submit_release_prs` script), it must
open the two PRs above without direct commits to `develop`.
Release coordination is a developer responsibility and is enforced by CI
gates or release checklists.

Canonical command:

```
python scripts/dev/submit_release_prs.py
```

## Main promotion workflow
1. Create a promotion branch from `release` and open a PR from that branch to
   `main` after validation in `release`.
2. If `main` has diverged, merge `main` into the promotion branch and resolve
   conflicts in the promotion branch before PR merge.
3. Merge the promotion PR using a merge commit (no squash).
4. The PR contains no version changes; it promotes the already-versioned
   release.

Promotion branch naming:
- `promotion/main-<version>-<yyyymmddhhmmss>`

Canonical command:

```
python scripts/dev/submit_main_pr.py
```

## Validation and failure modes
CI must fail when:
- The version string does not match `MAJOR.MINOR.PATCH.BUILD`.
- `BUILD` is not exactly one higher than the current `develop` value for merge
  PRs to `develop`.
- `PATCH` bump PRs do not reset `BUILD` to `0`.
- A version number is reused or regresses.

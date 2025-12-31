# MNEMOSYS Development — Branching & Deployment Model v0.1

## Status
Frozen v0.1 snapshot

---

## 1. Purpose

This document defines the **branching model and deployment semantics** for MNEMOSYS repositories.

The goal is to provide:
- Clear, boring, survivable workflows
- Deterministic promotion across environments
- Minimal cognitive overhead for future contributors
- Explicit handling of failure modes

This model prioritizes **clarity and durability** over cleverness.

---

## 2. Core Invariants

1. Each long-lived branch maps to exactly one deployment environment  
2. Promotion is monotonic: development → test → production  
3. Humans decide merges; automation performs deployments  
4. Branch names encode intent, not activity  
5. The system must survive without its original author  

---

## 3. Deployment Environments

There are exactly three environments:

- **development**
- **test**
- **production**

Each environment consists of:
- one database
- one API
- one running application version

Parallel stacks, canaries, or shadow environments are explicitly out of scope at v0.1.

---

## 4. Eternal Branches

The following branches always exist and are protected:

- `develop`
- `release`
- `main`

| Branch   | Purpose                        | Deployment Target |
|---------|--------------------------------|-------------------|
| develop | Integration and rapid iteration| development       |
| release | Qualification and validation   | test              |
| main    | Production truth               | production        |

### Pull Request Requirement

**ALL eternal branches require pull requests for changes.** Direct pushes to `develop`, `release`, or `main` are forbidden.

- Changes to `develop`: Create a `feature/*` or `bugfix/*` branch, then open a PR to `develop`
- Changes to `release`: Create a PR from `develop` to `release`
- Changes to `main`: Create a PR from `release` to `main`
- Exception: `hotfix/*` branches follow special forward-merge rules (see Section 5)

Each merge into these branches triggers **automatic deployment** to the corresponding environment.

---

## 5. Short-Lived Branches

All work occurs in short-lived branches.

### Branch Naming Conventions

Only the following branch prefixes are allowed:
- `feature/*`
- `bugfix/*`
- `hotfix/*`

**No other prefixes** (e.g., `fix/*`, `chore/*`, `refactor/*`) are permitted. When in doubt, use `feature/*`.

### feature/*

**Use for:**
- New functionality or features
- Structural changes or refactoring
- Documentation updates
- Dependency updates
- Build system changes
- Any work that is NOT a bug fix

**Rules:**
- Branched from `develop`
- Merged into `develop` via pull request
- Deleted immediately after merge

### bugfix/*

**Use for:**
- Non-urgent defect fixes discovered in development or test environments
- Fixes for issues that do NOT block production

**Rules:**
- Same rules as `feature/*`
- Distinction exists for semantic clarity only
- Branched from `develop`
- Merged into `develop` via pull request
- Deleted immediately after merge

### hotfix/*

**Use for:**
- Production-blocking issues ONLY
- Critical defects affecting live users
- Security vulnerabilities in production

**Rules:**
- Branched from `main`
- Merged into `main` via pull request
- Immediately forward-merged into `release` and `develop`
- Deleted immediately after resolution

**Important:** Creation of a `hotfix/*` branch is treated as an explicit admission of upstream process failure.

---

## 6. Promotion Flow

Normal flow:

```
feature/* or bugfix/* → develop → release → main
```

Promotion semantics:

- develop → release: candidate release, aggressive testing
- release → main: production-ready, ship

---

## 7. Forbidden Operations

The following are explicitly disallowed:

- Merging feature/* or bugfix/* directly into release or main
- Direct commits to eternal branches (all changes require pull requests)
- Direct pushes to develop, release, or main (all changes require pull requests)
- Cherry-picking between eternal branches
- Deploying to production without passing through release
- Long-lived non-eternal branches
- Using branch prefixes other than feature/*, bugfix/*, or hotfix/*

---

## 8. Guiding Principle

> Boring workflows that never surprise are a competitive advantage.

---

Status: Frozen v0.1

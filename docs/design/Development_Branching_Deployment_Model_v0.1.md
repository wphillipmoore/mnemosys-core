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

Each merge into these branches triggers **automatic deployment** to the corresponding environment.

---

## 5. Short-Lived Branches

All work occurs in short-lived branches.

### feature/*

- New functionality or structural changes
- Branched from `develop`
- Merged into `develop`
- Deleted immediately after merge

### bugfix/*

- Non-urgent defect fixes
- Same rules as `feature/*`
- Distinction exists for semantic clarity only

### hotfix/*

- Used only for production-blocking issues
- Branched from `main`
- Merged into `main`
- Immediately forward-merged into `release` and `develop`
- Deleted immediately after resolution

Creation of a `hotfix/*` branch is treated as an explicit admission of upstream process failure.

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
- Direct commits to eternal branches
- Cherry-picking between eternal branches
- Deploying to production without passing through release
- Long-lived non-eternal branches

---

## 8. Guiding Principle

> Boring workflows that never surprise are a competitive advantage.

---

Status: Frozen v0.1

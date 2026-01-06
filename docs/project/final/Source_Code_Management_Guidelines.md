# Source Code Management Guidelines v0.1

This document captures the initial assumptions, constraints, and guiding principles
for source code management within the MNEMOSYS project.

> **Note on nomenclature:** This document originally referenced "FSIPS / RPM project family." The project was subsequently renamed to **MNEMOSYS**, and RPM was integrated as a core component rather than a separate extension. This document has been updated to reflect current terminology while preserving its v0.1 snapshot status.

It represents a frozen **v0.1 snapshot**, intended to support:

- Long-term architectural clarity  
- Informed future revision  
- Survivability of the system without its original author  

---

## Table of Contents
- [1. AI Assistance (Explicitly Bounded)](#1-ai-assistance-explicitly-bounded)
- [2. Version Control Platform](#2-version-control-platform)
  - [Lock-In Awareness](#lock-in-awareness)
- [3. Repository Strategy](#3-repository-strategy)
  - [Core Philosophy](#core-philosophy)
  - [Boundary Rule](#boundary-rule)
  - [Explicit Non-Decision](#explicit-non-decision)
- [4. Python Version Policy](#4-python-version-policy)
  - [Supported Versions](#supported-versions)
  - [CI Requirements](#ci-requirements)
  - [Deployment Rule](#deployment-rule)
- [5. CI/CD Constraints](#5-cicd-constraints)
- [6. Locked vs. Flexible Decisions](#6-locked-vs-flexible-decisions)
  - [Locked at v0.1](#locked-at-v01)
  - [Explicitly Flexible](#explicitly-flexible)
- [7. Guiding Principle](#7-guiding-principle)

## 1. AI Assistance (Explicitly Bounded)

Constraints:

- All AI-generated code must be reviewed with the same rigor as external contributions
- AI assistance must never become a silent dependency
- The codebase must remain understandable, auditable, and maintainable **without AI**

**Invariant:**  
Code correctness, determinism, and maintainability always override speed or convenience.

---

## 2. Version Control Platform

Git is the source control system.

GitHub is selected as the **initial** central repository host, including use of GitHub Actions
for CI/CD pipelines.

This decision is **explicitly provisional**, not foundational.

### Lock-In Awareness

GitHub-specific dependencies must be:

- Understood
- Tracked
- Periodically reassessed

The project must retain sufficient knowledge to evaluate the cost and feasibility of migration
to an alternative hosting provider if required.

Migration readiness is not required at v0.1, but **migration awareness is**.

---

## 3. Repository Strategy

### Core Philosophy

Repositories should be:

- Small
- Modular
- Scoped to a single semantic responsibility

Independent components are expected to live in **separate repositories** by default.

Examples include (but are not limited to):

- ORM / schema tooling
- API services
- CLI tools
- UI clients

### Boundary Rule

Repository boundaries follow **semantic ownership and lifecycle**, not convenience.

This improves:

- Independent evolution
- Reduced cognitive load
- Long-term maintainability
- Survivability without original authorship

### Explicit Non-Decision

Monorepo vs. multirepo strategy is **not locked** at v0.1.

This decision may be revisited once:

- Dependency graphs stabilize
- Tooling friction is observed
- CI/CD cost and complexity are measurable

---

## 4. Python Version Policy

### Supported Versions

- Python **3.13** — current deployment target
- Python **3.14** — forward-compatibility target
- Python **3.15** — early warning target (informational)

### CI Requirements

All CI pipelines must validate in parallel against:

- Current version (3.13) — required
- Next versions (3.14, 3.15) — informational

Failures on the forward-compatibility tracks inform upgrade planning but do **not** block production deployment.

### Deployment Rule

Production deployments always use the current stable Python version.

**Invariant:**  
Code that cannot survive the next Python release without heroics is already technical debt.

---

## 5. CI/CD Constraints

CI/CD pipelines must be:

- Deterministic
- Stateless
- Reproducible locally

Automation should avoid reliance on opaque or irreducibly platform-specific behavior.

GitHub Actions configuration must remain:

- Readable
- Minimal
- Replaceable

**Anti-goal:**  
Clever automation that cannot be reasonably expressed outside GitHub.

---

## 6. Locked vs. Flexible Decisions

### Locked at v0.1

- Git as the source control system
- GitHub as the initial hosting provider
- GitHub Actions for CI/CD
- Python-first implementation
- Parallel testing on current and next Python versions (3.14, 3.15 informational)

### Explicitly Flexible

- Repository granularity and structure
- CI/CD provider choice
- Deployment orchestration details
- Degree and style of AI-assisted development

---

## 7. Guiding Principle

All source code management decisions are evaluated against a single overriding criterion:

> **The system must survive without its original author.**

Tooling, structure, and process choices are judged by their contribution to long-term clarity,
auditability, and evolutionary capacity — not short-term convenience.

---

**Status:**  
This document represents a frozen **v0.1** snapshot.

# Source Code Management Guidelines v0.1

This document captures the initial assumptions, constraints, and guiding principles
for source code management within the MNEMOSYS project.

> **Note on nomenclature:** This document originally referenced "FSIPS / RPM project family." The project was subsequently renamed to **MNEMOSYS**, and RPM was integrated as a core component rather than a separate extension. This document has been updated to reflect current terminology while preserving its v0.1 snapshot status.

It represents a frozen **v0.1 snapshot**, intended to support:

- Long-term architectural clarity  
- Informed future revision  
- Survivability of the system without its original author  

---

## 1. Development Environment

### Primary Editor

Visual Studio Code is the primary development environment.

This is a pragmatic choice and is **explicitly non-architectural**.  
Editor-specific configuration **must not** leak into:

- Repository structure
- Tooling contracts
- Build or deployment assumptions

The codebase must remain editor-agnostic.

### AI Assistance (Explicitly Bounded)

ChatGPT and GitHub Copilot may be used as **advisory tools only**.

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

### CI Requirements

All CI pipelines must validate in parallel against:

- Current version (3.13)
- Next version (3.14)

Failures on the next-version track inform upgrade planning but do **not** block production deployment.

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
- Visual Studio Code as primary editor
- Python-first implementation
- Parallel testing on current and next Python versions

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

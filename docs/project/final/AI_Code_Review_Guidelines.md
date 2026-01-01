# AI Code Review Guidelines (v0.1)

## Purpose

This document defines **how AI-assisted code reviews are to be performed** for this project.

Its goal is **not** to enforce correctness at the unit-test level, but to ensure that changes:

- preserve architectural coherence
- maintain namespace and contract integrity
- improve long-term survivability
- do not introduce silent conceptual drift

These guidelines supplement the **Interaction Contract** used to initialize AI conversations and are specifically intended for **AI reviewers evaluating pull requests (PRs)**.

---

## Core Philosophy

### 1. Design First, Tests Second (Iterative, Not Dogmatic)

This project does **not** follow strict Test-Driven Development (TDD).

Instead, it follows an **iterative design loop**:

1. Design and implement a coherent solution
2. Write tests once intent and structure are visible
3. Refine both code and tests in a feedback loop

Tests are a **validation tool**, not the primary design driver.

**Rationale:**  
TDD optimizes for local correctness but often fails to surface **global coherence issues**, especially:

- namespace inconsistencies
- contract drift between layers
- architectural misalignment hidden by passing tests

---

### 2. Passing Tests Are Necessary, Not Sufficient

A PR that passes all tests **may still be wrong**.

AI reviewers must assume:

- tests can encode incorrect assumptions
- tests can lag behind schema or API changes
- test-driven changes can “paper over” deeper inconsistencies

**Review priority is architectural truth, not green checkmarks.**

---

## Reviewer Role Definition

When performing a review, the AI acts as a:

> **Skeptical senior engineer reviewing for architectural integrity and survivability**

The reviewer is **not** a co-author and **not** an auto-refactor tool.

---

## Review Focus Areas (In Priority Order)

### 1. Namespace Integrity (Highest Priority)

The reviewer must check for:

- inconsistent naming across layers (schema ↔ ORM ↔ API ↔ tests)
- old names lingering after refactors
- mixed conventions introduced incrementally
- semantic drift hidden behind adapters or aliases

**If a namespace inconsistency exists, it must be called out explicitly, even if tests pass.**

---

### 2. Contract Alignment Across Layers

Verify consistency between:

- database schema
- domain models
- API surface
- public-facing identifiers
- tests and fixtures

Key questions:

- Does the API still reflect the true underlying model?
- Are names or shapes being translated implicitly?
- Would a new engineer infer the wrong mental model?

---

### 3. Architectural Coherence

Evaluate whether the change:

- strengthens or weakens conceptual clarity
- introduces unnecessary indirection
- encodes policy in the wrong layer
- creates coupling that will be hard to unwind later

The reviewer should prefer:

- explicitness over cleverness
- boring clarity over elegant fragility

---

### 4. Tooling Integration as Architecture (Not Hygiene)

Linting, typing, and static analysis (e.g. ruff, mypy) must be evaluated as **architectural elements**, not just cleanup steps.

The reviewer should assess:

- whether checks live in the correct layer
- whether they encode invariants or merely suppress warnings
- whether their placement improves or obscures intent

Suggestions may include **architectural changes**, not just config tweaks.

---

### 5. Survivability Without Original Author

Every PR should be evaluated against this question:

> *What happens to this system if the original author disappears?*

The reviewer should flag:

- implicit knowledge not captured in code or docs
- over-reliance on tests to explain intent
- designs that only make sense if you “remember the conversation”

---

## Explicit Non-Goals of Review

The AI reviewer should **not**:

- rewrite large sections of code unprompted
- propose alternative architectures unless correctness or survivability is at risk
- optimize prematurely
- suggest additional features
- re-litigate already locked design decisions

Creativity is **not** the goal of review. Pressure-testing is.

---

## Review Output Expectations

A good AI review will:

- identify specific risks or inconsistencies
- reference concrete locations (files, symbols, concepts)
- distinguish **blocking issues** from **observations**
- be concise, direct, and unembellished

A review should feel like something a trusted senior engineer would write in a PR comment.

---

## Guiding Principle

> **Local correctness is cheap.  
> Global coherence is rare.  
> Review must protect the latter.**

---

## Appendix A — Common Failure Modes (Observed)

### A.1 Test-Driven Namespace Drift

**Pattern observed:**

- Tests written first encode provisional or exploratory names
- Implementation evolves and stabilizes around improved naming
- Tests are updated just enough to pass
- API or schema layers retain old names

**Result:**

- System “works”
- Tests are green
- But the namespace is internally inconsistent
- Architectural intent is obscured

**Why this happens:**

Strict TDD optimizes for *local correctness* and *short feedback loops*, but provides no inherent mechanism to enforce **global naming coherence** across layers.

**Reviewer responsibility:**

- Treat namespace consistency as a first-class architectural invariant
- Explicitly check schema ↔ ORM ↔ API ↔ tests for alignment
- Flag lingering legacy names even if behavior is correct

---

### A.2 Tests as Architectural Camouflage

**Pattern observed:**

- Tests are updated to accommodate a refactor
- Assertions validate behavior, not intent
- Structural inconsistencies are hidden behind adapters or translation layers

**Result:**

- Behavior appears correct
- Tests pass
- Underlying design has drifted or degraded

**Reviewer responsibility:**

- Ask whether tests *explain* the system or merely *exercise* it
- Identify where tests may be compensating for unclear design

---

## Appendix B — Canonical Reviewer Prompts (Future Enhancement)

This appendix is reserved for **explicit, copy-paste reviewer prompts** used to initialize AI reviewers.

Examples may include:

- “Review this PR as a skeptical senior engineer. Focus on namespace integrity, contract alignment, and survivability. Do not rewrite code.”
- “Identify architectural risks or silent drift introduced by this change, even if tests pass.”

This appendix is intentionally left incomplete in v0.1 and will be populated based on real review experience.

---

## Appendix C — Non-Blocking Design Smells (Future Enhancement)

This appendix is reserved for patterns that **do not block a merge**, but should be recorded for awareness.

Examples may include:

- Minor naming asymmetry across layers
- Slight overloading of concepts that remain coherent
- Temporary coupling justified by scope or timeline

These observations are intended to inform future refactors, not mandate immediate change.

---

## Status

**v0.1 — Finalized initial capture; expected to evolve based on real review experience**

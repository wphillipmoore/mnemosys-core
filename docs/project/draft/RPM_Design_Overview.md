# Repertoire Practice Management (RPM)

**Integrated with the String Instrument Practice Framework (SIPF)**
**Design Overview – v0.1**

> **Nomenclature Note:** This document references "SIPF" (String Instrument Practice Framework), which is related to the project formerly known as "FSIPS". The project has since been renamed to **MNEMOSYS**. This historical document is preserved in draft form pending revision to reflect current terminology.

---

## 1. Overview

Repertoire Practice Management (RPM) is a structured system for acquiring, stabilizing, and retaining a large repertoire of technically demanding musical works over long time horizons. It treats repertoire as a portfolio of assets subject to decay, rather than a static list of songs.

## 2. System Summary

### Core Principles

- Repertoire and exercises are distinct but integrated.
- Decay is expected and explicitly managed.
- ProblemSections are the atomic unit of work.
- Cheap maintenance beats heroic relearning.
- Fatigue constraints are non-negotiable.

### Repertoire States

NEW, ACQUIRE, FRAGILE, STABLE, LEGACY, ARCHIVED. FRAGILE items receive highest priority outside of hard deadlines.

### Portfolios

Acquisition Portfolio (growth-focused) and Maintenance Portfolio (retention-focused). Acquisition is throttled if maintenance minimums are not met.

### ProblemSections

Each ProblemSection defines severity, technique tags, tempo ceiling, and failure modes. All exercise selection flows from active ProblemSections.

### Maintenance Tiers

- **Tier 0:** Memory Probe (0.5–2 min)
- **Tier 1:** Section Refresh (2–8 min)
- **Tier 2:** Skeleton Run (5–12 min)
- **Tier 3:** Full Performance (song-length, validation only)

### Decay Model

FAST (3–5 days), MED (7–14 days), SLOW (21–45 days). Intervals expand or contract based on PASS, CLEAN, SHAKY, or FAIL outcomes, with FRAGILE items capped to prevent neglect.

### Scheduler Invariants

- Maintenance scheduled first
- Decay outranks difficulty
- Sections outrank songs
- Lowest effective tier always preferred
- Fatigue limits are enforced via SIPF

## 3. Appendix: Next Steps

### Immediate

- Define canonical TechniqueTag taxonomy
- Define finite failure-mode list
- Run FRAGILE-only Tier 1 sessions

### Short-Term

- Encode minimal JSON data model
- Formalize scheduler interface
- Add lightweight session logging

### Medium-Term

- Automatic exercise selection from TechniqueTags
- Weekly planning layer
- Legacy repertoire bootstrap via Tier 0 probes

### Future / Optional

- Visualization of decay and risk
- Individual decay-rate estimation
- Tooling only after habits stabilize

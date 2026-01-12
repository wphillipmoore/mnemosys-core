# MNEMOSYS — Practice Generator Walkthrough

**Version:** 0.1

This document is a procedural companion to the MNEMOSYS v0.1 Architecture Overview. It describes, step by step, how the practice generator produces a concrete, executable practice session from inputs and system state.

## Table of Contents
- [1. Purpose](#1-purpose)
- [2. Generator Inputs](#2-generator-inputs)
  - [PracticeRequest](#practicerequest)
- [3. Generator State (Conceptual)](#3-generator-state-conceptual)
- [4. Practice Skeleton Construction](#4-practice-skeleton-construction)
- [5. Block-by-Block Resolution](#5-block-by-block-resolution)
- [6. Overload Assignment Rules](#6-overload-assignment-rules)
- [7. Fatigue Budgeting](#7-fatigue-budgeting)
- [8. Executable Output Requirement](#8-executable-output-requirement)
- [9. Determinism & Explainability](#9-determinism-explainability)

## 1. Purpose

The Practice Generator is responsible for converting:
- abstract exercises
- overload and fatigue rules
- available practice time

into a specific, playable practice session with clear intent and constraints.

This document focuses on how the generator thinks, not UI or implementation details.

## 2. Generator Inputs

### PracticeRequest

- InstrumentProfile
- Available time (minutes)
- Practice type: normal | light | heavy | deload
- Goal weights (domain or technique emphasis)

All inputs are explicit and bounded. No free-text interpretation is required.

## 3. Generator State (Conceptual)

At v0.1, the generator assumes minimal or empty state.

Future state (defined elsewhere) will include:
- Exercise recency
- Rolling volume (7-day / 28-day)
- Mastery estimates
- Recent fatigue exposure

When state is missing, conservative defaults are used.

## 4. Practice Skeleton Construction

The generator first builds a PracticeBlock skeleton based solely on available time.

**Examples:**
- ≤25 min: Warmup → Technique → Application
- 30–45 min: Warmup → Technique → Pitch/Harmony → Application
- 60–75 min: Warmup → Technique → Pitch/Harmony → Rhythm → Application

Block order is invariant.

## 5. Block-by-Block Resolution

For each PracticeBlock, the generator performs the following steps:

1. Filter exercises by:
   - allowed domains
   - instrument compatibility
   - fatigue compatibility
2. Score remaining exercises using a deterministic need model
3. Select the highest-need exercise
4. Generate a concrete exercise variant within block overload bounds

The generator never invents new exercises.

## 6. Overload Assignment Rules

For a selected exercise:

- Exactly one primary overload dimension is progressed at a time
- All overload values are clamped to PracticeBlock bounds
- Practice type may further cap overloads (e.g., deload)

If the previous attempt failed or was sloppy:
- overload is held or reduced

## 7. Fatigue Budgeting

Each session implicitly maintains a fatigue budget.

**Rules enforced:**
- No adjacent F2 blocks
- Warmup required if any F2 work appears
- F2 exposure limited in total duration

If fatigue budget is exceeded, the generator:
- downgrades overload
- substitutes a lower-fatigue exercise
- or shortens the block

## 8. Executable Output Requirement

Each PracticeBlock must emit:
- Selected exercise
- Concrete playable variant
- Human-readable instructions
- Focus cues
- Stop / regression conditions

If this cannot be produced, the session is invalid.

## 9. Determinism & Explainability

Given the same inputs and state, the generator will always produce the same session.

Every exercise choice is explainable in terms of:
- block intent
- exercise need
- fatigue constraints

---

**Status:** Practice Generator logic frozen at v0.1

# FSIPS UI/UX Design

**Version:** v0.1

> **Nomenclature Note:** This document uses the original project name "FSIPS" (Fretted String Instrument Practice System) and references "SIPF" (String Instrument Practice Framework). The project has since been renamed to **MNEMOSYS**. This historical document is preserved in draft form pending revision to reflect current terminology.

---

This document captures high-level UX/UI requirements and architectural design goals for the Fretted String Instrument Practice System (FSIPS), with emphasis on long-term survivability, platform independence, and instructor–student shared state.

## Core Invariants

- Data model is the product
- Cloud is the source of truth
- UI is a projection, never a decision-maker
- Determinism and explainability are mandatory
- The system must survive without its original author

## Platform Targets

### Primary

- Mobile-first: iOS (iPhone), Android

### Secondary

- Desktop: macOS, Windows
- Linux: best-effort, non-blocking

## Build Order (Strict)

1. API (canonical contract)
2. CLI (reference client)
3. UI (mobile first, desktop later)

## Cloud & Shared Access Model

- Single authoritative cloud-resident state per student
- Role-aware access (student vs instructor)
- Local devices act as cache and input terminals only
- No forked timelines or merge semantics

## Roles

### Student

- Execute sessions
- Log outcomes
- Inspect state and explanations

### Instructor

- Modify configuration envelopes
- Gate/unlock exercises
- Adjust progression and fatigue caps
- Inspect logs and trends

## Data-Centric Architecture

Layered design:
```
Data Model → Deterministic Engine → API → CLI → UI
```

## Non-Goals (Explicit)

- Offline-first architecture
- Audio analysis or ML
- Real-time collaboration
- UI-owned heuristics or state
- Gamification or social features

## UI Philosophy

- Execution-first, inspection-second
- Minimal daily friction
- Explainability over delight
- UI as instrumentation, not motivation

---

**Status:** This document represents a frozen v0.1 snapshot of UI/UX design intent.

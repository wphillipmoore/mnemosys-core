# FSIPS Architecture — Standards and Conventions

**Version:** v0.1

> **Nomenclature Note:** This document uses the original project name "FSIPS" (Fretted String Instrument Practice System). The project has since been renamed to **MNEMOSYS**. This historical document is preserved in draft form pending revision to reflect current terminology.

---

## 1. Purpose

This document defines standards, conventions, and architectural constraints that govern FSIPS-related design and implementation decisions.

Its role is explicitly normative, not descriptive.

## 2. Canonical vs Derivative Artifacts

Canonical artifacts are sources of truth and must be open, inspectable, and tool-independent.

Derivative artifacts are projections or renderings and may be lossy.

## 3. Proprietary Tools and Formats

Proprietary tools and formats are permitted but constrained.

They are treated as optional integrations and must never be authoritative.

**Guitar Pro (GP) Policy:**
- Guitar Pro is explicitly non-core.
- GP files are export-only artifacts.
- FSIPS must not depend on GP for exercise definition, progression, or visualization.

## 4. File Format Standards

Preference is given to text-based, declarative, diff-friendly formats.

Binary-only formats are discouraged for canonical data.

## 5. Instrument and Tool Independence

Exercises are instrument-agnostic.

Tools may assist but must not define meaning.

## 6. Versioning and Stability

All documents are explicitly versioned.

Breaking changes require version increments and explicit rationale.

## 7. Scope Notes (v0.1)

UI design, rendering aesthetics, and performance optimizations are out of scope.

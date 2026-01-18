# Sphinx Documentation Evaluation Plan

**Status:** Draft

## Table of Contents
- [Context](#context)
- [Goals](#goals)
- [Non-Goals](#non-goals)
- [Evaluation Criteria](#evaluation-criteria)
- [Pilot Scope](#pilot-scope)
- [Decision Outputs](#decision-outputs)
- [Risks](#risks)
- [Open Questions](#open-questions)

## Context

Current documentation is Markdown-only and organized by plans, decisions, and
standards. This works for policy-heavy docs but does not provide cross-references,
API documentation, or documentation quality gates. Sphinx is a potential build
system for structured, versioned docs and could unify standards, ADRs, and API
reference if the overhead is justified.

## Goals

- Determine whether Sphinx delivers durable value beyond Markdown-only docs.
- Define a minimal Sphinx configuration that preserves the current doc layout.
- Decide whether to adopt Sphinx, defer it, or reject it for now.

## Non-Goals

- Converting all Markdown docs into reStructuredText.
- Introducing a documentation toolchain that requires complex onboarding.
- Making a long-term commitment to API autodoc before API surface stabilizes.

## Evaluation Criteria

- **Durability:** Does Sphinx increase long-term maintainability or survivability?
- **Complexity cost:** How much new tooling and configuration does it add?
- **Author independence:** Can new contributors update docs without Sphinx expertise?
- **Documentation quality gates:** Can it enforce broken-link or missing-doc failures?
- **API utility:** Is there a concrete near-term use for autodoc or cross-referencing?

## Pilot Scope

- Build a minimal Sphinx setup that:
  - Renders current Markdown docs (MyST or similar).
  - Includes at least one plan, one ADR, and the standards doc.
  - Enables cross-references and link-checking.
  - Avoids reformatting the existing docs.
- Document the onboarding steps and time-to-first-build.
- Capture whether the build and CI integration are stable and low-friction.

## Decision Outputs

- Adopt now with the minimal pilot configuration, or
- Defer until a defined trigger (public API or docs growth), or
- Reject in favor of Markdown-only documentation.

## Risks

- Tooling overhead dilutes the "boring and explicit" architecture goal.
- Maintenance burden without a stable API undermines value.
- Documentation updates require specialized knowledge, slowing contributions.

## Open Questions

- Is cross-referenced documentation valuable enough to justify tooling?
- Should API reference be deferred until module stability is higher?
- Is Sphinx the best tool versus staying Markdown-only for now?

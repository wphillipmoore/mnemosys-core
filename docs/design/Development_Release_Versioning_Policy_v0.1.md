# MNEMOSYS Development — Release & Versioning Policy v0.1

## Status
Frozen v0.1 snapshot

---

## 1. Purpose

This document defines how MNEMOSYS components are **versioned, released, and consumed**.

The goal is to ensure:
- Deterministic builds
- Reproducible deployments
- Clean rollback semantics
- Auditability over time

---

## 2. Release Definition

A **release** is defined as:

- A merge into the `release` or `main` branch
- Producing a versioned, immutable Python artifact
- Suitable for deployment and rollback

Releases are not mutable.

---

## 3. Versioning

- Semantic Versioning (MAJOR.MINOR.PATCH) is used
- Version numbers are assigned at release time
- Version bumps are explicit and reviewed

Guideline:
- MAJOR: breaking changes
- MINOR: backward-compatible features
- PATCH: bug fixes

---

## 4. Artifact Properties

Released artifacts must be:

- Immutable
- Content-addressable by version
- Installable via pip
- Reproducible from source

Artifacts are first-class operational objects.

---

## 5. Relationship to Branches

- Branches drive deployment automation
- Artifacts provide audit, rollback, and traceability

Production runs what `main` points to, but operational truth is anchored in artifacts.

---

## 6. Rollback Strategy

Rollback is performed by:

- Re-deploying a previously released version
- Never mutating or reusing version numbers

Rollbacks are operational decisions, not code changes.

---

## 7. Forbidden Practices

- Mutating released artifacts
- Reusing version numbers
- Deploying unreleased code
- Publishing artifacts that never ran in test

---

## 8. Guiding Principle

> If you cannot precisely name what is running, you do not control it.

---

Status: Frozen v0.1

# MNEMOSYS Development — Hotfix Policy v0.1

## Status
Frozen v0.1 snapshot

---

## 1. Purpose

This document defines the **hotfix process**, explicitly treating it as a controlled failure mode.

Hotfixes exist to correct production-blocking issues when normal promotion flow is insufficient.

They are expected to be rare.

---

## 2. Definition

A **hotfix** is a change that:

- Addresses a production outage or critical defect
- Cannot wait for standard develop → release → main promotion
- Requires immediate correction in production

---

## 3. Branching Rules

Hotfixes use the following branch namespace:

```
hotfix/<concise-description>
```

Rules:

- Branch from `main`
- Fix only the production issue
- No unrelated refactors or enhancements

---

## 4. Merge Requirements

A hotfix branch must:

1. Be merged into `main`
2. Be forward-merged into `release`
3. Be forward-merged into `develop`
4. Produce a new release version
5. Be deleted immediately

Skipping any step is forbidden.

---

## 5. Cultural Invariant

Creating a hotfix is an explicit signal of process failure upstream.

The system is intentionally designed to make hotfixes:

- Visible
- Slightly painful
- Operationally expensive

This discourages normalization.

---

## 6. Postmortem Requirement

Every hotfix requires a brief written postmortem addressing:

- Root cause
- Why the issue escaped test
- What process change prevents recurrence

No blame. Only system correction.

---

## 7. Forbidden Practices

- Using hotfixes for convenience
- Long-lived hotfix branches
- Bypassing release validation post-hotfix
- Treating hotfixes as normal workflow

---

## 8. Guiding Principle

> Hotfixes are allowed, not accepted.

---

Status: Frozen v0.1

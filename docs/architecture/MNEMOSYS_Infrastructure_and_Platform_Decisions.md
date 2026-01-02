# MNEMOSYS — Infrastructure & Platform Decisions (v0.1)

## Results

- The MNEMOSYS project will use **Amazon Web Services (AWS)** as its cloud provider.
- The project will support **only one cloud provider at a time**.
- **Cloud-provider agnosticism is explicitly out of scope** for early and mid project phases.
- The primary persistent datastore will be **Managed PostgreSQL on AWS RDS**.
- PostgreSQL will be used as a **relational, schema-first database**.
- The initial PostgreSQL major version selected is **16.x**.
- Provider-native capabilities will be preferred before introducing custom tooling.
- SQLAlchemy is selected for ORM and schema definition.
- Alembic or equivalent migration tooling is **not assumed by default** and will be introduced only if provider tooling proves insufficient.
- Database access will be mediated through an API layer; direct client access is not a supported model.
- Temporary public database access is permitted only for controlled bootstrap or diagnostics and must be removed afterward.

---

## Reasoning

- Long-term experience with large-scale infrastructure informed skepticism toward premature multi-cloud strategies.
- Prior enterprise failures were cited where “provider independence” was attempted via third-party abstraction layers, increasing risk rather than reducing it.
- AWS was chosen because it is one of the “Big Three” providers with negligible risk of disappearance and a mature managed-services ecosystem.
- Accepting bounded provider lock-in was considered a lower-risk tradeoff than introducing abstraction complexity early.
- A relational database was selected because the project data (practice templates, instructor metadata, student metadata) is inherently structured and relational.
- PostgreSQL was preferred due to strong consistency guarantees, mature tooling, and deep existing expertise.
- Managed RDS was chosen to eliminate undifferentiated operational work (patching, backups, durability) and allow focus on schema and system design.
- PostgreSQL 16.x was selected as a conservative choice (N−1 policy) to balance maturity and longevity while avoiding early-adopter risk.
- Provider-native tooling is to be evaluated first to avoid carrying forward solutions to problems that may no longer exist.
- Past experience with schema tooling (SQLAlchemy + Alembic) shaped the desire to reuse familiar patterns, but only where they add clear value.
- The API-mediated access model is an implicit consequence of the database and security posture rather than a separately debated decision.
- Security discussions emphasized minimizing blast radius and treating public exposure as a temporary exception.

Reasoning regarding some decisions (e.g., exact future criteria for abandoning AWS) was acknowledged as implicit rather than exhaustively specified.

---

## Options Not Chosen

- **Option: Multi-cloud or cloud-agnostic architecture**
  - Reason: Introduces complexity and risk without near-term benefit; historical failures cited.
  - Status: Rejected.
  - Revisit triggers: A material degradation of AWS viability or a fundamental change in project scale or requirements.

- **Option: Third-party cloud abstraction platforms**
  - Reason: Creates dependency on a smaller, less stable vendor while failing to guarantee true portability.
  - Status: Rejected.
  - Revisit triggers: None stated.

- **Option: Non-relational or schemaless databases**
  - Reason: Poor fit for structured relational data and schema-driven design goals.
  - Status: Rejected.
  - Revisit triggers: If future requirements demand high-volume unstructured or event-only data.

- **Option: Immediate adoption of custom migration tooling**
  - Reason: Risk of solving a problem that may not exist given modern provider tooling.
  - Status: Deferred.
  - Revisit triggers: Demonstrated gaps or friction in provider-native schema evolution support.

---

## Optional: Open Questions

- Under what concrete conditions would Alembic become necessary beyond provider-native tooling?
- What formal criteria will trigger reconsideration of the cloud provider decision?

---

## Status

**v0.1 — Regenerated per Chat Summary Protocol v1.0; scope limited to infrastructure and platform foundations**

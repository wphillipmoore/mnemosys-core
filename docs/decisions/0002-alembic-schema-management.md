# 0002 — Alembic-First Schema Management

## Status
Accepted (near-term)

## Context

MNEMOSYS requires a deterministic, automated process for applying database
schema changes across development, test, and production environments.

AWS-native tooling could provide tighter integration with RDS, but the team
has existing Alembic expertise and wants a single migration workflow that
remains viable across infrastructure providers. Provider independence is
not a strategic priority, but it reduces near-term execution risk and keeps
the automation path consistent across environments.

## Decision

Adopt Alembic end-to-end for schema management and deployment automation
in the near term. This includes:

- Alembic-driven revision generation and migration history
- Automated upgrade and downgrade runners using Alembic commands
- Consistent behavior across development, test, and production

## Consequences

### Positive

- Single tooling path across environments and providers
- Leverages existing Alembic experience and reduces initial risk
- Clear, versioned schema history in the repository

### Negative

- Requires custom orchestration for deployments and rollbacks
- Adds migration runner code that must be maintained
- Potential overlap with AWS-native capabilities

## Revisit Triggers

- AWS-native tooling demonstrably reduces operational risk or complexity
- Alembic-based automation creates persistent deployment friction
- Organizational constraints shift toward deeper AWS-specific integration

## Notes

This decision is scoped to the near term. A re-evaluation is expected after
the Alembic automation is implemented and stabilized.

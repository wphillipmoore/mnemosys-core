# Alembic Migration Workflow

Deployment workflow diagram for Alembic-driven schema changes.

## Table of Contents
- [Diagram](#diagram)

## Diagram

### Sandbox

```mermaid
flowchart LR
  SBV["Validate migrations<br/>scripts/dev/validate_migrations.py<br/>(temp schema in mnemosys_sandbox)"]
  SB[(Sandbox DB)]
  SBV --> SB
```

### Development

```mermaid
flowchart LR
  DEV["Merge to develop"]
  DEV_PIPE["CI/CD deploy<br/>(develop -> development)"]
  DEV_GATE["Alembic runner<br/>alembic current + heads<br/>alembic upgrade heads if needed"]
  DEV_APP["Dev API + DB<br/>mnemosys_dev"]
  DEV --> DEV_PIPE --> DEV_GATE --> DEV_APP
```

### Test

```mermaid
flowchart LR
  REL["Merge to release"]
  TEST_PIPE["CI/CD deploy<br/>(release -> test)"]
  TEST_GATE["Alembic runner<br/>alembic current + heads<br/>alembic upgrade heads if needed"]
  TEST_APP["Test API + DB<br/>mnemosys_test"]
  REL --> TEST_PIPE --> TEST_GATE --> TEST_APP
```

### Production

```mermaid
flowchart LR
  MAIN["Merge to main"]
  PROD_PIPE["CI/CD deploy<br/>(main -> production)"]
  PROD_GATE["Alembic runner<br/>alembic current + heads<br/>alembic upgrade heads if needed"]
  PROD_APP["Prod API + DB<br/>mnemosys_prod"]
  MAIN --> PROD_PIPE --> PROD_GATE --> PROD_APP
```

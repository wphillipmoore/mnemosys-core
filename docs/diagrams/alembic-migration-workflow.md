# Alembic Migration Workflow

Deployment workflow diagram for Alembic-driven schema changes.

## Table of Contents
- [Diagram](#diagram)

## Diagram

### Sandbox

```mermaid
flowchart LR
  classDef compact font-size:12px;
  SBV["Validate migrations<br/>temp schema"]
  SB[(Sandbox DB)]
  SBV --> SB
  class SBV,SB compact;
```

Sandbox validation runs via `scripts/dev/validate_migrations.py` against temporary schema `mnemosys_sandbox`.

### Development

```mermaid
flowchart LR
  classDef compact font-size:12px;
  DEV["Merge to develop"]
  DEV_PIPE["CI/CD deploy<br/>develop -> development"]
  DEV_GATE["Alembic gate<br/>current/heads; upgrade"]
  DEV_APP["Dev API + DB<br/>mnemosys_dev"]
  DEV --> DEV_PIPE --> DEV_GATE --> DEV_APP
  class DEV,DEV_PIPE,DEV_GATE,DEV_APP compact;
```

### Test

```mermaid
flowchart LR
  classDef compact font-size:12px;
  REL["Merge to release"]
  TEST_PIPE["CI/CD deploy<br/>release -> test"]
  TEST_GATE["Alembic gate<br/>current/heads; upgrade"]
  TEST_APP["Test API + DB<br/>mnemosys_test"]
  REL --> TEST_PIPE --> TEST_GATE --> TEST_APP
  class REL,TEST_PIPE,TEST_GATE,TEST_APP compact;
```

### Production

```mermaid
flowchart LR
  classDef compact font-size:12px;
  MAIN["Merge to main"]
  PROD_PIPE["CI/CD deploy<br/>main -> production"]
  PROD_GATE["Alembic gate<br/>current/heads; upgrade"]
  PROD_APP["Prod API + DB<br/>mnemosys_prod"]
  MAIN --> PROD_PIPE --> PROD_GATE --> PROD_APP
  class MAIN,PROD_PIPE,PROD_GATE,PROD_APP compact;
```

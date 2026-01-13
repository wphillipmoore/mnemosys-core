# Alembic Migration Workflow

Deployment workflow diagram for Alembic-driven schema changes.

## Table of Contents
- [Diagram](#diagram)

## Diagram

### Sandbox

```mermaid
flowchart LR
  SBV["Validate migrations"]
  SB[(Sandbox DB)]
  SBV --> SB
```

Sandbox validation runs via `scripts/dev/validate_migrations.py` against temporary schema `mnemosys_sandbox`.
Branch: feature/bugfix/hotfix (manual).

### Development

```mermaid
flowchart LR
  DEV["Merge to develop"]
  DEV_PIPE["CI/CD deploy"]
  DEV_GATE["Alembic gate"]
  DEV_APP["Dev API + DB"]
  DEV --> DEV_PIPE --> DEV_GATE --> DEV_APP
```

Branch: `develop` -> environment `development`. Database: `mnemosys_dev`.

### Test

```mermaid
flowchart LR
  REL["Merge to release"]
  TEST_PIPE["CI/CD deploy"]
  TEST_GATE["Alembic gate"]
  TEST_APP["Test API + DB"]
  REL --> TEST_PIPE --> TEST_GATE --> TEST_APP
```

Branch: `release` -> environment `test`. Database: `mnemosys_test`.

### Production

```mermaid
flowchart LR
  MAIN["Merge to main"]
  PROD_PIPE["CI/CD deploy"]
  PROD_GATE["Alembic gate"]
  PROD_APP["Prod API + DB"]
  MAIN --> PROD_PIPE --> PROD_GATE --> PROD_APP
```

Branch: `main` -> environment `production`. Database: `mnemosys_prod`.

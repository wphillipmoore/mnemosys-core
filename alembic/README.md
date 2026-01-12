# Alembic Migrations

This directory contains Alembic database migration scripts for the mnemosys-core project.

## Table of Contents
- [Generating Migrations](#generating-migrations)
- [Applying Migrations](#applying-migrations)
- [Rolling Back Migrations](#rolling-back-migrations)
- [Migration Validation](#migration-validation)
- [Migration History](#migration-history)
- [Environment Configuration](#environment-configuration)

## Generating Migrations

Create a new migration after modifying models (message must be short `snake_case`, <= 60 chars):

```bash
python scripts/dev/alembic_revision.py add_column_to_practice
```

## Applying Migrations

Apply all pending migrations:

```bash
alembic upgrade head
```

## Rolling Back Migrations

Rollback one migration:

```bash
alembic downgrade -1
```

Rollback to a specific revision:

```bash
alembic downgrade <revision_id>
```

## Migration Validation

Validate upgrade/downgrade in a temporary schema (PostgreSQL only):

```bash
python scripts/dev/validate_migrations.py
```

Optional seed script:

```bash
python scripts/dev/validate_migrations.py --seed-script <path-to-seed-script>
```

## Migration History

View migration history:

```bash
alembic history
```

View current revision:

```bash
alembic current
```

## Environment Configuration

Migrations use the database URL from environment variables:
- Set `MNEMOSYS_ENV` to control environment (sandbox/development/test/production)
- Set `MNEMOSYS_DB_*` components (`DRIVERNAME`, `USERNAME`, `PASSWORD`, `HOST`, `PORT`, `DATABASE`)
  to build the URL (optionally include `SSLMODE`)
- Set `MNEMOSYS_DB_SCHEMA` to target a specific database schema

For migration tooling, admin credentials are expected via `MNEMOSYS_DB_ADMIN_*` (same component names). If admin
variables are not set, the tooling falls back to `MNEMOSYS_DB_*`.

See `src/mnemosys_core/config/settings.py` for configuration details.

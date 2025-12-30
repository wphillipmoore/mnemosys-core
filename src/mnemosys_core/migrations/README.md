# Alembic Migrations

This directory contains Alembic database migration scripts for the mnemosys-core project.

## Generating Migrations

Create a new migration after modifying models:

```bash
alembic revision --autogenerate -m "description of changes"
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
- Set `MNEMOSYS_ENV` to control environment (development/test/production)
- Set `DATABASE_URL` to override the default database connection string

See `src/mnemosys_core/config/settings.py` for configuration details.

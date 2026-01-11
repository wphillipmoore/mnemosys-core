# Test/Production Database Parity Plan (RDS Promotion)

**Status:** Draft

## Table of Contents
- [Context](#context)
- [Goals](#goals)
- [Non-Goals](#non-goals)
- [Invariants](#invariants)
- [Current State (Assumed)](#current-state-assumed)
- [Target State](#target-state)
- [Plan (Step-by-Step)](#plan-step-by-step)
- [Validation](#validation)
- [Risks](#risks)
- [Open Questions](#open-questions)

## Context

The test environment must be a near-identical proxy for production. That requires
test and production databases to run on the same infrastructure tier with minimal
configuration drift. To achieve this, we will promote the managed Postgres instance
used for development into a production-tier configuration and use that pattern for
the test database (release branch deployments).

This plan builds on:
- `docs/plans/pending/2026-01-04-aws-nonprod-rest-api-deploy-plan.md`
- `docs/project/final/Database_Environment_Setup.md`

## Goals

- Align test and production database infrastructure tiers.
- Document the production-grade AWS RDS configuration by applying it to test.
- Keep dev/test updates strictly pipeline-driven (no local credentials).
- Preserve "rebuild from scratch" and migration gate behavior.

## Non-Goals

- Full production cutover (main branch) and public-facing rollout.
- Multi-account or multi-region database strategy.
- Database sharding, read replicas, or cross-region replication.

## Invariants

- Test and production use the same engine version, parameter group, instance class,
  storage type, encryption, and backup policies.
- Release branch drives test deployments; developers do not hold test credentials.
- Migration gate remains the only automated schema change path.
- Any drift between test and production must be intentional, documented, and minimal.
- Test database data is disposable during this proof-of-concept phase.

## Current State (Assumed)

- Nonprod RDS exists and is used by development/test deployments.
- Development database is on a non-production tier configuration.
- Test database credentials are stored only in AWS (SSM/Secrets), not locally.

## Target State

- Test database runs on production-tier RDS configuration.
- Configuration parity with production is explicit and enforced.
- Development remains isolated from test (no shared credentials; no direct access).

## Plan (Step-by-Step)

1. Inventory current RDS configuration used by development/test:
   - Engine version, instance class, storage type, IOPS, encryption.
   - Parameter group, maintenance window, backup retention.
   - Security groups, subnet group, VPC placement.
2. Define the production-tier baseline:
   - Instance class and storage class sized for production.
   - Multi-AZ, backup retention, deletion protection, performance insights.
   - Parameter group settings required for production parity.
3. Destroy and recreate the test database as a clean production-tier instance:
   - No data preservation required in the current proof-of-concept phase.
   - Apply instance class, storage, and parameter group changes at creation time.
   - Enforce backups, encryption, monitoring, deletion protection.
4. Update AWS secrets/SSM parameters for the test environment:
   - `/mnemosys/test/db/host`, `/mnemosys/test/db/port`, etc.
   - Confirm admin credentials are present and rotate if required.
5. Validate pipeline behavior:
   - Merge `develop` -> `release` and confirm the migration gate runs against the
     updated test database and succeeds.
   - Confirm application health checks succeed post-deploy.
6. Document the production-grade RDS configuration and parity rules.

## Validation

- Release pipeline deploys to test without manual database access.
- Alembic migration gate applies cleanly and logs expected output.
- RDS configuration matches the production-tier baseline.

## Risks

- Misconfigured parameter group or storage settings can cause downtime.
- Drift between test and production if parity rules are not enforced in docs.
- Instance recreation changes endpoints and requires secrets updates.

## Open Questions

- Is Multi-AZ required for test (to mirror production) or optional for cost?
- What are the exact production-tier parameters (instance class, storage size, IOPS)?

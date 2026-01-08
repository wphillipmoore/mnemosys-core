# AWS Nonprod REST API Deployment Plan (Bootstrap v0.1)

**Date**: 2026-01-04
**Status**: Draft

## Table of Contents
- [Overview](#overview)
- [Scope](#scope)
- [Non-Goals](#non-goals)
- [Assumptions (Locked for v0.1)](#assumptions-locked-for-v01)
- [Architecture Summary (Minimal)](#architecture-summary-minimal)
- [Secrets and Parameter Naming (SSM)](#secrets-and-parameter-naming-ssm)
- [Migration Path to Durable Infrastructure (Explicit)](#migration-path-to-durable-infrastructure-explicit)
- [Runtime Contract (Migration Gate)](#runtime-contract-migration-gate)
- [Implementation Plan (Step-by-Step)](#implementation-plan-step-by-step)
  - [Step 0: Repository additions (local)](#step-0-repository-additions-local)
  - [Step 1: AWS bootstrap variables](#step-1-aws-bootstrap-variables)
  - [Step 2: Security groups](#step-2-security-groups)
  - [Step 3: ECR and logs](#step-3-ecr-and-logs)
  - [Step 4: IAM roles](#step-4-iam-roles)
  - [Step 5: ECS cluster + ALB](#step-5-ecs-cluster-alb)
  - [Step 6: ECS task definitions and services](#step-6-ecs-task-definitions-and-services)
  - [Step 7: GitHub Actions deployment](#step-7-github-actions-deployment)
  - [Step 8: Validation](#step-8-validation)
- [Known Issues](#known-issues)
- [Open Questions (Deferred)](#open-questions-deferred)
- [Bootstrap Outputs (Current State)](#bootstrap-outputs-current-state)

## Overview

This plan defines the AWS bootstrap steps and GitHub Actions automation needed to deploy
the MNEMOSYS REST API to **development** and **test** environments. It follows the
branch-to-environment mapping defined in `docs/project/final/Development_Branching_Deployment_Model.md`
and the database bootstrap constraints in `docs/project/final/Database_Environment_Setup.md`.

The initial implementation uses **minimal AWS infrastructure** (default VPC, HTTP-only ALB)
to reduce bootstrap friction, while preserving a clean migration path to a dedicated VPC
and TLS-based routing later.

## Scope

- Nonprod AWS infrastructure for REST API deployment (development + test).
- AWS CLI-first provisioning and updates.
- GitHub Actions automation for deploys on `develop` and `release`.
- Runtime contract for migration gate + API startup.

## Non-Goals

- Production deployment (main branch).
- Multi-account or multi-cloud configuration.
- Full Infrastructure-as-Code migration (Terraform/CDK/CloudFormation).
- TLS/ACM and custom DNS (deferred to durable phase).

## Assumptions (Locked for v0.1)

- REST API runtime: **FastAPI** on **ECS Fargate**.
- Nonprod AWS account: single account with `mnemosys-admin` IAM user.
- Region: `us-east-2`.
- Nonprod RDS is already provisioned per bootstrap doc; API needs only network access + creds.
- Sandbox is local-only and does not deploy.

## Architecture Summary (Minimal)

- **ECS Fargate**: one cluster, two services (`mnemosys-dev-api`, `mnemosys-test-api`).
- **ECR**: one repository (`mnemosys-core`) for container images.
- **ALB**: single load balancer with two listeners.
  - Port 80 -> dev target group
  - Port 8080 -> test target group
  - Rationale: ALB does not rewrite paths, so port-based routing avoids prefix rewrites.
- **Security Groups**:
  - ALB SG: inbound 80 from internet; outbound to ECS SG.
  - ECS SG: inbound 8000 from ALB SG; outbound 5432 to RDS SG.
- **IAM Roles**:
  - ECS task execution role (ECR pull + CloudWatch logs).
  - ECS task role (read secrets).
  - GitHub Actions OIDC role for deploys.
- **Logging**: CloudWatch log groups per environment (`/mnemosys/dev/api`, `/mnemosys/test/api`).
- **Secrets**: SSM Parameter Store (SecureString) for DB credentials.

## Secrets and Parameter Naming (SSM)

Parameters are stored under `/mnemosys/<environment>/` using SecureString values.
Environment values are `development` and `test` (log group names use `dev`/`test` shorthand for consistency with ECS service names).

Required parameters per environment:

- `/mnemosys/<environment>/db/drivername` (e.g., `postgresql`)
- `/mnemosys/<environment>/db/username`
- `/mnemosys/<environment>/db/password`
- `/mnemosys/<environment>/db/host`
- `/mnemosys/<environment>/db/port` (string)
- `/mnemosys/<environment>/db/database` (e.g., `mnemosys_dev` or `mnemosys_test`)
- `/mnemosys/<environment>/db/sslmode` (e.g., `require`)
- `/mnemosys/<environment>/db_admin/username`
- `/mnemosys/<environment>/db_admin/password`

Example parameter creation:

```bash
aws ssm put-parameter \
  --name /mnemosys/development/db/host \
  --type SecureString \
  --value <rds-endpoint> \
  --overwrite
```

## Migration Path to Durable Infrastructure (Explicit)

Minimal bootstrap must not block a dedicated VPC/TLS setup. To preserve the path:

- Use explicit, unique resource names (avoid implicit defaults).
- Keep ECS task definitions and services portable across subnets.
- Treat ALB + ECS + SGs as replaceable layers.
- Keep all sensitive values in Secrets Manager/SSM from day one.
- Avoid hardcoding VPC IDs or subnet IDs in code; use variables in CLI scripts.

See `docs/plans/2026-01-07-test-prod-db-parity-plan.md` for the test/production
database parity and RDS recreation plan.

## Runtime Contract (Migration Gate)

Every container start must execute the migration gate before serving traffic:

1. `python alembic/runner.py upgrade` (uses `MNEMOSYS_DB_ADMIN_*` with fallback).
2. Start `uvicorn` only after upgrade runner exits successfully.

This enforces the behavior documented in
`docs/plans/2026-01-03-alembic-schema-management-design.md`.

## Implementation Plan (Step-by-Step)

### Step 0: Repository additions (local)

- Add `Dockerfile` for FastAPI + uvicorn.
- Add `scripts/runtime/entrypoint.sh` to run migration runner then start API.
- Add `src/mnemosys_core/api/runtime.py` factory for uvicorn `--factory` usage.
- Add `infra/ecs/task-def-template.json` plus render helper at `scripts/deploy/render_task_definition.py`.
- Add IAM template render helper at `scripts/deploy/render_iam_templates.py`.
- Add AWS IAM policy JSON files under `infra/iam/`.
- Add `.github/workflows/deploy-nonprod.yml` for `develop` and `release`.

### Step 1: AWS bootstrap variables

```bash
export AWS_PROFILE=mnemosys-admin
export AWS_REGION=us-east-2
```

Use default VPC for v0.1 bootstrap:

```bash
VPC_ID=$(aws ec2 describe-vpcs --filters Name=isDefault,Values=true --query "Vpcs[0].VpcId" --output text)
SUBNET_IDS=$(aws ec2 describe-subnets --filters Name=vpc-id,Values=$VPC_ID --query "Subnets[].SubnetId" --output text)
```

### Step 2: Security groups

Create ALB and ECS security groups. Allow ALB -> ECS and ECS -> RDS:

```bash
ALB_SG_ID=$(aws ec2 create-security-group \
  --group-name mnemosys-nonprod-alb-sg \
  --description "ALB SG for mnemosys nonprod" \
  --vpc-id "$VPC_ID" --query "GroupId" --output text)

ECS_SG_ID=$(aws ec2 create-security-group \
  --group-name mnemosys-nonprod-ecs-sg \
  --description "ECS SG for mnemosys nonprod" \
  --vpc-id "$VPC_ID" --query "GroupId" --output text)

aws ec2 authorize-security-group-ingress \
  --group-id "$ALB_SG_ID" --protocol tcp --port 80 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id "$ALB_SG_ID" --protocol tcp --port 8080 --cidr 0.0.0.0/0

aws ec2 authorize-security-group-ingress \
  --group-id "$ECS_SG_ID" --protocol tcp --port 8000 --source-group "$ALB_SG_ID"
```

RDS SG rule (if RDS is already provisioned):

```bash
aws ec2 authorize-security-group-ingress \
  --group-id <rds-sg-id> --protocol tcp --port 5432 --source-group "$ECS_SG_ID"
```

### Step 3: ECR and logs

```bash
aws ecr create-repository --repository-name mnemosys-core
aws logs create-log-group --log-group-name /mnemosys/dev/api
aws logs create-log-group --log-group-name /mnemosys/test/api
```

### Step 4: IAM roles

Create IAM roles for:
- ECS execution role (ECR + logs).
- ECS task role (read DB secrets).
- GitHub Actions OIDC role (deploy automation).

These use JSON policy files stored in `infra/iam/` and require placeholder substitution:

- `infra/iam/ecs-task-exec-trust.json`
- `infra/iam/ecs-task-trust.json`
- `infra/iam/ecs-task-secrets-policy.json`
- `infra/iam/gha-deploy-role-trust.json`
- `infra/iam/gha-deploy-policy.json`

Render the templates into a temporary directory:

```bash
python scripts/deploy/render_iam_templates.py \
  --output-dir /tmp/mnemosys-iam \
  --aws-account-id <account-id> \
  --aws-region us-east-2 \
  --github-org <github-org> \
  --github-repo <github-repo>
```

Create the GitHub OIDC provider (required for Actions):

```bash
aws iam create-open-id-connect-provider \
  --url https://token.actions.githubusercontent.com \
  --client-id-list sts.amazonaws.com \
  --thumbprint-list 6938fd4d98bab03faadb97b34396831e3780aea1
```

Note: verify the current thumbprint from GitHub if AWS rejects the provider creation.

Create roles and policies using rendered files:

```bash
aws iam create-role \
  --role-name mnemosys-ecs-task-exec \
  --assume-role-policy-document file:///tmp/mnemosys-iam/ecs-task-exec-trust.json

aws iam attach-role-policy \
  --role-name mnemosys-ecs-task-exec \
  --policy-arn arn:aws:iam::aws:policy/service-role/AmazonECSTaskExecutionRolePolicy

aws iam create-role \
  --role-name mnemosys-ecs-task \
  --assume-role-policy-document file:///tmp/mnemosys-iam/ecs-task-trust.json

aws iam put-role-policy \
  --role-name mnemosys-ecs-task \
  --policy-name mnemosys-ecs-task-secrets \
  --policy-document file:///tmp/mnemosys-iam/ecs-task-secrets-policy.json

# ECS execution role also needs SSM access to fetch secrets at task startup.
aws iam put-role-policy \
  --role-name mnemosys-ecs-task-exec \
  --policy-name mnemosys-ecs-task-exec-ssm \
  --policy-document file:///tmp/mnemosys-iam/ecs-task-secrets-policy.json

aws iam create-role \
  --role-name mnemosys-gha-deploy \
  --assume-role-policy-document file:///tmp/mnemosys-iam/gha-deploy-role-trust.json

aws iam put-role-policy \
  --role-name mnemosys-gha-deploy \
  --policy-name mnemosys-gha-deploy-policy \
  --policy-document file:///tmp/mnemosys-iam/gha-deploy-policy.json
```

### Step 5: ECS cluster + ALB

```bash
aws ecs create-cluster --cluster-name mnemosys-nonprod

ALB_ARN=$(aws elbv2 create-load-balancer \
  --name mnemosys-nonprod-alb \
  --subnets $SUBNET_IDS \
  --security-groups "$ALB_SG_ID" \
  --query "LoadBalancers[0].LoadBalancerArn" --output text)

DEV_TG_ARN=$(aws elbv2 create-target-group \
  --name mnemosys-dev-tg --protocol HTTP --port 8000 \
  --vpc-id "$VPC_ID" --health-check-path /health/ \
  --target-type ip \
  --query "TargetGroups[0].TargetGroupArn" --output text)

TEST_TG_ARN=$(aws elbv2 create-target-group \
  --name mnemosys-test-tg --protocol HTTP --port 8000 \
  --vpc-id "$VPC_ID" --health-check-path /health/ \
  --target-type ip \
  --query "TargetGroups[0].TargetGroupArn" --output text)

DEV_LISTENER_ARN=$(aws elbv2 create-listener \
  --load-balancer-arn "$ALB_ARN" --protocol HTTP --port 80 \
  --default-actions Type=forward,TargetGroupArn="$DEV_TG_ARN" \
  --query "Listeners[0].ListenerArn" --output text)

TEST_LISTENER_ARN=$(aws elbv2 create-listener \
  --load-balancer-arn "$ALB_ARN" --protocol HTTP --port 8080 \
  --default-actions Type=forward,TargetGroupArn="$TEST_TG_ARN" \
  --query "Listeners[0].ListenerArn" --output text)
```

### Step 6: ECS task definitions and services

- Render `infra/ecs/task-def-template.json` with `scripts/deploy/render_task_definition.py`.
- Set `MNEMOSYS_ENV` to `development` or `test`.
- Inject `MNEMOSYS_DB_*` and `MNEMOSYS_DB_ADMIN_*` from SSM parameters.
- Entrypoint runs migration gate then starts uvicorn.

Register task definitions and create services:

```bash
python scripts/deploy/render_task_definition.py \
  --template infra/ecs/task-def-template.json \
  --output /tmp/task-def-dev.json \
  --environment development \
  --image-uri <image-uri> \
  --execution-role-arn <ecs-task-exec-role-arn> \
  --task-role-arn <ecs-task-role-arn> \
  --log-group /mnemosys/dev/api \
  --aws-region us-east-2

aws ecs register-task-definition --cli-input-json file:///tmp/task-def-dev.json

python scripts/deploy/render_task_definition.py \
  --template infra/ecs/task-def-template.json \
  --output /tmp/task-def-test.json \
  --environment test \
  --image-uri <image-uri> \
  --execution-role-arn <ecs-task-exec-role-arn> \
  --task-role-arn <ecs-task-role-arn> \
  --log-group /mnemosys/test/api \
  --aws-region us-east-2

aws ecs register-task-definition --cli-input-json file:///tmp/task-def-test.json

aws ecs create-service \
  --cluster mnemosys-nonprod \
  --service-name mnemosys-dev-api \
  --task-definition mnemosys-dev-api \
  --desired-count 1 --launch-type FARGATE \
  --health-check-grace-period-seconds 120 \
  --network-configuration "awsvpcConfiguration={subnets=[...],securityGroups=[$ECS_SG_ID],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=$DEV_TG_ARN,containerName=mnemosys-api,containerPort=8000

aws ecs create-service \
  --cluster mnemosys-nonprod \
  --service-name mnemosys-test-api \
  --task-definition mnemosys-test-api \
  --desired-count 1 --launch-type FARGATE \
  --health-check-grace-period-seconds 120 \
  --network-configuration "awsvpcConfiguration={subnets=[...],securityGroups=[$ECS_SG_ID],assignPublicIp=ENABLED}" \
  --load-balancers targetGroupArn=$TEST_TG_ARN,containerName=mnemosys-api,containerPort=8000
```

### Step 7: GitHub Actions deployment

Deploy on branch merges:
- `develop` -> development service
- `release` -> test service

Required GitHub Actions repository variables:

- `AWS_ACCOUNT_ID`
- `AWS_OIDC_ROLE_ARN` (role ARN for `mnemosys-gha-deploy`)

Workflow actions:
1. Build container image.
2. Push to ECR.
3. Render new task definition with updated image tag.
4. Register task definition.
5. Update ECS service and wait for stability.

Use GitHub OIDC for AWS auth (no static keys).

### Step 8: Validation

- Hit `/health` on ALB default path for development.
- Hit `/health` on the test listener (port 8080).
- Confirm ECS tasks log migration runner output.
- Confirm alembic gate applies new revisions before app start.

Example:

```bash
curl -fsSL http://<alb-dns>/health/
curl -fsSL http://<alb-dns>:8080/health/
```

## Known Issues

- `brew install --cask docker` can time out during Docker Desktop download; current Docker 20.10.12 is sufficient for nonprod builds.
- Retry the install locally if a Desktop upgrade is required: `brew install --cask docker`.

## Open Questions (Deferred)

- When to switch to a dedicated VPC and private subnets?
- When to add TLS and real subdomains for dev/test?
- Do we want separate ALBs for dev/test or keep shared until prod?
- Should migration gate run in container entrypoint or init task?

## Bootstrap Outputs (Current State)

Captured from the initial bootstrap run (update if re-provisioned):

- AWS account: `959713283130`
- Region: `us-east-2`
- Default VPC: `vpc-06f003b77e593c99a`
- Subnets: `subnet-0c174c9ad03ad6808`, `subnet-07ebe0f6e86eb955b`, `subnet-017aaa23437259fa2`
- RDS instance: `mnemosys-postgres`
- RDS endpoint: `mnemosys-postgres.c3uamoeq6wst.us-east-2.rds.amazonaws.com`
- RDS SG: `sg-0463c511b48bcbef5`
- ALB name: `mnemosys-nonprod-alb`
- ALB DNS: `mnemosys-nonprod-alb-1104521642.us-east-2.elb.amazonaws.com`
- ALB SG: `sg-0899f0b2207153896`
- ECS SG: `sg-069f915c6fc98b0a6`
- ECS cluster: `mnemosys-nonprod`
- ECR repo URI: `959713283130.dkr.ecr.us-east-2.amazonaws.com/mnemosys-core`
- Target groups:
  - dev: `arn:aws:elasticloadbalancing:us-east-2:959713283130:targetgroup/mnemosys-dev-tg/a9cebb5223d19b3a`
  - test: `arn:aws:elasticloadbalancing:us-east-2:959713283130:targetgroup/mnemosys-test-tg/df967036165866c3`
- Listeners:
  - dev: port 80 -> `arn:aws:elasticloadbalancing:us-east-2:959713283130:listener/app/mnemosys-nonprod-alb/ba78c0d6da6303b6/58c3cce7af769176`
  - test: port 8080 -> `arn:aws:elasticloadbalancing:us-east-2:959713283130:listener/app/mnemosys-nonprod-alb/ba78c0d6da6303b6/ad630da2ac235c61`
- Services:
  - dev: `mnemosys-dev-api`
  - test: `mnemosys-test-api`

# Architecture Decisions

## System boundaries

The control plane owns workflow metadata, governance, run telemetry, KPI calculation, and
review evidence. External systems remain systems of record. Integrations should use adapters
so JIRA, Confluence, SharePoint, or automation-platform changes do not leak into the domain.

## Reliability

- Every execution receives a correlation ID.
- Failed quality gates produce failed runs and no output records or claimed savings.
- Write operations require authentication.
- Workflow status prevents paused or draft workflows from executing.
- Health checks and persistent storage support automated recovery.

## Scalability path

The reference runner is intentionally synchronous so the repository remains easy to evaluate.
At higher volume, the API should publish idempotent jobs to a queue, workers should checkpoint
stage results, and metrics should be materialised asynchronously. PostgreSQL becomes the system
of record and object storage holds large execution artefacts. The bundled SQLite container uses
one application worker to avoid startup and write contention; enable multiple replicas only
after moving persistence to PostgreSQL.

## Data and metric integrity

Savings are estimates based on baseline manual minutes, automated minutes, and loaded labour
cost. Production governance must validate baselines with Finance or Operations and distinguish
capacity released from cashable savings. Failed runs never claim benefits.

## Security

The container is non-root and drops Linux capabilities. Secrets are environment supplied.
Enterprise use requires OIDC, RBAC, TLS, central secret management, audit-log export, data
classification controls, and retention aligned with policy.

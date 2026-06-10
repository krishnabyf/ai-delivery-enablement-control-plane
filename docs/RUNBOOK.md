# Production Runbook

## Start and verify

```bash
cp .env.example .env
docker compose up --build -d
curl --fail http://localhost:8000/health
```

Dashboard: `http://localhost:8000`  
API documentation: `http://localhost:8000/docs`

## Operational checks

```bash
docker compose ps
docker compose logs --tail=100 control-plane
curl --fail http://localhost:8000/api/v1/metrics
```

## Incident response

1. Confirm health endpoint and container state.
2. Correlate the failure using the run correlation ID.
3. Pause the affected workflow if quality or data integrity is at risk.
4. Preserve logs and database backup before remediation.
5. Restore the last known-good image or workflow version.
6. Complete a post-implementation review with owner and actions.

## Backup and recovery

The default deployment stores SQLite data in the `control-plane-data` Docker volume.
Production environments should use managed PostgreSQL with point-in-time recovery.
Backups must be encrypted, restoration-tested quarterly, and aligned to data retention policy.

## Security controls

- Replace the default API key and store it in a secret manager.
- Terminate TLS at the ingress or load balancer.
- Restrict CORS to approved origins.
- Run as a non-root user with Linux capabilities dropped.
- Review dependency and CodeQL findings before release.
- Apply enterprise SSO/RBAC before exposing write operations broadly.

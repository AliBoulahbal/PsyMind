# Production deployment

## Minimum host
Start with an Ubuntu LTS VM with Docker Engine + Compose plugin, encrypted disk,
restricted SSH, firewall allowing only SSH/80/443, and an off-host backup target.

## First deployment
1. Copy `.env.production.example` to `.env.production`.
2. Run `ops/generate-secrets.sh` and replace every placeholder.
3. Put TLS cert/key under `infra/nginx/certs/` or terminate TLS before Nginx.
4. Run `sh ops/deploy.sh`.
5. Verify `/health`, `/ready`, login, RLS isolation and audit events.
6. Run `sh ops/backup.sh`, then restore that backup into a disposable environment.
7. Only after restore and tenant-isolation tests pass should the service receive non-synthetic data.

## Important
The runtime API role is `psymind_app`. It must remain `NOSUPERUSER NOBYPASSRLS`.
The owner role is reserved for migrations/admin and must never be used by the API.

For healthcare production, infrastructure readiness is not equivalent to legal,
privacy, clinical, or medical-device approval.

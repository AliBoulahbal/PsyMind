# PsyMind V3 Validation Report

Date: 2026-10-05

## Baseline before V3
- Python compile: PASS
- Existing pytest: FAIL during collection because the project did not configure its Python import path (`ModuleNotFoundError: app`).
- Docker runtime: NOT AVAILABLE in the execution environment.
- Frontend dependency installation: NOT COMPLETED within the runner window.

## After V3
- Python compile: PASS
- Backend automated tests: PASS — 11/11
- PII encryption round-trip: PASS
- Prompt-injection baseline contract: PASS
- Critical action HITL contract: PASS
- Client schemas cannot control tenant_id: PASS
- Document chunking contract: PASS
- V3 RLS migration contains all 7 new tenant-scoped tables: PASS
- PostgreSQL application role provisioning includes NOBYPASSRLS: PASS
- Production configuration enforces psymind_app runtime role: PASS
- Production compose has no --reload: PASS
- PII production secret is required: PASS
- Preflight and postdeploy scripts: PRESENT

## Not executed in this environment
- Docker Compose config/runtime: Docker binary unavailable.
- PostgreSQL real RLS Tenant A/B integration: requires running PostgreSQL.
- Alembic migration against live PostgreSQL: requires Docker/PostgreSQL.
- MinIO upload integration: requires services.
- Ollama/Gemma runtime: requires Ollama/model.
- Frontend `npm install` did not complete in the runner; node_modules was absent, so typecheck/build could not be validly executed.
- Backup -> restore drill: requires running production-like PostgreSQL.
- External penetration test: external process, not performed.
- Clinical validation/regulatory review: not a software test and not performed.

## Required production acceptance on target server
Run:
1. `sh ops/preflight.sh`
2. tenant A/B isolation integration suite
3. upload/RAG/Ollama smoke test
4. backup then restore into disposable environment
5. `BASE_URL=https://your-domain sh ops/postdeploy-test.sh`
6. TLS/security scan and pentest
7. clinical/legal/privacy approval before real patient data

A deployment is not considered approved for real clinical data until all NOT RUN production gates are executed successfully.


# PsyMind V3 Clinical Production Edition

# PsyMind V2 — Full reference implementation

Production-oriented **reference architecture** for a multi-tenant clinical SaaS.
It is intentionally safe for development: use synthetic data only.

## Included
- FastAPI modular monolith, PostgreSQL + pgvector, Redis, MinIO
- JWT auth, tenant context, RBAC permissions
- PostgreSQL RLS + FORCE RLS migration
- Patients, consultations, diseases/diagnoses, medications, allergies, prescriptions
- Documents/chunks, deterministic local embeddings, hybrid retrieval + RRF
- AI Gateway abstraction with a safe mock provider by default
- Agent/HITL persistent approvals
- Risk engine interface + deterministic synthetic development model
- Append-only audit table + hash chain fields
- AI usage tracking
- Next.js dashboard starter
- Pytest tenant/security tests
- Docker Compose

## Important
This is **not a certified medical device** and does not provide autonomous diagnosis or treatment.
The risk and AI modules are engineering scaffolding until you plug in validated models/providers.
Do not use real patient data in development.

## Start
```bash
cp .env.example .env
# replace SECRET_KEY and MinIO credentials
docker compose up --build
```

API: http://localhost:8000/docs
Web: http://localhost:3000

Seed demo:
- tenant: `demo-center`
- admin: `admin@psymind.local`
- password: `ChangeMe123!`

Change/delete demo credentials before any non-local deployment.

## Algeria production target

For the Algeria-targeted dedicated-server edition, see `docs/FINALISATION_ALGERIE.md`. Production is configured for local Ollama inference and local embeddings only. The repository is not yet clinically/regulatorily approved and must pass all listed production gates before real patient data is used.

## Phase mapping
1. Foundation: Docker/Postgres/Redis/MinIO/config
2. Security: JWT/RBAC/tenant/RLS/audit
3. CRM: patients/consultations/diagnoses/prescriptions
4. RAG: documents/chunks/vector+FTS/RRF/citations
5. LLM: AI gateway/provider abstraction/usage
6. ML: risk interface + development model
7. Agents: persistent HITL approvals
8. SaaS: tenants/quotas/usage
9. Testing: unit/integration/security tests
10. Production: health checks, CI example, observability hooks

See `docs/PRODUCTION_CHECKLIST.md` before deployment.


## Application Edition
The `web/` directory now contains the connected clinical frontend. See `docs/APPLICATION_COMPLETE.md`.


See `docs/V3_PRODUCTION.md` for V3 production gates and deployment evidence requirements.

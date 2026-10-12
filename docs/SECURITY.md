# Security invariants
- Client payloads never establish tenant identity.
- Tenant is taken from verified authentication context.
- Runtime DB role is non-owner and NOBYPASSRLS.
- Every tenant table has ENABLE + FORCE ROW LEVEL SECURITY.
- Critical clinical/AI actions require explicit human approval.
- Audit events are append-only at DB trigger level and hash chained.
- Production secrets are external to source control.
- Clinical documents are private objects.
- No real patient data is permitted in local/dev environments.
- A DB superuser can still defeat database-local audit controls: export audit events to external immutable/WORM storage.

- Production AI inference is local Ollama only; no hosted LLM API keys are permitted.
- Production embeddings use a locally cached 384-dimensional Sentence Transformers model.
- AI outage returns 503 for AI requests; clinical record APIs remain available.
- Keep Ollama on the internal Compose network; never publish its port to the Internet.

# PsyMind V3 Clinical Production Edition

## What V3 adds
- encrypted Patient Identity Vault
- tenant-scoped Model Registry
- tenant-scoped versioned Knowledge Base metadata
- feature flags for controlled rollout
- clinician AI feedback labels
- Evaluation Run persistence model
- Security Event persistence
- AI quota enforcement
- AI disaster mode: CRM stays available if the LLM is down
- refresh/access JWTs include JTI
- governance UI
- preflight and post-deploy scripts
- V3 RLS migration for all new tenant tables

## Production gates
Code/build success is necessary but not sufficient.
Before real patient data, require:
1. PostgreSQL tenant A/B integration tests on the real DB role.
2. Successful backup -> disposable restore.
3. TLS and secret scan.
4. upload malware scanning.
5. OCR worker sandbox if scanned documents are accepted.
6. external immutable audit sink.
7. observability and alerts.
8. SSO/MFA for privileged users.
9. security test/pentest.
10. clinical/legal/privacy review.

## PII Vault
The new `patient_identities` table stores encrypted JSON separately from clinical data.
Production must use a high-entropy PII_ENCRYPTION_KEY from a secret manager. The included Fernet-derived key is an application-layer baseline. Mature deployments should use envelope encryption backed by KMS/HSM and key rotation.

## Model Registry
Models are registered as candidate. Approval is blocked until metrics exist.
Recommended promotion:
candidate -> evaluation -> clinical_review -> approved -> production -> retired.

## Shadow AI
The feature flag exists for controlled rollout. A full asynchronous shadow worker should compare a candidate model without returning its answer to clinicians.

## Disaster mode
If Ollama/LLM is unavailable, `/ai/query` returns 503 AI_UNAVAILABLE. Patient records, consultations and other CRM operations remain available.

## Before deploy
sh ops/preflight.sh

## After deploy
BASE_URL=https://your-domain.example sh ops/postdeploy-test.sh

## Explicitly not certified
The V3 package does not claim medical-device certification, legal compliance, clinical model validation, or a completed external penetration test.

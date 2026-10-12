# Production checklist

This repository is a full engineering reference, not clinical certification.

Before real deployment:
1. Replace all demo secrets and demo user.
2. Create a non-owner PostgreSQL application role; verify it cannot BYPASSRLS.
3. Run tenant A/B isolation tests for every tenant-scoped table and endpoint.
4. Separate patient identity/PII into a more restricted vault if required by your jurisdiction.
5. Configure encrypted object storage, backups, PITR, key rotation and disaster recovery.
6. Replace local hash embeddings with an approved real embedding model.
7. Configure a real LLM through the AI Gateway; add PII policy, prompt-injection defenses,
   output validation, grounded citation verification and model fallback.
8. Build a RAG evaluation set: Recall@K, MRR/NDCG, faithfulness, citation accuracy,
   unsupported-claim rate and leakage tests.
9. Replace `development_risk` with a validated training/inference pipeline. Record dataset version,
   features, calibration, AUROC/AUPRC, sensitivity/specificity, Brier score and subgroup evaluation.
10. Add real LangGraph StateGraph/checkpoint/interrupt/resume if autonomous tool orchestration is needed.
11. Add immutable/WORM external audit export; DB hash chaining detects tampering but does not stop a DB superuser.
12. Add OpenTelemetry, Prometheus/Grafana and error monitoring.
13. Threat model, dependency scanning, SAST/DAST, penetration test and incident response.
14. Legal/privacy/medical-device review for every country where the product will operate.
15. Never permit AI to autonomously diagnose, prescribe, change medication or execute high-risk clinical actions.

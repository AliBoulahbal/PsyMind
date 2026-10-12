# PsyMind V2 AI Complete

## Implemented in this edition
1. Connected clinical SaaS frontend.
2. PDF/DOCX/TXT upload to private MinIO.
3. SHA-256 duplicate detection.
4. Text extraction with page/section preservation where available.
5. Chunking with overlap and source hashes.
6. Pluggable 384-dimensional embeddings.
7. pgvector dense retrieval + PostgreSQL FTS + RRF.
8. Optional CrossEncoder reranking.
9. Ollama LLM provider with configurable model.
10. Grounded prompt contract and citation validation.
11. Baseline prompt-injection detection.
12. Human-in-the-loop action workflow.
13. Retrieval evaluation endpoint (Recall@8 / MRR).
14. AI usage and immutable-style hash-chain audit UI.
15. AI Governance Center.

## AI profiles

### Lightweight development
EMBEDDING_PROVIDER=hash
RERANKER_ENABLED=false
LLM_PROVIDER=mock

### Local semantic RAG
Install `requirements-ai.txt`, then:
EMBEDDING_PROVIDER=sentence_transformers
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
RERANKER_ENABLED=true
LLM_PROVIDER=ollama
OLLAMA_MODEL=gemma3:4b

Any embedding replacement MUST remain dimension 384 with the current schema, or the vector column/index must be migrated and the corpus re-embedded.

## OCR
Scanned PDFs with no extractable text are rejected with `422 OCR required`. This is intentional.
A production OCR worker (for example a validated OCR pipeline) should be asynchronous, sandboxed, resource-limited and evaluated on the actual document languages.

## Clinical safety boundary
AI can retrieve, summarize and propose. It must not autonomously diagnose, prescribe, alter medication, discharge, or execute other critical clinical actions.

## Recommended additions before real deployment
- patient identity vault with field-level encryption/KMS
- malware scanning for uploaded files
- asynchronous ingestion queue
- OCR worker
- external immutable/WORM audit sink
- OpenTelemetry/Prometheus/Grafana
- E2E tests
- PostgreSQL tenant A/B isolation suite
- adversarial prompt-injection suite
- clinical evaluation dataset
- model registry and promotion workflow
- subscription/plan enforcement
- SSO/MFA
- backup PITR and disaster-recovery exercises

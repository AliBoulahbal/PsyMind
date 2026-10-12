# PsyMind V2 Application Edition

## Implemented UI
- Authentication
- Operational dashboard
- Patient search/list/create
- Patient clinical record
- Consultation timeline
- Diagnoses/disease catalog
- Medication catalog
- Allergies
- Prescriptions with allergy conflict protection
- Documents/RAG view
- AI assistant with citations
- Risk view with explicit development warning
- HITL approvals
- Audit viewer
- AI usage viewer

## AI providers
`LLM_PROVIDER=mock` disables generation safely.
`LLM_PROVIDER=ollama` enables the Ollama provider.

Example:
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=gemma3:4b

The model name is configurable. A medical-tuned model can be evaluated without changing application code.

## Still required before real clinical production
- real document upload/extraction/OCR worker
- production semantic embeddings/reranker
- complete identity vault/encryption strategy
- validated risk model or keep risk feature disabled
- external immutable audit sink
- tenant isolation integration suite against PostgreSQL
- full E2E browser tests
- clinical/RAG evaluation dataset
- legal/privacy/medical-device assessment

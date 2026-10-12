from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import model_validator

class Settings(BaseSettings):
    app_name:str="PsyMind V3"
    environment:str="development"
    secret_key:str
    pii_encryption_key:str=""
    access_token_minutes:int=15
    refresh_token_days:int=7
    database_url:str
    redis_url:str
    minio_endpoint:str
    minio_access_key:str
    minio_secret_key:str
    minio_bucket:str="clinical-documents"
    llm_provider:str="mock"
    llm_api_key:str=""
    ollama_base_url:str="http://ollama:11434"
    ollama_model:str="gemma3:4b"
    embedding_provider:str="hash"
    embedding_model:str="sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"
    reranker_enabled:bool=False
    reranker_model:str="cross-encoder/ms-marco-MiniLM-L-6-v2"
    rag_top_k:int=8
    rag_candidate_k:int=20
    max_upload_mb:int=20
    cors_origins:str="http://localhost:3000"
    ai_fail_open:bool=True
    external_audit_url:str=""
    external_audit_token:str=""
    model_config=SettingsConfigDict(env_file=".env",extra="ignore")

    @model_validator(mode="after")
    def production_safety(self):
        if self.environment.lower() == "production":
            if len(self.secret_key) < 64 or "CHANGE" in self.secret_key.upper() or "REPLACE" in self.secret_key.upper():
                raise ValueError("Production SECRET_KEY must be a unique 64+ character secret")
            if "psymind_app" not in self.database_url:
                raise ValueError("Production DATABASE_URL must use the non-owner psymind_app role")
            if not self.pii_encryption_key or len(self.pii_encryption_key) < 40 or "CHANGE" in self.pii_encryption_key.upper():
                raise ValueError("A unique PII_ENCRYPTION_KEY is required in production")
            if self.llm_provider.lower() != "ollama":
                raise ValueError("Production requires LLM_PROVIDER=ollama; external/mock providers are disabled")
            if self.embedding_provider.lower() != "sentence_transformers":
                raise ValueError("Production requires local sentence_transformers embeddings; hash embeddings are development-only")
            if self.ai_fail_open:
                raise ValueError("AI_FAIL_OPEN must be false in production")
            if self.llm_api_key:
                raise ValueError("LLM_API_KEY must be empty for local-only AI deployments")
            if self.external_audit_url:
                raise ValueError("EXTERNAL_AUDIT_URL must be empty for local-only deployment unless explicitly reviewed")
        return self

@lru_cache
def get_settings(): return Settings()
settings=get_settings()

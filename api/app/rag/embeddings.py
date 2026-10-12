import hashlib, math
from functools import lru_cache
from app.core.config import settings

DIM=384

def _hash_embed(text:str)->list[float]:
    # Development-only deterministic fallback.
    v=[0.0]*DIM
    for token in text.lower().split():
        h=hashlib.sha256(token.encode()).digest()
        i=int.from_bytes(h[:4],"big")%DIM
        v[i]+=1 if h[4]%2 else -1
    n=math.sqrt(sum(x*x for x in v)) or 1.0
    return [x/n for x in v]

@lru_cache(maxsize=1)
def _st_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(settings.embedding_model)

def embed(text:str)->list[float]:
    if settings.embedding_provider=="sentence_transformers":
        vec=_st_model().encode(text,normalize_embeddings=True).tolist()
        if len(vec)!=DIM:
            raise RuntimeError(f"Embedding dimension {len(vec)} != PostgreSQL vector({DIM}). Use a 384-dimensional model or migrate schema.")
        return vec
    return _hash_embed(text)

def embed_many(texts:list[str])->list[list[float]]:
    if settings.embedding_provider=="sentence_transformers":
        arr=_st_model().encode(texts,normalize_embeddings=True)
        out=[x.tolist() for x in arr]
        if any(len(x)!=DIM for x in out):
            raise RuntimeError("Embedding model dimension mismatch; expected 384")
        return out
    return [_hash_embed(x) for x in texts]

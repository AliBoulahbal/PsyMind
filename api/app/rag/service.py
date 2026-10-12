from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.rag.embeddings import embed
from app.core.config import settings
from functools import lru_cache

@lru_cache(maxsize=1)
def _reranker():
    from sentence_transformers import CrossEncoder
    return CrossEncoder(settings.reranker_model)

async def hybrid_search(db:AsyncSession,tenant_id,patient_id,query:str,k:int=8):
    v=embed(query)
    sql=text('''
    WITH dense AS (
      SELECT id, document_id, page_number, section, content,
             row_number() OVER (ORDER BY embedding <=> CAST(:vec AS vector)) AS rank
      FROM clinical_chunks
      WHERE tenant_id=:tid AND patient_id=:pid AND embedding IS NOT NULL
      ORDER BY embedding <=> CAST(:vec AS vector) LIMIT 20
    ),
    lexical AS (
      SELECT id, document_id, page_number, section, content,
             row_number() OVER (ORDER BY ts_rank_cd(to_tsvector('simple',content), plainto_tsquery('simple',:q)) DESC) AS rank
      FROM clinical_chunks
      WHERE tenant_id=:tid AND patient_id=:pid
        AND to_tsvector('simple',content) @@ plainto_tsquery('simple',:q)
      LIMIT 20
    ),
    fused AS (
      SELECT COALESCE(d.id,l.id) id,
             COALESCE(d.document_id,l.document_id) document_id,
             COALESCE(d.page_number,l.page_number) page_number,
             COALESCE(d.section,l.section) section,
             COALESCE(d.content,l.content) content,
             COALESCE(1.0/(60+d.rank),0)+COALESCE(1.0/(60+l.rank),0) score
      FROM dense d FULL OUTER JOIN lexical l ON d.id=l.id
    )
    SELECT * FROM fused ORDER BY score DESC LIMIT :k
    ''')
    result=await db.execute(sql,{"vec":str(v),"tid":str(tenant_id),"pid":str(patient_id),"q":query,"k":k})
    rows=[dict(r._mapping) for r in result]
    if settings.reranker_enabled and rows:
        scores=_reranker().predict([(query,x["content"]) for x in rows])
        for row,score in zip(rows,scores): row["rerank_score"]=float(score)
        rows.sort(key=lambda x:x["rerank_score"],reverse=True)
    return rows[:k]

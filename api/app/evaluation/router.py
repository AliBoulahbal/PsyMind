from fastapi import APIRouter,Depends
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.deps import Principal,require
from app.rag.service import hybrid_search

router=APIRouter(prefix="/evaluation",tags=["evaluation"])

class RetrievalCase(BaseModel):
    patient_id:str
    query:str
    expected_document_ids:list[str]=[]

@router.post("/retrieval")
async def retrieval(case:RetrievalCase,p:Principal=Depends(require("patient.read")),db:AsyncSession=Depends(get_db)):
    hits=await hybrid_search(db,p.tenant_id,case.patient_id,case.query,k=8)
    got=[str(x["document_id"]) for x in hits]
    expected=set(case.expected_document_ids)
    recall=(len(expected.intersection(got))/len(expected)) if expected else None
    reciprocal_rank=0.0
    if expected:
        for i,d in enumerate(got,1):
            if d in expected: reciprocal_rank=1/i;break
    return {"retrieved":got,"expected":case.expected_document_ids,"recall_at_8":recall,"mrr":reciprocal_rank}

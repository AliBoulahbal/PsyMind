from datetime import datetime,timezone
from uuid import uuid4
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select,func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.deps import Principal,require
from app.models import Patient,AIUsage,Tenant,SecurityEvent
from app.schemas import ChatIn
from app.rag.service import hybrid_search
from app.ai.gateway import gateway
from app.ai.governance import inspect_prompt,validate_grounding
from app.core.config import settings

router=APIRouter(prefix="/ai",tags=["ai"])

@router.post("/query")
async def query(data:ChatIn,p:Principal=Depends(require("clinical.ai.query")),db:AsyncSession=Depends(get_db)):
    guard=inspect_prompt(data.question)
    if not guard.allowed:
        db.add(SecurityEvent(tenant_id=p.tenant_id,user_id=p.user_id,event_type="prompt_injection",severity="warning",payload={"reasons":guard.reasons}))
        await db.commit()
        raise HTTPException(400,{"code":"PROMPT_BLOCKED","reasons":guard.reasons})
    patient=(await db.execute(select(Patient).where(Patient.id==data.patient_id,Patient.tenant_id==p.tenant_id))).scalar_one_or_none()
    if not patient: raise HTTPException(404,"Patient not found")
    tenant=(await db.execute(select(Tenant).where(Tenant.id==p.tenant_id))).scalar_one()
    used=(await db.execute(select(func.coalesce(func.sum(AIUsage.input_tokens+AIUsage.output_tokens),0)).where(AIUsage.tenant_id==p.tenant_id))).scalar_one()
    if used>=tenant.monthly_ai_quota: raise HTTPException(429,"Monthly AI quota exceeded")
    chunks=await hybrid_search(db,p.tenant_id,data.patient_id,data.question,k=settings.rag_top_k)
    try:
        result=await gateway.answer(data.question,chunks)
    except Exception:
        # Fail closed: never substitute mock or remote AI when local inference is unavailable.
        raise HTTPException(503, {"code": "AI_UNAVAILABLE",
                                  "message": "Local AI is temporarily unavailable. Clinical records remain available."})
    grounding = validate_grounding(result.answer, chunks)
    safe_answer = result.answer if grounding.allowed else (
        "La réponse générée n'a pas pu être reliée de manière vérifiable aux sources retrouvées. "
        "Aucune conclusion clinique ne doit être tirée de cette réponse ; vérifiez directement le dossier et les sources."
    )
    request_id=str(uuid4())
    db.add(AIUsage(tenant_id=p.tenant_id,user_id=p.user_id,provider=result.provider,model=result.model,
                   input_tokens=result.input_tokens,output_tokens=result.output_tokens,latency_ms=result.latency_ms,
                   estimated_cost=0,request_id=request_id,created_at=datetime.now(timezone.utc)))
    await db.commit()
    return {"request_id":request_id,"answer":safe_answer,"grounded":grounding.allowed,
            "governance_reasons":grounding.reasons,
            "citations":[{"document_id":str(c["document_id"]),"page":c["page_number"],"section":c["section"],"chunk_id":str(c["id"])} for c in chunks]}

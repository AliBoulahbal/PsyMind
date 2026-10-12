from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.session import get_db
from app.deps import Principal,require
from app.models import ModelRegistry,FeatureFlag,KnowledgeDocument,EvaluationRun,AIFeedback
from app.audit.service import audit

router=APIRouter(prefix="/governance",tags=["governance"])

class ModelIn(BaseModel):
    name:str; provider:str; model_ref:str; purpose:str="generation"; config:dict={}
class FlagIn(BaseModel):
    enabled:bool; config:dict={}
class KnowledgeIn(BaseModel):
    title:str; version:str; source:str|None=None; effective_from:str|None=None; expires_on:str|None=None
class FeedbackIn(BaseModel):
    request_id:str; rating:str; note:str|None=None

@router.get("/models")
async def models(p:Principal=Depends(require("governance.read")),db:AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(ModelRegistry).where(ModelRegistry.tenant_id==p.tenant_id).order_by(ModelRegistry.created_at.desc()))).scalars().all()
    return [{"id":x.id,"name":x.name,"provider":x.provider,"model_ref":x.model_ref,"purpose":x.purpose,"status":x.status,"config":x.config,"metrics":x.metrics} for x in rows]

@router.post("/models")
async def add_model(data:ModelIn,p:Principal=Depends(require("governance.write")),db:AsyncSession=Depends(get_db)):
    row=ModelRegistry(tenant_id=p.tenant_id,**data.model_dump());db.add(row);await db.flush()
    await audit(db,p.tenant_id,p.user_id,"model.register","model_registry",row.id);await db.commit()
    return {"id":row.id,"status":row.status}

@router.post("/models/{model_id}/approve")
async def approve(model_id:UUID,p:Principal=Depends(require("governance.approve")),db:AsyncSession=Depends(get_db)):
    row=(await db.execute(select(ModelRegistry).where(ModelRegistry.id==model_id,ModelRegistry.tenant_id==p.tenant_id))).scalar_one_or_none()
    if not row: raise HTTPException(404,"Model not found")
    if not row.metrics: raise HTTPException(409,"Model cannot be approved without evaluation metrics")
    row.status="approved";row.approved_by=p.user_id
    await audit(db,p.tenant_id,p.user_id,"model.approve","model_registry",row.id,{"metrics":row.metrics});await db.commit()
    return {"status":"approved"}

@router.get("/flags")
async def flags(p:Principal=Depends(require("governance.read")),db:AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(FeatureFlag).where(FeatureFlag.tenant_id==p.tenant_id))).scalars().all()
    return [{"key":x.key,"enabled":x.enabled,"config":x.config} for x in rows]

@router.put("/flags/{key}")
async def set_flag(key:str,data:FlagIn,p:Principal=Depends(require("governance.write")),db:AsyncSession=Depends(get_db)):
    row=(await db.execute(select(FeatureFlag).where(FeatureFlag.tenant_id==p.tenant_id,FeatureFlag.key==key))).scalar_one_or_none()
    if row: row.enabled=data.enabled;row.config=data.config
    else: db.add(FeatureFlag(tenant_id=p.tenant_id,key=key,enabled=data.enabled,config=data.config))
    await audit(db,p.tenant_id,p.user_id,"feature_flag.change","feature_flag",key,data.model_dump());await db.commit()
    return {"key":key,**data.model_dump()}

@router.get("/knowledge")
async def knowledge(p:Principal=Depends(require("governance.read")),db:AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(KnowledgeDocument).where(KnowledgeDocument.tenant_id==p.tenant_id).order_by(KnowledgeDocument.created_at.desc()))).scalars().all()
    return [{"id":x.id,"title":x.title,"version":x.version,"status":x.status,"source":x.source,"effective_from":x.effective_from,"expires_on":x.expires_on} for x in rows]

@router.post("/feedback")
async def feedback(data:FeedbackIn,p:Principal=Depends(require("clinical.ai.query")),db:AsyncSession=Depends(get_db)):
    if data.rating not in {"useful","incorrect","unsupported","dangerous"}: raise HTTPException(422,"Invalid rating")
    row=AIFeedback(tenant_id=p.tenant_id,user_id=p.user_id,**data.model_dump());db.add(row)
    await audit(db,p.tenant_id,p.user_id,"ai.feedback","ai_request",data.request_id,{"rating":data.rating});await db.commit()
    return {"status":"recorded"}

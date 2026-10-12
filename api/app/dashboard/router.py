from fastapi import APIRouter,Depends
from sqlalchemy import select,func
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.deps import Principal,require
from app.models import Patient,Consultation,Prescription,PatientDiagnosis,AgentRun,AIUsage,AuditLog,Tenant,User

router=APIRouter(prefix="/dashboard",tags=["dashboard"])

@router.get("/summary")
async def summary(p:Principal=Depends(require("patient.read")),db:AsyncSession=Depends(get_db)):
    async def count(model):
        return (await db.execute(select(func.count()).select_from(model).where(model.tenant_id==p.tenant_id))).scalar_one()
    patients=await count(Patient)
    consultations=await count(Consultation)
    prescriptions=await count(Prescription)
    diagnoses=await count(PatientDiagnosis)
    pending=(await db.execute(select(func.count()).select_from(AgentRun).where(AgentRun.tenant_id==p.tenant_id,AgentRun.status=="pending_approval"))).scalar_one()
    usage=(await db.execute(select(func.coalesce(func.sum(AIUsage.input_tokens+AIUsage.output_tokens),0)).where(AIUsage.tenant_id==p.tenant_id))).scalar_one()
    tenant=(await db.execute(select(Tenant).where(Tenant.id==p.tenant_id))).scalar_one()
    return {"patients":patients,"consultations":consultations,"prescriptions":prescriptions,
            "diagnoses":diagnoses,"pending_approvals":pending,"ai_tokens":usage,
            "ai_quota":tenant.monthly_ai_quota,"tenant_name":tenant.name}

@router.get("/audit")
async def audits(p:Principal=Depends(require("patient.read")),db:AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(AuditLog).where(AuditLog.tenant_id==p.tenant_id).order_by(AuditLog.created_at.desc()).limit(100))).scalars().all()
    return [{"id":x.id,"action":x.action,"resource_type":x.resource_type,"resource_id":x.resource_id,
             "actor_id":x.actor_id,"created_at":x.created_at,"event_hash":x.event_hash} for x in rows]

@router.get("/ai-usage")
async def ai_usage(p:Principal=Depends(require("patient.read")),db:AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(AIUsage).where(AIUsage.tenant_id==p.tenant_id).order_by(AIUsage.created_at.desc()).limit(100))).scalars().all()
    return [{"id":x.id,"provider":x.provider,"model":x.model,"input_tokens":x.input_tokens,
             "output_tokens":x.output_tokens,"latency_ms":x.latency_ms,"estimated_cost":x.estimated_cost,
             "request_id":x.request_id,"created_at":x.created_at} for x in rows]

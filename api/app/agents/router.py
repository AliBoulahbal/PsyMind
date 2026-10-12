from uuid import UUID
from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.deps import Principal,require
from app.models import AgentRun,Patient
from app.schemas import AgentIn,DecisionIn
from app.audit.service import audit
router=APIRouter(prefix="/agents",tags=["agents"])


@router.get("")
async def list_runs(p:Principal=Depends(require("patient.read")),db:AsyncSession=Depends(get_db)):
    rows=(await db.execute(select(AgentRun).where(AgentRun.tenant_id==p.tenant_id).order_by(AgentRun.created_at.desc()).limit(100))).scalars().all()
    return [{"id":x.id,"patient_id":x.patient_id,"action":x.action,"payload":x.payload,"status":x.status,
             "requested_by":x.requested_by,"decision_by":x.decision_by,"decision_note":x.decision_note,
             "created_at":x.created_at} for x in rows]

@router.post("/propose")
async def propose(data:AgentIn,p:Principal=Depends(require("agent.propose")),db:AsyncSession=Depends(get_db)):
    patient=(await db.execute(select(Patient).where(Patient.id==data.patient_id,Patient.tenant_id==p.tenant_id))).scalar_one_or_none()
    if not patient: raise HTTPException(404,"Patient not found")
    row=AgentRun(tenant_id=p.tenant_id,patient_id=data.patient_id,requested_by=p.user_id,action=data.action,payload=data.payload,status="pending_approval")
    db.add(row); await db.flush(); await audit(db,p.tenant_id,p.user_id,"agent.propose","agent_run",row.id,{"action":data.action}); await db.commit()
    return {"id":row.id,"status":row.status}

@router.post("/{run_id}/approve")
async def approve(run_id:UUID,data:DecisionIn,p:Principal=Depends(require("approve.ai_action")),db:AsyncSession=Depends(get_db)):
    row=(await db.execute(select(AgentRun).where(AgentRun.id==run_id,AgentRun.tenant_id==p.tenant_id))).scalar_one_or_none()
    if not row or row.status!="pending_approval": raise HTTPException(409,"Run not pending")
    row.status="approved"; row.decision_by=p.user_id; row.decision_note=data.note
    await audit(db,p.tenant_id,p.user_id,"agent.approve","agent_run",row.id); await db.commit()
    return {"id":row.id,"status":row.status}

@router.post("/{run_id}/reject")
async def reject(run_id:UUID,data:DecisionIn,p:Principal=Depends(require("approve.ai_action")),db:AsyncSession=Depends(get_db)):
    row=(await db.execute(select(AgentRun).where(AgentRun.id==run_id,AgentRun.tenant_id==p.tenant_id))).scalar_one_or_none()
    if not row or row.status!="pending_approval": raise HTTPException(409,"Run not pending")
    row.status="rejected"; row.decision_by=p.user_id; row.decision_note=data.note
    await audit(db,p.tenant_id,p.user_id,"agent.reject","agent_run",row.id); await db.commit()
    return {"id":row.id,"status":row.status}

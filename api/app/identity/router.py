from fastapi import APIRouter,Depends,HTTPException
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.session import get_db
from app.deps import Principal,require
from app.models import Patient,PatientIdentity
from app.identity.crypto import encrypt_identity,decrypt_identity
from app.audit.service import audit

router=APIRouter(prefix="/identity",tags=["identity"])
class IdentityIn(BaseModel):
    legal_name:str
    birth_date:str|None=None
    phone:str|None=None
    email:str|None=None
    address:str|None=None

@router.put("/patients/{patient_id}")
async def put_identity(patient_id:UUID,data:IdentityIn,p:Principal=Depends(require("pii.write")),db:AsyncSession=Depends(get_db)):
    patient=(await db.execute(select(Patient).where(Patient.id==patient_id,Patient.tenant_id==p.tenant_id))).scalar_one_or_none()
    if not patient: raise HTTPException(404,"Patient not found")
    row=(await db.execute(select(PatientIdentity).where(PatientIdentity.patient_id==patient_id,PatientIdentity.tenant_id==p.tenant_id))).scalar_one_or_none()
    enc=encrypt_identity(data.model_dump())
    if row: row.encrypted_payload=enc
    else:
        row=PatientIdentity(tenant_id=p.tenant_id,patient_id=patient_id,encrypted_payload=enc,key_version="v1");db.add(row)
    patient.identity_ref=str(patient_id)
    await audit(db,p.tenant_id,p.user_id,"pii.update","patient_identity",patient_id)
    await db.commit();return {"status":"stored","key_version":"v1"}

@router.get("/patients/{patient_id}")
async def get_identity(patient_id:UUID,p:Principal=Depends(require("pii.read")),db:AsyncSession=Depends(get_db)):
    row=(await db.execute(select(PatientIdentity).where(PatientIdentity.patient_id==patient_id,PatientIdentity.tenant_id==p.tenant_id))).scalar_one_or_none()
    if not row: raise HTTPException(404,"Identity not found")
    await audit(db,p.tenant_id,p.user_id,"pii.read","patient_identity",patient_id)
    await db.commit()
    return {"patient_id":patient_id,"identity":decrypt_identity(row.encrypted_payload),"key_version":row.key_version}

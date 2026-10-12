from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.session import get_db
from app.deps import Principal, require
from app.models import Patient,Disease,PatientDiagnosis,Medication,Prescription,Allergy
from app.schemas import DiseaseIn,DiagnosisIn,MedicationIn,PrescriptionIn,AllergyIn
from app.audit.service import audit
router=APIRouter(prefix="/clinical",tags=["clinical"])

@router.get("/diseases")
async def diseases(q:str|None=None,p:Principal=Depends(require("patient.read")),db:AsyncSession=Depends(get_db)):
    stmt=select(Disease).order_by(Disease.name)
    if q: stmt=stmt.where(Disease.name.ilike(f"%{q}%"))
    rows=(await db.execute(stmt.limit(100))).scalars().all()
    return [{"id":x.id,"code":x.code,"name":x.name,"coding_system":x.coding_system} for x in rows]

@router.post("/diseases")
async def create_disease(data:DiseaseIn,p:Principal=Depends(require("catalog.manage")),db:AsyncSession=Depends(get_db)):
    row=Disease(**data.model_dump()); db.add(row); await db.commit(); await db.refresh(row); return {"id":row.id}

@router.post("/patients/{patient_id}/diagnoses")
async def diagnose(patient_id:UUID,data:DiagnosisIn,p:Principal=Depends(require("diagnosis.write")),db:AsyncSession=Depends(get_db)):
    patient=(await db.execute(select(Patient).where(Patient.id==patient_id,Patient.tenant_id==p.tenant_id))).scalar_one_or_none()
    disease=await db.get(Disease,data.disease_id)
    if not patient or not disease: raise HTTPException(404,"Patient or disease not found")
    row=PatientDiagnosis(tenant_id=p.tenant_id,patient_id=patient_id,diagnosed_by=p.user_id,**data.model_dump())
    db.add(row); await db.flush(); await audit(db,p.tenant_id,p.user_id,"diagnosis.create","diagnosis",row.id,{"disease_id":str(data.disease_id)})
    await db.commit(); return {"id":row.id}

@router.get("/medications")
async def medications(q:str|None=None,p:Principal=Depends(require("patient.read")),db:AsyncSession=Depends(get_db)):
    stmt=select(Medication).order_by(Medication.generic_name)
    if q: stmt=stmt.where(Medication.generic_name.ilike(f"%{q}%"))
    rows=(await db.execute(stmt.limit(100))).scalars().all()
    return [{"id":x.id,"code":x.code,"generic_name":x.generic_name,"brand_name":x.brand_name,"strength":x.strength} for x in rows]

@router.post("/medications")
async def create_medication(data:MedicationIn,p:Principal=Depends(require("catalog.manage")),db:AsyncSession=Depends(get_db)):
    row=Medication(**data.model_dump()); db.add(row); await db.commit(); await db.refresh(row); return {"id":row.id}

@router.post("/patients/{patient_id}/allergies")
async def add_allergy(patient_id:UUID,data:AllergyIn,p:Principal=Depends(require("prescription.write")),db:AsyncSession=Depends(get_db)):
    patient=(await db.execute(select(Patient).where(Patient.id==patient_id,Patient.tenant_id==p.tenant_id))).scalar_one_or_none()
    if not patient: raise HTTPException(404,"Patient not found")
    row=Allergy(tenant_id=p.tenant_id,patient_id=patient_id,**data.model_dump()); db.add(row); await db.flush()
    await audit(db,p.tenant_id,p.user_id,"allergy.create","allergy",row.id); await db.commit(); return {"id":row.id}

@router.post("/patients/{patient_id}/prescriptions")
async def prescribe(patient_id:UUID,data:PrescriptionIn,p:Principal=Depends(require("prescription.write")),db:AsyncSession=Depends(get_db)):
    patient=(await db.execute(select(Patient).where(Patient.id==patient_id,Patient.tenant_id==p.tenant_id))).scalar_one_or_none()
    med=await db.get(Medication,data.medication_id)
    if not patient or not med: raise HTTPException(404,"Patient or medication not found")
    allergies=(await db.execute(select(Allergy).where(Allergy.tenant_id==p.tenant_id,Allergy.patient_id==patient_id,
                                                     Allergy.medication_id==data.medication_id))).scalars().all()
    if allergies: raise HTTPException(409,"Medication matches a recorded patient allergy; clinician review required")
    row=Prescription(tenant_id=p.tenant_id,patient_id=patient_id,prescribed_by=p.user_id,**data.model_dump())
    db.add(row); await db.flush(); await audit(db,p.tenant_id,p.user_id,"prescription.create","prescription",row.id,{"medication_id":str(data.medication_id)})
    await db.commit(); return {"id":row.id,"status":row.status}

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.session import get_db
from app.deps import Principal, require
from app.models import Patient, Consultation, PatientDiagnosis, Disease, Prescription, Medication, Allergy, ClinicalDocument, RiskPrediction
from app.schemas import PatientIn, ConsultationIn
from app.audit.service import audit

router=APIRouter(prefix="/patients", tags=["patients"])

def patient_dict(r):
    return {"id":r.id,"file_number":r.file_number,"display_name":r.display_name,
            "birth_date":r.birth_date,"sex":r.sex,"status":r.status,"created_at":r.created_at}

@router.get("")
async def list_patients(q:str|None=None,p:Principal=Depends(require("patient.read")), db:AsyncSession=Depends(get_db)):
    stmt=select(Patient).where(Patient.tenant_id==p.tenant_id)
    if q:
        stmt=stmt.where((Patient.display_name.ilike(f"%{q}%")) | (Patient.file_number.ilike(f"%{q}%")))
    rows=(await db.execute(stmt.order_by(Patient.created_at.desc()).limit(250))).scalars().all()
    return [patient_dict(r) for r in rows]

@router.get("/{patient_id}")
async def get_patient(patient_id:UUID,p:Principal=Depends(require("patient.read")),db:AsyncSession=Depends(get_db)):
    row=(await db.execute(select(Patient).where(Patient.id==patient_id,Patient.tenant_id==p.tenant_id))).scalar_one_or_none()
    if not row: raise HTTPException(404,"Patient not found")
    return patient_dict(row)

@router.post("")
async def create_patient(data:PatientIn,p:Principal=Depends(require("patient.write")),db:AsyncSession=Depends(get_db)):
    row=Patient(tenant_id=p.tenant_id,**data.model_dump())
    db.add(row); await db.flush()
    await audit(db,p.tenant_id,p.user_id,"patient.create","patient",row.id)
    await db.commit(); await db.refresh(row)
    return patient_dict(row)

@router.get("/{patient_id}/timeline")
async def timeline(patient_id:UUID,p:Principal=Depends(require("patient.read")),db:AsyncSession=Depends(get_db)):
    patient=(await db.execute(select(Patient).where(Patient.id==patient_id,Patient.tenant_id==p.tenant_id))).scalar_one_or_none()
    if not patient: raise HTTPException(404,"Patient not found")
    cons=(await db.execute(select(Consultation).where(Consultation.patient_id==patient_id,Consultation.tenant_id==p.tenant_id).order_by(Consultation.occurred_at.desc()))).scalars().all()
    dx=(await db.execute(select(PatientDiagnosis,Disease).join(Disease,Disease.id==PatientDiagnosis.disease_id).where(PatientDiagnosis.patient_id==patient_id,PatientDiagnosis.tenant_id==p.tenant_id).order_by(PatientDiagnosis.diagnosed_on.desc()))).all()
    rx=(await db.execute(select(Prescription,Medication).join(Medication,Medication.id==Prescription.medication_id).where(Prescription.patient_id==patient_id,Prescription.tenant_id==p.tenant_id).order_by(Prescription.start_date.desc()))).all()
    allergies=(await db.execute(select(Allergy).where(Allergy.patient_id==patient_id,Allergy.tenant_id==p.tenant_id))).scalars().all()
    docs=(await db.execute(select(ClinicalDocument).where(ClinicalDocument.patient_id==patient_id,ClinicalDocument.tenant_id==p.tenant_id).order_by(ClinicalDocument.created_at.desc()))).scalars().all()
    risks=(await db.execute(select(RiskPrediction).where(RiskPrediction.patient_id==patient_id,RiskPrediction.tenant_id==p.tenant_id).order_by(RiskPrediction.created_at.desc()).limit(10))).scalars().all()
    return {
      "patient":patient_dict(patient),
      "consultations":[{"id":x.id,"note":x.note,"occurred_at":x.occurred_at,"clinician_id":x.clinician_id} for x in cons],
      "diagnoses":[{"id":x.id,"disease_id":d.id,"disease":d.name,"code":d.code,"status":x.status,"certainty":x.certainty,"diagnosed_on":x.diagnosed_on,"notes":x.notes} for x,d in dx],
      "prescriptions":[{"id":x.id,"medication_id":m.id,"medication":m.generic_name,"strength":m.strength,"dose":x.dose,"route":x.route,"frequency":x.frequency,"start_date":x.start_date,"end_date":x.end_date,"status":x.status,"instructions":x.instructions} for x,m in rx],
      "allergies":[{"id":x.id,"substance":x.substance,"reaction":x.reaction,"severity":x.severity,"medication_id":x.medication_id} for x in allergies],
      "documents":[{"id":x.id,"title":x.title,"mime_type":x.mime_type,"sha256":x.sha256,"created_at":x.created_at} for x in docs],
      "risks":[{"id":x.id,"score":x.score,"level":x.level,"model_version":x.model_version,"explanation":x.explanation,"created_at":x.created_at} for x in risks]
    }

@router.post("/{patient_id}/consultations")
async def consultation(patient_id:UUID,data:ConsultationIn,p:Principal=Depends(require("consultation.write")),db:AsyncSession=Depends(get_db)):
    patient=(await db.execute(select(Patient).where(Patient.id==patient_id,Patient.tenant_id==p.tenant_id))).scalar_one_or_none()
    if not patient: raise HTTPException(404,"Patient not found")
    row=Consultation(tenant_id=p.tenant_id,patient_id=patient_id,clinician_id=p.user_id,**data.model_dump())
    db.add(row); await db.flush()
    await audit(db,p.tenant_id,p.user_id,"consultation.create","consultation",row.id)
    await db.commit()
    return {"id":row.id}

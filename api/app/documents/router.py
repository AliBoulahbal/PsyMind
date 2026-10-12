from fastapi import APIRouter,Depends,File,Form,HTTPException,UploadFile
from sqlalchemy import select,delete
from sqlalchemy.ext.asyncio import AsyncSession
from uuid import UUID
from app.db.session import get_db
from app.deps import Principal,require
from app.models import Patient,ClinicalDocument,ClinicalChunk
from app.documents.service import extract,prepare_chunks,sha256_bytes
from app.documents.storage import put_bytes
from app.audit.service import audit
from app.core.config import settings

router=APIRouter(prefix="/documents",tags=["documents"])

@router.post("/patients/{patient_id}/upload")
async def upload(patient_id:UUID,file:UploadFile=File(...),title:str|None=Form(None),
                 p:Principal=Depends(require("patient.write")),db:AsyncSession=Depends(get_db)):
    patient=(await db.execute(select(Patient).where(Patient.id==patient_id,Patient.tenant_id==p.tenant_id))).scalar_one_or_none()
    if not patient: raise HTTPException(404,"Patient not found")
    data=await file.read()
    if len(data)>settings.max_upload_mb*1024*1024: raise HTTPException(413,"Document too large")
    try: pieces=extract(data,file.content_type or "",file.filename or "document")
    except ValueError as e: raise HTTPException(415,str(e))
    if not pieces:
        raise HTTPException(422,"No extractable text. The PDF may be scanned and requires an OCR worker.")
    sha=sha256_bytes(data)
    existing=(await db.execute(select(ClinicalDocument).where(ClinicalDocument.tenant_id==p.tenant_id,ClinicalDocument.patient_id==patient_id,ClinicalDocument.sha256==sha))).scalar_one_or_none()
    if existing: raise HTTPException(409,"This exact document is already attached to the patient")
    row=ClinicalDocument(tenant_id=p.tenant_id,patient_id=patient_id,title=title or file.filename or "Document",
                         object_key="pending",sha256=sha,mime_type=file.content_type or "application/octet-stream")
    db.add(row);await db.flush()
    key=f"{p.tenant_id}/{patient_id}/{row.id}/{file.filename or 'document'}"
    put_bytes(key,data,row.mime_type);row.object_key=key
    chunks=prepare_chunks(pieces)
    for i,c in enumerate(chunks):
        db.add(ClinicalChunk(tenant_id=p.tenant_id,patient_id=patient_id,document_id=row.id,chunk_index=i,**c))
    await audit(db,p.tenant_id,p.user_id,"document.ingest","clinical_document",row.id,
                {"filename":file.filename,"sha256":sha,"chunks":len(chunks)})
    await db.commit()
    return {"id":row.id,"title":row.title,"sha256":sha,"chunks":len(chunks),"pages_with_text":len(pieces)}

@router.delete("/{document_id}")
async def remove(document_id:UUID,p:Principal=Depends(require("patient.write")),db:AsyncSession=Depends(get_db)):
    doc=(await db.execute(select(ClinicalDocument).where(ClinicalDocument.id==document_id,ClinicalDocument.tenant_id==p.tenant_id))).scalar_one_or_none()
    if not doc: raise HTTPException(404,"Document not found")
    await db.execute(delete(ClinicalChunk).where(ClinicalChunk.document_id==document_id,ClinicalChunk.tenant_id==p.tenant_id))
    await db.delete(doc);await audit(db,p.tenant_id,p.user_id,"document.delete","clinical_document",document_id)
    await db.commit();return {"status":"deleted"}

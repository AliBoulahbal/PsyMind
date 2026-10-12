from datetime import date, datetime
from uuid import UUID
from pydantic import BaseModel, EmailStr, Field

class LoginIn(BaseModel):
    tenant_slug: str
    email: str
    password: str

class TokenOut(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"

class PatientIn(BaseModel):
    file_number: str
    display_name: str
    birth_date: date|None = None
    sex: str|None = None

class DiseaseIn(BaseModel):
    code: str
    name: str
    description: str|None = None
    coding_system: str = "LOCAL"

class DiagnosisIn(BaseModel):
    disease_id: UUID
    status: str = "active"
    certainty: str = "confirmed"
    diagnosed_on: date
    notes: str|None = None

class MedicationIn(BaseModel):
    code: str
    generic_name: str
    brand_name: str|None = None
    form: str|None = None
    strength: str|None = None
    description: str|None = None

class PrescriptionIn(BaseModel):
    medication_id: UUID
    dose: str
    route: str
    frequency: str
    start_date: date
    end_date: date|None = None
    instructions: str|None = None

class AllergyIn(BaseModel):
    medication_id: UUID|None = None
    substance: str
    reaction: str|None = None
    severity: str = "unknown"

class ConsultationIn(BaseModel):
    note: str
    occurred_at: datetime

class ChatIn(BaseModel):
    patient_id: UUID
    question: str = Field(min_length=3, max_length=4000)

class AgentIn(BaseModel):
    patient_id: UUID
    action: str
    payload: dict = {}

class DecisionIn(BaseModel):
    note: str|None = None

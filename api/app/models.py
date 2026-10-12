from datetime import date, datetime
from uuid import UUID
from sqlalchemy import String, Text, Boolean, Date, DateTime, ForeignKey, Integer, Float, JSON, UniqueConstraint, Index
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from pgvector.sqlalchemy import Vector
from app.db.base import Base, UUIDMixin, TimestampMixin

class Tenant(UUIDMixin, TimestampMixin, Base):
    __tablename__="tenants"
    slug: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(200))
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    monthly_ai_quota: Mapped[int] = mapped_column(Integer, default=10000)

class User(UUIDMixin, TimestampMixin, Base):
    __tablename__="users"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    email: Mapped[str] = mapped_column(String(320), index=True)
    password_hash: Mapped[str] = mapped_column(Text)
    full_name: Mapped[str] = mapped_column(String(200))
    role: Mapped[str] = mapped_column(String(50), default="clinician")
    permissions: Mapped[list] = mapped_column(JSON, default=list)
    active: Mapped[bool] = mapped_column(Boolean, default=True)
    __table_args__=(UniqueConstraint("tenant_id","email"),)

class Patient(UUIDMixin, TimestampMixin, Base):
    __tablename__="patients"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    file_number: Mapped[str] = mapped_column(String(80))
    identity_ref: Mapped[str|None] = mapped_column(String(120), nullable=True)
    display_name: Mapped[str] = mapped_column(String(200))
    birth_date: Mapped[date|None] = mapped_column(Date, nullable=True)
    sex: Mapped[str|None] = mapped_column(String(30), nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="active")
    __table_args__=(UniqueConstraint("tenant_id","file_number"),)

class Consultation(UUIDMixin, TimestampMixin, Base):
    __tablename__="consultations"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    patient_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("patients.id"), index=True)
    clinician_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    note: Mapped[str] = mapped_column(Text)
    occurred_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class Disease(UUIDMixin, TimestampMixin, Base):
    __tablename__="diseases"
    code: Mapped[str] = mapped_column(String(50), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(250), index=True)
    description: Mapped[str|None] = mapped_column(Text, nullable=True)
    coding_system: Mapped[str] = mapped_column(String(30), default="LOCAL")

class PatientDiagnosis(UUIDMixin, TimestampMixin, Base):
    __tablename__="patient_diagnoses"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    patient_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("patients.id"), index=True)
    disease_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("diseases.id"))
    diagnosed_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    status: Mapped[str] = mapped_column(String(30), default="active")
    certainty: Mapped[str] = mapped_column(String(30), default="confirmed")
    diagnosed_on: Mapped[date] = mapped_column(Date)
    notes: Mapped[str|None] = mapped_column(Text, nullable=True)

class Medication(UUIDMixin, TimestampMixin, Base):
    __tablename__="medications"
    code: Mapped[str] = mapped_column(String(80), unique=True, index=True)
    generic_name: Mapped[str] = mapped_column(String(250), index=True)
    brand_name: Mapped[str|None] = mapped_column(String(250), nullable=True)
    form: Mapped[str|None] = mapped_column(String(100), nullable=True)
    strength: Mapped[str|None] = mapped_column(String(100), nullable=True)
    description: Mapped[str|None] = mapped_column(Text, nullable=True)

class Allergy(UUIDMixin, TimestampMixin, Base):
    __tablename__="allergies"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    patient_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("patients.id"), index=True)
    medication_id: Mapped[UUID|None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("medications.id"), nullable=True)
    substance: Mapped[str] = mapped_column(String(250))
    reaction: Mapped[str|None] = mapped_column(Text, nullable=True)
    severity: Mapped[str] = mapped_column(String(30), default="unknown")

class Prescription(UUIDMixin, TimestampMixin, Base):
    __tablename__="prescriptions"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    patient_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("patients.id"), index=True)
    medication_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("medications.id"))
    prescribed_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    dose: Mapped[str] = mapped_column(String(100))
    route: Mapped[str] = mapped_column(String(100))
    frequency: Mapped[str] = mapped_column(String(100))
    start_date: Mapped[date] = mapped_column(Date)
    end_date: Mapped[date|None] = mapped_column(Date, nullable=True)
    instructions: Mapped[str|None] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(String(30), default="active")

class ClinicalDocument(UUIDMixin, TimestampMixin, Base):
    __tablename__="clinical_documents"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    patient_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("patients.id"), index=True)
    title: Mapped[str] = mapped_column(String(300))
    object_key: Mapped[str] = mapped_column(String(500))
    sha256: Mapped[str] = mapped_column(String(64))
    mime_type: Mapped[str] = mapped_column(String(120))

class ClinicalChunk(UUIDMixin, TimestampMixin, Base):
    __tablename__="clinical_chunks"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    patient_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("patients.id"), index=True)
    document_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("clinical_documents.id"), index=True)
    page_number: Mapped[int|None] = mapped_column(Integer, nullable=True)
    section: Mapped[str|None] = mapped_column(String(300), nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    content: Mapped[str] = mapped_column(Text)
    embedding: Mapped[list|None] = mapped_column(Vector(384), nullable=True)
    source_hash: Mapped[str] = mapped_column(String(64))
    __table_args__=(UniqueConstraint("document_id","chunk_index"),)

class RiskPrediction(UUIDMixin, TimestampMixin, Base):
    __tablename__="risk_predictions"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    patient_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("patients.id"), index=True)
    score: Mapped[float] = mapped_column(Float)
    level: Mapped[str] = mapped_column(String(30))
    model_version: Mapped[str] = mapped_column(String(100))
    explanation: Mapped[dict] = mapped_column(JSON)
    data_freshness: Mapped[dict] = mapped_column(JSON, default=dict)
    reviewed_by: Mapped[UUID|None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

class AgentRun(UUIDMixin, TimestampMixin, Base):
    __tablename__="agent_runs"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    patient_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("patients.id"), index=True)
    requested_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(String(100))
    payload: Mapped[dict] = mapped_column(JSON)
    status: Mapped[str] = mapped_column(String(30), default="pending_approval")
    decision_by: Mapped[UUID|None] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"), nullable=True)
    decision_note: Mapped[str|None] = mapped_column(Text, nullable=True)

class AuditLog(UUIDMixin, Base):
    __tablename__="audit_logs"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    actor_id: Mapped[UUID|None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    action: Mapped[str] = mapped_column(String(120))
    resource_type: Mapped[str] = mapped_column(String(120))
    resource_id: Mapped[str|None] = mapped_column(String(120), nullable=True)
    payload: Mapped[dict] = mapped_column(JSON, default=dict)
    prev_hash: Mapped[str|None] = mapped_column(String(64), nullable=True)
    event_hash: Mapped[str] = mapped_column(String(64))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))

class AIUsage(UUIDMixin, Base):
    __tablename__="ai_usage"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    provider: Mapped[str] = mapped_column(String(80))
    model: Mapped[str] = mapped_column(String(120))
    input_tokens: Mapped[int] = mapped_column(Integer, default=0)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0)
    latency_ms: Mapped[int] = mapped_column(Integer, default=0)
    estimated_cost: Mapped[float] = mapped_column(Float, default=0)
    request_id: Mapped[str] = mapped_column(String(100))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


class PatientIdentity(UUIDMixin, TimestampMixin, Base):
    __tablename__="patient_identities"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    patient_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("patients.id"), unique=True, index=True)
    encrypted_payload: Mapped[str] = mapped_column(Text)
    key_version: Mapped[str] = mapped_column(String(30), default="v1")

class ModelRegistry(UUIDMixin, TimestampMixin, Base):
    __tablename__="model_registry"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(120))
    provider: Mapped[str] = mapped_column(String(80))
    model_ref: Mapped[str] = mapped_column(String(200))
    purpose: Mapped[str] = mapped_column(String(50), default="generation")
    status: Mapped[str] = mapped_column(String(30), default="candidate")
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    approved_by: Mapped[UUID|None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    __table_args__=(UniqueConstraint("tenant_id","name"),)

class KnowledgeDocument(UUIDMixin, TimestampMixin, Base):
    __tablename__="knowledge_documents"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    title: Mapped[str] = mapped_column(String(300))
    version: Mapped[str] = mapped_column(String(50))
    status: Mapped[str] = mapped_column(String(30), default="draft")
    source: Mapped[str|None] = mapped_column(String(500), nullable=True)
    effective_from: Mapped[date|None] = mapped_column(Date, nullable=True)
    expires_on: Mapped[date|None] = mapped_column(Date, nullable=True)
    owner_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    object_key: Mapped[str|None] = mapped_column(String(500), nullable=True)
    sha256: Mapped[str|None] = mapped_column(String(64), nullable=True)
    __table_args__=(UniqueConstraint("tenant_id","title","version"),)

class FeatureFlag(UUIDMixin, TimestampMixin, Base):
    __tablename__="feature_flags"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    key: Mapped[str] = mapped_column(String(100))
    enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    config: Mapped[dict] = mapped_column(JSON, default=dict)
    __table_args__=(UniqueConstraint("tenant_id","key"),)

class AIFeedback(UUIDMixin, TimestampMixin, Base):
    __tablename__="ai_feedback"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    request_id: Mapped[str] = mapped_column(String(100), index=True)
    user_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))
    rating: Mapped[str] = mapped_column(String(30))
    note: Mapped[str|None] = mapped_column(Text, nullable=True)

class EvaluationRun(UUIDMixin, TimestampMixin, Base):
    __tablename__="evaluation_runs"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("tenants.id"), index=True)
    name: Mapped[str] = mapped_column(String(160))
    model_ref: Mapped[str] = mapped_column(String(200))
    dataset_version: Mapped[str] = mapped_column(String(80))
    status: Mapped[str] = mapped_column(String(30), default="completed")
    metrics: Mapped[dict] = mapped_column(JSON, default=dict)
    created_by: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), ForeignKey("users.id"))

class SecurityEvent(UUIDMixin, TimestampMixin, Base):
    __tablename__="security_events"
    tenant_id: Mapped[UUID] = mapped_column(PGUUID(as_uuid=True), index=True)
    user_id: Mapped[UUID|None] = mapped_column(PGUUID(as_uuid=True), nullable=True)
    event_type: Mapped[str] = mapped_column(String(100))
    severity: Mapped[str] = mapped_column(String(30), default="info")
    payload: Mapped[dict] = mapped_column(JSON, default=dict)

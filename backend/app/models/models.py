"""Modelos do banco de dados — SQLAlchemy 2.0"""

import uuid
from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import (
    String, Text, Float, Integer, Boolean, DateTime,
    ForeignKey, Enum, JSON, LargeBinary,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.app.core.database import Base


def utcnow():
    return datetime.now(timezone.utc)


def new_id():
    return str(uuid.uuid4())


# ── Enums ────────────────────────────────────────────────────

class UserRole(str, PyEnum):
    ADMIN = "admin"
    MEDICO = "medico"
    TECNICO = "tecnico"


class ExamStatus(str, PyEnum):
    UPLOADED = "uploaded"
    PROCESSING = "processing"
    ANALYZED = "analyzed"
    ERROR = "error"


class ReportStatus(str, PyEnum):
    DRAFT = "draft"
    REVIEW = "review"
    APPROVED = "approved"


class EEGClassification(str, PyEnum):
    NORMAL = "normal"
    ANORMAL = "anormal"
    INDETERMINADO = "indeterminado"


# ── User ─────────────────────────────────────────────────────

class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(200))
    email: Mapped[str] = mapped_column(String(200), unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String(200))
    role: Mapped[UserRole] = mapped_column(Enum(UserRole), default=UserRole.MEDICO)
    crm: Mapped[str | None] = mapped_column(String(50), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    reports: Mapped[list["Report"]] = relationship(back_populates="approved_by_user")


# ── Patient ──────────────────────────────────────────────────

class Patient(Base):
    __tablename__ = "patients"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    name: Mapped[str] = mapped_column(String(200))
    birth_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    gender: Mapped[str | None] = mapped_column(String(20), nullable=True)
    medical_record: Mapped[str | None] = mapped_column(String(100), nullable=True)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    exams: Mapped[list["Exam"]] = relationship(back_populates="patient")


# ── Exam ─────────────────────────────────────────────────────

class Exam(Base):
    __tablename__ = "exams"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    patient_id: Mapped[str] = mapped_column(ForeignKey("patients.id"))
    indication: Mapped[str | None] = mapped_column(String(500), nullable=True)
    exam_date: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    duration_seconds: Mapped[float | None] = mapped_column(Float, nullable=True)
    n_channels: Mapped[int | None] = mapped_column(Integer, nullable=True)
    sampling_rate: Mapped[float | None] = mapped_column(Float, nullable=True)
    channel_names: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    file_path: Mapped[str | None] = mapped_column(String(500), nullable=True)
    file_name: Mapped[str | None] = mapped_column(String(300), nullable=True)
    status: Mapped[ExamStatus] = mapped_column(Enum(ExamStatus), default=ExamStatus.UPLOADED)
    metadata_extra: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    patient: Mapped["Patient"] = relationship(back_populates="exams")
    report: Mapped["Report | None"] = relationship(back_populates="exam", uselist=False)
    analysis: Mapped["Analysis | None"] = relationship(back_populates="exam", uselist=False)


# ── Analysis (resultado da IA) ───────────────────────────────

class Analysis(Base):
    __tablename__ = "analyses"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    exam_id: Mapped[str] = mapped_column(ForeignKey("exams.id"), unique=True)
    classification: Mapped[EEGClassification] = mapped_column(
        Enum(EEGClassification), default=EEGClassification.INDETERMINADO
    )
    base_rhythm_hz: Mapped[float | None] = mapped_column(Float, nullable=True)
    base_rhythm_normal: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    has_asymmetry: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    asymmetry_details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    detected_patterns: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    spike_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    artifacts_detected: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    raw_analysis: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    exam: Mapped["Exam"] = relationship(back_populates="analysis")


# ── Report (laudo) ───────────────────────────────────────────

class Report(Base):
    __tablename__ = "reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    exam_id: Mapped[str] = mapped_column(ForeignKey("exams.id"), unique=True)
    generated_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    final_text: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[ReportStatus] = mapped_column(Enum(ReportStatus), default=ReportStatus.DRAFT)
    approved_by_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    approved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    llm_provider: Mapped[str | None] = mapped_column(String(50), nullable=True)
    llm_model: Mapped[str | None] = mapped_column(String(100), nullable=True)
    disclaimer: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    exam: Mapped["Exam"] = relationship(back_populates="report")
    approved_by_user: Mapped["User | None"] = relationship(back_populates="reports")


# ── RAG: Report Embeddings ───────────────────────────────────

class ReportEmbedding(Base):
    __tablename__ = "report_embeddings"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    report_id: Mapped[str] = mapped_column(ForeignKey("reports.id"), unique=True)
    exam_id: Mapped[str] = mapped_column(ForeignKey("exams.id"))
    text_summary: Mapped[str] = mapped_column(Text)
    embedding: Mapped[bytes] = mapped_column(LargeBinary)
    classification: Mapped[str | None] = mapped_column(String(50), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


# ── RAG: Reference Chunks (livros / documentos) ─────────────

class ReferenceChunk(Base):
    __tablename__ = "reference_chunks"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    source_name: Mapped[str] = mapped_column(String(300), index=True)
    source_file: Mapped[str | None] = mapped_column(String(500), nullable=True)
    chapter: Mapped[str | None] = mapped_column(String(200), nullable=True)
    page_start: Mapped[int | None] = mapped_column(Integer, nullable=True)
    page_end: Mapped[int | None] = mapped_column(Integer, nullable=True)
    chunk_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    embedding: Mapped[bytes] = mapped_column(LargeBinary)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


# ── Audit Log ────────────────────────────────────────────────

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=new_id)
    user_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    action: Mapped[str] = mapped_column(String(100))
    entity_type: Mapped[str | None] = mapped_column(String(50), nullable=True)
    entity_id: Mapped[str | None] = mapped_column(String(36), nullable=True)
    details: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

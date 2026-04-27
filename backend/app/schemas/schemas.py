"""Schemas Pydantic — validação de dados de entrada e saída da API."""

from datetime import datetime
from pydantic import BaseModel, EmailStr, Field


# ── Auth ─────────────────────────────────────────────────────

class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    email: EmailStr
    password: str = Field(min_length=6)
    role: str = "medico"
    crm: str | None = None


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    role: str
    crm: str | None
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Patient ──────────────────────────────────────────────────

class PatientCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    birth_date: datetime | None = None
    gender: str | None = None
    medical_record: str | None = None
    notes: str | None = None


class PatientUpdate(BaseModel):
    name: str | None = None
    birth_date: datetime | None = None
    gender: str | None = None
    medical_record: str | None = None
    notes: str | None = None


class PatientResponse(BaseModel):
    id: str
    name: str
    birth_date: datetime | None
    gender: str | None
    medical_record: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Exam ─────────────────────────────────────────────────────

class ExamCreate(BaseModel):
    patient_id: str
    indication: str | None = None
    exam_date: datetime | None = None


class ExamResponse(BaseModel):
    id: str
    patient_id: str
    indication: str | None
    exam_date: datetime | None
    duration_seconds: float | None
    n_channels: int | None
    sampling_rate: float | None
    channel_names: list[str] | None
    file_name: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Analysis ─────────────────────────────────────────────────

class AnalysisResponse(BaseModel):
    id: str
    exam_id: str
    classification: str
    base_rhythm_hz: float | None
    base_rhythm_normal: bool | None
    has_asymmetry: bool | None
    asymmetry_details: dict | None
    detected_patterns: dict | None
    spike_count: int | None
    created_at: datetime

    model_config = {"from_attributes": True}


# ── Report ───────────────────────────────────────────────────

class ReportResponse(BaseModel):
    id: str
    exam_id: str
    generated_text: str | None
    final_text: str | None
    status: str
    disclaimer: str | None
    approved_by_id: str | None
    approved_at: datetime | None
    llm_provider: str | None
    llm_model: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class ReportUpdateText(BaseModel):
    final_text: str


class ReportApprove(BaseModel):
    final_text: str | None = None


# ── Upload ───────────────────────────────────────────────────

class UploadResponse(BaseModel):
    exam_id: str
    file_name: str
    message: str


# ── Health ───────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    version: str
    database: str
    llm_provider: str
    storage_provider: str

"""Rotas de exames — upload, análise e geração de laudo."""

import uuid
from datetime import datetime
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.app.core.config import get_settings
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user_id
from backend.app.models.models import Exam, Patient, Analysis, Report, ExamStatus, ReportStatus
from backend.app.schemas.schemas import ExamResponse, UploadResponse, AnalysisResponse, ReportResponse
from backend.app.services.storage import get_storage
from backend.app.services.report_generator import generate_report

router = APIRouter(prefix="/api/exams", tags=["Exames"])
settings = get_settings()


@router.post("/upload", response_model=UploadResponse)
async def upload_exam(
    file: UploadFile = File(...),
    patient_id: str = Form(...),
    indication: str = Form(""),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Upload de arquivo .EDF de exame EEG."""
    # Validar paciente
    result = await db.execute(select(Patient).where(Patient.id == patient_id))
    patient = result.scalar_one_or_none()
    if not patient:
        raise HTTPException(status_code=404, detail="Paciente não encontrado")

    # Validar extensão
    if not file.filename or not file.filename.lower().endswith((".edf", ".edf+")):
        raise HTTPException(status_code=400, detail="Formato inválido. Envie um arquivo .EDF")

    # Salvar arquivo
    file_bytes = await file.read()
    storage = get_storage()
    file_id = str(uuid.uuid4())
    destination = f"edf/{file_id}/{file.filename}"
    saved_path = await storage.save(file_bytes, destination)

    # Criar registro do exame
    exam = Exam(
        patient_id=patient_id,
        indication=indication,
        file_path=saved_path,
        file_name=file.filename,
        status=ExamStatus.UPLOADED,
    )
    db.add(exam)
    await db.commit()
    await db.refresh(exam)

    return UploadResponse(
        exam_id=exam.id,
        file_name=file.filename,
        message="Arquivo enviado com sucesso. Use /api/exams/{exam_id}/analyze para processar.",
    )


@router.post("/{exam_id}/analyze", response_model=AnalysisResponse)
async def analyze_exam(
    exam_id: str,
    patient_age_years: int = 30,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Executar análise de IA no exame."""
    result = await db.execute(select(Exam).where(Exam.id == exam_id))
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="Exame não encontrado")

    if not exam.file_path or not Path(exam.file_path).exists():
        raise HTTPException(status_code=400, detail="Arquivo EDF não encontrado")

    # Executar análise
    exam.status = ExamStatus.PROCESSING
    await db.commit()

    try:
        from backend.app.ml.analysis_pipeline import run_full_analysis
        analysis_data = run_full_analysis(exam.file_path, patient_age_years)
    except Exception as e:
        exam.status = ExamStatus.ERROR
        await db.commit()
        raise HTTPException(status_code=500, detail=f"Erro na análise: {str(e)}")

    # Atualizar metadados do exame
    meta = analysis_data.get("metadata", {})
    exam.duration_seconds = meta.get("duration_seconds")
    exam.n_channels = meta.get("n_channels")
    exam.sampling_rate = meta.get("sampling_rate")
    exam.channel_names = meta.get("channel_names")
    exam.status = ExamStatus.ANALYZED

    # Salvar análise
    analysis = Analysis(
        exam_id=exam_id,
        classification=analysis_data.get("classification", "indeterminado"),
        base_rhythm_hz=analysis_data.get("base_rhythm_hz"),
        base_rhythm_normal=analysis_data.get("base_rhythm_normal"),
        has_asymmetry=analysis_data.get("has_asymmetry"),
        asymmetry_details=analysis_data.get("asymmetry_details"),
        detected_patterns=analysis_data.get("detected_patterns"),
        spike_count=analysis_data.get("spike_count"),
        artifacts_detected=analysis_data.get("artifacts_detected"),
        raw_analysis=analysis_data,
    )
    db.add(analysis)
    await db.commit()
    await db.refresh(analysis)

    return analysis


@router.post("/{exam_id}/generate-report", response_model=ReportResponse)
async def generate_exam_report(
    exam_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Gerar laudo via LLM a partir da análise."""
    # Carregar exame + análise + paciente
    result = await db.execute(
        select(Exam).options(selectinload(Exam.patient)).where(Exam.id == exam_id)
    )
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="Exame não encontrado")

    # Verificar se tem análise
    analysis_result = await db.execute(select(Analysis).where(Analysis.exam_id == exam_id))
    analysis = analysis_result.scalar_one_or_none()
    if not analysis:
        raise HTTPException(status_code=400, detail="Execute a análise primeiro (/api/exams/{id}/analyze)")

    # Calcular idade do paciente
    patient = exam.patient
    age_str = "Não informada"
    if patient.birth_date:
        age_years = (datetime.now() - patient.birth_date).days // 365
        age_str = f"{age_years} anos"

    # Gerar laudo
    analysis_dict = {
        "classification": analysis.classification.value if hasattr(analysis.classification, 'value') else analysis.classification,
        "base_rhythm_hz": analysis.base_rhythm_hz,
        "has_asymmetry": analysis.has_asymmetry,
        "asymmetry_details": analysis.asymmetry_details or {},
        "spike_count": analysis.spike_count or 0,
        "detected_patterns": analysis.detected_patterns or {},
    }

    report_text = await generate_report(
        patient_name=patient.name,
        patient_age=age_str,
        indication=exam.indication or "Não informada",
        duration_minutes=(exam.duration_seconds or 0) / 60,
        analysis_data=analysis_dict,
    )

    # Salvar relatório
    report = Report(
        exam_id=exam_id,
        generated_text=report_text,
        final_text=report_text,
        status=ReportStatus.DRAFT,
        llm_provider=settings.llm_provider,
        llm_model=settings.llm_model,
        disclaimer=settings.laudo_disclaimer,
    )
    db.add(report)
    await db.commit()
    await db.refresh(report)

    return report


@router.get("/", response_model=list[ExamResponse])
async def list_exams(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(select(Exam).order_by(Exam.created_at.desc()))
    return result.scalars().all()


@router.get("/{exam_id}", response_model=ExamResponse)
async def get_exam(
    exam_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(select(Exam).where(Exam.id == exam_id))
    exam = result.scalar_one_or_none()
    if not exam:
        raise HTTPException(status_code=404, detail="Exame não encontrado")
    return exam


@router.get("/{exam_id}/report", response_model=ReportResponse)
async def get_exam_report(
    exam_id: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    result = await db.execute(select(Report).where(Report.exam_id == exam_id))
    report = result.scalar_one_or_none()
    if not report:
        raise HTTPException(status_code=404, detail="Laudo não encontrado. Gere primeiro com /generate-report")
    return report

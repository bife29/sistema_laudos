"""Rotas de referências médicas — upload e gestão de livros/documentos para RAG."""

import uuid
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import get_settings
from backend.app.core.database import get_db
from backend.app.core.security import get_current_user_id
from backend.app.models.models import ReferenceChunk, ReportEmbedding
from backend.app.schemas.schemas import ReferenceSourceResponse, ReferenceStatsResponse

router = APIRouter(prefix="/api/references", tags=["Referências"])
settings = get_settings()


@router.post("/upload-pdf")
async def upload_reference_pdf(
    file: UploadFile = File(...),
    source_name: str = Form(...),
    chapter: str = Form(None),
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Upload de PDF de referência médica para RAG.

    O PDF é processado em background: extrai texto, divide em chunks,
    gera embeddings e salva no banco. Livros de ~1000 páginas são suportados.
    """
    if not settings.rag_enabled:
        raise HTTPException(
            status_code=400,
            detail="RAG não está habilitado. Configure RAG_ENABLED=true no .env",
        )

    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Envie um arquivo PDF")

    # Salvar PDF
    ref_dir = Path(settings.storage_local_path) / "references"
    ref_dir.mkdir(parents=True, exist_ok=True)
    safe_name = f"{uuid.uuid4()}_{Path(file.filename).name}"
    temp_path = ref_dir / safe_name

    content = await file.read()
    temp_path.write_bytes(content)

    try:
        from backend.app.services.pdf_ingestion import ingest_pdf

        result = await ingest_pdf(
            db=db,
            file_path=str(temp_path),
            source_name=source_name,
            chapter=chapter,
        )
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar PDF: {str(e)}")


@router.get("/sources", response_model=list[ReferenceSourceResponse])
async def list_reference_sources(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Listar fontes de referência cadastradas."""
    result = await db.execute(
        select(
            ReferenceChunk.source_name,
            func.count(ReferenceChunk.id).label("chunk_count"),
            func.min(ReferenceChunk.page_start).label("min_page"),
            func.max(ReferenceChunk.page_end).label("max_page"),
        ).group_by(ReferenceChunk.source_name)
    )
    rows = result.all()
    return [
        ReferenceSourceResponse(
            source_name=r.source_name,
            chunk_count=r.chunk_count,
            page_range=f"{r.min_page}-{r.max_page}" if r.min_page else None,
        )
        for r in rows
    ]


@router.delete("/sources/{source_name}")
async def delete_reference_source(
    source_name: str,
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Remover uma fonte de referência e todos os seus chunks."""
    result = await db.execute(
        delete(ReferenceChunk).where(ReferenceChunk.source_name == source_name)
    )
    await db.commit()
    return {"deleted": result.rowcount, "source_name": source_name}


@router.get("/stats", response_model=ReferenceStatsResponse)
async def get_rag_stats(
    db: AsyncSession = Depends(get_db),
    user_id: str = Depends(get_current_user_id),
):
    """Estatísticas do sistema RAG."""
    ref_count = await db.execute(select(func.count(ReferenceChunk.id)))
    report_emb_count = await db.execute(select(func.count(ReportEmbedding.id)))
    source_count = await db.execute(
        select(func.count(func.distinct(ReferenceChunk.source_name)))
    )

    return ReferenceStatsResponse(
        rag_enabled=settings.rag_enabled,
        embedding_provider=settings.embedding_provider,
        total_reference_chunks=ref_count.scalar() or 0,
        total_report_embeddings=report_emb_count.scalar() or 0,
        total_sources=source_count.scalar() or 0,
    )

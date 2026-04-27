"""Serviço RAG — Retrieval-Augmented Generation para laudos EEG.

Combina duas fontes de conhecimento:
1. Laudos aprovados anteriores (aprendizado contínuo)
2. Referências médicas / livros (base fixa de conhecimento)

A busca usa similaridade de cosseno com numpy — sem dependência
de pgvector. Para < 10.000 vetores, a busca leva < 5ms.
"""

import logging

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.config import get_settings
from backend.app.models.models import ReportEmbedding, ReferenceChunk
from backend.app.services.embedding_service import get_embedding_provider

logger = logging.getLogger(__name__)


def _cosine_similarity(query: np.ndarray, vectors: np.ndarray) -> np.ndarray:
    """Similaridade de cosseno entre query e array de vetores."""
    if vectors.size == 0:
        return np.array([])
    query_norm = query / (np.linalg.norm(query) + 1e-10)
    norms = np.linalg.norm(vectors, axis=1, keepdims=True) + 1e-10
    vectors_norm = vectors / norms
    return vectors_norm @ query_norm


async def store_report_embedding(
    db: AsyncSession,
    report_id: str,
    exam_id: str,
    text: str,
    classification: str | None = None,
) -> bool:
    """Armazena embedding de um laudo aprovado para futuras consultas RAG.

    Retorna True se armazenado, False se RAG desabilitado ou erro.
    """
    settings = get_settings()
    if not settings.rag_enabled:
        return False

    try:
        embedder = get_embedding_provider()
        vector = await embedder.embed(text)
        if vector is None:
            return False

        # Verificar se já existe
        existing = await db.execute(
            select(ReportEmbedding).where(ReportEmbedding.report_id == report_id)
        )
        if existing.scalar_one_or_none():
            logger.debug(f"Embedding já existe para report {report_id}")
            return True

        entry = ReportEmbedding(
            report_id=report_id,
            exam_id=exam_id,
            text_summary=text[:2000],  # Limita tamanho do resumo
            embedding=vector.tobytes(),
            classification=classification,
        )
        db.add(entry)
        await db.commit()
        logger.info(f"Embedding armazenado para report {report_id}")
        return True

    except Exception as e:
        logger.error(f"Erro ao armazenar embedding: {e}")
        return False


async def find_similar_reports(
    db: AsyncSession,
    query_text: str,
    top_k: int = 3,
) -> list[dict]:
    """Busca laudos aprovados similares ao texto de consulta."""
    settings = get_settings()
    if not settings.rag_enabled:
        return []

    try:
        embedder = get_embedding_provider()
        query_vec = await embedder.embed(query_text)
        if query_vec is None:
            return []

        result = await db.execute(select(ReportEmbedding))
        entries = result.scalars().all()
        if not entries:
            return []

        dim = len(query_vec)
        vectors = np.array(
            [np.frombuffer(e.embedding, dtype=np.float32)[:dim] for e in entries]
        )

        similarities = _cosine_similarity(query_vec, vectors)
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0.3:  # Threshold mínimo
                entry = entries[idx]
                results.append({
                    "text": entry.text_summary,
                    "similarity": float(similarities[idx]),
                    "classification": entry.classification,
                })
        return results

    except Exception as e:
        logger.error(f"Erro na busca de laudos similares: {e}")
        return []


async def find_relevant_references(
    db: AsyncSession,
    query_text: str,
    top_k: int = 3,
) -> list[dict]:
    """Busca trechos de livros/referências relevantes."""
    settings = get_settings()
    if not settings.rag_enabled:
        return []

    try:
        embedder = get_embedding_provider()
        query_vec = await embedder.embed(query_text)
        if query_vec is None:
            return []

        result = await db.execute(select(ReferenceChunk))
        chunks = result.scalars().all()
        if not chunks:
            return []

        dim = len(query_vec)
        vectors = np.array(
            [np.frombuffer(c.embedding, dtype=np.float32)[:dim] for c in chunks]
        )

        similarities = _cosine_similarity(query_vec, vectors)
        top_indices = np.argsort(similarities)[-top_k:][::-1]

        results = []
        for idx in top_indices:
            if similarities[idx] > 0.25:  # Threshold mais baixo para referências
                chunk = chunks[idx]
                results.append({
                    "text": chunk.text,
                    "source": chunk.source_name,
                    "chapter": chunk.chapter,
                    "page_start": chunk.page_start,
                    "similarity": float(similarities[idx]),
                })
        return results

    except Exception as e:
        logger.error(f"Erro na busca de referências: {e}")
        return []


async def build_rag_context(
    db: AsyncSession,
    analysis_summary: str,
) -> str | None:
    """Constrói contexto RAG combinando laudos similares + referências médicas.

    Retorna None se RAG desabilitado ou sem resultados — nesse caso
    o sistema gera o laudo normalmente como antes (zero impacto).
    """
    settings = get_settings()
    if not settings.rag_enabled:
        return None

    similar_reports = await find_similar_reports(db, analysis_summary, top_k=3)
    references = await find_relevant_references(db, analysis_summary, top_k=3)

    if not similar_reports and not references:
        return None

    parts = []

    if references:
        parts.append("REFERÊNCIAS MÉDICAS RELEVANTES:")
        for i, ref in enumerate(references, 1):
            source_info = ref["source"]
            if ref.get("chapter"):
                source_info += f" — {ref['chapter']}"
            if ref.get("page_start"):
                source_info += f" (p. {ref['page_start']})"
            parts.append(f"\n[Ref. {i}] {source_info}:")
            parts.append(ref["text"][:800])

    if similar_reports:
        parts.append("\nLAUDOS APROVADOS COM PADRÃO SIMILAR:")
        for i, report in enumerate(similar_reports, 1):
            classif = report.get("classification", "N/A")
            parts.append(f"\n[Laudo similar {i}] (classificação: {classif}):")
            parts.append(report["text"][:800])

    return "\n".join(parts)

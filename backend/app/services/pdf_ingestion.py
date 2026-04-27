"""Serviço de ingestão de PDFs — extrai texto, divide em chunks e gera embeddings.

Suporta livros de até ~1000 páginas. O processamento é feito em batches
para não sobrecarregar memória (batch de 20 chunks por vez).

Usa pypdf (puro Python, ~2MB) para extração de texto.
Para PDFs escaneados (imagem), o PDF precisa ter OCR aplicado antes.
"""

import logging
from pathlib import Path

from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.models.models import ReferenceChunk
from backend.app.services.embedding_service import get_embedding_provider

logger = logging.getLogger(__name__)


def extract_text_from_pdf(file_path: str) -> list[dict]:
    """Extrai texto página por página de um PDF.

    Retorna lista de {"page": int, "text": str}.
    """
    from pypdf import PdfReader

    reader = PdfReader(file_path)
    pages = []
    for i, page in enumerate(reader.pages):
        text = page.extract_text() or ""
        text = text.strip()
        if text:
            pages.append({"page": i + 1, "text": text})
    return pages


def chunk_pages(
    pages: list[dict],
    chunk_size: int = 800,
    overlap: int = 100,
) -> list[dict]:
    """Divide páginas em chunks de ~chunk_size palavras com overlap.

    Para um livro de 1000 páginas (~400 palavras/página):
    - 400.000 palavras total
    - ~570 chunks com chunk_size=800, overlap=100
    """
    chunks = []
    chunk_index = 0

    for page_data in pages:
        text = page_data["text"]
        page_num = page_data["page"]
        words = text.split()

        if len(words) <= chunk_size:
            chunks.append({
                "chunk_index": chunk_index,
                "text": text,
                "page_start": page_num,
                "page_end": page_num,
            })
            chunk_index += 1
        else:
            start = 0
            while start < len(words):
                end = min(start + chunk_size, len(words))
                chunk_text = " ".join(words[start:end])
                chunks.append({
                    "chunk_index": chunk_index,
                    "text": chunk_text,
                    "page_start": page_num,
                    "page_end": page_num,
                })
                chunk_index += 1
                start += chunk_size - overlap

    return chunks


async def ingest_pdf(
    db: AsyncSession,
    file_path: str,
    source_name: str,
    chapter: str | None = None,
    batch_size: int = 20,
) -> dict:
    """Pipeline completo: extrai PDF -> chunka -> embeda -> salva no banco.

    Args:
        db: Sessão do banco de dados
        file_path: Caminho do arquivo PDF
        source_name: Nome da fonte (ex: "Niedermeyer's EEG")
        chapter: Capítulo específico (opcional)
        batch_size: Quantos chunks processar por batch (controla memória)

    Returns:
        Dict com status, total_pages, total_chunks, chunks_saved
    """
    embedder = get_embedding_provider()

    # 1. Extrair texto
    logger.info(f"Extraindo texto de {file_path}...")
    pages = extract_text_from_pdf(file_path)
    if not pages:
        return {"status": "error", "message": "Nenhum texto extraído do PDF. Verifique se o PDF tem texto selecionável (não é imagem escaneada)."}

    logger.info(f"Extraídas {len(pages)} páginas com texto")

    # 2. Dividir em chunks
    chunks = chunk_pages(pages, chunk_size=800, overlap=100)
    logger.info(f"PDF dividido em {len(chunks)} chunks")

    # 3. Gerar embeddings e salvar em batches
    saved = 0
    errors = 0

    for i in range(0, len(chunks), batch_size):
        batch = chunks[i : i + batch_size]
        texts = [c["text"] for c in batch]

        try:
            embeddings = await embedder.embed_batch(texts)
            if embeddings is None:
                logger.warning("Embedding provider retornou None — abortando ingestão")
                break

            for chunk_data, embedding in zip(batch, embeddings):
                entry = ReferenceChunk(
                    source_name=source_name,
                    source_file=Path(file_path).name,
                    chapter=chapter,
                    page_start=chunk_data["page_start"],
                    page_end=chunk_data["page_end"],
                    chunk_index=chunk_data["chunk_index"],
                    text=chunk_data["text"],
                    embedding=embedding.tobytes(),
                )
                db.add(entry)
                saved += 1

            await db.commit()
            logger.info(
                f"  Batch {i // batch_size + 1}/{(len(chunks) - 1) // batch_size + 1}: "
                f"{saved} chunks salvos"
            )

        except Exception as e:
            errors += 1
            logger.error(f"Erro no batch {i // batch_size + 1}: {e}")
            await db.rollback()
            if errors > 3:
                logger.error("Muitos erros — abortando ingestão")
                break

    return {
        "status": "ok" if saved > 0 else "error",
        "source_name": source_name,
        "total_pages": len(pages),
        "total_chunks": len(chunks),
        "chunks_saved": saved,
        "errors": errors,
    }

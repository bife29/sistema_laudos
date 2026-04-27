"""Teste local completo do sistema RAG."""
import asyncio
import httpx
import json
import numpy as np

BASE = "http://localhost:8002"


def test_chunking():
    """Teste 1: chunking de texto médico."""
    from backend.app.services.pdf_ingestion import chunk_pages

    pages = [
        {"page": 1, "text": "Capitulo 1: Ritmo Alfa. O ritmo alfa normal tem frequencia entre 8-13 Hz e e predominante nas regioes occipitais posteriores. A atenuacao do ritmo alfa com abertura ocular e um achado fisiologico normal. Amplitudes tipicas variam de 20 a 100 microvolts. O ritmo alfa pode apresentar modulacao em amplitude conhecida como fuso alfa."},
        {"page": 2, "text": "Capitulo 2: Atividade Epileptiforme. Ondas agudas na regiao temporal sao consideradas potenciais epileptiformes quando apresentam duracao de 70-200ms e sao seguidas de onda lenta. Espiculas tem duracao de 20-70ms. A presenca de atividade epileptiforme focal sugere foco irritativo lateralizado. Complexos ponta-onda sao marcadores de epilepsia generalizada."},
        {"page": 3, "text": "Capitulo 3: Assimetrias. A assimetria inter-hemisferica significativa e definida como diferenca de amplitude maior que 50 por cento entre hemisferios homologos. Assimetrias persistentes devem ser correlacionadas com dados clinicos e de neuroimagem. Reducao focal de amplitude pode indicar lesao estrutural subjacente."},
        {"page": 4, "text": "Capitulo 4: EEG Normal do Adulto. O EEG normal do adulto em vigilia apresenta ritmo alfa posterior, atividade beta de baixa amplitude nas regioes anteriores e ausencia de atividade lenta patologica ou epileptiforme. A classificacao como normal requer analise sistematica de todos os canais durante todo o registro."},
        {"page": 5, "text": "Capitulo 5: Artefatos. Artefatos musculares sao comuns nas regioes temporais e frontais. Artefatos de movimento ocular predominam nos canais frontopolares. A identificacao correta de artefatos e essencial para evitar falsos positivos na deteccao de atividade epileptiforme."},
    ]

    chunks = chunk_pages(pages, chunk_size=30, overlap=5)
    print(f"  Paginas: {len(pages)}")
    print(f"  Chunks gerados: {len(chunks)}")
    for c in chunks:
        words = len(c["text"].split())
        print(f"    Chunk {c['chunk_index']}: pag {c['page_start']}, {words} palavras")
    return chunks


def test_cosine_similarity():
    """Teste 2: similaridade de cosseno."""
    from backend.app.services.rag_service import _cosine_similarity

    # Vetores de teste
    query = np.array([1.0, 0.0, 0.0], dtype=np.float32)
    vectors = np.array([
        [1.0, 0.0, 0.0],   # identico
        [0.0, 1.0, 0.0],   # ortogonal
        [0.7, 0.7, 0.0],   # similar
        [-1.0, 0.0, 0.0],  # oposto
    ], dtype=np.float32)

    sims = _cosine_similarity(query, vectors)
    print(f"  Identico:  {sims[0]:.3f} (esperado ~1.0)")
    print(f"  Ortogonal: {sims[1]:.3f} (esperado ~0.0)")
    print(f"  Similar:   {sims[2]:.3f} (esperado ~0.7)")
    print(f"  Oposto:    {sims[3]:.3f} (esperado ~-1.0)")
    assert abs(sims[0] - 1.0) < 0.01
    assert abs(sims[1] - 0.0) < 0.01
    assert sims[2] > 0.5


async def test_embedding_none():
    """Teste 3: NoneEmbedding retorna None."""
    from backend.app.services.embedding_service import NoneEmbedding

    emb = NoneEmbedding()
    result = await emb.embed("teste")
    assert result is None
    batch = await emb.embed_batch(["a", "b"])
    assert batch is None
    print("  NoneEmbedding.embed() = None")
    print("  NoneEmbedding.embed_batch() = None")


async def test_rag_disabled():
    """Teste 4: RAG desabilitado retorna listas vazias."""
    from backend.app.services.rag_service import build_rag_context

    # Simular sessao do banco
    from backend.app.core.database import async_session
    async with async_session() as db:
        ctx = await build_rag_context(db, "EEG normal, ritmo alfa 10Hz")
        assert ctx is None
        print("  build_rag_context() = None (RAG off)")


def test_api_endpoints():
    """Teste 5: endpoints via HTTP."""
    # Login
    r = httpx.post(BASE + "/api/auth/login", data={"username": "admin@eeg.com", "password": "admin123"})
    assert r.status_code == 200
    token = r.json()["access_token"]
    H = {"Authorization": "Bearer " + token}
    print("  Login OK")

    # Health
    r = httpx.get(BASE + "/api/health")
    rag = r.json().get("rag_status", "N/A")
    print(f"  Health OK - rag_status: {rag}")

    # Stats
    r = httpx.get(BASE + "/api/references/stats", headers=H)
    assert r.status_code == 200
    s = r.json()
    print(f"  Stats OK - enabled={s['rag_enabled']}, refs={s['total_reference_chunks']}, embs={s['total_report_embeddings']}")

    # Sources
    r = httpx.get(BASE + "/api/references/sources", headers=H)
    assert r.status_code == 200
    print(f"  Sources OK - {len(r.json())} fontes")

    # Upload bloqueado
    r = httpx.post(BASE + "/api/references/upload-pdf", headers=H,
        data={"source_name": "Teste"},
        files={"file": ("teste.pdf", b"%PDF fake", "application/pdf")})
    assert r.status_code == 400
    print(f"  Upload bloqueado OK (RAG off)")

    # Delete source (mesmo vazio, nao deve dar erro)
    r = httpx.delete(BASE + "/api/references/sources/inexistente", headers=H)
    assert r.status_code == 200
    print(f"  Delete source OK - deleted={r.json()['deleted']}")


if __name__ == "__main__":
    print("=" * 55)
    print("  TESTE LOCAL DO SISTEMA RAG")
    print("=" * 55)

    print("\n[1/5] Chunking de texto medico:")
    test_chunking()

    print("\n[2/5] Similaridade de cosseno:")
    test_cosine_similarity()

    print("\n[3/5] NoneEmbedding (RAG off):")
    asyncio.run(test_embedding_none())

    print("\n[4/5] RAG context desabilitado:")
    asyncio.run(test_rag_disabled())

    print("\n[5/5] Endpoints da API:")
    test_api_endpoints()

    print("\n" + "=" * 55)
    print("  TODOS OS 5 TESTES PASSARAM!")
    print("  RAG pronto. Zero impacto no fluxo atual.")
    print("=" * 55)

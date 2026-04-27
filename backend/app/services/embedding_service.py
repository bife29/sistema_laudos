"""Serviço de embeddings — gera vetores numéricos a partir de texto.

Provedores suportados:
- none: RAG desabilitado (padrão)
- ollama: Embeddings locais via Ollama (gratuito)
- openai: Embeddings via API OpenAI (pago, ~$0.02/1M tokens)
"""

import logging
from abc import ABC, abstractmethod

import numpy as np

from backend.app.core.config import get_settings

logger = logging.getLogger(__name__)

_provider_instance = None


class EmbeddingProvider(ABC):
    @abstractmethod
    async def embed(self, text: str) -> np.ndarray | None:
        ...

    async def embed_batch(self, texts: list[str]) -> list[np.ndarray] | None:
        results = []
        for t in texts:
            vec = await self.embed(t)
            if vec is None:
                return None
            results.append(vec)
        return results


class NoneEmbedding(EmbeddingProvider):
    """RAG desabilitado — retorna None para todos os embeddings."""

    async def embed(self, text: str) -> None:
        return None

    async def embed_batch(self, texts: list[str]) -> None:
        return None


class OllamaEmbedding(EmbeddingProvider):
    """Embeddings via Ollama (local, gratuito)."""

    def __init__(self, model: str, base_url: str):
        self.model = model
        self.base_url = base_url.rstrip("/")

    async def embed(self, text: str) -> np.ndarray:
        import httpx

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                f"{self.base_url}/api/embeddings",
                json={"model": self.model, "prompt": text},
            )
            resp.raise_for_status()
            return np.array(resp.json()["embedding"], dtype=np.float32)

    async def embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        # Ollama não tem batch nativo — processa sequencialmente
        return [await self.embed(t) for t in texts]


class OpenAIEmbedding(EmbeddingProvider):
    """Embeddings via API OpenAI."""

    def __init__(self, model: str, api_key: str):
        self.model = model
        self.api_key = api_key

    async def embed(self, text: str) -> np.ndarray:
        result = await self.embed_batch([text])
        return result[0]

    async def embed_batch(self, texts: list[str]) -> list[np.ndarray]:
        import httpx

        async with httpx.AsyncClient(timeout=60) as client:
            resp = await client.post(
                "https://api.openai.com/v1/embeddings",
                json={"model": self.model, "input": texts},
                headers={"Authorization": f"Bearer {self.api_key}"},
            )
            resp.raise_for_status()
            data = resp.json()["data"]
            return [
                np.array(d["embedding"], dtype=np.float32)
                for d in sorted(data, key=lambda x: x["index"])
            ]


def get_embedding_provider() -> EmbeddingProvider:
    """Retorna a instância do provedor de embeddings (singleton lazy)."""
    global _provider_instance
    if _provider_instance is not None:
        return _provider_instance

    settings = get_settings()
    provider = settings.embedding_provider.lower()

    if provider == "ollama":
        model = settings.embedding_model or "nomic-embed-text"
        base_url = (
            settings.embedding_base_url
            or settings.llm_base_url
            or "http://localhost:11434"
        )
        _provider_instance = OllamaEmbedding(model, base_url)
        logger.info(f"Embedding provider: Ollama ({model} @ {base_url})")

    elif provider == "openai":
        model = settings.embedding_model or "text-embedding-3-small"
        api_key = settings.embedding_api_key or settings.llm_api_key
        if not api_key or api_key == "COLOQUE-SUA-API-KEY-AQUI":
            logger.warning("OpenAI embedding configurado mas sem API key — RAG desabilitado")
            _provider_instance = NoneEmbedding()
        else:
            _provider_instance = OpenAIEmbedding(model, api_key)
            logger.info(f"Embedding provider: OpenAI ({model})")

    else:
        _provider_instance = NoneEmbedding()
        logger.info("Embedding provider: None (RAG desabilitado)")

    return _provider_instance

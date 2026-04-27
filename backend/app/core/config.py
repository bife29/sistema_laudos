"""Configurações centralizadas — todas parametrizáveis via .env"""

from pathlib import Path
from functools import lru_cache
from pydantic_settings import BaseSettings
from pydantic import Field


BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent


class Settings(BaseSettings):
    # ── App ──────────────────────────────────────────────────
    app_name: str = "Sistema de Laudos EEG"
    app_version: str = "0.1.0"
    app_env: str = "development"
    debug: bool = True
    secret_key: str = "TROQUE-POR-UMA-CHAVE-SECRETA"

    # ── Database ─────────────────────────────────────────────
    database_url: str = f"sqlite+aiosqlite:///{BASE_DIR / 'data' / 'eeg_laudos.db'}"

    # ── Storage ──────────────────────────────────────────────
    storage_provider: str = "local"  # local | s3 | minio
    storage_local_path: str = str(BASE_DIR / "data" / "uploads")
    storage_s3_bucket: str = ""
    storage_s3_region: str = ""
    storage_s3_access_key: str = ""
    storage_s3_secret_key: str = ""
    storage_s3_endpoint_url: str = ""

    # ── LLM ──────────────────────────────────────────────────
    llm_provider: str = "anthropic"  # anthropic | openai | ollama
    llm_model: str = "claude-sonnet-4-20250514"
    llm_api_key: str = ""
    llm_max_tokens: int = 2000
    llm_temperature: float = 0.3
    llm_base_url: str = ""  # Para Ollama

    # ── RAG / Embeddings ─────────────────────────────────────
    rag_enabled: bool = True
    embedding_provider: str = "none"  # none | openai | ollama
    embedding_model: str = ""
    embedding_api_key: str = ""
    embedding_base_url: str = ""

    # ── Redis ────────────────────────────────────────────────
    redis_url: str = ""

    # ── JWT ───────────────────────────────────────────────────
    jwt_secret_key: str = "TROQUE-POR-OUTRA-CHAVE-SECRETA"
    jwt_algorithm: str = "HS256"
    jwt_access_token_expire_minutes: int = 60
    jwt_refresh_token_expire_days: int = 7

    # ── CORS ─────────────────────────────────────────────────
    cors_origins: str = "http://localhost:5173,http://localhost:3000"

    # ── Laudo ────────────────────────────────────────────────
    laudo_disclaimer: str = (
        "Laudo gerado com auxílio de inteligência artificial. "
        "A validação e responsabilidade clínica são do médico assinante."
    )

    @property
    def cors_origins_list(self) -> list[str]:
        return [o.strip() for o in self.cors_origins.split(",") if o.strip()]

    @property
    def is_sqlite(self) -> bool:
        return "sqlite" in self.database_url

    model_config = {"env_file": str(BASE_DIR / ".env"), "extra": "ignore"}


@lru_cache
def get_settings() -> Settings:
    return Settings()

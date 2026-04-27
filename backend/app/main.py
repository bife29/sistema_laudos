"""Sistema de Laudos EEG — Aplicação FastAPI."""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from backend.app.core.config import get_settings
from backend.app.core.database import init_db
from backend.app.schemas.schemas import HealthResponse


settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Inicialização e encerramento da aplicação."""
    # Criar diretórios necessários
    Path(settings.storage_local_path).mkdir(parents=True, exist_ok=True)
    Path("data").mkdir(parents=True, exist_ok=True)

    # Criar tabelas do banco
    await init_db()

    yield


app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="Sistema de Laudos EEG com Inteligência Artificial",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Rotas
from backend.app.api.auth import router as auth_router
from backend.app.api.patients import router as patients_router
from backend.app.api.exams import router as exams_router

app.include_router(auth_router)
app.include_router(patients_router)
app.include_router(exams_router)


@app.get("/api/health", response_model=HealthResponse, tags=["Sistema"])
async def health_check():
    """Verifica o status do sistema."""
    db_type = "sqlite" if settings.is_sqlite else "postgresql"
    llm_configured = bool(settings.llm_api_key and settings.llm_api_key != "COLOQUE-SUA-API-KEY-AQUI")

    return HealthResponse(
        status="ok",
        version=settings.app_version,
        database=db_type,
        llm_provider=f"{settings.llm_provider} ({'configurado' if llm_configured else 'NÃO configurado'})",
        storage_provider=settings.storage_provider,
    )

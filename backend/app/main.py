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

    # Criar usuário admin padrão se não existir
    await create_default_admin()

    yield


async def create_default_admin():
    """Cria o usuário admin padrão se o banco estiver vazio."""
    from sqlalchemy import select
    from backend.app.core.database import async_session
    from backend.app.core.security import hash_password
    from backend.app.models.models import User, UserRole

    async with async_session() as session:
        result = await session.execute(select(User).where(User.email == "admin@eeg.com"))
        if result.scalar_one_or_none() is None:
            admin = User(
                name="Dr. Admin",
                email="admin@eeg.com",
                hashed_password=hash_password("admin123"),
                role=UserRole.ADMIN,
                is_active=True,
            )
            session.add(admin)
            await session.commit()
            print("✅ Usuário admin criado (admin@eeg.com / admin123)")


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
    if settings.llm_provider == "ollama":
        llm_status = "ollama (configurado)"
    elif settings.llm_api_key and settings.llm_api_key != "COLOQUE-SUA-API-KEY-AQUI":
        llm_status = f"{settings.llm_provider} (configurado)"
    else:
        llm_status = f"{settings.llm_provider} (NÃO configurado)"

    return HealthResponse(
        status="ok",
        version=settings.app_version,
        database=db_type,
        llm_provider=llm_status,
        storage_provider=settings.storage_provider,
    )

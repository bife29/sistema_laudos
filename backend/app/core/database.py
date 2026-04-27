"""Conexão com banco de dados — SQLite (dev) ou PostgreSQL (prod)."""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from backend.app.core.config import get_settings

settings = get_settings()

engine = create_async_engine(
    settings.database_url,
    echo=settings.debug,
    # SQLite precisa de check_same_thread=False
    connect_args={"check_same_thread": False} if settings.is_sqlite else {"ssl": True} if "neon.tech" in settings.database_url else {},
    # Reconecta automaticamente se a conexão cair (Neon auto-suspend)
    pool_pre_ping=True,
    pool_recycle=300,
    pool_size=5,
    max_overflow=10,
)

async_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


async def get_db() -> AsyncSession:
    """Dependency: retorna uma sessão do banco."""
    async with async_session() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Cria as tabelas no banco (para desenvolvimento)."""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

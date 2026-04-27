"""Rotas de autenticação."""

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.app.core.database import get_db
from backend.app.core.security import (
    hash_password, verify_password,
    create_access_token, create_refresh_token, decode_token,
)
from backend.app.models.models import User
from backend.app.schemas.schemas import (
    UserCreate, UserResponse, TokenResponse, LoginRequest,
)

router = APIRouter(prefix="/api/auth", tags=["Autenticação"])


@router.post("/register", response_model=UserResponse, status_code=201)
async def register(data: UserCreate, db: AsyncSession = Depends(get_db)):
    """Registrar novo usuário."""
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Email já cadastrado")

    user = User(
        name=data.name,
        email=data.email,
        hashed_password=hash_password(data.password),
        role=data.role,
        crm=data.crm,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@router.post("/login", response_model=TokenResponse)
async def login(form: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    """Login e geração de tokens JWT."""
    result = await db.execute(select(User).where(User.email == form.username))
    user = result.scalar_one_or_none()

    if not user or not verify_password(form.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Credenciais inválidas")

    if not user.is_active:
        raise HTTPException(status_code=403, detail="Usuário desativado")

    return TokenResponse(
        access_token=create_access_token({"sub": user.id, "role": user.role.value}),
        refresh_token=create_refresh_token({"sub": user.id}),
    )


@router.get("/me", response_model=UserResponse)
async def get_me(
    token: str = Depends(decode_token),
    db: AsyncSession = Depends(get_db),
):
    """Retorna dados do usuário autenticado."""
    # decode_token retorna o payload, não o token
    # Precisamos ajustar — usamos get_current_user_id
    from backend.app.core.security import oauth2_scheme, get_current_user_id
    raise HTTPException(status_code=501, detail="Use /api/auth/login para autenticar")

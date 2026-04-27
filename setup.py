"""Script de setup inicial — cria .env, instala deps, cria usuário admin."""

import shutil
import subprocess
import sys
from pathlib import Path


BASE_DIR = Path(__file__).parent


def main():
    print("=" * 60)
    print("  SETUP — Sistema de Laudos EEG com IA")
    print("=" * 60)

    # 1. Criar .env se não existe
    env_file = BASE_DIR / ".env"
    env_example = BASE_DIR / ".env.example"
    if not env_file.exists():
        shutil.copy(env_example, env_file)
        print("\n✅ Arquivo .env criado a partir do .env.example")
        print("   ⚠️  EDITE o .env para configurar suas chaves (LLM_API_KEY, etc)")
    else:
        print("\n✅ Arquivo .env já existe")

    # 2. Criar diretórios
    (BASE_DIR / "data" / "uploads").mkdir(parents=True, exist_ok=True)
    print("✅ Diretório data/uploads criado")

    # 3. Instalar dependências Python
    print("\n📦 Instalando dependências Python...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-e", ".", "--quiet"])
    print("✅ Dependências instaladas")

    # 4. Criar banco e tabelas
    print("\n🗄️  Criando banco de dados...")
    import asyncio
    from backend.app.core.database import init_db
    asyncio.run(init_db())
    print("✅ Banco de dados criado (SQLite)")

    # 5. Criar usuário admin
    print("\n👤 Criando usuário admin padrão...")
    asyncio.run(create_admin())

    print("\n" + "=" * 60)
    print("  SETUP CONCLUÍDO!")
    print("=" * 60)
    print()
    print("  Para iniciar o backend:")
    print("    python -m uvicorn backend.app.main:app --reload")
    print()
    print("  Para iniciar o frontend:")
    print("    cd frontend && npm install && npm run dev")
    print()
    print("  Login padrão:")
    print("    Email: admin@eeg.com")
    print("    Senha: admin123")
    print()
    print("  API docs: http://localhost:8000/docs")
    print()


async def create_admin():
    from backend.app.core.database import async_session
    from backend.app.models.models import User, UserRole
    from backend.app.core.security import hash_password
    from sqlalchemy import select

    async with async_session() as db:
        result = await db.execute(select(User).where(User.email == "admin@eeg.com"))
        if result.scalar_one_or_none():
            print("   Usuário admin já existe")
            return

        admin = User(
            name="Administrador",
            email="admin@eeg.com",
            hashed_password=hash_password("admin123"),
            role=UserRole.ADMIN,
        )
        db.add(admin)
        await db.commit()
        print("   ✅ Usuário admin criado (admin@eeg.com / admin123)")


if __name__ == "__main__":
    main()

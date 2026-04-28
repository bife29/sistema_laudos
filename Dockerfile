FROM python:3.12-slim

WORKDIR /app

# Copiar código-fonte e dependências
COPY pyproject.toml setup.py ./
COPY backend/ backend/

# Instalar dependências
RUN pip install --no-cache-dir ".[prod]" asyncpg

COPY .env* ./

# Diretório para uploads e referências
RUN mkdir -p /app/data/uploads /app/data/uploads/references

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

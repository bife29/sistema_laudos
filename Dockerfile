FROM python:3.12-slim

WORKDIR /app

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[prod]" 2>/dev/null || pip install --no-cache-dir . && pip install asyncpg

COPY backend/ backend/
COPY .env* ./

# Diretório para uploads temporários
RUN mkdir -p /app/data/uploads

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

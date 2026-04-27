FROM python:3.12-slim

WORKDIR /app

# Dependências do sistema para MNE-Python
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc g++ && rm -rf /var/lib/apt/lists/*

COPY pyproject.toml .
RUN pip install --no-cache-dir -e ".[prod]" 2>/dev/null || pip install --no-cache-dir .

COPY backend/ backend/
COPY .env* ./

EXPOSE 8000

CMD ["uvicorn", "backend.app.main:app", "--host", "0.0.0.0", "--port", "8000"]

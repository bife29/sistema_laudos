# 🧠 Sistema de Laudos EEG com IA

Sistema web que utiliza Inteligência Artificial para auxiliar médicos na elaboração de laudos de Eletroencefalograma (EEG).

---

## 📋 O que o sistema faz

1. **Upload** do arquivo do exame (.EDF)
2. **Leitura automática** dos 19 canais do EEG
3. **Análise com IA** — detecta padrões anormais, assimetrias, ritmo de base
4. **Geração de laudo** em linguagem médica profissional (via Claude/OpenAI/Ollama)
5. **Revisão** pelo médico e exportação em PDF

---

## 🏗️ Estrutura do Projeto

```
Sistema de Laudos/
├── backend/                      # API Python (FastAPI)
│   └── app/
│       ├── api/                  # Rotas da API
│       │   ├── auth.py           # Login, registro, JWT
│       │   ├── patients.py       # CRUD de pacientes
│       │   └── exams.py          # Upload, análise, laudo
│       ├── core/                 # Configuração central
│       │   ├── config.py         # Todas as variáveis (.env)
│       │   ├── database.py       # Conexão com banco
│       │   └── security.py       # JWT, hash de senha
│       ├── models/
│       │   └── models.py         # Tabelas do banco (User, Patient, Exam, etc)
│       ├── schemas/
│       │   └── schemas.py        # Validação de dados (Pydantic)
│       ├── services/
│       │   ├── llm_provider.py   # LLM parametrizável (Anthropic/OpenAI/Ollama)
│       │   ├── storage.py        # Storage parametrizável (Local/S3/MinIO)
│       │   └── report_generator.py  # Geração de laudos
│       ├── ml/                   # Módulo de IA/Machine Learning
│       │   ├── edf_reader.py     # Leitura de arquivos .EDF
│       │   ├── preprocessing.py  # Filtros e processamento de sinal
│       │   └── analysis_pipeline.py  # Pipeline completo de análise
│       └── main.py               # App FastAPI
├── frontend/                     # Interface React
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx     # Tela de login
│   │   │   └── UploadPage.jsx    # Upload + análise + laudo
│   │   ├── services/
│   │   │   └── api.js            # Cliente HTTP (axios)
│   │   ├── App.jsx               # Roteamento
│   │   ├── main.jsx              # Entrada
│   │   └── index.css             # Estilos
│   ├── package.json
│   └── vite.config.js
├── docs/                         # Documentos do projeto (PDFs, escopo)
├── data/                         # Banco SQLite + uploads (criado automaticamente)
├── .env.example                  # Modelo de configuração
├── .gitignore
├── pyproject.toml                # Dependências Python
├── setup.py                      # Script de instalação
├── Dockerfile
├── docker-compose.yml
└── README.md                     # Este arquivo
```

---

## 🚀 Como executar (passo a passo)

### Pré-requisitos

- **Python 3.11+** instalado
- **Node.js 18+** instalado (para o frontend)
- **Git** instalado

### Passo 1 — Clonar e entrar no projeto

```bash
cd C:\Projetos\Michel\Sistema de Laudos
```

### Passo 2 — Executar o setup

```bash
python setup.py
```

Isso vai:
- Criar o arquivo `.env` (copiar do `.env.example`)
- Instalar as dependências Python
- Criar o banco de dados SQLite
- Criar o usuário admin padrão

### Passo 3 — Configurar o .env (IMPORTANTE)

Abra o arquivo `.env` e configure:

```env
# Se já tiver a API key da Anthropic:
LLM_API_KEY=sk-ant-api...

# Se NÃO tiver ainda, deixe como está — o sistema vai
# funcionar com um laudo de exemplo (mock)
```

### Passo 4 — Iniciar o backend

```bash
python -m uvicorn backend.app.main:app --reload
```

O backend inicia em: **http://localhost:8000**
Documentação da API: **http://localhost:8000/docs**

### Passo 5 — Iniciar o frontend

Em outro terminal:

```bash
cd frontend
npm install
npm run dev
```

O frontend inicia em: **http://localhost:5173**

### Passo 6 — Acessar o sistema

1. Abra **http://localhost:5173**
2. Login: `admin@eeg.com` / `admin123`
3. Envie um arquivo `.EDF`
4. Clique em "Analisar com IA"
5. Clique em "Gerar Laudo"

---

## ⚙️ Configurações parametrizáveis (.env)

Todas as integrações são configuráveis via `.env`:

### LLM (Inteligência Artificial)

| Variável | Opções | Descrição |
|---|---|---|
| `LLM_PROVIDER` | `anthropic`, `openai`, `ollama` | Qual IA usar |
| `LLM_MODEL` | `claude-sonnet-4-20250514`, `gpt-4o`, `llama3` | Modelo específico |
| `LLM_API_KEY` | sua chave | Chave da API |
| `LLM_BASE_URL` | URL | Para Ollama (local) |

### Banco de Dados

| Variável | Opções | Descrição |
|---|---|---|
| `DATABASE_URL` | `sqlite+aiosqlite:///./data/eeg.db` | SQLite (dev) |
| `DATABASE_URL` | `postgresql+asyncpg://user:pass@host/db` | PostgreSQL (prod) |

### Armazenamento de Arquivos

| Variável | Opções | Descrição |
|---|---|---|
| `STORAGE_PROVIDER` | `local`, `s3`, `minio` | Onde salvar os .EDF |
| `STORAGE_LOCAL_PATH` | caminho | Pasta local |
| `STORAGE_S3_BUCKET` | nome | Bucket S3/MinIO |

### Hospedagem

| Variável | Opções | Descrição |
|---|---|---|
| `CORS_ORIGINS` | URLs | Origens permitidas (frontend) |

---

## 🐳 Com Docker (alternativa)

Se preferir usar Docker:

```bash
# Copiar .env
cp .env.example .env

# Subir tudo
docker-compose up --build
```

Acesse:
- Backend: http://localhost:8000
- Frontend: http://localhost:5173
- Banco PostgreSQL: localhost:5432

---

## 📡 Endpoints da API

| Método | Endpoint | Descrição |
|---|---|---|
| `POST` | `/api/auth/register` | Criar usuário |
| `POST` | `/api/auth/login` | Login (retorna JWT) |
| `POST` | `/api/patients/` | Criar paciente |
| `GET` | `/api/patients/` | Listar pacientes |
| `POST` | `/api/exams/upload` | Upload de arquivo .EDF |
| `POST` | `/api/exams/{id}/analyze` | Analisar exame com IA |
| `POST` | `/api/exams/{id}/generate-report` | Gerar laudo |
| `GET` | `/api/exams/{id}/report` | Ver laudo gerado |
| `GET` | `/api/health` | Status do sistema |

Documentação interativa: **http://localhost:8000/docs**

---

## 🔄 Trocar de provedor LLM

### Para usar OpenAI ao invés de Claude:
```env
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
LLM_API_KEY=sk-...
```

### Para usar Ollama (gratuito, local):
```env
LLM_PROVIDER=ollama
LLM_MODEL=llama3
LLM_BASE_URL=http://localhost:11434
LLM_API_KEY=não-necessário
```

### Para usar PostgreSQL ao invés de SQLite:
```env
DATABASE_URL=postgresql+asyncpg://eeg_user:eeg_pass@localhost:5432/eeg_laudos
```

---

## 📌 Pendências para funcionar 100%

| Item | Status | O que fazer |
|---|---|---|
| Arquivo .EDF de exemplo | ⏳ Pendente | Enviar um arquivo .EDF do aparelho de EEG |
| API Key Anthropic | ⏳ Pendente | Criar conta em console.anthropic.com |
| Node.js | Verificar | `node --version` (precisa 18+) |

Sem o arquivo .EDF, o upload funciona mas a análise não roda.
Sem a API key, o laudo gerado será um texto de exemplo (mock).

---

## 📝 Licença

Projeto privado — uso exclusivo.

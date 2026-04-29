# 🧠 Sistema de Laudos EEG com IA

Sistema web que utiliza Inteligência Artificial para auxiliar médicos na elaboração de laudos de Eletroencefalograma (EEG).

> 📐 **[Documentação Arquitetural (C4 Model)](README_C4.md)** — Diagramas de contexto, containers, componentes, fluxos e deploy.

---

## 📋 O que o sistema faz

1. **Upload** do arquivo do exame (.EDF)
2. **Leitura automática** dos 19 canais do EEG
3. **Análise com IA** — detecta padrões anormais, assimetrias, ritmo de base
4. **Geração de laudo** em linguagem médica profissional (via Claude/OpenAI/Ollama)
5. **Base de conhecimento (RAG)** — laudos aprovados e livros de referência enriquecem os próximos laudos
6. **Revisão** pelo médico e exportação em PDF

---

## 🏗️ Estrutura do Projeto

```
Sistema de Laudos/
├── backend/                      # API Python (FastAPI)
│   └── app/
│       ├── api/                  # Rotas da API
│       │   ├── auth.py           # Login, registro, JWT
│       │   ├── patients.py       # CRUD de pacientes
│       │   ├── exams.py          # Upload, análise, laudo
│       │   └── references.py     # Upload de livros e referências (RAG)
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
│       │   ├── report_generator.py  # Geração de laudos
│       │   ├── embedding_service.py # Embeddings para busca semântica (RAG)
│       │   ├── rag_service.py       # Busca de laudos similares e referências
│       │   └── pdf_ingestion.py     # Ingestão de livros/PDFs de referência
│       ├── ml/                   # Módulo de IA/Machine Learning
│       │   ├── edf_reader.py     # Leitura de arquivos .EDF
│       │   ├── preprocessing.py  # Filtros e processamento de sinal
│       │   └── analysis_pipeline.py  # Pipeline completo de análise
│       └── main.py               # App FastAPI
├── frontend/                     # Interface React
│   ├── src/
│   │   ├── pages/
│   │   │   ├── LoginPage.jsx     # Tela de login
│   │   │   ├── DashboardPage.jsx # Painel com listagem de exames
│   │   │   ├── UploadPage.jsx    # Upload + análise + laudo
│   │   │   ├── ReportPage.jsx    # Visualização/edição/aprovação de laudo
│   │   │   └── ReferencesPage.jsx # Gerenciamento de referências RAG
│   │   ├── services/
│   │   │   └── api.js            # Cliente HTTP (axios)
│   │   ├── App.jsx               # Roteamento
│   │   ├── main.jsx              # Entrada
│   │   └── index.css             # Estilos
│   ├── e2e/                      # Testes E2E (Playwright)
│   │   └── app.spec.js           # 40 testes de UI contra produção
│   ├── playwright.config.js      # Configuração Playwright
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

### RAG — Base de Conhecimento

| Variável | Opções | Descrição |
|---|---|---|
| `RAG_ENABLED` | `true`, `false` | Habilitar base de conhecimento |
| `EMBEDDING_PROVIDER` | `none`, `ollama`, `openai` | Provedor de embeddings |
| `EMBEDDING_MODEL` | `nomic-embed-text`, `text-embedding-3-small` | Modelo de embedding |
| `EMBEDDING_API_KEY` | sua chave | Chave da API (OpenAI) |
| `EMBEDDING_BASE_URL` | URL | URL do Ollama |

---

## 🧪 Testes

O projeto conta com **dois níveis de testes E2E** que rodam **diretamente contra produção**:

### Testes de API (Backend)

Validam todos os endpoints da API em produção via HTTP direto (sem browser):

```bash
python test_e2e_prod.py --verbose
```

**24 testes** cobrindo: health, autenticação, pacientes, exames, laudos, RAG, storage, CORS e segurança.

### Testes de UI (Frontend + Backend)

Validam a aplicação completa via browser real (Playwright/Chromium) contra produção:

```bash
cd frontend
npm run test:e2e            # headless (CI)
npm run test:e2e:headed     # com browser visível (debug)
npm run test:e2e:report     # abrir relatório HTML
```

**40 testes** cobrindo:

| Suite | O que valida |
|---|---|
| 1. Login | Formulário, login válido/inválido, redirect sem auth |
| 2. Navegação | Header, links (Painel, Upload, Referências), logout |
| 3. Dashboard | Listagem de exames, status, botões de ação |
| 4. Upload | Formulário, validação de campos, aceita .EDF |
| 5. Laudo | Visualização, edição, cancelar, aprovar, exportar PDF |
| 6. Referências RAG | Stats, upload de PDF, fontes cadastradas, remoção |
| 7. UI/UX | Título, console sem erros, loading states |
| 8. Integração | Dados reais da API chegam ao frontend |

### Onde rodam

Ambos os testes rodam **contra os ambientes de produção**:
- Backend: `https://eeg-laudos-api.onrender.com`
- Frontend: `https://sistemalaudos.vercel.app`

Isso garante que o sistema inteiro — deploy, build, banco, storage, LLM — está funcional.

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
| `GET` | `/api/exams/` | Listar exames |
| `GET` | `/api/exams/{id}` | Detalhes do exame |
| `POST` | `/api/exams/{id}/analyze` | Analisar exame com IA |
| `POST` | `/api/exams/{id}/generate-report` | Gerar laudo |
| `GET` | `/api/exams/{id}/report` | Ver laudo gerado |
| `PUT` | `/api/exams/{id}/report` | Editar texto do laudo |
| `POST` | `/api/exams/{id}/report/approve` | Aprovar laudo (assinatura) |
| `GET` | `/api/exams/{id}/report/pdf` | Baixar laudo em PDF |
| `POST` | `/api/references/upload-pdf` | Upload de livro/referência médica |
| `GET` | `/api/references/sources` | Listar fontes de referência |
| `GET` | `/api/references/stats` | Estatísticas do RAG |
| `DELETE` | `/api/references/sources/{nome}` | Remover uma fonte |
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

## � Base de Conhecimento (RAG)

O sistema possui uma base de conhecimento que **aprende e melhora continuamente**. Ele combina três fontes de informação para gerar laudos cada vez mais precisos:

### Como funciona

| Fonte | O que faz | Quando atua |
|---|---|---|
| **IA (LLM)** | Conhecimento médico geral e linguagem profissional | Sempre — é o motor de geração |
| **Laudos aprovados** | Padrões reais do consultório e estilo do médico | Automático — cada laudo aprovado alimenta a base |
| **Livros de referência** | Fundamentação científica e critérios diagnósticos | Manual — upload de PDFs pelo médico |

### Ciclo de melhoria contínua

1. O médico **aprova um laudo** → o sistema armazena como referência
2. No próximo exame similar → o sistema **busca laudos aprovados com padrão parecido**
3. O LLM recebe esses exemplos como contexto → gera um laudo **mais alinhado com a prática do médico**
4. Com o tempo, os laudos ficam mais consistentes e requerem menos edições

### Adicionando livros de referência

O sistema aceita PDFs de livros de medicina/neurologia (até 1000+ páginas). Os trechos relevantes são automaticamente recuperados durante a geração do laudo.

**Via API (Swagger):** `POST /api/references/upload-pdf`

```bash
# Via linha de comando:
curl -X POST http://localhost:8000/api/references/upload-pdf \
  -H "Authorization: Bearer SEU_TOKEN" \
  -F "file=@/caminho/do/livro.pdf" \
  -F "source_name=Niedermeyer EEG"
```

Os PDFs são salvos em `data/uploads/references/` e o texto é indexado automaticamente.

### Configuração do RAG

Para ativar com Ollama (gratuito, local):
```env
RAG_ENABLED=true
EMBEDDING_PROVIDER=ollama
EMBEDDING_MODEL=nomic-embed-text
EMBEDDING_BASE_URL=http://localhost:11434
```

Para ativar com OpenAI (pago, ~R$ 0,10/1M tokens):
```env
RAG_ENABLED=true
EMBEDDING_PROVIDER=openai
EMBEDDING_MODEL=text-embedding-3-small
EMBEDDING_API_KEY=sk-...
```

> **Nota:** Com `EMBEDDING_PROVIDER=none`, o RAG está habilitado estruturalmente mas não processa embeddings. O sistema funciona normalmente sem impacto.

---

## �📌 Pendências para funcionar 100%

| Item | Status | O que fazer |
|---|---|---|
| Arquivo .EDF de exemplo | ⏳ Pendente | Enviar um arquivo .EDF do aparelho de EEG |
| API Key Anthropic | ⏳ Pendente | Criar conta em console.anthropic.com |
| Livro de referência (PDF) | ⏳ Pendente | Upload via API quando disponível |
| Provedor de embeddings | ⏳ Pendente | Configurar Ollama ou OpenAI para ativar RAG |
| Node.js | Verificar | `node --version` (precisa 18+) |

Sem o arquivo .EDF, o upload funciona mas a análise não roda.
Sem a API key, o laudo gerado será um texto de exemplo (mock).

---

## 📝 Licença

Software proprietário — **Todos os direitos reservados.**

**© 2026 Michel Bueno Silva e Matheus Bueno Ribeiro da Silva**

Consulte o arquivo [LICENSE](LICENSE) para detalhes completos.
Documentação de registro: [docs/REGISTRO_PROPRIEDADE_INTELECTUAL.md](docs/REGISTRO_PROPRIEDADE_INTELECTUAL.md)

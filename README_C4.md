# 🧠 Sistema de Laudos EEG com IA — Documentação Arquitetural (C4 Model)

> Documentação baseada no [C4 Model](https://c4model.com) — uma abordagem de diagramação de arquitetura de software em 4 níveis de abstração.

---

## 📐 Nível 1 — Contexto do Sistema

Visão de alto nível: quem usa o sistema e com quais serviços externos ele se comunica.

```mermaid
C4Context
    title Sistema de Laudos EEG - Contexto do Sistema (Nível 1)

    Person(medico, "Médico Neurologista", "Realiza upload de EEG, revisa e aprova laudos gerados por IA")

    System(sistema, "Sistema de Laudos EEG", "Plataforma web que analisa exames EEG com IA e gera laudos médicos automatizados")

    System_Ext(openai, "OpenAI API", "GPT-4o-mini para geração de laudos + text-embedding-3-small para RAG")
    System_Ext(neon, "Neon PostgreSQL", "Banco de dados relacional na nuvem (serverless)")
    System_Ext(r2, "Cloudflare R2", "Armazenamento de arquivos EDF (S3-compatível)")
    System_Ext(vercel, "Vercel", "Hospedagem do frontend React")
    System_Ext(render, "Render", "Hospedagem do backend FastAPI (Docker)")

    Rel(medico, sistema, "Acessa via navegador", "HTTPS")
    Rel(sistema, openai, "Gera laudos e embeddings", "HTTPS/API")
    Rel(sistema, neon, "Persiste dados", "PostgreSQL/SSL")
    Rel(sistema, r2, "Armazena arquivos EDF", "S3 API/HTTPS")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

**Decisões-chave:**
| Decisão | Motivo |
|---|---|
| OpenAI (única API key) | Serve tanto LLM (gpt-4o-mini) quanto Embeddings (text-embedding-3-small) |
| Neon PostgreSQL | Serverless, free tier generoso, compatível com asyncpg |
| Cloudflare R2 | 10 GB grátis, S3-compatível, sem egress fees |
| Render (Docker) | Deploy automático via GitHub, free tier para testes |
| Vercel | Deploy estático otimizado para React SPA |

---

## 📦 Nível 2 — Diagrama de Containers

Zoom no sistema: quais são os principais containers (aplicações/serviços) e como se comunicam.

```mermaid
C4Container
    title Sistema de Laudos EEG - Diagrama de Containers (Nível 2)

    Person(medico, "Médico Neurologista", "Revisa e aprova laudos EEG")

    Container_Boundary(sistema, "Sistema de Laudos EEG") {
        Container(spa, "Frontend SPA", "React 18, Vite 5", "Interface web para upload, análise e revisão de laudos")
        Container(api, "Backend API", "FastAPI, Python 3.12", "API REST: autenticação, análise EEG, geração de laudos, RAG")
        Container(ml, "Módulo ML/EEG", "edfio, NumPy, SciPy", "Leitura de EDF, processamento de sinais, detecção de padrões")
        Container(rag, "Módulo RAG", "OpenAI Embeddings", "Base de conhecimento: laudos aprovados + livros de referência")
    }

    System_Ext(openai, "OpenAI API", "LLM + Embeddings")
    System_Ext(neon, "Neon PostgreSQL", "Banco de dados")
    System_Ext(r2, "Cloudflare R2", "Storage de arquivos")

    Rel(medico, spa, "Acessa", "HTTPS")
    Rel(spa, api, "Requisições", "REST/JSON")
    Rel(api, ml, "Executa análise EEG")
    Rel(api, rag, "Busca contexto similar")
    Rel(api, openai, "Gera laudo / embeddings", "HTTPS")
    Rel(api, neon, "CRUD", "asyncpg/SSL")
    Rel(api, r2, "Upload/Download EDF", "boto3/S3")

    UpdateLayoutConfig($c4ShapeInRow="3", $c4BoundaryInRow="1")
```

**Tecnologias por container:**
| Container | Stack | Hospedagem |
|---|---|---|
| Frontend SPA | React 18 + Vite 5 + Axios | Vercel |
| Backend API | FastAPI + SQLAlchemy 2.0 + Pydantic | Render (Docker) |
| Módulo ML/EEG | edfio + NumPy + SciPy | Embarcado no backend |
| Módulo RAG | OpenAI Embeddings + Cosine Similarity | Embarcado no backend |

---

## 🔧 Nível 3 — Componentes do Backend

Zoom no container "Backend API": cada módulo e suas responsabilidades.

```mermaid
C4Component
    title Backend API - Diagrama de Componentes (Nível 3)

    Container_Boundary(api, "Backend API — FastAPI") {

        Component(auth, "Auth Controller", "api/auth.py", "Login, registro, JWT tokens")
        Component(patients, "Patients Controller", "api/patients.py", "CRUD de pacientes")
        Component(exams, "Exams Controller", "api/exams.py", "Upload EDF, análise, geração de laudo")
        Component(refs, "References Controller", "api/references.py", "Upload de PDFs médicos para RAG")

        Component(security, "Security", "core/security.py", "Hash de senhas, validação JWT")
        Component(config, "Config", "core/config.py", "Variáveis de ambiente (.env)")

        Component(llm, "LLM Provider", "services/llm_provider.py", "Abstração: OpenAI / Anthropic / Ollama")
        Component(report, "Report Generator", "services/report_generator.py", "Monta prompt médico e chama LLM")
        Component(storage, "Storage Provider", "services/storage.py", "Abstração: Local / R2 / S3")
        Component(embed, "Embedding Service", "services/embedding_service.py", "Gera vetores: OpenAI / Ollama")
        Component(ragsvc, "RAG Service", "services/rag_service.py", "Busca laudos similares e referências")
        Component(ingest, "PDF Ingestion", "services/pdf_ingestion.py", "Extrai texto, chunka e indexa PDFs")

        Component(pipeline, "Analysis Pipeline", "ml/analysis_pipeline.py", "Pipeline completo de análise EEG")
        Component(edf, "EDF Reader", "ml/edf_reader.py", "Leitura de arquivos .EDF via edfio")
        Component(preproc, "Preprocessing", "ml/preprocessing.py", "Filtros e processamento de sinais")
    }

    Rel(exams, storage, "Save/Load EDF")
    Rel(exams, pipeline, "Executa análise")
    Rel(exams, report, "Gera laudo")
    Rel(exams, ragsvc, "Busca contexto RAG")
    Rel(report, llm, "Chama LLM")
    Rel(ragsvc, embed, "Gera embeddings")
    Rel(refs, ingest, "Processa PDF")
    Rel(ingest, embed, "Gera embeddings dos chunks")
    Rel(pipeline, edf, "Lê .EDF")
    Rel(pipeline, preproc, "Filtra sinais")
    Rel(auth, security, "Valida credenciais")

    UpdateLayoutConfig($c4ShapeInRow="4", $c4BoundaryInRow="1")
```

**Padrão Strategy (plugável via .env):**
| Abstração | Implementações | Variável |
|---|---|---|
| LLM Provider | OpenAI, Anthropic, Ollama, Mock | `LLM_PROVIDER` |
| Storage Provider | Local, Cloudflare R2, AWS S3, MinIO | `STORAGE_PROVIDER` |
| Embedding Provider | OpenAI, Ollama, None | `EMBEDDING_PROVIDER` |

---

## 🔄 Fluxo Principal — Do Upload à Aprovação

O fluxo completo de um exame EEG, passando por todas as etapas do sistema.

```mermaid
flowchart TD
    subgraph UPLOAD ["1. Upload do Exame"]
        A1[Médico seleciona .EDF] --> A2[Frontend envia arquivo]
        A2 --> A3[API valida extensão .EDF]
        A3 --> A4{Storage Provider}
        A4 -->|Local| A5[Salva em disco]
        A4 -->|R2/S3| A6[Upload via boto3]
        A5 --> A7[Cria registro no PostgreSQL<br/>Status: UPLOADED]
        A6 --> A7
    end

    subgraph ANALISE ["2. Análise com IA"]
        B1[Médico clica Analisar] --> B2[API carrega EDF do storage]
        B2 --> B3[edfio lê canais do EEG]
        B3 --> B4[Filtros: bandpass 0.5-50Hz<br/>notch 60Hz]
        B4 --> B5[Extrai ritmo de base<br/>Detecta spikes<br/>Analisa assimetria]
        B5 --> B6[Classifica: normal /<br/>anormal / indeterminado]
        B6 --> B7[Salva Analysis no DB<br/>Status: ANALYZED]
    end

    subgraph LAUDO ["3. Geração de Laudo"]
        C1[Médico clica Gerar Laudo] --> C2[Monta resumo da análise]
        C2 --> C3{RAG habilitado?}
        C3 -->|Sim| C4[Busca laudos similares<br/>+ referências médicas]
        C3 -->|Não| C5[Sem contexto extra]
        C4 --> C6[Monta prompt médico<br/>com contexto RAG]
        C5 --> C6
        C6 --> C7[Envia para LLM<br/>OpenAI / Anthropic / Ollama]
        C7 --> C8[Salva Report no DB<br/>Status: DRAFT]
    end

    subgraph APROVACAO ["4. Revisão e Aprovação"]
        D1[Médico revisa laudo] --> D2{Edita?}
        D2 -->|Sim| D3[Atualiza texto<br/>Status: REVIEW]
        D2 -->|Não| D4[Aprova laudo]
        D3 --> D4
        D4 --> D5[Status: APPROVED]
        D5 --> D6{RAG habilitado?}
        D6 -->|Sim| D7[Gera embedding do laudo<br/>Armazena para aprendizado]
        D6 -->|Não| D8[Fim]
        D7 --> D8
    end

    UPLOAD --> ANALISE --> LAUDO --> APROVACAO

    style UPLOAD fill:#e1f5fe,stroke:#0288d1
    style ANALISE fill:#f3e5f5,stroke:#7b1fa2
    style LAUDO fill:#e8f5e9,stroke:#388e3c
    style APROVACAO fill:#fff3e0,stroke:#f57c00
```

---

## 🧠 Fluxo RAG — Base de Conhecimento e Aprendizado Contínuo

Como o sistema aprende com laudos aprovados e referências médicas para gerar laudos cada vez melhores.

```mermaid
flowchart TD
    subgraph RAG ["Ciclo RAG - Aprendizado Contínuo"]
        direction TB

        subgraph FONTES ["Fontes de Conhecimento"]
            F1[📚 Livros de Referência<br/>PDFs médicos]
            F2[✅ Laudos Aprovados<br/>Histórico do médico]
        end

        subgraph INGESTAO ["Ingestão de PDFs"]
            I1[Upload PDF] --> I2[pypdf extrai texto]
            I2 --> I3[Divide em chunks<br/>800 palavras, overlap 100]
            I3 --> I4[OpenAI gera embedding<br/>por chunk]
            I4 --> I5[Salva em<br/>reference_chunks DB]
        end

        subgraph APROVACAO_EMB ["Aprovação → Embedding"]
            A1[Médico aprova laudo] --> A2[Texto do laudo final]
            A2 --> A3[OpenAI gera embedding]
            A3 --> A4[Salva em<br/>report_embeddings DB]
        end

        subgraph BUSCA ["Busca na Geração do Laudo"]
            B1[Nova análise EEG] --> B2[Gera embedding<br/>do resumo]
            B2 --> B3[Similaridade de cosseno<br/>vs report_embeddings]
            B2 --> B4[Similaridade de cosseno<br/>vs reference_chunks]
            B3 --> B5[Top 3 laudos similares<br/>threshold > 0.30]
            B4 --> B6[Top 3 referências<br/>threshold > 0.25]
            B5 --> B7[Contexto RAG montado]
            B6 --> B7
            B7 --> B8[Enviado ao LLM<br/>junto com o prompt]
        end

        F1 --> INGESTAO
        F2 --> APROVACAO_EMB
        INGESTAO --> BUSCA
        APROVACAO_EMB --> BUSCA
    end

    style FONTES fill:#e3f2fd,stroke:#1565c0
    style INGESTAO fill:#fce4ec,stroke:#c62828
    style APROVACAO_EMB fill:#e8f5e9,stroke:#2e7d32
    style BUSCA fill:#fff8e1,stroke:#f9a825
```

**Parâmetros RAG:**
| Parâmetro | Valor | Descrição |
|---|---|---|
| Modelo de Embedding | `text-embedding-3-small` | 1536 dimensões |
| Chunk size | 800 palavras | Com overlap de 100 palavras |
| Top-K laudos | 3 | Similaridade mínima: 0.30 |
| Top-K referências | 3 | Similaridade mínima: 0.25 |
| Batch size (ingestão) | 20 chunks/batch | Controle de memória |

---

## 🏗️ Arquitetura de Deploy

Infraestrutura em produção e comunicação entre serviços.

```mermaid
flowchart LR
    subgraph DEPLOY ["Arquitetura de Deploy"]
        direction TB

        subgraph CLIENTE ["Cliente"]
            Browser[🌐 Navegador]
        end

        subgraph VERCEL ["Vercel (Frontend)"]
            SPA[React SPA<br/>sistemalaudos.vercel.app]
        end

        subgraph RENDER ["Render (Backend)"]
            Docker[Docker Container<br/>Python 3.12]
            FastAPI[FastAPI + Uvicorn<br/>eeg-laudos-api.onrender.com]
            Docker --> FastAPI
        end

        subgraph DADOS ["Serviços de Dados"]
            Neon[(Neon PostgreSQL<br/>Serverless)]
            R2[(Cloudflare R2<br/>Object Storage)]
        end

        subgraph IA ["Serviços de IA"]
            OpenAI_LLM[OpenAI GPT-4o-mini<br/>Geração de laudos]
            OpenAI_EMB[OpenAI Embeddings<br/>text-embedding-3-small]
        end

        Browser -->|HTTPS| SPA
        SPA -->|REST/JSON| FastAPI
        FastAPI -->|asyncpg/SSL| Neon
        FastAPI -->|boto3/S3 API| R2
        FastAPI -->|HTTPS| OpenAI_LLM
        FastAPI -->|HTTPS| OpenAI_EMB
    end

    style CLIENTE fill:#f5f5f5,stroke:#616161
    style VERCEL fill:#000000,stroke:#ffffff,color:#ffffff
    style RENDER fill:#46548a,stroke:#ffffff,color:#ffffff
    style DADOS fill:#e8eaf6,stroke:#283593
    style IA fill:#e8f5e9,stroke:#1b5e20
```

**URLs de produção:**
| Serviço | URL |
|---|---|
| Frontend | https://sistemalaudos.vercel.app |
| Backend API | https://eeg-laudos-api.onrender.com |
| API Docs (Swagger) | https://eeg-laudos-api.onrender.com/docs |
| Health Check | https://eeg-laudos-api.onrender.com/api/health |

---

## 🗄️ Modelo de Dados

Diagrama entidade-relacionamento com todas as tabelas do sistema.

```mermaid
erDiagram
    USER ||--o{ EXAM : "gerencia"
    USER ||--o{ REPORT : "aprova"
    PATIENT ||--o{ EXAM : "realiza"
    EXAM ||--o| ANALYSIS : "gera"
    EXAM ||--o| REPORT : "possui"
    REPORT ||--o| REPORT_EMBEDDING : "alimenta RAG"

    USER {
        uuid id PK
        string name
        string email UK
        string hashed_password
        enum role "admin | doctor | technician"
        string crm
        bool is_active
    }

    PATIENT {
        uuid id PK
        string name
        date birth_date
        string gender
        string medical_record
    }

    EXAM {
        uuid id PK
        uuid patient_id FK
        string file_path
        string file_name
        enum status "uploaded | processing | analyzed | error"
        float duration_seconds
        int n_channels
        float sampling_rate
    }

    ANALYSIS {
        uuid id PK
        uuid exam_id FK
        enum classification "normal | anormal | indeterminado"
        float base_rhythm_hz
        bool has_asymmetry
        json detected_patterns
        int spike_count
    }

    REPORT {
        uuid id PK
        uuid exam_id FK
        text generated_text
        text final_text
        enum status "draft | review | approved"
        string llm_provider
        string llm_model
        uuid approved_by_id FK
        datetime approved_at
    }

    REPORT_EMBEDDING {
        uuid id PK
        uuid report_id FK
        uuid exam_id FK
        text text_summary
        binary embedding "1536 dims"
        string classification
    }

    REFERENCE_CHUNK {
        uuid id PK
        string source_name
        string source_file
        string chapter
        int page_start
        int page_end
        int chunk_index
        text text
        binary embedding "1536 dims"
    }
```

---

## 📡 Mapa de Endpoints da API

```mermaid
flowchart LR
    subgraph AUTH ["🔐 Auth"]
        POST_REG[POST /api/auth/register]
        POST_LOG[POST /api/auth/login]
        GET_ME[GET /api/auth/me]
    end

    subgraph PATIENTS ["👤 Patients"]
        POST_PAT[POST /api/patients/]
        GET_PATS[GET /api/patients/]
    end

    subgraph EXAMS ["🧪 Exams"]
        POST_UP[POST /api/exams/upload]
        POST_AN[POST /api/exams/:id/analyze]
        POST_GEN[POST /api/exams/:id/generate-report]
        GET_EX[GET /api/exams/:id]
        GET_REP[GET /api/exams/:id/report]
        PUT_REP[PUT /api/exams/:id/report]
        POST_APR[POST /api/exams/:id/report/approve]
    end

    subgraph REFS ["📚 References"]
        POST_PDF[POST /api/references/upload-pdf]
        GET_SRC[GET /api/references/sources]
        GET_STAT[GET /api/references/stats]
        DEL_SRC[DELETE /api/references/sources/:name]
    end

    subgraph SYS ["⚙️ Sistema"]
        GET_HP[GET /api/health]
    end

    POST_UP -->|arquivo .EDF| POST_AN
    POST_AN -->|análise pronta| POST_GEN
    POST_GEN -->|laudo gerado| PUT_REP
    PUT_REP -->|texto revisado| POST_APR

    style AUTH fill:#e8eaf6,stroke:#3f51b5
    style PATIENTS fill:#e0f2f1,stroke:#00897b
    style EXAMS fill:#fff3e0,stroke:#ef6c00
    style REFS fill:#fce4ec,stroke:#c62828
    style SYS fill:#f5f5f5,stroke:#616161
```

---

## 🔑 Configurações Plugáveis (Strategy Pattern)

O sistema é totalmente parametrizável via variáveis de ambiente:

```mermaid
flowchart TD
    subgraph CONFIG ["Configuração via .env"]
        direction LR

        subgraph LLM_CFG ["LLM_PROVIDER"]
            LLM_OAI[openai<br/>GPT-4o-mini]
            LLM_ANT[anthropic<br/>Claude Sonnet]
            LLM_OLL[ollama<br/>Llama 3 local]
            LLM_MOCK[mock<br/>Texto exemplo]
        end

        subgraph STORAGE_CFG ["STORAGE_PROVIDER"]
            ST_LOCAL[local<br/>Disco /data/uploads]
            ST_R2[r2<br/>Cloudflare R2]
            ST_S3[s3<br/>AWS S3]
            ST_MINIO[minio<br/>Self-hosted]
        end

        subgraph EMB_CFG ["EMBEDDING_PROVIDER"]
            EMB_OAI[openai<br/>text-embedding-3-small]
            EMB_OLL[ollama<br/>nomic-embed-text]
            EMB_NONE[none<br/>RAG desabilitado]
        end

        subgraph DB_CFG ["DATABASE_URL"]
            DB_SQLITE[sqlite<br/>Desenvolvimento]
            DB_PG[postgresql<br/>Produção Neon]
        end
    end

    style LLM_CFG fill:#e8f5e9,stroke:#2e7d32
    style STORAGE_CFG fill:#e3f2fd,stroke:#1565c0
    style EMB_CFG fill:#fff8e1,stroke:#f9a825
    style DB_CFG fill:#f3e5f5,stroke:#7b1fa2
```

---

> **Referência:** Esta documentação segue o [C4 Model](https://c4model.com) de Simon Brown.
> Diagramas renderizados com [Mermaid.js](https://mermaid.js.org/) — compatíveis com GitHub, GitLab e VS Code.

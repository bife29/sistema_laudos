# 🧠 Sistema de Laudos EEG com IA

### Geração automatizada de laudos de Eletroencefalograma com Inteligência Artificial

<br/>

> **Projeto full-stack** que combina processamento de sinais biomédicos, IA generativa (LLM) e RAG (Retrieval-Augmented Generation) para automatizar a elaboração de laudos de EEG — com aprendizado contínuo a partir da prática do médico.

<br/>

| | |
|---|---|
| **Backend** | Python 3.12 · FastAPI · SQLAlchemy 2.0 · asyncpg |
| **Frontend** | React 18 · Vite 5 · Axios |
| **IA** | OpenAI GPT-4o-mini · RAG com Embeddings |
| **Infra** | Render (Docker) · Vercel · Neon PostgreSQL · Cloudflare R2 |
| **Padrões** | Strategy Pattern · Async/Await · JWT Auth · S3-compatible Storage |

---

## 🎯 Como funciona — Visão para não-técnicos

O fluxo completo em 5 passos simples:

```mermaid
flowchart TB
    subgraph JORNADA [" "]
        direction TB
        
        S1["📤 &nbsp; <b>Upload</b><br/>O médico envia o arquivo<br/>do exame de EEG (.EDF)"]
        S2["🔬 &nbsp; <b>Análise Automática</b><br/>A IA lê os 19 canais do EEG<br/>e detecta padrões anormais"]
        S3["📝 &nbsp; <b>Laudo Gerado por IA</b><br/>O sistema gera o laudo completo<br/>em linguagem médica profissional"]
        S4["✏️ &nbsp; <b>Revisão Médica</b><br/>O médico revisa, edita se<br/>necessário e aprova o laudo"]
        S5["🧠 &nbsp; <b>IA Aprende</b><br/>O laudo aprovado alimenta a base<br/>de conhecimento — laudos futuros<br/>ficam cada vez melhores"]

        S1 --> S2 --> S3 --> S4 --> S5
        S5 -.->|"melhoria contínua"| S3
    end

    style S1 fill:#e3f2fd,stroke:#1976d2,stroke-width:2px,color:#0d47a1
    style S2 fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px,color:#4a148c
    style S3 fill:#e8f5e9,stroke:#388e3c,stroke-width:2px,color:#1b5e20
    style S4 fill:#fff3e0,stroke:#f57c00,stroke-width:2px,color:#e65100
    style S5 fill:#fce4ec,stroke:#c62828,stroke-width:2px,color:#b71c1c
    style JORNADA fill:transparent,stroke:none
```

> **Diferencial:** Cada laudo aprovado pelo médico é armazenado como referência. Quanto mais o sistema é usado, mais os laudos se alinham com o estilo e padrão do profissional.

---

## ☁️ Arquitetura Cloud — Serviços e Integrações

Visão geral de todos os serviços e como se comunicam:

```mermaid
flowchart TB
    subgraph INFRA [" "]
        direction TB
        
        USER(("👨‍⚕️<br/>Médico"))
        
        subgraph FRONT ["  🖥️  Frontend  "]
            REACT["<b>React 18</b><br/>Interface moderna e responsiva"]
        end
        
        subgraph BACK ["  ⚙️  Backend  "]
            API["<b>FastAPI</b><br/>API de alta performance"]
            ML["<b>Motor de Análise EEG</b><br/>edfio + NumPy + SciPy"]
            RAG["<b>Base de Conhecimento</b><br/>RAG com embeddings"]
        end
        
        subgraph CLOUD ["  ☁️  Cloud Services  "]
            OPENAI["<b>OpenAI</b><br/>GPT-4o-mini + Embeddings"]
            NEON[("<b>Neon</b><br/>PostgreSQL")]
            R2[("<b>Cloudflare R2</b><br/>Object Storage")]
        end

        USER -->|"HTTPS"| REACT
        REACT -->|"REST API"| API
        API --> ML
        API --> RAG
        API -->|"Gera laudos"| OPENAI
        API -->|"Dados"| NEON
        API -->|"Arquivos EDF"| R2
        RAG -->|"Embeddings"| OPENAI
    end
    
    style USER fill:#ffffff,stroke:#1976d2,stroke-width:3px,color:#0d47a1
    style REACT fill:#61dafb,stroke:#0d47a1,stroke-width:2px,color:#000000
    style API fill:#009688,stroke:#004d40,stroke-width:2px,color:#ffffff
    style ML fill:#7e57c2,stroke:#4527a0,stroke-width:2px,color:#ffffff
    style RAG fill:#ff7043,stroke:#bf360c,stroke-width:2px,color:#ffffff
    style OPENAI fill:#10a37f,stroke:#0a6847,stroke-width:2px,color:#ffffff
    style NEON fill:#3ecf8e,stroke:#1a7f5a,stroke-width:2px,color:#000000
    style R2 fill:#f6821f,stroke:#a85400,stroke-width:2px,color:#ffffff
    style FRONT fill:#e1f5fe,stroke:#0288d1,stroke-width:2px
    style BACK fill:#e8eaf6,stroke:#3949ab,stroke-width:2px
    style CLOUD fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style INFRA fill:transparent,stroke:none
```

**Decisões de arquitetura:**

| Serviço | Escolha | Por quê |
|---|---|---|
| 🤖 IA | **OpenAI** (GPT-4o-mini + Embeddings) | Uma única API key serve LLM e embeddings |
| 🗄️ Banco | **Neon** PostgreSQL | Serverless, free tier generoso, asyncpg |
| 💾 Storage | **Cloudflare R2** | 10 GB grátis, S3-compatível, sem egress fees |
| 🚀 Backend | **Render** (Docker) | Deploy automático via GitHub push |
| 🖥️ Frontend | **Vercel** | Deploy estático otimizado para React |

---

## 🔧 Componentes Internos do Backend

Cada módulo e suas dependências dentro da API:

```mermaid
flowchart TD
    subgraph COMP [" "]
        direction TB
        
        subgraph CONTROLLERS ["  🎯  API Controllers  "]
            AUTH["🔐 <b>Auth</b><br/>Login e JWT"]
            PAT["👤 <b>Patients</b><br/>CRUD pacientes"]
            EXAM["🧪 <b>Exams</b><br/>Upload + Análise + Laudo"]
            REF["📚 <b>References</b><br/>Upload de livros"]
        end

        subgraph SERVICES ["  🔧  Services  "]
            LLM["🤖 <b>LLM Provider</b><br/>OpenAI · Anthropic · Ollama"]
            STORE["💾 <b>Storage</b><br/>R2 · S3 · Local"]
            REPORT["📄 <b>Report Generator</b><br/>Prompt médico + LLM"]
            EMBED["🧲 <b>Embeddings</b><br/>Vetorização de texto"]
            RAGSVC["🔍 <b>RAG Service</b><br/>Busca semântica"]
            INGEST["📖 <b>PDF Ingestion</b><br/>Chunking + indexação"]
        end

        subgraph ENGINE ["  🧠  ML Engine  "]
            PIPE["⚡ <b>Analysis Pipeline</b><br/>Pipeline completo"]
            EDF["📊 <b>EDF Reader</b><br/>Leitura 19 canais"]
            PREP["🔉 <b>Preprocessing</b><br/>Filtros de sinal"]
        end

        EXAM --> STORE
        EXAM --> PIPE
        EXAM --> REPORT
        EXAM --> RAGSVC
        REPORT --> LLM
        RAGSVC --> EMBED
        REF --> INGEST
        INGEST --> EMBED
        PIPE --> EDF
        PIPE --> PREP
    end

    style AUTH fill:#5c6bc0,stroke:#283593,stroke-width:2px,color:#ffffff
    style PAT fill:#5c6bc0,stroke:#283593,stroke-width:2px,color:#ffffff
    style EXAM fill:#5c6bc0,stroke:#283593,stroke-width:2px,color:#ffffff
    style REF fill:#5c6bc0,stroke:#283593,stroke-width:2px,color:#ffffff
    style LLM fill:#10a37f,stroke:#0a6847,stroke-width:2px,color:#ffffff
    style STORE fill:#f6821f,stroke:#a85400,stroke-width:2px,color:#ffffff
    style REPORT fill:#26a69a,stroke:#00796b,stroke-width:2px,color:#ffffff
    style EMBED fill:#ab47bc,stroke:#6a1b9a,stroke-width:2px,color:#ffffff
    style RAGSVC fill:#ef5350,stroke:#b71c1c,stroke-width:2px,color:#ffffff
    style INGEST fill:#ff7043,stroke:#d84315,stroke-width:2px,color:#ffffff
    style PIPE fill:#7e57c2,stroke:#4527a0,stroke-width:2px,color:#ffffff
    style EDF fill:#7e57c2,stroke:#4527a0,stroke-width:2px,color:#ffffff
    style PREP fill:#7e57c2,stroke:#4527a0,stroke-width:2px,color:#ffffff
    style CONTROLLERS fill:#e8eaf6,stroke:#3949ab,stroke-width:2px
    style SERVICES fill:#e0f2f1,stroke:#00897b,stroke-width:2px
    style ENGINE fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style COMP fill:transparent,stroke:none
```

---

## ⚡ Pipeline Técnico — Fluxo Completo Detalhado

Do upload do arquivo ao aprendizado contínuo, com todas as decisões do sistema:

```mermaid
flowchart TD
    subgraph FLOW [" "]
        direction TB

        A["📤 <b>Upload .EDF</b>"]
        B{"💾 Storage"}
        B1["Local"]
        B2["☁️ Cloudflare R2"]
        C["📊 <b>Leitura do EEG</b><br/>19 canais · edfio"]
        D["🔉 <b>Processamento</b><br/>Filtros bandpass 0.5-50Hz<br/>Filtro notch 60Hz"]
        E["🧠 <b>Detecção de Padrões</b><br/>Ritmo de base · Spikes<br/>Assimetria · Artefatos"]
        F["🏷️ <b>Classificação</b>"]
        F1["✅ Normal"]
        F2["⚠️ Anormal"]
        F3["❓ Indeterminado"]
        G{"🔍 RAG"}
        G1["Busca laudos<br/>similares aprovados"]
        G2["Busca referências<br/>de livros médicos"]
        H["📝 <b>Prompt Médico</b><br/>Análise + Contexto RAG"]
        I["🤖 <b>LLM gera laudo</b><br/>OpenAI GPT-4o-mini"]
        J["✏️ <b>Médico revisa</b>"]
        K["✅ <b>Laudo aprovado</b>"]
        L["🧲 <b>Embedding armazenado</b><br/>Alimenta futuros laudos"]

        A --> B
        B --> B1
        B --> B2
        B1 --> C
        B2 --> C
        C --> D --> E --> F
        F --> F1
        F --> F2
        F --> F3
        F1 --> G
        F2 --> G
        F3 --> G
        G -->|"habilitado"| G1
        G -->|"habilitado"| G2
        G1 --> H
        G2 --> H
        G -->|"desabilitado"| H
        H --> I --> J --> K --> L
        L -.->|"melhoria contínua"| G1
    end

    style A fill:#1976d2,stroke:#0d47a1,stroke-width:2px,color:#ffffff
    style C fill:#7e57c2,stroke:#4527a0,stroke-width:2px,color:#ffffff
    style D fill:#7e57c2,stroke:#4527a0,stroke-width:2px,color:#ffffff
    style E fill:#7e57c2,stroke:#4527a0,stroke-width:2px,color:#ffffff
    style F fill:#546e7a,stroke:#263238,stroke-width:2px,color:#ffffff
    style F1 fill:#66bb6a,stroke:#2e7d32,stroke-width:2px,color:#ffffff
    style F2 fill:#ffa726,stroke:#e65100,stroke-width:2px,color:#ffffff
    style F3 fill:#78909c,stroke:#37474f,stroke-width:2px,color:#ffffff
    style G fill:#ef5350,stroke:#b71c1c,stroke-width:2px,color:#ffffff
    style G1 fill:#ef9a9a,stroke:#c62828,stroke-width:2px,color:#000000
    style G2 fill:#ef9a9a,stroke:#c62828,stroke-width:2px,color:#000000
    style H fill:#26a69a,stroke:#00796b,stroke-width:2px,color:#ffffff
    style I fill:#10a37f,stroke:#0a6847,stroke-width:2px,color:#ffffff
    style J fill:#ff7043,stroke:#d84315,stroke-width:2px,color:#ffffff
    style K fill:#66bb6a,stroke:#2e7d32,stroke-width:2px,color:#ffffff
    style L fill:#ab47bc,stroke:#6a1b9a,stroke-width:2px,color:#ffffff
    style B fill:#f6821f,stroke:#a85400,stroke-width:2px,color:#ffffff
    style B1 fill:#ffe0b2,stroke:#e65100,stroke-width:1px,color:#000000
    style B2 fill:#ffe0b2,stroke:#e65100,stroke-width:1px,color:#000000
    style FLOW fill:transparent,stroke:none
```

---

## 🔌 Provedores Plugáveis — Strategy Pattern

Tudo parametrizável via variáveis de ambiente. Troque de provedor sem alterar uma linha de código:

```mermaid
flowchart LR
    subgraph PLUG [" "]
        direction LR
        
        subgraph LLM_P ["  🤖  Geração de Laudos  "]
            direction TB
            LLM_H{"LLM_PROVIDER"}
            L1["<b>OpenAI</b><br/>GPT-4o-mini"]
            L2["<b>Anthropic</b><br/>Claude Sonnet"]
            L3["<b>Ollama</b><br/>Llama 3 · Local"]
            LLM_H --> L1
            LLM_H --> L2
            LLM_H --> L3
        end

        subgraph STORAGE_P ["  💾  Armazenamento  "]
            direction TB
            ST_H{"STORAGE_PROVIDER"}
            S1["<b>Cloudflare R2</b><br/>10 GB free"]
            S2["<b>AWS S3</b>"]
            S3["<b>Local</b><br/>Disco"]
            ST_H --> S1
            ST_H --> S2
            ST_H --> S3
        end

        subgraph EMB_P ["  🧲  Embeddings  "]
            direction TB
            EM_H{"EMBEDDING_PROVIDER"}
            E1["<b>OpenAI</b><br/>text-embedding-3-small"]
            E2["<b>Ollama</b><br/>nomic-embed-text"]
            E3["<b>None</b><br/>RAG desabilitado"]
            EM_H --> E1
            EM_H --> E2
            EM_H --> E3
        end

        subgraph DB_P ["  🗄️  Banco de Dados  "]
            direction TB
            DB_H{"DATABASE_URL"}
            D1["<b>PostgreSQL</b><br/>Neon · Produção"]
            D2["<b>SQLite</b><br/>Desenvolvimento"]
            DB_H --> D1
            DB_H --> D2
        end
    end

    style LLM_H fill:#10a37f,stroke:#0a6847,stroke-width:2px,color:#ffffff
    style L1 fill:#10a37f,stroke:#0a6847,stroke-width:1px,color:#ffffff
    style L2 fill:#d97706,stroke:#92400e,stroke-width:1px,color:#ffffff
    style L3 fill:#6366f1,stroke:#3730a3,stroke-width:1px,color:#ffffff
    style ST_H fill:#f6821f,stroke:#a85400,stroke-width:2px,color:#ffffff
    style S1 fill:#f6821f,stroke:#a85400,stroke-width:1px,color:#ffffff
    style S2 fill:#ff9900,stroke:#cc7a00,stroke-width:1px,color:#000000
    style S3 fill:#78909c,stroke:#37474f,stroke-width:1px,color:#ffffff
    style EM_H fill:#ab47bc,stroke:#6a1b9a,stroke-width:2px,color:#ffffff
    style E1 fill:#10a37f,stroke:#0a6847,stroke-width:1px,color:#ffffff
    style E2 fill:#6366f1,stroke:#3730a3,stroke-width:1px,color:#ffffff
    style E3 fill:#78909c,stroke:#37474f,stroke-width:1px,color:#ffffff
    style DB_H fill:#3ecf8e,stroke:#1a7f5a,stroke-width:2px,color:#000000
    style D1 fill:#3ecf8e,stroke:#1a7f5a,stroke-width:1px,color:#000000
    style D2 fill:#78909c,stroke:#37474f,stroke-width:1px,color:#ffffff
    style LLM_P fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px
    style STORAGE_P fill:#fff3e0,stroke:#e65100,stroke-width:2px
    style EMB_P fill:#f3e5f5,stroke:#7b1fa2,stroke-width:2px
    style DB_P fill:#e0f7fa,stroke:#00838f,stroke-width:2px
    style PLUG fill:transparent,stroke:none
```

---

## 🚀 Deploy em Produção

Pipeline de deploy e comunicação entre os serviços hospedados:

```mermaid
flowchart LR
    subgraph DEPLOY [" "]
        direction LR

        Browser["🌐 <b>Navegador</b>"]
        
        VERCEL["<b>Vercel</b><br/>sistemalaudos.vercel.app"]
        RENDER["<b>Render</b><br/>Docker + FastAPI"]
        
        NEON[("<b>Neon</b><br/>PostgreSQL")]
        R2[("<b>Cloudflare R2</b><br/>10 GB free")]
        OPENAI["<b>OpenAI</b><br/>GPT-4o-mini"]

        Browser -->|"HTTPS"| VERCEL
        VERCEL -->|"REST/JSON"| RENDER
        RENDER -->|"asyncpg/SSL"| NEON
        RENDER -->|"boto3/S3"| R2
        RENDER -->|"HTTPS"| OPENAI
    end

    style Browser fill:#f5f5f5,stroke:#9e9e9e,stroke-width:2px,color:#212121
    style VERCEL fill:#000000,stroke:#333333,stroke-width:2px,color:#ffffff
    style RENDER fill:#46548a,stroke:#2a3255,stroke-width:2px,color:#ffffff
    style NEON fill:#3ecf8e,stroke:#1a7f5a,stroke-width:2px,color:#000000
    style R2 fill:#f6821f,stroke:#a85400,stroke-width:2px,color:#ffffff
    style OPENAI fill:#10a37f,stroke:#0a6847,stroke-width:2px,color:#ffffff
    style DEPLOY fill:transparent,stroke:none
```

| Serviço | URL | Status |
|---|---|---|
| Frontend | [sistemalaudos.vercel.app](https://sistemalaudos.vercel.app) | ✅ Live |
| Backend API | [eeg-laudos-api.onrender.com](https://eeg-laudos-api.onrender.com) | ✅ Live |
| Swagger Docs | [/docs](https://eeg-laudos-api.onrender.com/docs) | ✅ Live |
| Health Check | [/api/health](https://eeg-laudos-api.onrender.com/api/health) | ✅ Live |

---

## 🗄️ Modelo de Dados

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

## 📡 API Endpoints

```mermaid
flowchart LR
    subgraph AUTH ["🔐 Auth"]
        POST_REG["POST /register"]
        POST_LOG["POST /login"]
        GET_ME["GET /me"]
    end

    subgraph PATIENTS ["👤 Patients"]
        POST_PAT["POST /"]
        GET_PATS["GET /"]
    end

    subgraph EXAMS ["🧪 Exams"]
        POST_UP["POST /upload"]
        POST_AN["POST /:id/analyze"]
        POST_GEN["POST /:id/generate-report"]
        GET_REP["GET /:id/report"]
        PUT_REP["PUT /:id/report"]
        POST_APR["POST /:id/report/approve"]
        GET_PDF["GET /:id/report/pdf"]
    end

    subgraph REFS ["📚 References"]
        POST_PDF["POST /upload-pdf"]
        GET_SRC["GET /sources"]
        GET_STAT["GET /stats"]
        DEL_SRC["DELETE /sources/:name"]
    end

    POST_UP -->|"arquivo .EDF"| POST_AN
    POST_AN -->|"análise pronta"| POST_GEN
    POST_GEN -->|"laudo gerado"| PUT_REP
    PUT_REP -->|"texto revisado"| POST_APR
    POST_APR -->|"laudo aprovado"| GET_PDF

    style AUTH fill:#5c6bc0,stroke:#283593,stroke-width:2px,color:#ffffff
    style PATIENTS fill:#26a69a,stroke:#00796b,stroke-width:2px,color:#ffffff
    style EXAMS fill:#ff7043,stroke:#d84315,stroke-width:2px,color:#ffffff
    style REFS fill:#ab47bc,stroke:#6a1b9a,stroke-width:2px,color:#ffffff
```

---

## 🧪 Testes E2E

O sistema possui **dois níveis de testes** que rodam contra **produção real**:

| Tipo | Ferramenta | Testes | O que valida |
|---|---|---|---|
| **API** | Python + httpx | 24 | Backend endpoints (auth, CRUD, RAG, CORS, segurança) |
| **UI** | Playwright + Chromium | 40 | Frontend completo (login, navegação, botões, formulários, PDF) |

Ambos validam a aplicação **em produção** (Render + Vercel), garantindo que deploy, build, banco, storage e LLM estão funcionais.

```bash
# Testes de API
python test_e2e_prod.py --verbose

# Testes de UI (frontend)
cd frontend
npm run test:e2e            # headless
npm run test:e2e:headed     # com browser visível
```

---

<br/>

<div align="center">

**Feito com** FastAPI · React · OpenAI · PostgreSQL · Cloudflare R2

Diagramas renderizados com [Mermaid.js](https://mermaid.js.org/) — compatíveis com GitHub, GitLab e VS Code.

</div>

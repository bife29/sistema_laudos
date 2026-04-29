# Registro de Propriedade Intelectual

## Sistema de Laudos EEG com Inteligência Artificial

---

## 1. Identificação do Software

| Campo | Informação |
|---|---|
| **Nome** | Sistema de Laudos EEG com IA |
| **Versão** | 1.0.0 |
| **Data de Criação** | Abril de 2026 |
| **Linguagens** | Python 3.12, JavaScript (React 18) |
| **Tipo** | Aplicação Web (SaaS) — Sistema de apoio à decisão médica |
| **Categoria INPI** | Programa de Computador — Área: Saúde / Inteligência Artificial |

---

## 2. Titulares dos Direitos Autorais

### Autor 1 — Titular Principal
| Campo | Informação |
|---|---|
| **Nome completo** | Michel Bueno Silva |
| **Nacionalidade** | Brasileira |
| **Participação** | Co-titular (50%) |

### Autor 2 — Titular
| Campo | Informação |
|---|---|
| **Nome completo** | Matheus Bueno Ribeiro da Silva |
| **Nacionalidade** | Brasileira |
| **Participação** | Co-titular (50%) |

---

## 3. Descrição Técnica do Programa

### 3.1 Resumo (para formulário INPI — máx. 500 palavras)

O "Sistema de Laudos EEG com IA" é uma aplicação web que utiliza inteligência artificial para auxiliar médicos neurologistas na elaboração de laudos de Eletroencefalograma (EEG). O sistema recebe arquivos de exame no formato EDF (European Data Format), realiza leitura automática dos 19 canais padrão do Sistema Internacional 10-20, aplica processamento de sinais digitais (filtros passa-banda, notch 60Hz, normalização), extrai características relevantes (ritmo de base, assimetrias inter-hemisféricas, atividade epileptiforme, artefatos) e gera um laudo médico profissional em linguagem técnica por meio de modelos de linguagem de grande escala (LLM).

O sistema implementa uma arquitetura de Retrieval-Augmented Generation (RAG), onde laudos anteriormente aprovados pelo médico e trechos de livros de referência em neurologia são indexados por embeddings vetoriais e recuperados por similaridade semântica para enriquecer a geração de laudos futuros. Isso permite um ciclo de aprendizado contínuo adaptado ao estilo e à prática clínica de cada profissional.

A aplicação é composta por um backend em Python (framework FastAPI) com banco de dados PostgreSQL, armazenamento de arquivos em Cloudflare R2 (compatível S3), e um frontend em React com Vite. A infraestrutura suporta múltiplos provedores de LLM (OpenAI, Anthropic, Ollama) e de armazenamento (local, S3, MinIO), sendo totalmente configurável via variáveis de ambiente.

As funcionalidades principais incluem: autenticação JWT, cadastro de pacientes, upload e armazenamento persistente de EDF, pipeline de análise com processamento de sinais, geração de laudos com contexto RAG, ciclo de revisão/aprovação médica, e ingestão de livros de referência em PDF.

### 3.2 Funcionalidades Originais

1. **Pipeline de análise de EEG em tempo real** — Leitura de arquivos EDF, filtragem de sinais (Butterworth band-pass, notch), extração de características por banda de frequência (delta, theta, alpha, beta, gamma), detecção de assimetrias inter-hemisféricas e atividade epileptiforme.

2. **Geração de laudos por LLM com RAG** — Sistema de Retrieval-Augmented Generation que combina: (a) conhecimento geral do LLM, (b) laudos aprovados anteriormente pelo médico (aprendizado contínuo), e (c) trechos de livros de referência médica indexados por embeddings vetoriais, usando similaridade de cosseno para recuperação semântica.

3. **Arquitetura plugável multi-provedor** — Abstração que permite trocar LLM (OpenAI/Anthropic/Ollama), banco de dados (SQLite/PostgreSQL), armazenamento (local/S3/R2/MinIO) e embeddings (OpenAI/Ollama) sem alteração de código, apenas por variáveis de ambiente.

4. **Ciclo de aprendizado contínuo** — Cada laudo aprovado pelo médico é automaticamente vetorizado e armazenado, melhorando a qualidade dos laudos futuros para exames com padrões similares.

---

## 4. Campos Técnicos de Aplicação

- Inteligência Artificial aplicada à Saúde
- Processamento de Sinais Biomédicos (EEG)
- Processamento de Linguagem Natural (NLP/LLM)
- Retrieval-Augmented Generation (RAG)
- Sistemas de Apoio à Decisão Clínica (CDSS)

---

## 5. Tecnologias Utilizadas

| Camada | Tecnologia | Versão |
|---|---|---|
| Backend | Python + FastAPI | 3.12 / 0.115 |
| Frontend | React + Vite | 18 / 5 |
| Banco de Dados | PostgreSQL (Neon) | 16 |
| ORM | SQLAlchemy (async) | 2.0 |
| Processamento EEG | edfio + NumPy + SciPy | — |
| LLM | OpenAI API / Anthropic API / Ollama | gpt-4o-mini |
| Embeddings | OpenAI text-embedding-3-small | 1536 dims |
| Armazenamento | Cloudflare R2 (S3-compatible) | — |
| Autenticação | JWT (python-jose + bcrypt) | — |
| Deploy Backend | Render (Docker) | — |
| Deploy Frontend | Vercel | — |
| Controle de Versão | Git + GitHub | — |

---

## 6. Procedimento para Registro no INPI

### 6.1 O que é

O **Registro de Programa de Computador** no INPI (Instituto Nacional da Propriedade Industrial) é o mecanismo oficial brasileiro para proteger software como propriedade intelectual. Tem validade de **50 anos** a partir de 1º de janeiro do ano seguinte à publicação.

### 6.2 Passo a passo

| Etapa | Ação | Responsável |
|---|---|---|
| **1** | Criar conta no [e-INPI](https://www.gov.br/inpi) (cada titular precisa de conta) | Michel + Matheus |
| **2** | Emitir GRU (Guia de Recolhimento da União) — taxa ~R$ 185,00 (pessoa física) | Michel |
| **3** | Pagar a GRU em qualquer banco | Michel |
| **4** | Preencher formulário eletrônico no sistema e-Software do INPI | Michel |
| **5** | Gerar o hash SHA-512 do código-fonte (compactado em .zip) | Automático (script abaixo) |
| **6** | Anexar: resumo funcional + hash do código | Michel |
| **7** | Protocolar o pedido | Automático |
| **8** | Receber número de registro (imediato) | INPI |

### 6.3 Documentos necessários

| Documento | Status |
|---|---|
| CPF de Michel Bueno Silva | **Necessário** — você fornece |
| CPF de Matheus Bueno Ribeiro da Silva | **Necessário** — você fornece |
| Código-fonte compactado (.zip) | **Pronto** — gerado pelo script abaixo |
| Hash SHA-512 do .zip | **Pronto** — gerado pelo script abaixo |
| Resumo funcional (até 500 palavras) | **Pronto** — Seção 3.1 deste documento |
| Descrição técnica | **Pronto** — Seção 3.2 deste documento |
| Comprovante GRU paga | **Necessário** — pagar no banco |

### 6.4 Script para gerar hash do código-fonte

Execute no terminal do projeto:

```powershell
# 1. Compactar código-fonte (sem node_modules, .env, etc.)
Compress-Archive -Path backend, frontend/src, frontend/package.json, frontend/vite.config.js, pyproject.toml, Dockerfile, docker-compose.yml, LICENSE -DestinationPath codigo_fonte_registro.zip -Force

# 2. Gerar hash SHA-512
$hash = (Get-FileHash -Path codigo_fonte_registro.zip -Algorithm SHA512).Hash
Write-Output "SHA-512: $hash"
Write-Output $hash | Out-File -FilePath hash_registro.txt
Write-Output "Hash salvo em hash_registro.txt"
```

O INPI aceita o hash (não exige upload do código real) — isso protege o sigilo do código-fonte.

---

## 7. Proteções Complementares Recomendadas

### 7.1 Registro no GitHub (prova de anterioridade)

O repositório Git já serve como prova de anterioridade com timestamps de cada commit:
- **Repositório:** https://github.com/bife29/sistema_laudos.git
- **Primeiro commit:** contém data de criação verificável
- **Commits assinados:** recomendável ativar `git config commit.gpgsign true`

### 7.2 Registro na Blockchain (opcional, gratuito)

Serviços como [OriginalMy](https://originalmy.com) ou [Opentimestamps](https://opentimestamps.org) permitem registrar o hash do código-fonte na blockchain Bitcoin, criando prova imutável e pública de existência na data do registro.

### 7.3 Ata Notarial (opcional, mais forte juridicamente)

Para proteção máxima, um cartório de notas pode lavrar uma **Ata Notarial** descrevendo o software e incluindo capturas de tela, hash do código e funcionalidades. Custo: ~R$ 300–500.

### 7.4 Marca Registrada (futuro)

Se o nome "Sistema de Laudos EEG" ou outro nome comercial for adotado, recomenda-se registrar a **marca** no INPI (processo separado, classe 42 — serviços de tecnologia).

---

## 8. Legislação Aplicável

| Lei | Cobertura |
|---|---|
| **Lei 9.609/1998** | Proteção da propriedade intelectual de programa de computador |
| **Lei 9.610/1998** | Direitos autorais (software é equiparado a obra literária) |
| **Lei 13.709/2018 (LGPD)** | Proteção de dados pessoais dos pacientes |
| **Decreto 2.556/1998** | Regulamenta o registro de software no INPI |
| **Convenção de Berna** | Proteção internacional automática (175 países) |
| **Acordo TRIPS (OMC)** | Proteção internacional de propriedade intelectual |

> **Nota importante:** No Brasil, o software é protegido por **direito autoral** (não por patente). A proteção existe automaticamente a partir da criação, mas o **registro no INPI** serve como prova oficial de autoria e data.

---

## 9. Resumo de Custos Estimados

| Item | Custo | Obrigatório? |
|---|---|---|
| Registro INPI (pessoa física) | ~R$ 185,00 | Recomendado |
| Ata Notarial | ~R$ 300–500 | Opcional |
| Registro de Marca | ~R$ 355,00 | Futuro |
| Blockchain (OriginalMy) | Gratuito–R$ 50 | Opcional |
| **Total mínimo** | **~R$ 185,00** | — |

---

## 10. Declaração de Autoria

Nós, abaixo identificados, declaramos que somos os autores e titulares exclusivos dos direitos patrimoniais
sobre o programa de computador denominado **"Sistema de Laudos EEG com IA"**, desenvolvido integralmente
por nós, sem utilização de código de terceiros protegido por licenças restritivas incompatíveis.

As bibliotecas de código aberto utilizadas (FastAPI, React, SQLAlchemy, edfio, etc.) são distribuídas
sob licenças permissivas (MIT, BSD, Apache 2.0) que permitem uso em software proprietário.

**Titular 1:**
Nome: Michel Bueno Silva
Assinatura: ________________________________________
Data: ____/____/2026

**Titular 2:**
Nome: Matheus Bueno Ribeiro da Silva
Assinatura: ________________________________________
Data: ____/____/2026

---

*Documento gerado em Abril de 2026 para fins de registro de propriedade intelectual.*

"""Gera PDF com a análise completa do projeto Sistema de Laudos EEG."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable
)
from reportlab.lib import colors
from datetime import datetime


def build_pdf():
    filename = "Analise_Projeto_Sistema_Laudos_EEG.pdf"
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2.5 * cm,
        rightMargin=2.5 * cm,
    )

    styles = getSampleStyleSheet()

    # Custom styles
    styles.add(ParagraphStyle(
        name="Cover_Title",
        fontSize=26,
        leading=32,
        alignment=TA_CENTER,
        textColor=HexColor("#1a237e"),
        spaceAfter=10,
        fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="Cover_Sub",
        fontSize=14,
        leading=18,
        alignment=TA_CENTER,
        textColor=HexColor("#37474f"),
        spaceAfter=6,
        fontName="Helvetica",
    ))
    styles.add(ParagraphStyle(
        name="H1",
        fontSize=18,
        leading=22,
        textColor=HexColor("#1a237e"),
        spaceBefore=20,
        spaceAfter=10,
        fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="H2",
        fontSize=14,
        leading=18,
        textColor=HexColor("#283593"),
        spaceBefore=14,
        spaceAfter=8,
        fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="H3",
        fontSize=12,
        leading=15,
        textColor=HexColor("#3949ab"),
        spaceBefore=10,
        spaceAfter=6,
        fontName="Helvetica-Bold",
    ))
    styles.add(ParagraphStyle(
        name="Body",
        fontSize=10,
        leading=14,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        fontName="Helvetica",
    ))
    styles.add(ParagraphStyle(
        name="BulletCustom",
        fontSize=10,
        leading=14,
        leftIndent=20,
        spaceAfter=3,
        fontName="Helvetica",
    ))
    styles.add(ParagraphStyle(
        name="TableHeader",
        fontSize=9,
        leading=12,
        textColor=colors.white,
        fontName="Helvetica-Bold",
        alignment=TA_CENTER,
    ))
    styles.add(ParagraphStyle(
        name="TableCell",
        fontSize=9,
        leading=12,
        fontName="Helvetica",
    ))
    styles.add(ParagraphStyle(
        name="Footer",
        fontSize=8,
        leading=10,
        textColor=HexColor("#9e9e9e"),
        alignment=TA_CENTER,
    ))

    elements = []
    W = doc.width

    BLUE = HexColor("#1a237e")
    LIGHT_BLUE = HexColor("#e8eaf6")
    HEADER_BG = HexColor("#283593")
    ALT_ROW = HexColor("#f5f5f5")
    RED_LIGHT = HexColor("#ffebee")
    GREEN_LIGHT = HexColor("#e8f5e9")

    def hr():
        return HRFlowable(width="100%", thickness=1, color=HexColor("#bdbdbd"), spaceAfter=10, spaceBefore=10)

    def make_table(headers, rows, col_widths=None):
        data = [[Paragraph(h, styles["TableHeader"]) for h in headers]]
        for row in rows:
            data.append([Paragraph(str(c), styles["TableCell"]) for c in row])
        if col_widths is None:
            col_widths = [W / len(headers)] * len(headers)
        t = Table(data, colWidths=col_widths, repeatRows=1)
        style_cmds = [
            ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ALIGN", (0, 0), (-1, 0), "CENTER"),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#bdbdbd")),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]
        for i in range(1, len(data)):
            if i % 2 == 0:
                style_cmds.append(("BACKGROUND", (0, i), (-1, i), ALT_ROW))
        t.setStyle(TableStyle(style_cmds))
        return t

    # =========================================================
    # COVER PAGE
    # =========================================================
    elements.append(Spacer(1, 5 * cm))
    elements.append(Paragraph("ANÁLISE COMPLETA DO PROJETO", styles["Cover_Title"]))
    elements.append(Paragraph("SISTEMA DE LAUDOS EEG COM IA", styles["Cover_Title"]))
    elements.append(Spacer(1, 1 * cm))
    elements.append(hr())
    elements.append(Paragraph("Avaliação de Arquitetura, Stack Tecnológica,<br/>Performance, Escalabilidade e Visão de Mercado", styles["Cover_Sub"]))
    elements.append(Spacer(1, 1 * cm))
    elements.append(Paragraph(f"Data: {datetime.now().strftime('%d/%m/%Y')}", styles["Cover_Sub"]))
    elements.append(Paragraph("Versão 1.0", styles["Cover_Sub"]))
    elements.append(PageBreak())

    # =========================================================
    # 1. RESUMO DO ESCOPO ORIGINAL
    # =========================================================
    elements.append(Paragraph("1. RESUMO DO ESCOPO ORIGINAL", styles["H1"]))
    elements.append(hr())
    elements.append(Paragraph(
        "O plano original propõe um MVP de 6 meses com 3 camadas tecnológicas distintas:", styles["Body"]))
    elements.append(Paragraph("• <b>Frontend:</b> Angular 17 (PWA)", styles["BulletCustom"]))
    elements.append(Paragraph("• <b>Backend:</b> .NET 8 Web API (Clean Architecture)", styles["BulletCustom"]))
    elements.append(Paragraph("• <b>IA:</b> Python FastAPI (microserviço separado)", styles["BulletCustom"]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "Orçamento estimado: ~R$ 520.000 | Equipe: 5 pessoas | Meta: reduzir tempo de laudo de 20-30 min para 10 min por exame.", styles["Body"]))

    # =========================================================
    # 2. PROBLEMAS CRÍTICOS DA ARQUITETURA ORIGINAL
    # =========================================================
    elements.append(Paragraph("2. PROBLEMAS CRÍTICOS DA ARQUITETURA ORIGINAL", styles["H1"]))
    elements.append(hr())

    elements.append(Paragraph("2.1 Complexidade desnecessária para um MVP", styles["H2"]))
    elements.append(make_table(
        ["Problema", "Impacto"],
        [
            ["3 linguagens/stacks (.NET + Angular + Python)", "Requer 3 perfis diferentes, dificulta contratação e manutenção"],
            ["Clean Architecture em .NET para CRUD simples", "Over-engineering para um MVP de 6 meses"],
            ["Angular 17 + NgRx + RxJS", "Pesado demais; curva de aprendizado alta para equipe pequena"],
            ["gRPC entre .NET e Python", "Complexidade de integração sem benefício real nesta escala"],
            ["Dois backends (.NET + FastAPI)", "Duplicação de lógica de autenticação, validação, routing"],
        ],
        [W * 0.45, W * 0.55],
    ))

    elements.append(Paragraph("2.2 Gargalos de performance identificados", styles["H2"]))
    elements.append(Paragraph("• Retornar dados EEG como <b>JSON via REST</b> (19 canais × 256 Hz × 60 min ≈ 175 MB de JSON) é inviável", styles["BulletCustom"]))
    elements.append(Paragraph("• <b>Chart.js / Plotly.js</b> não escalam para visualização contínua de 19 canais EEG em tempo real", styles["BulletCustom"]))
    elements.append(Paragraph("• Ausência de <b>WebSocket</b> para streaming de dados do sinal", styles["BulletCustom"]))
    elements.append(Paragraph("• Sem estratégia de <b>compressão</b> dos dados do sinal", styles["BulletCustom"]))

    elements.append(Paragraph("2.3 Gaps técnicos do escopo", styles["H2"]))
    gaps = [
        "Não menciona formato de exportação de dados (HL7 FHIR, DICOM-EEG)",
        "Sem plano de backup do modelo de IA (se a Claude API ficar offline)",
        "Sem estratégia de versionamento de modelos ML",
        "Sem pipeline de CI/CD para modelos (MLOps)",
        "Sem plano de migração de dados de sistemas legados",
        "Sem módulo de agendamento/workflow (fila de exames)",
        "Sem notificações (exame pronto, laudo pendente)",
        "Sem módulo de faturamento/relatórios gerenciais",
        "Sem integração com sistemas hospitalares (HIS/RIS)",
    ]
    for g in gaps:
        elements.append(Paragraph(f"• {g}", styles["BulletCustom"]))

    elements.append(PageBreak())

    # =========================================================
    # 3. ARQUITETURA PROPOSTA — 100% PYTHON
    # =========================================================
    elements.append(Paragraph("3. ARQUITETURA PROPOSTA — CONSOLIDADA EM PYTHON", styles["H1"]))
    elements.append(hr())
    elements.append(Paragraph(
        "Eliminando .NET e Angular, consolidamos tudo em Python, ganhando:", styles["Body"]))
    elements.append(Paragraph("• <b>1 linguagem principal</b> para toda a equipe", styles["BulletCustom"]))
    elements.append(Paragraph("• <b>Contratação mais fácil</b> — Python é a linguagem mais popular do mundo", styles["BulletCustom"]))
    elements.append(Paragraph("• <b>Ecossistema unificado</b> de IA/ML nativo", styles["BulletCustom"]))
    elements.append(Paragraph("• <b>Menor custo de equipe</b> — 2-3 devs ao invés de 5", styles["BulletCustom"]))

    elements.append(Paragraph("3.1 Stack Tecnológica Recomendada", styles["H2"]))

    stack_data = [
        ["Camada", "Tecnologia", "Justificativa"],
        ["Frontend (PWA)", "React + Vite + TypeScript", "Melhor ecossistema para Canvas/WebGL (EEG viewer). PWA nativo."],
        ["Backend API", "FastAPI (async)", "Alta performance, documentação automática, tipagem nativa, async I/O"],
        ["Autenticação", "fastapi-users + JWT + OAuth2", "Solução completa, RBAC integrado"],
        ["ORM", "SQLAlchemy 2.0 + Alembic", "Async support, migrações robustas"],
        ["Tarefas assíncronas", "Celery + Redis", "Processamento de EEG em background"],
        ["WebSocket", "FastAPI WebSocket nativo", "Streaming de dados EEG em tempo real"],
        ["Geração PDF", "WeasyPrint ou ReportLab", "PDFs profissionais com layout customizado"],
        ["Processamento EEG", "MNE-Python + SciPy", "Padrão da indústria para EEG"],
        ["ML Clássico", "scikit-learn", "Baseline rápido (Random Forest)"],
        ["Deep Learning", "PyTorch", "Evolução futura (CNN para detecção de spikes)"],
        ["LLM", "Anthropic SDK (Claude)", "Geração de texto médico em português"],
        ["MLOps", "MLflow", "Versionamento de modelos, tracking de experimentos"],
        ["Banco de dados", "PostgreSQL 16 + pgvector", "Relacional + embeddings para busca semântica"],
        ["Cache/Fila", "Redis", "Cache de sessão + broker Celery"],
        ["Storage", "MinIO ou AWS S3", "Arquivos EDF, PDFs, modelos treinados"],
        ["Containerização", "Docker + Docker Compose", "Ambiente reproduzível"],
        ["CI/CD", "GitHub Actions", "Pipeline automatizado"],
    ]
    t_data = [[Paragraph(c, styles["TableHeader"] if i == 0 else styles["TableCell"]) for c in row] for i, row in enumerate(stack_data)]
    t = Table(t_data, colWidths=[W * 0.20, W * 0.30, W * 0.50], repeatRows=1)
    t_style = [
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("GRID", (0, 0), (-1, -1), 0.5, HexColor("#bdbdbd")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
    ]
    for i in range(2, len(t_data), 2):
        t_style.append(("BACKGROUND", (0, i), (-1, i), ALT_ROW))
    t.setStyle(TableStyle(t_style))
    elements.append(t)

    elements.append(Paragraph("3.2 Decisão de Frontend — Opções Ranqueadas", styles["H2"]))
    elements.append(make_table(
        ["Opção", "Prós", "Contras", "Recomendação"],
        [
            ["React + Vite (PWA)", "Melhor para EEG viewer (WebGL/Canvas), PWA nativo, mercado amplo", "Precisa de dev JS/TS", "MELHOR PARA PRODUÇÃO"],
            ["NiceGUI / Reflex", "100% Python, rápido para MVP", "Limitado para visualização EEG complexa", "Bom para admin/dashboard"],
            ["Streamlit", "MVP em semanas", "Não escala, sem PWA, sem controle fino de UI", "Apenas protótipo"],
            ["HTMX + Jinja2", "Leve, Python puro no backend", "Limitado para interatividade rica do EEG viewer", "Viável exceto viewer"],
        ],
        [W * 0.17, W * 0.30, W * 0.28, W * 0.25],
    ))

    elements.append(PageBreak())

    # =========================================================
    # 4. DIAGRAMA DA ARQUITETURA
    # =========================================================
    elements.append(Paragraph("4. DIAGRAMA DA ARQUITETURA PROPOSTA", styles["H1"]))
    elements.append(hr())

    arch_text = """
    <font face="Courier" size="9" color="#1a237e">
    ┌──────────────────────────────────────────────────┐<br/>
    │           CAMADA CLIENTE (PWA)                    │<br/>
    │   React + Vite + TypeScript                      │<br/>
    │   EEG Viewer (Canvas/WebGL) | Editor de Laudo    │<br/>
    │   Service Worker (offline) | WebSocket client    │<br/>
    └─────────────────────┬────────────────────────────┘<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│ HTTPS / WebSocket<br/>
    ┌─────────────────────▼────────────────────────────┐<br/>
    │          BACKEND UNIFICADO — FastAPI              │<br/>
    │  ┌──────────┐ ┌──────────┐ ┌─────────────────┐   │<br/>
    │  │ Auth JWT │ │ REST API │ │ WebSocket EEG   │   │<br/>
    │  └──────────┘ └──────────┘ └─────────────────┘   │<br/>
    │  ┌──────────────────────────────────────────┐     │<br/>
    │  │ MÓDULO IA (mesmo processo)               │     │<br/>
    │  │ MNE-Python │ SciPy │ scikit-learn/PyTorch│     │<br/>
    │  │ Claude API │ MLflow                      │     │<br/>
    │  └──────────────────────────────────────────┘     │<br/>
    │  Celery Workers (processamento background)        │<br/>
    └──────────┬───────────────────┬───────────────────┘<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│<br/>
    ┌──────────▼─────┐  ┌─────────▼────────────────────┐<br/>
    │ PostgreSQL 16  │  │ Redis (Cache + Celery Broker) │<br/>
    │ + pgvector     │  └──────────────────────────────┘<br/>
    └────────────────┘  ┌──────────────────────────────┐<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;│ MinIO / S3 (EDF, PDF, Models) │<br/>
    &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└──────────────────────────────┘<br/>
    </font>
    """
    elements.append(Paragraph(arch_text, styles["Body"]))

    # =========================================================
    # 5. COMPARAÇÃO ORIGINAL vs PROPOSTA
    # =========================================================
    elements.append(Paragraph("5. COMPARAÇÃO: ESCOPO ORIGINAL vs. PROPOSTA", styles["H1"]))
    elements.append(hr())
    elements.append(make_table(
        ["Aspecto", "Original (.NET + Angular + Python)", "Proposto (Python + React)"],
        [
            ["Linguagens", "3 (C#, TypeScript, Python)", "2 (Python, TypeScript)"],
            ["Backends", "2 (.NET API + FastAPI)", "1 (FastAPI)"],
            ["Equipe mínima", "5 pessoas", "2-3 pessoas"],
            ["Custo estimado", "R$ 520.000", "R$ 250.000 - 300.000"],
            ["Time to market", "6 meses", "4-5 meses"],
            ["Comunicação inter-serviços", "HTTP/gRPC entre .NET e Python", "Chamada direta de função"],
            ["Deploy", "3 containers distintos", "1-2 containers"],
            ["Autenticação", "Duplicada em 2 backends", "Única no FastAPI"],
            ["ORM", "Entity Framework (C#)", "SQLAlchemy 2.0 (Python)"],
            ["Performance IA", "Latência de rede .NET → Python", "Zero latência (mesmo processo)"],
        ],
        [W * 0.22, W * 0.39, W * 0.39],
    ))

    elements.append(PageBreak())

    # =========================================================
    # 6. VISÃO DE MERCADO
    # =========================================================
    elements.append(Paragraph("6. VISÃO DE MERCADO", styles["H1"]))
    elements.append(hr())

    elements.append(Paragraph("6.1 Concorrentes no Brasil e no mundo", styles["H2"]))
    elements.append(make_table(
        ["Produto", "País", "O que faz", "Preço aprox."],
        [
            ["Persyst", "EUA", "Detecção automática de spikes em EEG", "~$500/mês/licença"],
            ["BESA", "Alemanha", "Análise de sinais EEG/MEG", "~€3.000 licença única"],
            ["Natus NeuroWorks", "EUA", "EEG completo (hardware + software)", "Bundled c/ hardware"],
            ["EpiScan", "Brasil (UFMG)", "Detecção de crises epilépticas", "Acadêmico"],
            ["Neuroelectrics NIC2", "Espanha", "Análise EEG com IA", "~€200/mês"],
        ],
        [W * 0.20, W * 0.15, W * 0.40, W * 0.25],
    ))

    elements.append(Paragraph("6.2 Diferenciais do produto", styles["H2"]))
    elements.append(Paragraph("• <b>IA + LLM para geração de laudo em português</b> — nenhum concorrente oferece isso", styles["BulletCustom"]))
    elements.append(Paragraph("• <b>PWA offline</b> — funciona em clínicas com internet instável", styles["BulletCustom"]))
    elements.append(Paragraph("• <b>Preço competitivo</b> para mercado brasileiro (R$ 500/mês vs $500/mês dos importados)", styles["BulletCustom"]))
    elements.append(Paragraph("• <b>Aprendizado contínuo</b> com feedback médico (active learning)", styles["BulletCustom"]))

    elements.append(Paragraph("6.3 Oportunidades de mercado", styles["H2"]))
    elements.append(Paragraph("• ~5.000 clínicas de neurofisiologia no Brasil", styles["BulletCustom"]))
    elements.append(Paragraph("• SUS realiza ~300.000 EEGs/ano → potencial de licitação pública", styles["BulletCustom"]))
    elements.append(Paragraph("• Telemedicina: laudos a distância é tendência pós-COVID", styles["BulletCustom"]))
    elements.append(Paragraph("• Expansão futura: polissonografia, EMG, potenciais evocados (mesma base tecnológica)", styles["BulletCustom"]))

    # =========================================================
    # 7. O QUE FALTA PARA INICIAR
    # =========================================================
    elements.append(Paragraph("7. ITENS NECESSÁRIOS PARA INICIAR O DESENVOLVIMENTO", styles["H1"]))
    elements.append(hr())

    elements.append(Paragraph("7.1 Itens obrigatórios ANTES de codar", styles["H2"]))
    elements.append(make_table(
        ["#", "Item", "Status", "Ação necessária"],
        [
            ["1", "Arquivo EDF de exemplo", "FALTA", "Pedir ao médico ao menos 1 arquivo .EDF real (anonimizado)"],
            ["2", "Modelo de laudo padrão", "OK", "O PDF do Isaac serve como template"],
            ["3", "Definição de montagens EEG", "PARCIAL", "Confirmar com médico quais montagens usar"],
            ["4", "Lista de padrões anormais", "PARCIAL", "Falta: polipontas, surto-supressão, PLED, GRDA etc."],
            ["5", "Requisitos ANVISA", "FALTA", "Consultar se precisa registro como SaMD"],
            ["6", "Consentimento LGPD", "FALTA", "Modelo de termo de consentimento"],
            ["7", "Ambiente de desenvolvimento", "PARCIAL", "Faltam: PostgreSQL, Redis, Node.js"],
            ["8", "Credenciais Claude API", "FALTA", "Criar conta Anthropic e obter API key"],
            ["9", "Dataset público de EEG", "DISPONÍVEL", "TUH EEG Corpus (Temple University) — gratuito"],
            ["10", "Domínio e SSL", "FALTA", "Para deploy futuro"],
        ],
        [W * 0.05, W * 0.22, W * 0.12, W * 0.61],
    ))

    elements.append(Paragraph("7.2 Perguntas pendentes para o stakeholder/médico", styles["H2"]))
    perguntas = [
        "Quantos tipos de exame o sistema vai suportar inicialmente? (Só EEG rotina? Vídeo-EEG? Polissonografia?)",
        "Quantos médicos vão usar o sistema na fase inicial?",
        "O sistema precisa gerar nota fiscal ou integrar com sistema de faturamento?",
        "Qual a meta de laudos/dia? (Isso define a infraestrutura necessária)",
        "Já existe algum sistema legado que precisa de migração de dados?",
        "O médico aceita usar o sistema para marcar exames durante o desenvolvimento (treino da IA)?",
    ]
    for i, p in enumerate(perguntas, 1):
        elements.append(Paragraph(f"<b>{i}.</b> {p}", styles["BulletCustom"]))

    elements.append(PageBreak())

    # =========================================================
    # 8. ESTRUTURA DE PROJETO PROPOSTA
    # =========================================================
    elements.append(Paragraph("8. ESTRUTURA DE PROJETO PROPOSTA", styles["H1"]))
    elements.append(hr())

    structure = """<font face="Courier" size="9">
eeg-laudo-system/<br/>
├── backend/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# FastAPI<br/>
│&nbsp;&nbsp;&nbsp;├── app/<br/>
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── api/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Rotas (auth, patients, exams, reports)<br/>
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── core/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Config, security, database<br/>
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── models/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# SQLAlchemy models<br/>
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── schemas/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Pydantic schemas<br/>
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── services/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Business logic<br/>
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└── ml/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Módulo IA<br/>
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── preprocessing/&nbsp;&nbsp;# Filtros, segmentação<br/>
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── detectors/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Spike detector, asymmetry, base rhythm<br/>
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;├── report_gen/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Geração de laudo (Claude API)<br/>
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;└── models/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Modelos treinados (.pkl, .pt)<br/>
│&nbsp;&nbsp;&nbsp;├── migrations/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Alembic<br/>
│&nbsp;&nbsp;&nbsp;├── tests/<br/>
│&nbsp;&nbsp;&nbsp;└── pyproject.toml<br/>
├── frontend/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# React + Vite (PWA)<br/>
│&nbsp;&nbsp;&nbsp;├── src/<br/>
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── components/<br/>
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── EEGViewer/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Canvas/WebGL renderer<br/>
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── ReportEditor/&nbsp;&nbsp;&nbsp;# Editor de laudo (rich text)<br/>
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└── MarkingTool/&nbsp;&nbsp;&nbsp;&nbsp;# Marcação de eventos<br/>
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── pages/<br/>
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;├── services/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# API client<br/>
│&nbsp;&nbsp;&nbsp;│&nbsp;&nbsp;&nbsp;└── stores/&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;# Zustand (estado)<br/>
│&nbsp;&nbsp;&nbsp;└── package.json<br/>
├── docker-compose.yml<br/>
├── .env.example<br/>
└── README.md<br/>
</font>"""
    elements.append(Paragraph(structure, styles["Body"]))

    # =========================================================
    # 9. VEREDICTO FINAL
    # =========================================================
    elements.append(Paragraph("9. VEREDICTO FINAL", styles["H1"]))
    elements.append(hr())

    elements.append(Paragraph(
        "O escopo original é <b>bem elaborado clinicamente</b> mas <b>over-engineered tecnicamente</b> para um MVP. "
        "A consolidação em Python + React proporcionará:", styles["Body"]))
    elements.append(Spacer(1, 6))

    veredito = [
        ["Redução de custo", "~40% (de R$ 520k para ~R$ 280k)"],
        ["Aceleração", "~30% (de 6 para 4-5 meses)"],
        ["Simplificação", "1 backend ao invés de 2"],
        ["Iteração com médico", "Mais rápida com menos camadas de complexidade"],
    ]
    elements.append(make_table(["Benefício", "Resultado"], veredito, [W * 0.30, W * 0.70]))

    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        "<b>Item mais crítico:</b> O arquivo .EDF real é indispensável para iniciar o desenvolvimento do pipeline de processamento. "
        "Sem ele, todo o trabalho de IA fica bloqueado.", styles["Body"]))

    elements.append(Spacer(1, 12))
    elements.append(Paragraph(
        "<b>ROI Esperado (mantido do escopo original):</b>", styles["Body"]))
    elements.append(Paragraph("• Investimento revisado: ~R$ 280.000", styles["BulletCustom"]))
    elements.append(Paragraph("• Por cliente (R$ 500/mês): 100 clientes = R$ 50.000/mês", styles["BulletCustom"]))
    elements.append(Paragraph("• Break-even em ~6 meses (antes era ~11 meses)", styles["BulletCustom"]))
    elements.append(Paragraph("• Ano 2: R$ 600.000/ano de receita", styles["BulletCustom"]))

    # Build
    doc.build(elements)
    print(f"PDF gerado com sucesso: {filename}")


if __name__ == "__main__":
    build_pdf()

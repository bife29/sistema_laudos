"""Gera PDF com cronograma de entregas — versão para o médico."""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.colors import HexColor
from reportlab.lib.units import cm
from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY, TA_LEFT, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, HRFlowable,
)
from reportlab.lib import colors
from datetime import datetime


def build_pdf():
    filename = "Cronograma_Sistema_Laudos_EEG.pdf"
    doc = SimpleDocTemplate(
        filename,
        pagesize=A4,
        topMargin=2 * cm,
        bottomMargin=2 * cm,
        leftMargin=2.2 * cm,
        rightMargin=2.2 * cm,
    )

    styles = getSampleStyleSheet()
    W = doc.width

    BLUE_DARK = HexColor("#1a237e")
    BLUE_MED = HexColor("#283593")
    BLUE_LIGHT = HexColor("#e8eaf6")
    HEADER_BG = HexColor("#283593")
    GREEN = HexColor("#2e7d32")
    GREEN_LIGHT = HexColor("#e8f5e9")
    GREY_LINE = HexColor("#bdbdbd")
    ALT_ROW = HexColor("#f5f5f5")
    WHITE = colors.white

    styles.add(ParagraphStyle("CoverTitle", fontSize=28, leading=34, alignment=TA_CENTER,
                              textColor=BLUE_DARK, fontName="Helvetica-Bold", spaceAfter=8))
    styles.add(ParagraphStyle("CoverSub", fontSize=13, leading=17, alignment=TA_CENTER,
                              textColor=HexColor("#37474f"), fontName="Helvetica", spaceAfter=6))
    styles.add(ParagraphStyle("H1", fontSize=17, leading=21, textColor=BLUE_DARK,
                              spaceBefore=18, spaceAfter=8, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle("H2", fontSize=13, leading=17, textColor=BLUE_MED,
                              spaceBefore=12, spaceAfter=6, fontName="Helvetica-Bold"))
    styles.add(ParagraphStyle("Body", fontSize=10, leading=14, alignment=TA_JUSTIFY,
                              spaceAfter=5, fontName="Helvetica"))
    styles.add(ParagraphStyle("BulletItem", fontSize=10, leading=14, leftIndent=18,
                              spaceAfter=3, fontName="Helvetica"))
    styles.add(ParagraphStyle("TH", fontSize=9, leading=12, textColor=WHITE,
                              fontName="Helvetica-Bold", alignment=TA_CENTER))
    styles.add(ParagraphStyle("TC", fontSize=9, leading=12, fontName="Helvetica"))
    styles.add(ParagraphStyle("MonthTitle", fontSize=14, leading=18, fontName="Helvetica-Bold",
                              textColor=WHITE, alignment=TA_LEFT))
    styles.add(ParagraphStyle("SmallNote", fontSize=8, leading=10,
                              textColor=HexColor("#757575"), fontName="Helvetica"))

    elements = []

    def hr():
        return HRFlowable(width="100%", thickness=1, color=GREY_LINE, spaceAfter=8, spaceBefore=8)

    def make_table(headers, rows, col_widths=None):
        data = [[Paragraph(h, styles["TH"]) for h in headers]]
        for row in rows:
            data.append([Paragraph(str(c), styles["TC"]) for c in row])
        if col_widths is None:
            col_widths = [W / len(headers)] * len(headers)
        t = Table(data, colWidths=col_widths, repeatRows=1)
        cmds = [
            ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("GRID", (0, 0), (-1, -1), 0.5, GREY_LINE),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ]
        for i in range(2, len(data), 2):
            cmds.append(("BACKGROUND", (0, i), (-1, i), ALT_ROW))
        t.setStyle(TableStyle(cmds))
        return t

    def month_header(title, subtitle=""):
        data = [[Paragraph(title, styles["MonthTitle"]),
                 Paragraph(subtitle, ParagraphStyle("ms", fontSize=10, leading=13,
                           textColor=HexColor("#c5cae9"), fontName="Helvetica", alignment=TA_RIGHT))]]
        t = Table(data, colWidths=[W * 0.55, W * 0.45])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), BLUE_MED),
            ("TOPPADDING", (0, 0), (-1, 0), 8),
            ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
            ("LEFTPADDING", (0, 0), (-1, 0), 12),
            ("RIGHTPADDING", (0, 0), (-1, 0), 12),
            ("VALIGN", (0, 0), (-1, 0), "MIDDLE"),
        ]))
        return t

    def item(text):
        return Paragraph(f'\u2713 {text}', styles["BulletItem"])

    def green_box(text):
        data = [[Paragraph(text,
                 ParagraphStyle("gb", fontSize=10, leading=14, fontName="Helvetica", textColor=HexColor("#1b5e20")))]]
        t = Table(data, colWidths=[W])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), GREEN_LIGHT),
            ("BOX", (0, 0), (-1, -1), 1, GREEN),
            ("TOPPADDING", (0, 0), (-1, -1), 10),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
            ("LEFTPADDING", (0, 0), (-1, -1), 12),
            ("RIGHTPADDING", (0, 0), (-1, -1), 12),
        ]))
        return t

    def blue_box(text):
        data = [[Paragraph(text,
                 ParagraphStyle("bb", fontSize=10, leading=14, fontName="Helvetica", textColor=BLUE_DARK))]]
        t = Table(data, colWidths=[W])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), BLUE_LIGHT),
            ("BOX", (0, 0), (-1, -1), 1.5, BLUE_DARK),
            ("TOPPADDING", (0, 0), (-1, -1), 12),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 12),
            ("LEFTPADDING", (0, 0), (-1, -1), 14),
            ("RIGHTPADDING", (0, 0), (-1, -1), 14),
        ]))
        return t

    # ==============================================================
    # CAPA
    # ==============================================================
    elements.append(Spacer(1, 4 * cm))
    elements.append(Paragraph("SISTEMA DE LAUDOS EEG COM IA", styles["CoverTitle"]))
    elements.append(Spacer(1, 0.5 * cm))
    elements.append(hr())
    elements.append(Paragraph("Cronograma de Entregas", styles["CoverSub"]))
    elements.append(Paragraph("Abril 2026 \u2014 Dezembro 2026", styles["CoverSub"]))
    elements.append(Spacer(1, 2 * cm))

    summary_data = [
        [Paragraph("<b>Dura\u00e7\u00e3o</b>", styles["TC"]), Paragraph("9 meses (Abril \u2014 Dezembro 2026)", styles["TC"])],
        [Paragraph("<b>Equipe</b>", styles["TC"]), Paragraph("1 Desenvolvedor S\u00eanior", styles["TC"])],
        [Paragraph("<b>Investimento mensal</b>", styles["TC"]), Paragraph("<b>R$ 1.680,00 / m\u00eas</b>  (tudo incluso)", styles["TC"])],
        [Paragraph("<b>Investimento total</b>", styles["TC"]), Paragraph("<b>R$ 15.120,00</b>", styles["TC"])],
    ]
    st = Table(summary_data, colWidths=[W * 0.35, W * 0.65])
    st.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (0, -1), BLUE_LIGHT),
        ("GRID", (0, 0), (-1, -1), 0.5, GREY_LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(st)

    elements.append(PageBreak())

    # ==============================================================
    # O QUE E O PROJETO
    # ==============================================================
    elements.append(Paragraph("O QUE \u00c9 O PROJETO", styles["H1"]))
    elements.append(hr())
    elements.append(Paragraph(
        "Um sistema que usa Intelig\u00eancia Artificial para ajudar o m\u00e9dico a fazer laudos de EEG "
        "de forma mais r\u00e1pida, consistente e profissional.", styles["Body"]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("<b>Como funciona:</b>", styles["Body"]))
    elements.append(item("O m\u00e9dico faz upload do arquivo do exame (arquivo .EDF que sai do aparelho)"))
    elements.append(item("A IA analisa automaticamente os 19 canais do EEG"))
    elements.append(item("O sistema detecta padr\u00f5es anormais (pontas, ondas agudas, assimetrias e outros)"))
    elements.append(item("A IA gera um laudo completo em linguagem m\u00e9dica profissional"))
    elements.append(item("O m\u00e9dico revisa, ajusta se necess\u00e1rio, e aprova"))
    elements.append(item("O laudo final \u00e9 exportado em PDF pronto para entrega"))
    elements.append(Spacer(1, 8))
    elements.append(Paragraph("<b>Resultado:</b> O tempo de elabora\u00e7\u00e3o cai de 20-30 minutos para ~10 minutos por laudo.", styles["Body"]))

    elements.append(Spacer(1, 12))
    elements.append(Paragraph("PADR\u00d5ES QUE A IA VAI DETECTAR", styles["H2"]))
    patterns = [
        ["Pontas (spikes)", "Descargas epileptiformes de curta dura\u00e7\u00e3o"],
        ["Ondas agudas", "Descargas epileptiformes de dura\u00e7\u00e3o maior"],
        ["Polipontas", "M\u00faltiplas pontas consecutivas em sequ\u00eancia r\u00e1pida"],
        ["Complexos ponta-onda", "Ponta seguida de onda lenta \u2014 padr\u00e3o epil\u00e9ptico cl\u00e1ssico"],
        ["Surto-supress\u00e3o", "Altern\u00e2ncia entre atividade e sil\u00eancio \u2014 padr\u00e3o de gravidade"],
        ["PLED / LPD", "Descargas peri\u00f3dicas lateralizadas \u2014 les\u00e3o focal aguda"],
        ["GRDA / GPD", "Descargas peri\u00f3dicas generalizadas \u2014 encefalopatia"],
        ["Ondas trif\u00e1sicas", "Morfologia trif\u00e1sica \u2014 encefalopatia metab\u00f3lica"],
        ["Delta focal", "Ondas lentas focais \u2014 les\u00e3o estrutural"],
        ["Assimetria entre hemisf\u00e9rios", "Diferen\u00e7a de atividade entre lado esquerdo e direito"],
        ["Alentecimento difuso", "Desorganiza\u00e7\u00e3o geral da atividade cerebral"],
        ["FIRDA / OIRDA", "Atividade r\u00edtmica intermitente frontal ou occipital"],
        ["Beta excessivo", "Pode indicar efeito de medicamentos"],
        ["Artefatos", "Movimentos, piscadas, EMG \u2014 identificados e sinalizados"],
    ]
    elements.append(make_table(["Padr\u00e3o", "O que significa"], patterns, [W * 0.30, W * 0.70]))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph(
        "<i>Todo laudo inclui: \"Laudo gerado com aux\u00edlio de intelig\u00eancia artificial. "
        "A valida\u00e7\u00e3o e responsabilidade cl\u00ednica s\u00e3o do m\u00e9dico assinante.\"</i>", styles["SmallNote"]))

    elements.append(PageBreak())

    # ==============================================================
    # ENTREGAS MES A MES
    # ==============================================================
    elements.append(Paragraph("ENTREGAS M\u00caS A M\u00caS", styles["H1"]))
    elements.append(hr())

    # -- MES 1 --
    elements.append(month_header("M\u00caS 1 \u2014 ABRIL 2026", "Sistema funcional + Primeiro laudo"))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("<b>O que o m\u00e9dico recebe neste m\u00eas:</b>", styles["Body"]))
    elements.append(Spacer(1, 3))
    elements.append(item("Sistema com login seguro (usu\u00e1rio e senha)"))
    elements.append(item("Tela para enviar o arquivo do exame (.EDF) \u2014 basta arrastar e soltar"))
    elements.append(item("O sistema l\u00ea o exame e extrai as informa\u00e7\u00f5es automaticamente (paciente, dura\u00e7\u00e3o, canais)"))
    elements.append(item("A IA gera o laudo completo com estrutura profissional"))
    elements.append(item("Laudo exibido na tela para visualiza\u00e7\u00e3o"))
    elements.append(Spacer(1, 8))
    elements.append(green_box(
        "<b>RESULTADO DO M\u00caS 1:</b> O m\u00e9dico j\u00e1 faz upload de um exame e recebe um laudo gerado "
        "automaticamente pela IA. O fluxo principal j\u00e1 funciona de ponta a ponta."))
    elements.append(Spacer(1, 14))

    # -- MES 2 --
    elements.append(month_header("M\u00caS 2 \u2014 MAIO 2026", "Visualiza\u00e7\u00e3o do EEG no navegador"))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("<b>O que o m\u00e9dico recebe neste m\u00eas:</b>", styles["Body"]))
    elements.append(Spacer(1, 3))
    elements.append(item("Visualiza\u00e7\u00e3o completa dos 19 canais do EEG diretamente no navegador"))
    elements.append(item("Navega\u00e7\u00e3o pelo exame inteiro (avan\u00e7ar, retroceder, linha do tempo)"))
    elements.append(item("Zoom para examinar detalhes do tra\u00e7ado"))
    elements.append(item("Ajuste de escala de amplitude"))
    elements.append(item("Escolha de montagem (bipolar banana / referencial)"))
    elements.append(item("Filtros de limpeza aplicados no sinal"))
    elements.append(Spacer(1, 14))

    # -- MES 3 --
    elements.append(month_header("M\u00caS 3 \u2014 JUNHO 2026", "Limpeza autom\u00e1tica + Cadastro de pacientes"))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("<b>O que o m\u00e9dico recebe neste m\u00eas:</b>", styles["Body"]))
    elements.append(Spacer(1, 3))
    elements.append(item("Artefatos (movimentos, piscadas, ru\u00eddos) detectados e sinalizados automaticamente"))
    elements.append(item("Sinal limpo e preparado para a IA analisar com mais precis\u00e3o"))
    elements.append(item("Cadastro completo de pacientes"))
    elements.append(item("Hist\u00f3rico de exames por paciente"))
    elements.append(Spacer(1, 14))

    # -- MES 4 --
    elements.append(month_header("M\u00caS 4 \u2014 JULHO 2026", "IA detecta paroxismos epileptiformes"))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("<b>O que o m\u00e9dico recebe neste m\u00eas:</b>", styles["Body"]))
    elements.append(Spacer(1, 3))
    elements.append(item("A IA detecta automaticamente: pontas, ondas agudas, polipontas e complexos ponta-onda"))
    elements.append(item("Eventos detectados aparecem marcados no gr\u00e1fico do EEG"))
    elements.append(item("Cada detec\u00e7\u00e3o mostra localiza\u00e7\u00e3o, tipo e n\u00edvel de confian\u00e7a"))
    elements.append(item("Detec\u00e7\u00e3o com sensibilidade superior a 80%"))

    elements.append(PageBreak())

    # -- MES 5 --
    elements.append(month_header("M\u00caS 5 \u2014 AGOSTO 2026", "IA detecta todos os padr\u00f5es anormais"))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("<b>O que o m\u00e9dico recebe neste m\u00eas:</b>", styles["Body"]))
    elements.append(Spacer(1, 3))
    elements.append(item("Detec\u00e7\u00e3o de assimetria entre hemisf\u00e9rios (esquerdo vs. direito)"))
    elements.append(item("Identifica\u00e7\u00e3o autom\u00e1tica do ritmo de base"))
    elements.append(item("Avalia\u00e7\u00e3o de normalidade conforme a idade do paciente"))
    elements.append(item("Detec\u00e7\u00e3o de surto-supress\u00e3o, PLED, GRDA, ondas trif\u00e1sicas, delta focal"))
    elements.append(item("Detec\u00e7\u00e3o de FIRDA/OIRDA e beta excessivo"))
    elements.append(item("Classifica\u00e7\u00e3o autom\u00e1tica: EEG Normal ou EEG Anormal"))
    elements.append(Spacer(1, 8))
    elements.append(green_box(
        "<b>RESULTADO DO M\u00caS 5:</b> A IA analisa o exame completo e detecta todos os 14 padr\u00f5es "
        "anormais. A an\u00e1lise alimenta diretamente a gera\u00e7\u00e3o do laudo."))
    elements.append(Spacer(1, 14))

    # -- MES 6 --
    elements.append(month_header("M\u00caS 6 \u2014 SETEMBRO 2026", "Laudo profissional + Editor de revis\u00e3o"))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("<b>O que o m\u00e9dico recebe neste m\u00eas:</b>", styles["Body"]))
    elements.append(Spacer(1, 3))
    elements.append(item("Laudo gerado com base nos dados reais da an\u00e1lise (n\u00e3o mais gen\u00e9rico)"))
    elements.append(item("Tela dividida: EEG com marca\u00e7\u00f5es da IA \u00e0 esquerda + laudo \u00e0 direita"))
    elements.append(item("M\u00e9dico pode confirmar ou rejeitar cada detec\u00e7\u00e3o da IA"))
    elements.append(item("Editor de texto para ajustar o laudo antes de aprovar"))
    elements.append(item("O sistema aprende com as corre\u00e7\u00f5es do m\u00e9dico (melhora com o tempo)"))
    elements.append(item("Aviso legal autom\u00e1tico no rodap\u00e9 de cada laudo"))
    elements.append(Spacer(1, 14))

    # -- MES 7 --
    elements.append(month_header("M\u00caS 7 \u2014 OUTUBRO 2026", "PDF profissional + Funciona offline"))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("<b>O que o m\u00e9dico recebe neste m\u00eas:</b>", styles["Body"]))
    elements.append(Spacer(1, 3))
    elements.append(item("Laudo exportado em PDF com layout profissional (cabe\u00e7alho, corpo, assinatura)"))
    elements.append(item("PDF com logo da cl\u00ednica personaliz\u00e1vel"))
    elements.append(item("Download e impress\u00e3o direta"))
    elements.append(item("Sistema instal\u00e1vel no computador como aplicativo"))
    elements.append(item("Funciona mesmo sem internet \u2014 sincroniza quando voltar online"))
    elements.append(item("Hist\u00f3rico completo de todos os laudos emitidos"))
    elements.append(Spacer(1, 14))

    # -- MES 8 --
    elements.append(month_header("M\u00caS 8 \u2014 NOVEMBRO 2026", "Seguran\u00e7a e prote\u00e7\u00e3o dos dados"))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("<b>O que o m\u00e9dico recebe neste m\u00eas:</b>", styles["Body"]))
    elements.append(Spacer(1, 3))
    elements.append(item("Dados dos pacientes protegidos com criptografia"))
    elements.append(item("Registro de quem acessou e alterou cada dado (auditoria completa)"))
    elements.append(item("Controle de acesso por perfil (Administrador / M\u00e9dico / T\u00e9cnico)"))
    elements.append(item("Tela para gerenciar usu\u00e1rios do sistema"))
    elements.append(item("Backup autom\u00e1tico di\u00e1rio dos dados"))
    elements.append(item("Adequa\u00e7\u00e3o \u00e0 LGPD (Lei Geral de Prote\u00e7\u00e3o de Dados)"))

    elements.append(PageBreak())

    # -- MES 9 --
    elements.append(month_header("M\u00caS 9 \u2014 DEZEMBRO 2026", "Testes finais + Sistema em produ\u00e7\u00e3o"))
    elements.append(Spacer(1, 6))
    elements.append(Paragraph("<b>O que o m\u00e9dico recebe neste m\u00eas:</b>", styles["Body"]))
    elements.append(Spacer(1, 3))
    elements.append(item("Sistema testado com 10+ exames reais"))
    elements.append(item("Todos os ajustes finais aplicados"))
    elements.append(item("Sistema publicado na internet (acess\u00edvel de qualquer lugar)"))
    elements.append(item("Treinamento de uso do sistema"))
    elements.append(item("Material de apoio (guia r\u00e1pido de uso)"))
    elements.append(Spacer(1, 10))
    elements.append(blue_box(
        "<b>RESULTADO FINAL \u2014 DEZEMBRO 2026:</b><br/><br/>"
        "Sistema completo e funcional. O m\u00e9dico faz upload do exame, a IA analisa os 19 canais, "
        "detecta 14 tipos de padr\u00f5es anormais, gera o laudo automaticamente em linguagem m\u00e9dica "
        "profissional, e exporta em PDF. Redu\u00e7\u00e3o de 50% ou mais no tempo de elabora\u00e7\u00e3o de laudos."))

    elements.append(PageBreak())

    # ==============================================================
    # TIMELINE VISUAL
    # ==============================================================
    elements.append(Paragraph("VIS\u00c3O GERAL", styles["H1"]))
    elements.append(hr())

    timeline = [
        ["M\u00eas", "Per\u00edodo", "O que ser\u00e1 entregue", "Marco principal"],
        ["1", "Abril/26", "Upload do exame + Laudo gerado pela IA", "PRIMEIRO LAUDO AUTOM\u00c1TICO"],
        ["2", "Maio/26", "Visualiza\u00e7\u00e3o dos 19 canais do EEG + Filtros", "VER O EEG NO SISTEMA"],
        ["3", "Junho/26", "Limpeza autom\u00e1tica de artefatos + Cadastro de pacientes", "SINAL LIMPO"],
        ["4", "Julho/26", "IA detecta pontas, ondas agudas e polipontas", "IA DETECTANDO PADR\u00d5ES"],
        ["5", "Agosto/26", "IA detecta todos os 14 padr\u00f5es anormais", "AN\u00c1LISE COMPLETA"],
        ["6", "Setembro/26", "Laudo avan\u00e7ado + Editor de revis\u00e3o para o m\u00e9dico", "LAUDO PROFISSIONAL"],
        ["7", "Outubro/26", "PDF pronto para impress\u00e3o + Funciona offline", "PDF + OFFLINE"],
        ["8", "Novembro/26", "Seguran\u00e7a dos dados + LGPD + Auditoria", "DADOS PROTEGIDOS"],
        ["9", "Dezembro/26", "Testes finais + Sistema publicado na internet", "SISTEMA EM PRODU\u00c7\u00c3O"],
    ]

    t_data = []
    for i, row in enumerate(timeline):
        if i == 0:
            t_data.append([Paragraph(c, styles["TH"]) for c in row])
        else:
            t_data.append([Paragraph(c, styles["TC"]) for c in row])

    t = Table(t_data, colWidths=[W * 0.06, W * 0.12, W * 0.48, W * 0.34], repeatRows=1)
    cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("GRID", (0, 0), (-1, -1), 0.5, GREY_LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),
        ("BACKGROUND", (0, 1), (-1, 1), GREEN_LIGHT),
        ("BACKGROUND", (0, -1), (-1, -1), BLUE_LIGHT),
    ]
    for i in range(2, len(t_data) - 1, 2):
        cmds.append(("BACKGROUND", (0, i), (-1, i), ALT_ROW))
    t.setStyle(TableStyle(cmds))
    elements.append(t)

    elements.append(PageBreak())

    # ==============================================================
    # INVESTIMENTO
    # ==============================================================
    elements.append(Paragraph("INVESTIMENTO", styles["H1"]))
    elements.append(hr())

    elements.append(Paragraph("Custo mensal \u2014 tudo incluso", styles["H2"]))

    cost_data = [
        [Paragraph("<b>Item</b>", styles["TH"]),
         Paragraph("<b>O que \u00e9</b>", styles["TH"]),
         Paragraph("<b>Valor/m\u00eas</b>", styles["TH"])],
        [Paragraph("Desenvolvimento", styles["TC"]),
         Paragraph("Programa\u00e7\u00e3o do sistema por desenvolvedor s\u00eanior", styles["TC"]),
         Paragraph("<b>R$ 1.600,00</b>", styles["TC"])],
        [Paragraph("Intelig\u00eancia Artificial", styles["TC"]),
         Paragraph("IA que analisa os exames e escreve os laudos", styles["TC"]),
         Paragraph("<b>R$ 50,00</b>", styles["TC"])],
        [Paragraph("Hospedagem e dom\u00ednio", styles["TC"]),
         Paragraph("Servidor online + endere\u00e7o do site", styles["TC"]),
         Paragraph("<b>R$ 30,00</b>", styles["TC"])],
        [Paragraph("<b>TOTAL MENSAL</b>", styles["TC"]),
         Paragraph("", styles["TC"]),
         Paragraph("<b>R$ 1.680,00</b>", styles["TC"])],
    ]
    ct = Table(cost_data, colWidths=[W * 0.22, W * 0.52, W * 0.26])
    ct.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), HEADER_BG),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("GRID", (0, 0), (-1, -1), 0.5, GREY_LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("BACKGROUND", (0, -1), (-1, -1), GREEN_LIGHT),
        ("BACKGROUND", (0, 1), (-1, 1), ALT_ROW),
        ("BACKGROUND", (0, 3), (-1, 3), ALT_ROW),
    ]))
    elements.append(ct)

    elements.append(Spacer(1, 16))
    elements.append(Paragraph("Investimento total do projeto", styles["H2"]))

    total_data = [
        [Paragraph("<b>Dura\u00e7\u00e3o</b>", styles["TC"]), Paragraph("9 meses", styles["TC"])],
        [Paragraph("<b>Custo por m\u00eas</b>", styles["TC"]), Paragraph("R$ 1.680,00", styles["TC"])],
        [Paragraph("<b>TOTAL DO PROJETO</b>", styles["TC"]), Paragraph("<b>R$ 15.120,00</b>", styles["TC"])],
    ]
    tt = Table(total_data, colWidths=[W * 0.40, W * 0.60])
    tt.setStyle(TableStyle([
        ("GRID", (0, 0), (-1, -1), 0.5, GREY_LINE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ("LEFTPADDING", (0, 0), (-1, -1), 10),
        ("BACKGROUND", (0, 0), (0, -1), BLUE_LIGHT),
        ("BACKGROUND", (0, -1), (-1, -1), GREEN_LIGHT),
    ]))
    elements.append(tt)

    elements.append(Spacer(1, 20))
    elements.append(Paragraph(
        "<i>Ap\u00f3s a conclus\u00e3o do projeto, o custo para manter o sistema funcionando \u00e9 de apenas "
        "<b>R$ 80/m\u00eas</b> (R$ 50 da IA + R$ 30 de hospedagem).</i>", styles["Body"]))

    elements.append(Spacer(1, 24))
    elements.append(Paragraph("PARA INICIAR", styles["H2"]))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("Para dar in\u00edcio ao desenvolvimento, s\u00e3o necess\u00e1rios apenas dois itens:", styles["Body"]))
    elements.append(Spacer(1, 4))
    elements.append(Paragraph("<b>1.</b> O arquivo do exame (.EDF) \u2014 o arquivo que sai do aparelho de EEG", styles["BulletItem"]))
    elements.append(Paragraph("<b>2.</b> Aprova\u00e7\u00e3o deste cronograma", styles["BulletItem"]))

    doc.build(elements)
    print(f"PDF gerado: {filename}")


if __name__ == "__main__":
    build_pdf()

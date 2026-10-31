# -*- coding: utf-8 -*-
"""
Monta o relatório técnico em .docx a partir do Markdown de `docs/relatorio_tecnico.md`.

O relatório é um artefato do projeto, então a regra T9 vale para ele também:
títulos, tabelas e destaques usam a paleta v06, e nenhuma cor vem de fora dela.

Gera os dois formatos da convenção das fases anteriores, sem depender de GUI:
o .docx (python-docx) e o .pdf (reportlab), a partir da MESMA fonte Markdown.

Uso:  python3 src/monta_relatorio.py
Saída: docs/technical_report_phase4_<VERSAO>.docx · .pdf  (VERSAO definida abaixo)
"""

import os
import re
import sys

from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paleta import ESTRUTURA, CHAMADAS, BASE
from determinismo import datar_pdf, fixar_docx, fixar_propriedades, fixar_reportlab

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(RAIZ, "docs", "relatorio_tecnico.md")
VERSAO = "v1_powerbi"

# Metadados gravados no .docx e no .pdf — o que aparece nas propriedades do arquivo
TITULO = "Relatório Técnico — Tech Challenge Fase 4 — Grupo 12"
AUTORIA = "Grupo 12 — POSTECH DTAT"
ASSUNTO = "Amazon Product Performance & Customer Insights"
# bater com a linha de versão de docs/relatorio_tecnico.md
PALAVRAS_CHAVE = "Tech Challenge; Fase 4; Power BI; Customer Insights; marketplace"
OUT = os.path.join(RAIZ, "docs", f"technical_report_phase4_{VERSAO}.docx")
OUT_PDF = os.path.join(RAIZ, "docs", f"technical_report_phase4_{VERSAO}.pdf")

TINTA = RGBColor.from_string(ESTRUTURA["tinta"][1:])
SECUND = RGBColor.from_string(ESTRUTURA["secundario"][1:])
TEAL = RGBColor.from_string(CHAMADAS["favoravel"][1:])
LARANJA = RGBColor.from_string(CHAMADAS["atencao"][1:])
DIVISOR = BASE["divisor"][1:]
CANVAS = BASE["canvas"][1:]


def celulas(linha):
    """Divide uma linha de tabela markdown respeitando o pipe escapado `\\|`.

    Sem isto, uma célula como `Computers & Acc. \\| Networking Devices` quebra em
    duas e a linha inteira desloca uma coluna — foi o que acontecia com a tabela
    de subcategorias, cujo rótulo carrega a hierarquia separada por pipe.
    """
    bruto = re.split(r"(?<!\\)\|", linha.strip().strip("|"))
    return [c.strip().replace("\\|", "|") for c in bruto]


def rotulo_secao(titulo):
    """"§5.5" para "5.5 Q3 · Existe relação…"; o título curto quando não há número."""
    m = re.match(r"(\d+(?:\.\d+)*)\.?\s", titulo)
    return f"§{m.group(1)}" if m else titulo.split("·")[0].split("—")[0].strip()


def varre_indices(bruto):
    """Sumário, figuras e tabelas lidos do Markdown numa ÚNICA passagem.

    Uma passagem só, e os dois formatos consomem a mesma lista. Quando cada
    saída varria o texto por conta própria, o índice de tabelas do .docx
    listava só a primeira coluna e o do .pdf as três primeiras — dois índices
    diferentes para o mesmo relatório, que é a classe de divergência que este
    projeto combateu em todos os outros artefatos.

    Cada entrada de tabela diz ONDE a tabela está. Sem a seção, o índice
    repete "Base · n · Quando usar" três vezes sem dizer em qual delas, e
    deixa de servir para localizar coisa alguma.
    """
    linhas = bruto.split("\n")
    secoes, figuras, tabelas = [], [], []
    onde = ""
    for i, ln in enumerate(linhas):
        if ln.startswith("## ") and not ln.startswith("###"):
            secoes.append(("h2", ln[3:].strip()))
            onde = rotulo_secao(ln[3:].strip())
        elif ln.startswith("### "):
            secoes.append(("h3", ln[4:].strip()))
            onde = rotulo_secao(ln[4:].strip())
        m = re.match(r"!\[([^\]]*)\]", ln.strip())
        if m:
            figuras.append(m.group(1))
        if (ln.startswith("|") and i + 1 < len(linhas)
                and re.match(r"^\|[\s:|-]+\|$", linhas[i + 1].strip())):
            cels = [c for c in (c.strip("*` ") for c in celulas(ln)) if c]
            if cels:
                # o cabeçalho pode trazer marcação; o índice é texto, não markdown
                limpo = [re.sub(r"[*`_]", "", c).strip() for c in cels[:3]]
                tabelas.append(" · ".join(([onde] if onde else []) + limpo))
    return secoes, figuras, tabelas


def sombrear(celula, hexcor):
    tc = celula._tc.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:fill"), hexcor)
    tc.append(shd)


def inline(paragrafo, texto):
    """Interpreta **negrito**, *itálico* e `código` de um trecho markdown."""
    # "**a *b* c**" precisa casar o negrito INTEIRO; com [^*]+ o padrão parava no
    # asterisco interno e os dois pedaços saíam crus no documento.
    for parte in re.split(r"(\*\*.+?\*\*|(?<!\*)\*[^*]+\*(?!\*)|`[^`]+`)", texto):
        if not parte:
            continue
        r = paragrafo.add_run()
        if parte.startswith("**") and parte.endswith("**"):
            r.text = parte[2:-2].replace("*", "")      # itálico aninhado: fica só o negrito
            r.bold = True
        elif parte.startswith("`") and parte.endswith("`"):
            r.text = parte[1:-1]
            r.font.name = "Consolas"
            r.font.size = Pt(9)
            r.font.color.rgb = TEAL
        elif parte.startswith("*") and parte.endswith("*"):
            r.text = parte[1:-1]
            r.italic = True
        else:
            r.text = parte
        if r.font.color.rgb is None:
            r.font.color.rgb = TINTA


def estilos(doc):
    n = doc.styles["Normal"]
    n.font.name = "Calibri"
    n.font.size = Pt(10.5)
    n.font.color.rgb = TINTA
    n.paragraph_format.space_after = Pt(7)
    n.paragraph_format.line_spacing = 1.15
    for nome, tam, cor in [("Heading 1", 17, TEAL), ("Heading 2", 13.5, TINTA), ("Heading 3", 11.5, SECUND)]:
        s = doc.styles[nome]
        s.font.name = "Calibri"
        s.font.size = Pt(tam)
        s.font.bold = True
        s.font.color.rgb = cor
        s.paragraph_format.space_before = Pt(15 if nome == "Heading 1" else 11)
        s.paragraph_format.space_after = Pt(5)


def indices_docx(doc, secoes, figuras, tabelas):
    """Sumário, Índice de Figuras e Índice de Tabelas no .docx.

    As fases 2 e 3 traziam os três. Sem eles, quem lê só o começo — ou uma
    ferramenta que trunca a extração — não tem como saber o que vem depois.
    """
    doc.add_heading("Sumário", level=1)
    for nivel, titulo in secoes:
        if titulo.lower().startswith(("sumário", "índice")):
            continue
        p = doc.add_paragraph()
        p.paragraph_format.left_indent = Cm(0 if nivel == "h2" else 0.7)
        p.paragraph_format.space_after = Pt(1)
        r = p.add_run(titulo)
        r.bold = (nivel == "h2")
        r.font.size = Pt(9.5 if nivel == "h2" else 9)
        r.font.color.rgb = TINTA if nivel == "h2" else SECUND
    for rotulo, itens in [("Índice de Figuras", figuras), ("Índice de Tabelas", tabelas)]:
        if not itens:
            continue
        doc.add_heading(rotulo, level=1)
        for it in itens:
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.5)
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(it)
            r.font.size = Pt(8.5)
            r.font.color.rgb = SECUND
    doc.add_page_break()


def main():
    if not os.path.exists(MD):
        sys.exit(f"ERRO: {MD} não existe. Gere o Markdown antes.")
    doc = Document()
    estilos(doc)
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Cm(2.2)
        s.left_margin = s.right_margin = Cm(2.4)

    bruto = open(MD, encoding="utf-8").read()
    secoes, figuras, tabelas = varre_indices(bruto)
    linhas = bruto.split("\n")
    i = 0
    while i < len(linhas):
        ln = linhas[i].rstrip()

        # imagem
        m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", ln.strip())
        if m:
            legenda, caminho = m.group(1), m.group(2)
            real = os.path.normpath(os.path.join(os.path.dirname(MD), caminho))
            if os.path.exists(real):
                doc.add_picture(real, width=Cm(16.2))
                doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                r = p.add_run(legenda)
                r.font.size = Pt(8.5)
                r.italic = True
                r.font.color.rgb = SECUND
            else:
                print(f"  AVISO: figura não encontrada — {caminho}")
            i += 1
            continue

        # tabela
        if ln.startswith("|") and i + 1 < len(linhas) and re.match(r"^\|[\s:|-]+\|$", linhas[i + 1].strip()):
            bloco = []
            while i < len(linhas) and linhas[i].strip().startswith("|"):
                bloco.append(celulas(linhas[i]))
                i += 1
            cab, corpo = bloco[0], bloco[2:]
            t = doc.add_table(rows=1, cols=len(cab))
            t.style = "Table Grid"
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            for j, c in enumerate(cab):
                cel = t.rows[0].cells[j]
                cel.text = ""
                inline(cel.paragraphs[0], c)
                for r in cel.paragraphs[0].runs:
                    r.bold = True
                    r.font.size = Pt(9)
                sombrear(cel, DIVISOR)
            for lin in corpo:
                cells = t.add_row().cells
                for j, c in enumerate(lin[:len(cab)]):
                    cells[j].text = ""
                    inline(cells[j].paragraphs[0], c)
                    for r in cells[j].paragraphs[0].runs:
                        r.font.size = Pt(9)
            doc.add_paragraph()
            continue

        # títulos
        if ln.startswith("#"):
            nivel = len(ln) - len(ln.lstrip("#"))
            # título não leva marcação: o Word já o formata, e "**não**" saía cru
            texto = re.sub(r"[*`]", "", ln.lstrip("#").strip())
            if nivel == 1:
                doc.add_heading(texto, level=1)
            else:
                doc.add_heading(texto, level=min(nivel, 3))
            i += 1
            continue

        # citação
        if ln.startswith(">"):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.8)
            inline(p, ln.lstrip("> ").strip())
            for r in p.runs:
                r.italic = True
            i += 1
            continue

        # lista
        if re.match(r"^\s*[-*]\s+", ln):
            p = doc.add_paragraph(style="List Bullet")
            inline(p, re.sub(r"^\s*[-*]\s+", "", ln))
            i += 1
            continue
        if re.match(r"^\s*\d+\.\s+", ln):
            p = doc.add_paragraph(style="List Number")
            inline(p, re.sub(r"^\s*\d+\.\s+", "", ln))
            i += 1
            continue

        # bloco de código cercado: a cerca não é conteúdo
        if ln.strip().startswith("```"):
            i += 1
            while i < len(linhas) and not linhas[i].strip().startswith("```"):
                p = doc.add_paragraph()
                r = p.add_run(linhas[i].rstrip())
                r.font.name, r.font.size, r.font.color.rgb = "Consolas", Pt(9), TEAL
                i += 1
            i += 1
            continue

        # separador
        if ln.strip() in ("---", "***"):
            i += 1
            continue

        if ln.strip():
            p = doc.add_paragraph()
            inline(p, ln.strip())
        i += 1

    # Os índices precisam dos títulos coletados; inseridos no topo ao final.
    corpo = list(doc.element.body)
    for el in corpo:
        doc.element.body.remove(el)
    indices_docx(doc, secoes, figuras, tabelas)
    for el in corpo:
        doc.element.body.append(el)
    # Metadados do arquivo. Sem isto o python-docx grava o padrão da biblioteca
    # — Autor "python-docx", Comentários "generated by python-docx" —, que é o
    # que aparece em Arquivo > Propriedades para quem abre o relatório.
    cp = doc.core_properties
    cp.author = AUTORIA
    cp.last_modified_by = AUTORIA
    cp.title = TITULO
    cp.subject = ASSUNTO
    cp.keywords = PALAVRAS_CHAVE
    cp.comments = ""
    fixar_propriedades(cp)
    doc.save(OUT)
    fixar_docx(OUT)
    print(f"  {OUT}")
    print(f"  {len(figuras)} figuras · {len(tabelas)} tabelas")
    total = sum(len(p.text) for p in doc.paragraphs)
    print(f"  {total:,} caracteres em {len(doc.paragraphs)} parágrafos".replace(",", "."))




# ---------------------------------------------------------------------------
# PDF — mesma fonte Markdown, sem depender do Word
# ---------------------------------------------------------------------------
def gerar_pdf():
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_JUSTIFY
    from reportlab.platypus import (SimpleDocTemplate, Paragraph, Spacer, Image,
                                    Table, TableStyle, KeepTogether, PageBreak)

    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont as RLFont
    from reportlab.lib.fonts import addMapping

    # Fontes embutidas: Helvetica não tem ⁻⁸, ρ nem ≥ — sairiam como quadrados.
    FDIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    for nome, arq in [("DejaVu", "DejaVuSans.ttf"), ("DejaVu-Bold", "DejaVuSans-Bold.ttf"),
                      ("DejaVu-Obl", "DejaVuSans-Oblique.ttf"),
                      ("DejaVu-BoldObl", "DejaVuSans-BoldOblique.ttf"),
                      ("DejaVuMono", "DejaVuSansMono.ttf")]:
        pdfmetrics.registerFont(RLFont(nome, os.path.join(FDIR, arq)))
    addMapping("DejaVu", 0, 0, "DejaVu")
    addMapping("DejaVu", 1, 0, "DejaVu-Bold")
    addMapping("DejaVu", 0, 1, "DejaVu-Obl")
    addMapping("DejaVu", 1, 1, "DejaVu-BoldObl")

    def cor(h):
        return colors.HexColor(h)

    ss = getSampleStyleSheet()
    est = {
        "corpo": ParagraphStyle("corpo", parent=ss["Normal"], fontName="DejaVu",
                                fontSize=9.2, leading=13.4, textColor=cor(ESTRUTURA["tinta"]),
                                alignment=TA_JUSTIFY, spaceAfter=6),
        "h1": ParagraphStyle("h1", parent=ss["Heading1"], fontName="DejaVu-Bold",
                             fontSize=16, leading=20, textColor=cor(CHAMADAS["favoravel"]),
                             spaceBefore=16, spaceAfter=7),
        "h2": ParagraphStyle("h2", parent=ss["Heading2"], fontName="DejaVu-Bold",
                             fontSize=12.5, leading=16, textColor=cor(ESTRUTURA["tinta"]),
                             spaceBefore=12, spaceAfter=5),
        "h3": ParagraphStyle("h3", parent=ss["Heading3"], fontName="DejaVu-Bold",
                             fontSize=10.5, leading=14, textColor=cor(ESTRUTURA["secundario"]),
                             spaceBefore=9, spaceAfter=4),
        "leg": ParagraphStyle("leg", parent=ss["Normal"], fontName="DejaVu-Obl",
                              fontSize=7.8, leading=10, textColor=cor(ESTRUTURA["secundario"]),
                              alignment=TA_CENTER, spaceAfter=9),
        "cit": ParagraphStyle("cit", parent=ss["Normal"], fontName="DejaVu-Obl",
                              fontSize=9.2, leading=13.4, textColor=cor(ESTRUTURA["secundario"]),
                              leftIndent=14, spaceAfter=6),
        "item": ParagraphStyle("item", parent=ss["Normal"], fontName="DejaVu",
                               fontSize=9.2, leading=13.2, textColor=cor(ESTRUTURA["tinta"]),
                               leftIndent=12, bulletIndent=4, spaceAfter=3),
    }

    # A fonte embutida não tem estes glifos: sem substituição, ❌ e ⚠️ saem como quadrado
    # vazio — e um quadrado vazio numa coluna de situação inverte o sentido da linha.
    # Por isso cada um vira a palavra que ele significa, não um símbolo parecido.
    EMOJI = {"⏳": "a produzir", "✅": "sim", "❌": "não", "⚠️": "parcial", "⭐": "",
             "🔸": "[decisão de Ricardo]", "📊": "", "🎯": "", "📦": "", "🗂️": "",
             "📐": "", "🎨": "", "🔍": "", "📚": "", "🤖": "", "⚖️": "", "🧾": "", "👥": ""}

    def rico(txt):
        """markdown inline -> marcação do reportlab"""
        for e, sub in EMOJI.items():
            txt = txt.replace(e, sub)
        txt = (txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
        txt = re.sub(r"\*\*\*([^*]+)\*\*\*", r"<b><i>\1</i></b>", txt)   # ***x***
        # negrito primeiro, e o itálico DENTRO dele: "**a *b* c**" saía com os asteriscos
        # internos crus, porque o padrão de negrito não aceitava asterisco no meio.
        txt = re.sub(r"\*\*(.+?)\*\*", lambda m: "<b>" + re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\\1</i>", m.group(1)) + "</b>", txt)
        txt = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", txt)
        txt = re.sub(r"`([^`]+)`", r'<font face="DejaVuMono" size="8.2" color="'
                     + CHAMADAS["favoravel"] + r'">\1</font>', txt)
        txt = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", txt)
        return txt

    # ---- Sumário e índices, extraídos do próprio Markdown -------------------
    # Sem eles, um leitor (ou uma ferramenta de extração) que pare no meio do
    # documento não tem como saber o que vem depois. Convenção das fases 2 e 3.
    bruto = open(MD, encoding="utf-8").read()
    secoes, figs_idx, tabs_idx = varre_indices(bruto)

    fluxo = []
    linhas = bruto.split("\n")
    i = 0
    while i < len(linhas):
        ln = linhas[i].rstrip()

        # Bloco de código cercado: as cercas ``` não são conteúdo, e o que está dentro
        # é comando — vai em monoespaçada, sem interpretar markdown.
        if ln.strip().startswith("```"):
            i += 1
            codigo = []
            while i < len(linhas) and not linhas[i].strip().startswith("```"):
                codigo.append(linhas[i].rstrip())
                i += 1
            i += 1
            if codigo:
                texto = "<br/>".join(c.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
                                     .replace(" ", "&nbsp;") for c in codigo)
                fluxo.append(Paragraph(f'<font face="DejaVuMono" size="8.2">{texto}</font>', est["corpo"]))
            continue

        m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", ln.strip())
        if m:
            real = os.path.normpath(os.path.join(os.path.dirname(MD), m.group(2)))
            if os.path.exists(real):
                from PIL import Image as PILImage
                w, h = PILImage.open(real).size
                larg = 16.0 * cm
                fluxo.append(KeepTogether([Image(real, width=larg, height=larg * h / w),
                                           Spacer(1, 3), Paragraph(rico(m.group(1)), est["leg"])]))
            i += 1
            continue

        if ln.startswith("|") and i + 1 < len(linhas) and re.match(r"^\|[\s:|-]+\|$", linhas[i + 1].strip()):
            bloco = []
            while i < len(linhas) and linhas[i].strip().startswith("|"):
                bloco.append(celulas(linhas[i]))
                i += 1
            cab, corpo = bloco[0], bloco[2:]
            ncols = len(cab)
            dados = [[Paragraph(rico(c), ParagraphStyle("th", parent=est["corpo"], fontSize=8,
                                                        leading=10.5, fontName="DejaVu-Bold",
                                                        alignment=TA_CENTER)) for c in cab]]
            for lin in corpo:
                dados.append([Paragraph(rico(c), ParagraphStyle("td", parent=est["corpo"],
                                                                fontSize=8, leading=10.5,
                                                                alignment=TA_JUSTIFY))
                              for c in (lin + [""] * ncols)[:ncols]])
            t_ = Table(dados, colWidths=[16.0 * cm / ncols] * ncols, repeatRows=1)
            t_.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), cor(BASE["divisor"])),
                ("GRID", (0, 0), (-1, -1), 0.4, cor(ESTRUTURA["grade"])),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4),
                ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3),
                ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
            ]))
            fluxo.append(t_)
            fluxo.append(Spacer(1, 9))
            continue

        if ln.startswith("#"):
            nivel = len(ln) - len(ln.lstrip("#"))
            fluxo.append(Paragraph(rico(ln.lstrip("#").strip()), est[f"h{min(nivel,3)}"]))
            i += 1
            continue
        if ln.startswith(">"):
            fluxo.append(Paragraph(rico(ln.lstrip("> ").strip()), est["cit"]))
            i += 1
            continue
        if re.match(r"^\s*[-*]\s+", ln):
            fluxo.append(Paragraph(rico(re.sub(r"^\s*[-*]\s+", "", ln)), est["item"], bulletText="\u2022"))
            i += 1
            continue
        if re.match(r"^\s*\d+\.\s+", ln):
            fluxo.append(Paragraph(rico(re.sub(r"^\s*\d+\.\s+", "", ln)), est["item"], bulletText="\u2013"))
            i += 1
            continue
        if ln.strip() in ("---", "***"):
            fluxo.append(Spacer(1, 7))
            i += 1
            continue
        if ln.strip():
            fluxo.append(Paragraph(rico(ln.strip()), est["corpo"]))
        i += 1

    def indice(titulo, itens, estilo_item):
        bloco = [Paragraph(titulo, est["h1"])]
        for it in itens:
            bloco.append(Paragraph(rico(it), estilo_item))
        bloco.append(Spacer(1, 10))
        return bloco

    est["sum1"] = ParagraphStyle("sum1", parent=est["corpo"], fontSize=9.4, leading=13,
                                 spaceAfter=2, fontName="DejaVu-Bold")
    est["sum2"] = ParagraphStyle("sum2", parent=est["corpo"], fontSize=8.8, leading=12,
                                 leftIndent=14, spaceAfter=1)
    est["idx"] = ParagraphStyle("idx", parent=est["corpo"], fontSize=8.4, leading=11.5,
                                leftIndent=8, spaceAfter=1)

    # Capa. Sem ela o PDF abria direto no Sumário, e o título, a autoria e a versão só
    # apareciam na página 5 — quem recebe o arquivo precisa saber o que é na primeira tela.
    linha_versao = next((linha_.strip() for linha_ in bruto.split("\n") if linha_.startswith("**Versão ")), "")
    est["capa_t"] = ParagraphStyle("capa_t", parent=est["corpo"], fontSize=21, leading=26,
                                   alignment=1, textColor=colors.HexColor(ESTRUTURA["tinta"]),
                                   fontName="DejaVu-Bold", spaceAfter=10)
    est["capa_s"] = ParagraphStyle("capa_s", parent=est["corpo"], fontSize=13, leading=18,
                                   alignment=1, textColor=colors.HexColor(ESTRUTURA["secundario"]),
                                   spaceAfter=26)
    est["capa_c"] = ParagraphStyle("capa_c", parent=est["corpo"], fontSize=10, leading=16,
                                   alignment=1, textColor=colors.HexColor(ESTRUTURA["tinta"]))
    capa = [Spacer(1, 150),
            Paragraph("Relatório Técnico", est["capa_t"]),
            Paragraph("Amazon Product Performance &amp; Customer Insights", est["capa_s"]),
            Paragraph("Tech Challenge Fase 4 · POSTECH DTAT · Grupo 12", est["capa_c"]),
            Spacer(1, 14),
            Paragraph("Efraim Oliveira · Érica Tarsis · Ricardo Moraes<br/>Rodrigo Bernardino · Thiago Galvão", est["capa_c"]),
            Spacer(1, 26),
            Paragraph(rico(linha_versao or VERSAO), est["capa_c"]),
            PageBreak()]

    sumario = capa + [Paragraph("Sumário", est["h1"])]
    for nivel, titulo in secoes:
        if titulo.lower().startswith(("sumário", "índice")):
            continue
        sumario.append(Paragraph(rico(titulo), est["sum1"] if nivel == "h2" else est["sum2"]))
    sumario.append(Spacer(1, 12))
    if figs_idx:
        sumario += indice("Índice de Figuras", figs_idx, est["idx"])
    if tabs_idx:
        sumario += indice("Índice de Tabelas", tabs_idx, est["idx"])

    def rodape(canvas, doc_):
        canvas.saveState()
        # Página branca: documento impresso não leva o creme do dashboard.
        canvas.setFont("DejaVu", 7.5)
        canvas.setFillColor(cor(ESTRUTURA["secundario"]))
        canvas.drawString(2.2 * cm, 1.2 * cm, f"Tech Challenge Fase 4 · Grupo 12 · Relatório Técnico {VERSAO}")
        canvas.drawRightString(A4[0] - 2.2 * cm, 1.2 * cm, str(doc_.page))
        canvas.restoreState()

    fixar_reportlab()
    doc_pdf = SimpleDocTemplate(OUT_PDF, pagesize=A4, topMargin=2.0 * cm,
                                bottomMargin=2.0 * cm, leftMargin=2.5 * cm, rightMargin=2.5 * cm,
                                title=TITULO, author=AUTORIA, subject=ASSUNTO,
                                keywords=PALAVRAS_CHAVE, creator=AUTORIA)
    doc_pdf.build(sumario + fluxo, onFirstPage=rodape, onLaterPages=rodape)
    print(f"  {OUT_PDF}")
    linearizar(OUT_PDF)
    datar_pdf(OUT_PDF)


def linearizar(caminho):
    """Reescreve o PDF em modo linearizado ('fast web view').

    POR QUE ISTO EXISTE. O reportlab grava PDF não linearizado, e dois
    revisores independentes relataram que o documento "cortava" — um na
    página 23, outro na 29. O arquivo estava íntegro nas duas vezes (99
    páginas, conferidas por pypdf E por poppler). O sintoma é de visualizador
    que renderiza por streaming: preview de webmail, do Drive, de app de
    mensagem. Sem linearização o leitor precisa do arquivo inteiro antes de
    paginar; se o stream é interrompido, ele mostra o que tem e para. Páginas
    de corte DIFERENTES entre revisores é a assinatura disso, não de defeito
    no arquivo.

    Linearizar reordena os objetos para que a primeira página venha antes do
    resto, o que torna a renderização progressiva possível. Efeito colateral
    bem-vindo: o arquivo fica ~17% menor.
    """
    try:
        import pikepdf
    except ImportError:
        print("  ⚠ pikepdf ausente — PDF gravado SEM linearização.")
        print("    Visualizadores que renderizam por streaming podem exibir o")
        print("    documento truncado. Instale com: pip install -r requirements.txt")
        return
    import os
    antes = os.path.getsize(caminho)
    with pikepdf.open(caminho, allow_overwriting_input=True) as pdf:
        paginas = len(pdf.pages)
        pdf.save(caminho, linearize=True, deterministic_id=True)
    depois = os.path.getsize(caminho)
    print(f"  linearizado (fast web view) · {paginas} páginas · "
          f"{antes/1048576:.2f} MB -> {depois/1048576:.2f} MB")


if __name__ == "__main__":
    main()
    gerar_pdf()

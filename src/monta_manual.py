# -*- coding: utf-8 -*-
"""
Monta o Manual de Leitura do Dashboard em .docx e .pdf a partir de
`docs/manual_leitura_dashboard.md`.

O manual explica o que cada elemento de cada página do dashboard mostra e como
lê-lo. Cada página aparece como imagem, com marcadores numerados sobre os
elementos; a tabela logo abaixo explica cada número.

As imagens saem do PDF exportado do Power BI. Quando o dashboard mudar:

    python3 src/monta_manual.py --pdf caminho/do/dashboard.pdf

renderiza as 8 páginas, desenha os marcadores (posições em MARCAS, abaixo) e
grava `docs/manual_imagens/`. Sem `--pdf`, usa as imagens já gravadas.

Saída: docs/manual_leitura_dashboard_<VERSAO>.docx · .pdf

A regra T9 vale aqui também: cores só da paleta v06.
"""

import argparse
import os
import re
import subprocess
import sys
import tempfile

from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.shared import Cm, Pt, RGBColor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from determinismo import datar_pdf, fixar_docx, fixar_propriedades, fixar_reportlab
from monta_relatorio import celulas, estilos, inline, sombrear
from paleta import BASE, CHAMADAS, ESTRUTURA

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MD = os.path.join(RAIZ, "docs", "manual_leitura_dashboard.md")
PASTA_IMG = os.path.join(RAIZ, "docs", "manual_imagens")
VERSAO = "v1"
OUT = os.path.join(RAIZ, "docs", f"manual_leitura_dashboard_{VERSAO}.docx")
OUT_PDF = os.path.join(RAIZ, "docs", f"manual_leitura_dashboard_{VERSAO}.pdf")

TITULO = "Manual de Leitura do Dashboard — Tech Challenge Fase 4 — Grupo 12"
AUTORIA = "Grupo 12 — POSTECH DTAT"
ASSUNTO = "Amazon Product Performance & Customer Insights"
PALAVRAS_CHAVE = "Tech Challenge; Fase 4; Power BI; dashboard; manual de leitura"
EQUIPE = "Efraim Oliveira · Érica Tarsis · Ricardo Moraes · Rodrigo Bernardino · Thiago Galvão"



def _pula_manual(tipo, cont):
    """No corpo do manual não entram o título (vai para a capa) nem a linha de versão."""
    return tipo == "h1" or (tipo == "par" and cont.startswith("**Versão "))


# O que muda entre os documentos montados por este gerador. O roteiro do vídeo
# (src/monta_roteiro.py) usa o mesmo gerador com outra configuração.
MANUAL = {
    "out_docx": OUT, "out_pdf": OUT_PDF, "titulo": TITULO, "palavras": PALAVRAS_CHAVE,
    "capa": "Manual de Leitura do Dashboard",
    "rodape": "Tech Challenge Fase 4 · Grupo 12 · Manual de Leitura do Dashboard",
    "sumario": True, "quebra_h2": True, "pula": _pula_manual,
}

TINTA = RGBColor.from_string(ESTRUTURA["tinta"][1:])
SECUND = RGBColor.from_string(ESTRUTURA["secundario"][1:])
TEAL = RGBColor.from_string(CHAMADAS["favoravel"][1:])
DIVISOR = BASE["divisor"][1:]

# ---------------------------------------------------------------------------
# Imagens anotadas
# ---------------------------------------------------------------------------
# Página do PDF do dashboard -> arquivo de imagem do manual.
PAGINAS = {
    0: (3, "manual_00_comuns.png"),       # elementos comuns, marcados sobre a página 2a
    1: (1, "manual_01_pagina_inicial.png"),
    2: (2, "manual_02_visao_executiva.png"),
    3: (3, "manual_03_categorias.png"),
    4: (4, "manual_04_quadrantes.png"),
    5: (5, "manual_05_rankings.png"),
    6: (6, "manual_06_precos.png"),
    7: (7, "manual_07_customer_insights.png"),
    8: (8, "manual_08_recomendacoes.png"),
}

# Centro de cada marcador, em pixels de uma imagem com 2.000 de largura.
# A ordem é a da tabela do manual; o rótulo é o texto do marcador.
MARCAS = {
    0: [("A", 815, 60), ("B", 958, 33), ("C", 22, 122), ("D", 158, 1106)],
    1: [("1", 28, 28), ("2", 36, 306), ("3", 492, 298), ("4", 1413, 306)],
    2: [("1", 1428, 54), ("2", 33, 188), ("3", 428, 188), ("4", 815, 188), ("5", 1203, 188),
        ("6", 1588, 188), ("7", 575, 372), ("8", 45, 885), ("9", 669, 354), ("10", 718, 925),
        ("11", 1339, 354), ("12", 1360, 918)],
    3: [("1", 70, 203), ("2", 512, 203), ("3", 58, 672), ("4", 494, 668), ("5", 956, 192),
        ("6", 956, 662)],
    4: [("1", 28, 201), ("2", 1075, 185), ("3", 36, 790), ("4", 1098, 778)],
    5: [("1", 35, 202), ("2", 676, 190), ("3", 1326, 190), ("4", 110, 712), ("5", 805, 712),
        ("6", 1510, 712)],
    6: [("1", 33, 232), ("2", 719, 232), ("3", 1337, 232), ("4", 33, 359), ("5", 33, 805),
        ("6", 699, 359), ("7", 699, 805), ("8", 1330, 352)],
    7: [("1", 30, 168), ("2", 37, 272), ("3", 361, 272), ("4", 689, 272), ("5", 37, 409),
        ("6", 35, 593), ("7", 1050, 272)],
    8: [("1", 30, 226), ("2", 432, 252), ("3", 808, 230), ("4", 1202, 226), ("5", 1590, 228),
        ("6", 28, 552), ("7", 668, 552), ("8", 1378, 552)],
}
LARGURA = 2000


def gera_imagens(pdf_dashboard):
    """Renderiza as páginas do PDF do dashboard e desenha os marcadores."""
    from PIL import Image, ImageDraw, ImageFont

    fonte = ImageFont.truetype(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                            "fonts", "DejaVuSans-Bold.ttf"), 20)
    os.makedirs(PASTA_IMG, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp:
        subprocess.run(["pdftoppm", "-r", "110", "-png", "-f", "1", "-l", "8",
                        pdf_dashboard, os.path.join(tmp, "pg")], check=True)
        pngs = sorted(f for f in os.listdir(tmp) if f.endswith(".png"))
        if len(pngs) < 8:
            sys.exit(f"ERRO: o PDF do dashboard tem {len(pngs)} páginas; o manual descreve 8.")
        for chave, (pagina, nome) in PAGINAS.items():
            im = Image.open(os.path.join(tmp, pngs[pagina - 1])).convert("RGB")
            im = im.resize((LARGURA, round(im.height * LARGURA / im.width)), Image.LANCZOS)
            d = ImageDraw.Draw(im)
            for rotulo, x, y in MARCAS[chave]:
                r = 18 if len(rotulo) == 1 else 21
                d.ellipse((x - r - 3, y - r - 3, x + r + 3, y + r + 3), fill=BASE["card"])
                d.ellipse((x - r, y - r, x + r, y + r), fill=ESTRUTURA["tinta"])
                d.text((x, y + 1), rotulo, font=fonte, fill=BASE["card"], anchor="mm")
            im = im.quantize(colors=256, method=Image.Quantize.MEDIANCUT, dither=Image.Dither.NONE)
            im.save(os.path.join(PASTA_IMG, nome), optimize=True)
            print(f"  {os.path.join(PASTA_IMG, nome)}")


# ---------------------------------------------------------------------------
# Leitura do Markdown
# ---------------------------------------------------------------------------
def blocos(bruto, base=None):
    """Converte o Markdown numa lista de blocos (tipo, conteúdo).

    Subconjunto usado: # título (só capa), ## e ### seções, parágrafo, lista
    com '-', lista numerada, citação '>', tabela e imagem. Um parágrafo ou item
    quebrado em várias linhas, sem linha em branco no meio, vira um só bloco.
    """
    base = base or os.path.dirname(MD)
    linhas = bruto.split("\n")
    saida, i = [], 0
    while i < len(linhas):
        ln = linhas[i].rstrip()
        if not ln.strip() or ln.strip() in ("---", "***"):
            i += 1
            continue
        continua = i > 0 and linhas[i - 1].strip() and saida
        m = re.match(r"!\[([^\]]*)\]\(([^)]+)\)", ln.strip())
        if continua and saida[-1][0] in ("par", "nota") and not (
                m or ln.startswith(("|", "#", ">")) or re.match(r"^\s*([-*]|\d+\.)\s+", ln)):
            saida[-1] = (saida[-1][0], saida[-1][1] + " " + ln.strip())
        elif continua and saida[-1][0] == "item" and ln.startswith(" ") and not re.match(r"^\s*[-*]\s+", ln):
            saida[-1] = ("item", saida[-1][1] + " " + ln.strip())
        elif m:
            saida.append(("img", (m.group(1), os.path.normpath(os.path.join(base, m.group(2))))))
        elif ln.startswith("|") and i + 1 < len(linhas) and re.match(r"^\|[\s:|-]+\|$", linhas[i + 1].strip()):
            tab = []
            while i < len(linhas) and linhas[i].strip().startswith("|"):
                tab.append(celulas(linhas[i]))
                i += 1
            saida.append(("tab", (tab[0], tab[2:])))
            continue
        elif ln.startswith("# "):
            saida.append(("h1", ln[2:].strip()))
        elif ln.startswith("### "):
            saida.append(("h3", ln[4:].strip()))
        elif ln.startswith("## "):
            saida.append(("h2", ln[3:].strip()))
        elif ln.startswith(">"):
            saida.append(("nota", ln.lstrip("> ").strip()))
        elif re.match(r"^\s*[-*]\s+", ln):
            saida.append(("item", re.sub(r"^\s*[-*]\s+", "", ln)))
        elif re.match(r"^\s*\d+\.\s+", ln):
            n = re.match(r"^\s*(\d+)\.\s+", ln).group(1)
            saida.append(("num", (n, re.sub(r"^\s*\d+\.\s+", "", ln))))
        else:
            saida.append(("par", ln.strip()))
        i += 1
    return saida


def larguras(cab, total):
    """Larguras de coluna em cm: a coluna do número é estreita; a explicação é a mais larga."""
    if len(cab) == 3 and cab[1] == "Pergunta":
        base = [1.7, 9.4, 0.0]
    elif len(cab) == 3 and cab[0] == "Tempo":
        base = [2.5, 6.9, 0.0]
    elif len(cab) == 6 and cab[1] == "Bloco":
        base = [0.6, 5.0, 5.6, 1.4, 1.4, 0.0]
    elif len(cab) == 3 and cab[0] == "Código":
        base = [1.7, 5.0, 0.0]
    elif len(cab) == 3:
        base = [1.0, 4.3, 0.0]
    elif len(cab) == 2:
        base = [4.2, 0.0]
    else:
        return [total / len(cab)] * len(cab)
    base[-1] = total - sum(base)
    return base


# ---------------------------------------------------------------------------
# .docx
# ---------------------------------------------------------------------------
def gerar_docx(itens, versao, cfg=None):
    cfg = cfg or MANUAL
    doc = Document()
    estilos(doc)
    for s in doc.sections:
        s.top_margin = s.bottom_margin = Cm(2.0)
        s.left_margin = s.right_margin = Cm(2.2)
    util = 21.0 - 4.4

    # capa
    for _ in range(7):
        doc.add_paragraph()
    for texto, tam, cor, negrito in [(cfg["capa"], 26, TINTA, True),
                                      ("Amazon Product Performance & Customer Insights", 15, SECUND, False),
                                      ("", 10, TINTA, False),
                                      ("Tech Challenge Fase 4 · POSTECH DTAT · Grupo 12", 11, TINTA, False),
                                      (EQUIPE, 10, SECUND, False),
                                      ("", 10, TINTA, False),
                                      (versao, 10, TINTA, False)]:
        p = doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        if texto:
            r = p.add_run(texto)
            r.font.size, r.font.color.rgb, r.bold = Pt(tam), cor, negrito
    doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)

    # sumário
    if cfg["sumario"]:
        doc.add_heading("Sumário", level=1)
    for tipo, cont in (itens if cfg["sumario"] else []):
        if tipo in ("h2", "h3"):
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0 if tipo == "h2" else 0.7)
            p.paragraph_format.space_after = Pt(1)
            r = p.add_run(cont)
            r.bold = tipo == "h2"
            r.font.size = Pt(10 if tipo == "h2" else 9.5)
            r.font.color.rgb = TINTA if tipo == "h2" else SECUND

    for tipo, cont in itens:
        if cfg["pula"](tipo, cont):
            continue
        if tipo == "h2":
            if cfg["quebra_h2"]:
                doc.add_paragraph().add_run().add_break(WD_BREAK.PAGE)
            doc.add_heading(cont, level=1)
        elif tipo == "h3":
            doc.add_heading(cont, level=2)
        elif tipo == "par":
            inline(doc.add_paragraph(), cont)
        elif tipo == "nota":
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.6)
            inline(p, cont)
            for r in p.runs:
                r.font.color.rgb = SECUND
        elif tipo == "item":
            inline(doc.add_paragraph(style="List Bullet"), cont)
        elif tipo == "num":
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Cm(0.6)
            p.paragraph_format.first_line_indent = Cm(-0.6)
            r = p.add_run(f"{cont[0]}.  ")
            r.bold, r.font.color.rgb = True, TEAL
            inline(p, cont[1])
        elif tipo == "img":
            legenda, caminho = cont
            if not os.path.exists(caminho):
                sys.exit(f"ERRO: imagem não encontrada — {caminho}. Rode com --pdf.")
            doc.add_picture(caminho, width=Cm(util))
            doc.paragraphs[-1].alignment = WD_ALIGN_PARAGRAPH.CENTER
            doc.paragraphs[-1].paragraph_format.keep_with_next = True
            p = doc.add_paragraph()
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            r = p.add_run(legenda)
            r.font.size, r.italic, r.font.color.rgb = Pt(8.5), True, SECUND
        elif tipo == "tab":
            cab, corpo = cont
            w = larguras(cab, util)
            t = doc.add_table(rows=1, cols=len(cab))
            t.style = "Table Grid"
            t.alignment = WD_TABLE_ALIGNMENT.CENTER
            t.autofit = False
            for j, c in enumerate(cab):
                cel = t.rows[0].cells[j]
                cel.width = Cm(w[j])
                cel.text = ""
                inline(cel.paragraphs[0], c)
                for r in cel.paragraphs[0].runs:
                    r.bold, r.font.size = True, Pt(9)
                sombrear(cel, DIVISOR)
            for lin in corpo:
                cells = t.add_row().cells
                for j, c in enumerate((lin + [""] * len(cab))[:len(cab)]):
                    cells[j].width = Cm(w[j])
                    cells[j].text = ""
                    inline(cells[j].paragraphs[0], c)
                    for r in cells[j].paragraphs[0].runs:
                        r.font.size = Pt(9)
            doc.add_paragraph()

    cp = doc.core_properties
    cp.author = cp.last_modified_by = AUTORIA
    cp.title, cp.subject, cp.keywords, cp.comments = cfg["titulo"], ASSUNTO, cfg["palavras"], ""
    fixar_propriedades(cp)
    doc.save(cfg["out_docx"])
    fixar_docx(cfg["out_docx"])
    print(f"  {cfg['out_docx']}")


# ---------------------------------------------------------------------------
# .pdf
# ---------------------------------------------------------------------------
def gerar_pdf(itens, versao, cfg=None):
    cfg = cfg or MANUAL
    from PIL import Image as PILImage
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.fonts import addMapping
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import cm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (Image, KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                    Spacer, Table, TableStyle)

    fdir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")
    for nome, arq in [("DejaVu", "DejaVuSans.ttf"), ("DejaVu-Bold", "DejaVuSans-Bold.ttf"),
                      ("DejaVu-Obl", "DejaVuSans-Oblique.ttf"), ("DejaVu-BoldObl", "DejaVuSans-BoldOblique.ttf"),
                      ("DejaVuMono", "DejaVuSansMono.ttf")]:
        pdfmetrics.registerFont(TTFont(nome, os.path.join(fdir, arq)))
    addMapping("DejaVu", 0, 0, "DejaVu")
    addMapping("DejaVu", 1, 0, "DejaVu-Bold")
    addMapping("DejaVu", 0, 1, "DejaVu-Obl")
    addMapping("DejaVu", 1, 1, "DejaVu-BoldObl")

    tinta, secund = colors.HexColor(ESTRUTURA["tinta"]), colors.HexColor(ESTRUTURA["secundario"])
    ss = getSampleStyleSheet()
    est = {
        "corpo": ParagraphStyle("corpo", parent=ss["Normal"], fontName="DejaVu", fontSize=9.4,
                                leading=13.6, textColor=tinta, alignment=TA_LEFT, spaceAfter=6),
        "h2": ParagraphStyle("h2", parent=ss["Heading1"], fontName="DejaVu-Bold", fontSize=16, leading=20,
                             textColor=colors.HexColor(CHAMADAS["favoravel"]), spaceBefore=4, spaceAfter=8,
                             keepWithNext=1),
        "h3": ParagraphStyle("h3", parent=ss["Heading2"], fontName="DejaVu-Bold", fontSize=11.5, leading=15,
                             textColor=tinta, spaceBefore=10, spaceAfter=5, keepWithNext=1),
        "leg": ParagraphStyle("leg", parent=ss["Normal"], fontName="DejaVu-Obl", fontSize=7.8, leading=10,
                              textColor=secund, alignment=TA_CENTER, spaceAfter=8),
        "nota": ParagraphStyle("nota", parent=ss["Normal"], fontName="DejaVu", fontSize=9.0, leading=13,
                               textColor=secund, leftIndent=12, spaceAfter=6),
        "item": ParagraphStyle("item", parent=ss["Normal"], fontName="DejaVu", fontSize=9.4, leading=13.4,
                               textColor=tinta, leftIndent=14, bulletIndent=4, spaceAfter=3),
        "th": ParagraphStyle("th", fontName="DejaVu-Bold", fontSize=8.4, leading=11, textColor=tinta),
        "td": ParagraphStyle("td", fontName="DejaVu", fontSize=8.4, leading=11.4, textColor=tinta),
        "tdn": ParagraphStyle("tdn", fontName="DejaVu-Bold", fontSize=8.8, leading=11.4,
                              textColor=colors.HexColor(CHAMADAS["favoravel"]), alignment=TA_CENTER),
        "sum1": ParagraphStyle("sum1", fontName="DejaVu-Bold", fontSize=10, leading=15, textColor=tinta),
        "sum2": ParagraphStyle("sum2", fontName="DejaVu", fontSize=9.2, leading=13, textColor=secund,
                               leftIndent=14),
        "capa_t": ParagraphStyle("capa_t", fontName="DejaVu-Bold", fontSize=24, leading=30, textColor=tinta,
                                 alignment=TA_CENTER, spaceAfter=12),
        "capa_s": ParagraphStyle("capa_s", fontName="DejaVu", fontSize=13.5, leading=18, textColor=secund,
                                 alignment=TA_CENTER, spaceAfter=30),
        "capa_c": ParagraphStyle("capa_c", fontName="DejaVu", fontSize=10, leading=16, textColor=tinta,
                                 alignment=TA_CENTER),
    }

    def rico(txt):
        txt = txt.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        txt = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", txt)
        txt = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", txt)
        txt = re.sub(r"`([^`]+)`", r'<font face="DejaVuMono" size="8.2" color="'
                     + CHAMADAS["favoravel"] + r'">\1</font>', txt)
        return txt

    util = 21.0 * cm - 2 * 2.2 * cm
    fluxo = [Spacer(1, 190),
             Paragraph(rico(cfg["capa"]), est["capa_t"]),
             Paragraph("Amazon Product Performance &amp; Customer Insights", est["capa_s"]),
             Paragraph("Tech Challenge Fase 4 · POSTECH DTAT · Grupo 12", est["capa_c"]),
             Spacer(1, 8),
             Paragraph(EQUIPE, est["capa_c"]),
             Spacer(1, 26),
             Paragraph(rico(versao), est["capa_c"]),
             PageBreak()]
    if cfg["sumario"]:
        fluxo.append(Paragraph("Sumário", est["h2"]))
    for tipo, cont in (itens if cfg["sumario"] else []):
        if tipo in ("h2", "h3"):
            fluxo.append(Paragraph(rico(cont), est["sum1" if tipo == "h2" else "sum2"]))

    for tipo, cont in itens:
        if cfg["pula"](tipo, cont):
            continue
        if tipo == "h2":
            fluxo += ([PageBreak()] if cfg["quebra_h2"] else []) + [Paragraph(rico(cont), est["h2"])]
        elif tipo == "h3":
            fluxo.append(Paragraph(rico(cont), est["h3"]))
        elif tipo == "par":
            fluxo.append(Paragraph(rico(cont), est["corpo"]))
        elif tipo == "nota":
            fluxo.append(Paragraph(rico(cont), est["nota"]))
        elif tipo == "item":
            fluxo.append(Paragraph(rico(cont), est["item"], bulletText="•"))
        elif tipo == "num":
            fluxo.append(Paragraph(rico(cont[1]), est["item"], bulletText=f"{cont[0]}."))
        elif tipo == "img":
            legenda, caminho = cont
            w, h = PILImage.open(caminho).size
            fluxo.append(KeepTogether([Image(caminho, width=util, height=util * h / w), Spacer(1, 3),
                                       Paragraph(rico(legenda), est["leg"])]))
        elif tipo == "tab":
            cab, corpo = cont
            w = [x * cm for x in larguras(cab, util / cm)]
            dados = [[Paragraph(rico(c), est["th"]) for c in cab]]
            for lin in corpo:
                lin = (lin + [""] * len(cab))[:len(cab)]
                dados.append([Paragraph(rico(c), est["tdn"] if j == 0 and len(cab) == 3 else est["td"])
                              for j, c in enumerate(lin)])
            t = Table(dados, colWidths=w, repeatRows=1)
            t.setStyle(TableStyle([
                ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor(BASE["divisor"])),
                ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor(ESTRUTURA["grade"])),
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
                ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ]))
            fluxo += [t, Spacer(1, 9)]

    def rodape(canvas, doc_):
        if doc_.page == 1:
            return
        canvas.saveState()
        canvas.setFont("DejaVu", 7.5)
        canvas.setFillColor(secund)
        canvas.drawString(2.2 * cm, 1.1 * cm, cfg["rodape"])
        canvas.drawRightString(A4[0] - 2.2 * cm, 1.1 * cm, str(doc_.page))
        canvas.restoreState()

    fixar_reportlab()
    pdf = SimpleDocTemplate(cfg["out_pdf"], pagesize=A4, topMargin=1.8 * cm, bottomMargin=1.8 * cm,
                            leftMargin=2.2 * cm, rightMargin=2.2 * cm, title=cfg["titulo"], author=AUTORIA,
                            subject=ASSUNTO, keywords=cfg["palavras"], creator=AUTORIA)
    pdf.build(fluxo, onFirstPage=rodape, onLaterPages=rodape)
    datar_pdf(cfg["out_pdf"])
    print(f"  {cfg['out_pdf']}")


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--pdf", help="PDF exportado do dashboard, para regerar as imagens anotadas")
    args = ap.parse_args()
    if args.pdf:
        gera_imagens(args.pdf)
    bruto = open(MD, encoding="utf-8").read()
    versao = next((ln.strip().strip("*") for ln in bruto.split("\n") if ln.startswith("**Versão ")), VERSAO)
    itens = blocos(bruto)
    gerar_docx(itens, versao)
    gerar_pdf(itens, versao)


if __name__ == "__main__":
    main()

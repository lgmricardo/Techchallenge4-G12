# -*- coding: utf-8 -*-
"""
Checklist de qualidade da F8 — 03_dashboard/checklist_qualidade.md e .pdf.

POR QUE EXISTE
--------------
A F8 era dividida: uma pessoa conferia as regras T1–T9 nas sete páginas, outra
os números, outra LGPD e limitações. Com uma pessoa só, a conferência precisa
de um roteiro fixo — página por página, regra por regra —, impresso e marcado
contra as imagens exportadas na F8. O que fica sem marca impede o Portão C.

O QUE É GERADO, E POR QUÊ
-------------------------
A matriz página × regra é especificação (o que cada regra exige em cada tela)
e mora aqui, como dado. Os NÚMEROS que cada tela tem de mostrar não: são
calculados da gold e das tabelas de resultado a cada execução. E o script
confere cada um contra a seção 6 do guia de montagem, que é o que o montador
segue — se o guia e o dado discordarem, ele falha antes de imprimir.

Uso: python 03_dashboard/gera_checklist.py
"""

import os
import sys

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA = os.path.join(RAIZ, "03_dashboard")
GOLD = os.path.join(RAIZ, "00_data", "gold")
TAB = os.path.join(RAIZ, "02_results", "tables")
GUIA = os.path.join(PASTA, "INSTRUCOES_MONTAGEM_POWERBI.md")
SAIDA_MD = os.path.join(PASTA, "checklist_qualidade.md")
SAIDA_PDF = os.path.join(PASTA, "checklist_qualidade.pdf")
sys.path.insert(0, os.path.join(RAIZ, "src"))
from paleta import BASE, ESTRUTURA  # noqa: E402
from determinismo import datar_pdf, fixar_reportlab  # noqa: E402


def br(x, casas=0):
    """Número no formato do material: milhar com ponto, decimal com vírgula."""
    s = f"{x:,.{casas}f}"
    # sinal de menos tipográfico (U+2212), como em todo o material — não o hífen
    return s.replace(",", "§").replace(".", ",").replace("§", ".").replace("-", "\u2212")


def pct(x, casas=1):
    return br(100 * x, casas) + "%"


# ------------------------------------------------------- os números, medidos
g = pd.read_csv(os.path.join(GOLD, "base_analitica.csv"))
ref = pd.read_csv(os.path.join(PASTA, "valores_referencia.csv"))
pub = {r.medida + ("·" + r.nome.split(" · ")[-1] if r.medida == "M15" else ""): r.publicado
       for r in ref.itertuples()}
t03 = pd.read_csv(os.path.join(TAB, "tab03_correlacoes.csv")).set_index("par")
t05 = pd.read_csv(os.path.join(TAB, "tab05_arquetipos.csv")).set_index("arquetipo")
t06 = pd.read_csv(os.path.join(TAB, "tab06_corpus.csv")).set_index("faixa_nota")
t07 = pd.read_csv(os.path.join(TAB, "tab07_ml2_blocos.csv")).set_index("bloco_preditores")
t08 = pd.read_csv(os.path.join(TAB, "tab08_faixas_desconto.csv")).set_index("faixa_desconto")

N = len(g)
alto, baixo = g.engajamento == "alto", g.engajamento == "baixo"
alta, baixa = g.satisfacao == "alta", g.satisfacao == "baixa"
quadrantes = {"Âncora": (alto & alta).sum(), "Risco": (alto & baixa).sum(),
              "Subexplorado": g.q6_subexplorado.sum(), "Cauda frágil": (baixo & baixa).sum()}
intermediario = N - sum(quadrantes.values())
pareto_baixa = (g.pareto_80 & (g.nota < 4.0)).sum()
tres_familias = g.categoria_n1.value_counts().nlargest(3).sum() / N
# L8: variantes compartilham o par (avaliacoes, nota); colapsar mantém uma por grupo
colapsada = g.drop_duplicates(["avaliacoes", "nota"])
eletronicos_sem_variantes = (colapsada.loc[colapsada.categoria_n1 == "Electronics", "avaliacoes"].sum()
                             / colapsada.avaliacoes.sum())
refs_total = int(t06.referencias.sum())
rho_q3, p_q3 = t03.loc["Desconto × nota", "rho"], t03.loc["Desconto × nota", "p_valor"]
P_Q3 = f"{float(p_q3):.1e}".replace(".", ",")   # dois algarismos, como no material: 3,1e-08
rho_qa4, p_qa4 = t03.loc["Preço de tabela × nota", "rho"], t03.loc["Preço de tabela × nota", "p_valor"]
auc = t07.auc.tolist()
dp_auc = br(float(t07.desvio_entre_particoes.iloc[-1]), 2)   # do modelo completo; antes era '± 0,03' escrito à mão
# O destaque da página 3 é o achado defensável de QA1 (§5.10): a única faixa abaixo de 4,0.
# A primeira faixa tem a maior nota corrigida, mas a diferença para a segunda é 0,053 —
# magnitude sem leitura de negócio, e T5 manda dizer isso em vez de destacá-la.
faixa_pior = t08.loc[t08.nota_corrigida_wilson.idxmin()]

NUMEROS = {
    "1": [pub["M06"], f"{pub['M05']}%", pub["M04"], pub["M08"], pub["M18"],
          f"histograma {br(baixa.sum())} / {br(alta.sum())}", pub["M13"], pub["M14"],
          f"{pareto_baixa} dos {pub['M13']}",
          " · ".join(f"{k} {v}" for k, v in quadrantes.items()) + f" · Intermediário {intermediario}"],
    "2a": [f"{pub['M15·Electronics']} · {pub['M15·Computers&Accessories']} · {pub['M15·Home&Kitchen']} · "
           f"{pub['M15·OfficeProducts']}", f"Electronics sem variantes {pct(eletronicos_sem_variantes)}",
           f"{pub['M16']} subcategorias · {pct(float(ref.loc[ref.medida == 'M17', 'valor'].iloc[0]) / 100)}"],
    "2b": [f"{pub['M11']} (Q5)", f"{pub['M12']} funil · {pub['M22']} acionáveis",
           f"cortes {pub['M18']} · {pub['M19']} · 4,0 · 4,3"],
    "2c": [" · ".join(f"{a} {int(t05.loc[a, 'n'])}" for a in "ABCD"),
           f"B × D: desconto {int(t05.loc['B', 'desconto_mediano'])}% × {int(t05.loc['D', 'desconto_mediano'])}%",
           f"avaliações {br(t05.loc['B', 'avaliacoes_medianas'])} × {br(t05.loc['D', 'avaliacoes_medianas'])}",
           f"nota {br(t05.loc['B', 'nota_mediana'], 1)} × {br(t05.loc['D', 'nota_mediana'], 1)}"],
    "3": [pub["M03"], pub["M04"], f"{pub['M05']}%",
          f"{faixa_pior.name}: {br(faixa_pior.nota_corrigida_wilson, 3)} (n = {int(faixa_pior.n)})",
          f"ρ Q3 = {br(rho_q3, 3)} (p = {P_Q3})",
          f"ρ QA4 = +{br(rho_qa4, 3)} (p = {br(float(p_qa4), 3)})"],
    "4": [f"{br(N)} blocos · {br(refs_total)} referências · {pub['M20']} reviews",
          " / ".join(br(v) for v in t06.blocos), f"até 8 por produto (média {br(refs_total / N, 2)})",
          f"{pub['M11']} blocos de Q5"],
    "5": [f"{pub['M11']} · 335 · {pub['M22']} · ρ = {br(rho_q3, 3)} (p = {P_Q3}) · {pct(tres_familias)}",
          "AUC " + " · ".join(br(a, 2) for a in auc[:-1]) + f" · {br(auc[-1], 2)} ± {dp_auc}",
          "8 limitações · 21 de 21 medidas (33 linhas conferidas)",
          "caixa 'como estes números foram conferidos' (G-36)"],
    "Conferência": ["Conf · Divergentes = 0", "33 de 33 linhas"],
}

# Cada número abaixo também está escrito na seção 6 do guia. Se o dado mudar e
# o guia não, ou o contrário, o checklist não é impresso.
guia = open(GUIA, encoding="utf-8").read()
secao6 = guia[guia.index("## 6 "):guia.index("## 7 ")]
NO_GUIA = [pub["M06"], pub["M04"], pub["M08"], pub["M18"], f"**{pub['M13']}**", f"**{pub['M14']}**",
           f"**{pareto_baixa} dos {pub['M13']}**", f"Âncora {quadrantes['Âncora']}",
           f"Cauda frágil {quadrantes['Cauda frágil']}", f"({intermediario})",
           "59,7 · 26,6 · 12,6 · 0,6%", f"**{pct(eletronicos_sem_variantes)}**",
           f"**{pub['M12']}**", f"**{pub['M22']}**",
           " · ".join(f"{a} {int(t05.loc[a, 'n'])}" for a in "ABCD"),
           f"**{br(faixa_pior.nota_corrigida_wilson, 3)}**; n = {int(faixa_pior.n)}",
           f"ρ = +{br(rho_qa4, 3)}, p = {br(float(p_qa4), 3)}",
           f"média {br(refs_total / N, 2)}", f"{br(N)} blocos · {br(refs_total)} referências · {pub['M20']} reviews",
           " · ".join(br(v) for v in t06.blocos), f"ρ = {br(rho_q3, 3)}", pct(tres_familias),
           " · ".join(br(a, 2) for a in auc[:-1]) + f" · **{br(auc[-1], 2)} ± {dp_auc}**"]
divergentes = [n for n in NO_GUIA if n not in secao6]
# o p-valor de Q3 está nos Números de conferência do guia, fora da seção 6
if f"{br(rho_q3, 3)} ({P_Q3})" not in guia:
    divergentes.append(f"desconto×nota {br(rho_q3, 3)} ({P_Q3})")
assert not divergentes, f"o guia (seção 6) não traz estes números medidos: {divergentes}"

# --------------------------------------------- a matriz: página × regra
REGRAS = ["T1 Wilson + n", "T2 piso 30", "T3 rodapé", "T4 sem causa", "T5 ρ com p",
          "T6 volume ≠ venda", "T7 consumidor", "T8 corpus", "T9 paleta"]
TODAS = "rodapé M21 · L5 sem símbolo"
PAGINAS = [
    ("1 · Visão Executiva", ["—", "—", TODAS, "títulos sem causa", "—", "cartão 36.384 = volume",
                             "nenhum user_*", "—", "âmbar só no ponto de 80%"]),
    ("2a · Categorias", ["nota corrigida (T2)", "só 4 categorias · rodapé 5 cat./7 prod./0,5%", TODAS,
                         "títulos sem causa", "—", "participação no volume", "nenhum user_*", "—",
                         "sem âmbar · fones e climatização em laranja"]),
    ("2b · Quadrantes", ["19 e 61 com Wilson e n", "listas nominais = exceção declarada", TODAS,
                         "títulos sem causa", "—", "vedado \"baixa visibilidade\"",
                         "tabelas sem consumidor", "—", "âmbar só no quadrante Q5"]),
    ("2c · Rankings", ["top 10 Wilson ao lado do bruto", "arquétipos n ≥ 268", TODAS,
                       "\"convenção descritiva, não descoberta\"", "—", "nenhuma venda", "nenhum user_*",
                       "—", "B × D em 2 séries"]),
    ("3 · Preços", ["QA1 por nota corrigida, n no rótulo", "5 faixas, todas n ≥ 30", TODAS,
                    "\"associação, não causa\"", "ρ com p e n nos 4 pares", "nenhuma venda",
                    "nenhum user_*", "—", "âmbar só em 81–100% · escala divergente"]),
    ("4 · Customer Insights", ["—", "QA5: denominador 19 visível", TODAS, "títulos sem causa",
                               "Δ TF-IDF como magnitude", "nenhuma venda",
                               "nenhum trecho de avaliação, nenhum user_*",
                               "caixa: até 8 por produto · bloco · dedup review_id", "faixa média em cinza"]),
    ("5 · Recomendações", ["—", "—", TODAS, "\"triagem, não veredito\"", "AUC com o desvio ao lado",
                           "nada em receita", "nenhum user_*", "—", "1 âmbar"]),
    ("Oculta · detalhamento", ["Wilson e n na ficha", "—", TODAS, "—", "—", "—",
                               "nenhum dado de consumidor", "—", "—"]),
    ("Oculta · dica", ["n e nota corrigida", "—", "—", "—", "—", "—", "—", "—", "—"]),
    ("Oculta · Conferência", ["—", "—", "rodapé da referência", "—", "—", "—", "—", "—",
                              "0 em favoravel, ≠ 0 em atencao"]),
]
CHAVE_NUMEROS = {"1 · Visão Executiva": "1", "2a · Categorias": "2a", "2b · Quadrantes": "2b",
                 "2c · Rankings": "2c", "3 · Preços": "3", "4 · Customer Insights": "4",
                 "5 · Recomendações": "5", "Oculta · Conferência": "Conferência"}
GERAIS = [
    "um único elemento em âmbar por página (T9)", "nenhuma pizza ou rosca", "no máximo 5 séries por visual",
    "nenhum visual de Python, de R ou de loja", "valores em rupia indiana, sem símbolo (L5)",
    "L1 dita na página 4; L4 e as 8 limitações na página 5",
    "`verifica_pbix.py` com saída 0 sobre o .pbit exportado do .pbix final",
    "página Conferência: Conf · Divergentes = 0",
]

# ------------------------------------------------------------ markdown
md = ["# Checklist de qualidade — F8", "",
      "> **Gerado por `gera_checklist.py`. Não editar à mão.** Os números são medidos na gold e nas tabelas "
      "de resultado a cada execução, e conferidos contra a seção 6 do guia de montagem.", "",
      "Marcar contra as **imagens exportadas na F8** (`03_dashboard/screenshots/`), uma página por vez. `—` = a regra não se aplica à página. "
      "**Qualquer célula sem marca impede o Portão C.** A versão para imprimir é `checklist_qualidade.pdf`.", "",
      "| Página | " + " | ".join(REGRAS) + " |", "|---" * (len(REGRAS) + 1) + "|"]
for pagina, celulas in PAGINAS:
    md.append(f"| **{pagina}** | " + " | ".join(("☐ " + c) if c != "—" else "—" for c in celulas) + " |")
md += ["", "## Os números que cada tela tem de mostrar", "", "| Página | Números |", "|---|---|"]
for pagina, _ in PAGINAS:
    if pagina in CHAVE_NUMEROS:
        md.append(f"| **{pagina}** | " + " · ".join(f"☐ {n}" for n in NUMEROS[CHAVE_NUMEROS[pagina]]) + " |")
md += ["", "## Em todas as páginas", ""] + [f"- ☐ {g_}" for g_ in GERAIS] + [""]
open(SAIDA_MD, "w", encoding="utf-8").write("\n".join(md))

# ----------------------------------------------------------------- PDF
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.pagesizes import A4, landscape  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle  # noqa: E402

fixar_reportlab()

FONTES = os.path.join(RAIZ, "src", "fonts")
pdfmetrics.registerFont(TTFont("DejaVu", os.path.join(FONTES, "DejaVuSans.ttf")))
pdfmetrics.registerFont(TTFont("DejaVu-Bold", os.path.join(FONTES, "DejaVuSans-Bold.ttf")))
from reportlab.lib.fonts import addMapping  # noqa: E402
addMapping("DejaVu", 0, 0, "DejaVu")
addMapping("DejaVu", 1, 0, "DejaVu-Bold")
tinta, sec = colors.HexColor(ESTRUTURA["tinta"]), colors.HexColor(ESTRUTURA["secundario"])
cel = ParagraphStyle("cel", fontName="DejaVu", fontSize=7.4, leading=8.9, textColor=tinta)
cab = ParagraphStyle("cab", parent=cel, fontName="DejaVu-Bold", fontSize=7.4, textColor=colors.white)
tit = ParagraphStyle("tit", fontName="DejaVu-Bold", fontSize=13, leading=16, textColor=tinta)
sub = ParagraphStyle("sub", fontName="DejaVu", fontSize=8.2, leading=10.4, textColor=sec)


def p(texto, estilo=cel):
    return Paragraph(texto.replace("&", "&amp;").replace("<", "&lt;").replace("`", ""), estilo)


dados = [[p("Página", cab)] + [p(r, cab) for r in REGRAS] + [p("Números na tela", cab)]]
for pagina, celulas in PAGINAS:
    nums = NUMEROS.get(CHAVE_NUMEROS.get(pagina, ""), [])
    dados.append([p(pagina, ParagraphStyle("pg", parent=cel, fontName="DejaVu-Bold"))]
                 + [p(("☐ " + c) if c != "—" else "—") for c in celulas]
                 + [p(" · ".join(f"☐ {n}" for n in nums) if nums else "—")])
larguras = [2.65 * cm] + [2.05 * cm] * len(REGRAS) + [6.55 * cm]   # soma 27,65 cm = a área útil
tabela = Table(dados, colWidths=larguras, repeatRows=1)
tabela.setStyle(TableStyle([
    ("BACKGROUND", (0, 0), (-1, 0), tinta),
    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor(BASE["divisor"])]),
    ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor(ESTRUTURA["grade"])),
    ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ("TOPPADDING", (0, 0), (-1, -1), 2.2), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.2),
    ("LEFTPADDING", (0, 0), (-1, -1), 2.6), ("RIGHTPADDING", (0, 0), (-1, -1), 2.6),
]))
gerais = Paragraph("<b>Em todas as páginas:</b> " + " · ".join(f"☐ {x}" for x in GERAIS).replace("`", ""), sub)
doc = SimpleDocTemplate(SAIDA_PDF, pagesize=landscape(A4), leftMargin=1 * cm, rightMargin=1 * cm,
                        topMargin=0.9 * cm, bottomMargin=0.8 * cm,
                        title="Checklist de qualidade — F8", author="Grupo 12 — POSTECH DTAT")
doc.build([p("Checklist de qualidade — F8 · conferir contra as imagens exportadas de cada página", tit),
           p("Uma linha por página, uma coluna por regra. — = não se aplica. Qualquer célula sem marca "
             "impede o Portão C. Números medidos na gold e nas tabelas de resultado, e conferidos contra a "
             "seção 6 do guia. Gerado por 03_dashboard/gera_checklist.py.", sub),
           Spacer(1, 5), tabela, Spacer(1, 5), gerais])

from pypdf import PdfReader  # noqa: E402
datar_pdf(SAIDA_PDF)
paginas_pdf = len(PdfReader(SAIDA_PDF).pages)
assert paginas_pdf == 1, f"o checklist precisa caber em uma página; saiu com {paginas_pdf}"
print(f"  {SAIDA_MD}")
print(f"  {SAIDA_PDF} · 1 página")
print(f"  {len(PAGINAS)} páginas × {len(REGRAS)} regras · {sum(len(v) for v in NUMEROS.values())} números · "
      f"{len(NO_GUIA)} conferidos contra o guia")

# -*- coding: utf-8 -*-
"""
Gera as figuras e tabelas do relatório técnico, a partir da base canônica.

Toda figura sai da paleta v06 (regra T9) e declara base e *n* no rodapé (T3).
Saídas: 02_results/images/figNN_*.png · 02_results/tables/tabNN_*.csv

Uso:  python3 src/gera_figuras.py [caminho/para/amazon.csv]
"""

import os
import sys

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from scipy.stats import spearmanr
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from paleta import (aplicar, confere_visual, rodape, SO_NUMERO, BASE, CATEGORICA, CHAMADAS, ESTRUTURA)
import ml2

# O caractere abaixo é o marcador de moeda NA ORIGEM — aquilo que o tratamento
# REMOVE. Ele é escrito como escape unicode de propósito: a premissa do projeto
# é que o símbolo de rupia não apareça em nenhum rótulo, visual, tabela ou texto
# publicado (escreve-se "rupia" por extenso). Aqui ele existe só como alvo de
# remoção, e o escape garante que o glifo não esteja nem no código-fonte.
MARCADOR_MOEDA_ORIGEM = "\u20b9"  # rupia indiana, U+20B9

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
IMG = os.path.join(RAIZ, "02_results", "images")
TAB = os.path.join(RAIZ, "02_results", "tables")
os.makedirs(IMG, exist_ok=True)
os.makedirs(TAB, exist_ok=True)
aplicar(fundo="card")   # documento impresso: fundo branco

AMBAR, TEAL, ARDOSIA = CATEGORICA[0], CHAMADAS["favoravel"], ESTRUTURA["secundario"]
LARANJA, AZUL, CLARA = CHAMADAS["atencao"], CATEGORICA[1], CATEGORICA[2]
TINTA = ESTRUTURA["tinta"]


def _virgula(valor, _pos=None):
    """Rótulo numérico em português: vírgula decimal e ponto de milhar."""
    inteiro = float(valor).is_integer()
    texto = f"{valor:,.0f}" if inteiro else f"{valor:,.3f}".rstrip("0").rstrip(".")
    return texto.replace(",", "\u0000").replace(".", ",").replace("\u0000", ".")


def salva(fig, nome):
    # Vírgula decimal em todo eixo NUMÉRICO — sem isso a mesma figura trazia "22.7%" no
    # rótulo e "22,7%" no texto do relatório ao lado, e a leitora fica sem saber qual é
    # o número.
    #
    # A regra abaixo é deliberadamente burra, e é por isso que funciona. Deduzir quais
    # eixos são numéricos pelo TIPO do eixo custou três figuras ilegíveis: eixo de
    # categoria que o matplotlib trata como linear (e formatá-lo troca "Electronics" por
    # "8"), rótulo escrito à mão com `set_xticklabels`, e eixo compartilhado por
    # `twinx()`, em que formatar o gêmeo apaga o rótulo do original. Em vez de prever o
    # mecanismo, aqui se DESENHA primeiro e se lê o que o eixo mostra: se já é número,
    # formata; se tem letra, %, ou qualquer outra coisa, não se toca nele.
    fig.canvas.draw()
    for eixo in fig.axes:
        for escala in (eixo.xaxis, eixo.yaxis):
            if escala.get_scale() != "linear":
                continue                               # log já tem formatador próprio
            rotulos = [t.get_text() for t in escala.get_ticklabels() if t.get_text()]
            if rotulos and all(SO_NUMERO.match(r) for r in rotulos):
                escala.set_major_formatter(FuncFormatter(_virgula))

    confere_visual(fig, nome)
    fig.savefig(os.path.join(IMG, nome), dpi=150, bbox_inches="tight",
                pad_inches=0.28, facecolor=BASE["card"])
    plt.close(fig)
    print(f"  {nome}")


def wilson(nota, n, z=1.96):
    """T1 — limite inferior de Wilson, com a nota normalizada de 1–5 para 0–1."""
    p = (nota - 1) / 4.0
    d = 1 + z ** 2 / n
    centro = p + z ** 2 / (2 * n)
    margem = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2))
    return ((centro - margem) / d) * 4 + 1


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------
caminho = sys.argv[1] if len(sys.argv) > 1 else os.path.join(RAIZ, "00_data", "bronze", "amazon.csv")
df = pd.read_csv(caminho, dtype=str)


def num(serie, remover):
    saida = serie.astype(str)
    for ch in remover:
        saida = saida.str.replace(ch, "", regex=False)
    return pd.to_numeric(saida, errors="coerce")


df["preco_desc"] = num(df.discounted_price, [MARCADOR_MOEDA_ORIGEM, ","])
df["preco_tab"] = num(df.actual_price, [MARCADOR_MOEDA_ORIGEM, ","])
df["desconto"] = num(df.discount_percentage, ["%"])
df["avaliacoes"] = num(df.rating_count, [","])
df["nota"] = pd.to_numeric(df.rating, errors="coerce")
df["_ordem"] = np.arange(len(df))

# Mesma regra de prepara_dados.py: o glifo de moeda aparece dentro do nome de um
# produto (o teclado com a tecla da rupia) e as tabelas daqui são versionadas.
df["product_name"] = df.product_name.str.replace(MARCADOR_MOEDA_ORIGEM, "rupia", regex=False)

prod = (df.sort_values(["avaliacoes", "_ordem"], ascending=[False, True], na_position="last")
          .drop_duplicates("product_id", keep="first"))
an = prod[prod.nota.notna() & prod.avaliacoes.notna()].copy()
an["cat1"] = an.category.str.split("|").str[0]
an["cat2"] = an.category.str.split("|").str[:2].str.join(" | ")
an["wilson"] = wilson(an.nota, an.avaliacoes)

P90 = an.avaliacoes.quantile(0.90)
MED = an.avaliacoes.median()
N = len(an)

# Multiplicidade. O relatório testa SEIS correlações de Spearman (as quatro do eixo do enunciado,
# tab03, mais as duas de apoio, tab24). Com seis testes ao nível de 5%, a chance de ao menos um
# falso positivo é de ~26%. Corrige-se por Bonferroni — conservador, mas simples de auditar:
# o alfa de cada teste passa a ser 0,05 / 6. A correção está na coluna `leitura`, não escondida.
N_TESTES_CORR = 6
ALFA_CORR = 0.05 / N_TESTES_CORR

# ---------------------------------------------------------------------------
# A TRAVA QUE FALTAVA: ESTA RECONSTRUÇÃO × A CAMADA GOLD
#
# POR QUE EXISTE. Este script lê o BRONZE e refaz a base analítica por conta
# própria — deduplicação, cortes e Wilson — em vez de importar a gold. A
# independência é deliberada: duas implementações que chegam ao mesmo número
# são prova melhor que uma só. Mas independência sem conferência é outra
# coisa: é duas verdades esperando divergir.
#
# A regra de Wilson existe em dois arquivos, a de deduplicação em três e os
# cortes em seis. Enquanto nada comparasse os dois lados, uma alteração em
# `prepara_dados.py` que não fosse replicada aqui produziria figuras e listas
# nominais silenciosamente diferentes da camada que o dashboard consome — e
# ninguém saberia, porque cada lado é internamente coerente.
#
# É o mesmo papel que a `qa_compara_gold` cumpre do lado do Power BI, aplicado
# onde faltava: dentro do próprio Python.
_gold = pd.read_csv(os.path.join(RAIZ, "00_data", "gold", "base_analitica.csv"))
_meu = an.set_index("product_id").reindex(_gold.product_id)
_divergencias = []
if len(an) != len(_gold):
    _divergencias.append(f"n: {len(an)} aqui × {len(_gold)} na gold")
else:
    for _aqui, _la in [("nota", "nota"), ("avaliacoes", "avaliacoes"), ("preco_tab", "preco_tab"),
                       ("preco_desc", "preco_desc"), ("desconto", "desconto"), ("wilson", "nota_corrigida")]:
        _d = int((~np.isclose(_meu[_aqui].values.astype(float), _gold[_la].values.astype(float),
                              rtol=0, atol=1e-9)).sum())
        if _d:
            _divergencias.append(f"{_la}: {_d} produto(s)")
    _d = int((_meu["product_name"].values != _gold["product_name"].values).sum())
    if _d:
        _divergencias.append(f"product_name: {_d} produto(s)")
assert not _divergencias, (
    "a base reconstruída aqui diverge da camada gold — uma das duas implementações mudou "
    "sem a outra: " + " · ".join(_divergencias) + ". Rodar src/prepara_dados.py e comparar as regras "
    "de deduplicação, de corte e de Wilson nos dois arquivos.")
print(f"  base reconstruída confere com a gold em {len(_gold)} produtos e 7 colunas")

FONTE = (f"Fonte: Kaggle · karkavelrajaj/amazon-sales-dataset · base analítica n = {N:,}".replace(",", ".")
         + " · valores monetários em rupia indiana, sem conversão (L5)")

print(f"base analítica n = {N}\nfiguras:")

# ---------------------------------------------------------------------------
# A ORDEM DOS BLOCOS ABAIXO NÃO É A DOS NÚMEROS, E ISSO É DELIBERADO.
# O número da figura segue a ordem em que ela aparece no relatório; o bloco
# segue a ordem em que o dado fica disponível (o recorte de ML4, por exemplo,
# produz a silhueta — fig13 — antes dos arquétipos — fig10). Cada comentário
# declara o número que o bloco grava; conferir sempre pelo nome do arquivo.
# fig01 — reconciliação das cinco bases
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8, 3.4))
etapas = ["Bruta\n1.465", "Produtos\n1.351", "Nota válida\n1.350", "Engaj. válido\n1.349", "Analítica\n1.348"]
vals = [1465, 1351, 1350, 1349, 1348]
cores = [CLARA, CLARA, CLARA, CLARA, TEAL]
b = ax.bar(etapas, vals, color=cores, width=0.62)
# "Nota válida" e "Engajamento válido" são filtros PARALELOS sobre os 1.351 produtos (tab01: "só rating"
# e "só rating_count"), e a Analítica aplica os dois. Rotular os degraus como cadeia (-1, -1, -1) fazia
# parecer que o segundo filtro partia dos 1.350, e não dos 1.351. Cada perda é medida a partir de Produtos.
assert [vals[1] - v for v in vals[2:]] == [1, 2, 3], "os filtros paralelos deixaram de somar 1 + 2 = 3"
perdas = [None, "−114\nrepetições", "−1\nnota inválida", "−2\nsem volume", "−3\nos dois filtros"]
for r, v, perda in zip(b, vals, perdas):
    ax.text(r.get_x() + r.get_width() / 2, v + 12, f"{v:,}".replace(",", "."),
            ha="center", fontsize=9, color=TINTA, fontweight="bold")
    if perda:
        # tinta sobre o cinza, branco sobre o teal: o laranja não tinha contraste com nenhum dos dois
        ax.text(r.get_x() + r.get_width() / 2, 1257, perda, ha="center", va="bottom", fontsize=7.5,
                color="white" if v == vals[-1] else TINTA, fontweight="bold", linespacing=1.15)
ax.set_ylim(1250, 1500)
ax.text(0.995, 0.96, "eixo começa em 1.250 · as três últimas perdas são medidas a partir de Produtos (1.351)",
        transform=ax.transAxes, ha="right", va="top", fontsize=7.5, color=ESTRUTURA["secundario"])
ax.set_title("As cinco bases oficiais e a reconciliação entre elas")
ax.set_ylabel("produtos")
ax.grid(axis="x", visible=False)
rodape(fig, FONTE + " · deduplicação determinística (maior rating_count; empate → menor índice)")
salva(fig, "fig01_reconciliacao_bases.png")

# ---------------------------------------------------------------------------
# fig02 — distribuição de preço (log) e desconto
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(1, 3, figsize=(12, 3.3))
ax[0].hist(np.log10(an.preco_tab), bins=32, color=AZUL, edgecolor=BASE["card"], linewidth=0.4)
ax[0].axvline(np.log10(an.preco_tab.median()), color=LARANJA, lw=1.8, ls="--")
ax[0].set_title("Preço de tabela (log₁₀)")
ax[0].set_xlabel(f"mediana {an.preco_tab.median():,.0f}".replace(",", "."))

ax[1].hist(np.log10(an.preco_desc), bins=32, color=TEAL, edgecolor=BASE["card"], linewidth=0.4)
ax[1].axvline(np.log10(an.preco_desc.median()), color=LARANJA, lw=1.8, ls="--")
ax[1].set_title("Preço com desconto (log₁₀)")
ax[1].set_xlabel(f"mediana {an.preco_desc.median():,.0f}".replace(",", "."))

ax[2].hist(an.desconto, bins=32, color=AMBAR, edgecolor=BASE["card"], linewidth=0.4)
ax[2].axvline(an.desconto.median(), color=LARANJA, lw=1.8, ls="--")
ax[2].set_title("Desconto (%)")
ax[2].set_xlabel(f"mediana {an.desconto.median():.0f}%")
for a in ax:
    a.set_ylabel("produtos")
rodape(fig, FONTE + " · linha tracejada = mediana")
salva(fig, "fig02_distribuicao_precos.png")

# ---------------------------------------------------------------------------
# fig03 — nota e engajamento
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(1, 2, figsize=(10, 3.3))
ax[0].hist(an.nota, bins=28, color=TEAL, edgecolor=BASE["card"], linewidth=0.4)
ax[0].axvline(4.0, color=LARANJA, lw=1.8)
ax[0].axvline(4.3, color=AMBAR, lw=1.8)
ax[0].set_title("Nota")
ax[0].set_xlabel("corte de satisfação baixa (4,0) e alta (4,3)")
ax[0].set_ylabel("produtos")

ax[1].hist(np.log10(an.avaliacoes), bins=32, color=AZUL, edgecolor=BASE["card"], linewidth=0.4)
ax[1].axvline(np.log10(MED), color=ARDOSIA, lw=1.8, ls="--")
ax[1].axvline(np.log10(P90), color=LARANJA, lw=1.8)
ax[1].set_title("Volume de avaliações (log₁₀)")
ax[1].set_xlabel(f"mediana {MED:,.0f} · p90 {P90:,.0f}".replace(",", "."))
ax[1].set_ylabel("produtos")
rodape(fig, FONTE + " · rating_count é volume de avaliações, nunca vendas (T6)")
salva(fig, "fig03_nota_engajamento.png")

# ---------------------------------------------------------------------------
# fig05 — portfólio por categoria com o piso n>=30
# ---------------------------------------------------------------------------
vc = an.cat1.value_counts()
fig, ax = plt.subplots(figsize=(8, 3.6))
cores = [TEAL if v >= 30 else LARANJA for v in vc.values][::-1]
ax.barh(list(vc.index)[::-1], list(vc.values)[::-1], color=cores)
ax.axvline(30, color=ARDOSIA, ls="--", lw=1.4)
ax.text(33, 0.2, "piso amostral n = 30 (T2)", fontsize=8, color=ARDOSIA)
for i, v in enumerate(list(vc.values)[::-1]):
    ax.text(v + 8, i, str(v), va="center", fontsize=9, color=TINTA)
ax.set_title("Portfólio por categoria de nível 1 — 4 acima do piso, 5 abaixo")
ax.set_xlabel("produtos")
ax.grid(axis="y", visible=False)
rodape(fig, FONTE + " · as 5 categorias abaixo do piso somam 7 produtos e nunca são ranqueadas")
salva(fig, "fig05_portfolio_categoria.png")

# ---------------------------------------------------------------------------
# fig08 — Pareto
# ---------------------------------------------------------------------------
ordenado = an.avaliacoes.sort_values(ascending=False).values
acum = np.cumsum(ordenado) / ordenado.sum() * 100
corte = int((acum < 80).sum() + 1)
fig, ax = plt.subplots(figsize=(8, 3.4))
ax.plot(np.arange(1, N + 1), acum, color=TEAL, lw=2)
ax.axhline(80, color=ARDOSIA, ls="--", lw=1.2)
ax.axvline(corte, color=LARANJA, lw=1.8)
ax.fill_between(np.arange(1, corte + 1), 0, acum[:corte], color=TEAL, alpha=0.13)
ax.annotate(f"{corte} produtos = {100*corte/N:.1f}".replace(".", ",") + "% da base\nconcentram 80% das avaliações",
            xy=(corte, 80), xytext=(corte + 190, 52), fontsize=9, color=TINTA,
            arrowprops=dict(arrowstyle="->", color=LARANJA, lw=1.4))
ax.set_title("Concentração do engajamento — curva de Pareto (QA2)")
ax.set_xlabel("produtos, ordenados por volume de avaliações")
ax.set_ylabel("% acumulado das avaliações")
ax.set_xlim(0, N)
ax.set_ylim(0, 101)
rodape(fig, FONTE)
salva(fig, "fig08_pareto_engajamento.png")

# ---------------------------------------------------------------------------
# fig04 — desconto x nota (Q3) e preço x nota (QA4)
# ---------------------------------------------------------------------------
r1, p1 = spearmanr(an.desconto, an.nota)
r2, p2 = spearmanr(an.preco_tab, an.nota)
fig, ax = plt.subplots(1, 2, figsize=(11, 3.6))
ax[0].scatter(an.desconto, an.nota, s=9, color=AZUL, alpha=0.32, edgecolors="none")
z = np.polyfit(an.desconto, an.nota, 1)
xs = np.linspace(an.desconto.min(), an.desconto.max(), 50)
ax[0].plot(xs, np.polyval(z, xs), color=LARANJA, lw=2)
# Título curto no eixo e os números numa ANOTAÇÃO dentro do painel. Com ρ, p e n no
# título, os dois textos se encontravam no meio da figura e o "n = 1.348" sumia por
# baixo do título do painel da direita. A anotação também resolve a leitura: o número
# fica ao lado dos pontos a que se refere, não numa linha acima dos dois gráficos.
def _anota(eixo, texto):
    eixo.text(0.03, 0.06, texto, transform=eixo.transAxes, fontsize=8.6, color=TINTA,
              bbox=dict(boxstyle="round,pad=0.35", facecolor=BASE["card"],
                        edgecolor=ESTRUTURA["secundario"], lw=0.6, alpha=0.9))


ax[0].set_title("Q3 · Desconto × nota", loc="left")
ax[0].set_xlabel("desconto (%)")
ax[0].set_ylabel("nota")
_anota(ax[0], f"ρ = {r1:+.3f} · p = {p1:.1e} · n = {N:,}".replace(",", "X").replace(".", ",").replace("X", "."))

ax[1].scatter(np.log10(an.preco_tab), an.nota, s=9, color=TEAL, alpha=0.32, edgecolors="none")
ax[1].set_title("QA4 · Preço de tabela × nota", loc="left")
ax[1].set_xlabel("preço de tabela (log₁₀)")
ax[1].set_ylabel("nota")
_anota(ax[1], f"ρ = {r2:+.3f} · p = {p2:.3f} · n = {N:,}".replace(",", "X").replace(".", ",").replace("X", ".") + " — sem associação")
rodape(fig, FONTE + " · associação, nunca causa (T4) · magnitude ao lado da significância (T5)")
salva(fig, "fig04_correlacoes.png")

# ---------------------------------------------------------------------------
# fig06 — quadrantes Q5 e Q6
# ---------------------------------------------------------------------------
fig, ax = plt.subplots(figsize=(8.4, 4.6))
ax.scatter(np.log10(an.avaliacoes), an.nota, s=10, color=CLARA, alpha=0.45, edgecolors="none")
q5 = an[(an.avaliacoes >= P90) & (an.nota < 4.0)]
q6 = an[(an.nota >= 4.3) & (an.avaliacoes < MED)]
ax.scatter(np.log10(q5.avaliacoes), q5.nota, s=34, color=LARANJA, label=f"Q5 · alto engajamento e nota < 4,0 ({len(q5)})", zorder=3)
ax.scatter(np.log10(q6.avaliacoes), q6.nota, s=18, color=TEAL, alpha=0.75, label=f"Q6 · nota ≥ 4,3 e engajamento < mediana ({len(q6)})", zorder=2)
ax.axvline(np.log10(P90), color=ARDOSIA, ls="--", lw=1.1)
ax.axvline(np.log10(MED), color=ARDOSIA, ls=":", lw=1.1)
ax.axhline(4.0, color=ARDOSIA, ls="--", lw=1.1)
ax.axhline(4.3, color=ARDOSIA, ls=":", lw=1.1)
ax.set_title("Os dois quadrantes que geram ação (Q5 e Q6)")
ax.set_xlabel("volume de avaliações (log₁₀) · linhas: mediana e p90")
ax.set_ylabel("nota · linhas: 4,0 e 4,3")
ax.legend(loc="lower left", fontsize=8.5)
rodape(fig, FONTE + " · listas nominais não estão sujeitas ao piso n≥30 (T2)")
salva(fig, "fig06_quadrantes.png")

# ---------------------------------------------------------------------------
# fig07 — QA1 faixas de desconto
# ---------------------------------------------------------------------------
an["faixa"] = pd.cut(an.desconto, [0, 20, 40, 60, 80, 100],
                     labels=["0–20%", "21–40%", "41–60%", "61–80%", "81–100%"], include_lowest=True)
faixas = an.groupby("faixa", observed=True).agg(n=("nota", "size"), nota=("nota", "median"),
                                           wil=("wilson", "median"), aval=("avaliacoes", "median"))
faixas = faixas[faixas.n >= 30]
fig, ax1 = plt.subplots(figsize=(8.6, 3.6))
x = np.arange(len(faixas))
ax1.bar(x - 0.2, faixas.nota, 0.4, color=CLARA, label="nota mediana")
ax1.bar(x + 0.2, faixas.wil, 0.4, color=TEAL, label="nota corrigida (Wilson)")
ax1.set_xticks(x)
ax1.set_xticklabels([f"{i}\nn={int(v)}" for i, v in zip(faixas.index, faixas.n)])
ax1.set_ylim(3.0, 4.6)
ax1.set_ylabel("nota")
ax1.legend(loc="lower left", fontsize=8.5, ncol=2, frameon=True, framealpha=1.0, facecolor="white", edgecolor=CLARA)
# O destaque é do achado, não decoração: a faixa acima de 80% é a ÚNICA cuja nota corrigida cai
# abaixo de 4,0. Se o dado mudar e isso deixar de ser verdade, a figura não é gerada com o
# destaque errado — o roteiro e o relatório descrevem exatamente esta marcação.
assert (faixas.wil < 4.0).sum() == 1 and faixas.wil.iloc[-1] < 4.0, \
    "a faixa 81–100% deixou de ser a única abaixo de 4,0: o destaque da fig07 e a recomendação 3 precisam de revisão"
ax1.axvspan(x[-1] - 0.5, x[-1] + 0.5, color=AMBAR, alpha=0.18, zorder=0, lw=0)
ax1.text(x[-1], 4.56, "única faixa com\nnota corrigida < 4,0", ha="center", va="top", fontsize=8, color=TINTA)
ax2 = ax1.twinx()
ax2.plot(x, faixas.aval, color=LARANJA, marker="o", lw=2, label="volume mediano")
ax2.set_ylabel("avaliações (mediana)", color=LARANJA)
ax2.tick_params(axis="y", colors=LARANJA)
ax2.grid(False)
ax1.set_title("QA1 · Existe faixa de desconto em que nota e engajamento se sustentam?")
rodape(fig, FONTE + " · só faixas acima do piso n≥30 (T2) · nota corrigida obrigatória em ranking (T1)")
salva(fig, "fig07_faixas_desconto.png")

# ---------------------------------------------------------------------------
# fig09 — QA3 dispersão por subcategoria
# ---------------------------------------------------------------------------
vc2 = an.cat2.value_counts()
sub = vc2[vc2 >= 30].index
dados = [an[an.cat2 == s].nota.values for s in sub]
# dp amostral (ddof = 1), o mesmo da tab16, do §5.13 e do STDEV.S do guia
ordem = np.argsort([np.std(d, ddof=1) for d in dados])
fig, ax = plt.subplots(figsize=(9, 4))
bp = ax.boxplot([dados[i] for i in ordem], vert=False, patch_artist=True, widths=0.6,
                medianprops=dict(color=TINTA, lw=1.6), flierprops=dict(markersize=3, markerfacecolor=CLARA, markeredgecolor="none"))
for patch in bp["boxes"]:
    patch.set_facecolor(TEAL)
    patch.set_alpha(0.55)
    patch.set_edgecolor(ARDOSIA)
rot = [f"{sub[i].split(' | ')[-1]}\n(n={len(dados[i])}, dp={np.std(dados[i], ddof=1):.3f})".replace(".", ",", 1)
       for i in ordem]
ax.set_yticklabels(rot, fontsize=8)
ax.set_title("QA3 · Dispersão de notas por subcategoria (nível 2) — 8 grupos acima do piso")
ax.set_xlabel("nota")
rodape(fig, FONTE + " · cobertura " + f"{100*vc2[vc2>=30].sum()/N:.1f}".replace(".", ",") + "% dos produtos")
salva(fig, "fig09_dispersao_subcategoria.png")

# ---------------------------------------------------------------------------
# fig13 e fig10 — ML4
# ---------------------------------------------------------------------------
X = StandardScaler().fit_transform(np.c_[np.log(an.preco_tab), an.desconto, np.log(an.avaliacoes), an.nota])
sils = {}
for k in range(2, 8):
    km = KMeans(k, random_state=42, n_init=10).fit(X)
    sils[k] = silhouette_score(X, km.labels_)
fig, ax = plt.subplots(figsize=(7, 3.1))
ax.plot(list(sils), list(sils.values()), color=TEAL, marker="o", lw=2)
ax.scatter([4], [sils[4]], s=130, facecolor="none", edgecolor=LARANJA, lw=2.2, zorder=4)
ax.annotate(f"k = 4 adotado ({sils[4]:.3f})".replace(".", ",") + "\npor interpretabilidade", xy=(4, sils[4]),
            xytext=(4.7, sils[4] - 0.012), fontsize=8.5, color=TINTA,
            arrowprops=dict(arrowstyle="->", color=LARANJA))
ax.scatter([5], [sils[5]], s=130, facecolor="none", edgecolor=ARDOSIA, lw=2.2, zorder=4)
ax.annotate(f"máximo em k = 5 ({sils[5]:.3f})".replace(".", ","), xy=(5, sils[5]), xytext=(5.45, sils[5] + 0.0018),
            fontsize=8.5, color=ARDOSIA, arrowprops=dict(arrowstyle="->", color=ARDOSIA))
ax.set_ylim(min(sils.values()) - 0.002, max(sils.values()) + 0.004)    # folga para o rótulo ficar DENTRO do eixo
ax.set_title("ML4 · Coeficiente de silhueta por número de grupos")
ax.set_xlabel("k")
ax.set_ylabel("silhueta")
rodape(fig, FONTE + " · silhueta ≤ 0,237 indica ausência de estrutura natural de agrupamento")
salva(fig, "fig13_silhueta.png")

km = KMeans(4, random_state=42, n_init=10).fit(X)
an["grupo"] = km.labels_
arq = an.groupby("grupo").agg(n=("grupo", "size"), preco=("preco_tab", "median"),
                              preco_pago=("preco_desc", "median"),
                              desc=("desconto", "median"), aval=("avaliacoes", "median"),
                              nota=("nota", "median"), wilson=("wilson", "median"))
# Letras conforme method/definitions/registro_machine_learning.md — atribuídas pelo
# perfil, não pela ordem do KMeans (que varia). A = ticket alto · B = desconto
# agressivo sem tração (único abaixo de 4,0) · C = baixo preço e pouco desconto ·
# D = alto giro com desconto alto.
rot_map = {}
rot_map[arq.preco.idxmax()] = "A"
rot_map[arq.nota.idxmin()] = "B"
_restantes = [gid for gid in arq.index if gid not in rot_map]
rot_map[min(_restantes, key=lambda gid: arq.desc[gid])] = "C"
rot_map[max(_restantes, key=lambda gid: arq.aval[gid])] = "D"
arq["rotulo"] = [rot_map.get(gid, "?") for gid in arq.index]
arq = arq.sort_values("rotulo")
fig, ax = plt.subplots(figsize=(8.6, 4.2))
ax.scatter(arq.desc, arq.nota, s=arq.n * 1.6, c=[AMBAR, LARANJA, TEAL, AZUL][:len(arq)],
           alpha=0.82, edgecolors=BASE["card"], linewidth=1.5)
ax.axhline(4.0, color=ARDOSIA, ls="--", lw=1.1)
# Rótulos escalonados: bolhas próximas no eixo x receberiam rótulos sobrepostos.
acima = arq[arq.nota >= 4.0].sort_values("desc")
alturas = {}
ultimo_x = -99
nivel = 0
for gid, row in acima.iterrows():
    nivel = (nivel + 1) % 2 if row.desc - ultimo_x < 16 else 0
    alturas[gid] = 27 + nivel * 24
    ultimo_x = row.desc
for gid, row in arq.iterrows():
    abaixo = row.nota < 4.0                      # B fica sob a linha: rótulo vai para baixo
    ax.annotate(f"{row.rotulo} · n={int(row.n)}\n{row.preco:,.0f} · {int(row.aval):,} aval.".replace(",", "."),
                xy=(row.desc, row.nota), xytext=(0, -42 if abaixo else alturas.get(gid, 27)),
                textcoords="offset points", ha="center", fontsize=8.2, color=TINTA)
ax.text(0.5, 4.028, "limiar de satisfação baixa (4,0)", transform=ax.get_yaxis_transform(),
        ha="center", fontsize=7.5, color=ARDOSIA,
        bbox=dict(facecolor=BASE["card"], edgecolor="none", pad=1.5))
ax.set_title("ML4 · Arquétipos comerciais (k = 4) — tamanho ∝ número de produtos")
ax.set_xlabel("desconto mediano (%) · preço mediano em rupia indiana")
ax.set_ylabel("nota mediana")
ax.set_ylim(3.70, 4.56)
ax.set_xlim(12, 72)
rodape(fig, FONTE + " · convenção descritiva, nunca apresentada como descoberta")
salva(fig, "fig10_arquetipos.png")

# ---------------------------------------------------------------------------
# fig11 — ML2 AUC por bloco de preditores
# ---------------------------------------------------------------------------
# A validação mora em `src/ml2.py`, que a divide com o notebook 04 e com `numeros_roteiro.py`:
# três cópias do mesmo cálculo foi o que deixou passar o vazamento que ela corrige.
blocos = {"volume": (["avaliacoes"], []), "comerciais": (["preco_tab", "preco_desc", "desconto"], []),
          "comerciais\n+ categoria": (["preco_tab", "preco_desc", "desconto"], ["cat1"]),
          "completo": (["preco_tab", "preco_desc", "desconto", "avaliacoes"], ["cat1"])}
aucs, erros, aucs_ing, erros_ing = [], [], [], []
for num_, categ_ in blocos.values():
    s = ml2.auc(an, num_, categ_, agrupar=True)        # a que se publica: gêmeas (L8) na mesma partição
    s_ing = ml2.auc(an, num_, categ_, agrupar=False)   # a ingênua, só para medir o vazamento
    aucs.append(s.mean())
    erros.append(s.std())
    aucs_ing.append(s_ing.mean())
    erros_ing.append(s_ing.std())
# O vazamento tem de aparecer em TODOS os blocos: se algum deixasse de inflar, ou a regra de
# agrupamento ou a leitura do relatório (§6.2) deixaria de valer, e esta linha avisa.
assert all(i > a for i, a in zip(aucs_ing, aucs)), \
    f"a validação ingênua deveria inflar o AUC em todo bloco: {aucs_ing} vs {aucs}"
fig, ax = plt.subplots(figsize=(8, 3.3))
b = ax.bar(list(blocos), aucs, yerr=erros, color=[CLARA, CLARA, CLARA, TEAL], capsize=5,
           error_kw=dict(ecolor=ARDOSIA, lw=1.2))
for r, v, e in zip(b, aucs, erros):
    ax.text(r.get_x() + r.get_width() / 2, v + e + 0.012, f"{v:.2f}".replace(".", ","), ha="center", fontsize=9, color=TINTA, fontweight="bold")
ax.axhline(0.5, color=LARANJA, ls="--", lw=1.2)
ax.text(1.01, 0.5, "acaso", transform=ax.get_yaxis_transform(), ha="left", va="center", fontsize=8, color=LARANJA)
ax.set_ylim(0.45, 0.85)
ax.set_ylabel("AUC (5 partições)")   # curto: o título é longo e encostava neste rótulo
ax.set_title("ML2 · O sinal é multivariado: nenhum bloco isolado chega perto do conjunto")
rodape(fig, FONTE + " · Random Forest 300, random_state=42, StratifiedGroupKFold(5, shuffle=True) por variante (L8)\n"
       "barra = desvio entre partições")
salva(fig, "fig11_ml2_blocos.png")


# ---------------------------------------------------------------------------
# fig12 — corpus textual
# ---------------------------------------------------------------------------
ex = an.assign(_r=an.review_id.str.split(",")).explode("_r")
ex["_r"] = ex._r.str.strip()
faixa = np.where(an.nota < 4.0, "< 4,0", np.where(an.nota >= 4.3, "≥ 4,3", "4,0–4,29"))
exf = ex.assign(_f=np.where(ex.nota < 4.0, "< 4,0", np.where(ex.nota >= 4.3, "≥ 4,3", "4,0–4,29")))
ordem_f = ["< 4,0", "4,0–4,29", "≥ 4,3"]
blocos_n = [int((faixa == f).sum()) for f in ordem_f]
refs = [int((exf._f == f).sum()) for f in ordem_f]
dist = [int(exf[exf._f == f]._r.nunique()) for f in ordem_f]
fig, ax = plt.subplots(figsize=(8.6, 3.4))
x = np.arange(3)
ax.bar(x - 0.26, refs, 0.26, color=CLARA, label=f"referências ({sum(refs):,})".replace(",", "."))
ax.bar(x, dist, 0.26, color=TEAL, label=f"reviews distintos ({sum(dist):,})".replace(",", "."))
ax.bar(x + 0.26, blocos_n, 0.26, color=AMBAR, label=f"blocos = produtos ({sum(blocos_n):,})".replace(",", "."))
for i in range(3):
    ax.text(i - 0.26, refs[i] + 60, f"{refs[i]:,}".replace(",", "."), ha="center", fontsize=8, color=TINTA)
    ax.text(i, dist[i] + 60, f"{dist[i]:,}".replace(",", "."), ha="center", fontsize=8, color=TINTA)
ax.set_xticks(x)
ax.set_xticklabels([f"nota {f}" for f in ordem_f])
ax.set_ylabel("contagem")
ax.legend(fontsize=8.5)
ax.set_title("ML3 · O corpus tem três contagens — publicar só uma infla o material em 14%")
rodape(fig, FONTE + " · deduplicação por review_id obrigatória (T8) · truncamento em 8 avaliações por produto (L1)")
salva(fig, "fig12_corpus.png")

# ---------------------------------------------------------------------------
# Tabelas
# ---------------------------------------------------------------------------
print("tabelas:")


def salva_tab(dframe, nome):
    dframe.to_csv(os.path.join(TAB, nome), index=False, encoding="utf-8")
    print(f"  {nome}")


salva_tab(pd.DataFrame({
    "base": ["Bruta", "Produtos", "Nota válida", "Engajamento válido", "Analítica"],
    "n": [1465, 1351, 1350, 1349, 1348],
    "quando_usar": ["qualidade da origem", "contagem de portfólio", "só rating",
                    "só rating_count", "padrão — toda análise cruzada"]}), "tab01_bases_oficiais.csv")

dist_tab = []
for rot, col in [("Preço de tabela (rupia indiana)", "preco_tab"), ("Preço com desconto (rupia indiana)", "preco_desc"),
                 ("Desconto (%)", "desconto"), ("Nota", "nota"), ("Avaliações", "avaliacoes")]:
    s = an[col]
    dist_tab.append({"variavel": rot, "p25": round(s.quantile(.25), 2), "mediana": round(s.median(), 2),
                     "p75": round(s.quantile(.75), 2), "p90": round(s.quantile(.90), 2), "maximo": round(s.max(), 2)})
salva_tab(pd.DataFrame(dist_tab), "tab02_distribuicao.csv")

corr = []
for rot, a, b in [("Desconto × nota", "desconto", "nota"), ("Desconto × engajamento", "desconto", "avaliacoes"),
                  ("Preço de tabela × nota", "preco_tab", "nota"), ("Engajamento × nota", "avaliacoes", "nota")]:
    r, p = spearmanr(an[a], an[b])
    corr.append({"par": rot, "rho": round(r, 4), "p_valor": f"{p:.2e}", "n": N,
                 "leitura": "sem associação" if p > ALFA_CORR else "significativa, magnitude pequena"})
salva_tab(pd.DataFrame(corr), "tab03_correlacoes.csv")

# Dois pares de APOIO, citados no texto (§1.2 e §5.14) e fora da tab03 porque a tab03 é a
# tabela que o dashboard importa — a página 3 mostra os quatro pares do eixo do enunciado.
# Antes estes dois eram publicados sem código e com a tab03 como fonte, que não os tinha.
apoio = []
for rot, a, b in [("Preço de tabela × desconto", "preco_tab", "desconto"),
                  ("Preço com desconto × nota", "preco_desc", "nota")]:
    r, p_ = spearmanr(an[a], an[b])
    apoio.append({"par": rot, "rho": round(r, 4), "p_valor": f"{p_:.2e}", "n": N,
                  "leitura": ("sem associação após correção de multiplicidade" if p_ > ALFA_CORR
                             else "significativa, magnitude desprezível")})
salva_tab(pd.DataFrame(apoio), "tab24_correlacoes_apoio.csv")

cat = vc.reset_index()
cat.columns = ["categoria_nivel_1", "produtos"]
cat["acima_do_piso"] = cat.produtos >= 30
salva_tab(cat, "tab04_categorias.csv")

arq_out = arq.reset_index(drop=True)[["rotulo", "n", "preco", "preco_pago", "desc", "aval", "nota", "wilson"]]
arq_out.columns = ["arquetipo", "n", "preco_tabela_mediano", "preco_com_desconto_mediano",
                   "desconto_mediano", "avaliacoes_medianas", "nota_mediana", "nota_corrigida_mediana"]
arq_out = arq_out.round(3)
salva_tab(arq_out, "tab05_arquetipos.csv")

salva_tab(pd.DataFrame({"faixa_nota": ordem_f, "blocos": blocos_n, "referencias": refs, "reviews_distintos": dist}),
          "tab06_corpus.csv")

# O rótulo "comerciais\n+ categoria" tem quebra de linha de propósito: ela é
# para o EIXO da figura, onde o texto não cabe numa linha. No CSV a mesma
# quebra viraria um salto de linha dentro da célula, e quem abrir a tabela lê
# `comerciais\n+ categoria` como se fosse erro de geração. Sanitiza aqui.
salva_tab(pd.DataFrame({"bloco_preditores": [b.replace("\n", " ") for b in blocos],
                        "auc": [round(a, 3) for a in aucs],
                        "desvio_entre_particoes": [round(e, 3) for e in erros]}), "tab07_ml2_blocos.csv")

# tab27 · o tamanho do vazamento, medido bloco a bloco. É o que sustenta, no §6.2, a frase
# "o AUC publicado não é o ingênuo", e é o que um avaliador pede para conferir.
salva_tab(pd.DataFrame({
    "bloco_preditores": [b_.replace("\n", " ") for b_ in blocos],
    "auc_validacao_ingenua": [round(a_, 3) for a_ in aucs_ing],
    "auc_validacao_agrupada": [round(a_, 3) for a_ in aucs],
    "inflacao": [round(i_ - a_, 3) for i_, a_ in zip(aucs_ing, aucs)],
    "criterio": "ingênua = StratifiedKFold · agrupada = StratifiedGroupKFold por par (avaliacoes, nota), a regra de variante da L8"}),
    "tab27_ml2_vazamento.csv")
# ---------------------------------------------------------------------------
# tab25 · ML2 — QUAIS ATRIBUTOS ACOMPANHAM A BAIXA SATISFAÇÃO
#
# POR QUE EXISTE. O AUC por bloco diz que o sinal é multivariado; não diz
# **quais** atributos carregam esse sinal. Sem o ranking publicado, o relatório
# prova que o modelo discrimina e deixa o leitor sem a leitura de negócio —
# que é o que a pergunta Q5 pede e o que o capítulo promete entregar.
#
# A importância do Random Forest é calculada sobre o modelo COMPLETO, ajustado
# na base inteira (as partições servem para medir o AUC, não para a leitura de
# importância). As nove colunas de categoria viram uma linha só, `categoria
# nível 1`, somando as importâncias do one-hot: o que interessa é o peso da
# VARIÁVEL, não o de cada categoria dentro dela.
#
# T4 vale aqui com força: importância de variável é ASSOCIAÇÃO. A coluna
# `leitura` diz o que o número autoriza, e nenhuma linha afirma causa.
_num_full, _cat_full = blocos["completo"]
_pipe_full = ml2.monta(_num_full, _cat_full)           # o mesmo pipeline da validação, sem cópia
_pipe_full.fit(an[_num_full + _cat_full], ml2.alvo(an))
_nomes = list(_pipe_full.named_steps["pre"].get_feature_names_out())
_imp = _pipe_full.named_steps["rf"].feature_importances_
_ROTULO = {"preco_tab": "preço de tabela", "preco_desc": "preço com desconto",
           "desconto": "desconto (%)", "avaliacoes": "volume de avaliações"}
_peso = {}
for nome, valor in zip(_nomes, _imp):
    curto = nome.split("__", 1)[-1]
    chave = "categoria nível 1" if curto.startswith("cat1") else _ROTULO[curto]
    _peso[chave] = _peso.get(chave, 0.0) + float(valor)
_LEITURA = {
    "volume de avaliações": "maior peso isolado — é a associação de Q5 aparecendo no modelo",
    "desconto (%)": "segundo peso, na mesma direção de Q3 (ρ = -0,150)",
    "preço com desconto": "empatado com desconto e com preço de tabela: nenhum dos três se destaca",
    "preço de tabela": "empatado com os outros dois de preço, apesar de QA4 não achar associação univariada",
    "categoria nível 1": ("menor peso aqui, e isto precisa de ressalva: a importância de impureza "
                          "subestima variavel categorica em one-hot e superestima continua com muitos "
                          "pontos de corte. A escada de AUC mede melhor a contribuicao da familia — "
                          "ela sobe de 0,62 para 0,69 quando a categoria entra"),
}
_tab25 = (pd.DataFrame({"atributo": list(_peso), "importancia": [round(v, 4) for v in _peso.values()]})
          .sort_values("importancia", ascending=False).reset_index(drop=True))
_tab25["importancia_pct"] = (100 * _tab25.importancia / _tab25.importancia.sum()).round(1)
_tab25["leitura"] = _tab25.atributo.map(_LEITURA)
_tab25["criterio"] = "importância de impureza do Random Forest · associação, nunca causa (T4)"
_tab25["base"] = f"analítica, n = {N}"
salva_tab(_tab25, "tab25_ml2_importancia.csv")

# ---------------------------------------------------------------------------
# tab26 · B × D — O CONFLITO CENTRAL, SUBMETIDO A TESTE
#
# POR QUE EXISTE. O achado que o relatório, o sumário e o vídeo colocam em
# primeiro lugar — "B e D descontam quase o mesmo e terminam opostos" — vinha
# apoiado só na comparação de medianas. Comparar medianas não diz se a
# diferença é distinguível do acaso, e a pergunta que uma banca faz primeiro
# é exatamente essa. Aqui ela fica respondida antes de ser feita.
#
# Mann-Whitney U, não teste t: as três variáveis são assimétricas, e é a mesma
# razão pela qual o projeto usa Spearman em vez de Pearson. O tamanho de efeito
# é a correlação rank-biserial, que vem do próprio U — sem ele, p pequeno com
# n grande seria lido como "diferença grande", que é o erro que T5 existe para
# impedir.
#
# O resultado é o argumento: desconto é significativo e DESPREZÍVEL (efeito
# 0,13), enquanto nota e volume são significativos e GRANDES (0,67 e 0,89).
from scipy.stats import mannwhitneyu  # noqa: E402

_bd = an.assign(arquetipo=an.grupo.map(rot_map))
_B, _D = _bd[_bd.arquetipo == "B"], _bd[_bd.arquetipo == "D"]
_LINHAS = [("desconto", "desconto (%)", "desprezível"),
           ("nota", "nota", "grande"),
           ("avaliacoes", "volume de avaliações", "grande")]
_t26 = []
for col, rotulo, leitura in _LINHAS:
    u, pv = mannwhitneyu(_B[col], _D[col], alternative="two-sided")
    efeito = 1 - 2 * u / (len(_B) * len(_D))
    _t26.append({"variavel": rotulo, "mediana_B": round(_B[col].median(), 3),
                 "mediana_D": round(_D[col].median(), 3), "u": int(u), "p_valor": f"{pv:.2e}",
                 "efeito_rank_biserial": round(efeito, 3), "magnitude": leitura,
                 "n_B": len(_B), "n_D": len(_D),
                 "teste": "Mann-Whitney U bicaudal · efeito = correlação rank-biserial · sinal positivo = valores maiores em D",
                 "base": f"analítica, n = {N}"})
_t26 = pd.DataFrame(_t26)
salva_tab(_t26, "tab26_bxd_teste.csv")
print("  B × D: " + " · ".join(f"{r.variavel} efeito {r.efeito_rank_biserial:+.2f}" for r in _t26.itertuples()))
assert (_t26.n_B.iloc[0], _t26.n_D.iloc[0]) == (335, 447), "B e D divergem do publicado"
assert (_t26.efeito_rank_biserial > 0).all(), \
    "o sinal positivo significa 'maior em D': se algum efeito inverteu, a legenda da tab26 e o §5.17 precisam mudar"
assert abs(_t26.loc[0, "efeito_rank_biserial"]) < 0.2, \
    "o argumento do relatório exige que o efeito do DESCONTO seja desprezível"
assert (_t26.loc[1:, "efeito_rank_biserial"].abs() > 0.5).all(), \
    "o argumento exige que nota e volume tenham efeito grande"
print("  ML2 · importância: " + " · ".join(f"{r.atributo} {r.importancia_pct}%" for r in _tab25.itertuples()))
assert abs(sum(_peso.values()) - 1) < 1e-9, "as importâncias precisam somar 1 antes do arredondamento"
assert len(_tab25) == 5, f"esperados 5 atributos, {len(_tab25)}"

# tab29 e tab30 · a dispersão e a taxa de insatisfação de cada subcategoria, COM intervalo.
#
# POR QUE EXISTEM. O relatório distinguia fones ("dispersão baixa: revisão da categoria") de
# climatização ("a maior dispersão: revisão produto a produto") a partir de DOIS desvios-padrão
# sem intervalo. Medido: o teste de Levene entre os dois dá p = 0,18 e o IC95% do desvio-padrão
# da climatização (0,26–0,45) encosta no dos fones (0,19–0,25) e contém o de Kitchen (0,336).
# A distinção é HIPÓTESE, não conclusão — o que está bem sustentado é a TAXA (52,4% e 37,9%,
# ambas com intervalo acima dos 25,1% da base). As asserções abaixo prendem essa leitura ao dado:
# se um dia a dispersão passar a se distinguir, ou a taxa deixar de se distinguir da base,
# a geração falha e o texto precisa mudar.
from scipy.stats import levene  # noqa: E402

_rng = np.random.default_rng(42)


def _ic_dp(x, reps=5000):
    dps = [np.std(_rng.choice(x, len(x)), ddof=1) for _ in range(reps)]
    return np.percentile(dps, [2.5, 97.5])


def _ic_prop(k, n, z=1.96):
    """Intervalo de Wilson para proporção binomial."""
    p_ = k / n
    centro = (p_ + z * z / (2 * n)) / (1 + z * z / n)
    meia = z * np.sqrt(p_ * (1 - p_) / n + z * z / (4 * n * n)) / (1 + z * z / n)
    return centro - meia, centro + meia


_taxa_base = float((an.nota < 4.0).mean())
_c2 = an.cat2.value_counts()
_t29 = []
for _s in _c2[_c2 >= 30].index:
    _x = an[an.cat2 == _s].nota.values
    _lo, _hi = _ic_dp(_x)
    _k = int((_x < 4.0).sum())
    _plo, _phi = _ic_prop(_k, len(_x))
    _t29.append({"subcategoria": _s, "n": len(_x), "dp_nota": round(float(np.std(_x, ddof=1)), 3),
                 "dp_ic95_inf": round(float(_lo), 3), "dp_ic95_sup": round(float(_hi), 3),
                 "pct_abaixo_4_0": round(100 * _k / len(_x), 1),
                 "pct_ic95_inf": round(100 * _plo, 1), "pct_ic95_sup": round(100 * _phi, 1),
                 "taxa_da_base_pct": round(100 * _taxa_base, 1)})
_t29 = pd.DataFrame(_t29).sort_values("dp_nota").reset_index(drop=True)
_t29["criterio"] = "IC95% do desvio-padrão por bootstrap (5.000 reamostragens, semente 42) · IC95% da proporção por Wilson"
salva_tab(_t29, "tab29_dispersao_intervalos.csv")

_fones = an[an.cat2.str.contains("Headphones", na=False)].nota.values
_clima = an[an.cat2.str.contains("Heating", na=False)].nota.values
_p_lev = float(levene(_fones, _clima, center="median").pvalue)
_f29 = _t29[_t29.subcategoria.str.contains("Headphones")].iloc[0]
_c29 = _t29[_t29.subcategoria.str.contains("Heating")].iloc[0]
salva_tab(pd.DataFrame([{
    "comparacao": "fones × climatização", "teste": "Levene (centro = mediana) sobre a nota",
    "n_fones": len(_fones), "n_climatizacao": len(_clima), "p_valor": round(_p_lev, 3),
    "leitura": "dispersões não distinguíveis: a distinção por dispersão é hipótese, não conclusão",
    "base": f"analítica, n = {N}"}]), "tab30_levene_fones_climatizacao.csv")
print(f"  fones × climatização: dp {_f29.dp_nota:.3f} × {_c29.dp_nota:.3f} · Levene p = {_p_lev:.3f}")
assert _f29.dp_nota < _c29.dp_nota, "a leitura 'fones têm dispersão menor' deixou de valer"
assert _p_lev > 0.05, ("a dispersão de fones e climatização passou a se distinguir (Levene p ≤ 0,05): "
                       "a distinção 'categoria × produto a produto' pode voltar a ser conclusão — revisar §5.18 e §7.7")
assert _f29.pct_ic95_inf > 100 * _taxa_base and _c29.pct_ic95_inf > 100 * _taxa_base, \
    "a taxa de insatisfação de fones ou climatização deixou de se distinguir da taxa da base"

g_out = faixas.reset_index()
g_out.columns = ["faixa_desconto", "n", "nota_mediana", "nota_corrigida_wilson", "avaliacoes_medianas"]
salva_tab(g_out.round(3), "tab08_faixas_desconto.csv")

# tab28 · a fatia de produtos abaixo de 4,0 por faixa de desconto — o KPI de insatisfação do próprio
# projeto, e o outro corte do mesmo dado. A mediana da nota corrigida (tab08) é plana nas quatro
# primeiras faixas; a fatia abaixo de 4,0 sobe com o desconto. Os dois não se contradizem (a mediana
# mede o produto típico, a fatia mede a cauda), e publicar só um deles era contar meia história.
_ab = an.groupby("faixa", observed=True).agg(n=("nota", "size"), abaixo_4_0=("nota", lambda v: int((v < 4.0).sum())))
_ab["pct_abaixo_4_0"] = (100 * _ab.abaixo_4_0 / _ab.n).round(1)
_ab["taxa_da_base_pct"] = round(100 * float((an.nota < 4.0).mean()), 1)
_ab["criterio"] = "produtos com nota bruta < 4,0 sobre os produtos da faixa · associação, nunca causa (T4)"
assert int(_ab.n.sum()) == N and int(_ab.abaixo_4_0.sum()) == 339, "tab28 não fecha com 1.348 produtos e 339 abaixo de 4,0"
assert _ab.pct_abaixo_4_0.iloc[0] < _ab.taxa_da_base_pct.iloc[0] < _ab.pct_abaixo_4_0.iloc[-1], \
    "a leitura 'a fatia abaixo de 4,0 sobe com o desconto' deixou de valer"
salva_tab(_ab.reset_index().rename(columns={"faixa": "faixa_desconto"}), "tab28_faixa_desconto_insatisfacao.csv")

# ---------------------------------------------------------------------------
# tab19-tab21 · AS TRÊS LISTAS NOMINAIS
#
# POR QUE EXISTEM. T2 impõe piso de n >= 30 para comparar grupos agregados e
# abre exceção para lista nominal de produtos — mas a exceção é CONDICIONADA a
# "exibir o n de avaliações produto a produto". Enquanto as listas não eram
# publicadas, a condição que autoriza a exceção não estava cumprida: o
# relatório recomendava agir sobre 19 produtos que não existiam como lista
# recuperável, e sobre os 61 de Q6 que não existiam em arquivo nenhum.
#
# A lista de Q6 é a CORRIGIDA (nota corrigida >= 4,3), não o funil de 187:
# uma lista de oportunidades é um ranking, e T1 exige nota corrigida em todo
# ranking. É a medida M22 do catálogo DAX.
#
# Os nomes de coluna na saída seguem o vocabulário canônico do dicionário
# (categoria_n1, categoria_n2, nota_corrigida), não os apelidos internos
# deste script (cat1, cat2, wilson).
def lista_nominal(quadro, arquivo, ordenar_por):
    saida = (quadro[["product_id", "product_name", "cat1", "cat2",
                     "avaliacoes", "nota", "wilson", "preco_tab", "desconto"]]
             .rename(columns={"cat1": "categoria_n1", "cat2": "categoria_n2",
                              "wilson": "nota_corrigida"})
             .sort_values(ordenar_por, ascending=False))
    salva_tab(saida.round(3), arquivo)
    return saida


_q5 = lista_nominal(an[(an.avaliacoes >= P90) & (an.nota < 4.0)],
                    "tab19_q5_risco_vitrine_nominal.csv", "avaliacoes")
_q6 = lista_nominal(an[(an.nota >= 4.3) & (an.avaliacoes < MED) & (an.wilson >= 4.3)],
                    "tab20_q6_acionavel_nominal.csv", "nota_corrigida")
_anc = lista_nominal(an[(an.avaliacoes >= P90) & (an.nota >= 4.3)],
                     "tab21_ancoras_nominal.csv", "nota_corrigida")

# A lista que responde Q2 ("quais produtos possuem maior engajamento?"): todos os de engajamento
# alto (volume >= p90). A tab13 já dizia "lista nominal com volume e nota corrigida por produto",
# e o relatório só trazia o corte e a proporção: a pergunta do enunciado é literalmente "quais produtos".
_q2 = lista_nominal(an[an.avaliacoes >= P90], "tab31_q2_engajamento_alto_nominal.csv", "avaliacoes")

print(f"  listas nominais: Q2 = {len(_q2)} · Q5 = {len(_q5)} · Q6 acionável = {len(_q6)} · âncoras = {len(_anc)}")
assert len(_q2) == 136, f"engajamento alto deveria ter 136 produtos, tem {len(_q2)}"
assert len(_q5) == 19, f"Q5 deveria ter 19 produtos, tem {len(_q5)}"
assert len(_q6) == 61, f"Q6 acionável deveria ter 61, tem {len(_q6)}"
assert len(_anc) == 41, f"âncoras deveriam ser 41, são {len(_anc)}"

# ---------------------------------------------------------------------------
# tab22 · O ARQUÉTIPO DE CADA PRODUTO
#
# POR QUE EXISTE. O Power Query refaz a preparação dos dados, mas não roda
# KMeans: o agrupamento de ML4 só existe aqui. A tab05 publica o RESUMO dos
# quatro arquétipos; o dashboard precisa da LETRA de cada produto para filtrar
# a página 2c e o detalhamento — o passo 11 do Power Query mescla esta tabela
# na BaseAnalitica por product_id.
#
# A letra vem do mesmo rot_map da fig10 e da tab05 (perfil, não ordem do
# KMeans), então as três saídas não podem divergir. As contagens publicadas
# são conferidas por assertion, e a soma por letra precisa ser a da tab05.
# Além da versão do scikit-learn, o KMeans é sensível à ORDEM DAS LINHAS:
# reordenada por product_id, a mesma especificação desloca 2 produtos de
# letra. A ordem canônica (avaliações decrescentes, depois ordem de origem)
# é a mesma na gold, aqui e no notebook 04 — não reordenar `an` antes daqui.
# Sem texto de avaliação e sem identificador de consumidor (T7).
_tab22 = (an.assign(arquetipo=an.grupo.map(rot_map))[["product_id", "arquetipo"]]
          .sort_values("product_id").reset_index(drop=True))
salva_tab(_tab22, "tab22_arquetipo_por_produto.csv")
_cont22 = _tab22.arquetipo.value_counts().sort_index().to_dict()
print(f"  arquétipo por produto: {_cont22}")
assert len(_tab22) == N and _tab22.product_id.is_unique, "tab22 precisa de 1 linha por produto"
assert _tab22.arquetipo.isin(list("ABCD")).all(), "tab22 com produto sem letra de arquétipo"
assert _cont22 == {"A": 268, "B": 335, "C": 298, "D": 447}, f"tab22 diverge do publicado: {_cont22}"
assert _cont22 == dict(zip(arq_out.arquetipo, arq_out.n)), "tab22 diverge da tab05"

# ---------------------------------------------------------------------------
# tab15 a tab18 · SATISFAÇÃO POR GRUPO E A MATRIZ DE RELEVÂNCIA
#
# POR QUE EXISTEM AQUI. Estas quatro tabelas estavam publicadas em
# 02_results/tables sem gerador em lugar nenhum: tinham sido escritas num
# notebook que depois mudou. Enquanto foi assim, "toda tabela é regenerável"
# era promessa sem prova — e a correção do nome de produto que carrega o glifo
# de moeda não alcançava a tab17, porque nada a reescrevia.
#
# A tab17 é a matriz de D-2 produto a produto, com os MESMOS cortes já
# operacionais (volume >= p90 ou < mediana × nota bruta >= 4,3 ou < 4,0): não
# há limiar novo aqui. Os rótulos de engajamento e de satisfação repetem a
# regra da camada gold, e as contagens dos dois lados são conferidas por
# assertion — divergir de prepara_dados.py passa a ser erro, não surpresa.
#
# A ordenação da tab17 é por nota corrigida (T1) e ESTÁVEL: nos empates vale a
# ordem canônica da gold (avaliações decrescentes, depois ordem de origem). A
# versão anterior do arquivo saíra de uma ordenação instável, que devolve
# ordem diferente a cada versão de biblioteca — nenhuma contagem muda, mas o
# arquivo deixava de ser reprodutível.
PISO = 30


def _pct_baixa(serie):
    return round(100 * (serie < 4.0).mean(), 3)


_c1 = an.groupby("cat1")
_t15 = pd.DataFrame({"n": _c1.size(), "nota_med": _c1.nota.median(),
                     "wilson_med": _c1.wilson.median().round(3),
                     "pct_baixa": _c1.nota.agg(_pct_baixa),
                     "aval_med": _c1.avaliacoes.median(), "desc_med": _c1.desconto.median()})
_t15 = (_t15[_t15.n >= PISO].sort_values("wilson_med", ascending=False)
        .reset_index().rename(columns={"cat1": "categoria_n1"}))
salva_tab(_t15, "tab15_satisfacao_categoria.csv")

# dp amostral (ddof = 1), que é o mesmo do STDEV.S do guia do Power BI
_c2 = an.groupby("cat2")
_t16 = pd.DataFrame({"n": _c2.size(), "nota_med": _c2.nota.median(),
                     "wilson_med": _c2.wilson.median().round(3),
                     "dp": _c2.nota.std(ddof=1).round(3),
                     "iqr": (_c2.nota.quantile(0.75) - _c2.nota.quantile(0.25)).round(3),
                     "pct_baixa": _c2.nota.agg(_pct_baixa)})
_t16 = (_t16[_t16.n >= PISO].sort_values("wilson_med", ascending=False)
        .reset_index().rename(columns={"cat2": "categoria_n2"}))
salva_tab(_t16, "tab16_satisfacao_subcategoria.csv")

_relev = np.where((an.avaliacoes >= P90) & (an.nota >= 4.3), "Âncora",
         np.where((an.avaliacoes >= P90) & (an.nota < 4.0), "Risco de vitrine (Q5)",
         np.where((an.nota >= 4.3) & (an.avaliacoes < MED), "Subexplorado (Q6)",
         np.where((an.nota < 4.0) & (an.avaliacoes < MED), "Cauda frágil", "Intermediário"))))
_mat = an.assign(
    relevancia=_relev,
    engajamento=np.where(an.avaliacoes >= P90, "alto",
                         np.where(an.avaliacoes < MED, "baixo", "intermediario")),
    satisfacao=np.where(an.nota < 4.0, "baixa", np.where(an.nota >= 4.3, "alta", "media")))
_t17 = (_mat.rename(columns={"cat1": "categoria_n1", "wilson": "nota_corrigida"})
        [["product_id", "product_name", "categoria_n1", "relevancia", "engajamento",
          "satisfacao", "avaliacoes", "nota", "nota_corrigida"]]
        .sort_values("nota_corrigida", ascending=False, kind="stable").reset_index(drop=True))
salva_tab(_t17, "tab17_matriz_relevancia.csv")

_t18 = pd.DataFrame({
    "produtos": _c1.size(), "volume": _c1.avaliacoes.sum(), "wilson": _c1.wilson.median().round(3),
    "ancoras": _mat[_mat.relevancia == "Âncora"].groupby("cat1").size(),
    "q5": _mat[_mat.relevancia == "Risco de vitrine (Q5)"].groupby("cat1").size()}).fillna(0)
_t18 = _t18[_t18.produtos >= PISO].copy()
_t18["share_volume_pct"] = (100 * _t18.volume / an.avaliacoes.sum()).round(1)
_t18[["ancoras", "q5"]] = _t18[["ancoras", "q5"]].astype(int)
_t18 = (_t18.sort_values("volume", ascending=False).reset_index()
        .rename(columns={"cat1": "categoria_n1"}))
salva_tab(_t18, "tab18_relevancia_categoria.csv")

_cont17 = _t17.relevancia.value_counts().to_dict()
print(f"  satisfação por grupo: {len(_t15)} categorias · {len(_t16)} subcategorias acima do piso")
print(f"  matriz de relevância: {_cont17}")
assert len(_t17) == N and _t17.product_id.is_unique, "tab17 precisa de 1 linha por produto"
assert _cont17 == {"Intermediário": 874, "Cauda frágil": 227, "Subexplorado (Q6)": 187,
                   "Âncora": 41, "Risco de vitrine (Q5)": 19}, f"matriz diverge do publicado: {_cont17}"
assert _t17.engajamento.value_counts().to_dict() == {"baixo": 673, "intermediario": 539, "alto": 136}, \
    "faixas de engajamento divergem da camada gold"
assert _t17.satisfacao.value_counts().to_dict() == {"media": 591, "alta": 418, "baixa": 339}, \
    "faixas de satisfação divergem da camada gold"
assert (len(_t15), len(_t16)) == (4, 8), f"piso T2: esperadas 4 categorias e 8 subcategorias, {len(_t15)} e {len(_t16)}"
assert _t18.ancoras.sum() == 41 and _t18.q5.sum() == 19, "tab18 não fecha com a matriz"
assert abs(_t18.share_volume_pct.sum() - 99.5) < 0.05, "share de volume das 4 elegíveis deveria somar 99,5%"


print(f"\n{len(os.listdir(IMG))} figuras · {len(os.listdir(TAB))} tabelas")
print("Todas as figuras usam a paleta v06 (T9) e declaram base e n no rodapé (T3).")

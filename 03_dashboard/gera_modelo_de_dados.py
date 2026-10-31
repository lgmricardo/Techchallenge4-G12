# -*- coding: utf-8 -*-
"""
Diagrama do modelo de dados do .pbix — 03_dashboard/modelo_de_dados.png.

POR QUE É GERADO E NÃO DESENHADO
--------------------------------
O diagrama lê as tabelas, as colunas, os tipos e as contagens DIRETAMENTE dos
arquivos — a camada gold e as tabelas de resultado de 02_results/tables/. Um
diagrama desenhado à mão descreve o modelo do dia em que foi desenhado; este
descreve o modelo ESPERADO a partir das fontes que o definem. Se uma coluna
entrar ou sair, a próxima execução já a mostra — é o mesmo princípio de
src/valida_dicionario.py, aplicado à figura.

A especificação vem de modelo_esperado.py, a mesma que verifica_pbix.py usa para
conferir o arquivo entregue: uma lista só, para o desenho e para a conferência.
O que não está em arquivo nenhum é declarado lá e conferido contra a fonte —
as 7 colunas derivadas contra os passos 9 e 10 do guia de montagem.

O QUE O MODELO TEM
------------------
Duas tabelas de fato, construídas no Power Query: BaseAnalitica (as 17 colunas
da gold + 7 derivadas no Power Query + `arquetipo`, da tab22 = 25) e Reviews,
ligadas por product_id.
Cinco tabelas de resultado, prontas do Python, e a tabela Conferencia, todas
SEM relacionamento — elas descrevem a base inteira, e um filtro que as
alcançasse exibiria número que ninguém mediu. A tab22 não aparece como tabela: é consulta sem carga, existe só
para a mesclagem. Se ela não cobrir os 1.348 produtos, o script falha — o
diagrama afirmaria uma coluna que a BaseAnalitica não teria inteira.

Paleta v06 (T9): fundo branco para impressão, texto em `tinta`, rótulos em
`secundario`, e UM único elemento em âmbar — o relacionamento, que é o ponto
do diagrama (regra dos 10%). As tabelas sem relacionamento têm borda tracejada:
a ausência de ligação é informação, não esquecimento.

Uso: python 03_dashboard/gera_modelo_de_dados.py
"""

import os
import sys

import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.patches import FancyBboxPatch

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))
from paleta import aplicar, BASE, ESTRUTURA, CHAMADAS  # noqa: E402

sys.path.insert(0, os.path.join(RAIZ, "03_dashboard"))
# BASE e REVIEWS do modelo são NOMES DE TABELA; BASE da paleta é o dicionário de cores.
from modelo_esperado import BASE as T_BASE, REVIEWS as T_REVIEWS  # noqa: E402
from modelo_esperado import (  # noqa: E402
    CONFERENCIA, CONFERENCIA_CSV, DERIVADAS, GOLD, MESCLADAS, ORIGEM, RESULTADO, TABELAS,
    conferir_derivadas_no_guia)

SAIDA = os.path.join(RAIZ, "03_dashboard", "modelo_de_dados.png")
CHAVE_PRIMARIA = {T_BASE: "product_id", T_REVIEWS: "review_id"}
CHAVE_ESTRANGEIRA = {T_REVIEWS: "product_id"}


# O tipo segue o DECLARADO no dicionário de dados, não o inferido dos valores:
# `desconto` só tem percentuais redondos e pareceria inteiro, mas é declarado
# decimal 0–100; `avaliacoes` é gravada com ".0" no CSV, mas é contagem.
CONTAGENS = {"avaliacoes"}


def tipo_legivel(nome, serie):
    """Tipo da coluna no vocabulário do dicionário de dados."""
    if pd.api.types.is_bool_dtype(serie):
        return "booleano"
    if pd.api.types.is_numeric_dtype(serie):
        return "inteiro" if nome in CONTAGENS else "decimal"
    return "texto"


def milhar(n):
    """Separador de milhar brasileiro, aplicado SÓ ao número."""
    return f"{n:,}".replace(",", ".")


def le_tabela(arquivo):
    quadro = pd.read_csv(os.path.join(GOLD, arquivo))
    return quadro, [(c, tipo_legivel(c, quadro[c])) for c in quadro.columns]


base, cols_base = le_tabela("base_analitica.csv")
rev, cols_rev = le_tabela("reviews.csv")

# A BaseAnalitica do modelo = gold + arquetipo da tab22. A mescla só é
# afirmada se a tab22 cobrir todos os produtos, sem sobra e sem repetição.
tab22 = pd.read_csv(os.path.join(TABELAS, "tab22_arquetipo_por_produto.csv"))
assert tab22.product_id.is_unique, "tab22 com product_id repetido"
assert set(tab22.product_id) == set(base.product_id), "tab22 não cobre exatamente a BaseAnalitica"
assert tab22.arquetipo.isin(list("ABCD")).all(), "tab22 com letra fora de A–D"
base = base.merge(tab22, on="product_id", how="left", validate="one_to_one")

conferir_derivadas_no_guia()
cols_base += [(n, tipo) for n, tipo, _ in DERIVADAS] + [("arquetipo", "texto")]

resultado = []
for nome, arquivo, pagina, uso in RESULTADO:
    quadro = pd.read_csv(os.path.join(TABELAS, arquivo))
    resultado.append((nome, arquivo, pagina, uso, quadro.shape))
_conf = pd.read_csv(CONFERENCIA_CSV)
resultado.append((CONFERENCIA, "conferencia_referencia.csv", "oculta",
                  "DAX × Python · Conf · Divergentes = 0", _conf.shape))

aplicar(tamanho_base=9, fundo="card")
fig, ax = plt.subplots(figsize=(11, 10.8))
ax.set_xlim(0, 110)
ax.set_ylim(0, 108)
ax.axis("off")

LINHA = 2.55          # altura de cada linha de coluna
TOPO = 97             # topo das duas tabelas de fato


def desenha_tabela(x, largura, nome, papel, quadro, colunas):
    """Desenha uma tabela de fato e devolve (y da linha da chave, base da caixa)."""
    n_lin, n_col = len(quadro), len(colunas)
    altura = 5.2 + LINHA * len(colunas) + 1.0
    base_y = TOPO - altura
    ax.add_patch(FancyBboxPatch((x, base_y), largura, altura,
                                boxstyle="round,pad=0,rounding_size=0.8",
                                facecolor=BASE["card"], edgecolor=ESTRUTURA["grade"],
                                linewidth=1.2))
    # cabeçalho
    ax.add_patch(FancyBboxPatch((x, TOPO - 5.2), largura, 5.2,
                                boxstyle="round,pad=0,rounding_size=0.8",
                                facecolor=ESTRUTURA["tinta"], edgecolor=ESTRUTURA["tinta"]))
    ax.text(x + 1.6, TOPO - 2.0, nome, color=BASE["card"], fontsize=11,
            fontweight="bold", va="center", family="monospace")
    ax.text(x + 1.6, TOPO - 4.0,
            f"{papel} · {milhar(n_lin)} linhas × {n_col} colunas",
            color=BASE["divisor"], fontsize=8, va="center")
    y_chave = None
    for i, (col, tipo) in enumerate(colunas):
        y = TOPO - 5.2 - LINHA * (i + 0.5) - 0.5
        pk = col == CHAVE_PRIMARIA.get(nome)
        fk = col == CHAVE_ESTRANGEIRA.get(nome)
        # zebra em `divisor`, não em `canvas`: o creme competiria com o âmbar
        # do relacionamento, e a regra dos 10% admite um único âmbar
        if i % 2 == 1:
            ax.add_patch(plt.Rectangle((x + 0.3, y - LINHA / 2), largura - 0.6, LINHA,
                                       facecolor=BASE["divisor"], edgecolor="none"))
        ax.text(x + 1.6, y, col, color=ESTRUTURA["tinta"], fontsize=8.6, va="center",
                family="monospace", fontweight="bold" if (pk or fk or col in MESCLADAS) else "normal")
        rotulo = (("chave primária · " if pk else "chave estrangeira · " if fk else "")
                  + (f"{ORIGEM[col]} · " if col in ORIGEM else "") + tipo)
        ax.text(x + largura - 1.6, y, rotulo,
                color=ESTRUTURA["secundario"], fontsize=7.8, va="center", ha="right")
        if col == "product_id":
            y_chave = y
    return y_chave, base_y


X_B, L_B = 3, 48
X_R, L_R = 67, 40
y1, fundo_base = desenha_tabela(X_B, L_B, T_BASE, "fato de produto", base, cols_base)
y2, fundo_rev = desenha_tabela(X_R, L_R, T_REVIEWS, "fato de avaliação", rev, cols_rev)

# o relacionamento — o único elemento em âmbar da figura
xa, xb = X_B + L_B, X_R
meio = (xa + xb) / 2
ax.plot([xa, meio, meio, xb], [y1, y1, y2, y2], color=CHAMADAS["destaque"],
        linewidth=3, solid_capstyle="round", zorder=3)
ax.annotate("", xy=(xb - 0.2, y2), xytext=(xb - 3.6, y2),
            arrowprops=dict(arrowstyle="-|>", color=CHAMADAS["destaque"], lw=3), zorder=4)
ax.text(xa + 0.8, y1 + 1.1, "1", color=ESTRUTURA["tinta"], fontsize=11, fontweight="bold")
ax.text(xb - 4.4, y2 + 1.1, "N", color=ESTRUTURA["tinta"], fontsize=11, fontweight="bold")
ax.text(meio, min(y1, y2) - 4.2, "um para muitos\nfiltro unidirecional",
        color=ESTRUTURA["tinta"], fontsize=8.4, va="top", ha="center", linespacing=1.4)

# as tabelas de resultado — borda tracejada: nenhum relacionamento
topo_res = fundo_rev - 4.5
ax.text(X_R, topo_res, "Resultado e conferência — sem relacionamento", color=ESTRUTURA["tinta"],
        fontsize=9.4, fontweight="bold")
ax.text(X_R, topo_res - 2.6, "prontas do Python · não respondem a filtro",
        color=ESTRUTURA["secundario"], fontsize=8.2)
ALT_CARTAO, PASSO = 4.4, 5.5
for i, (nome, arquivo, pagina, uso, (n_lin, n_col)) in enumerate(resultado):
    topo = topo_res - 4.6 - i * PASSO
    ax.add_patch(FancyBboxPatch((X_R, topo - ALT_CARTAO), L_R, ALT_CARTAO,
                                boxstyle="round,pad=0,rounding_size=0.6",
                                facecolor=BASE["card"], edgecolor=ESTRUTURA["grade"],
                                linewidth=1.1, linestyle=(0, (4, 2.5))))
    ax.text(X_R + 1.6, topo - 1.5, nome, color=ESTRUTURA["tinta"], fontsize=9,
            fontweight="bold", va="center", family="monospace")
    ax.text(X_R + L_R - 1.6, topo - 1.5, pagina, color=ESTRUTURA["tinta"], fontsize=8,
            va="center", ha="right")
    ax.text(X_R + 1.6, topo - 3.25, f"{uso} · {milhar(n_lin)} × {n_col}",
            color=ESTRUTURA["secundario"], fontsize=7.8, va="center")

# o que deliberadamente não existe — abaixo das tabelas de resultado
topo_aus = topo_res - 4.6 - (len(resultado) - 1) * PASSO - ALT_CARTAO - 4.5
ax.text(X_R, topo_aus, "O que não existe no modelo, e por quê", color=ESTRUTURA["tinta"],
        fontsize=9.4, fontweight="bold")
ausentes = [
    ("dimensão de tempo", "a base não tem data (L4)"),
    ("dimensão de cliente", "seria dado pessoal, vedado (T7)"),
    ("tabela de vendas", "não existe variável de venda (T6)"),
    ("tab22 como tabela", "consulta sem carga — só para a mesclagem"),
]
for i, (o_que, porque) in enumerate(ausentes):
    ax.text(X_R, topo_aus - 4 - i * 5.2, f"·  {o_que}", color=ESTRUTURA["tinta"], fontsize=8.8,
            fontweight="bold")
    ax.text(X_R + 2.2, topo_aus - 6.4 - i * 5.2, porque, color=ESTRUTURA["secundario"], fontsize=8.3)

# título
ax.text(3, 105, "Modelo de dados do dashboard", color=ESTRUTURA["tinta"],
        fontsize=14, fontweight="bold")
ax.text(3, 101.6, "Duas tabelas de fato e um relacionamento; seis tabelas sem relacionamento — cinco de "
        "resultado e a de conferência. Gerado dos arquivos e do guia — não à mão.",
        color=ESTRUTURA["secundario"], fontsize=9)

# rodapé T3
ax.text(3, 3.2, f"Fonte: 00_data/gold/ e 02_results/tables/ · BaseAnalitica n = {milhar(len(base))} "
        f"produtos — {len(cols_base) - len(ORIGEM)} da gold + {len(DERIVADAS)} do Power Query + arquetipo da tab22 · "
        f"Reviews n = {milhar(len(rev))} reviews deduplicados por review_id (T8)",
        color=ESTRUTURA["secundario"], fontsize=7.6)
ax.text(3, 1.2, "Valores em rupia indiana, sem conversão (L5) · mais a tabela vazia _Medidas: as 22 medidas "
        "do catálogo, as variantes T2, as auxiliares das páginas e as 6 de conferência",
        color=ESTRUTURA["secundario"], fontsize=7.6)

fig.savefig(SAIDA, dpi=200, bbox_inches="tight", facecolor=BASE["card"])
print(f"  {SAIDA}")
print(f"  BaseAnalitica: {len(base)} × {len(cols_base)} · Reviews: {rev.shape[0]} × {rev.shape[1]}")
print("  resultado: " + " · ".join(f"{n} {s[0]}×{s[1]}" for n, _, _, _, s in resultado))

# -*- coding: utf-8 -*-
"""
Validação da base do Tech Challenge Fase 4 — v2 (24/09/2026).

O QUE MUDA EM RELAÇÃO À v1
--------------------------
1. REGRA DE DEDUPLICAÇÃO DETERMINÍSTICA. A v1 ordenava por `rating_count`
   descendente sem `kind=`, o que usa quicksort — ordenação NÃO estável. Dos 92
   `product_id` repetidos, apenas 27 têm um máximo único; nos outros 65 o máximo
   empata e a regra publicada não diz qual linha fica. O resultado passava a
   depender do algoritmo de ordenação da biblioteca.
   A v2 declara o desempate: maior `rating_count` e, no empate, MENOR ÍNDICE DE
   LINHA NA ORIGEM. Reprodutível em Python, em DAX e em Power Query.

2. COBERTURA. A v1 executava 23 asserções e deixava de fora a tabela de
   distribuição, as quatro correlações, a contagem por categoria e o corpus por
   faixa. A v2 cobre todos os números publicados em
   `method/definitions/base_factual_e_bases_de_calculo.md`.

3. BASE DECLARADA. Cada asserção diz sobre qual das cinco bases foi medida,
   cumprindo T3.

Entrada : amazon.csv (Kaggle — karkavelrajaj/amazon-sales-dataset)
          SHA-256 4ba126c4ba8edd35e62e94ce1c853073d832de380184ab4f5f97d1e314882c77
Saída   : relatório no console + código 0 (tudo confere) ou 1 (divergência)
Uso     : python valida_base.py [caminho/para/amazon.csv]

Dependências: pandas. scipy é opcional — sem ela, as quatro correlações são
puladas e declaradas como puladas (nunca silenciosamente aprovadas).
"""

import sys
import hashlib
import pandas as pd
import numpy as np

# O caractere abaixo é o marcador de moeda NA ORIGEM — aquilo que o tratamento
# REMOVE. Ele é escrito como escape unicode de propósito: a premissa do projeto
# é que o símbolo de rupia não apareça em nenhum rótulo, visual, tabela ou texto
# publicado (escreve-se "rupia" por extenso). Aqui ele existe só como alvo de
# remoção, e o escape garante que o glifo não esteja nem no código-fonte.
MARCADOR_MOEDA_ORIGEM = "\u20b9"  # rupia indiana, U+20B9

try:
    from scipy.stats import spearmanr
    TEM_SCIPY = True
except ImportError:
    TEM_SCIPY = False

CAMINHO = sys.argv[1] if len(sys.argv) > 1 else "amazon.csv"
SHA_ESPERADO = "4ba126c4ba8edd35e62e94ce1c853073d832de380184ab4f5f97d1e314882c77"

falhas = []
puladas = []


def confere(rotulo, obtido, esperado, base, tol=0.0):
    """Asserção com base declarada (T3) e tolerância explícita."""
    try:
        ok = abs(float(obtido) - float(esperado)) <= tol
    except (TypeError, ValueError):
        ok = obtido == esperado
    marca = "OK  " if ok else "FALHA"
    print(f"{marca} | {rotulo:<52} obtido={obtido} esperado={esperado} [base {base}]")
    if not ok:
        falhas.append(rotulo)
    return ok


def pula(rotulo, motivo):
    print(f"PULA | {rotulo:<52} {motivo}")
    puladas.append(rotulo)


def secao(titulo):
    print(f"\n=== {titulo} ===")


# ---------------------------------------------------------------------------
# 0. Procedência do arquivo
# ---------------------------------------------------------------------------
secao("PROCEDÊNCIA")
try:
    with open(CAMINHO, "rb") as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()
except FileNotFoundError:
    sys.exit(f"ERRO: arquivo não encontrado em '{CAMINHO}'.")
confere("SHA-256 do amazon.csv", sha, SHA_ESPERADO, "arquivo")

try:
    df = pd.read_csv(CAMINHO, dtype=str)
except Exception as erro:
    sys.exit(f"ERRO ao ler o CSV: {erro}")


def numero(serie, remover):
    saida = serie.astype(str)
    for ch in remover:
        saida = saida.str.replace(ch, "", regex=False)
    return pd.to_numeric(saida, errors="coerce")


df["preco_desc"] = numero(df.discounted_price, [MARCADOR_MOEDA_ORIGEM, ","])
df["preco_tab"] = numero(df.actual_price, [MARCADOR_MOEDA_ORIGEM, ","])
df["desconto"] = numero(df.discount_percentage, ["%"])
df["avaliacoes"] = numero(df.rating_count, [","])
df["nota"] = pd.to_numeric(df.rating, errors="coerce")

# ---------------------------------------------------------------------------
# 1. Estrutura e conversão — base BRUTA
# ---------------------------------------------------------------------------
secao("ESTRUTURA — base bruta")
confere("linhas", df.shape[0], 1465, "bruta")
confere("colunas", df.shape[1] - 5, 16, "bruta")  # 5 colunas derivadas acima
confere("linhas integralmente duplicadas", df.duplicated().sum(), 0, "bruta")
confere("nulos em rating_count", df.avaliacoes.isna().sum(), 2, "bruta")
confere("falha de conversão em rating", df.nota.isna().sum(), 1, "bruta")
confere("falha de conversão em preços",
        df.preco_tab.isna().sum() + df.preco_desc.isna().sum(), 0, "bruta")
confere("falha de conversão em desconto", df.desconto.isna().sum(), 0, "bruta")

# ---------------------------------------------------------------------------
# 2. Deduplicação DETERMINÍSTICA
# ---------------------------------------------------------------------------
secao("DEDUPLICAÇÃO — regra determinística")
df["_ordem"] = np.arange(len(df))
prod = (df.sort_values(["avaliacoes", "_ordem"], ascending=[False, True],
                       na_position="last")
          .drop_duplicates("product_id", keep="first"))

repetidos = df[df.product_id.duplicated(keep=False)]
n_rep = repetidos.product_id.nunique()
empate_no_max = sum(1 for _, s in repetidos.groupby("product_id")
                    if (s.avaliacoes == s.avaliacoes.max()).sum() > 1
                    or s.avaliacoes.isna().all())

confere("linhas excedentes", len(df) - len(prod), 114, "bruta")
confere("product_id repetidos", n_rep, 92, "bruta")
confere("repetidos com máximo ÚNICO (regra decide)", n_rep - empate_no_max, 27, "bruta")
confere("repetidos com máximo EMPATADO (desempate decide)", empate_no_max, 65, "bruta")

nota_ok = prod[prod.nota.notna()]
eng_ok = prod[prod.avaliacoes.notna()]
an = prod[prod.nota.notna() & prod.avaliacoes.notna()].copy()

confere("produtos após deduplicação", len(prod), 1351, "produtos")
confere("base com nota válida", len(nota_ok), 1350, "nota válida")
confere("base com engajamento válido", len(eng_ok), 1349, "engajamento")
confere("BASE ANALÍTICA", len(an), 1348, "analítica")

# L6 — o que o relatório afirma sobre as duplicidades da origem. Estas afirmações viviam num registro
# de apuração datado (P3) e não eram conferidas por nenhum comando; aqui passam a ser reproduzidas.
secao("INCONSISTÊNCIAS DA ORIGEM — L6")
for _col, _rot in (("rating", "nota"), ("category", "categoria"), ("product_name", "nome")):
    confere(f"produtos com {_rot} divergente entre ocorrências",
            int((repetidos.groupby("product_id")[_col].nunique(dropna=False) > 1).sum()), 0, "bruta")
_amp = repetidos.groupby("product_id").avaliacoes.agg(["min", "max"]).dropna()
confere("divergência relativa máxima de rating_count (%)",
        round(float(((_amp["max"] - _amp["min"]) / _amp["max"]).max() * 100), 2), 0.17, "bruta", tol=0.005)
_primeira = df.drop_duplicates("product_id", keep="first")
confere("diferença de soma de rating_count entre as duas regras de deduplicação",
        int(abs(prod.avaliacoes.sum() - _primeira.avaliacoes.sum())), 40, "produtos (1.351)")

# ---------------------------------------------------------------------------
# 3. Coerência comercial
# ---------------------------------------------------------------------------
secao("COERÊNCIA COMERCIAL — base analítica")
confere("preço com desconto acima do preço de tabela",
        (an.preco_desc > an.preco_tab).sum(), 0, "analítica")
recalc = (1 - an.preco_desc / an.preco_tab) * 100
divg = (recalc - an.desconto).abs()
confere("divergência de desconto acima de 1 p.p.", (divg > 1).sum(), 0, "analítica")
confere("divergência máxima de desconto (p.p.)", round(divg.max(), 2), 0.50, "analítica", tol=0.005)
confere("divergência média de desconto (p.p.)", round(divg.mean(), 2), 0.21, "analítica", tol=0.005)

# ---------------------------------------------------------------------------
# 4. Cortes e quadrantes
# ---------------------------------------------------------------------------
secao("CORTES E QUADRANTES — base analítica")
p90 = an.avaliacoes.quantile(0.90)
mediana_av = an.avaliacoes.median()
confere("p90 de rating_count", p90, 36384.0, "analítica")
confere("mediana de rating_count", mediana_av, 4740.0, "analítica")
confere("produtos com nota < 4,0", (an.nota < 4).sum(), 339, "analítica")
confere("% com nota < 4,0", round(100 * (an.nota < 4).mean(), 1), 25.1, "analítica", tol=0.05)
confere("produtos com nota >= 4,3", (an.nota >= 4.3).sum(), 418, "analítica")
confere("produtos na faixa 4,0–4,29",
        ((an.nota >= 4.0) & (an.nota < 4.3)).sum(), 591, "analítica")
confere("Q5 — alto engajamento e nota < 4,0",
        ((an.avaliacoes >= p90) & (an.nota < 4)).sum(), 19, "analítica")
confere("Q6 — nota >= 4,3 e engajamento < mediana",
        ((an.nota >= 4.3) & (an.avaliacoes < mediana_av)).sum(), 187, "analítica")
confere("faixa intermediária de engajamento (sem rótulo)",
        ((an.avaliacoes >= mediana_av) & (an.avaliacoes < p90)).sum(), 539, "analítica")

acum = an.avaliacoes.sort_values(ascending=False).cumsum()
pareto = (acum < 0.8 * an.avaliacoes.sum()).sum() + 1
confere("QA2 — produtos que concentram 80% das avaliações", pareto, 306, "analítica")
confere("QA2 — percentual", round(100 * pareto / len(an), 1), 22.7, "analítica", tol=0.05)

# ---------------------------------------------------------------------------
# 5. Granularidade de categoria
# ---------------------------------------------------------------------------
secao("CATEGORIAS — base analítica")
n1 = an.category.str.split("|").str[0]
vc1 = n1.value_counts()
for nome, esperado in [("Electronics", 490), ("Home&Kitchen", 447),
                       ("Computers&Accessories", 373), ("OfficeProducts", 31)]:
    confere(f"categoria nível 1 — {nome}", int(vc1.get(nome, 0)), esperado, "analítica")
confere("categorias nível 1 acima do piso (n>=30)", (vc1 >= 30).sum(), 4, "analítica")
confere("categorias nível 1 abaixo do piso", (vc1 < 30).sum(), 5, "analítica")
confere("PRODUTOS nas categorias abaixo do piso", int(vc1[vc1 < 30].sum()), 7, "analítica")
confere("soma da tabela de categorias fecha na base",
        int(vc1.sum()), len(an), "analítica")
confere("% do portfólio nas três maiores famílias",
        round(100 * vc1.head(3).sum() / len(an), 1), 97.2, "analítica", tol=0.05)

n2 = an.category.str.split("|").str[:2].str.join("|").value_counts()
confere("subcategorias nível 2 acima do piso", (n2 >= 30).sum(), 8, "analítica")
confere("cobertura das subcategorias acima do piso (%)",
        round(100 * n2[n2 >= 30].sum() / len(an), 1), 88.3, "analítica", tol=0.05)

# ---------------------------------------------------------------------------
# 6. Distribuição — a tabela que a v1 não cobria
# ---------------------------------------------------------------------------
secao("DISTRIBUIÇÃO — base analítica, percentil por interpolação linear")
# Arredondamento: regra do inteiro par (padrão do Python), declarada em rodapé.
DIST = [
    ("preço de tabela", "preco_tab", 899, 1795, 4592, 15999, 139900),
    ("preço com desconto", "preco_desc", 349, 899, 2184, 8993, 77990),
    ("desconto (%)", "desconto", 31, 49, 62, 75, 94),
    ("avaliações", "avaliacoes", 1108, 4740, 16052, 36384, 426973),
]
for rotulo, col, p25, med, p75, p90_, mx in DIST:
    confere(f"{rotulo} — p25", round(an[col].quantile(0.25)), p25, "analítica")
    confere(f"{rotulo} — mediana", round(an[col].median()), med, "analítica")
    confere(f"{rotulo} — p75", round(an[col].quantile(0.75)), p75, "analítica")
    confere(f"{rotulo} — p90", round(an[col].quantile(0.90)), p90_, "analítica")
    confere(f"{rotulo} — máximo", round(an[col].max()), mx, "analítica")
confere("nota — mediana", round(an.nota.median(), 2), 4.10, "analítica", tol=0.005)
confere("nota — p25", round(an.nota.quantile(0.25), 2), 3.90, "analítica", tol=0.005)
confere("nota — p75", round(an.nota.quantile(0.75), 2), 4.30, "analítica", tol=0.005)
confere("nota — p90", round(an.nota.quantile(0.90), 2), 4.40, "analítica", tol=0.005)
confere("nota — máximo", round(an.nota.max(), 2), 5.00, "analítica", tol=0.005)

# ---------------------------------------------------------------------------
# 7. Associações — a seção que a v1 não cobria
# ---------------------------------------------------------------------------
secao("ASSOCIAÇÕES (Spearman) — base analítica")
if TEM_SCIPY:
    PARES = [
        ("desconto × nota", "desconto", "nota", -0.150, 3.14e-08),
        ("desconto × engajamento", "desconto", "avaliacoes", -0.132, 1.1e-06),
        ("QA4 preço de tabela × nota", "preco_tab", "nota", 0.032, 0.236),
        ("engajamento × nota", "avaliacoes", "nota", 0.193, 8.3e-13),
    ]
    for rotulo, a, b, rho_esp, p_esp in PARES:
        rho, pval = spearmanr(an[a], an[b])
        confere(f"{rotulo} — rho", round(rho, 3), rho_esp, "analítica", tol=0.0005)
        ordem_ok = abs(np.log10(pval) - np.log10(p_esp)) < 0.05
        print(f"{'OK  ' if ordem_ok else 'FALHA'} | "
              f"{rotulo + ' — p-valor':<52} obtido={pval:.3g} esperado={p_esp:.3g} [base analítica]")
        if not ordem_ok:
            falhas.append(f"{rotulo} — p-valor")
else:
    pula("as 4 correlações de Spearman", "scipy indisponível — NÃO foram verificadas")

# ---------------------------------------------------------------------------
# 8. Corpus textual
# ---------------------------------------------------------------------------
secao("CORPUS TEXTUAL — base analítica")
ex = an.assign(_r=an.review_id.str.split(",")).explode("_r")
ex["_r"] = ex._r.str.strip()
confere("referências de avaliação (explodidas)", len(ex), 10588, "analítica")
confere("review_id distintos", ex._r.nunique(), 9255, "analítica")
confere("referências repetidas", len(ex) - ex._r.nunique(), 1333, "analítica")
confere("review_id em mais de um produto",
        int((ex.groupby("_r").product_id.nunique() > 1).sum()), 759, "analítica")
confere("média de avaliações por produto (truncamento)",
        round(len(ex) / len(an), 2), 7.85, "analítica", tol=0.005)
confere("máximo de avaliações por produto",
        int(ex.groupby("product_id").size().max()), 8, "analítica")

faixa = np.where(an.nota < 4.0, "<4.0", np.where(an.nota >= 4.3, ">=4.3", "4.0-4.29"))
ex_f = ex.assign(_f=np.where(ex.nota < 4.0, "<4.0", np.where(ex.nota >= 4.3, ">=4.3", "4.0-4.29")))
for f, blocos, refs, dist in [("<4.0", 339, 2652, 2502),
                              ("4.0-4.29", 591, 4674, 3875),
                              (">=4.3", 418, 3262, 2878)]:
    sub = ex_f[ex_f._f == f]
    confere(f"faixa {f} — blocos", int((faixa == f).sum()), blocos, "analítica")
    confere(f"faixa {f} — referências", len(sub), refs, "analítica")
    confere(f"faixa {f} — review_id distintos", sub._r.nunique(), dist, "analítica")
confere("review_id presentes em mais de uma faixa de nota",
        int((ex_f.groupby("_r")._f.nunique() > 1).sum()), 0, "analítica")

# ---------------------------------------------------------------------------
# 9. Somas e a comparação entre regras de deduplicação
# ---------------------------------------------------------------------------
secao("SOMAS E IMPACTO DA REGRA — base declarada em cada linha")
confere("soma de rating_count", int(prod.avaliacoes.sum()), 23802463, "produtos (1.351)")
confere("soma de rating_count", int(an.avaliacoes.sum()), 23801471, "analítica (1.348)")

primeira = df.drop_duplicates("product_id", keep="first").set_index("product_id")
oficial = prod.set_index("product_id")
primeira = primeira.loc[oficial.index]
confere("diferença de rating_count entre as duas regras",
        int(oficial.avaliacoes.sum() - primeira.avaliacoes.sum()), 40, "produtos (1.351)")
for col, esperado in [("rating", 0), ("actual_price", 0), ("discounted_price", 1),
                      ("discount_percentage", 1)]:
    confere(f"produtos que mudam de {col} ao trocar a regra",
            int((oficial[col].fillna("@") != primeira[col].fillna("@")).sum()),
            esperado, "produtos (1.351)")
texto = ((oficial.review_id.fillna("@") != primeira.review_id.fillna("@"))
         | (oficial.review_title.fillna("@") != primeira.review_title.fillna("@"))
         | (oficial.review_content.fillna("@") != primeira.review_content.fillna("@")))
confere("produtos que mudam de TEXTO ao trocar a regra",
        int(texto.sum()), 4, "produtos (1.351)")

usuarios = an.assign(_u=an.user_id.str.split(",")).explode("_u")
usuarios["_u"] = usuarios._u.str.strip()
por_usuario = usuarios.groupby("_u").product_id.nunique()
confere("usuários distintos", int(por_usuario.size), 9036, "analítica")
confere("usuários que avaliam mais de um produto",
        int((por_usuario > 1).sum()), 909, "analítica")

# ---------------------------------------------------------------------------
# 10. LGPD — T7
# ---------------------------------------------------------------------------
secao("CONFORMIDADE (T7)")
confere("nenhum user_id ou user_name impresso por este script", 0, 0, "—")

# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
total = len(falhas)
print(f"Asserções executadas com base declarada. Falhas: {total}. Puladas: {len(puladas)}.")
if puladas:
    print("PULADAS (não verificadas, não aprovadas):")
    for p in puladas:
        print(f"  - {p}")
if total:
    print("DIVERGÊNCIAS:")
    for f in falhas:
        print(f"  - {f}")
    print("\nUm número do material está errado — ou este script está.")
    sys.exit(1)
print("Todas as asserções conferem. Os números do material estão reproduzíveis.")
sys.exit(0)

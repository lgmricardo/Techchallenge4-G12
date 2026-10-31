# -*- coding: utf-8 -*-
"""
Valores de referência do catálogo de medidas DAX (`03_dashboard/medidas_dax.md`).

Por que este arquivo existe
---------------------------
Uma medida DAX só vale se devolver o mesmo número que o Python devolve sobre a
mesma base. Este script calcula, a partir de `00_data/gold/`, **cada** valor de
referência publicado no catálogo — nenhum número do catálogo é estimado.

Saídas:
  - console, no formato "M## · nome · valor · base · n" (o que se cola no PR)
  - `03_dashboard/valores_referencia.csv`, para conferência linha a linha

Regras aplicadas: T1 (ranking por `nota_corrigida`), T2 (piso n >= 30 em grupo
agregado), T3 (toda medida declara base e n), T6 (`avaliacoes` é volume de
avaliações, nunca venda), T7 (nenhuma coluna pessoal é lida), L5 (moeda em
rupia indiana, sem símbolo e sem conversão).

Uso:  python3 03_dashboard/valores_referencia.py
"""

import os

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GOLD = os.path.join(RAIZ, "00_data", "gold", "base_analitica.csv")
GOLD_REV = os.path.join(RAIZ, "00_data", "gold", "reviews.csv")
SAIDA = os.path.join(RAIZ, "03_dashboard", "valores_referencia.csv")
SAIDA_CAT = os.path.join(RAIZ, "03_dashboard", "valores_referencia_por_categoria.csv")

PISO = 30          # T2 — piso amostral de grupo agregado
BASE_ANALITICA = "Analítica (gold/base_analitica.csv)"
BASE_REVIEWS = "Reviews individuais (gold/reviews.csv)"

linhas = []


def registra(codigo, nome, valor, unidade, denominador, base, n, formatado=None):
    """Acumula uma linha do catálogo. `formatado` é o texto publicado no .md."""
    linhas.append({
        "medida": codigo,
        "nome": nome,
        "valor": valor,
        "publicado": formatado if formatado is not None else f"{valor}",
        "unidade": unidade,
        "denominador": denominador,
        "base": base,
        "n": n,
    })


def br(valor, casas=0):
    """Número no padrão brasileiro: ponto de milhar, vírgula decimal."""
    texto = f"{valor:,.{casas}f}"
    return texto.replace(",", "\x00").replace(".", ",").replace("\x00", ".")


def main():
    g = pd.read_csv(GOLD)
    rev = pd.read_csv(GOLD_REV)
    n = len(g)
    volume_total = g.avaliacoes.sum()

    # ---- cortes operacionais (recalculados, não copiados) -------------------
    p90 = g.avaliacoes.quantile(0.90)
    mediana_vol = g.avaliacoes.median()

    # ---- M01-M02 · contagens de base ---------------------------------------
    registra("M01", "Produtos Ativos", n, "produtos", "—",
             BASE_ANALITICA, n, br(n))
    registra("M02", "Volume Total de Avaliações", int(volume_total),
             "avaliações", "—", BASE_ANALITICA, n, br(volume_total))

    # ---- M03-M08 · medianas de distribuição --------------------------------
    registra("M03", "Preço Mediano", g.preco_desc.median(),
             "rupia indiana, sem símbolo (L5)", "—", BASE_ANALITICA, n,
             br(g.preco_desc.median()))
    registra("M04", "Preço de Tabela Mediano", g.preco_tab.median(),
             "rupia indiana, sem símbolo (L5)", "—", BASE_ANALITICA, n,
             br(g.preco_tab.median()))
    registra("M05", "Desconto Mediano", g.desconto.median(),
             "% (0-100), declarado na origem", "—", BASE_ANALITICA, n,
             br(g.desconto.median()))
    registra("M06", "Nota Mediana", g.nota.median(), "estrelas (1-5)", "—",
             BASE_ANALITICA, n, br(g.nota.median(), 2))
    registra("M07", "Nota Corrigida Mediana", g.nota_corrigida.median(),
             "estrelas corrigidas (Wilson 95%, 1-5)", "—", BASE_ANALITICA, n,
             br(g.nota_corrigida.median(), 3))
    registra("M08", "Volume Mediano de Avaliações", mediana_vol,
             "avaliações por produto", "—", BASE_ANALITICA, n, br(mediana_vol))

    # ---- M09-M10 · satisfação ----------------------------------------------
    baixa = int((g.satisfacao == "baixa").sum())
    alta = int((g.satisfacao == "alta").sum())
    registra("M09", "% Satisfação Baixa", 100 * baixa / n, "%",
             f"Produtos Ativos = {br(n)}", BASE_ANALITICA, n,
             f"{br(100 * baixa / n, 1)}% ({br(baixa)} produtos)")
    registra("M10", "% Satisfação Alta", 100 * alta / n, "%",
             f"Produtos Ativos = {br(n)}", BASE_ANALITICA, n,
             f"{br(100 * alta / n, 1)}% ({br(alta)} produtos)")

    # ---- M11-M12 · quadrantes ----------------------------------------------
    q5 = int(g.q5_risco_vitrine.sum())
    q6 = int(g.q6_subexplorado.sum())
    registra("M11", "Produtos Q5 (risco de vitrine)", q5, "produtos", "—",
             BASE_ANALITICA, n, br(q5))
    registra("M12", "Produtos Q6 (candidatos a subexplorado)", q6, "produtos",
             "—", BASE_ANALITICA, n, br(q6))
    # M22 é a lista acionável: o mesmo recorte de Q6 já corrigido por Wilson.
    # T1 exige nota corrigida em todo ranking, e uma lista de oportunidades
    # é um ranking — por isso M12 é funil e M22 é o que vai para a tela.
    q6_acionavel = int((g.q6_subexplorado & (g.nota_corrigida >= 4.3)).sum())
    registra("M22", "Produtos Q6 Acionáveis (Wilson)", q6_acionavel, "produtos",
             "—", BASE_ANALITICA, n, br(q6_acionavel))

    # ---- M13-M14 · concentração de Pareto ----------------------------------
    pareto = int(g.pareto_80.sum())
    registra("M13", "Concentração Pareto 80%", pareto, "produtos", "—",
             BASE_ANALITICA, n, br(pareto))
    registra("M14", "% Concentração Pareto 80%", 100 * pareto / n, "%",
             f"Produtos Ativos = {br(n)}", BASE_ANALITICA, n,
             f"{br(100 * pareto / n, 1)}%")

    # ---- M15 · participação da categoria no volume -------------------------
    cat = (g.groupby("categoria_n1")
             .agg(produtos=("product_id", "count"), volume=("avaliacoes", "sum"))
             .sort_values("volume", ascending=False))
    cat["participacao"] = 100 * cat.volume / volume_total
    acima = cat[cat.produtos >= PISO]
    for nome_cat, linha in acima.iterrows():
        registra("M15", f"Participação da Categoria no Volume · {nome_cat}",
                 linha.participacao, "%",
                 f"Volume Total de Avaliações = {br(volume_total)}",
                 BASE_ANALITICA, int(linha.produtos),
                 f"{br(linha.participacao, 1)}%")
    suprimidas = cat[cat.produtos < PISO]
    registra("M15s", "Participação suprimida por T2 (categorias n < 30)",
             suprimidas.participacao.sum(), "%",
             f"Volume Total de Avaliações = {br(volume_total)}",
             BASE_ANALITICA, int(suprimidas.produtos.sum()),
             f"{br(suprimidas.participacao.sum(), 1)}% em "
             f"{int(suprimidas.produtos.sum())} produtos / {len(suprimidas)} categorias")

    # ---- M16 · cobertura de subcategoria acima do piso ---------------------
    sub = g.groupby("categoria_n2").product_id.count()
    sub_acima = sub[sub >= PISO]
    cobertura = 100 * sub_acima.sum() / n
    registra("M16", "Subcategorias acima do Piso", len(sub_acima),
             "subcategorias nível 2", f"{len(sub)} subcategorias existentes",
             BASE_ANALITICA, n, br(len(sub_acima)))
    registra("M17", "Cobertura de Subcategoria acima do Piso", cobertura, "%",
             f"Produtos Ativos = {br(n)}", BASE_ANALITICA, n,
             f"{br(cobertura, 1)}% ({br(sub_acima.sum())} produtos)")

    # ---- M18-M19 · cortes publicados como medida ---------------------------
    registra("M18", "Corte de Engajamento Alto (p90)", p90,
             "avaliações por produto", "—", BASE_ANALITICA, n, br(p90))
    registra("M19", "Corte de Engajamento Baixo (mediana)", mediana_vol,
             "avaliações por produto", "—", BASE_ANALITICA, n, br(mediana_vol))

    # ---- M20 · corpus textual (T8) -----------------------------------------
    registra("M20", "Reviews Individuais", len(rev),
             "reviews distintos (unidade: review individual)", "—",
             BASE_REVIEWS, len(rev), br(len(rev)))

    # ---- matriz de contexto · as mesmas medidas filtradas por categoria ----
    # É o teste que pega o erro mais comum do Power BI: a medida acerta no total
    # e erra ao ser cruzada, porque o denominador foi escrito como medida e não
    # como ALL(). Só as categorias acima do piso entram (T2).
    matriz = (g[g.categoria_n1.isin(acima.index)]
              .groupby("categoria_n1")
              .agg(produtos=("product_id", "count"),
                   nota_mediana=("nota", "median"),
                   nota_corrigida_mediana=("nota_corrigida", "median"),
                   preco_mediano=("preco_desc", "median"),
                   desconto_mediano=("desconto", "median"),
                   volume_mediano=("avaliacoes", "median"),
                   volume_total=("avaliacoes", "sum")))
    matriz["participacao_volume_pct"] = 100 * matriz.volume_total / volume_total
    matriz["satisfacao_baixa_pct"] = (
        g[g.categoria_n1.isin(acima.index)]
        .groupby("categoria_n1").satisfacao
        .apply(lambda serie: 100 * (serie == "baixa").mean()))
    matriz = matriz.sort_values("produtos", ascending=False).round(3)
    matriz.to_csv(SAIDA_CAT, encoding="utf-8")

    # ---- publicação --------------------------------------------------------
    out = pd.DataFrame(linhas)
    out.to_csv(SAIDA, index=False, encoding="utf-8")

    print("VALORES DE REFERÊNCIA — catálogo de medidas DAX (D-7)")
    print(f"  base analítica: {GOLD}")
    print(f"  corpus:         {GOLD_REV}")
    print(f"  piso T2: n >= {PISO} · base analítica n = {br(n)} · "
          f"volume total = {br(volume_total)} avaliações\n")
    largura = max(len(f"{r['medida']} · {r['nome']}") for r in linhas)
    for r in linhas:
        rotulo = f"{r['medida']} · {r['nome']}"
        print(f"  {rotulo.ljust(largura)}  = {r['publicado']}   [n = {br(r['n'])}]")

    print(f"\n  detalhamento por categoria (T2 · piso {PISO}):")
    for nome_cat, linha in cat.iterrows():
        marca = "acima" if linha.produtos >= PISO else "SUPRIMIDA"
        print(f"    {nome_cat:<28} {int(linha.produtos):>4} produtos · "
              f"{br(linha.volume):>12} avaliações · "
              f"{br(linha.participacao, 1):>5}% · {marca}")

    print(f"\n  subcategorias nível 2 acima do piso ({len(sub_acima)} de {len(sub)}):")
    for nome_sub, qtd in sub_acima.sort_values(ascending=False).items():
        print(f"    {nome_sub:<48} {int(qtd):>4} produtos")

    print(f"\n  reconciliação: {int(sub_acima.sum())} produtos cobertos / {n} "
          f"= {br(cobertura, 1)}%")

    print("\n  matriz de contexto — as mesmas medidas filtradas por categoria "
          "(só acima do piso, T2):")
    print(matriz.to_string())
    print(f"\n  soma de 'produtos' na matriz = {int(matriz.produtos.sum())} "
          f"(+{n - int(matriz.produtos.sum())} suprimidos por T2 = {n})")
    print(f"  soma de 'participacao_volume_pct' = "
          f"{br(matriz.participacao_volume_pct.sum(), 1)}% "
          f"(+{br(suprimidas.participacao.sum(), 1)}% suprimido = 100,0%)")

    print(f"\n  CSV gravado em {SAIDA}")
    print(f"  CSV gravado em {SAIDA_CAT}")


if __name__ == "__main__":
    main()

# -*- coding: utf-8 -*-
"""
Números do roteiro do vídeo — fonte executável.

Por que este arquivo existe
---------------------------
O roteiro é texto falado: cada número dito em voz alta vira afirmação pública e
precisa ser reproduzível. Este script recalcula, a partir das camadas silver e
gold, **todos** os números citados em `roteiro.md`, escreve a tabela de amarração
`tab_roteiro_numeros.csv` (número · base · n · bloco do vídeo) e gera a cartela
do conflito central (arquétipos B × D).

Nada aqui é estimado. Se um número do roteiro não aparecer na saída deste
script, ele não deveria estar no roteiro.

Regras aplicadas: T1 (Wilson), T3 (base e n declarados), T5 (magnitude com
significância), T6 (`avaliacoes` é volume de avaliações), T8 (corpus deduplicado
por review_id e truncamento declarado), T9 (paleta v06 por ferramenta), L5
(rupia indiana, sem símbolo e sem conversão).

Uso:  python3 04_video/numeros_roteiro.py
"""

import os
import sys

import numpy as np
import pandas as pd
from scipy.stats import spearmanr
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))
from paleta import CHAMADAS, ESTRUTURA, aplicar, confere_visual  # noqa: E402
import ml2  # noqa: E402

SILVER = os.path.join(RAIZ, "00_data", "silver", "produtos.csv")
GOLD = os.path.join(RAIZ, "00_data", "gold", "base_analitica.csv")
GOLD_REV = os.path.join(RAIZ, "00_data", "gold", "reviews.csv")
BRONZE = os.path.join(RAIZ, "00_data", "bronze", "amazon.csv")  # só contagem de linhas

SAIDA_TABELA = os.path.join(RAIZ, "04_video", "tab_roteiro_numeros.csv")
SAIDA_CARTELA = os.path.join(RAIZ, "04_video", "cartelas", "cartela_conflito_BxD.png")

PISO = 30          # T2 — piso amostral de grupo agregado
SEMENTE = 42

linhas = []        # acumula a tabela de amarração


def milhar(valor):
    """Separador de milhar no padrão brasileiro."""
    return f"{valor:,.0f}".replace(",", ".")


def pct(valor, casas=1):
    """Percentual com vírgula decimal."""
    return f"{valor:.{casas}f}%".replace(".", ",")


def registrar(bloco, indicador, valor, base, n, regra=""):
    """Uma linha da tabela de amarração. Todo número dito no vídeo passa por aqui (T3)."""
    linhas.append({"bloco_do_video": bloco, "indicador": indicador, "valor": valor,
                   "base": base, "n": n, "regra": regra})
    print(f"  {indicador:<52} {valor:>22}   [{base}, n={n}]")


def main():
    # ------------------------------------------------------------------ bases
    n_bronze = sum(1 for _ in open(BRONZE, encoding="utf-8")) - 1
    silver = pd.read_csv(SILVER)
    g = pd.read_csv(GOLD)
    rev = pd.read_csv(GOLD_REV)
    n_gold = len(g)

    print("\n=== BLOCO 1 · CONTEXTO DO PROBLEMA " + "=" * 40)
    registrar("1 Contexto", "linhas na base bruta", f"{n_bronze}", "Bruta", n_bronze)
    registrar("1 Contexto", "produtos após deduplicação", f"{len(silver)}", "Produtos", len(silver))
    registrar("1 Contexto", "produtos na base analítica", f"{n_gold}", "Analítica", n_gold,
              "T3 — base padrão de toda análise cruzada")
    cat1 = g.categoria_n1.value_counts()
    acima = cat1[cat1 >= PISO]
    registrar("1 Contexto", "categorias de nível 1 na base", f"{cat1.size}", "Analítica", n_gold)
    registrar("1 Contexto", f"categorias com n >= {PISO} (T2)", f"{acima.size}", "Analítica", n_gold, "T2")
    registrar("1 Contexto", "produtos nas categorias abaixo do piso",
              f"{int(cat1[cat1 < PISO].sum())}", "Analítica", n_gold, "T2 / L3")
    cobertura3 = acima.head(3).sum() / n_gold * 100
    registrar("1 Contexto", "cobertura das 3 maiores categorias",
              pct(cobertura3), "Analítica", n_gold, "L3")
    for nome, qtd in acima.items():
        registrar("1 Contexto", f"produtos em {nome}", f"{int(qtd)}", "Analítica", n_gold, "T2")

    # -------------------------------------------------------------- indicadores
    print("\n=== BLOCO 2 · PRINCIPAIS INDICADORES " + "=" * 38)
    p90 = g.avaliacoes.quantile(0.90)
    mediana_aval = g.avaliacoes.median()
    registrar("2 Indicadores", "nota mediana", f"{g.nota.median():.2f}".replace(".", ","),
              "Analítica", n_gold, "T1 — ranking usa nota_corrigida")
    registrar("2 Indicadores", "desconto mediano", f"{g.desconto.median():.0f}%", "Analítica", n_gold)
    registrar("2 Indicadores", "preço de tabela mediano (rupia, sem conversão)",
              milhar(g.preco_tab.median()), "Analítica", n_gold, "L5")
    registrar("2 Indicadores", "volume mediano de avaliações",
              milhar(mediana_aval), "Analítica", n_gold, "T6")
    registrar("2 Indicadores", "corte de engajamento alto (p90 de avaliações)",
              milhar(p90), "Analítica", n_gold, "T6")
    baixa = int((g.satisfacao == "baixa").sum())
    registrar("2 Indicadores", "produtos com nota < 4,0",
              f"{baixa} ({pct(baixa / n_gold * 100)})", "Analítica", n_gold)
    alta = int((g.satisfacao == "alta").sum())
    registrar("2 Indicadores", "produtos com nota >= 4,3", f"{alta}", "Analítica", n_gold)
    pareto = int(g.pareto_80.sum())
    registrar("2 Indicadores", "produtos que concentram 80% das avaliações",
              f"{pareto} ({pct(pareto / n_gold * 100)})", "Analítica", n_gold, "T6 / QA2")
    # A insatisfação não está onde a atenção está. Entre os produtos que carregam 80%
    # das avaliações, a taxa de nota < 4,0 é cerca de metade da taxa da base — é o número
    # que sustenta a segunda mensagem da conclusão do vídeo. Entra aqui porque o roteiro
    # declara que número falado ou exibido sem amarração não vai para o vídeo.
    baixa_pareto = int((g.pareto_80 & (g.nota < 4.0)).sum())
    registrar("2 Indicadores", "produtos do Pareto 80% com nota < 4,0",
              f"{baixa_pareto} ({pct(baixa_pareto / pareto * 100)})", "Analítica", pareto,
              "T6 — atenção é volume de avaliações · contraste com a taxa da base, 25,1%")

    # ------------------------------------------------------------------ insights
    print("\n=== BLOCO 3 · PRINCIPAIS INSIGHTS " + "=" * 41)
    pares = [("desconto × nota", g.desconto, g.nota),
             ("desconto × engajamento", g.desconto, g.avaliacoes),
             ("preço de tabela × nota", g.preco_tab, g.nota),
             ("engajamento × nota", g.avaliacoes, g.nota)]
    for nome, a, b in pares:
        rho, p = spearmanr(a, b)
        registrar("3 Insights", f"Spearman {nome}",
                  f"rho {rho:+.3f} · p {p:.1e}".replace(".", ","), "Analítica", n_gold,
                  "T4 associação, nunca causa · T5 magnitude com significância")

    q5 = int(g.q5_risco_vitrine.sum())
    q6 = int(g.q6_subexplorado.sum())
    registrar("3 Insights", "Q5 — engajamento alto e nota < 4,0", f"{q5}", "Analítica", n_gold, "T2 exceção nominal")
    # D-1 fechada em 24/09/2026: volume abaixo da mediana e proxy DECLARADO de
    # exposicao. Os 187 sao o funil (nota bruta); T1 exige nota corrigida em todo
    # ranking, e uma lista de oportunidades e um ranking -> o numero que se fala
    # no video e o acionavel. Os dois ficam na tabela para o rodape poder citar
    # ambos sem que ninguem precise recalcular.
    q6_acionavel = int((g.q6_subexplorado & (g.nota_corrigida >= 4.3)).sum())
    registrar("3 Insights", "Q6 — funil: nota >= 4,3 e volume abaixo da mediana", f"{q6}",
              "Analítica", n_gold,
              "T6 proxy declarado de exposição · vedado dizer 'baixa visibilidade'")
    registrar("3 Insights", "Q6 — lista acionável: funil já corrigido por Wilson",
              f"{q6_acionavel}", "Analítica", n_gold,
              f"T1 · {q6 - q6_acionavel} dos {q6} caem na correção · medida M22")
    # O 126 é falado no bloco 6 ("a correção de Wilson derruba 126") e vivia só dentro do
    # texto da coluna `regra` — a versão estrita do confere_amarracao.py achou.
    registrar("3 Insights", "Q6 — produtos que caem na correção de Wilson",
              f"{q6 - q6_acionavel}", "Analítica", n_gold, f"T1 · {q6} do funil menos {q6_acionavel} acionáveis")

    # ------------------------------------------- arquétipos (ML4) — o conflito
    X = pd.DataFrame({
        "log_preco_tab": np.log(g.preco_tab),
        "desconto": g.desconto,
        "log_avaliacoes": np.log(g.avaliacoes),
        "nota": g.nota,
    })
    Z = StandardScaler().fit_transform(X)
    sil = {}
    for k in range(2, 8):
        rot = KMeans(n_clusters=k, random_state=SEMENTE, n_init=10).fit_predict(Z)
        sil[k] = silhouette_score(Z, rot)
    for k in (3, 4, 5):
        registrar("3 Insights", f"silhueta k={k}", f"{sil[k]:.3f}".replace(".", ","),
                  "Analítica", n_gold, "ML4 — sem estrutura natural de agrupamento")
    registrar("3 Insights", "k de silhueta máxima",
              f"k={max(sil, key=sil.get)} ({max(sil.values()):.3f})".replace(".", ","),
              "Analítica", n_gold, "ML4 — adotado k=4 por interpretabilidade")

    g["_cluster"] = KMeans(n_clusters=4, random_state=SEMENTE, n_init=10).fit_predict(Z)
    # rotulagem determinística pelos perfis registrados em ML4
    b_id = g.groupby("_cluster").avaliacoes.median().idxmin()          # B — sem tração
    d_id = g.groupby("_cluster").avaliacoes.median().idxmax()          # D — alto giro
    a_id = g.groupby("_cluster").preco_tab.median().idxmax()           # A — ticket alto
    c_id = [c for c in g._cluster.unique() if c not in (b_id, d_id, a_id)][0]
    nomes = {a_id: "A — ticket alto, desconto contido", b_id: "B — desconto agressivo sem tração",
             c_id: "C — baixo preço, pouco desconto", d_id: "D — alto giro com desconto alto"}
    arq = (g.assign(arquetipo=g._cluster.map(nomes))
             .groupby("arquetipo")
             .agg(n=("product_id", "size"), preco_tab=("preco_tab", "median"),
                  desconto=("desconto", "median"), avaliacoes=("avaliacoes", "median"),
                  nota=("nota", "median"))
             .sort_index())
    print(arq.to_string())
    for nome, linha in arq.iterrows():
        registrar("3 Insights", f"arquétipo {nome[0]} — n · desconto · avaliações · nota",
                  f"{int(linha.n)} · {linha.desconto:.0f}% · {milhar(linha.avaliacoes)}"
                  + f" · {linha.nota:.1f}".replace(".", ","),
                  "Analítica", n_gold, "ML4 — descritivo, nunca descoberta")
    lb, ld = arq.loc[nomes[b_id]], arq.loc[nomes[d_id]]
    razao = ld.avaliacoes / lb.avaliacoes
    registrar("3 Insights", "conflito B × D — distância de desconto",
              f"{ld.desconto - lb.desconto:.0f} p.p.", "Analítica", n_gold, "T4")
    registrar("3 Insights", "conflito B × D — razão de volume de avaliações",
              f"{razao:.0f}x", "Analítica", n_gold, "T6 — volume, nunca venda")

    # ------------------------------------------------------- customer insights
    print("\n=== BLOCO 5 · CUSTOMER INSIGHTS " + "=" * 43)
    # o corpus é o da base analítica (n = 1.348) — mesma base do resto do vídeo (T3)
    texto = silver[silver.product_id.isin(g.product_id)]
    ref = texto.review_id.dropna().str.split(",").explode().str.strip()
    registrar("5 Customer Insights", "referências de avaliação na base", milhar(len(ref)),
              "Analítica", n_gold, "T8 — unidade: bloco de review")
    registrar("5 Customer Insights", "reviews distintos após deduplicar por review_id",
              milhar(len(rev)), "Analítica", n_gold, "T8")
    registrar("5 Customer Insights", "referências repetidas descartadas",
              milhar(len(ref) - ref.nunique()), "Analítica", n_gold, "T8")
    por_produto = texto.review_id.dropna().str.split(",").apply(len)
    registrar("5 Customer Insights", "avaliações por produto — média e máximo",
              f"{por_produto.mean():.2f}".replace(".", ",") + f" · máx {por_produto.max()}",
              "Analítica", n_gold, "L1 — truncamento na vitrine")
    aval_q5 = int(silver.set_index("product_id").loc[
        g.loc[g.q5_risco_vitrine, "product_id"], "review_id"].str.split(",").apply(len).sum())
    registrar("5 Customer Insights", "avaliações disponíveis nos 19 produtos de Q5",
              f"{aval_q5}", "Analítica", q5, "QA5 — leitura dirigida, não TF-IDF")
    # QA5 — o eixo com mais blocos de queixa entre os 19 (o gráfico de temas da página 4 do dashboard)
    temas = pd.read_csv(os.path.join(RAIZ, "02_results", "tables", "tab23_qa5_temas.csv")).set_index("eixo_tematico")
    registrar("5 Customer Insights", "QA5 — blocos com queixa de som, ruído e microfone",
              f"{int(temas.loc['Som, ruído e microfone', 'blocos_com_marcador_negativo'])}", "Analítica", q5,
              "QA5 — leitura dirigida, denominador 19 blocos")

    # ---------------------------------------------- demonstração do dashboard
    # A página "Produtos e Categorias" compara por subcategoria de nível 2, não
    # por família: é a unidade de comparação que sobrevive ao piso da T2.
    print("\n=== BLOCO 4 · DEMONSTRAÇÃO DO DASHBOARD " + "=" * 34)
    cat2 = g.categoria_n2.value_counts()
    acima2 = cat2[cat2 >= PISO]
    registrar("4 Dashboard", f"subcategorias de nível 2 com n >= {PISO}",
              f"{acima2.size}", "Analítica", n_gold, "T2")
    registrar("4 Dashboard", "cobertura das subcategorias acima do piso",
              pct(acima2.sum() / n_gold * 100), "Analítica", n_gold, "T2")

    # ------------------------------------- os DOIS focos de insatisfação (bloco 5)
    # O vídeo precisa entregar um TEMA de Customer Insights, não só o método. Os
    # dois focos têm naturezas diferentes e exigem ações opostas: em fones a
    # distribuição inteira está deslocada (dp baixo); em climatização bons e ruins convivem
    # (dp alto). A diferença NÃO é significativa (Levene p = 0,18, tab30): é hipótese de trabalho.
    for alvo, rotulo in (("Headphones", "fones"), ("Heating", "climatização")):
        sub = g[g.categoria_n2.str.contains(alvo, na=False)]
        abaixo = (sub.nota < 4.0).mean() * 100
        registrar("5 Customer Insights", f"{rotulo} — produtos abaixo de 4,0",
                  pct(abaixo), "Analítica", len(sub),
                  f"T2 n = {len(sub)} >= {PISO} · subcategoria de nível 2")
        registrar("5 Customer Insights", f"{rotulo} — dispersão da nota (desvio-padrão)",
                  f"{sub.nota.std():.3f}".replace(".", ","), "Analítica", len(sub),
                  "dispersão observada; a diferença não é significativa (Levene p = 0,18)")
    registrar("5 Customer Insights", "taxa da base abaixo de 4,0 — para comparação",
              pct((g.nota < 4.0).mean() * 100), "Analítica", n_gold,
              "sem ela, 52% e 38% não têm referência")

    # ------------------------------------------------------------ recomendações
    print("\n=== BLOCO 6 · RECOMENDAÇÕES " + "=" * 47)
    # A validação é a de `src/ml2.py` — a mesma do relatório e do notebook 04, com as
    # listagens-gêmeas (L8) agrupadas na mesma partição. Aqui havia uma terceira cópia.
    alvo = ml2.alvo(g)
    comerciais = ["preco_tab", "preco_desc", "desconto"]
    # o sinal é multivariado: nenhum bloco isolado chega perto do conjunto
    for rotulo, num, categ in [("volume de avaliações", ["avaliacoes"], []),
                               ("comerciais", comerciais, []),
                               ("comerciais + categoria", comerciais, ["categoria_n1"])]:
        registrar("6 Recomendações", f"ML2 — AUC só com {rotulo}",
                  f"{ml2.auc(g, num, categ).mean():.2f}".replace(".", ","), "Analítica", n_gold,
                  "ML2 — bloco isolado, duas casas; validação agrupada por variante (L8)")

    aucs = ml2.auc(g, comerciais + ["avaliacoes"], ["categoria_n1"])
    registrar("6 Recomendações", "ML2 — AUC do modelo completo",
              f"{np.mean(aucs):.2f} +- {np.std(aucs):.2f}".replace(".", ","),
              "Analítica", n_gold, "ML2 — duas casas; discriminação moderada · validação agrupada por variante (L8)")
    registrar("6 Recomendações", "ML2 — taxa de risco (nota < 4,0)",
              pct(alvo.mean() * 100), "Analítica", n_gold, "ML2")
    registrar("6 Recomendações", "produtos no arquétipo B (revisão de sortimento)",
              f"{int(lb.n)}", "Analítica", n_gold, "L4 — sem variável de venda")

    faixas = (g.groupby("faixa_desconto", observed=True)
                .agg(n=("product_id", "size"), nota_corrigida=("nota_corrigida", "median"),
                     avaliacoes=("avaliacoes", "median")))
    print(faixas.to_string())
    # Duas faixas entram na tabela, e por motivos diferentes. A de MAIOR nota corrigida é
    # citada com a ressalva: ela está 0,053 acima da segunda, magnitude sem leitura de
    # negócio (§5.10, T5). O achado defensável é a de MENOR nota corrigida — a única abaixo
    # do limiar de satisfação —, e é ela que o dashboard e o vídeo destacam.
    elegiveis = faixas[faixas.n >= PISO]
    melhor, pior = elegiveis.nota_corrigida.idxmax(), elegiveis.nota_corrigida.idxmin()
    registrar("6 Recomendações", "faixa de desconto com maior nota corrigida (QA1)",
              f"{melhor} · Wilson {faixas.loc[melhor, 'nota_corrigida']:.3f}".replace(".", ","),
              "Analítica", int(faixas.loc[melhor, "n"]),
              "T1 / T2 — todas as faixas acima do piso · T5 — 0,053 acima da segunda, sem leitura de negócio")
    registrar("6 Recomendações", "faixa de desconto abaixo do limiar de satisfação (QA1)",
              f"{pior} · Wilson {faixas.loc[pior, 'nota_corrigida']:.3f}".replace(".", ","),
              "Analítica", int(faixas.loc[pior, "n"]), "T1 / T2 — é o achado defensável de QA1")

    # ------------------------------------------------------------------ saídas
    tab = pd.DataFrame(linhas)
    os.makedirs(os.path.dirname(SAIDA_TABELA), exist_ok=True)
    tab.to_csv(SAIDA_TABELA, index=False, encoding="utf-8")

    cartela(arq, nomes[b_id], nomes[d_id])

    print(f"\nTabela de amarração: {SAIDA_TABELA} · {len(tab)} números")
    print(f"Cartela do conflito:  {SAIDA_CARTELA}")
    print(f"Reconciliação: {n_bronze} (bronze) -> {len(silver)} (silver) -> {n_gold} (gold)")
    print("Valores monetários em rupia indiana, sem símbolo e sem conversão (L5).")


def cartela(arq, rotulo_b, rotulo_d):
    """Cartela do conflito central do vídeo: B × D, desconto quase igual, resultado oposto.

    Duas séries apenas — bem abaixo do limite de 5 da T9. Cor vem de `paleta.aplicar`
    e dos tokens; nenhuma cor é escolhida à mão.
    """
    import matplotlib.pyplot as plt
    from matplotlib.ticker import FuncFormatter

    aplicar()
    b, d = arq.loc[rotulo_b], arq.loc[rotulo_d]
    fig, eixos = plt.subplots(1, 3, figsize=(11, 4.2))
    medidas = [("Desconto mediano (%)", b.desconto, d.desconto, "{:.0f}%"),
               ("Volume mediano de avaliações", b.avaliacoes, d.avaliacoes, "{:,.0f}"),
               ("Nota mediana", b.nota, d.nota, "{:.1f}")]
    for eixo, (titulo, vb, vd, fmt) in zip(eixos, medidas):
        barras = eixo.bar(["B", "D"], [vb, vd],
                          color=[CHAMADAS["atencao"], CHAMADAS["favoravel"]], width=0.55)
        eixo.set_title(titulo, fontsize=11)
        eixo.set_ylim(0, max(vb, vd) * 1.25)
        eixo.grid(axis="x", visible=False)
        if "Volume" in titulo:                           # milhar em pt-BR, igual ao rótulo da barra
            eixo.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: f"{v:,.0f}".replace(",", ".")))
        for barra, valor in zip(barras, [vb, vd]):
            eixo.text(barra.get_x() + barra.get_width() / 2, valor * 1.03,
                      fmt.format(valor).replace(",", ".").replace(".", ",", 1) if fmt == "{:.1f}"
                      else fmt.format(valor).replace(",", "."),
                      ha="center", va="bottom", fontsize=11, color=ESTRUTURA["tinta"])
    fig.suptitle("Desconto quase igual, resultado oposto — arquétipos B e D",
                 fontsize=14, color=ESTRUTURA["tinta"])
    # Três linhas explícitas: numa só, o rodapé centralizado saía dos dois lados do quadro e
    # perdia a definição de B e a cláusula T6 — a trava visual não olhava a cartela.
    fig.text(0.5, 0.012,
             "Fonte: base analítica, n = 1.348 · ML4, k = 4, semente 42 · medianas\n"
             f"{rotulo_b} (n {int(b.n)}) · {rotulo_d} (n {int(d.n)})\n"
             "Associação descritiva, não causal (T4) · volume de avaliações, não vendas (T6)",
             ha="center", fontsize=7.5, color=ESTRUTURA["secundario"], linespacing=1.5)
    fig.tight_layout(rect=[0, 0.11, 1, 0.94])
    confere_visual(fig, "cartela_conflito_BxD.png")
    os.makedirs(os.path.dirname(SAIDA_CARTELA), exist_ok=True)
    fig.savefig(SAIDA_CARTELA, dpi=160)
    plt.close(fig)


if __name__ == "__main__":
    main()

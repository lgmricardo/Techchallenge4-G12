# -*- coding: utf-8 -*-
"""
Preparação dos dados em três camadas: bronze → silver → gold.

Por que três camadas, e não uma leitura direta
----------------------------------------------
O CSV de origem **nunca é alterado**. Ele é lido, e todo resultado é escrito em
outra camada. Essa é a razão de existir da separação — não o tamanho do arquivo.

  bronze/   o `amazon.csv` como veio do Kaggle. 16 colunas, tudo texto, preço
            com símbolo de moeda e separador de milhar, avaliações concatenadas.
            NUNCA escrito por este script. NÃO versionado: contém `user_id` e
            `user_name` (LGPD, regra T7).

  silver/   tipado e deduplicado. Símbolo de moeda e separadores removidos na
            conversão, `product_id` único pela regra determinística, colunas
            pessoais descartadas.
            Sai em DOIS arquivos, e a separação é deliberada:
              produtos.csv        9 colunas, sem nenhum campo de texto livre.
                                  VERSIONADO — não carrega nome de pessoa.
              produtos_texto.csv  product_id + os campos de texto livre.
                                  NÃO versionado: o texto das avaliações traz
                                  nomes escritos pelos próprios usuários (assinatura,
                                  seção de perguntas, menção a atendente). Medido:
                                  ao menos 11 nomes reais em 21 produtos. Não são a
                                  coluna `user_name` — que foi removida — mas expõem
                                  autor do mesmo jeito, e o repositório é público.

  gold/     pronto para consumo. A base analítica (n = 1.348) com os campos
            derivados que o dashboard e os notebooks usam — nota corrigida de
            Wilson, faixas de engajamento, níveis de categoria, marcações de
            quadrante. É desta camada que o `.pbix` lê. Versionado.

Uso:  python3 src/prepara_dados.py
"""

import hashlib
import os
import sys

import numpy as np
import pandas as pd

# O caractere abaixo é o marcador de moeda NA ORIGEM — aquilo que o tratamento
# REMOVE. Ele é escrito como escape unicode de propósito: a premissa do projeto
# é que o símbolo de rupia não apareça em nenhum rótulo, visual, tabela ou texto
# publicado (escreve-se "rupia" por extenso). Aqui ele existe só como alvo de
# remoção, e o escape garante que o glifo não esteja nem no código-fonte.
MARCADOR_MOEDA_ORIGEM = "\u20b9"  # rupia indiana, U+20B9

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BRONZE = os.path.join(RAIZ, "00_data", "bronze", "amazon.csv")
SILVER = os.path.join(RAIZ, "00_data", "silver", "produtos.csv")
SILVER_TXT = os.path.join(RAIZ, "00_data", "silver", "produtos_texto.csv")
GOLD = os.path.join(RAIZ, "00_data", "gold", "base_analitica.csv")
GOLD_REV = os.path.join(RAIZ, "00_data", "gold", "reviews.csv")

SHA_BRONZE = "4ba126c4ba8edd35e62e94ce1c853073d832de380184ab4f5f97d1e314882c77"


def rel(caminho):
    """Caminho relativo à raiz: a saída do script é lida em notebook versionado,
    e a pasta pessoal de quem rodou não faz parte do resultado."""
    return os.path.relpath(caminho, RAIZ)

PESSOAIS = ["user_id", "user_name"]          # T7 / LGPD — não saem do bronze
SEM_USO = ["img_link", "product_link"]       # sem uso analítico declarado


def num(serie, remover):
    saida = serie.astype(str)
    for ch in remover:
        saida = saida.str.replace(ch, "", regex=False)
    return pd.to_numeric(saida, errors="coerce")


def wilson(nota, n, z=1.96):
    """T1 — limite inferior de Wilson, nota normalizada de 1–5 para 0–1."""
    p = (nota - 1) / 4.0
    d = 1 + z ** 2 / n
    centro = p + z ** 2 / (2 * n)
    margem = z * np.sqrt(p * (1 - p) / n + z ** 2 / (4 * n ** 2))
    return ((centro - margem) / d) * 4 + 1


def main():
    # ---------------- BRONZE — só leitura, e com prova de integridade --------
    if not os.path.exists(BRONZE):
        sys.exit(f"ERRO: bronze ausente em {BRONZE}.\n"
                 "Baixe de https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset")
    with open(BRONZE, "rb") as fh:
        sha = hashlib.sha256(fh.read()).hexdigest()
    print("BRONZE")
    print(f"  {rel(BRONZE)}")
    print(f"  SHA-256 {sha}")
    if sha != SHA_BRONZE:
        sys.exit("ERRO: o bronze não é a base canônica. Nenhum número do material vale sobre ele.")
    print("  integridade conferida · o arquivo não será escrito por este script")

    df = pd.read_csv(BRONZE, dtype=str)
    print(f"  {df.shape[0]} linhas × {df.shape[1]} colunas, tudo texto")

    # ---------------- SILVER — tipagem e deduplicação determinística ---------
    s = df.copy()
    s["preco_desc"] = num(s.discounted_price, [MARCADOR_MOEDA_ORIGEM, ","])
    s["preco_tab"] = num(s.actual_price, [MARCADOR_MOEDA_ORIGEM, ","])
    s["desconto"] = num(s.discount_percentage, ["%"])
    # O marcador de moeda não está só no preço: um dos produtos é um teclado cujo
    # diferencial de venda é ter a tecla, e o glifo aparece dentro do product_name.
    # Ali ele é dado citado, não formatação nossa — mas a silver e a gold são
    # versionadas, e a premissa vale para todo texto publicado. O nome sai com a
    # palavra no lugar do glifo; o bronze continua intacto.
    s["product_name"] = s.product_name.str.replace(MARCADOR_MOEDA_ORIGEM, "rupia", regex=False)
    s["avaliacoes"] = num(s.rating_count, [","])
    s["nota"] = pd.to_numeric(s.rating, errors="coerce")
    s["_ordem"] = np.arange(len(s))

    # Regra determinística: maior rating_count; no empate, menor índice de origem.
    # Sem o desempate a base não é reproduzível — 65 dos 92 repetidos empatam no máximo.
    s = (s.sort_values(["avaliacoes", "_ordem"], ascending=[False, True], na_position="last")
           .drop_duplicates("product_id", keep="first")
           .drop(columns=["_ordem"] + PESSOAIS + SEM_USO
                 + ["discounted_price", "actual_price", "discount_percentage", "rating", "rating_count"]))
    os.makedirs(os.path.dirname(SILVER), exist_ok=True)
    TEXTO_LIVRE = ["about_product", "review_id", "review_title", "review_content"]
    s[["product_id"] + TEXTO_LIVRE].to_csv(SILVER_TXT, index=False, encoding="utf-8")
    s.drop(columns=[c for c in TEXTO_LIVRE if c != "review_id"]).to_csv(
        SILVER, index=False, encoding="utf-8")
    print("\nSILVER")
    print(f"  {rel(SILVER)}")
    print(f"  {rel(SILVER_TXT)}")
    print(f"  {len(s)} produtos · texto livre · NÃO versionado (nomes escritos nas avaliações)")
    print(f"  {len(s)} produtos deduplicados e tipados")
    print(f"  removidas: {', '.join(PESSOAIS)} (T7/LGPD) · {', '.join(SEM_USO)} (sem uso)")
    print("  texto livre separado: about_product, review_title, review_content")

    # ---------------- GOLD — base analítica com os derivados ------------------
    g = s[s.nota.notna() & s.avaliacoes.notna()].copy()
    p90 = g.avaliacoes.quantile(0.90)
    mediana = g.avaliacoes.median()

    g["nota_corrigida"] = wilson(g.nota, g.avaliacoes)
    g["categoria_n1"] = g.category.str.split("|").str[0]
    g["categoria_n2"] = g.category.str.split("|").str[:2].str.join(" | ")
    g["engajamento"] = np.where(g.avaliacoes >= p90, "alto",
                                np.where(g.avaliacoes < mediana, "baixo", "intermediario"))
    g["satisfacao"] = np.where(g.nota < 4.0, "baixa",
                               np.where(g.nota >= 4.3, "alta", "media"))
    g["q5_risco_vitrine"] = (g.avaliacoes >= p90) & (g.nota < 4.0)
    g["q6_subexplorado"] = (g.nota >= 4.3) & (g.avaliacoes < mediana)
    g["faixa_desconto"] = pd.cut(g.desconto, [0, 20, 40, 60, 80, 100],
                                 labels=["0-20%", "21-40%", "41-60%", "61-80%", "81-100%"],
                                 include_lowest=True)
    acum = g.avaliacoes.sort_values(ascending=False).cumsum()
    limite = acum[acum < 0.8 * g.avaliacoes.sum()].index
    g["pareto_80"] = g.index.isin(limite) | (g.index == acum.index[len(limite)])

    os.makedirs(os.path.dirname(GOLD), exist_ok=True)
    g.drop(columns=["review_id", "review_title", "review_content", "about_product"]).to_csv(
        GOLD, index=False, encoding="utf-8")

    # corpus textual, deduplicado por review_id (T8)
    ex = g.assign(_r=g.review_id.str.split(",")).explode("_r")
    ex["_r"] = ex._r.str.strip()
    rev = (ex[["_r", "product_id", "categoria_n1", "nota", "satisfacao"]]
           .rename(columns={"_r": "review_id"})
           .drop_duplicates("review_id"))
    rev.to_csv(GOLD_REV, index=False, encoding="utf-8")

    print("\nGOLD")
    print(f"  {rel(GOLD)}")
    print(f"  {len(g)} produtos — base analítica · {g.shape[1] - 4} colunas com derivados")
    print(f"  cortes aplicados: p90 = {p90:,.0f} · mediana = {mediana:,.0f}".replace(",", "."))
    print(f"  Q5 = {int(g.q5_risco_vitrine.sum())} · Q6 = {int(g.q6_subexplorado.sum())} · "
          f"Pareto 80% = {int(g.pareto_80.sum())}")
    print(f"  {rel(GOLD_REV)}")
    print(f"  {len(rev)} reviews distintos (de {len(ex)} referências) · deduplicado por review_id (T8)")

    print("\nReconciliação: "
          f"{len(df)} (bronze) → {len(s)} (silver) → {len(g)} (gold)")
    print("Nenhuma coluna pessoal atravessa o bronze. Valores monetários sem símbolo, "
          "em rupia indiana (L5).")


if __name__ == "__main__":
    main()

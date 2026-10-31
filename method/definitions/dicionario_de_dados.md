# 📚 DICIONÁRIO DE DADOS

**Granularidade da origem:** uma linha por produto, com o bloco de avaliações concatenado. Após deduplicação: **1 linha = 1 produto**.

Este arquivo é verificado por `src/valida_dicionario.py`, que confere **coluna a coluna** se o que está escrito aqui existe nos artefatos — e se todo artefato tem a coluna documentada. Saída 0 significa que o dicionário e os dados não divergem.

---

## 1. Colunas da origem — e o nome que cada uma recebe no pipeline

A terceira coluna é a que faltava neste dicionário e é a que importa para quem modela: **o pipeline renomeia os campos**, e é o nome tratado que aparece na silver, na gold e nas medidas DAX.

| Coluna na origem | Nome tratado | Tipo na origem | Tipo tratado | Regra de tratamento | Uso |
|---|---|---|---|---|---|
| `product_id` | `product_id` | string | string | chave; deduplicar mantendo a ocorrência de maior `rating_count`; **no empate, menor índice de linha na origem** | chave primária |
| `product_name` | `product_name` | string | string | sem alteração | rótulo de produto |
| `category` | `category` | string | hierarquia | preservada inteira; os níveis saem em `categoria_n1` e `categoria_n2` (§2); até 7 níveis | agrupamento |
| `discounted_price` | **`preco_desc`** | string `1.234` com marcador de rupia à frente | decimal | remover o marcador de rupia e o separador de milhar | preço praticado |
| `actual_price` | **`preco_tab`** | string `1.234` com marcador de rupia à frente | decimal | idem | preço de tabela |
| `discount_percentage` | **`desconto`** | string `64%` | decimal 0–100 | remover `%` | desconto declarado |
| `rating` | **`nota`** | string | decimal 1–5 | 1 registro com valor `\|` → nulo, produto excluído da base analítica | satisfação |
| `rating_count` | **`avaliacoes`** | string `1,234` | inteiro | remover separador; 2 nulos → excluídos da base analítica | **volume de avaliações** |
| `about_product` | `about_product` | string | texto | preservada apenas na silver de texto, **fora da gold** — descreve a promessa do vendedor, não a percepção do consumidor (D-5) | — |
| `user_id` | — | string | **eliminada** | **não entra em nenhum arquivo versionado** (T7 / LGPD) | nenhum |
| `user_name` | — | string | **eliminada** | **não entra em nenhum arquivo versionado** (T7 / LGPD) | nenhum |
| `review_id` | `review_id` | string, lista | lista | explodir por `,`; **deduplicar** — há identificadores repetidos entre produtos | dimensionar corpus |
| `review_title` | `review_title` | string, lista | lista | explodir junto com `review_id` | NLP |
| `review_content` | `review_content` | string, lista | lista | explodir junto com `review_id`; remover URLs e tokens não latinos | NLP |
| `img_link` · `product_link` | — | string | **descartadas** | sem uso analítico | — |

**Das 16 colunas da origem, o tratamento preserva 12:** saem `user_id` e `user_name` por T7/LGPD, e `img_link` e `product_link` por não terem uso analítico.

---

## 2. Campos derivados — todos existem na gold, com a fórmula do código

Nove colunas derivadas, criadas em `src/prepara_dados.py`. **A fórmula abaixo é a do código**, não uma paráfrase:

| Campo | Cálculo | Tipo | Observação |
|---|---|---|---|
| `nota_corrigida` | **limite inferior de Wilson a 95%** (z = 1,96) sobre a nota normalizada de 1–5 para 0–1, revertida à escala 1–5 | decimal 1–5 | **obrigatório em todo ranking por nota (T1).** D-3 fechada em 01/10/2026 nesta forma; a média bayesiana foi descartada por exigir arbitrar um *prior* |
| `categoria_n1` | primeiro nó de `category`, separado por `\|` | string | família de produto — 9 valores, 4 acima do piso de T2 |
| `categoria_n2` | dois primeiros nós de `category`, unidos por `" \| "` | string | **unidade de comparação por subcategoria** — 29 valores, 8 acima do piso |
| `engajamento` | `alto` se `avaliacoes ≥ 36.384` (p90); `baixo` se `< 4.740` (mediana); senão `intermediario` | categórico | **volume de avaliações, nunca venda (T6)** |
| `satisfacao` | `baixa` se `nota < 4,0`; `alta` se `nota ≥ 4,3` (p75); senão `media` | categórico | os dois cortes que todo o projeto usa |
| `q5_risco_vitrine` | `avaliacoes ≥ 36.384` **e** `nota < 4,0` | booleano | **19 produtos** — responde Q5 |
| `q6_subexplorado` | `nota ≥ 4,3` **e** `avaliacoes < 4.740` | booleano | **187 produtos — é o funil de triagem.** Cruzando com `nota_corrigida ≥ 4,3` restam **61**, que é a lista acionável e a medida **M22** do catálogo DAX. T1 exige a corrigida em todo ranking, e uma lista de oportunidades é um ranking |
| `faixa_desconto` | `desconto` em 5 faixas: `0-20%` · `21-40%` · `41-60%` · `61-80%` · `81-100%` | categórico | todas as 5 acima do piso de T2 |
| `pareto_80` | verdadeiro para os produtos que, ordenados por `avaliacoes` decrescente, acumulam 80% do volume total — **incluindo o produto que cruza o limiar** | booleano | **306 produtos (22,7%)** — responde QA2 |

**Nota sobre `desconto`.** Ele é o campo **declarado** pela origem (`discount_percentage`), não recalculado. O recálculo `(1 − preco_desc / preco_tab) × 100` foi medido para verificação e divergiu no máximo **0,50 p.p.** do declarado; por isso o declarado é mantido, e **não existe coluna `desconto_recalculado`** em nenhum artefato.

---

## 3. Onde cada coluna vive

| Artefato | Colunas | Versionado? |
|---|---|---|
| `00_data/bronze/amazon.csv` | as 16 da origem | ❌ **não** — contém `user_id` e `user_name` |
| `00_data/silver/produtos.csv` | **9** — `product_id` `product_name` `category` `review_id` `preco_desc` `preco_tab` `desconto` `avaliacoes` `nota` | ✅ sim |
| `00_data/silver/produtos_texto.csv` | **5** — `product_id` `about_product` `review_id` `review_title` `review_content` | ❌ **não** — o texto das avaliações contém nomes de pessoas reais |
| `00_data/gold/base_analitica.csv` | **17** — as 8 estruturadas de produto + as 9 derivadas de §2 | ✅ sim |
| `00_data/gold/reviews.csv` | **5** — `review_id` `product_id` `categoria_n1` `nota` `satisfacao` | ✅ sim |

As 9 da silver e as 5 do arquivo de texto somam 12 contando `product_id` e `review_id` **uma vez** — são as chaves que permitem rejuntar as duas partes para quem tiver o arquivo de texto localmente.

---

## 4. Vocabulário de granularidade — termo fora desta lista não entra em documento

| Termo | Significado | Contagem |
|---|---|---|
| **Produto** | linha após deduplicação | 1.351 |
| **Bloco de review** | conjunto truncado de até 8 avaliações de um produto | 1 por produto |
| **Referência de avaliação** | item após explodir o bloco | 10.588 |
| **Review individual** | referência após deduplicar por `review_id` | **9.255** |
| **Categoria nível 1** | primeiro nó da hierarquia — `categoria_n1` | 9 (4 acima do piso) |
| **Subcategoria nível 2** | unidade de comparação — `categoria_n2` | 29 (8 acima do piso) |

# 📏 BASE FACTUAL E BASES DE CÁLCULO
**Fonte única de números do projeto · medido em 23/09/2026 sobre `amazon.csv`**

Nenhum número entra em visual, slide ou fala do vídeo sem declarar qual destas bases usou.

## 1. As cinco bases oficiais

| Base | *n* | Quando usar |
|---|---|---|
| Bruta | **1.465** | apenas para relatar a qualidade da origem |
| Produtos | **1.351** | contagem de portfólio, após deduplicação |
| Nota válida | **1.350** | análises que dependem só de `rating` |
| Engajamento válido | **1.349** | análises que dependem só de `rating_count` |
| **Analítica** | **1.348** | **padrão** — toda análise cruzada, modelagem e quadrante |

**Reconciliação:** 1.465 − 114 linhas excedentes = 1.351 → −1 (`rating` inválido) = 1.350 → −2 (`rating_count` nulo, sem sobreposição) = **1.348**.

## 2. Qualidade da origem

| Verificação | Resultado |
|---|---|
| Colunas | 16, todas string na origem |
| Linhas integralmente duplicadas | 0 |
| Linhas excedentes por `product_id` | **114**, distribuídas em **92** `product_id` |
| `product_id` com `rating_count` divergente entre ocorrências | **31** |
| Falha de conversão numérica | `rating` = 1 (valor `\|`) · `rating_count` = 2 nulos · preços e desconto = 0 |
| Preço com desconto acima do preço de tabela | 0 casos |
| Divergência entre desconto declarado e recalculado | máx. **0,50 p.p.** · média 0,21 · nenhum caso acima de 1 p.p. |

## 3. Regra de deduplicação — única válida
Manter a ocorrência de **maior `rating_count`** por `product_id`; **no empate, a de menor índice de linha na origem** (ordenação estável). O desempate é obrigatório: dos 92 `product_id` repetidos, apenas **27** têm máximo único — nos outros **65** o máximo empata e a regra sozinha não decide. Impacto medido e reproduzido por `src/valida_base.py`. A escolha é imaterial para **toda métrica agregada** (diferença somada de 40 avaliações em 23.802.463 — 0,0002%). Altera, produto a produto, o **preço com desconto de 1**, o **desconto de 1** e o **texto de avaliação de 4**. Nota e categoria nunca mudam.

## 4. Cortes operacionais fechados

| Conceito | Corte | Valor medido |
|---|---|---|
| Engajamento alto | ≥ p90 de `rating_count` | **36.384** |
| Engajamento baixo | < mediana de `rating_count` | **4.740** |
| Satisfação baixa | `rating` < 4,0 | **339 produtos · 25,1%** |
| Satisfação alta | `rating` ≥ 4,3 | **418 produtos** |
| Piso amostral de grupo agregado | n ≥ 30 | — |

## 5. Quadrantes e concentrações

| Item | Valor |
|---|---|
| Alto engajamento + nota < 4,0 (Q5) | **19 produtos · 147 avaliações · ≈49,5 mil caracteres** |
| Nota ≥ 4,3 + engajamento abaixo da mediana (candidato a Q6) | **187 produtos** |
| Produtos que concentram 80% das avaliações (QA2) | **306 = 22,7% da base analítica** |
| Subcategorias de nível 2 acima do piso (QA3) | **8**, cobrindo **88,3%** dos produtos |

## 6. Distribuição das variáveis principais (n = 1.348)

| Variável | Mediana | p25 | p75 | p90 | Máx |
|---|---|---|---|---|---|
| Preço de tabela (rupia indiana) | 1.795 | 899 | 4.592 | 15.999 | 139.900 |
| Preço com desconto (rupia indiana) | 899 | 349 | 2.184 | 8.993 | 77.990 |
| Desconto (%) | 49 | 31 | 62 | 75 | 94 |
| Nota | 4,10 | 3,90 | 4,30 | 4,40 | 5,00 |
| Avaliações | 4.740 | 1.108 | 16.052 | 36.384 | 426.973 |

## 7. Categorias de nível 1 (n = 1.348)

| Categoria | Produtos | Situação |
|---|---|---|
| Electronics | 490 | acima do piso |
| Home & Kitchen | 447 | acima do piso |
| Computers & Accessories | 373 | acima do piso |
| Office Products | 31 | acima do piso, no limite |
| Musical Instruments (2) · Home Improvement (2) · Toys & Games (1) · Health & Personal Care (1) · Car & Motorbike (1) | **7 produtos em 5 categorias** | abaixo do piso — nunca ranqueadas |

**Reconciliação da tabela:** 490 + 447 + 373 + 31 + 7 = **1.348** ✅

**Leitura obrigatória:** 97,2% do portfólio está em três famílias. "Análise de categorias" significa, na prática, três categorias mais uma no limite.

## 8. Associações medidas (Spearman, n = 1.348)

| Par | ρ | p | Leitura |
|---|---|---|---|
| Desconto × nota | **−0,150** | 3,1e-08 | significativa, magnitude pequena |
| Desconto × engajamento | **−0,132** | 1,1e-06 | desconto não acompanha volume |
| Preço de tabela × nota | +0,032 | 0,236 | **sem associação** |
| Engajamento × nota | +0,193 | 8,3e-13 | associação fraca positiva |

**Regra de publicação:** magnitude sempre ao lado do p-valor. Com n = 1.348, diferenças irrelevantes cruzam o limiar de significância.

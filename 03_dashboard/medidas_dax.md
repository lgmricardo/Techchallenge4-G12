# 🧮 CATÁLOGO DE MEDIDAS DAX

**Entrega 1 · `TechChallenge4_G12.pbix` · POSTECH DTAT — Tech Challenge Fase 4**
Medido em 24/09/2026 sobre `00_data/gold/`. Fonte executável dos números: **`03_dashboard/valores_referencia.py`**.

---

## Situação desta entrega — D-7 está FECHADA

**D-7 foi fechada em 01/10/2026.** Ela pedia duas coisas, e as duas existem:

| Metade de D-7 | Onde está | Estado |
|---|---|---|
| Catálogo de medidas | **este arquivo** — 22 medidas, M01 a M22 | ✅ |
| Matriz de aderência C1–C9 | `method/definitions/matriz_aderencia_C1_C9.md` | ✅ |

A numeração antiga ia até M10; esta vai até **M22** porque o escopo de perguntas exige mais do que dez indicadores. **As decisões que condicionavam medidas também fecharam:**

| Medida | Decisão | Estado |
|---|---|---|
| **M07 · Nota Corrigida Mediana** | **D-3** (Wilson × média bayesiana) | ✅ **fechada em 01/10/2026 no limite inferior de Wilson a 95%** — é o que a gold já traz e o que todo ranking usa |
| **M12 · Produtos Q6** | **D-1** (visibilidade × engajamento baixo) | ✅ **fechada em 24/09/2026** — proxy declarado de exposição; o nome publicado é **"bem avaliados com baixo volume de avaliações"**, nunca "baixa visibilidade" (T6). "Subexplorado" vale só como nome do quadrante da matriz de D-2 |

**Quantos números este catálogo garante.** São **22 medidas catalogadas** (M01–M22). Delas, **21 têm valor de referência calculado em Python**, distribuído em **25 linhas** de `valores_referencia.csv` — a diferença existe porque **M15 se desdobra nas 4 categorias elegíveis mais a parcela suprimida por T2**. A medida sem linha própria é **M21**, que é texto composto de M01 e M18: reconciliar as duas reconcilia o rodapé.

---

## Convenções que valem para todas as medidas

**Modelo.** As medidas deste catálogo usam só as duas tabelas de fato, construídas no Power Query a partir do bronze, e moram numa tabela vazia. O modelo completo — inclusive as cinco tabelas de resultado, sem relacionamento — está em `modelo_de_dados.md`.

| Tabela no modelo | Origem | Linhas | Grão |
|---|---|---|---|
| `BaseAnalitica` | Power Query: `gold_intermediaria` + `tab22` (passos 3–11) · gabarito `00_data/gold/base_analitica.csv` | 1.348 | 1 linha = 1 produto · 25 colunas |
| `Reviews` | Power Query: `gold_intermediaria` (passos 12–13) · contagem igual à de `00_data/gold/reviews.csv` | 9.255 | 1 linha = 1 review individual (dedup. por `review_id`, T8) |
| `_Medidas` | tabela vazia | — | abriga todas as medidas; nenhuma medida mora em tabela de fato |

**Tipagem obrigatória no Power Query**, antes de qualquer medida:

1. **Locale da fonte = `English (United States)`.** O bronze e as tabelas de `02_results/tables/` usam `.` como separador decimal. Em locale pt-BR, `4.395703192709469` é lido como **4.395.703.192.709.469** e toda medida de nota vira lixo silenciosamente. É o erro de reconciliação nº 1.
2. `q5_risco_vitrine`, `q6_subexplorado`, `pareto_80` → tipo **Verdadeiro/Falso (logical)**. Se ficarem como texto, **corrigir o tipo no Power Query**, não a medida: M11, M12, M13 e M22 comparam com `TRUE ()`, e `verifica_pbix.py` compara cada expressão do arquivo com a deste catálogo.
3. `avaliacoes` → **Número inteiro**. `preco_desc`, `preco_tab`, `desconto`, `nota`, `nota_corrigida` → **Número decimal**.
4. `user_id`, `user_name` e o texto das avaliações **existem** nas consultas intermediárias, porque o Power Query parte do bronze. Nenhuma delas pode carregar no modelo — o passo 16 do guia é obrigatório, e é ele que mantém **T7** cumprida dentro do arquivo.

**Moeda (L5).** Valores monetários são publicados **sem símbolo**, em **rupia indiana**, **sem conversão**. Formato `#.##0` na tela.

**Notação.** As linhas *Formato* deste catálogo descrevem como o número **aparece** — em notação brasileira (`#.##0`, `0,0%`). Dentro do DAX (`FORMAT`) e na caixa de formato do Power BI vale a notação **invariante** (`#,##0`, `0.0%`), que o Power BI exibe no padrão brasileiro. As expressões deste catálogo já vêm na invariante: copiar como está. Nenhuma medida deste catálogo leva o símbolo de rupia ou `R$`.

**T6.** `avaliacoes` é **volume de avaliações**. Nenhum rótulo de medida, eixo ou tooltip pode dizer venda, receita, demanda ou popularidade. As medidas foram nomeadas para tornar isso difícil de errar: é "Volume de Avaliações", nunca "Vendas".

**T2 — piso amostral.** Grupo agregado com n < 30 não é ranqueado nem comparado. O piso é aplicado **por medida**, com o padrão da seção *Padrão T2* mais abaixo, não no olho de quem monta o visual.

**T3.** Toda medida declara aqui a **base** e o **n**. O rodapé da página que a exibe repete a declaração (medida **M21**).

---

## Resumo — os 21 valores de referência

Todos calculados por `03_dashboard/valores_referencia.py`; nenhum estimado.

| # | Medida | Valor de referência | Base | n |
|---|---|---|---|---|
| M01 | Produtos Ativos | **1.348** | Analítica | 1.348 |
| M02 | Volume Total de Avaliações | **23.801.471** | Analítica | 1.348 |
| M03 | Preço Mediano | **899** | Analítica | 1.348 |
| M04 | Preço de Tabela Mediano | **1.795** | Analítica | 1.348 |
| M05 | Desconto Mediano | **49** | Analítica | 1.348 |
| M06 | Nota Mediana | **4,10** | Analítica | 1.348 |
| M07 | Nota Corrigida Mediana | **4,065** | Analítica | 1.348 |
| M08 | Volume Mediano de Avaliações | **4.740** | Analítica | 1.348 |
| M09 | % Satisfação Baixa | **25,1%** (339) | Analítica | 1.348 |
| M10 | % Satisfação Alta | **31,0%** (418) | Analítica | 1.348 |
| M11 | Produtos Q5 | **19** | Analítica | 1.348 |
| M12 | Produtos Q6 | **187** | Analítica | 1.348 |
| M13 | Concentração Pareto 80% | **306** | Analítica | 1.348 |
| M14 | % Concentração Pareto 80% | **22,7%** | Analítica | 1.348 |
| M15 | Participação da Categoria no Volume | **59,7 / 26,6 / 12,6 / 0,6%** | Analítica | 490 / 373 / 447 / 31 |
| M16 | Subcategorias acima do Piso | **8** de 29 | Analítica | 1.348 |
| M17 | Cobertura de Subcategoria acima do Piso | **88,3%** (1.190) | Analítica | 1.348 |
| M18 | Corte de Engajamento Alto (p90) | **36.384** | Analítica | 1.348 |
| M19 | Corte de Engajamento Baixo (mediana) | **4.740** | Analítica | 1.348 |
| M20 | Reviews Individuais | **9.255** | Reviews | 9.255 |
| M21 | Rodapé T3 | texto composto de M01 e M18 | Analítica | 1.348 |
| **M22** | **Produtos Q6 Acionáveis (Wilson)** | **61** | Analítica | 1.348 |

---

# As medidas

## M01 · Produtos Ativos

```dax
Produtos Ativos =
COUNTROWS ( BaseAnalitica )
```

| | |
|---|---|
| **Unidade** | produtos |
| **Denominador** | — (contagem simples) |
| **Base (T3)** | Analítica · `gold/base_analitica.csv` · n = 1.348 |
| **Valor de referência** | **1.348** |
| **Formato** | `#.##0` |
| **Onde aparece** | KPI da Visão Executiva; denominador de M09, M10, M14, M17 |

**Conferência cruzada:** `DISTINCTCOUNT ( BaseAnalitica[product_id] )` tem de devolver **1.348** também. Se divergir, a deduplicação do Power Query duplicou linha — o grão do modelo quebrou.

**Por que não é 1.465 nem 1.351:** 1.465 (bruta) → −114 linhas excedentes = 1.351 (produtos) → −1 `rating` inválido = 1.350 → −2 `rating_count` nulo = **1.348**. A base bruta só serve para relatar qualidade da origem; nenhuma medida deste catálogo a usa.

---

## M02 · Volume Total de Avaliações

```dax
Volume Total de Avaliações =
SUM ( BaseAnalitica[avaliacoes] )
```

| | |
|---|---|
| **Unidade** | avaliações (**T6** — não é venda, receita nem demanda) |
| **Denominador** | — |
| **Base (T3)** | Analítica · n = 1.348 |
| **Valor de referência** | **23.801.471** |
| **Formato** | `#.##0` |
| **Onde aparece** | denominador de M15; KPI de apoio |

**Atenção a um número parecido:** `base_factual` cita **23.802.463** avaliações ao discutir a materialidade da deduplicação. Aquele total é da camada **silver (n = 1.351)**; o desta medida é da **analítica (n = 1.348)**. A diferença de **992 avaliações** são os 3 produtos removidos por `rating`/`rating_count` inválidos. Não é erro — é base diferente, e por isso T3 exige declarar qual.

---

## M03 · Preço Mediano

```dax
Preço Mediano =
MEDIAN ( BaseAnalitica[preco_desc] )
```

| | |
|---|---|
| **Unidade** | **rupia indiana, sem símbolo, sem conversão (L5)** |
| **Denominador** | — |
| **Base (T3)** | Analítica · n = 1.348 |
| **Valor de referência** | **899** |
| **Formato** | `#.##0` — **nunca** formato de moeda |
| **Onde aparece** | Preços e Estratégia Comercial |

É o **preço praticado** (com desconto). Mediana, não média: a distribuição vai de 349 (p25) a 77.990 (máx) e a média não descreve nada nesse intervalo.

---

## M04 · Preço de Tabela Mediano

```dax
Preço de Tabela Mediano =
MEDIAN ( BaseAnalitica[preco_tab] )
```

| | |
|---|---|
| **Unidade** | rupia indiana, sem símbolo (L5) |
| **Denominador** | — |
| **Base (T3)** | Analítica · n = 1.348 |
| **Valor de referência** | **1.795** |
| **Formato** | `#.##0` |
| **Onde aparece** | Preços — par de M03; sustenta QA4 |

**T4/T5:** ao exibir junto da nota, a leitura é ρ = **+0,032**, p = **0,236** — **não há associação** entre preço de tabela e satisfação. Não escrever que preço "influencia", "explica" ou "leva a" nota.

---

## M05 · Desconto Mediano

```dax
Desconto Mediano =
MEDIAN ( BaseAnalitica[desconto] )
```

| | |
|---|---|
| **Unidade** | % declarado na origem, escala 0–100 |
| **Denominador** | — (é percentual da origem, não razão calculada no modelo) |
| **Base (T3)** | Analítica · n = 1.348 |
| **Valor de referência** | **49** |
| **Formato** | `0"%"` — **não** usar formato percentual do Power BI, que multiplicaria por 100 de novo |
| **Onde aparece** | Preços; QA1 |

Usa o **desconto declarado**, não o recalculado. A divergência entre os dois foi medida em **0,50 p.p. no máximo** (média 0,21), e está fora do escopo como pergunta — entra como controle de qualidade.

---

## M06 · Nota Mediana

```dax
Nota Mediana =
MEDIAN ( BaseAnalitica[nota] )
```

| | |
|---|---|
| **Unidade** | estrelas, 1–5 |
| **Denominador** | — |
| **Base (T3)** | Analítica · n = 1.348 |
| **Valor de referência** | **4,10** |
| **Formato** | `0,00` |
| **Onde aparece** | Visão Executiva; contexto de M07 |

**Nunca ranquear com esta medida (T1).** M06 descreve a distribuição; quem ordena é M07. Um produto com 5 avaliações e nota 5,0 lidera qualquer ranking feito sobre `nota` bruta.

---

## M07 · Nota Corrigida Mediana

```dax
Nota Corrigida Mediana =
MEDIAN ( BaseAnalitica[nota_corrigida] )
```

| | |
|---|---|
| **Unidade** | estrelas corrigidas, 1–5 — **limite inferior de Wilson a 95%** |
| **Denominador** | — |
| **Base (T3)** | Analítica · n = 1.348 |
| **Valor de referência** | **4,065** (4,065164 com seis casas) |
| **Formato** | `0,00` no visual; `0,000` na conferência |
| **Onde aparece** | **toda ordenação por nota** (T1); Produtos e Categorias; QA6 |

`nota_corrigida` é **coluna da `BaseAnalitica`**, calculada **no Power Query** sobre `nota` e `avaliacoes` — não é recalculada em DAX. A medida consome a coluna; não recomputa a fórmula a cada visual. O valor é conferido contra a camada gold do Python pela consulta `qa_compara_gold`, que exige zero divergência.

**T1 na prática:** todo visual ordenado por M07 exibe o **n de avaliações ao lado** — use M02 (soma) ou `avaliacoes` no tooltip. Ranking sem o n é descumprimento.

**D-3 fechada em 01/10/2026:** adotado o **limite inferior de Wilson a 95%**. A ressalva metodológica fica registrada e deve acompanhar o visual quando houver espaço: Wilson é um intervalo para proporção binomial, aplicado aqui à nota normalizada de 1–5 para 0–1 — **aproximação deliberada e declarada**, não uso canônico. A alternativa descartada foi a média bayesiana, que exigiria arbitrar um *prior* sem resposta defensável.

---

## M08 · Volume Mediano de Avaliações

```dax
Volume Mediano de Avaliações =
MEDIAN ( BaseAnalitica[avaliacoes] )
```

| | |
|---|---|
| **Unidade** | avaliações por produto (**T6**) |
| **Denominador** | — |
| **Base (T3)** | Analítica · n = 1.348 |
| **Valor de referência** | **4.740** |
| **Formato** | `#.##0` |
| **Onde aparece** | Visão Executiva; corte de engajamento alto |

Numericamente igual a **M19** no contexto total, e **diferente** dela em qualquer contexto filtrado: M08 é a mediana do que está filtrado; M19 é o **corte fixo** da base inteira. Ver M19.

---

## M09 · % Satisfação Baixa

```dax
% Satisfação Baixa =
VAR _Baixa =
    CALCULATE ( [Produtos Ativos], BaseAnalitica[satisfacao] = "baixa" )
VAR _Total = [Produtos Ativos]
RETURN
    DIVIDE ( _Baixa, _Total )
```

| | |
|---|---|
| **Unidade** | % de produtos |
| **Denominador** | **[Produtos Ativos] no mesmo contexto** — total = 1.348 |
| **Base (T3)** | Analítica · n = 1.348 |
| **Valor de referência** | **25,1%** — 339 de 1.348 (25,148%) |
| **Formato** | `0,0%` |
| **Onde aparece** | Visão Executiva; Q4 |

Corte: `nota < 4,0`, fechado. `DIVIDE` e não `/`: protege o caso de contexto vazio.

**Denominador local, de propósito.** Filtrada por Electronics, a medida devolve **26,1%** (a fatia de Electronics), não a contribuição de Electronics para os 25,1% globais. É a leitura que Q4 pede. Valores por categoria em `valores_referencia_por_categoria.csv`.

---

## M10 · % Satisfação Alta

```dax
% Satisfação Alta =
VAR _Alta =
    CALCULATE ( [Produtos Ativos], BaseAnalitica[satisfacao] = "alta" )
VAR _Total = [Produtos Ativos]
RETURN
    DIVIDE ( _Alta, _Total )
```

| | |
|---|---|
| **Unidade** | % de produtos |
| **Denominador** | [Produtos Ativos] no mesmo contexto — total = 1.348 |
| **Base (T3)** | Analítica · n = 1.348 |
| **Valor de referência** | **31,0%** — 418 de 1.348 (31,009%) |
| **Formato** | `0,0%` |
| **Onde aparece** | Visão Executiva; Q4 |

Corte: `nota ≥ 4,3`. M09 + M10 não somam 100%: a faixa média (4,0 ≤ nota < 4,3) tem **591 produtos**, 43,8%.

---

## M11 · Produtos Q5 (risco de vitrine)

```dax
Produtos Q5 =
CALCULATE ( [Produtos Ativos], BaseAnalitica[q5_risco_vitrine] = TRUE () )
```

| | |
|---|---|
| **Unidade** | produtos |
| **Denominador** | — |
| **Base (T3)** | Analítica · n = 1.348 · cortes: `avaliacoes ≥ 36.384` **e** `nota < 4,0` |
| **Valor de referência** | **19** |
| **Formato** | `#.##0` |
| **Onde aparece** | Produtos e Categorias (Q5); Customer Insights (QA5) |

**T2 não se aplica.** A lista nominal dos 19 produtos é exceção declarada em T2 — não é grupo agregado. Exibe o **n de avaliações produto a produto**.

Os 19 concentram **147 avaliações** e ≈49,5 mil caracteres. Em QA5 isso é corpus pequeno demais para TF-IDF: o método declarado é **leitura qualitativa dirigida com protocolo de codificação**.

---

## M12 · Produtos Q6 (candidatos a subexplorado)

```dax
Produtos Q6 =
CALCULATE ( [Produtos Ativos], BaseAnalitica[q6_subexplorado] = TRUE () )
```

| | |
|---|---|
| **Unidade** | produtos |
| **Denominador** | — |
| **Base (T3)** | Analítica · n = 1.348 · cortes: `nota ≥ 4,3` **e** `avaliacoes < 4.740` |
| **Valor de referência** | **187** |
| **Formato** | `#.##0` |
| **Onde aparece** | Produtos e Categorias (Q6) |

**Rótulo fixado por D-1 (fechada em 24/09/2026) e por T6.** O título do visual é **"bem avaliados com baixo volume de avaliações"** — o único nome publicado. "Subexplorado" vale apenas como nome do **quadrante** da matriz de relevância (D-2), onde não é rótulo de recomendação. **Vedado** escrever "baixa visibilidade": visibilidade real (impressões, cliques, posição na busca) não existe nesta base.

**⚠️ Esta medida é o funil, não a recomendação.** Os 187 selecionam por **nota bruta**, e **126 deles caem** quando se aplica a correção que T1 exige em todo ranking. O número que vai para a tela de recomendação é o de **M22**, não este. Um visual que publique 187 como "oportunidade" descumpre T1 — exiba os dois, com M12 rotulado *funil de triagem* e M22 *lista acionável*.

---

## M13 · Concentração Pareto 80%

```dax
Concentração Pareto 80% =
CALCULATE ( [Produtos Ativos], BaseAnalitica[pareto_80] = TRUE () )
```

| | |
|---|---|
| **Unidade** | produtos |
| **Denominador** | — |
| **Base (T3)** | Analítica · n = 1.348 |
| **Valor de referência** | **306** |
| **Formato** | `#.##0` |
| **Onde aparece** | Visão Executiva (QA2) |

**Lê a coluna `pareto_80` da `BaseAnalitica`, calculada no Power Query — não recalcula a curva em DAX.** A regra é: ordenar por `avaliacoes` decrescente, marcar os produtos cujo acumulado fica abaixo de 80% do volume total, **mais o produto seguinte** (o que cruza a linha). O 306º produto leva o acumulado a **80,018%**; o 305º parava em **79,941%**.

A versão nativa em DAX existe e confere, mas é cara e sensível a empate:

```dax
-- alternativa dinâmica; usar só para auditar M13, nunca em produção
Pareto 80% (dinâmico) =
VAR _Total = CALCULATE ( SUM ( BaseAnalitica[avaliacoes] ), ALL ( BaseAnalitica ) )
VAR _Acum =
    ADDCOLUMNS (
        ALL ( BaseAnalitica[product_id] ),
        "@Acumulado",
            VAR _V = CALCULATE ( SUM ( BaseAnalitica[avaliacoes] ) )
            RETURN
                CALCULATE (
                    SUM ( BaseAnalitica[avaliacoes] ),
                    ALL ( BaseAnalitica ),
                    BaseAnalitica[avaliacoes] >= _V
                )
    )
RETURN
    COUNTROWS ( FILTER ( _Acum, [@Acumulado] < 0.8 * _Total ) ) + 1
```

---

## M14 · % Concentração Pareto 80%

```dax
% Concentração Pareto 80% =
DIVIDE (
    [Concentração Pareto 80%],
    CALCULATE ( [Produtos Ativos], ALL ( BaseAnalitica ) )
)
```

| | |
|---|---|
| **Unidade** | % da base analítica |
| **Denominador** | **fixo em `ALL(BaseAnalitica)` = 1.348** |
| **Base (T3)** | Analítica · n = 1.348 |
| **Valor de referência** | **22,7%** — 306 de 1.348 (22,700%) |
| **Formato** | `0,0%` |
| **Onde aparece** | Visão Executiva (QA2) |

**Denominador fixo, ao contrário de M09/M10.** A frase publicada é "306 produtos = 22,7% **da base analítica**"; se o denominador fosse local, o número mudaria a cada clique de segmentação e deixaria de corresponder à frase. Filtrada por categoria, a medida responde "que fatia da base inteira são os produtos Pareto desta categoria".

---

## M15 · Participação da Categoria no Volume

```dax
Participação da Categoria no Volume =
DIVIDE (
    [Volume Total de Avaliações],
    CALCULATE (
        [Volume Total de Avaliações],
        ALL ( BaseAnalitica[categoria_n1] )
    )
)
```

| | |
|---|---|
| **Unidade** | % do volume de avaliações (**T6** — do volume, não de vendas) |
| **Denominador** | **`ALL(BaseAnalitica[categoria_n1])` = 23.801.471 avaliações**, inclusive as categorias suprimidas |
| **Base (T3)** | Analítica · n = 1.348 |
| **Formato** | `0,0%` |
| **Onde aparece** | Produtos e Categorias (Q1, Q4) |

**Valores de referência — categorias acima do piso (T2, n ≥ 30):**

| Categoria | Produtos | Volume | Participação |
|---|---|---|---|
| Electronics | 490 | 14.208.441 | **59,7%** |
| Computers & Accessories | 373 | 6.335.182 | **26,6%** |
| Home & Kitchen | 447 | 2.990.077 | **12,6%** |
| Office Products | 31 | 149.675 | **0,6%** |
| **Soma publicada** | **1.341** | **23.683.375** | **99,5%** |
| *Suprimido por T2* (5 categorias) | *7* | *118.096* | *0,5%* |

**A supressão é declarada, não escondida.** Rodapé obrigatório do visual: *"5 categorias com n < 30 (7 produtos, 0,5% do volume) suprimidas por piso amostral — T2."* Sem essa linha, os 99,5% parecem erro de arredondamento.

**Leitura obrigatória:** 490 produtos (36% do portfólio) respondem por 59,7% do volume de avaliações — **53,1% colapsando as listagens variantes (L8)**, e as duas versões andam juntas em toda leitura de participação. Isso é **concentração de engajamento**, não de vendas (T6, L4).

**Padrão T2 — aplicar o piso na medida, não no olho:**

```dax
Participação da Categoria no Volume (T2) =
IF ( [Produtos Ativos] >= 30, [Participação da Categoria no Volume], BLANK () )
```

Use a variante `(T2)` em **todo** visual que ranqueia ou compara categorias. O `BLANK()` remove a linha do visual automaticamente. Vale igualmente para M07, M09 e M10 quando cruzadas por categoria ou subcategoria.

*Variante para segmentação interativa:* trocar `ALL` por `ALLSELECTED ( BaseAnalitica[categoria_n1] )` faz as fatias somarem 100% **dentro da seleção**. Não reproduz os valores acima e não é a medida homologada — é um visual diferente, com rodapé diferente.

---

## M16 · Subcategorias acima do Piso

```dax
Subcategorias acima do Piso =
COUNTROWS (
    FILTER (
        VALUES ( BaseAnalitica[categoria_n2] ),
        CALCULATE ( COUNTROWS ( BaseAnalitica ) ) >= 30
    )
)
```

| | |
|---|---|
| **Unidade** | subcategorias de nível 2 |
| **Denominador** | **29 subcategorias de nível 2 existentes** na base analítica |
| **Base (T3)** | Analítica · n = 1.348 · piso T2 = 30 |
| **Valor de referência** | **8** (de 29) |
| **Formato** | `#.##0` |
| **Onde aparece** | Produtos e Categorias (subcategorias, Q4) |

O `CALCULATE` dentro do `FILTER` faz a **transição de contexto**: conta produtos de cada subcategoria, uma a uma. Sem ele, a expressão compara o total da tabela com 30 e devolve 29.

**As 8 acima do piso:**

| Subcategoria (nível 2) | Produtos |
|---|---|
| Home & Kitchen \| Kitchen & Home Appliances | 307 |
| Computers & Accessories \| Accessories & Peripherals | 305 |
| Electronics \| Home Theater, TV & Video | 156 |
| Electronics \| Mobiles & Accessories | 151 |
| Home & Kitchen \| Heating, Cooling & Air Quality | 116 |
| Electronics \| Headphones, Earbuds & Accessories | 63 |
| Electronics \| Wearable Technology | 62 |
| Computers & Accessories \| Networking Devices | 30 |
| **Total coberto** | **1.190** |

Networking Devices entra com **exatamente 30** — no limite. Qualquer mudança na regra de deduplicação que remova um produto dela a derruba do visual.

---

## M17 · Cobertura de Subcategoria acima do Piso

```dax
Cobertura de Subcategoria acima do Piso =
VAR _Cobertos =
    SUMX (
        FILTER (
            VALUES ( BaseAnalitica[categoria_n2] ),
            CALCULATE ( COUNTROWS ( BaseAnalitica ) ) >= 30
        ),
        CALCULATE ( COUNTROWS ( BaseAnalitica ) )
    )
VAR _Total = CALCULATE ( [Produtos Ativos], ALL ( BaseAnalitica ) )
RETURN
    DIVIDE ( _Cobertos, _Total )
```

| | |
|---|---|
| **Unidade** | % de produtos |
| **Denominador** | **fixo em `ALL(BaseAnalitica)` = 1.348** |
| **Base (T3)** | Analítica · n = 1.348 · piso T2 = 30 |
| **Valor de referência** | **88,3%** — 1.190 de 1.348 (88,279%) |
| **Formato** | `0,0%` |
| **Onde aparece** | rodapé das subcategorias (2a); página de Recomendações |

É a medida que **mede a própria T2**: diz quanto do portfólio sobrevive ao piso amostral. Os 11,7% restantes (158 produtos, 21 subcategorias) não entram em nenhuma comparação por subcategoria.

Denominador fixo pela mesma razão de M14: a frase publicada é "88,3% **do portfólio**".

---

## M18 · Corte de Engajamento Alto (p90)

```dax
Corte de Engajamento Alto =
PERCENTILEX.INC ( ALL ( BaseAnalitica ), BaseAnalitica[avaliacoes], 0.90 )
```

| | |
|---|---|
| **Unidade** | avaliações por produto (**T6**) |
| **Denominador** | — |
| **Base (T3)** | Analítica · n = 1.348 · p90 de `rating_count` |
| **Valor de referência** | **36.384** |
| **Formato** | `#.##0` |
| **Onde aparece** | rodapé do corte de engajamento e de Q5; linha de referência em gráfico de dispersão |

**O `ALL` é obrigatório e não é detalhe.** O corte é **fechado sobre a base inteira**. Sem `ALL`, o p90 recalcula dentro de cada categoria, a linha de corte passa a flutuar e o visual deixa de bater com os 19 produtos de M11. É o segundo erro de reconciliação mais comum, e o mais silencioso: nenhum número parece errado isoladamente.

`PERCENTILEX.INC` usa a mesma interpolação linear do `quantile(0.90)` do pandas e cai exatamente em **36.384,0** — não há diferença de convenção a conciliar aqui.

---

## M19 · Corte de Engajamento Baixo (mediana)

```dax
Corte de Engajamento Baixo =
PERCENTILEX.INC ( ALL ( BaseAnalitica ), BaseAnalitica[avaliacoes], 0.50 )
```

| | |
|---|---|
| **Unidade** | avaliações por produto (**T6**) |
| **Denominador** | — |
| **Base (T3)** | Analítica · n = 1.348 · mediana de `rating_count` |
| **Valor de referência** | **4.740** |
| **Formato** | `#.##0` |
| **Onde aparece** | rodapé de Q6; linha de referência |

**M19 não é M08.** No total as duas devolvem 4.740; filtradas por Electronics, M08 devolve **9.129,5** (a mediana de Electronics) e M19 continua em **4.740** (o corte da base). O corte que define Q6 é M19. Usar M08 como linha de corte reclassifica produtos a cada segmentação.

---

## M20 · Reviews Individuais

```dax
Reviews Individuais =
DISTINCTCOUNT ( Reviews[review_id] )
```

| | |
|---|---|
| **Unidade** | reviews individuais — **unidade declarada (T8)** |
| **Denominador** | — |
| **Base (T3)** | Reviews · `gold/reviews.csv` · n = 9.255 |
| **Valor de referência** | **9.255** |
| **Formato** | `#.##0` |
| **Onde aparece** | Customer Insights (corpus e QA5) |

**T8 completo, obrigatório no rodapé da página:**

> Unidade: **review individual**. **10.588** referências de avaliação explodidas do bloco de cada produto → **1.333** repetidas removidas por `review_id` → **9.255** reviews distintos. A base exibe no máximo **8 avaliações por produto** (média 7,85) — **truncamento (L1)**.

Sem a linha do truncamento, o corpus aparece **14% maior** do que é, e o bloco de Customer Insights passa a se apresentar como "a voz do cliente" quando descreve **os temas visíveis na vitrine**.

---

## M21 · Rodapé T3

```dax
Rodapé T3 =
"Fonte: Amazon Sales Dataset (Kaggle) · base analítica n = "
    & FORMAT ( CALCULATE ( [Produtos Ativos], ALL ( BaseAnalitica ) ), "#,##0", "pt-BR" )
    & " produtos · n filtrado = "
    & FORMAT ( [Produtos Ativos], "#,##0", "pt-BR" )
    & " · corte de engajamento alto = "
    & FORMAT ( [Corte de Engajamento Alto], "#,##0", "pt-BR" )
    & " avaliações (p90) · valores em rupia indiana, sem conversão (L5)"
```

| | |
|---|---|
| **Unidade** | texto |
| **Denominador** | — |
| **Base (T3)** | Analítica · n = 1.348 |
| **Valor de referência** | *(composto de M01 e M18, ambos medidos)* → **"Fonte: Amazon Sales Dataset (Kaggle) · base analítica n = 1.348 produtos · n filtrado = 1.348 · corte de engajamento alto = 36.384 avaliações (p90) · valores em rupia indiana, sem conversão (L5)"** |
| **Formato** | cartão de texto, `secundario` `#5B6770` (T9) |
| **Onde aparece** | **rodapé de todas as 7 páginas** |

**Por que `"pt-BR"` nos três `FORMAT`.** Sem o terceiro argumento, `FORMAT` usa a cultura do modelo, que é en-US desde a criação do arquivo e não muda pela localidade de importação: o rodapé saía "1,348" ao lado de cartões com "1.348". As medidas de título já passavam `"pt-BR"`; o rodapé passou a fazer o mesmo em 13/11/2026.

É T3 mecanizado: o rodapé passa a mostrar **o n que está efetivamente filtrado**, em vez de um texto fixo que envelhece no primeiro clique de segmentação. Quando os dois n diferem, a diferença fica visível ao leitor — que é exatamente o ponto da regra.

---

## M22 · Produtos Q6 Acionáveis (Wilson)

```dax
Produtos Q6 Acionáveis =
CALCULATE (
    [Produtos Ativos],
    BaseAnalitica[q6_subexplorado] = TRUE (),
    BaseAnalitica[nota_corrigida] >= 4.3
)
```

| | |
|---|---|
| **Unidade** | produtos |
| **Denominador** | — |
| **Base (T3)** | Analítica · n = 1.348 · cortes: `q6_subexplorado` **e** `nota_corrigida ≥ 4,3` |
| **Valor de referência** | **61** |
| **Formato** | `#.##0` |
| **Onde aparece** | Produtos e Categorias (Q6) · Recomendações |

**Por que esta medida existe, e por que ela — não M12 — é a que vai para a recomendação.** M12 seleciona por **nota bruta** e devolve 187. Desses, **126 (67%) caem abaixo de 4,3 quando se aplica o limite inferior de Wilson**, porque a nota alta deles repousa em pouquíssimas avaliações — o menor volume entre os 187 é de **5 avaliações**, e 11 produtos têm menos de 30. T1 exige nota corrigida em **todo ranking**, e uma lista de oportunidades é um ranking.

**A regra de uso no `.pbix`, em uma frase:** **M12 é o funil, M22 é a fila de trabalho.** Publicar os dois lado a lado, com o rótulo de cada um, é o que torna o visual auditável; publicar só o 187 é descumprimento de T1, e publicar só o 61 esconde o tamanho do funil.

**Dependência de coluna.** `nota_corrigida` é calculada no Power Query (passo 9) e conferida contra a gold pela `qa_compara_gold`; não é recalculada em DAX — igual a M07. Se a definição de `nota_corrigida` mudar, M07 **e** M22 mudam juntas.

*Fonte do valor de referência: `03_dashboard/valores_referencia.py` · relatório §5.18.*

---

# Como reconciliar — DAX contra Python

Procedimento fechado. Rodar **antes de cada publicação** do `.pbix` e sempre que a camada gold for regerada.

### Passo 0 — a gold é a canônica

```bash
python3 src/prepara_dados.py
```

Confere o SHA-256 do bronze e falha se a origem não for a base canônica. Se falhar, **pare**: nenhum número do material vale. O script imprime a reconciliação `1.465 → 1.351 → 1.348`.

### Passo 1 — gerar os valores de referência

```bash
python3 03_dashboard/valores_referencia.py
```

Imprime as 21 medidas com valor, base e n, e grava:

- `03_dashboard/valores_referencia.csv` — uma linha por medida
- `03_dashboard/valores_referencia_por_categoria.csv` — as mesmas medidas cruzadas por `categoria_n1`

### Passo 2 — conferir o total, medida a medida

**Na página oculta `Conferência`** (`conferencia_dax.md`), montada logo depois das 22 medidas: a tabela `Conferencia` traz os 25 valores deste catálogo, e a medida `Conf · Valor DAX` recalcula cada um pela expressão daqui. O cartão **`Conf · Divergentes` tem de mostrar 0**.

A tolerância é **por linha, na escala do DAX** — percentuais como fração: **0** em contagens e somas, **1e-12** em frações e medianas decimais, **1e-8** na nota corrigida. A folga só existe para diferença de ponto flutuante. Além do total, a página confere **6 medidas sob filtro de categoria** — o `ALL` de M14, M17, M18 e M19 só faz diferença sob filtro — e **as linhas da `Reviews`**, que M20 não vê. Qualquer divergência acima disso é **erro de modelo**, não de arredondamento. A conferência cartão a cartão, com tolerância de exibição, ficou para trás: ela dependia de olhar, e a página se refaz sozinha a cada alteração.

### Passo 3 — conferir o contexto filtrado (o passo que pega o erro real)

O erro comum não aparece no total: aparece ao cruzar. Monte uma matriz com `categoria_n1` nas linhas e M01, M06, M07, M03, M05, M08, M15 e M09 nas colunas, e compare **linha a linha** com `valores_referencia_por_categoria.csv`:

| Categoria | Produtos | Nota mediana | Nota corrigida mediana | Preço mediano | Desconto mediano | Volume mediano | Participação | % Satisf. baixa |
|---|---|---|---|---|---|---|---|---|
| Electronics | 490 | 4,10 | 4,076 | 1.384 | 52 | 9.129,5 | 59,7% | 26,1% |
| Home & Kitchen | 447 | 4,10 | 3,975 | 1.199 | 42 | 2.311 | 12,6% | 32,2% |
| Computers & Accessories | 373 | 4,20 | 4,150 | 399 | 56 | 7.317 | 26,6% | 17,4% |
| Office Products | 31 | 4,30 | 4,248 | 178 | 5 | 4.426 | 0,6% | 0,0% |

Duas somas de controle, na mesma matriz:

- coluna **Produtos** soma **1.341**; +7 suprimidos por T2 = **1.348** ✅
- coluna **Participação** soma **99,5%**; +0,5% suprimido = **100,0%** ✅

Um denominador com `ALLSELECTED` no lugar de `ALL` **não aparece nesta matriz sem segmentação** — os dois dão 99,5%. Aparece com uma segmentação que exclua as 5 categorias pequenas: `ALL` mantém 99,5%, `ALLSELECTED` vai a 100% — **corrigir para `ALL`**. `verifica_pbix.py` pega o mesmo erro comparando a expressão com este catálogo.

### Passo 4 — as quatro armadilhas conhecidas

| Sintoma | Causa | Correção |
|---|---|---|
| M07 devolve número na casa dos trilhões | locale pt-BR leu `4.0657` como inteiro | Power Query → fonte → **English (United States)** |
| M11/M12/M13/M22 devolvem **0**, branco ou erro | `q5/q6/pareto_80` importados como texto | tipar como **Verdadeiro/Falso** no Power Query — não trocar a medida |
| M18 muda ao clicar numa categoria | faltou `ALL` no `PERCENTILEX.INC` | o corte é da base inteira, nunca do contexto |
| M01 devolve **1.351** ou **1.465** | a `BaseAnalitica` saiu de `silver_produtos` ou de `bronze_amazon`, não de `gold_intermediaria` | refazer a origem do passo 11 a partir de `gold_intermediaria` e rodar a `qa_compara_gold` — **nunca** importar o CSV da gold no lugar: ele é o gabarito, e compará-lo consigo mesmo dá zero linhas sem provar nada |

### Passo 5 — registrar

A conferência em si é a página oculta `Conferência` (`conferencia_dax.md`): `Conf · Divergentes` = 0, 33 de 33 linhas. Na página de Recomendações, uma linha: *"Medidas conferidas contra `03_dashboard/valores_referencia.py` em DD/MM/AAAA — 21 de 21 (página Conferência, 33 de 33 linhas)."* Divergência não resolvida vira linha em `method/open_decisions.md`, **não** um número ajustado à mão no visual.

---

## Verificação transversal deste catálogo

- [x] **T1** — a ordenação por nota é M07 (Wilson), com o n de avaliações ao lado
- [x] **T2** — piso de 30 aplicado por medida (padrão `(T2)` em M15) e supressão declarada em M15, M16 e M17; listas nominais de Q5/Q6 (M11, M12) explicitamente fora do piso
- [x] **T3** — as 21 medidas declaram base, n e denominador; M21 mecaniza o rodapé
- [x] **T4** — nenhuma medida ou nota deste arquivo afirma causa; M04 declara ausência de associação
- [x] **T5** — onde há correlação (M04), magnitude e p aparecem juntos
- [x] **T6** — `avaliacoes` nomeado "volume de avaliações" em M02, M08, M15, M18, M19 e M20
- [x] **T7** — nenhuma medida toca `user_id` ou `user_name`; as colunas existem só nas consultas intermediárias, que não carregam (passo 16)
- [x] **T8** — M20 declara unidade, deduplicação por `review_id` e truncamento em 8
- [x] **T9** — M21 usa token `secundario` da paleta v06; nenhuma cor escolhida à mão
- [x] **L5** — M03 e M04 publicados sem símbolo, em rupia indiana, sem conversão

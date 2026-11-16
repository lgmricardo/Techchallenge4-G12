# 📈 GUIA DE GRÁFICOS — MAPEAMENTO PARA O POWER BI

**Amazon Product Performance & Customer Insights · Tech Challenge Fase 4 · Grupo 12**

> **Para que serve.** Abrir o Power BI e montar cada visual sem precisar decidir nada: qual tabela, qual coluna, em qual campo do visual, com qual ordenação e qual formatação. Quem monta não escolhe — segue.
>
> **O que este guia não repete, de propósito.** Os **números esperados** de cada página estão em [`checklist_qualidade.md`](checklist_qualidade.md), que é **gerado** a partir dos dados; o **DAX** de cada medida está em [`medidas_dax.md`](medidas_dax.md); as regras **T1–T9** em [`../method/definitions/regras_transversais_T1_T9.md`](../method/definitions/regras_transversais_T1_T9.md) e as limitações **L1–L8** em [`../method/limitations/limitacoes_obrigatorias.md`](../method/limitations/limitacoes_obrigatorias.md). Repetir número aqui criaria um segundo lugar para ele divergir. Este guia traz **estrutura**; o valor vem do gerado.
>
> **Pré-requisito.** As fases F2 (Power Query), F3 (modelo) e F4 (medidas) de [`INSTRUCOES_MONTAGEM_POWERBI.md`](INSTRUCOES_MONTAGEM_POWERBI.md) concluídas, com `qa_compara_gold` em zero linhas e `Conf · Divergentes` = 0. Montar visual antes disso é montar sobre número não conferido.

---

## Como ler cada ficha

| Linha da ficha | O que diz |
|---|---|
| **Página · Pergunta** | onde o visual mora e qual pergunta ele responde ou apoia |
| **Tipo de visual** | o nome exato no painel *Visualizações* do Desktop em português |
| **Tabela** | de onde vêm os campos |
| **Campos** | `Poço do visual` ← `Tabela[coluna]` ou `[Medida]`, um por linha |
| **Classificar por** | coluna de ordenação, quando a ordem alfabética estaria errada |
| **Filtros do visual** | o que entra no painel *Filtros neste visual* |
| **Interação** | se o visual reage às segmentações da página |
| **Formatação** | o que muda em relação ao padrão |
| **Título · subtítulo** | título escrito como **achado com número**; subtítulo com base, *n* e limiar |
| **Conferir** | onde está o número que o visual tem de exibir |
| **Regras** | as que mordem neste visual |

**Convenções válidas em todos os visuais:** tema v06 importado **antes** do primeiro visual (T9) · um único elemento em âmbar por página · nenhuma pizza ou rosca · no máximo 5 séries · rodapé **M21** em todas as páginas visíveis · nenhum visual de Python, de R ou de loja externa · nenhum valor monetário com símbolo (L5).

---

## O que existe para usar

**Tabelas que carregam no modelo:**

| Tabela | Linhas | Para que serve aqui |
|---|---|---|
| `BaseAnalitica` | 1.348 | tudo que é por produto: cartões, histograma, Pareto, quadrantes, rankings, faixas |
| `Reviews` | 9.255 | contagem de reviews individuais (M20) e a quebra por faixa de nota |
| `tab03` | 4 | os quatro ρ de Spearman do eixo do enunciado |
| `tab05` | 4 | perfil dos quatro arquétipos |
| `tab07` | 4 | AUC por bloco de preditores |
| `tab14` | 105 | n-gramas e Δ TF-IDF |
| `tab23` | 9 | eixos temáticos de QA5 |
| `Conferencia` | 33 | página oculta de conferência |

**As 25 colunas da `BaseAnalitica`** — 17 da camada gold, 7 derivadas no Power Query e `arquetipo`, mesclada da `tab22`:

| Grupo | Colunas |
|---|---|
| Identificação | `product_id` · `product_name` · `category` · `categoria_n1` · `categoria_n2` |
| Medidas do produto | `preco_desc` · `preco_tab` · `desconto` · `avaliacoes` · `nota` · `nota_corrigida` |
| Rótulos de faixa | `engajamento` · `satisfacao` · `faixa_desconto` · `relevancia` · `arquetipo` |
| Marcadores | `q5_risco_vitrine` · `q6_subexplorado` · `pareto_80` |
| Apoio | `n_referencias` · `pareto_posicao` · `pareto_acumulado_pct` |
| Ordenação | `faixa_ordem` · `engaj_ordem` · `satisf_ordem` |

> **As três colunas de ordenação existem por um motivo.** Sem elas o Power BI ordena texto em ordem alfabética, e `81-100%` vem antes de `0-20%`, `alto` antes de `baixo`. Em **toda** coluna de faixa usada em eixo, aplicar *Ferramentas de coluna > Classificar por coluna*. Isso se faz **uma vez por coluna, no modelo**, e vale em todos os visuais.

As 22 medidas estão em [`medidas_dax.md`](medidas_dax.md) com o DAX pronto. Aqui elas aparecem só pelo nome, entre colchetes.

---
## Página 1 · Visão Executiva

Responde "como está o portfólio" em cinco segundos. Nenhum visual aqui exige clique.

### G-01 · Os quatro números que descrevem o catálogo

| | |
|---|---|
| **Página · Pergunta** | 1 · Visão Executiva · indicadores de portfólio |
| **Tipo de visual** | **Cartão** (quatro, lado a lado) |
| **Tabela** | `_Medidas` |
| **Campos** | `Campos` ← `[Nota Mediana]` (M06)<br>`Campos` ← `[Desconto Mediano]` (M05)<br>`Campos` ← `[Preço de Tabela Mediano]` (M04)<br>`Campos` ← `[Volume Mediano de Avaliações]` (M08) |
| **Classificar por** | — |
| **Filtros do visual** | — |
| **Interação** | **não reage** às segmentações: é o retrato da base inteira |
| **Formatação** | Rótulo de chamada 28 pt · **sem símbolo de moeda** · nota com 2 casas · desconto com 0 e `%` · preço e volume com separador de milhar |
| **Título · subtítulo** | Nota mediana 4,10 · desconto mediano 49% — subtítulo: base analítica · n = 1.348 |
| **Conferir** | linha `1 · Visão Executiva` do checklist |
| **Regras** | T3 · T6 · L5 |

### G-02 · O corte que define engajamento alto

| | |
|---|---|
| **Página · Pergunta** | 1 · corte de engajamento alto (Q5 e matriz 2×2) |
| **Tipo de visual** | **Cartão** |
| **Tabela** | `_Medidas` |
| **Campos** | `Campos` ← `[Corte de Engajamento Alto]` (M18) |
| **Classificar por** | — |
| **Filtros do visual** | — |
| **Interação** | **não reage** — o corte é da base inteira. Se mudar ao clicar numa categoria, faltou `ALL` no `PERCENTILEX.INC` |
| **Formatação** | separador de milhar · 0 casas |
| **Título · subtítulo** | Engajamento alto começa em 36.384 avaliações (p90) — subtítulo: percentil 90 da base analítica |
| **Conferir** | linha `1` do checklist |
| **Regras** | T6 — é volume de avaliações, nunca venda |

### G-03 · Como as notas se distribuem

| | |
|---|---|
| **Página · Pergunta** | 1 · Q4 |
| **Tipo de visual** | **Gráfico de colunas agrupadas** |
| **Tabela** | `BaseAnalitica` |
| **Campos** | `Eixo X` ← `BaseAnalitica[nota]`, como **categoria** (não somar)<br>`Eixo Y` ← `BaseAnalitica[product_id]`, agregação **Contagem**<br>`Legenda` ← `BaseAnalitica[satisfacao]` |
| **Classificar por** | `satisfacao` por `satisf_ordem` |
| **Filtros do visual** | — |
| **Interação** | reage às segmentações da página |
| **Formatação** | **Não usar *Novo grupo > Compartimento***: isso cria coluna calculada na `BaseAnalitica` e o `verifica_pbix.py` reprova. A coluna `nota` já tem 25 valores distintos, todos com uma casa — serve como eixo direto. Rótulo direto nas duas faixas extremas |
| **Título · subtítulo** | Um quarto do catálogo está abaixo de 4,0 — subtítulo: base analítica · n = 1.348 · cortes 4,0 e 4,3 |
| **Conferir** | linha `1` do checklist (339 e 418) |
| **Regras** | T3 |

### G-04 · A concentração do engajamento

| | |
|---|---|
| **Página · Pergunta** | 1 · QA2 |
| **Tipo de visual** | **Gráfico de linhas** |
| **Tabela** | `BaseAnalitica` |
| **Campos** | `Eixo X` ← `BaseAnalitica[pareto_posicao]`<br>`Eixo Y` ← `BaseAnalitica[pareto_acumulado_pct]`, agregação **Máximo** |
| **Classificar por** | — |
| **Filtros do visual** | — |
| **Interação** | **não reage** — a curva é da base inteira |
| **Formatação** | *Análise > Linha constante* em **80** no eixo Y, tracejada · o ponto onde a curva cruza os 80% é o **único âmbar da página** · eixo X sem rótulos individuais |
| **Título · subtítulo** | 306 produtos concentram 80% das avaliações — subtítulo: base analítica · n = 1.348 · curva de Pareto |
| **Conferir** | linha `1` do checklist (306 · 22,7%) |
| **Regras** | T6 |

### G-05 · Os dois números do Pareto

| | |
|---|---|
| **Página · Pergunta** | 1 · QA2 |
| **Tipo de visual** | **Cartão** (dois) |
| **Tabela** | `_Medidas` |
| **Campos** | `Campos` ← `[Concentração Pareto 80%]` (M13)<br>`Campos` ← `[% Concentração Pareto 80%]` (M14) |
| **Classificar por** | — |
| **Filtros do visual** | — |
| **Interação** | não reage |
| **Formatação** | M14 como percentual, 1 casa |
| **Título · subtítulo** | 306 produtos · 22,7% da base |
| **Conferir** | linha `1` do checklist |
| **Regras** | T6 |

### G-06 · A insatisfação dentro do Pareto

| | |
|---|---|
| **Página · Pergunta** | 1 · Q8 |
| **Tipo de visual** | **Cartão** |
| **Tabela** | `BaseAnalitica` |
| **Campos** | `Campos` ← `BaseAnalitica[product_id]`, agregação **Contagem** |
| **Classificar por** | — |
| **Filtros do visual** | `BaseAnalitica[pareto_80]` **é Verdadeiro** · `BaseAnalitica[satisfacao]` **é** `baixa` |
| **Interação** | não reage |
| **Formatação** | 0 casas · ao lado, caixa de texto com a taxa da base, para dar referência |
| **Título · subtítulo** | 39 dos 306 produtos do Pareto estão abaixo de 4,0 — metade da taxa da base — subtítulo: subconjunto Pareto, n = 306 |
| **Conferir** | linha `1` do checklist (39 de 306) |
| **Regras** | T3 — o *n* do subconjunto vai no subtítulo |

### G-07 · A matriz de relevância

| | |
|---|---|
| **Página · Pergunta** | 1 · Q1 |
| **Tipo de visual** | **Matriz** |
| **Tabela** | `BaseAnalitica` |
| **Campos** | `Linhas` ← `BaseAnalitica[relevancia]`<br>`Valores` ← `BaseAnalitica[product_id]`, agregação **Contagem** |
| **Classificar por** | — |
| **Filtros do visual** | — |
| **Interação** | não reage |
| **Formatação** | Sem totais · `Intermediário` fica na matriz, e o rodapé diz que ele é o resto da base, não um quadrante de ação |
| **Título · subtítulo** | Âncora 41 · Risco de vitrine 19 · Subexplorado 187 · Cauda frágil 227 — subtítulo: matriz 2×2, volume × nota bruta |
| **Conferir** | linha `1` do checklist |
| **Regras** | T6 — *Subexplorado* é nome de quadrante, nunca rótulo de visibilidade |

---

## Página 2a · Categorias

Só as **4 categorias acima do piso** entram em comparação. As outras 5 aparecem como supressão declarada no rodapé, nunca como barra.

### G-08 · Satisfação por categoria

| | |
|---|---|
| **Página · Pergunta** | 2a · Categorias · Q4 |
| **Tipo de visual** | **Gráfico de barras agrupadas** |
| **Tabela** | `BaseAnalitica` + `_Medidas` |
| **Campos** | `Eixo Y` ← `BaseAnalitica[categoria_n1]`<br>`Eixo X` ← `[% Satisfação Baixa (T2)]` — a **variante com piso**, não a M09 crua<br>`Eixo X` ← `[Nota Corrigida Mediana (T2)]` — variante com piso |
| **Classificar por** | por `[Nota Corrigida Mediana (T2)]`, decrescente |
| **Filtros do visual** | — |
| **Interação** | reage às segmentações |
| **Formatação** | 2 séries · categoria abaixo do piso não aparece, porque a variante devolve `BLANK()` · rodapé do visual: *5 categorias com 7 produtos (0,5%) suprimidas por T2* |
| **Título · subtítulo** | Office Products lidera, com 31 produtos no limite do piso — subtítulo: 4 categorias com n ≥ 30 · base analítica |
| **Conferir** | linha `2a · Categorias` do checklist |
| **Regras** | **T2** · T1 · T3 |

### G-09 · Participação no volume, nas duas versões

| | |
|---|---|
| **Página · Pergunta** | 2a · Q4 · L8 |
| **Tipo de visual** | **Gráfico de barras agrupadas** |
| **Tabela** | `BaseAnalitica` + `_Medidas` |
| **Campos** | `Eixo Y` ← `BaseAnalitica[categoria_n1]`<br>`Eixo X` ← `[Participação da Categoria no Volume (T2)]` (M15, variante com piso)<br>`Eixo X` ← `[Participação no Volume sem Variantes]` — medida de L8, DAX no passo 4.4 do guia de montagem |
| **Classificar por** | por participação, decrescente |
| **Filtros do visual** | — |
| **Interação** | reage |
| **Formatação** | 2 séries lado a lado — **as duas versões andam sempre juntas** (L8) · percentual com 1 casa |
| **Título · subtítulo** | Electronics responde por 59,7% do volume — 53,1% sem contar listagens variantes — subtítulo: base analítica · n = 1.348 |
| **Conferir** | linha `2a` do checklist |
| **Regras** | **L8** · T2 · T6 |

### G-10 · Dispersão de nota por subcategoria

| | |
|---|---|
| **Página · Pergunta** | 2a · Q4 (subcategorias) |
| **Tipo de visual** | **Gráfico de barras agrupadas** |
| **Tabela** | `BaseAnalitica` + `_Medidas` |
| **Campos** | `Eixo Y` ← `BaseAnalitica[categoria_n2]`<br>`Eixo X` ← `[Desvio-Padrão da Nota (T2)]` — medida extra do passo 4.4, com `STDEV.S`<br>`Dicas de ferramenta` ← `[Produtos Ativos]` (M01) |
| **Classificar por** | pelo desvio-padrão, decrescente |
| **Filtros do visual** | `[Produtos Ativos] >= 30` — só as 8 acima do piso |
| **Interação** | reage, **e por isso precisa do filtro de piso**: com uma categoria selecionada, subcategoria cai para n < 30 |
| **Formatação** | **n no rótulo de cada barra** · climatização e fones em **laranja**; nenhum âmbar nesta página |
| **Título · subtítulo** | A dispersão quase dobra entre a primeira e a última subcategoria — subtítulo: 8 subcategorias com n ≥ 30 · cobertura 88,3% |
| **Conferir** | linha `2a` do checklist |
| **Regras** | **T2** · T3 |

### G-11 · A tabela que acompanha a dispersão

| | |
|---|---|
| **Página · Pergunta** | 2a · Q4 (subcategorias) |
| **Tipo de visual** | **Tabela** |
| **Tabela** | `BaseAnalitica` + `_Medidas` |
| **Campos** | `Colunas` ← `BaseAnalitica[categoria_n2]`<br>`Colunas` ← `[Produtos Ativos]` (M01)<br>`Colunas` ← `[Desvio-Padrão da Nota (T2)]`<br>`Colunas` ← `[IQR da Nota (T2)]`<br>`Colunas` ← `[% Satisfação Baixa (T2)]` (M09) |
| **Classificar por** | pelo desvio-padrão, decrescente |
| **Filtros do visual** | `[Produtos Ativos] >= 30` |
| **Interação** | reage |
| **Formatação** | Desvio-padrão e IQR com 3 casas · percentual com 1 casa |
| **Título · subtítulo** | As 8 subcategorias comparáveis, com n, dispersão e taxa abaixo de 4,0 |
| **Conferir** | `tab16_satisfacao_subcategoria.csv` |
| **Regras** | T2 · T3 |

---

## Página 2b · Quadrantes

A página das duas listas nominais. **Lista nominal é exceção declarada ao piso de 30** (T2), desde que o *n* de avaliações apareça produto a produto.

### G-12 · O mapa de volume × nota

| | |
|---|---|
| **Página · Pergunta** | 2b · Quadrantes · Q1 · Q5 |
| **Tipo de visual** | **Gráfico de dispersão** |
| **Tabela** | `BaseAnalitica` |
| **Campos** | `Valores` ← `BaseAnalitica[product_id]` — **obrigatório**: sem ele o visual agrega tudo num ponto só<br>`Eixo X` ← `BaseAnalitica[avaliacoes]`, **Não resumir**<br>`Eixo Y` ← `BaseAnalitica[nota]`, **Não resumir**<br>`Legenda` ← `BaseAnalitica[relevancia]`<br>`Dicas de ferramenta` ← `product_name` · `nota_corrigida` |
| **Classificar por** | — |
| **Filtros do visual** | — |
| **Interação** | reage |
| **Formatação** | Eixo X em **escala logarítmica** (*Formatar > Eixo X > Tipo de escala > Log*) · quatro linhas constantes: X em 36.384 e 4.740, Y em 4,0 e 4,3 · **só o quadrante Q5 em âmbar** · caixa de texto “como ler” no canto |
| **Título · subtítulo** | 19 produtos muito avaliados têm nota abaixo de 4,0 — subtítulo: base analítica · n = 1.348 · cortes p90 e mediana × 4,0 e 4,3 |
| **Conferir** | linha `2b · Quadrantes` do checklist |
| **Regras** | T6 · T3 |

### G-13 · A forma de cada subcategoria

| | |
|---|---|
| **Página · Pergunta** | 2b · Q4 (subcategorias) |
| **Tipo de visual** | **Gráfico de dispersão** |
| **Tabela** | `BaseAnalitica` |
| **Campos** | `Valores` ← `BaseAnalitica[product_id]`<br>`Eixo X` ← `BaseAnalitica[categoria_n2]`<br>`Eixo Y` ← `BaseAnalitica[nota]`, **Não resumir** |
| **Classificar por** | — |
| **Filtros do visual** | `[Produtos Ativos] >= 30` |
| **Interação** | reage |
| **Formatação** | Um ponto por produto, com transparência — o visual mostra **a forma**, não o ranking: fones deslocado para baixo, climatização espalhado |
| **Título · subtítulo** | Fones e climatização concentram a insatisfação acima da base — subtítulo: 8 subcategorias acima do piso · a diferença de dispersão entre os dois é hipótese (Levene p = 0,18) |
| **Conferir** | `tab16` |
| **Regras** | T2 · T3 |

### G-14 · A fila de Q5, nome a nome

| | |
|---|---|
| **Página · Pergunta** | 2b · Q5 |
| **Tipo de visual** | **Tabela** |
| **Tabela** | `BaseAnalitica` |
| **Campos** | `Colunas` ← `product_name` · `categoria_n2` · `avaliacoes` · `nota` · `nota_corrigida` |
| **Classificar por** | por `avaliacoes`, decrescente |
| **Filtros do visual** | `BaseAnalitica[q5_risco_vitrine]` **é Verdadeiro** |
| **Interação** | reage |
| **Formatação** | 19 linhas · `avaliacoes` com separador de milhar · `nota_corrigida` com 3 casas |
| **Título · subtítulo** | Os 19 produtos para revisar esta semana — subtítulo: lista nominal, exceção declarada ao piso (T2), com o n ao lado de cada um |
| **Conferir** | `tab19_q5_risco_vitrine_nominal.csv` |
| **Regras** | **T1** · **T2 exceção** · T7 — nenhuma coluna de consumidor |

### G-15 · O funil e a lista acionável de Q6

| | |
|---|---|
| **Página · Pergunta** | 2b · Q6 |
| **Tipo de visual** | **Cartão** (dois) |
| **Tabela** | `_Medidas` |
| **Campos** | `Campos` ← `[Produtos Q6]` (M12) — o funil<br>`Campos` ← `[Produtos Q6 Acionáveis]` (M22) — depois de Wilson |
| **Classificar por** | — |
| **Filtros do visual** | — |
| **Interação** | reage |
| **Formatação** | Rótulo do primeiro: *funil de triagem*; do segundo: *lista acionável* |
| **Título · subtítulo** | 187 no funil, 61 acionáveis depois da correção de Wilson — subtítulo: nota ≥ 4,3 e volume abaixo da mediana |
| **Conferir** | linha `2b` do checklist |
| **Regras** | **D-1 / T6** — o rótulo publicado é *bem avaliados com baixo volume de avaliações*; **vedado** escrever *baixa visibilidade* · **T1** |

### G-16 · A lista acionável, nome a nome

| | |
|---|---|
| **Página · Pergunta** | 2b · Q6 |
| **Tipo de visual** | **Tabela** |
| **Tabela** | `BaseAnalitica` |
| **Campos** | `Colunas` ← `product_name` · `categoria_n2` · `avaliacoes` · `nota` · `nota_corrigida` |
| **Classificar por** | por `nota_corrigida`, decrescente |
| **Filtros do visual** | `q6_subexplorado` **é Verdadeiro** · `nota_corrigida` **é maior ou igual a** 4,3 |
| **Interação** | reage |
| **Formatação** | 61 linhas |
| **Título · subtítulo** | Os 61 que sobrevivem à correção de Wilson — subtítulo: dos 187 do funil, 126 caem |
| **Conferir** | `tab20_q6_acionavel_nominal.csv` |
| **Regras** | **T1** · T2 exceção · D-1 |

---

## Página 2c · Rankings e arquétipos

### G-17 · Top 10 por nota bruta

| | |
|---|---|
| **Página · Pergunta** | 2c · Rankings · QA6 |
| **Tipo de visual** | **Tabela** |
| **Tabela** | `BaseAnalitica` |
| **Campos** | `Colunas` ← `product_name` · `nota` · `avaliacoes` |
| **Classificar por** | por `nota`, decrescente |
| **Filtros do visual** | *Filtros neste visual* → `product_name` → **N Principais**, 10, por `nota` |
| **Interação** | reage |
| **Formatação** | **Há empate no 10º lugar**: o Top N devolve 11 linhas. Ou declarar *top 10 (11 por empate em 4,7)* no subtítulo, ou desempatar por `avaliacoes` numa medida de ranking |
| **Título · subtítulo** | O ranking que a nota bruta produz — subtítulo: sem correção, mostrado só para contraste |
| **Conferir** | `tab21` e a leitura de QA6 |
| **Regras** | **T1** — este é o ranking **não** homologado, e o subtítulo diz isso |

### G-18 · Top 10 por nota corrigida

| | |
|---|---|
| **Página · Pergunta** | 2c · QA6 |
| **Tipo de visual** | **Tabela** |
| **Tabela** | `BaseAnalitica` |
| **Campos** | `Colunas` ← `product_name` · `nota_corrigida` · `nota` · `avaliacoes` |
| **Classificar por** | por `nota_corrigida`, decrescente |
| **Filtros do visual** | **N Principais**, 10, por `nota_corrigida` |
| **Interação** | reage |
| **Formatação** | `nota_corrigida` com 3 casas · **o n aparece em toda linha** |
| **Título · subtítulo** | O ranking homologado: nota corrigida de Wilson, com o n ao lado — subtítulo: T1, todo ranking por nota usa a corrigida |
| **Conferir** | `tab21_ancoras_nominal.csv` |
| **Regras** | **T1** |

### G-19 · O perfil dos quatro arquétipos

| | |
|---|---|
| **Página · Pergunta** | 2c · QA7 |
| **Tipo de visual** | **Matriz** |
| **Tabela** | `tab05` |
| **Campos** | `Linhas` ← `tab05[arquetipo]`<br>`Valores` ← `n` · `desconto_mediano` · `avaliacoes_medianas` · `nota_mediana` |
| **Classificar por** | por `arquetipo` |
| **Filtros do visual** | — |
| **Interação** | **não reage** — a `tab05` entra sem relacionamento, de propósito: é resultado da base inteira |
| **Formatação** | Sem totais · nota com 1 casa · volume com separador de milhar |
| **Título · subtítulo** | Quatro perfis comerciais — convenção descritiva, não descoberta — subtítulo: k = 4, semente 42, silhueta 0,234 (ML4) |
| **Conferir** | `tab05_arquetipos.csv` |
| **Regras** | **ML4** — nunca apresentar como descoberta · T6 |

### G-20 · O conflito B × D

| | |
|---|---|
| **Página · Pergunta** | 2c · QA7 |
| **Tipo de visual** | **Gráfico de colunas agrupadas** (três pequenos, lado a lado) |
| **Tabela** | `tab05` |
| **Campos** | `Eixo X` ← `tab05[arquetipo]`<br>`Eixo Y` ← `desconto_mediano` (1º painel) · `avaliacoes_medianas` (2º) · `nota_mediana` (3º) |
| **Classificar por** | por `arquetipo` |
| **Filtros do visual** | `tab05[arquetipo]` **está em** `B`, `D` |
| **Interação** | não reage |
| **Formatação** | **2 séries** em cada painel · escala própria por painel |
| **Título · subtítulo** | Desconto quase igual, resultado oposto — subtítulo: B e D descontam 58% e 61%, três pontos de distância |
| **Conferir** | linha `2c` do checklist |
| **Regras** | T4 — associação, nunca causa · T6 |

---

## Página 3 · Preços e Estratégia Comercial

### G-21 · Os três números de preço

| | |
|---|---|
| **Página · Pergunta** | 3 · Preços · Q3 |
| **Tipo de visual** | **Cartão** (três) |
| **Tabela** | `_Medidas` |
| **Campos** | `Campos` ← `[Preço Mediano]` (M03)<br>`Campos` ← `[Preço de Tabela Mediano]` (M04)<br>`Campos` ← `[Desconto Mediano]` (M05) |
| **Classificar por** | — |
| **Filtros do visual** | — |
| **Interação** | reage |
| **Formatação** | **Sem símbolo de moeda** · separador de milhar · o rodapé da página declara *rupia indiana, sem conversão* |
| **Título · subtítulo** | Preço mediano 899, com 49% de desconto — subtítulo: base analítica · valores em rupia indiana (L5) |
| **Conferir** | linha `3 · Preços` do checklist |
| **Regras** | **L5** · T3 |

### G-22 · Nota corrigida por faixa de desconto

| | |
|---|---|
| **Página · Pergunta** | 3 · QA1 |
| **Tipo de visual** | **Gráfico de colunas agrupadas** |
| **Tabela** | `BaseAnalitica` + `_Medidas` |
| **Campos** | `Eixo X` ← `BaseAnalitica[faixa_desconto]`<br>`Eixo Y` ← `[Nota Corrigida Mediana (T2)]`<br>`Eixo Y secundário` ← `[Volume Mediano de Avaliações]` (M08), como linha<br>`Dicas de ferramenta` ← `[Produtos Ativos]` (M01) |
| **Classificar por** | **`faixa_desconto` por `faixa_ordem`** — sem isso as faixas saem em ordem alfabética |
| **Filtros do visual** | — |
| **Interação** | reage, **e por isso usa a variante T2**: com uma categoria selecionada, faixas caem abaixo de 30 |
| **Formatação** | **n no rótulo de cada coluna** · **âmbar só na faixa 81–100%**, a única abaixo de 4,0; as quatro primeiras ficam entre 4,02 e 4,14, diferença sem leitura de negócio (T5) |
| **Título · subtítulo** | Acima de 80% de desconto a nota corrigida cai para 3,906 — a única faixa abaixo de 4,0 — subtítulo: 5 faixas, todas n ≥ 30 |
| **Conferir** | linha `3` do checklist |
| **Regras** | **T1** · T2 · **T5** |

### G-23 · As quatro associações medidas

| | |
|---|---|
| **Página · Pergunta** | 3 · Q3 · QA4 |
| **Tipo de visual** | **Gráfico de barras agrupadas** |
| **Tabela** | `tab03` |
| **Campos** | `Eixo Y` ← `tab03[par]`<br>`Eixo X` ← `tab03[rho]`, **Não resumir**<br>`Dicas de ferramenta` ← `p_valor` · `n` |
| **Classificar por** | por `rho` |
| **Filtros do visual** | — |
| **Interação** | **não reage** — a `tab03` entra sem relacionamento |
| **Formatação** | Barras em torno de **zero** · escala divergente · **p e n no rótulo de cada barra**, não só na dica de ferramenta |
| **Título · subtítulo** | O desconto não é a alavanca — subtítulo: Spearman · base analítica · n = 1.348 · associação, nunca causa |
| **Conferir** | `tab03_correlacoes.csv` |
| **Regras** | **T4** · **T5 — ρ nunca sem o p** |

### G-24 · Preço de tabela contra nota

| | |
|---|---|
| **Página · Pergunta** | 3 · QA4 |
| **Tipo de visual** | **Gráfico de dispersão** |
| **Tabela** | `BaseAnalitica` |
| **Campos** | `Valores` ← `BaseAnalitica[product_id]`<br>`Eixo X` ← `BaseAnalitica[preco_tab]`, **Não resumir**<br>`Eixo Y` ← `BaseAnalitica[nota]`, **Não resumir** |
| **Classificar por** | — |
| **Filtros do visual** | — |
| **Interação** | reage |
| **Formatação** | Eixo X em **escala logarítmica** · uma cor só · **sem linha de tendência** — ela sugeriria associação que o teste não encontra |
| **Título · subtítulo** | Preço de tabela não tem associação detectável com a nota — subtítulo: ρ = +0,032 · p = 0,236 · n = 1.348 |
| **Conferir** | `tab03` |
| **Regras** | **T4** · **T5** · L5 |

---

## Página 4 · Customer Insights

A página que mais precisa de ressalva: tudo aqui é **o que a vitrine exibe**, não o que o cliente pensa (L1).

### G-25 · A ressalva que abre a página

| | |
|---|---|
| **Página · Pergunta** | 4 · Customer Insights · L1 |
| **Tipo de visual** | **Caixa de texto** |
| **Tabela** | — (texto fixo) |
| **Campos** | — |
| **Classificar por** | — |
| **Filtros do visual** | — |
| **Interação** | — |
| **Formatação** | No topo, antes de qualquer visual · texto de L1 por extenso |
| **Título · subtítulo** | No máximo 8 avaliações por produto (média 7,85): o texto é o recorte da vitrine, não a opinião do cliente |
| **Conferir** | linha `4 · Customer Insights` do checklist |
| **Regras** | **L1** — dita na página, não só no rodapé |

### G-26 · O corpus nas três contagens

| | |
|---|---|
| **Página · Pergunta** | 4 · Customer Insights (T8) |
| **Tipo de visual** | **Cartão** (três) + **Tabela** |
| **Tabela** | `BaseAnalitica` · `Reviews` · `_Medidas` |
| **Campos** | `Campos` ← `[Produtos Ativos]` (M01) — blocos<br>`Campos` ← soma de `BaseAnalitica[n_referencias]` — referências<br>`Campos` ← `[Reviews Individuais]` (M20) — reviews distintos<br>Tabela: `Linhas` ← `Reviews[satisfacao]`; `Valores` ← contagem de `Reviews[review_id]` |
| **Classificar por** | `satisfacao` por `satisf_ordem` |
| **Filtros do visual** | — |
| **Interação** | reage |
| **Formatação** | A faixa intermediária em **cinza**, com o rótulo *fora do contraste*: ela existe e não entra no contraste de TF-IDF |
| **Título · subtítulo** | 1.348 blocos · 10.588 referências · 9.255 reviews distintos — subtítulo: a diferença são 1.333 referências repetidas (T8) |
| **Conferir** | linha `4` do checklist |
| **Regras** | **T8** — a unidade é o bloco de review, e a contagem declara qual das três é |

### G-27 · Os termos que separam nota baixa de nota alta

| | |
|---|---|
| **Página · Pergunta** | 4 · Customer Insights (T8) |
| **Tipo de visual** | **Gráfico de barras agrupadas** |
| **Tabela** | `tab14` |
| **Campos** | `Eixo Y` ← `tab14[n_grama]`<br>`Eixo X` ← `tab14[delta_tfidf]`, **Não resumir** |
| **Classificar por** | por `delta_tfidf` |
| **Filtros do visual** | `tab14[secao]` **é** `contraste` · **`tab14[recorte]` é `Electronics`** — é o recorte medido no `05_nlp.ipynb`; sobre a base inteira o sinal se dilui |
| **Interação** | não reage |
| **Formatação** | Barras em torno de zero: Δ positivo de um lado (nota baixa), negativo do outro (nota alta) · **o recorte entra no subtítulo** |
| **Título · subtítulo** | Som aparece onde a nota é baixa; imagem, onde é alta — subtítulo: recorte Electronics · 128 blocos < 4,0 e 136 ≥ 4,3 · unidade: bloco de review |
| **Conferir** | `tab14_ngramas.csv`, coluna `recorte` |
| **Regras** | **T8** · **T3** — recorte e *n* no subtítulo · L1 |

### G-28 · Os temas dos 19 produtos de Q5

| | |
|---|---|
| **Página · Pergunta** | 4 · QA5 |
| **Tipo de visual** | **Gráfico de barras agrupadas** |
| **Tabela** | `tab23` |
| **Campos** | `Eixo Y` ← `tab23[eixo_tematico]`<br>`Eixo X` ← `tab23[blocos_com_o_eixo]`, **Não resumir**<br>`Dicas de ferramenta` ← `blocos_com_marcador_negativo` · `de_um_total_de` |
| **Classificar por** | por `blocos_com_o_eixo`, decrescente |
| **Filtros do visual** | — |
| **Interação** | não reage |
| **Formatação** | **O denominador 19 aparece no rótulo ou no eixo** — sem ele a barra vira proporção de clientes, que a base não tem |
| **Título · subtítulo** | O que as 147 avaliações dos 19 produtos dizem — subtítulo: leitura qualitativa dirigida, **não** TF-IDF · 19 blocos |
| **Conferir** | `tab23_qa5_temas.csv` |
| **Regras** | **L1** · T8 · T2 exceção — denominador sempre visível |

### G-29 · As quatro perguntas de Customer Insights do enunciado

| | |
|---|---|
| **Página · Pergunta** | 4 · D-8 |
| **Tipo de visual** | **Caixa de texto** |
| **Tabela** | — (texto fixo) |
| **Campos** | — |
| **Classificar por** | — |
| **Filtros do visual** | — |
| **Interação** | — |
| **Formatação** | Quatro linhas, cada uma com a pergunta do enunciado e a pergunta do escopo que a responde |
| **Título · subtítulo** | Onde cada pergunta de Customer Insights foi respondida |
| **Conferir** | §7.1 do relatório e `escopo_perguntas.md` §6 |
| **Regras** | torna a cobertura visível ao avaliador |

---

## Página 5 · Recomendações

Nenhuma recomendação em dinheiro, unidade vendida ou tendência — a base não tem variável de venda nem data (L4).

### G-30 · As cinco recomendações, uma por cartão

| | |
|---|---|
| **Página · Pergunta** | 5 · Recomendações · Q8 |
| **Tipo de visual** | **Cartão** (cinco, de texto) |
| **Tabela** | `_Medidas` + texto |
| **Campos** | `[Produtos Q5]` (M11) — revisar os 19 de alta exposição e baixa nota<br>335 — tratar o arquétipo B como candidato a revisão de sortimento<br>`[Produtos Q6 Acionáveis]` (M22) — testar exposição nos 61, não nos 187<br>ρ = −0,150 **(p = 3,1e-08; n = 1.348)** — parar de usar profundidade de desconto como alavanca isolada<br>97,2% — concentrar a governança em três famílias, começando por fones e climatização |
| **Classificar por** | — |
| **Filtros do visual** | — |
| **Interação** | não reage |
| **Formatação** | **ρ nunca sem o p** · um único âmbar na página · nada expresso em receita |
| **Título · subtítulo** | Cinco decisões que cabem nesta base |
| **Conferir** | linha `5 · Recomendações` do checklist |
| **Regras** | **T5** · **L4** · T6 · D-1 |

### G-31 · O AUC por bloco de preditores

| | |
|---|---|
| **Página · Pergunta** | 5 · Q8 |
| **Tipo de visual** | **Gráfico de barras agrupadas** |
| **Tabela** | `tab07` |
| **Campos** | `Eixo Y` ← `tab07[bloco_preditores]`<br>`Eixo X` ← `tab07[auc]`, **Não resumir**<br>`Dicas de ferramenta` ← `desvio_entre_particoes` |
| **Classificar por** | por `auc` |
| **Filtros do visual** | — |
| **Interação** | não reage |
| **Formatação** | 2 casas · **barra de erro** com `desvio_entre_particoes` · linha constante em **0,50**, o piso do acaso |
| **Título · subtítulo** | O sinal é multivariado: nenhum bloco isolado passa de 0,58 — subtítulo: AUC 0,70 ± 0,01 no modelo completo, validação cruzada agrupada por variante (L8) em 5 partições |
| **Conferir** | `tab07_ml2_blocos.csv` |
| **Regras** | **T5** — magnitude com o desvio ao lado · *triagem, não veredito* |

### G-32 · As oito limitações, por extenso

| | |
|---|---|
| **Página · Pergunta** | 5 · — |
| **Tipo de visual** | **Caixa de texto** |
| **Tabela** | — (texto fixo) |
| **Campos** | — |
| **Classificar por** | — |
| **Filtros do visual** | — |
| **Interação** | — |
| **Formatação** | L1 a L8 completas, uma linha cada, mais o registro *21 de 21 medidas conferidas · 33 linhas* |
| **Título · subtítulo** | O que esta base não permite dizer |
| **Conferir** | `limitacoes_obrigatorias.md` |
| **Regras** | **L1–L8** |

### G-36 · Como estes números foram conferidos

| | |
|---|---|
| **Página · Pergunta** | 5 · — |
| **Tipo de visual** | **Caixa de texto** |
| **Tabela** | — (texto fixo) |
| **Campos** | — |
| **Classificar por** | — |
| **Filtros do visual** | — |
| **Interação** | — |
| **Formatação** | Quatro linhas curtas, fonte menor que a dos cartões, no rodapé da área principal. Sem ícone, sem cor de destaque: é nota de rodapé, não chamada |
| **Título · subtítulo** | *"Como estes números foram conferidos"* |
| **Conferir** | o texto está fixado abaixo; os quatro números (33, 36, 41, 0,134) vêm de artefatos que existem no repositório |
| **Regras** | — |

**O texto, por extenso:**

> **Como estes números foram conferidos**
> · A página **Conferência**, oculta neste arquivo, recalcula **33 valores em DAX** e compara com o Python: `Conf · Divergentes` = **0**.
> · `verifica_pbix.py` confere modelo, colunas, relação e as **22 medidas** do arquivo entregue — provado em **38 casos**.
> · O sumário executivo falha se afirmar número que o relatório não sustenta — provado contra **41 números plantados**.
> · O achado central (B × D) é **testado**, não comparado: Mann-Whitney, com o efeito do desconto em **0,134** e o da nota em **0,670**.

**Por que esta caixa existe.** Os quatro mecanismos acima são o que separa um trabalho rigoroso de um trabalho que **demonstra** rigor. Eles estão nos arquivos do repositório — e um avaliador que vê só as sete páginas do dashboard não tem como saber que existem. A caixa ocupa quatro linhas e torna verificável, na tela, o que já é verdade no projeto.

---

## Páginas ocultas

Três, e todas ficam no arquivo entregue. Ocultar é *botão direito na aba > Ocultar página*.

### G-33 · Detalhamento do produto

| | |
|---|---|
| **Página · Pergunta** | Oculta · detalhamento · — |
| **Tipo de visual** | **Tabela** + cartões, em página com *Drill-through* |
| **Tabela** | `BaseAnalitica` |
| **Campos** | `Adicionar campos de detalhamento aqui` ← `BaseAnalitica[product_id]`<br>`Colunas` ← `product_name` · `categoria_n2` · `nota` · `nota_corrigida` · `avaliacoes` · `preco_tab` · `desconto` · `arquetipo` · `relevancia` |
| **Classificar por** | — |
| **Filtros do visual** | — |
| **Interação** | — |
| **Formatação** | Botão *Voltar* automático · rodapé M21 também aqui · **nenhuma coluna de consumidor, nenhum texto de avaliação** |
| **Título · subtítulo** | Ficha do produto |
| **Conferir** | `checklist`, célula *Oculta · detalhamento* |
| **Regras** | **T7** · L5 |

### G-34 · Dica de ferramenta

| | |
|---|---|
| **Página · Pergunta** | Oculta · dica · — |
| **Tipo de visual** | **Página de dica de ferramenta** (*Formatar página > Tamanho da tela > Dica de Ferramenta*) |
| **Tabela** | `_Medidas` |
| **Campos** | `Campos` ← `[Produtos Ativos]` (M01)<br>`Campos` ← `[Nota Corrigida Mediana]` (M07) |
| **Classificar por** | — |
| **Filtros do visual** | — |
| **Interação** | — |
| **Formatação** | Usada pelos visuais de categoria e subcategoria, em *Formatar visual > Dica de ferramenta > Página* |
| **Título · subtítulo** | — |
| **Conferir** | `checklist`, célula *Oculta · dica* |
| **Regras** | **T1** — a corrigida acompanha o n |

### G-35 · Conferência DAX × Python

| | |
|---|---|
| **Página · Pergunta** | Oculta · Conferência · — |
| **Tipo de visual** | **Tabela** + **Cartão** |
| **Tabela** | `Conferencia` + `_Medidas` |
| **Campos** | Tabela: `Colunas` ← `chave` · `nome` · `categoria_n1` · `[Conf · Valor DAX]` · `[Conf · Esperado]` · `[Conf · Diferença]` · `[Conf · Situação]`<br>Cartão: `Campos` ← `[Conf · Divergentes]`<br>Cartão: `Campos` ← `[Conf · Conferidas]` |
| **Classificar por** | por `chave` |
| **Filtros do visual** | — |
| **Interação** | **não reage** — as medidas `Conf` usam `REMOVEFILTERS`, de propósito |
| **Formatação** | 33 linhas · `Conf · Divergentes` tem de exibir **0** |
| **Título · subtítulo** | 33 de 33 linhas conferidas, 0 divergentes |
| **Conferir** | `conferencia_dax.md` e `conferencia_referencia.csv` |
| **Regras** | é o portão B e o portão C: nenhuma página fecha com divergente > 0 |

---
## Antes de fechar cada página

| Conferência | Onde |
|---|---|
| o número exibido bate com o publicado | [`checklist_qualidade.md`](checklist_qualidade.md), na linha da página |
| um único elemento em âmbar | regra dos 10% · T9 |
| nenhuma pizza ou rosca, no máximo 5 séries | T9 |
| rodapé **M21** presente, com base e *n* filtrado | T3 |
| nenhum rótulo diz "venda", "receita", "demanda" ou "visibilidade" | T6 · D-1 |
| nenhuma coluna de consumidor, nenhum trecho de avaliação | T7 |
| nenhum valor monetário com símbolo | L5 |

Ao fim da fase: `Conf · Divergentes` = 0 · `qa_compara_gold` com zero linhas · `python3 03_dashboard/verifica_pbix.py` com saída 0.

---

*Este guia detalha a seção 6 de [`INSTRUCOES_MONTAGEM_POWERBI.md`](INSTRUCOES_MONTAGEM_POWERBI.md). Os números esperados são gerados em [`checklist_qualidade.md`](checklist_qualidade.md); o DAX, em [`medidas_dax.md`](medidas_dax.md). Havendo divergência entre este guia e um desses dois, vale o gerado.*

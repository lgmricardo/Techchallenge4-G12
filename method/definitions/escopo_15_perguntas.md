# 🎯 ESCOPO ANALÍTICO — 15 PERGUNTAS
**Status: FECHADO.** Revoga todos os conjuntos anteriores. Nenhuma pergunta foi adicionada ou removida pela auditoria de 23/09/2026.

## 1. As 8 do enunciado
O enunciado as apresenta como **sugestões**; o projeto optou por respondê-las integralmente, inclusive as inconclusivas, com justificativa.

| # | Pergunta | Página do dashboard | Situação |
|---|---|---|---|
| Q1 | Quais categorias e produtos apresentam maior relevância? | Produtos e Categorias | ✅ **matriz de relevância 2×2** (D-2, fechada em 24/09/2026): Âncora 41 · Risco 19 · Subexplorado 187 · Cauda frágil 227. Sem índice composto |
| Q2 | Quais produtos possuem maior engajamento? | Visão Executiva | corte fechado: p90 = 36.384 |
| Q3 | Existe relação entre descontos e avaliações? | Preços | medido: ρ = −0,150 · p = 3,1e-08 |
| Q4 | Quais categorias apresentam maior ou menor satisfação? | Produtos e Categorias | só as 4 acima do piso (T2) |
| Q5 | Existem produtos com alto engajamento e baixa avaliação? | Produtos e Categorias | **19 produtos** |
| Q6 | Existem produtos com boa avaliação e pouca visibilidade? | Produtos e Categorias | ✅ **187** pelo funil de nota bruta · **61** após Wilson, a lista acionável (D-1, fechada em 24/09/2026 — volume abaixo da mediana como *proxy declarado de exposição*) |
| Q7 | Quais padrões podem ser identificados nas avaliações? | Customer Insights | corpus 339 e 418 blocos |
| Q8 | Quais oportunidades ou riscos para o negócio? | Recomendações | consolida as demais |

## 2. As 7 próprias do grupo

| # | Pergunta | Método | Página |
|---|---|---|---|
| QA1 | Existe faixa de desconto em que **nota e engajamento** se sustentam? | faixas de desconto com nota corrigida e volume; absorve o antigo teste de corte em 60% | Preços |
| QA2 | Quantos produtos concentram 80% das avaliações? | curva de Pareto — **306 = 22,7%** | Visão Executiva |
| QA3 | Quais **subcategorias (nível 2)** têm maior dispersão de notas? | desvio-padrão e IQR; 8 grupos acima do piso, 88,3% de cobertura | Produtos e Categorias |
| QA4 | O preço de tabela explica a satisfação? | correlação — **ρ = +0,032, p = 0,236: não há associação** | Preços |
| QA5 | Quais temas de reclamação predominam nos produtos de alto engajamento e baixa nota? | **leitura qualitativa dirigida com protocolo de codificação — não TF-IDF**; 19 produtos, 147 avaliações | Customer Insights |
| QA6 | Os produtos no topo do ranking merecem estar lá? | correção de variância pelo **limite inferior de Wilson a 95%** (D-3, fechada em 01/10/2026); a média bayesiana foi descartada por exigir arbitrar um *prior* | Produtos e Categorias |
| QA7 | Quais arquétipos comerciais emergem ao agrupar por preço, desconto, nota e volume? | segmentação descritiva multivariada, **k = 4**, semente 42 | Produtos e Categorias |

## 3. Fora do escopo
Divergência entre desconto declarado e recalculado: medida em **0,50 p.p. no máximo**. Deixa de ser pergunta e vira **controle de qualidade**, reportável em uma linha como achado positivo.

## 4. Nota sobre método textual
O TF-IDF **permanece válido em Q7**, onde há 339 e 418 blocos. A vedação vale **apenas para QA5**, cujo corpus de 19 blocos não sustenta o método. As duas decisões coexistem e não se contradizem.

## 5. As definições que bloqueavam Q1 e Q6 — fechadas

Nenhuma pergunta deste escopo depende hoje de decisão não tomada. As três que bloqueavam, e como fecharam:

| Decisão | Bloqueava | Fechada em | Resolução |
|---|---|---|---|
| **D-2** | Q1 — fórmula de relevância | 24/09/2026 | matriz 2×2 sobre os cortes já operacionais; **nenhum índice composto**, porque um peso arbitrado não tem resposta defensável |
| **D-1** | Q6 — rótulo de visibilidade | 24/09/2026 | volume abaixo da mediana como **proxy declarado de exposição**; fica **vedado** escrever "baixa visibilidade" em qualquer visual |
| **D-3** | QA6 — método de correção | 01/10/2026 | limite inferior de **Wilson a 95%**, com a ressalva de ser aproximação para nota 1–5 declarada no relatório |

Nenhuma das três criou limiar novo: todas reaproveitaram cortes já medidos e publicados. As oito decisões do projeto estão fechadas. Ver `method/open_decisions.md`.

## 6. Cobertura das perguntas de Customer Insights do enunciado

O enunciado traz, na seção **Customer Insights** (pág. 4–5), quatro perguntas próprias, separadas das 8 orientadoras. Elas são respondidas assim:

| Pergunta do enunciado | Respondida por | Corpus |
|---|---|---|
| O que os clientes mais valorizam? | **Q7** · ML3 | 418 blocos de nota ≥ 4,3 (2.878 reviews distintos) |
| Quais problemas aparecem com maior frequência? | **Q7** + **QA5** | 339 blocos de nota < 4,0 (2.502 distintos) + leitura dirigida dos 19 de Q5 |
| Quais padrões estão presentes em avaliações positivas? | **Q7** | contraste entre as duas faixas |
| Quais temas aparecem em avaliações negativas? | **Q7** + **QA5** | 339 blocos + leitura qualitativa dirigida |

*Decisão D-8, fechada em 01/10/2026. Nenhuma pergunta foi acrescentada ao escopo — a tabela apenas torna visível uma cobertura que já existia.*

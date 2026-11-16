# 🎯 ESCOPO ANALÍTICO — 12 PERGUNTAS
**Status: FECHADO — versão final de 10/11/2026.** Entram as perguntas cuja resposta o dashboard entregue mostra por inteiro. A numeração é a do dashboard, e por isso não é contínua.

## 1. As 6 do enunciado
O enunciado as apresenta como **sugestões**; o projeto respondeu as que o dashboard mostra por inteiro, inclusive as inconclusivas, com justificativa.

| # | Pergunta | Página do dashboard | Situação |
|---|---|---|---|
| Q1 | Quais categorias e produtos apresentam maior relevância? | 1 · Visão Executiva | ✅ **matriz de relevância 2×2** (D-2, fechada em 24/09/2026): Âncora 41 · Risco 19 · Subexplorado 187 · Cauda frágil 227. Sem índice composto |
| Q3 | Existe relação entre descontos e avaliações? | 3 · Preços e estratégia | medido: ρ = −0,150 · p = 3,1e-08 |
| Q4 | Quais categorias apresentam maior ou menor satisfação? | 2a · Categorias | só as 4 acima do piso (T2) |
| Q5 | Existem produtos com alto engajamento e baixa avaliação? | 2b · Quadrantes | **19 produtos** |
| Q6 | Existem produtos com boa avaliação e pouca visibilidade? | 2b · Quadrantes | ✅ **187** pelo funil de nota bruta · **61** após Wilson, a lista acionável (D-1, fechada em 24/09/2026 — volume abaixo da mediana como *proxy declarado de exposição*) |
| Q8 | Quais oportunidades ou riscos para o negócio? | 5 · Recomendações | consolida as demais |

## 2. As 6 próprias do grupo

| # | Pergunta | Método | Página |
|---|---|---|---|
| QA1 | Existe faixa de desconto em que **nota e engajamento** se sustentam? | faixas de desconto com nota corrigida e volume; absorve o antigo teste de corte em 60% | 3 · Preços e estratégia |
| QA2 | Quantos produtos concentram 80% das avaliações? | curva de Pareto — **306 = 22,7%** | 1 · Visão Executiva |
| QA4 | O preço de tabela explica a satisfação? | correlação — **ρ = +0,032, p = 0,236: não há associação** | 3 · Preços e estratégia |
| QA5 | Quais temas de reclamação predominam nos produtos de alto engajamento e baixa nota? | **leitura qualitativa dirigida com protocolo de codificação — não TF-IDF**; 19 produtos, 147 avaliações | 4 · Customer Insights |
| QA6 | Os produtos no topo do ranking merecem estar lá? | correção de variância pelo **limite inferior de Wilson a 95%** (D-3, fechada em 01/10/2026); a média bayesiana foi descartada por exigir arbitrar um *prior* | 2c · Rankings e arquétipos |
| QA7 | Quais arquétipos comerciais emergem ao agrupar por preço, desconto, nota e volume? | segmentação descritiva multivariada, **k = 4**, semente 42 | 2c · Rankings e arquétipos |

## 3. Fora do escopo
Divergência entre desconto declarado e recalculado: medida em **0,50 p.p. no máximo**. Deixa de ser pergunta e vira **controle de qualidade**.

## 4. Nota sobre método textual
O TF-IDF é **vedado na QA5**: o corpus de 19 blocos não sustenta estatística de frequência. Ali o método é leitura qualitativa dirigida com protocolo de codificação, e a contagem é sempre sobre o denominador 19.

## 5. As definições que bloqueavam Q1 e Q6 — fechadas

Nenhuma pergunta deste escopo depende hoje de decisão não tomada. As três que bloqueavam, e como fecharam:

| Decisão | Bloqueava | Fechada em | Resolução |
|---|---|---|---|
| **D-2** | Q1 — fórmula de relevância | 24/09/2026 | matriz 2×2 sobre os cortes já operacionais; **nenhum índice composto**, porque um peso arbitrado não tem resposta defensável |
| **D-1** | Q6 — rótulo de visibilidade | 24/09/2026 | volume abaixo da mediana como **proxy declarado de exposição**; fica **vedado** escrever "baixa visibilidade" em qualquer visual |
| **D-3** | QA6 — método de correção | 01/10/2026 | limite inferior de **Wilson a 95%**, com a ressalva de ser aproximação para nota 1–5 declarada no relatório |

Nenhuma das três criou limiar novo: todas reaproveitaram cortes já medidos e publicados. As oito decisões do projeto estão fechadas. Ver `method/open_decisions.md`.

## 6. Cobertura das perguntas de Customer Insights do enunciado

Na seção **Customer Insights** (pág. 4–5), o enunciado traz perguntas próprias, separadas das orientadoras. As cobertas por este escopo são respondidas assim:

| Pergunta do enunciado | Respondida por | Corpus |
|---|---|---|
| Quais problemas aparecem com maior frequência? | **QA5** | leitura dirigida das 147 avaliações dos 19 produtos de Q5 |
| Quais temas aparecem em avaliações negativas? | **QA5** | os mesmos 19 blocos de alto engajamento e nota abaixo de 4,0 |

*Decisão D-8, fechada em 01/10/2026: declarar onde cada pergunta de Customer Insights é respondida.*

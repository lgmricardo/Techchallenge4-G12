# Folha de defesa — os 61 números falados no vídeo

> **Gerada por `src/gera_resumo.py`. Não editar à mão.** Lê `04_video/tab_roteiro_numeros.csv` e localiza cada número no relatório técnico; falha se um número falado não estiver no relatório. Para imprimir: `defense_sheet_phase4_v1_powerbi.pdf`.

| Bloco | Valor falado | Indicador | Base · n | Onde está | Regra que o protege |
|---|---|---|---|---|---|
| 1 Contexto | **1.465** | linhas na base bruta | Bruta · 1.465 | §2.3 | — |
| 1 Contexto | **1.351** | produtos após deduplicação | Produtos · 1.351 | §3.3 | — |
| 1 Contexto | **1.348** | produtos na base analítica | Analítica · 1.348 | §2.4 | T3 — base padrão de toda análise cruzada |
| 1 Contexto | **9** | categorias de nível 1 na base | Analítica · 1.348 | §2.6 | — |
| 1 Contexto | **4** | categorias com n ≥ 30 (T2) | Analítica · 1.348 | §2.6 | T2 |
| 1 Contexto | **7** | produtos nas categorias abaixo do piso | Analítica · 1.348 | §2.6 | T2 / L3 |
| 1 Contexto | **97,2%** | cobertura das 3 maiores categorias | Analítica · 1.348 | §2.6 | L3 |
| 1 Contexto | **490** | produtos em Electronics | Analítica · 1.348 | §2.6 | T2 |
| 1 Contexto | **447** | produtos em Home&Kitchen | Analítica · 1.348 | §2.6 | T2 |
| 1 Contexto | **373** | produtos em Computers&Accessories | Analítica · 1.348 | §2.6 | T2 |
| 1 Contexto | **31** | produtos em OfficeProducts | Analítica · 1.348 | §2.6 | T2 |
| 2 Indicadores | **4,10** | nota mediana | Analítica · 1.348 | §2.5 | T1 — ranking usa nota_corrigida |
| 2 Indicadores | **49%** | desconto mediano | Analítica · 1.348 | §2.5 | — |
| 2 Indicadores | **1.795** | preço de tabela mediano (rupia, sem conversão) | Analítica · 1.348 | §2.5 | L5 |
| 2 Indicadores | **4.740** | volume mediano de avaliações | Analítica · 1.348 | §4.3 | T6 |
| 2 Indicadores | **36.384** | corte de engajamento alto (p90 de avaliações) | Analítica · 1.348 | §4.3 | T6 |
| 2 Indicadores | **339 (25,1%)** | produtos com nota < 4,0 | Analítica · 1.348 | §4.5 | — |
| 2 Indicadores | **418** | produtos com nota ≥ 4,3 | Analítica · 1.348 | §4.5 | — |
| 2 Indicadores | **306 (22,7%)** | produtos que concentram 80% das avaliações | Analítica · 1.348 | §5.12 | T6 / QA2 |
| 2 Indicadores | **39 (12,7%)** | produtos do Pareto 80% com nota < 4,0 | Analítica · 306 | §5.12 | T6 — atenção é volume de avaliações · contraste com a taxa da base, 25,1% |
| 3 Insights | **ρ −0,150 · p 3,1e−08** | Spearman desconto × nota | Analítica · 1.348 | §5.5 | T4 associação, nunca causa · T5 magnitude com significância |
| 3 Insights | **ρ −0,132 · p 1,1e−06** | Spearman desconto × engajamento | Analítica · 1.348 | §5.5 | T4 associação, nunca causa · T5 magnitude com significância |
| 3 Insights | **ρ +0,032 · p 2,4e−01** | Spearman preço de tabela × nota | Analítica · 1.348 | §5.14 | T4 associação, nunca causa · T5 magnitude com significância |
| 3 Insights | **ρ +0,193 · p 8,3e−13** | Spearman engajamento × nota | Analítica · 1.348 | §5.5 | T4 associação, nunca causa · T5 magnitude com significância |
| 3 Insights | **19** | Q5 — engajamento alto e nota < 4,0 | Analítica · 1.348 | §5.7 | T2 exceção nominal |
| 3 Insights | **187** | Q6 — funil: nota ≥ 4,3 e volume abaixo da mediana | Analítica · 1.348 | §5.8 | T6 proxy declarado de exposição · vedado dizer 'baixa visibilidade' |
| 3 Insights | **61** | Q6 — lista acionável: funil já corrigido por Wilson | Analítica · 1.348 | §5.8 | T1 · 126 dos 187 caem na correção · medida M22 |
| 3 Insights | **126** | Q6 — produtos que caem na correção de Wilson | Analítica · 1.348 | §5.19 | T1 · 187 do funil menos 61 acionáveis |
| 3 Insights | **0,215** | silhueta k=3 | Analítica · 1.348 | §6.5 | ML4 — sem estrutura natural de agrupamento |
| 3 Insights | **0,234** | silhueta k=4 | Analítica · 1.348 | §6.5 | ML4 — sem estrutura natural de agrupamento |
| 3 Insights | **0,237** | silhueta k=5 | Analítica · 1.348 | §6.5 | ML4 — sem estrutura natural de agrupamento |
| 3 Insights | **k=5 (0,237)** | k de silhueta máxima | Analítica · 1.348 | §6.5 | ML4 — adotado k=4 por interpretabilidade |
| 3 Insights | **268 · 32% · 6.836 · 4,2** | arquétipo A — n · desconto · avaliações · nota | Analítica · 1.348 | §6.5 | ML4 — descritivo, nunca descoberta |
| 3 Insights | **335 · 58% · 468 · 3,9** | arquétipo B — n · desconto · avaliações · nota | Analítica · 1.348 | §6.5 | ML4 — descritivo, nunca descoberta |
| 3 Insights | **298 · 22% · 6.534 · 4,2** | arquétipo C — n · desconto · avaliações · nota | Analítica · 1.348 | §6.5 | ML4 — descritivo, nunca descoberta |
| 3 Insights | **447 · 61% · 13.120 · 4,2** | arquétipo D — n · desconto · avaliações · nota | Analítica · 1.348 | §6.5 | ML4 — descritivo, nunca descoberta |
| 3 Insights | **3 p.p.** | conflito B × D — distância de desconto | Analítica · 1.348 | §5.17 | T4 |
| 3 Insights | **28x** | conflito B × D — razão de volume de avaliações | Analítica · 1.348 | §5.17 | T6 — volume, nunca venda |
| 4 Dashboard | **8** | subcategorias de nível 2 com n ≥ 30 | Analítica · 1.348 | §5.13 | T2 / QA3 |
| 4 Dashboard | **88,3%** | cobertura das subcategorias acima do piso | Analítica · 1.348 | §5.13 | T2 / QA3 |
| 5 Customer Insights | **10.588** | referências de avaliação na base | Analítica · 1.348 | §7.3 | T8 — unidade: bloco de review |
| 5 Customer Insights | **9.255** | reviews distintos após deduplicar por review_id | Analítica · 1.348 | §7.3 | T8 |
| 5 Customer Insights | **1.333** | referências repetidas descartadas | Analítica · 1.348 | §7.3 | T8 |
| 5 Customer Insights | **7,85 · máx 8** | avaliações por produto — média e máximo | Analítica · 1.348 | §7.5 | L1 — truncamento na vitrine |
| 5 Customer Insights | **339** | blocos de review com nota < 4,0 | Analítica · 1.348 | §6.4 | ML3 / T8 |
| 5 Customer Insights | **418** | blocos de review com nota ≥ 4,3 | Analítica · 1.348 | §6.4 | ML3 / T8 |
| 5 Customer Insights | **591 (44%)** | faixa intermediária fora do contraste | Analítica · 1.348 | §6.4 | ML3 — lacuna declarada |
| 5 Customer Insights | **147** | avaliações disponíveis nos 19 produtos de Q5 | Analítica · 19 | §5.7 | QA5 — leitura dirigida, não TF-IDF |
| 5 Customer Insights | **52,4%** | fones — produtos abaixo de 4,0 | Analítica · 63 | §5.18 | T2 n = 63 ≥ 30 · subcategoria de nível 2 |
| 5 Customer Insights | **0,224** | fones — dispersão da nota (desvio-padrão) | Analítica · 63 | §5.13 | QA3 — dispersão observada; a diferença não é significativa (Levene p = 0,18) |
| 5 Customer Insights | **37,9%** | climatização — produtos abaixo de 4,0 | Analítica · 116 | §5.18 | T2 n = 116 ≥ 30 · subcategoria de nível 2 |
| 5 Customer Insights | **0,346** | climatização — dispersão da nota (desvio-padrão) | Analítica · 116 | §5.13 | QA3 — dispersão observada; a diferença não é significativa (Levene p = 0,18) |
| 5 Customer Insights | **25,1%** | taxa da base abaixo de 4,0 — para comparação | Analítica · 1.348 | §5.18 | sem ela, 52% e 38% não têm referência |
| 6 Recomendações | **0,56** | ML2 — AUC só com volume de avaliações | Analítica · 1.348 | §6.3 | ML2 — bloco isolado, duas casas; validação agrupada por variante (L8) |
| 6 Recomendações | **0,58** | ML2 — AUC só com comerciais | Analítica · 1.348 | §6.3 | ML2 — bloco isolado, duas casas; validação agrupada por variante (L8) |
| 6 Recomendações | **0,66** | ML2 — AUC só com comerciais + categoria | Analítica · 1.348 | §6.3 | ML2 — bloco isolado, duas casas; validação agrupada por variante (L8) |
| 6 Recomendações | **0,70 ± 0,01** | ML2 — AUC do modelo completo | Analítica · 1.348 | §6.3 | ML2 — duas casas; discriminação moderada · validação agrupada por variante (L8) |
| 6 Recomendações | **25,1%** | ML2 — taxa de risco (nota < 4,0) | Analítica · 1.348 | §6.3 | ML2 |
| 6 Recomendações | **335** | produtos no arquétipo B (revisão de sortimento) | Analítica · 1.348 | §5.17 | L4 — sem variável de venda |
| 6 Recomendações | **0–20% · Wilson 4,136** | faixa de desconto com maior nota corrigida (QA1) | Analítica · 175 | §5.11 | T1 / T2 — todas as faixas acima do piso · T5 — 0,053 acima da segunda, sem leitura de negócio |
| 6 Recomendações | **81–100% · Wilson 3,906** | faixa de desconto abaixo do limiar de satisfação (QA1) | Analítica · 51 | §5.11 | T1 / T2 — é o achado defensável de QA1 |

**Regras e limitações citadas:** **T1** Todo ranking por nota usa a nota corrigida de Wilson, com o n ao lado · **T2** Nenhum grupo agregado com n < 30 é ranqueado; supressão declarada. Listas nominais são exceção · **T3** Todo visual declara fonte, base, n efetivo e limiar · **T4** Vedada linguagem causal — correlação indica associação · **T5** Magnitude sempre junto com significância · **T6** rating_count é volume de avaliações — nunca vendas, receita ou demanda. Vedado "baixa visibilidade" · **T8** Todo método textual declara unidade, deduplica por review_id e cita o truncamento em 8 · **L1** Truncamento em 8 avaliações por produto · **L3** Concentração de categorias · **L4** Ausência de variável de venda · **L5** Mercado e moeda · **L8** Listagens variantes compartilham as mesmas avaliações

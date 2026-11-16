# 🤖 REGISTRO DE MACHINE LEARNING — QUADRO FECHADO
**Base de todas as medições: n = 1.348.** Nenhuma aplicação entra sem número que a sustente e sem destino declarado na entrega.

| # | Aplicação | Status | Destino | Métrica |
|---|---|---|---|---|
| ML1 | Regressão explicativa da nota | **Absorvida no ML2** — decisão fechada em 23/09/2026, não reabrir | — | R² 0,10 (justificativa da absorção) |
| ML2 | **Atributos associados à baixa satisfação** | Adotado | Q5, apoio a Q8 | AUC **0,70 ± 0,01** |
| ML3 | n-gramas e TF-IDF sobre blocos de review | Mantido fora do relatório final | página 4 do dashboard (`tab14`) | 339 e 418 blocos |
| ML4 | Segmentação descritiva multivariada | Obrigatório | QA7 | **k = 4**, semente 42, silhueta 0,234 |

## ML2 — definição
- **Alvo:** `rating` < 4,0 — mesmo limiar dos cortes operacionais, sem critério paralelo
- **Preditores:** preço de tabela · preço com desconto · percentual de desconto · volume de avaliações · categoria nível 1
- **Vedação de vazamento:** nenhuma variável derivada de `rating` entra nos preditores, e **nenhuma listagem-gêmea (L8) fica dividida entre treino e teste** — a validação agrupa as variantes
- **Saída:** a **escada de AUC por bloco de preditores**, a que o relatório (§6.3) e a página 5 do dashboard publicam. O ranking de importância de atributos continua gerado (`tab25`), fora do relatório final. Não existe coluna de probabilidade de risco por produto — a formulação anterior está revogada
- **Evidência:** validação cruzada agrupada por variante em 5 partes, taxa de risco 25,1%. Nenhum bloco isolado chega perto do conjunto — volume **0,556** · comerciais **0,583** · comerciais+categoria **0,658** · completo **0,70** (Random Forest 300, `random_state=42`, `StratifiedGroupKFold(5, shuffle=True, random_state=42)` agrupada por `(rating_count, rating)`). O sinal é multivariado — é exatamente por isso que o modelo existe.
  > ⚠️ **Valores anteriores revogados.** O registro trazia 0,640 · 0,655 · 0,715 · 0,755, medidos sob especificação não declarada, e depois 0,622 · 0,624 · 0,691 · 0,750 sob validação ingênua — que **inflava o AUC por vazamento de listagens-gêmeas** (L8): de 0,034 a 0,066 por bloco, medido em 31/10/2026 (`tab27_ml2_vazamento.csv`). Os valores acima são os de `02_results/tables/tab07_ml2_blocos.csv`, reproduzíveis com `python3 src/gera_figuras.py`. O desvio entre as cinco partições é de até **±0,039**, o que torna a terceira casa decimal indefensável: reportar duas
- **Especificação de reprodução (obrigatória — sem ela o número não é verificável):** Random Forest, 300 árvores, `random_state=42`; preditores numéricos padronizados e categoria nível 1 em *one-hot*; `StratifiedGroupKFold(n_splits=5, shuffle=True, random_state=42)`, agrupada por `(rating_count, rating)`; a validação mora em `src/ml2.py`.
  **⚠️ O embaralhamento é obrigatório.** O CSV vem ordenado por categoria; sem `shuffle=True`, o `StratifiedKFold` ingênuo deixa as partições quase puras por categoria e o AUC medido cai para **≈0,33** — pior que o acaso. Quem reproduzir sem essa cláusula concluirá, de boa-fé, que o modelo não funciona.
- **Ressalva obrigatória:** o AUC é **0,70 ± 0,01** entre as cinco partições. Publicar três casas decimais é precisão que a medição não sustenta — reportar `0,70`, com o desvio ao lado. É um poder de discriminação moderado, e isso se declara

## ML3 — definição
- **Unidade de modelagem:** o **bloco** de review, rotulado pela nota do produto
- **Corpus, com as três contagens lado a lado:**

| Faixa | Blocos | Referências | **Reviews distintos** |
|---|---|---|---|
| Nota < 4,0 | 339 | 2.652 | **2.502** |
| Nota ≥ 4,3 | 418 | 3.262 | **2.878** |
| Faixa 4,0–4,29 | 591 | 4.674 | **3.875** |

- **Pipeline:** remoção de URLs → remoção de tokens não latinos → stopwords em inglês → n-gramas
- **Lacuna declarada:** a faixa intermediária (591 produtos, 44% do portfólio) fica fora do contraste entre satisfação alta e baixa. Isso é escolha de método, e deve ser dito

## ML4 — definição e redação honesta do `k`
- **Variáveis:** **preço de tabela** (log natural), desconto, volume de avaliações (log natural) e nota — as quatro padronizadas (z-score). *A leitura de "preço" é decisiva: com preço com desconto a curva achata — k=2 → 0,235 · k=4 → 0,232 · k=5 → 0,236 — e o máximo deixa de ter vencedor claro.*
- **Silhueta medida:** k=2 → 0,218 · k=3 → 0,215 · **k=4 → 0,234** · k=5 → 0,237 · k=6 → 0,227 · k=7 → 0,219
- **Redação obrigatória no material:** *"o coeficiente de silhueta foi calculado para k de 2 a 7 e atinge o máximo em k = 5 (0,237). Adotou-se **k = 4** (0,234) por interpretabilidade, com diferença estatística desprezível entre os dois."*
  Dizer "k escolhido pela silhueta" é impreciso e derruba o argumento se questionado.
- **Fraqueza declarada:** silhueta ≤ 0,237 indica que **não há estrutura natural de agrupamento** nesta base. Os arquétipos são convenção descritiva útil, **nunca apresentados como descoberta**
- **Fronteira:** clusterização é vedada para definir limiar de qualquer conceito univariado — relevância, engajamento, visibilidade e satisfação seguem cortes fixos. Fora de QA7, vedada
- **Reprodutibilidade:** semente 42, k testados de 2 a 7, curva de silhueta e variáveis padronizadas registrados no notebook

### Arquétipos medidos (k = 4, n = 1.348)

| Grupo | n | Preço mediano | Desconto | Avaliações | Nota |
|---|---|---|---|---|---|
| A — Ticket alto, desconto contido | 268 | 14.999 | 32% | 6.836 | 4,2 |
| **B — Desconto agressivo sem tração** | 335 | 1.290 | 58% | 468 | **3,9** |
| C — Baixo preço, pouco desconto | 298 | 900 | 22% | 6.534 | 4,2 |
| D — Alto giro com desconto alto | 447 | 1.500 | 61% | 13.120 | 4,2 |

Soma = 1348 ✅.

> ⚠️ **Sensibilidade de versão.** Estes valores reproduzem com `scikit-learn==1.9.1`, a versão fixada em `requirements.txt`. O `random_state=42` **não** garante o mesmo particionamento entre versões diferentes da biblioteca: medimos variação de 1 a 2 produtos por grupo. Quem soltar a pinagem precisa **regerar esta tabela** com `python3 src/gera_figuras.py`, não apenas reexecutar. A fonte executável é `02_results/tables/tab05_arquetipos.csv`. **Leitura descritiva** (convenção, não descoberta — ver fraqueza declarada acima): B e D têm desconto praticamente igual (58% × 61%) e divergem em tudo o mais — D tem 28 vezes mais avaliações; B é o único grupo abaixo do limiar de satisfação. O desconto profundo não separa os dois. **B é o candidato natural a revisão de sortimento.**

## Aplicações avaliadas e descartadas

| Aplicação | Motivo |
|---|---|
| Previsão de vendas, receita ou demanda | não existe variável de venda na base |
| Séries temporais e forecast | ausência total de dimensão temporal |
| Filtragem colaborativa | apenas **909 de 9.036 usuários distintos (10,1%)** avaliam mais de um produto — base analítica |
| Detecção de anomalia em preço | sem histórico, reduz-se a outlier univariado |
| Classificador de sentimento pré-treinado | reprodutibilidade frágil no escopo do módulo |
| Regressão para prever `rating_count` | prever visibilidade não gera decisão |

## Teto de esforço
Os 9 critérios de avaliação do enunciado **não incluem modelagem**. Nenhuma aplicação consome tempo adicional depois que seu destino no `.pbix` ou no vídeo estiver montado.

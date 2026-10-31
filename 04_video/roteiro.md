# 🎬 ROTEIRO DO VÍDEO EXECUTIVO
**Tech Challenge Fase 4 · Grupo 12 · POSTECH DTAT**
**Duração máxima: 7:00 · cronometragem fechada em 6:50, com 10 s de margem**

Todo número **falado** aqui sai de `04_video/numeros_roteiro.py` e está amarrado em
`04_video/tab_roteiro_numeros.csv` (indicador · valor · base · *n* · regra), e
`04_video/confere_amarracao.py` reprova o roteiro se um deles não estiver lá. Nenhum valor foi
estimado. Os números **da tela** seguem como conferência humana, com a figura na frente: o script
lê só a coluna do que é dito.

**Ritmo — a segunda medição, e a que decide se o vídeo cabe.** A cronometragem soma os tempos
escritos; ela não mede a fala. Por isso a fala também é orçada: **1.000 palavras em 410 s =
2,46 palavras por segundo**, dentro da faixa de apresentação executiva (2,3 a 2,6 p/s), e
**nenhum bloco passa de 2,62 p/s**.
Duas regras produzem esse número e valem para qualquer edição futura: **número que a tela já
mostra só é dito quando decide a mensagem**, e **justificativa de método vira legenda**. A fala carrega o que a
liderança decide; a tela carrega a prova. Para remedir depois de qualquer alteração, a contagem
é feita por `python3 04_video/confere_amarracao.py`, que reprova se a fala passar de 2,6 p/s
ou se um número falado não tiver linha na tabela de amarração.

---

## Storytelling — os quatro elementos

| Elemento | Definição |
|---|---|
| **Personagem** | A **liderança** é o herói. Quem decide o sortimento e a política de desconto. Nem a marca nem o time de dados são protagonistas — o time entrega o mapa, a liderança escolhe o caminho. |
| **Ambiente** | Um catálogo de **1.348 produtos** de marketplace indiano, sem histórico, sem venda e sem cliente identificado. Decisões de preço e sortimento sendo tomadas com a única evidência disponível: o que o consumidor avaliou. |
| **Conflito** | **Arquétipos B e D.** Desconto praticamente igual — **58% contra 61%, 3 pontos percentuais de distância** — e resultado oposto: **D tem 28 vezes mais avaliações**; **B é o único grupo abaixo do limiar de satisfação (nota mediana 3,9)**. O desconto profundo não separa os dois. Logo, o desconto sozinho não explica o destino de um produto no catálogo. |
| **Mensagem** | **Desconto não é estratégia de sortimento.** Existe um bloco de 335 produtos descontando fundo sem tração e com a pior nota do portfólio — e ele é identificável hoje, sem dado novo. |

## Cronometragem

| # | Bloco | Início | Fim | Duração |
|---|---|---|---|---|
| 1 | Contexto do problema *(inclui **L5**, 10 s)* | 0:00 | 0:40 | 0:40 |
| 2 | Principais indicadores | 0:40 | 1:30 | 0:50 |
| 3 | Principais insights *(o conflito B × D)* | 1:30 | 2:40 | 1:10 |
| 4 | Demonstração do dashboard | 2:40 | 3:37 | 0:57 |
| — | **L1 — limitação dita antes de Customer Insights** | 3:37 | 3:50 | **0:13** |
| 5 | Customer Insights *(inclui os dois focos de insatisfação)* | 3:50 | 4:50 | 1:00 |
| 6 | Recomendações *(inclui **L4**, 12 s)* | 4:50 | 6:00 | 1:10 |
| 7 | Conclusão executiva | 6:00 | 6:50 | 0:50 |
| — | margem | 6:50 | 7:00 | 0:10 |
| | **Total** | | | **6:50 / 7:00** |

> **Por que L1 tem 13 s e não 10.** É o único trecho em cartela de tela cheia, sem número
> competindo com a fala, e é a limitação que condiciona todo o bloco seguinte. A 10 s ela sairia
> a 3,4 p/s — rápida justamente onde a dicção precisa ser lenta. Os 3 s vieram do bloco 5, do
> trecho de corpus, que é método e continua na tela, na tabela e no relatório.

> **Padrão visual (T9):** toda cartela, gráfico e captura usa a paleta v06, aplicada por ferramenta —
> `method/design_system/tema_fase4_ambar_ardosia.json` no Power BI e `src/paleta.py` em Python.
> Nenhuma cor escolhida à mão. Máximo de 5 séries por visual.
> **Rodapé fixo em todos os frames com número:** *fonte · base · n*.

---

## 1 · Contexto do problema — 0:00 a 0:40

| Tempo | O que é dito | O que aparece na tela |
|---|---|---|
| 0:00–0:10 | "Boa tarde. O que 1.348 produtos de marketplace revelam sobre preço, desconto e satisfação — e o que a liderança decide a partir disso esta semana." | Cartela de abertura: título do projeto, Grupo 12, Fase 4. Um único elemento em âmbar. |
| 0:10–0:20 | **⚠️ L5 — LIMITAÇÃO, DITA EM VOZ ALTA.** "Primeiro, a ressalva que muda a leitura de tudo: marketplace indiano, valores em rupia indiana, sem conversão. Transpor para o nosso mercado é analogia, não resultado." | Cartela **L5** em ardósia, texto curto: *"Mercado indiano · valores em rupia indiana · sem conversão · L5"*. Cronômetro discreto marcando os 10 s. |
| 0:20–0:31 | "Partimos de 1.465 linhas de catálogo. Removendo repetições e três registros inválidos, chegamos à base analítica de 1.348 produtos — a base de tudo o que vem a seguir." | `02_results/images/fig01_reconciliacao_bases.png` — funil 1.465 → 1.351 → 1.350 → 1.349 → **1.348**, com o último passo destacado e cada degrau rotulado (repetições · nota inválida · dois sem volume de avaliações). Rodapé: *base analítica · n = 1.348 · aparece no rodapé de cada tela*. |
| 0:31–0:40 | "Das nove famílias de produto, só quatro passam do piso de trinta. As outras cinco somam sete produtos e não entram em nenhuma comparação." | `fig05_portfolio_categoria.png`. Barras das 4 acima do piso **com o n em cada uma**: Electronics 490 · Home & Kitchen 447 · Computers & Accessories 373 · Office Products 31. As 5 suprimidas agrupadas em cinza, com a nota *"n < 30 — suprimidas (T2 / L3)"*. |

**Personagem e Ambiente entram aqui.** O herói é quem decide o sortimento; o ambiente é um catálogo sem venda, sem histórico e sem cliente identificado.

---

## 2 · Principais indicadores — 0:40 a 1:30

| Tempo | O que é dito | O que aparece na tela |
|---|---|---|
| 0:40–0:55 | "Quatro números desenham o portfólio, todos sobre os 1.348: nota mediana 4,10; desconto mediano 49%; preço de tabela mediano 1.795, em rupia indiana; volume mediano de avaliações 4.740." | Página **Visão Executiva** do dashboard, faixa de KPIs. Ao lado do desconto mediano, a leitura em uma linha: *"metade do catálogo desconta quase pela metade"*. Rodapé: *base analítica · n = 1.348*. |
| 0:55–1:08 | "Vocabulário, e vale para o vídeo inteiro: volume de avaliações é quantas pessoas avaliaram. Não é venda, não é receita, não é demanda — a base não traz essas variáveis. Chamo isso de engajamento." | Cartela de vocabulário, duas linhas: *"avaliações = volume de avaliações"* / *"≠ vendas · ≠ receita · ≠ demanda (T6)"*. Abaixo, o corte de engajamento alto: *p90 = 36.384 avaliações*. |
| 1:08–1:20 | "A divisão é desconfortável: 339 produtos — 25,1% do catálogo — estão abaixo de 4,0. Um em cada quatro. No outro extremo, 418 estão em 4,3 ou mais." | `fig03_nota_engajamento.png`, com as duas faixas marcadas. Rótulos diretos, sem legenda lateral. |
| 1:20–1:30 | "E a atenção não se distribui: 306 produtos, 22,7% da base, concentram 80% de todas as avaliações." | `fig08_pareto_engajamento.png` — curva de Pareto com o ponto de 80% marcado em âmbar. Na tela: *"pouco mais de um quinto do catálogo carrega quatro quintos da atenção"*. |

---

## 3 · Principais insights — 1:30 a 2:40  ·  **o conflito**

| Tempo | O que é dito | O que aparece na tela |
|---|---|---|
| 1:30–1:45 | "Associações por Spearman. Desconto e nota andam em sentido contrário: rô menos 0,150, p da ordem de 3 vezes 10 elevado a menos 8 — significativo e de magnitude pequena. É associação, não causa." | `fig04_correlacoes.png`, painel esquerdo (desconto × nota), com ρ e p ao lado. Faixa fixa no rodapé: *base analítica · n = 1.348 · associação, não causalidade (T4) · magnitude junto com significância (T5)*. |
| 1:45–1:58 | "As outras três estão na tela, cada rô com o seu p. Uma merece a voz: preço de tabela e nota, mais 0,032 com p de 0,24 — não há associação alguma." | `fig04`, painel direito (preço de tabela × nota, *"sem associação · p = 0,236"*) e, ao lado, a tabela das quatro correlações (`tab03_correlacoes.csv`), reveladas em sequência: *desconto × nota −0,150* · *desconto × volume −0,132* · *preço de tabela × nota +0,032* · *volume × nota +0,193*, cada uma com o seu p. A `fig04` mostra dois dos quatro pares; os outros dois só existem na tabela. Na tela: *"nenhuma é forte o bastante para virar regra de preço sozinha"*. |
| 1:58–2:20 | "É o achado central. Dois dos quatro arquétipos são quase idênticos no desconto e opostos em volume e em nota: D desconta 61% e tem 13.120 avaliações medianas; B desconta 58% e tem 468. Vinte e oito vezes menos, com três pontos de diferença — e B é o único dos quatro abaixo do limiar de satisfação, nota 3,9." | **Cartela do conflito:** `04_video/cartelas/cartela_conflito_BxD.png` — três painéis lado a lado (desconto · volume de avaliações · nota), só duas séries, B e D. Título na tela: *"Desconto quase igual, resultado oposto"*. |
| 2:20–2:32 | "Duas ressalvas que sustentam o achado em vez de enfraquecê-lo. Primeira: os arquétipos são convenção descritiva, não descoberta — a silhueta máxima é 0,237, e nesse patamar não há estrutura natural de agrupamento." | `fig13_silhueta.png` — curva de k = 2 a 7, com **k = 5 (0,237)** e **k = 4 (0,234)** marcados. Nota na tela: *"adotado k = 4 por interpretabilidade · diferença desprezível · convenção descritiva, não descoberta (ML4)"*. |
| 2:32–2:40 | "Segunda: B tem 335 produtos, muito acima do piso de trinta. Não é um punhado de casos estranhos." | Tabela dos quatro arquétipos com o *n* de cada um (`02_results/tables/tab05_arquetipos.csv`): A 268 · **B 335** · C 298 · D 447. Soma 1.348 — **B é um quarto do catálogo**. |

---

## 4 · Demonstração do dashboard — 2:40 a 3:37

| Tempo | O que é dito | O que aparece na tela |
|---|---|---|
| 2:40–2:50 | "O dashboard tem sete páginas e responde às quinze perguntas do escopo. A Visão Executiva abre com os indicadores e a curva de concentração." | **Gravação de tela, ao vivo.** Página *Visão Executiva*. Cursor percorrendo KPIs e Pareto; o *306 produtos · 80% das avaliações* visível no visual. |
| 2:50–3:03 | "Produtos e Categorias compara por subcategoria, não por família: oito acima do piso, cobrindo 88,3% do portfólio. Comparar Electronics com Home & Kitchen junta coisas que não competem." | Página *Produtos e Categorias*. Filtro sendo aplicado. Rodapé: *8 subcategorias · 88,3% · piso n ≥ 30*. |
| 3:03–3:17 | "Aqui vive uma correção decisiva: todo ranking por nota usa o limite inferior de Wilson, nunca a nota bruta, com o número de avaliações ao lado. Sem ela, um produto com cinco avaliações lidera a lista." | Comparação lado a lado: *top 10 por nota bruta* × *top 10 por nota corrigida (Wilson)*, com a coluna de *n* visível. T7: nenhum identificador de consumidor em tela. |
| 3:17–3:27 | "Preços e Estratégia Comercial cruza preço de tabela, preço com desconto e percentual, e compara as cinco faixas de desconto, todas acima do piso." | Página *Preços*. `fig07_faixas_desconto.png`. Valores sem símbolo monetário; rodapé repetindo *rupia indiana, sem conversão (L5)*. |
| 3:27–3:37 | "Customer Insights traz o conteúdo das avaliações; Recomendações fecha com o que fazer, com as limitações na própria página. Toda tela tem rodapé com fonte, base e n." | Varredura rápida pelas páginas 4 e 5. Zoom no rodapé de limitações da página *Recomendações*. |

---

## ⚠️ L1 — LIMITAÇÃO OBRIGATÓRIA, DITA EM VOZ ALTA — 3:37 a 3:50

| Tempo | O que é dito | O que aparece na tela |
|---|---|---|
| 3:37–3:50 | "A limitação mais importante do projeto: no máximo 8 avaliações por produto, média 7,85. Não é amostra aleatória — é a vitrine. São os temas visíveis, não a distribuição real das opiniões." | Cartela **L1**, tela cheia, ardósia com uma linha em âmbar: *"Máximo 8 avaliações por produto (média 7,85) · é o recorte que o marketplace escolheu exibir na página · são os temas visíveis na vitrine, não a distribuição real das opiniões · L1"*. Sem gráfico, sem número competindo com a fala. |

**Regra de dicção deste bloco.** Nenhuma frase do bloco 5 começa com *"a maioria dos clientes"*. É consequência direta de L1 e está no checklist de gravação.

---

## 5 · Customer Insights — 3:50 a 4:50

> **Por que este bloco entrega tema, e não só método.** Customer Insights é um dos nove critérios
> de avaliação. Um bloco que apresentasse apenas o tamanho do corpus e a deduplicação cumpriria o
> método e deixaria o critério ausente justamente onde a banca assiste: a liderança não decide
> nada com a contagem de deduplicação. Por isso o corpus está comprimido e **o que o cliente
> reclama tem 18 s de fala** — a maior fatia do bloco.

| Tempo | O que é dito | O que aparece na tela |
|---|---|---|
| 3:50–3:58 | "Com essa régua, o corpus: 10.588 referências de avaliação, 9.255 distintas depois de deduplicar." | `fig12_corpus.png` — 10.588 → 9.255, com as **1.333 repetidas** destacadas. Rodapé: *unidade = bloco de review · deduplicado por review_id (T8)*. |
| 3:58–4:12 | "A leitura contrasta os dois extremos: abaixo de 4,0 contra 4,3 ou mais. E declaro a lacuna: a faixa intermediária, 44% do portfólio, fica fora do contraste. Foi escolha de método." | Tabela do corpus por faixa (`tab06_corpus.csv`): *339 abaixo de 4,0 · 591 intermediária · 418 de 4,3 ou mais*, com a linha intermediária marcada em cinza e o rótulo *"fora do contraste — lacuna declarada"*. |
| **4:12–4:30** | "E o que o cliente reclama tem dois endereços. Em fones, 52,4% abaixo de 4,0, o dobro da base; em climatização, 37,9%. A dispersão sugere revisar fones como categoria e climatização produto a produto — mas é hipótese: a diferença não é significativa." | `fig09_dispersao_subcategoria.png`, com as duas subcategorias em **laranja** (`atencao`, leitura negativa) e as demais em ardósia. **Sem âmbar nesta tela**: o ponto aqui são **dois** focos, e a regra dos 10% admite um só — destacar os dois em âmbar seria não destacar nenhum. Ao lado, duas linhas: *fones · 52,4% (IC95% 40–64%) · dp 0,224 · n = 63* e *climatização · 37,9% (IC95% 30–47%) · dp 0,346 · n = 116*, e abaixo delas: *"diferença de dispersão não significativa — Levene p = 0,18 · hipótese, não conclusão"* (`tab29`, `tab30`). Rodapé: *base analítica · n = 1.348 · taxa da base: 25,1%*. |
| 4:30–4:40 | "E onde começar: 19 produtos muito avaliados e com nota abaixo de 4,0. Lista nominal, com o n ao lado: dá para agir na segunda-feira." | `fig06_quadrantes.png` com o **quadrante Q5 em âmbar** — e só ele; ao lado, a lista nominal dos 19 produtos com nota e *n*. Rodapé: *lista nominal — não sujeita ao piso de 30 (T2) · 147 avaliações escritas disponíveis*. |
| 4:40–4:50 | "No texto: nas notas baixas, produto que para de funcionar; nas altas, instalação fácil, velocidade e imagem. Medido dentro de Electronics, a maior família." | Tabela dos n-gramas do **recorte Electronics** (`tab14_ngramas.csv`): à esquerda *working · properly · stopped working*, à direita *installation · speed · fast · picture quality*. A `fig_nlp_02_contraste_ngramas.png` mostra a base inteira e **não** entra neste frame. Rodapé: *recorte Electronics · 128 blocos abaixo de 4,0 e 136 acima de 4,3 · unidade: bloco de review (T8) · no máximo 8 avaliações por produto (L1)*. |

**A taxa da base entra na tela por necessidade, não por simetria.** Sem os 25,1% ao lado, **52,4% e 37,9% não têm referência**: o espectador não sabe se é muito. Os cinco números deste bloco saem de `tab_roteiro_numeros.csv`, seção *5 Customer Insights*, cada um com o *n* da sua subcategoria.

**O que este bloco não diz, de propósito.** Não diz que o texto das avaliações *confirma* o problema dos fones. O eixo de áudio no texto e os 52,4% da subcategoria **não são medições independentes** — excluindo os fones do corpus, o tema de áudio colapsa de seis termos para um (relatório §7.7). Os 52,4% se sustentam sozinhos, na distribuição de notas de 63 produtos. Apresentar as duas coisas como confirmação cruzada seria contar a mesma evidência duas vezes, e é o tipo de reforço aparente que uma banca testa primeiro.

---

## 6 · Recomendações — 4:50 a 6:00

| Tempo | O que é dito | O que aparece na tela |
|---|---|---|
| 4:50–5:02 | **⚠️ L4 — LIMITAÇÃO, DITA EM VOZ ALTA.** "Uma condição antes das recomendações: esta base não tem variável de venda — sem receita, margem, estoque ou data. Nenhuma recomendação vem com cifra, e nada aqui fala de tendência." | Cartela **L4**: *"Sem variável de venda · sem unidade vendida · sem receita · sem margem · sem data · nenhuma recomendação em dinheiro · nenhuma afirmação de tendência ou sazonalidade · L4"*. |
| 5:02–5:14 | "Primeira: revisar o sortimento do arquétipo B — 335 produtos, o grupo que desconta 58% e entrega nota 3,9. Não é cortar; é revisar caso a caso." | Volta rápida à cartela B × D. Ao lado, o cartão da recomendação 1 com o *n* = 335, o contraste *468 × 13.120 avaliações medianas* e a razão da revisão: *"o desconto ali não vem acompanhado de avaliação nem de nota"*. |
| 5:14–5:26 | "Segunda: tratar os 19 produtos de risco de vitrine como fila de trabalho, esta semana. São poucos, nominais, muito avaliados e abaixo de 4,0, e cada um tem avaliação escrita disponível." | Lista dos 19 produtos, formatada como fila de trabalho. Coluna de *n* de avaliações visível. Na tela: *"a ação mais simples de executar do conjunto: a lista já existe"*. |
| 5:26–5:44 | "Terceira: desconto profundo não é alavanca isolada. Na nota corrigida, o topo é plano; o extremo se destaca: acima de 80% de desconto a nota corrigida cai para 3,906, a única faixa abaixo do limiar, sobre 51 produtos. Associação, não causa — o que a evidência autoriza é rever a política." | `fig07_faixas_desconto.png` com a faixa 81–100% em âmbar e o *n* de cada faixa. Na tela, sobre as quatro primeiras faixas: *"nota corrigida sem destaque entre si (T5)"*; ao lado, a fatia abaixo de 4,0 por faixa (`tab28_faixa_desconto_insatisfacao.csv`: 16,6% → 43,1%, taxa da base 25,1%). Rodapé: *nota corrigida de Wilson (T1) · 5 faixas, todas n ≥ 30*. |
| 5:44–6:00 | "Quarta: testar exposição nos 61 bem avaliados com baixo volume — não nos 187. A correção de Wilson derruba 126 e sobram 61. Volume de avaliações é proxy declarado de exposição: a base não tem impressão nem clique." | `fig06_quadrantes.png`, quadrante Q6, com a lista dos 61 ao lado. Na tela: *funil 187 → lista acionável 61, correção de Wilson (T1) · n = 1.348*. |

---

## 7 · Conclusão executiva — 6:00 a 6:50

> **Responde diretamente:** *"Quais são as principais mensagens que a liderança deve levar a partir desta análise?"*

| Tempo | O que é dito | O que aparece na tela |
|---|---|---|
| 6:00–6:06 | "Encerro respondendo à pergunta que importa: quais as mensagens que a liderança deve levar? São quatro." | Cartela de fechamento com a pergunta escrita, e quatro linhas numeradas que se revelam uma a uma. |
| 6:06–6:15 | "Primeira: desconto não é estratégia de sortimento. Dois grupos a três pontos de distância no desconto terminam em lados opostos do portfólio." | Linha 1 em destaque. Miniatura da cartela B × D ao lado, com *58% × 61%* e *468 × 13.120 avaliações medianas · notas 3,9 × 4,2*. |
| 6:15–6:27 | "Segunda: um quarto do catálogo está abaixo de 4,0. Mas a insatisfação não está onde a atenção está, e tem dois endereços: fones e climatização." | Linha 2. Dois números grandes: **25,1%** (339 de 1.348) e **12,7%** (39 dos 306 do Pareto), com a base e o *n* embaixo e o rótulo *"metade da taxa da base"*. Ao lado, os dois endereços em uma linha cada. |
| 6:27–6:34 | "Terceira: existe uma fila de 19 produtos para começar esta semana. Sem dado novo e sem projeto: a lista já existe." | Linha 3. Os 19 produtos como fila curta: alto engajamento · nota abaixo de 4,0 · avaliação escrita disponível. |
| 6:34–6:50 | "Quarta, e a mais importante: medimos sobre volume de avaliações, não vendas, e sobre no máximo 8 avaliações por produto, em rupia indiana, sem conversão. Dentro desses limites a evidência sustenta decisão; fora deles, não. É esse o valor da análise. Obrigado." | Linha 4. Cartela final compacta com **L1 · L4 · L5** em uma linha cada, o logo do grupo, e o rodapé: *Fonte: Kaggle · karkavelrajaj/amazon-sales-dataset · base analítica · n = 1.348*. |

---

## Checklist de gravação — conferir antes de publicar

| Regra | Verificação |
|---|---|
| **T1** | Todo ranking por nota exibido em tela usa `nota_corrigida` (Wilson), com o *n* ao lado — blocos 4 e 6 |
| **T2** | Nenhum grupo com n < 30 é comparado. As 5 categorias suprimidas aparecem agrupadas, não ranqueadas. As listas nominais (19 de Q5, 61 de Q6) são exceção declarada em tela |
| **T3** | Rodapé com fonte, base e *n* em **todo** frame que tem número. A base dos números falados é declarada na voz no bloco 2 e repetida no rodapé de cada tela |
| **T4** | Nenhuma frase **afirma** causa. "Causa" só aparece negada ("é associação, não causa"), nos blocos 3 e 6. Nenhuma ocorrência de "faz com que", "leva a" ou "provoca" |
| **T5** | Todo ρ falado vem acompanhado do p-valor e da leitura de magnitude. Os quatro ρ aparecem na tela com o p ao lado; dois são falados |
| **T6** | `rating_count` é sempre **volume de avaliações**. A cartela de vocabulário em 0:55 torna isso explícito antes de qualquer uso |
| **T7** | Nenhum `user_id` ou `user_name` em nenhum frame — conferir especialmente as capturas de Customer Insights |
| **T8** | O corpus declara unidade (bloco de review), deduplicação por `review_id` e o truncamento em 8 — bloco 5 e cartela L1 |
| **T9** | Cartelas, figuras e capturas na paleta v06, aplicada por `src/paleta.py` e pelo tema do Power BI. Máximo 5 séries por visual — a cartela do conflito usa 2 |
| **L1** | Dita em voz alta em **3:37**, **imediatamente antes** de Customer Insights, em cartela de tela cheia, com 13 s dedicados |
| **L4** | Dita em voz alta em 4:50, **abrindo** o bloco de recomendações, com 12 s dedicados |
| **L5** | Dita em voz alta em 0:10, na **abertura**, com 10 s dedicados |
| **Dicção** | Nenhuma frase do bloco 5 começa com "a maioria dos clientes" — consequência de L1 |
| **Moeda** | Nenhum símbolo monetário em tela ou na fala. Só "rupia indiana", e só quando necessário |
| **Amarração** | Nenhum número **falado** fora de `tab_roteiro_numeros.csv` — conferido por `python3 04_video/confere_amarracao.py`. Os números **da tela** seguem como conferência humana, com a figura na frente |
| **Tempo** | Cronometrar bloco a bloco. O total fecha em **6:50**, com 10 s de margem para o limite de 7:00 |
| **Ritmo** | **Ler em voz alta cronometrando.** A fala mede 1.000 palavras em 410 s (2,44 p/s; ≈ 2,9 lendo os numerais por extenso), conferido pelo mesmo script; a leitura real é a única medição que vale |

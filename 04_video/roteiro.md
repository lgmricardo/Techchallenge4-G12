# 🎬 ROTEIRO DO VÍDEO EXECUTIVO
**Tech Challenge Fase 4 · Grupo 12 · POSTECH DTAT**
**Duração-alvo: 6:00 · cronometragem fechada em 5:50, com 10 s de margem**

O vídeo é uma apresentação executiva feita **dentro do dashboard**. Abre com a preparação dos
dados e o método, em pouco mais de um minuto. Depois passa pelas páginas do Power BI na ordem
da barra de navegação: em cada uma, diz para que ela serve, o que ler primeiro e onde clicar.
Fecha com as recomendações e as mensagens para a liderança.

A base de cada trecho é o **Manual de Leitura do Dashboard**
(`docs/manual_leitura_dashboard_v1.pdf`): as telas citadas abaixo usam a numeração dos itens do
manual ("página 2b, item 3").

Todo número **falado** está em `04_video/tab_roteiro_numeros.csv`, e
`python3 04_video/confere_amarracao.py` reprova o roteiro se um deles não estiver lá ou se a fala
passar do ritmo de apresentação (2,6 palavras por segundo).

---

## Os sete itens do enunciado, na ordem

| # | Bloco | O que o enunciado pede | Início | Fim | Duração |
|---|---|---|---|---|---|
| 1 | Contexto, preparação dos dados e método | Contexto do problema | 0:00 | 1:10 | 1:10 |
| 2 | Página inicial e Visão Executiva | Principais indicadores | 1:10 | 1:56 | 0:46 |
| 3 | Categorias, Quadrantes, Rankings e Preços | Principais insights | 1:56 | 3:30 | 1:34 |
| 4 | Como usar o painel: filtro e ficha do produto | Demonstração do dashboard | 3:30 | 4:00 | 0:30 |
| 5 | Customer Insights | Customer Insights | 4:00 | 4:40 | 0:40 |
| 6 | Recomendações | Recomendações para o negócio | 4:40 | 5:20 | 0:40 |
| 7 | As três mensagens | Conclusão executiva e mensagens para a liderança | 5:20 | 5:50 | 0:30 |
| — | margem | | 5:50 | 6:00 | 0:10 |
| | **Total** | | | | **5:50 / 6:00** |

**O fio condutor.** Quem decide é a liderança: sortimento, preço e desconto. O painel entrega
onde agir e com qual evidência. A mensagem que amarra o vídeo: **desconto não é estratégia de
sortimento, e a insatisfação tem endereço.**

---

## 1 · Contexto, preparação dos dados e método — 0:00 a 1:10

| Tempo | O que é dito | O que aparece na tela |
|---|---|---|
| 0:00–0:12 | "Boa tarde. Este painel responde a uma pergunta da liderança: onde agir em preço, desconto e sortimento num catálogo de 1.348 produtos, usando só o que o consumidor avaliou." | Power BI aberto na **Página inicial** (manual, seção 4). Cursor parado no cabeçalho (item 1). |
| 0:12–0:24 | "A base é pública: um marketplace indiano, com preços em rupia, sem conversão. Não há dado de venda; o volume de avaliações mede atenção, não vendas." | Mesma tela, zoom na caixa **Compromissos metodológicos** (item 2), no trecho "Vitrine, não caixa". |
| 0:24–0:44 | "A preparação foi feita no próprio Power BI, no Power Query, em camadas. Partimos de 1.465 linhas; retiramos nome e identificador de quem avaliou, convertemos preços e percentuais, mantivemos um registro por produto e descartamos três registros inválidos. Ficam 1.348 produtos." | **Transformar dados** abre o Editor do Power Query. Painel de consultas visível: `bronze_amazon` → `silver_produtos` → `gold_intermediaria` → `BaseAnalitica`. Clique em `silver_produtos`: a lista de **etapas aplicadas**, com nomes descritivos, aparece à direita. Fechar sem aplicar. |
| 0:44–0:56 | "Refizemos a mesma preparação em Python, como gabarito: o painel confere os próprios números contra ele, com zero divergência. As análises usam correlação, agrupamento em perfis e leitura do texto das avaliações." | Página oculta **Conferência** (manual, seção 12.3): cartões *Divergentes 0* e *Conferidas 33*, tabela com a coluna *Situação* em "confere". |
| 0:56–1:10 | "E quatro regras de leitura valem em todo o painel: ranking só pela nota corrigida pelo número de avaliações; grupo só com trinta produtos ou mais; associação nunca é causa; e avaliação nunca é venda." | Volta à **Página inicial**, caixa **Compromissos metodológicos** (item 2): cursor descendo pelas regras T1, T2, T4/T5 e T6. |

---

## 2 · Página inicial e Visão Executiva — 1:10 a 1:56

| Tempo | O que é dito | O que aparece na tela |
|---|---|---|
| 1:10–1:22 | "O painel abre na página inicial. A barra no topo leva a qualquer página, e o rodapé mostra sempre a base e quantos produtos estão na tela." | Cursor percorre a **barra de navegação** e para no **rodapé** (manual, seção 3, itens C e D). Clique em *1 · Visão Executiva*. |
| 1:22–1:36 | "A Visão Executiva é o retrato do catálogo inteiro. Nos cartões, a nota mediana é 4,10, e um produto passa a ser muito avaliado a partir de 36.384 avaliações." | **Visão Executiva** (manual, seção 5). Cursor sobre os cartões *Nota mediana* (item 2) e *Engajamento alto começa em* (item 6). |
| 1:36–1:56 | "O histograma mostra que um quarto do catálogo está abaixo de 4,0. A curva ao lado mostra concentração: 306 produtos reúnem 80% das avaliações. E os quadros separam os 19 muito avaliados com nota baixa dos 187 bem avaliados e pouco vistos." | Cursor no histograma (item 7), na barra laranja; depois no **ponto amarelo** da curva de Pareto (item 9); por fim nos quadros *Risco de vitrine (Q5)* e *Subexplorado (Q6)* (item 11). |

---

## 3 · Categorias, Quadrantes, Rankings e Preços — 1:56 a 3:30

| Tempo | O que é dito | O que aparece na tela |
|---|---|---|
| 1:56–2:18 | "Em Categorias, só comparamos grupos com trinta produtos ou mais. Home and Kitchen tem a maior parcela de produtos abaixo de 4,0. À direita, a variação das notas por subcategoria: climatização é a mais irregular. Passando o mouse numa barra, aparece quantos produtos há no grupo." | **2a · Categorias** (manual, seção 6). Cursor na barra de Home&Kitchen (item 1); depois no gráfico de dispersão (item 5), barra laranja de climatização. **Passar o mouse** sobre uma barra de categoria para abrir a caixa com *Produtos (n)* e *Nota corrigida*. |
| 2:18–2:42 | "Quadrantes é a página de ação. No mapa, cada ponto é um produto, cruzando volume de avaliações e nota. Fones têm 52,4% dos produtos abaixo de 4,0, o dobro da base; climatização, 37,9%. Embaixo, as listas: os 19 para revisar e os 61 que merecem mais exposição." | **2b · Quadrantes** (manual, seção 7). Cursor nos pontos laranja do mapa (item 1); depois nas duas barras laranja do gráfico ao lado, com a linha tracejada da base (item 2); por fim nas listas dos 19 (item 3) e dos 61 (item 4). |
| 2:42–3:06 | "Rankings e arquétipos mostra por que corrigimos a nota: pela nota bruta, um produto com cinco avaliações chega ao topo; pela corrigida, só ficam produtos com milhares. E os quatro perfis trazem o achado central: B e D descontam quase igual, 58 e 61%, mas D tem 28 vezes mais avaliações e nota maior." | **2c · Rankings e arquétipos** (manual, seção 8). Cursor no ranking bruto (item 1), linha de 5 avaliações; depois no ranking homologado (item 2), coluna *Avaliações*; por fim nos três gráficos B × D (itens 4, 5 e 6). |
| 3:06–3:30 | "Em Preços e estratégia, o desconto não aparece como alavanca: mais desconto anda com nota um pouco menor, correlação de menos 0,150. Acima de 80% de desconto, a nota corrigida cai para 3,906, a única faixa abaixo de 4,0. E o preço de tabela não acompanha o desconto, nem a nota." | **3 · Preços e estratégia** (manual, seção 9). Cursor na barra laranja *Desconto × nota* (item 6); depois na coluna laranja da faixa 81-100% (item 4); por fim no gráfico *O preço de tabela não acompanha o desconto* (item 8): colunas escuras, preço de tabela; claras, preço com desconto, como diz a legenda abaixo do gráfico. |

---

## 4 · Como usar o painel: filtro e ficha do produto — 3:30 a 4:00

| Tempo | O que é dito | O que aparece na tela |
|---|---|---|
| 3:30–3:44 | "No dia a dia, a liderança escolhe uma categoria no filtro, aqui Electronics. O filtro vale para as quatro páginas de análise, e o rodapé passa a mostrar 490 produtos." | Em **2b · Quadrantes**, abrir a segmentação **Categoria** e marcar *Electronics* (manual, seção 3, item B). O mapa se redesenha. Zoom no **rodapé**: *n filtrado = 490*. |
| 3:44–4:00 | "Para ver um produto, clique com o botão direito na lista e escolha Detalhamento: abre a ficha, com notas, avaliações, preço e perfil. Para limpar, volte o filtro para Todos." | Na lista dos 19, **botão direito** na primeira linha > **Detalhamento** > **Detalhe do produto** (manual, seção 12.1). A ficha aparece por 4 s. Volta a *2b · Quadrantes* pela aba da página; segmentação *Categoria* de volta para *Todos*. |

---

## 5 · Customer Insights — 4:00 a 4:40

| Tempo | O que é dito | O que aparece na tela |
|---|---|---|
| 4:00–4:12 | "No texto das avaliações, um aviso antes: são no máximo 8 por produto, as que a vitrine exibia. O que vemos são os temas visíveis, não a opinião de todos." | **4 · Customer Insights** (manual, seção 10). Zoom no aviso do topo da página (item 1). |
| 4:12–4:26 | "O gráfico de palavras compara eletrônicos com nota baixa e com nota alta: som, ruído e ouvido aparecem nas notas baixas; imagem, instalação e excelente, nas altas." | Gráfico *Som aparece onde a nota é baixa; imagem, onde é alta* (item 7). Cursor nas barras laranja *bass*, *noise* e *ear*; depois nas verdes *picture*, *installation* e *excellent*. |
| 4:26–4:40 | "E nas 147 avaliações dos 19 produtos de risco, preço e custo-benefício aparece em quase todos; som, ruído e microfone, em 15. É por onde começar a revisão." | Gráfico *O que as 147 avaliações dos 19 produtos dizem* (item 6). Cursor nas duas primeiras barras. |

---

## 6 · Recomendações — 4:40 a 5:20

| Tempo | O que é dito | O que aparece na tela |
|---|---|---|
| 4:40–4:54 | "A última página fecha com cinco decisões, cada uma com o seu número. Primeira: revisar os 19 produtos muito avaliados com nota baixa. Segunda: revisar o sortimento do perfil B, 335 produtos." | **5 · Recomendações** (manual, seção 11). Cursor nos cartões 1 e 2. |
| 4:54–5:08 | "Terceira: dar exposição aos 61 bem avaliados, não aos 187. Quarta: parar de usar a profundidade do desconto como alavanca isolada. Quinta: concentrar a governança em três famílias, começando por fones e climatização." | Cursor nos cartões 3, 4 e 5. |
| 5:08–5:20 | "Dois limites: sem dado de venda, nenhuma recomendação fala em receita. E o modelo de risco, com AUC de 0,70, serve para triagem, não para veredito." | Cursor no gráfico *O sinal é multivariado* (item 6), barra *completo*; depois na linha L4 do quadro *O que esta base não permite dizer* (item 7). |

---

## 7 · As três mensagens — 5:20 a 5:50

| Tempo | O que é dito | O que aparece na tela |
|---|---|---|
| 5:20–5:30 | "Ficam três mensagens. Primeira: desconto não é estratégia de sortimento; perfis com o mesmo desconto terminam em lados opostos." | Volta a **2c · Rankings e arquétipos**: os três gráficos B × D (itens 4, 5 e 6). |
| 5:30–5:40 | "Segunda: um quarto do catálogo está abaixo de 4,0, e a insatisfação tem endereço: fones e climatização." | **2b · Quadrantes**: gráfico *Fones e climatização lideram a insatisfação* (item 2). |
| 5:40–5:50 | "Terceira: as listas já estão no painel, com nome e número de avaliações, para agir nesta semana. Obrigado." | **2b · Quadrantes**: lista *Os 19 produtos para revisar esta semana* (item 3). Corte para a **Página inicial**. |

**Resposta à pergunta final do enunciado** ("Quais são as principais mensagens que a liderança
deve levar?"): as três mensagens do bloco 7.

---

## Antes de gravar

- **Arquivo:** o `.pbix` final, o mesmo do PDF que gerou o manual. Se o dashboard mudar, as telas
  citadas aqui continuam válidas pelo título de cada gráfico; confira só os números falados.
- **Estado inicial:** todas as segmentações em *Todos*; Power BI aberto na *Página inicial*;
  painéis *Filtros*, *Visualizações* e *Dados* recolhidos; zoom em *Ajustar à página*.
- **Navegação no Power BI Desktop:** os botões da barra pedem **Ctrl + clique**. No navegador
  (Power BI Service), basta um clique.
- **Página Conferência (bloco 1):** fica oculta. No Desktop, ela aparece nas abas de página,
  embaixo, com o ícone de página oculta; clique na aba para abrir.
- **Power Query (bloco 1):** *Página Inicial > Transformar dados*. Feche com *Fechar*, sem
  aplicar alterações.
- **Ficha do produto (bloco 4):** abra só pelo detalhamento. Para voltar, clique na aba
  *2b · Quadrantes*.
- **Gravação:** 1920 × 1080, cursor visível, sem notificações na tela. Grave por bloco e
  cronometre cada um; o total não passa de 6:00.
- **Pronúncia:** "Home and Kitchen" em inglês; os números como estão escritos ("trinta e seis
  mil, trezentos e oitenta e quatro").
- **Depois de editar a fala:** rode `python3 04_video/confere_amarracao.py` e
  `python3 04_video/gera_storyboard.py`.

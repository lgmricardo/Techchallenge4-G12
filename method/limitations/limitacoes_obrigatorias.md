# ⚠️ LIMITAÇÕES OBRIGATÓRIAS
**Todas as oito entram no `.pbix` (página de Recomendações ou rodapé). Três são ditas em voz alta no vídeo: L5, L1 e L4.**
Texto pronto para uso.

---

## L1. Truncamento em 8 avaliações por produto
> A base disponibiliza no máximo **8 avaliações por produto** (média medida: 7,85). O texto analisado **não é uma amostra aleatória** do que os consumidores escreveram: é o recorte que o marketplace escolheu exibir na página do produto.
>
> **Consequência:** os achados de Customer Insights descrevem **os temas visíveis na vitrine**, não a distribuição real das opiniões. Nenhuma conclusão deste bloco pode ser expressa como "a maioria dos clientes pensa que…".

*Por que é a limitação mais importante: apresentada como "a voz do cliente", a análise cai na primeira pergunta de quem conhece a base. Apresentada como "os temas visíveis", o achado permanece íntegro.*

## L2. Idioma do corpus
> As avaliações estão predominantemente em inglês, com ocorrências em outros idiomas e em alfabetos não latinos. O pipeline remove tokens não latinos, o que **descarta conteúdo real** antes da análise.
>
> **Consequência:** os temas extraídos representam o subconjunto de avaliações em alfabeto latino. A parcela descartada não foi quantificada por idioma.

## L3. Concentração de categorias
> Das 9 categorias de nível 1, apenas **4 têm 30 produtos ou mais**: Electronics (490), Home & Kitchen (447), Computers & Accessories (373) e Office Products (31). As **outras 5 categorias somam 7 produtos**.
>
> **Consequência:** "análise de portfólio por categoria" significa, na prática, **três famílias de produto mais uma no limite amostral**. Nenhuma recomendação se estende às categorias suprimidas.

## L4. Ausência de variável de venda
> A base **não contém** unidades vendidas, receita, margem, estoque ou data. `rating_count` é **volume de avaliações** — um proxy de engajamento, nunca de vendas.
>
> **Consequência:** nenhuma recomendação pode ser expressa em receita, volume vendido ou retorno financeiro. Não há análise temporal possível — nenhuma afirmação sobre tendência, sazonalidade ou evolução.

## L5. Mercado e moeda
> A base é do marketplace **indiano**, com valores em **rupia indiana**. Nenhuma conversão para real foi aplicada.
>
> **Consequência:** as faixas de preço descrevem o comportamento comercial daquele mercado. A transposição para outro mercado é analogia, não resultado — e precisa ser declarada na abertura do vídeo.

**Premissa de notação — vale para todo artefato.** O **símbolo** da rupia (U+20B9) **não é usado em nenhum lugar do material**: nem em rótulo de visual, título, eixo, tabela, cartela de vídeo, slide, texto de relatório ou nome de medida. Escreve-se **"rupia"** ou **"rupia indiana"** por extenso, e o valor vai **sem símbolo algum**, no formato `#.##0`.

São três razões, e a terceira é a que decide:

| Razão | Detalhe |
|---|---|
| **Renderização** | o símbolo depende de suporte da fonte. Em exportação para PDF, em compressão de vídeo e em visualizador de terceiros, ele degrada para quadrado ou interrogação — e um número com glifo quebrado ao lado parece erro de dado |
| **Ambiguidade** | um símbolo monetário desconhecido no slide convida o leitor a supor a moeda que ele conhece. "Rupia" escrito por extenso não deixa margem |
| **O risco que importa** | é o risco **R3** da matriz: valor em rupia lido como real. Um número de quatro dígitos sem símbolo, com a palavra "rupia" no rodapé, é mais difícil de confundir do que o mesmo número com um glifo que o leitor não reconhece |

**Duas exceções, ambas por integridade de dado, não por estilo:**

1. **O arquivo de origem não se altera.** O `bronze/amazon.csv` traz os preços como texto com o marcador de moeda à frente, e é assim que ele fica — o SHA-256 depende disso. Nos scripts, o caractere existe **apenas como alvo de remoção**, e está escrito como escape unicode (`MARCADOR_MOEDA_ORIGEM`) para que o glifo não apareça nem no código-fonte.
2. **Nome de produto: o glifo vira palavra, e a troca é declarada.** Exatamente **um** produto da base tem o símbolo no próprio nome — um teclado cujo diferencial de venda é ter essa tecla (`B08CF4SCNP`). Como a silver, a gold e a `tab17` são versionadas e o nome chega ao detalhamento do dashboard, o tratamento **substitui o glifo pela palavra `rupia`**, do mesmo jeito em `prepara_dados.py` e em `gera_figuras.py`, e o passo 4 do Power Query repete a regra. O bronze não muda: a substituição acontece na leitura, e o SHA-256 continua o mesmo.

## L6. Inconsistências da origem
> A base traz **114 linhas excedentes** distribuídas em **92 `product_id`**, das quais **31** apresentam `rating_count` divergente entre as ocorrências. Adotou-se a regra de manter a **maior** ocorrência.
>
> **Impacto medido:** a maior divergência é de **0,17%** e a diferença agregada é de **40 avaliações em 23,8 milhões** — imaterial. **Nota, categoria e nome nunca divergem** entre ocorrências do mesmo produto. **O preço de tabela diverge em 1 produto e o preço com desconto em 3**; em dois deles a divergência cai dentro de um empate de `rating_count` (`B096MSW6CT`, 999 × 1.899, e `B0B5LVS732`) — por isso o desempate declarado é obrigatório. A escolha da regra altera o texto de avaliação de **4** produtos.

## L7. Amostragem e generalização
> Os dados descrevem os produtos presentes neste recorte do catálogo, não o catálogo completo do marketplace nem o mercado de e-commerce em geral. Não há pesos amostrais.


## L8. Listagens variantes compartilham as mesmas avaliações
> Na Amazon, variantes de um mesmo anúncio (cores, tamanhos, embalagens) **compartilham o contador de avaliações do produto-pai**. Medido na base analítica: **254 produtos (18,8%)** apresentam exatamente o mesmo par `(rating_count, rating)` que outro produto, distribuídos em **96 grupos**.
>
> **Consequência:** a soma de `rating_count` **não é a soma de avaliações distintas**. Do total de 23.801.471, cerca de **5.564.434 (23,4%)** são contagem repetida entre variantes do mesmo anúncio.
>
> **O que muda e o que não muda.** A curva de Pareto é robusta: 22,7% dos produtos concentram 80% das avaliações, contra 22,4% colapsando as variantes. A **participação por categoria não é robusta**: Electronics cai de **59,7% para 53,1%** e Home & Kitchen sobe de 12,6% para 16,4%. Toda leitura de "share de volume" por categoria deve citar as duas versões.

*Por que esta limitação é nova: ela só aparece quando se procura por produtos distintos com volume e nota idênticos — uma verificação que a deduplicação por `product_id` não faz, porque os `product_id` são legitimamente diferentes.*

---

## Como usar no material
- **`.pbix`:** rodapé fixo com L1, L4 e L5 em uma linha cada; página de Recomendações com o bloco completo.
- **Vídeo:** L5 na abertura (10 segundos), L1 imediatamente antes do bloco de Customer Insights, L4 junto às recomendações.
- **Notebook:** todas as oito no cabeçalho do `01_eda`.

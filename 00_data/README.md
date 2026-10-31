# `00_data/` — as três camadas

O arquivo de origem **nunca é alterado**. Ele é lido, e todo resultado é escrito em outra camada. É essa a razão de existir da separação — não o tamanho do arquivo.

Tudo é produzido por `src/prepara_dados.py`, em um comando:

```bash
python3 src/prepara_dados.py
```

## `bronze/` — a origem, intocada · **não versionada**

`amazon.csv` como veio do Kaggle: 1.465 linhas × 16 colunas, tudo em texto, preço com símbolo de moeda e separador de milhar, avaliações concatenadas em uma célula.

**Não sobe para o repositório**, porque traz `user_id` (9.050 distintos) e `user_name` (7.699 distintos) — dado pessoal, e este repositório é público (LGPD, regra T7).

Para obter:
1. Baixar de https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset
2. Colocar em `00_data/bronze/amazon.csv`
3. Conferir o SHA-256: `4ba126c4ba8edd35e62e94ce1c853073d832de380184ab4f5f97d1e314882c77`

O `prepara_dados.py` confere esse hash antes de qualquer coisa e **para** se divergir — se a base for outra, nenhum número do material vale.

## `silver/` — tipado e deduplicado · **dois arquivos**

### `produtos.csv` — 1.351 × 9 · **versionado**
Sem nenhum campo de texto livre. É o que sobe para o GitHub.

### `produtos_texto.csv` — 1.351 × 5 · **NÃO versionado**
`product_id` mais `about_product`, `review_title` e `review_content`.

**Por que fica de fora.** O texto das avaliações traz nomes escritos pelos próprios usuários — assinatura no fim do comentário, seção de perguntas e respostas com o nome de quem perguntou, menção a atendente. Medido: **ao menos 11 nomes completos reais, em 21 produtos (1,6%)**.

Não é a coluna `user_name` — essa foi removida, e T7 está cumprido à letra. Mas identifica autor do mesmo jeito, e as diretrizes §8.1 exigem que comentários sejam tratados **de forma agregada, sem autor identificado**. Um repositório público que declara conformidade LGPD não deveria republicar nome identificável.

*Ressalva honesta sobre a medição:* a detecção compara com a coluna `user_name`, então só encontra nomes que aparecem nos dois lugares. Um nome citado numa avaliação de outro autor passa despercebido. São **pelo menos** 11, não exatamente 11.

O notebook `05_nlp` lê deste arquivo localmente; só os n-gramas agregados são versionados.

| O que aconteceu | Detalhe |
|---|---|
| Conversão de tipo | símbolo de moeda, `%` e separador de milhar removidos **na leitura** |
| Deduplicação determinística | maior `rating_count` por `product_id`; **no empate, menor índice de linha na origem** |
| Colunas pessoais removidas | `user_id`, `user_name` (T7/LGPD) |
| Colunas sem uso removidas | `img_link`, `product_link` |

O desempate não é detalhe: dos 92 `product_id` repetidos, apenas **27** têm máximo único. Nos outros **65** o máximo empata, e sem o critério declarado a base deixa de ser reproduzível.

## `gold/` — pronta para consumo · versionada

`base_analitica.csv` — **1.348 produtos × 17 colunas**. É desta camada que os notebooks leem. O `.pbix` **não** a importa: reconstrói a base no Power Query a partir do bronze e usa esta camada como **gabarito**, na consulta `qa_compara_gold`.

Além das colunas do silver, traz os derivados que o dashboard usa:

| Campo | O que é |
|---|---|
| `nota_corrigida` | limite inferior de Wilson a 95% — obrigatório em todo ranking (T1) |
| `categoria_n1` · `categoria_n2` | níveis da hierarquia; o nível 2 é a unidade de comparação |
| `engajamento` | `alto` (≥ p90 = 36.384) · `intermediario` · `baixo` (< mediana = 4.740) |
| `satisfacao` | `baixa` (< 4,0) · `media` · `alta` (≥ 4,3) |
| `q5_risco_vitrine` | alto engajamento **e** nota < 4,0 — **19 produtos** |
| `q6_subexplorado` | nota **bruta** ≥ 4,3 **e** engajamento abaixo da mediana — **187 produtos**. É o **funil de triagem**: cruzando com `nota_corrigida ≥ 4,3`, restam **61** — a lista acionável, porque T1 exige nota corrigida em todo ranking (relatório §5.19) |
| `faixa_desconto` | cinco faixas, todas acima do piso n ≥ 30 |
| `pareto_80` | os **306 produtos** que concentram 80% das avaliações |

`reviews.csv` — **9.255 reviews distintos**, obtidos explodindo os blocos (10.588 referências) e deduplicando por `review_id`, como T8 exige.

## Reconciliação das cinco bases

| Base | *n* | Como se chega |
|---|---|---|
| Bruta | **1.465** | bronze, como veio |
| Produtos | **1.351** | silver — menos 114 linhas excedentes |
| Nota válida | 1.350 | menos 1 `rating` inválido |
| Engajamento válido | 1.349 | menos 2 `rating_count` nulos |
| **Analítica** | **1.348** | gold — interseção das duas anteriores |

Nenhum número entra em visual sem declarar qual destas usou (T3).

## Moeda

Valores monetários são publicados **sem símbolo**, em rupia indiana, sem conversão (L5). O símbolo existe apenas dentro do bronze, que é texto de origem: a conversão o remove dos preços na leitura e, no único nome de produto que o traz, o substitui pela palavra `rupia`.

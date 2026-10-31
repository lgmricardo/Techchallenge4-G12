# `results/` — saídas dos notebooks e do gerador

Nada aqui é escrito à mão. Tudo é gerado e pode ser regenerado.

| Pasta | Conteúdo |
|---|---|
| `images/` | **32 figuras** |
| `tables/` | **27 tabelas** |

## Duas convenções de nome, e o critério entre elas

| Prefixo | O que é | Fundo | Quantas |
|---|---|---|---|
| `fig01_` a `fig13_` | **figuras do relatório** — citadas em `docs/relatorio_tecnico.md`, geradas por `src/gera_figuras.py` | **branco** (documento impresso) | **13** |
| `fig_<notebook>_<nn>_` | **figuras de notebook** — produzidas durante a análise, com o notebook de origem no nome (`eda`, `trat`, `med`, `an`, `nlp`, `st`) | **creme** (contexto de tela) | **19** |

Os dois fundos são tokens da paleta v06 (`card` e `canvas`), então a diferença **não fere T9** — ela é deliberada: documento impresso em branco, tela no creme do dashboard.

**O número da figura do relatório segue a ordem de aparição no documento**, não a ordem em que o gerador a produz: os blocos de `src/gera_figuras.py` estão na ordem em que o dado fica disponível, e cada um declara no comentário o número que grava.

Havia uma terceira convenção, `fig14_02_` a `fig17_03_`, que numerava figura de notebook na mesma sequência das do relatório. Foi eliminada em 12/10/2026: o prefixo `figNN_` passava a significar duas coisas, e quem abria a pasta não distinguia o que o relatório cita do que é saída intermediária. As quatro foram renomeadas para `fig_trat_01`, `fig_trat_02`, `fig_med_01` e `fig_med_02`, nos notebooks de origem, e os arquivos antigos removidos depois de confirmar que nenhuma referência sobrava.

Tabelas seguem `tab01_` a `tab26_`, numeração sequencial por ordem de criação.

**As `tab19` a `tab21` são listas nominais de produto**, e existem por exigência de regra, não por conveniência: T2 abre exceção ao piso de n ≥ 30 para lista nominal **desde que o n de avaliações apareça produto a produto**. Enquanto elas não eram publicadas, a condição que autoriza a exceção não estava cumprida — e o relatório recomendava ação sobre conjuntos que o leitor não conseguia recuperar.

| Arquivo | Conteúdo | *n* |
|---|---|---|
| `tab19_q5_risco_vitrine_nominal.csv` | volume ≥ p90 (36.384) **e** nota < 4,0 — a fila de revisão prioritária | **19** |
| `tab20_q6_acionavel_nominal.csv` | bem avaliados e pouco comentados, **já corrigidos por Wilson** (medida M22) — não o funil de 187 | **61** |
| `tab21_ancoras_nominal.csv` | volume ≥ p90 **e** nota ≥ 4,3 — o que sustenta a reputação do catálogo | **41** |

As três trazem nome, categoria, subcategoria de nível 2, volume, nota bruta, nota corrigida, preço de tabela e desconto. `src/gera_figuras.py` **falha** se as contagens divergirem de 19, 61 e 41: a lista não pode deixar de bater com o número publicado no texto sem que alguém perceba.

**As duas seguintes são insumos do dashboard**, e existem porque o Power Query refaz a preparação dos dados mas não treina modelo nem lê texto de avaliação (T7):

| Arquivo | Conteúdo | Origem | *n* |
|---|---|---|---|
| `tab22_arquetipo_por_produto.csv` | a letra do arquétipo (ML4) de cada produto — **mesclada na `BaseAnalitica`** por `product_id` | `src/gera_figuras.py` | **1.348** · A 268 · B 335 · C 298 · D 447 |
| `tab23_qa5_temas.csv` | os 9 eixos temáticos codificados nos blocos de Q5, com o denominador em toda linha — importada **sem relacionamento** | `01_notebooks/05_nlp.ipynb` | **9 eixos · 19 blocos** |

As duas falham na origem se divergirem do publicado: o gerador confere as quatro contagens e a soma contra a `tab05`; o notebook confere um eixo por linha do livro de códigos, o denominador 19 e a ausência de coluna de texto ou de usuário.

## Regras

- Toda figura sai da paleta v06 (T9) — ou seja, de código que chamou `aplicar()`.
- Toda figura declara **fonte, base e *n*** no rodapé (T3).
- Figura usada no relatório é referenciada pelo número, e **entra uma única vez**; repetições são remissões textuais.

## Como regerar

```bash
python3 src/gera_figuras.py                       # fig01–fig13 · tab01–tab08 · tab15–tab22 · tab24–tab28
jupyter nbconvert --execute --inplace 01_notebooks/*.ipynb   # as demais (tab09–tab14, tab23 e as figuras de notebook)
```

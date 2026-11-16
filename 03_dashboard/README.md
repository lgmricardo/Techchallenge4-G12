# Entrega 1 — Dashboard `.pbix`

> **Para montar o dashboard:** [`INSTRUCOES_MONTAGEM_POWERBI.md`](INSTRUCOES_MONTAGEM_POWERBI.md) — só o que se executa no Desktop, com os números de conferência de cada passo. É o que fica aberto ao lado do Power BI.

Esta pasta reúne tudo que define o dashboard: o modelo, as medidas com o valor que cada uma precisa reproduzir, o diagrama e a montagem. Os dados e o tema vivem nas pastas de origem — a lista completa está abaixo.

---

## O que está aqui

| Arquivo | Descrição |
|---|---|
| **`INSTRUCOES_MONTAGEM_POWERBI.md`** | **o que se executa no Desktop** — ambiente, Power Query, modelo, medidas, as 7 páginas e a navegação |
| [`GUIA_GRAFICOS_POWERBI.md`](GUIA_GRAFICOS_POWERBI.md) | ficha de montagem de cada um dos 36 visuais: tabela, coluna por poço, ordenação, filtro e formatação |
| `medidas_dax.md` | as **22 medidas** (M01–M22), cada uma com expressão DAX, unidade, denominador, base declarada e **o valor de referência calculado em Python** |
| `modelo_de_dados.md` | as **oito tabelas** em três papéis — duas de fato, cinco de resultado e a de conferência —, as 25 colunas da `BaseAnalitica`, o relacionamento e o que deliberadamente **não** entra no modelo |
| `modelo_de_dados.png` | o diagrama, **gerado** dos arquivos da gold e de `02_results/tables/` — não desenhado à mão |
| `gera_modelo_de_dados.py` | regenera o diagrama; rode se o esquema mudar |
| `modelo_esperado.py` | o modelo como ele **tem de ser**, em um lugar só — lido pelo diagrama e pela conferência do arquivo |
| `valores_referencia.py` | calcula os valores que as medidas DAX precisam reproduzir |
| `valores_referencia.csv` | **25 linhas** — medida a medida, para a reconciliação da Fase 4 |
| `valores_referencia_por_categoria.csv` | as mesmas medidas por categoria, para conferir o **contexto filtrado** |
| `gera_conferencia.py` | gera a página oculta de conferência a partir da referência e do catálogo — **falha** se os dois se desencontrarem |
| `conferencia_referencia.csv` · `conferencia_dax.md` | a tabela `Conferencia` e as 6 medidas `Conf ·`: o `.pbix` confere a si mesmo contra o Python, **`Conf · Divergentes` = 0** |
| `verifica_pbix.py` | confere o arquivo entregue pelo `.pbit`: nenhuma coluna pessoal (T7), nenhuma tabela a mais, tipos, **um** relacionamento 1 → N, as 22 medidas **com a expressão do catálogo**, e que o `.pbit` é do `.pbix` entregue |
| `testa_verifica_pbix.py` | prova que o verificador reprova os 30 defeitos que deve e aprova as 8 variações legítimas — 38 casos |
| `gera_checklist.py` · `checklist_qualidade.md` · `.pdf` | o checklist T1–T9 da F8, uma folha, com os números de cada tela medidos e conferidos contra o guia |
| `screenshots/` | uma imagem por página — **a produzir na Fase 9** |
| `TechChallenge4_G12.pbit` | o esquema legível do modelo, exportado do `.pbix` final — **a produzir na Fase 9** |
| `TechChallenge4_G12.pbix` | o entregável — **a produzir** |

## O que o montador busca fora desta pasta

| Insumo | Onde | Para quê |
|---|---|---|
| `method/design_system/tema_fase4_ambar_ardosia.json` | tema | **importar antes do primeiro visual** (Fase 0.8) |
| `00_data/bronze/amazon.csv` | base de origem | o Power Query parte daqui (Fase 2) — **não vem no git**, baixar do Kaggle |
| `00_data/gold/base_analitica.csv` · `reviews.csv` | base tratada | `base_analitica.csv` é o gabarito da `qa_compara_gold`; `reviews.csv`, da contagem de 9.255 |
| `02_results/tables/tab03_correlacoes.csv` | Spearman (ρ, p, n) | Q3 e QA4, página 3 |
| `02_results/tables/tab05_arquetipos.csv` | resumo dos arquétipos | QA7, página 2c |
| `02_results/tables/tab07_ml2_blocos.csv` | AUC por bloco | Q8, página 5 |
| `02_results/tables/tab14_ngramas.csv` | n-gramas e TF-IDF | página 4 |
| `02_results/tables/tab22_arquetipo_por_produto.csv` | arquétipo de cada produto | QA7 · mesclada na `BaseAnalitica` — ✅ gerada em 26/10 |
| `02_results/tables/tab23_qa5_temas.csv` | temas da QA5 | QA5, página 4 — ✅ gerada em 26/10 |
| `method/definitions/regras_transversais_T1_T9.md` | T1 a T9 | checklist de cada página (Fase 8) |
| `method/limitations/limitacoes_obrigatorias.md` | L1 a L8 | rodapé e página de Recomendações |

## As cinco áreas, em sete páginas

1. **Visão Executiva** — indicadores e visão geral do portfólio
2. **Produtos e Categorias**, dividida em três páginas para caber na tela da gravação:
   **2a Categorias** · **2b Quadrantes** · **2c Rankings**
3. **Preços e Estratégia Comercial** — preço de tabela, preço praticado e desconto
4. **Customer Insights** — conteúdo das avaliações
5. **Recomendações** — o que fazer, com o número de cada recomendação

*O enunciado apresenta essa estrutura como **referência**, não obrigação. O grupo a adotou por decisão própria, e dividir a área 2 em três páginas é decisão registrada.*

## Três coisas antes do primeiro visual

1. **Importar o tema** — `../method/design_system/tema_fase4_ambar_ardosia.json`. **Antes**, não depois: cor escolhida à mão se sobrepõe ao tema e o padrão se perde sem aviso.
2. **Localidade de importação em Inglês (Estados Unidos)**, para que `4.2` seja lido como 4,2 e não como 42.
3. **Rodar os validadores** e confirmar saída `0`:
   ```bash
   python3 ../src/valida_base.py ../00_data/bronze/amazon.csv
   python3 ../src/valida_dicionario.py
   ```

## O que vale em toda página

Rodapé com fonte, base e *n* (**T3**) · todo ranking por nota usa a nota corrigida, com o *n* ao lado (**T1**) · nenhum grupo com n < 30 é comparado (**T2**) · valores sem símbolo de moeda (**L5**) · nada de "vendas", "receita" ou "demanda" (**T6**) · nenhuma frase causal (**T4**) · **um único** elemento em âmbar por página (**T9**).

**Zero dependência externa:** nenhum visual de loja, de Python ou de R. O arquivo tem de abrir e funcionar em qualquer máquina com Power BI Desktop.

# 📊 Amazon Product Performance & Customer Insights

**Tech Challenge — Fase 4 · POSTECH DTAT — 2026**

Análise do desempenho de portfólio e da percepção de consumidores em um marketplace, a partir de **1.348 produtos** e **9.255 avaliações** da base pública `amazon-sales-dataset`. O entregável é um dashboard analítico em Power BI que transforma esses dados em decisões de sortimento, preço e atenção a produto.

> **Em uma frase (para quem não é da área):** olhamos preço, desconto, volume de avaliações e nota de cada produto para responder onde a empresa deve prestar atenção — quais produtos estão sendo muito avaliados e mal avaliados, quais são bem avaliados e têm baixo volume de avaliações, e se descontar mais realmente melhora alguma coisa.

**Integrantes (ordem alfabética):** Efraim Oliveira · Érica Tarsis · Ricardo Moraes · Rodrigo Bernardino · Thiago Galvão

---

## 🎯 Pergunta norteadora

> **"Quais produtos, categorias e estratégias comerciais merecem maior atenção e quais oportunidades podem ser identificadas a partir dos dados disponíveis?"**

As 8 perguntas orientadoras do enunciado e as 4 da seção de Customer Insights são respondidas pelo **escopo fechado de 15 perguntas** em [`method/definitions/escopo_15_perguntas.md`](method/definitions/escopo_15_perguntas.md). Nenhuma análise entra no material sem vínculo com uma delas.

---

## 📦 Entregáveis

O enunciado pede **dois** artefatos, e a estrutura deste repositório coloca os dois em primeiro plano:

| # | Entregável | Onde |
|---|---|---|
| 1 | **Dashboard `.pbix`** — 5 áreas, com tratamento, medidas, visuais, filtros e navegação | [`03_dashboard/`](03_dashboard/) |
| 2 | **Vídeo executivo** — até 7 minutos, apresentação para a liderança | [`04_video/`](04_video/) |

Todo o resto do repositório existe para sustentar esses dois. **Para ler primeiro:** o sumário executivo de 2 páginas, [`docs/executive_summary_phase4_v1_powerbi.pdf`](docs/executive_summary_phase4_v1_powerbi.pdf); a defesa completa está no relatório técnico, [`docs/technical_report_phase4_v1_powerbi.pdf`](docs/technical_report_phase4_v1_powerbi.pdf).

---

## 🗂️ Estrutura

O repositório é organizado pela **ordem fixada de trabalho** do projeto — dados → Python → Power BI → vídeo — com o método que governa tudo isolado em `method/`.

As pastas do **fluxo** são numeradas: a ordem em que aparecem no `ls` é a ordem em que o trabalho acontece. As de **apoio** não têm número.

```text
Techchallenge4-G12/
│
├── 00_data/                 a base, em três camadas
│   ├── bronze/              amazon.csv original, intocado — NÃO versionado (dado pessoal)
│   ├── silver/              produtos.csv (9 colunas, versionado)
│   │                        produtos_texto.csv (texto livre — NÃO versionado, ver LGPD)
│   └── gold/                base_analitica.csv (n = 1.348) · reviews.csv (n = 9.255)
│
├── 01_notebooks/            01_eda · 02_tratamento · 03_medidas
│                            04_analises · 05_nlp · 06_storytelling — nesta ordem
│
├── 02_results/              saídas dos notebooks, todas regeneráveis
│   ├── images/              fig01_*.png … fig13_*.png
│   └── tables/              tab01_*.csv … tab17_*.csv
│
├── 03_dashboard/            ⭐ ENTREGA 1 — o .pbix, o modelo, as 22 medidas DAX
│   └── screenshots/         uma imagem por página
│
├── 04_video/                ⭐ ENTREGA 2 — roteiro, storyboard, cartelas
│
├── method/                  o que governa todo o resto. Ler antes de produzir qualquer coisa
│   ├── definitions/         as 5 bases, dicionário, escopo das 15 perguntas, regras
│   │                        transversais T1–T9, registro de ML, matriz C1–C9
│   ├── limitations/         L1 a L8, com texto pronto para o .pbix e para o vídeo
│   ├── design_system/       tokens de cor v06 + tema do Power BI
│   └── open_decisions.md    D-1 a D-8 — todas fechadas
│
├── src/                     prepara_dados.py (bronze→silver→gold) · valida_base.py
│                            (107 asserções) · valida_dicionario.py (dicionário ×
│                            artefatos) · paleta.py (T9) · gera_figuras.py
│                            · monta_relatorio.py (gera o .docx e o .pdf)
│
└── docs/                    relatório técnico (.md · .docx · .pdf), sumário executivo (2 p.),
    │                        folha de defesa (1 p.) e o enunciado
    └── evidence/            saída datada dos validadores
```

**Por que a numeração para de 04.** `00` a `04` é o fluxo do dado — entra em `00_data`, atravessa Python, sai no dashboard e no vídeo. `method/`, `src/` e `docs/` não são etapas: são transversais, usados em todas elas. Numerá-los sugeriria uma ordem que não existe — e o caso de `method/` deixa isso óbvio: ele precisa ser lido **antes** de qualquer coisa acontecer em `00_data`, então qualquer número que recebesse estaria errado.

Um exemplo do que a numeração erraria: `05_docs` colocaria o relatório **depois** do vídeo, afirmando que ele é escrito por último. É o contrário — o relatório sustenta os dois entregáveis, e não o contrário.

**Por que os arquivos da raiz também não têm número.** Eles não são etapas: são a porta de entrada. `README.md` responde *o que é isto*, `EXECUCAO.md` responde *como rodar*. E dois dos três têm **nome obrigatório**, não escolhido: o GitHub só renderiza a página inicial do repositório se o arquivo se chamar `README.md`, e `pip install -r` espera `requirements.txt` — é o nome que todo tutorial, todo CI e os scanners de dependência procuram. Numerá-los custaria a página inicial e a convenção, sem organizar nada.

**Por que há `bronze/silver/gold`.** As três camadas não estão aqui por cerimônia, e cada uma resolve um problema concreto deste projeto:

| Camada | Função | Por que não dá para juntar com a vizinha |
|---|---|---|
| **bronze** | o CSV original, **nunca alterado** | é a origem auditável: `prepara_dados.py` confere o **SHA-256** dela e **aborta** se não for a base canônica. Sem camada intocada não há essa checagem |
| **silver** | tipos corrigidos, deduplicado, `user_id`/`user_name` eliminados | é onde a **separação LGPD** acontece: `produtos.csv` (9 colunas) é versionado; `produtos_texto.csv` fica fora do git porque o texto das avaliações contém nomes de pessoas reais |
| **gold** | base analítica de 1.348 produtos + corpus de 9.255 reviews | é o que todo notebook, figura e medida DAX consome — um único arquivo canônico, para que dois artefatos nunca discordem |

A separação bronze↔silver é o que torna a reprodutibilidade verificável em um comando, e a separação silver↔gold é o que permite publicar a base tratada **sem publicar dado pessoal**. Juntar as camadas custaria exatamente essas duas garantias.

---

## 📐 Fundamentos que valem para tudo

Quatro coisas governam qualquer número, visual ou frase produzida neste projeto. Estão detalhadas em `method/`, mas resumidas aqui porque ninguém deveria precisar procurá-las:

**1. Cinco bases convivem — toda publicação declara qual usou.**

| Base | *n* | Quando usar |
|---|---|---|
| Bruta | 1.465 | apenas para relatar qualidade da origem |
| Produtos | 1.351 | contagem de portfólio |
| Nota válida | 1.350 | análises que dependem só de `rating` |
| Engajamento válido | 1.349 | análises que dependem só de `rating_count` |
| **Analítica** | **1.348** | **padrão** — toda análise cruzada e modelagem |

**2. `rating_count` é volume de avaliações — nunca vendas, receita ou demanda.** A base não contém variável de venda. Nenhuma recomendação se expressa em receita.

**3. Vedada linguagem causal.** Correlação e importância de variável indicam associação. Magnitude sempre ao lado da significância: com *n* = 1.348, um coeficiente pode ser significativo e irrelevante ao mesmo tempo.

**4. `user_id` e `user_name` não aparecem em lugar nenhum** — visual, slide ou frame de vídeo. Por isso a base versionada não os contém, e o **texto livre das avaliações fica fora do git**: ele carrega nomes de pessoas reais assinando o próprio comentário.

---

## ⚠️ Limitações declaradas

As oito limitações obrigatórias estão em [`method/limitations/`](method/limitations/), com texto pronto. As três que mudam a leitura de tudo:

- **Truncamento em 8 avaliações por produto** (média medida: 7,85). O texto analisado não é amostra aleatória: é o recorte que o marketplace escolheu exibir. Customer Insights descreve **os temas visíveis na vitrine**, não a distribuição real das opiniões.
- **Não existe variável de venda.** Sem receita, margem, estoque ou data — logo, sem análise temporal e sem recomendação em reais.
- **Marketplace indiano, valores em rupia indiana.** Nenhuma conversão aplicada. Transpor para outro mercado é analogia, não resultado.

---

## 🎨 Padrão visual — regra T9

A paleta v06 vale em **todo** artefato: dashboard, notebook, gráfico, tabela, relatório, deck, vídeo e qualquer arquivo gerado. A aplicação é sempre por ferramenta, nunca pelo seletor de cor:

```python
from paleta import aplicar
aplicar()        # configura o matplotlib no padrão do projeto
```

No Power BI, importar `method/design_system/tema_fase4_ambar_ardosia.json` **antes do primeiro visual**. Máximo de 5 séries por visual; com 6, rótulo direto é obrigatório — teal e ardósia são indistinguíveis sob deuteranopia.

---

## ✅ Reprodutibilidade

**Python 3.12** — a versão não é detalhe: a pinagem do `requirements.txt` resolve as bibliotecas, não o interpretador, e `random_state=42` só reproduz os números do ML2 e do ML4 na mesma versão do `scikit-learn`.

```bash
python3.12 -m venv .venv && source .venv/bin/activate    # Windows: py -3.12 -m venv .venv
pip install -r requirements.txt
python3 src/valida_base.py 00_data/bronze/amazon.csv
python3 src/valida_dicionario.py
```

### Verificação em dois minutos — os oito comandos que reprovam o projeto

Um resultado verde não prova nada se ninguém puder provocá-lo a ficar vermelho. Estes oito **falham sozinhos** quando o material deixa de ser verdade, e rodam em menos de dois minutos:

```bash
python3 src/valida_base.py 00_data/bronze/amazon.csv   # 107 asserções, base declarada em cada uma
python3 src/valida_dicionario.py                       # dicionário × artefatos, coluna a coluna
python3 src/gera_figuras.py                            # confere a reconstrução contra a gold antes de desenhar
python3 src/testa_gera_resumo.py                       # planta 41 números errados e exige que o gerador reprove
python3 src/testa_confere_visual.py                    # 10 casos: a trava visual das figuras reprova o que deve
python3 04_video/confere_amarracao.py                  # todo número falado está na tabela · ritmo dentro dos tetos
python3 03_dashboard/testa_verifica_pbix.py            # 36 casos: o verificador do .pbix reprova o que deve
python -m ruff check .                                 # lint, com o padrão declarado em pyproject.toml
```

| Comando | O que ele lê | O que ele pega | Provado |
|---|---|---|---|
| `valida_base` | o **bronze**, e recalcula | SHA da origem alterado · número publicado que deixou de bater com o recálculo | 107 asserções, 0 puladas |
| `valida_dicionario` | dicionário × silver × gold | coluna documentada que não existe, ou que existe sem documentação | plantando uma coluna inexistente no dicionário, **sai com 1** |
| `gera_figuras` | o **bronze** e a **gold** | as duas pipelines de Python divergindo entre si | plantando 0,01 na nota de **1 produto entre 1.348**, **sai com 1** |
| `testa_gera_resumo` | cópias do relatório e do roteiro | sumário afirmando número que o corpo não sustenta | **41 números plantados**, um por vez |
| `testa_confere_visual` | figuras montadas com defeito | eixo de categoria apagado, pizza, série a mais, rodapé ausente **ou cortado pela borda** | **10 casos**, 6 que reprovam e 4 que passam |
| `confere_amarracao` | o roteiro e a tabela de amarração do vídeo | número falado sem linha na tabela · segmento sem fala conferida · bloco denso demais | `--planta`, `--planta-ritmo` e o **roteiro anterior ao corte**, que reprova com ritmo de 4,27 p/s |
| `testa_verifica_pbix` | `.pbit` sintéticos | `.pbix` entregue fora da especificação | **36 casos**, 7 que passam e 29 que falham |
| `ruff check` | o código | import morto, nome indefinido, linha acima do limite | padrão declarado em `pyproject.toml` |

> **Os escopos não se sobrepõem por acaso.** O `valida_base` recalcula a partir do **bronze** e não olha a gold — quem guarda a gold é o `gera_figuras`, que reconstrói a base por um caminho independente e compara. Um só comando cobrindo tudo seria um ponto único de falha; o conjunto existe para que **nenhuma camada se valide sozinha**.

Com o `.pbix` pronto, somam-se dois: `Conf · Divergentes` = 0 na página de conferência, **dentro** do arquivo entregue, e `python3 03_dashboard/verifica_pbix.py` sobre o par `.pbit` + `.pbix`.

O primeiro executa **107 asserções**, cada uma declarando sobre qual das cinco bases foi medida. O segundo cruza o dicionário de dados com os arquivos, **coluna a coluna** — nome declarado que não existe, coluna real sem documentação, contagem errada. Saída 0 nos dois = o material confere e a documentação não divergiu do dado. Passo a passo completo em [`EXECUCAO.md`](EXECUCAO.md).

---

## 🔍 Para quem revisa

A conferência do material não depende de outra pessoa: ela é feita por comandos que falham sozinhos. Para quem quiser auditar, o caminho mais curto:

1. **Conferir um número?** → os oito comandos de *Verificação em dois minutos*, acima; depois `src/valida_base.py` e o notebook que o produz.
2. **Discordar de uma definição?** → `method/definitions/` — cada decisão tem justificativa registrada.
3. **Revisar um visual?** → `method/design_system/tokens_paleta_v06.md` e a checklist T1–T9 em `method/definitions/`.
4. **Saber o que falta?** → `03_dashboard/` e `04_video/` — o que estiver vazio ainda não existe.

---

## 📚 Fonte

Base: Kaggle — [`karkavelrajaj/amazon-sales-dataset`](https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset). Citação obrigatória em todo visual e no material final.

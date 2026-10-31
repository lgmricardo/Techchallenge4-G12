# ▶️ EXECUÇÃO — do zero ao `.pbix` aberto

Comandos literais, na ordem. Nada aqui é narrativa.

## 1. Ambiente

**Python 3.12.** A versão não é detalhe: `random_state=42` só reproduz os números do ML2 e do ML4 na mesma versão do `scikit-learn`, e a pinagem do `requirements.txt` resolve as bibliotecas, não o interpretador. Medido em 3.12.13.

```bash
python3.12 -m venv .venv           # Windows: py -3.12 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python -c "import sys; assert sys.version_info[:2] == (3, 12), sys.version"
```

## 2. Obter a base
A base crua **não é versionada** — contém dado pessoal (ver `00_data/README.md`).

```bash
# baixar de https://www.kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset
# colocar em 00_data/bronze/amazon.csv, e conferir:
shasum -a 256 00_data/bronze/amazon.csv
# esperado: 4ba126c4ba8edd35e62e94ce1c853073d832de380184ab4f5f97d1e314882c77
```

Se o hash divergir, **pare**. A base é outra, e nenhum número do material vale.

## 3. Gerar a base tratada
```bash
jupyter nbconvert --execute --inplace 01_notebooks/02_tratamento.ipynb
```
Produz `00_data/silver/produtos.csv` (9 colunas, versionado), `00_data/silver/produtos_texto.csv` (5 colunas, **fora do git** — texto livre com nomes de pessoas), `00_data/gold/base_analitica.csv` (17 colunas, n = 1.348) e `00_data/gold/reviews.csv` (5 colunas, n = 9.255). Nenhum deles contém `user_id` ou `user_name`.

## 4. Validar
```bash
python3 src/valida_base.py 00_data/bronze/amazon.csv
python3 src/valida_dicionario.py
python3 src/paleta.py
```
O primeiro roda **107 asserções** e sai com 0 se todos os números do material conferem, 1 se algum divergir. O segundo cruza o **dicionário de dados** com os arquivos reais, coluna a coluna — ele existe porque o dicionário já descreveu cinco campos com nomes que o pipeline havia abandonado, e nenhuma revisão humana pega isso. O terceiro confere a paleta contra o tema do Power BI.

**Rodar os três antes de fechar qualquer página do dashboard.** Todos saem com 0 quando não há divergência.

## 5. Reproduzir as análises e todos os artefatos
```bash
# os seis notebooks, nesta ordem
for nb in 01_eda 02_tratamento 03_medidas 04_analises 05_nlp 06_storytelling; do
  jupyter nbconvert --to notebook --execute --inplace 01_notebooks/$nb.ipynb
done

python3 src/gera_figuras.py                    # 13 figuras do relatório · tab01–08 · satisfação e matriz tab15–18 · listas nominais tab19–21 · arquétipo tab22 · correlações de apoio tab24 · importância do ML2 tab25 · teste B × D tab26 · vazamento do ML2 tab27 · fatia abaixo de 4,0 por faixa tab28
python3 03_dashboard/valores_referencia.py     # o valor que cada medida DAX precisa reproduzir
python3 03_dashboard/gera_modelo_de_dados.py   # diagrama do modelo, lido da gold e de 02_results/tables/
python3 03_dashboard/gera_conferencia.py       # página de conferência DAX × Python (tabela + medidas)
python3 03_dashboard/gera_checklist.py         # checklist T1–T9 da F8, conferido contra o guia
python3 03_dashboard/testa_verifica_pbix.py    # prova que o verificador do .pbix reprova o que deve
python3 04_video/numeros_roteiro.py            # todo número falado no vídeo
python3 04_video/gera_storyboard.py            # storyboard extraído do roteiro + conferência da cronometragem
python3 04_video/confere_amarracao.py          # todo número falado existe na tabela, e a fala cabe em 2,6 p/s
python3 src/monta_relatorio.py                 # relatório técnico em .docx e .pdf
python3 src/gera_resumo.py                     # sumário executivo (2 p.) e folha de defesa (1 p.)
python3 src/testa_gera_resumo.py               # prova que o gerador do sumário reprova número errado (41 casos)
python3 src/testa_confere_visual.py            # prova que a trava visual das figuras reprova o que deve (10 casos)
python -m ruff check .                         # lint: limite de linha e regras declarados em pyproject.toml
```
Saídas em `02_results/images/`, `02_results/tables/`, `03_dashboard/`, `04_video/` e `docs/`.

**Estes comandos falham de propósito quando algo diverge**, em vez de gerar um artefato errado: `gera_figuras.py` se as listas nominais não tiverem 19, 61 e 41 produtos ou os arquétipos saírem de 268 · 335 · 298 · 447; `gera_storyboard.py` se a cronometragem do roteiro não fechar ou passar de 7:00; `confere_amarracao.py` se a fala passar de 2,6 palavras por segundo ou citar número que não esteja na tabela de amarração; `gera_modelo_de_dados.py` se o guia não criar as colunas que o modelo declara; `gera_conferencia.py` se o catálogo DAX e a referência se desencontrarem; `gera_checklist.py` se um número do guia não bater com o dado; `gera_resumo.py` se o sumário trouxer número que o corpo do relatório não traz, ou se um número falado no vídeo não estiver no relatório; e `valida_dicionario.py` (passo 4) se o dicionário descrever colunas que os dados não têm.

**Com o `.pbix` pronto**, o arquivo entregue é conferido pelo esquema exportado (*Arquivo > Exportar > Modelo do Power BI*):
```bash
python3 03_dashboard/verifica_pbix.py 03_dashboard/TechChallenge4_G12.pbit 03_dashboard/TechChallenge4_G12.pbix
```

## 6. Abrir o dashboard
1. Abrir `03_dashboard/TechChallenge4_G12.pbix`
2. Se for construir do zero: **importar `method/design_system/tema_fase4_ambar_ardosia.json` antes do primeiro visual**
3. Conferir cada medida DAX contra o valor de referência em `03_dashboard/medidas_dax.md`

## Se algo não reproduzir
1. Conferir o SHA-256 da base (passo 2)
2. Conferir as versões: `pip freeze | grep -E 'pandas|scipy|scikit-learn'` — precisam bater com `requirements.txt`
3. Rodar `src/valida_base.py`: ele diz **qual** número divergiu e sobre qual base

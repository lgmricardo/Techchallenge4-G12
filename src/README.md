# `src/` — código reutilizável

Sete scripts, o teste de um deles e um módulo de apoio. Todos leem a camada certa, nenhum escreve no bronze.

| Script | O que faz | Quando rodar |
|---|---|---|
| `prepara_dados.py` | bronze → silver → gold. Confere o SHA-256 do bronze e **para** se divergir | depois de baixar a base, e sempre que a regra de tratamento mudar |
| `valida_base.py` | **107 asserções** sobre a base, cada uma declarando sobre qual das cinco bases foi medida (T3) | **antes de fechar qualquer página do dashboard** |
| `valida_dicionario.py` | cruza `method/definitions/dicionario_de_dados.md` com os artefatos, **coluna a coluna**: nome declarado que não existe, coluna real sem documentação, contagem de §3 errada, dado pessoal vazado | sempre que o esquema ou o dicionário mudar |
| `paleta.py` | a paleta v06 aplicável (T9): `aplicar()`, `mapa_sequencial()`, `mapa_divergente()`, `checar_series()`, **`rodape()`** (o rodapé de fonte quebrado na largura da figura) e **`confere_visual()`** | importado pelos notebooks; rodado sozinho, confere contra o tema |
| `ml2.py` | módulo, não script: **a** validação do ML2, uma só — `StratifiedGroupKFold` agrupado pelo par `(avaliacoes, nota)`, a regra de variante da L8. Antes eram três cópias (figura, notebook 04, tabela do vídeo), todas com `StratifiedKFold` ingênuo, que deixava a gêmea de um anúncio no treino e a outra no teste e inflava o AUC de 0,034 a 0,066 por bloco | importado por `gera_figuras.py`, pelo notebook 04 e por `04_video/numeros_roteiro.py` |
| `gera_figuras.py` | as 13 figuras do relatório e 21 tabelas — `tab01`–`tab08`, satisfação por grupo e matriz de relevância `tab15`–`tab18`, as listas nominais `tab19`–`tab21`, o arquétipo de cada produto `tab22` as correlações de apoio `tab24` e a importância de atributos do ML2 `tab25` e o teste B × D `tab26`, o vazamento do ML2 `tab27` e a fatia abaixo de 4,0 por faixa de desconto `tab28` —, a partir da base canônica. **Falha** se as listas não tiverem 19, 61 e 41 produtos ou os arquétipos saírem de 268 · 335 · 298 · 447 | quando um número mudar |
| `monta_relatorio.py` | `docs/relatorio_tecnico.md` → `.docx` + `.pdf`, pela mesma fonte | quando o relatório mudar |
| `gera_resumo.py` | o **sumário executivo** (2 páginas, extraído do relatório) e a **folha de defesa** (1 página, os números do vídeo com a seção onde cada um está). **Falha** se o sumário trouxer número que o corpo do relatório não traz, ou se um número falado no vídeo não estiver no relatório | depois de `monta_relatorio.py`, sempre que o relatório ou o roteiro mudar |
| `testa_gera_resumo.py` | prova de que a trava de `gera_resumo.py` reprova o que deve: planta 40 números errados, um por vez, em cópias do relatório e do roteiro, e exige que o gerador falhe em cada um e passe nas cópias intactas. Não toca no projeto | sempre que a regra de `gera_resumo.py` mudar |
| `gera_figuras.py` **confere contra a gold** | antes de desenhar qualquer coisa, compara a base que ele reconstrói do bronze com `00_data/gold/base_analitica.csv` em 7 colunas e **falha** se divergirem. A regra de Wilson existe em dois arquivos e a de deduplicação em três: sem essa trava, uma alteração em `prepara_dados.py` não replicada aqui produziria figuras silenciosamente diferentes da camada que o dashboard consome | — |
| `testa_confere_visual.py` | prova que a trava visual de `gera_figuras.py` reprova o que deve: monta figura sem rodapé, com pizza, com 6 séries e com o eixo de categoria apagado, e com o rodapé cortado pela borda, e exige que cada uma seja acusada — e que as quatro corretas passem. **10 casos** | sempre que uma regra visual mudar |
| `determinismo.py` | módulo, não script: fixa data e identificadores dos PDF e DOCX, para que gerar de novo sem mudar nada produza os mesmos bytes. Usado por `monta_relatorio.py`, `gera_resumo.py` e `03_dashboard/gera_checklist.py` | — |

## Uso

```bash
python3 src/prepara_dados.py                                  # bronze → silver → gold
python3 src/valida_base.py 00_data/bronze/amazon.csv          # 0 = tudo confere · 1 = divergência
python3 src/valida_dicionario.py                              # dicionário × artefatos, coluna a coluna
python3 src/paleta.py                                         # confere a paleta contra o tema
python3 src/gera_figuras.py                                   # 13 figuras + 21 tabelas
python3 src/monta_relatorio.py                                # .docx e .pdf do relatório
python3 src/gera_resumo.py                                    # sumário executivo e folha de defesa
python3 src/testa_gera_resumo.py                              # 41 casos: a trava reprova o que deve
```

## Nos notebooks

Primeira célula de código, sempre — sem isso os gráficos saem na paleta padrão da biblioteca, o que descumpre T9:

```python
import sys; sys.path.insert(0, '../src')
from paleta import aplicar
aplicar()
```

## `fonts/`

DejaVu Sans, embutida para a geração do PDF. As fontes padrão do reportlab não têm `ρ`, `⁻⁸`, `≥` nem `×` — sem ela esses caracteres saem como quadrados pretos. Ver `fonts/README.md`.

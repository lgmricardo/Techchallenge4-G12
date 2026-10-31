# ✅ MATRIZ DE ADERÊNCIA AOS 9 CRITÉRIOS DE AVALIAÇÃO

**Fecha a segunda metade da decisão D-7.** O catálogo de medidas está em `03_dashboard/medidas_dax.md`; esta é a matriz que faltava.

Os nove critérios são os do enunciado (pág. 7), com a redação literal dele.

| # | Critério | O que o enunciado avalia | Onde está atendido | Evidência verificável | Estado |
|---|---|---|---|---|---|
| **C1** | Compreensão do problema | *capacidade de interpretar o contexto de negócio* | relatório §1 · §3.9 · as 8 limitações (`method/limitations/`) | a separação entre o que a base entrega (vitrine) e o que não entrega (venda) está declarada antes de qualquer número · **as cinco fontes que o enunciado lista estão **mapeadas uma a uma** (tabela da §3.9): quatro entram na análise e as *Descrições Dos Produtos* ficam de fora, com a exclusão justificada e o que se perde | ✅ |
| **C2** | Preparação dos dados | *qualidade das transformações realizadas* | `src/prepara_dados.py` · `src/valida_base.py` · `src/valida_dicionario.py` · notebooks `01_eda` e `02_tratamento` · relatório §2 e §3 | **107 asserções** com `exit 0` e **0 puladas** · **dicionário conferido coluna a coluna**, com `exit 0` · deduplicação determinística com desempate declarado · os 6 notebooks executam sem erro · a réplica em Power Query está especificada em 16 passos, com `qa_compara_gold` exigindo **zero linhas** contra a gold | ✅ **em Python**; a réplica no Power Query viaja junto com C6 |
| **C3** | Indicadores | *relevância das métricas criadas* | `03_dashboard/medidas_dax.md` — **22 medidas** (M01–M22) | cada medida tem expressão DAX, unidade, denominador, base declarada (T3) e **valor de referência calculado em Python** | ✅ |
| **C4** | Análise | *capacidade de identificar padrões e oportunidades* | relatório §5 (15 perguntas) e §6 (ML) | 4 correlações com ρ **e** p, mais 2 de apoio (`tab24`) · matriz de relevância · Pareto · **o conflito central B × D submetido a teste** (Mann-Whitney com tamanho de efeito, `tab26`, §5.17) · ML2 com AUC por bloco **e o ranking de importância de atributos publicado** (`tab25`, §6.3), com a ressalva de que a importância de impureza subestima categórica em *one-hot* · ML4 com especificação de reprodução | ✅ |
| **C5** | Customer Insights | *exploração da percepção dos consumidores* | relatório §7 (§7.7 e §7.8) · roteiro, bloco 5 | contraste de n-gramas no recorte Electronics, com teste de robustez · leitura qualitativa dirigida dos 19 de Q5 · **dois focos de insatisfação (a distinção por dispersão, como hipótese)** · **o vídeo diz tema, não só método**: produto que para de funcionar na faixa baixa; instalação, velocidade e imagem na alta (4:40–4:50) · cobertura das 4 perguntas do enunciado amarrada em §7.1 e em `escopo_15_perguntas.md` §6 | ✅ |
| **C6** | Dashboard | *clareza, organização e interatividade* | `03_dashboard/` — modelo, 22 medidas, tema, guia de montagem · relatório §9 | modelo fechado · tema v06 conferido · **5 áreas em 7 páginas** · **36 fichas de visual** (`GUIA_GRAFICOS_POWERBI.md`) com tabela, coluna por poço, filtro e formatação · página de Conferência DAX × Python e `verifica_pbix.py` prontos · a página 5 declara, em quatro linhas, **como os números foram conferidos** (G-36) | 🔨 **em construção** — o `.pbix` é o último item da ordem fixada |
| **C7** | Insights | *relevância das descobertas* | relatório §5.20 · Resumo Executivo | B × D (desconto quase igual, resultado oposto) · 19 de Q5 · 61 de Q6 corrigidos · dois focos de insatisfação | ✅ |
| **C8** | Recomendações | *capacidade de transformar dados em ações* | relatório §Recomendações | 5 recomendações, cada uma ligada a um número medido e **nenhuma expressa em receita** (L4) | ✅ |
| **C9** | Vídeo executivo | *clareza, objetividade e narrativa* | `04_video/roteiro.md` · `storyboard.md` · `confere_amarracao.py` · relatório §10 | os **7 blocos do enunciado**, na ordem, encerrando na pergunta final com 4 mensagens · L5, L1 e L4 ditas em voz alta, com posição e tempo reservados · **o bloco de Customer Insights entrega tema**: produto que para de funcionar na faixa baixa, instalação, velocidade e imagem na alta · as 4 recomendações faladas são **quatro das cinco** do relatório, em outra ordem (a quinta, governança em três famílias, fica no relatório e no dashboard), incluindo os 61 de Q6 · todo número falado consta de `tab_roteiro_numeros.csv` com base e *n* · cronometragem conferida pelo `gera_storyboard.py` · **amarração e ritmo conferidos pelo `confere_amarracao.py`** | 🔨 **em construção** — gravação pendente; **o roteiro está fechado**. A fala mede **1.000 palavras em 410 s = 2,44 p/s** (≈ 2,9 lendo os numerais por extenso), dentro da faixa de apresentação executiva (2,3 a 2,6), e nenhum bloco passa de 2,62. `confere_amarracao.py` reprova o roteiro se a fala citar número fora da tabela de amarração ou passar de 2,6 p/s |

## A resposta ao item 2 do protocolo, pronta

O protocolo abaixo pergunta, para cada critério, *"como um avaliador confirma em 2 minutos?"*. A resposta não é um texto: são oito comandos que **falham sozinhos** quando o material deixa de ser verdade.

| Comando | Confirma | Provado contra |
|---|---|---|
| `python3 src/valida_base.py 00_data/bronze/amazon.csv` | **C2 · C3 · C4** — recalcula do **bronze** e confere contra o publicado | 107 asserções, 0 puladas |
| `python3 src/valida_dicionario.py` | **C2** — dicionário × silver × gold, coluna a coluna | coluna inexistente plantada: sai com 1 |
| `python3 src/gera_figuras.py` | **C2** — as duas pipelines de Python não divergiram | 0,01 em 1 produto de 1.348 derruba a geração |
| `python3 src/testa_gera_resumo.py` | **C7 · C8** — o resumo não afirma o que o relatório não sustenta | 41 números plantados |
| `python3 03_dashboard/testa_verifica_pbix.py` | **C6** — o verificador do `.pbix` reprova o que deve | 36 casos |
| `python3 src/testa_confere_visual.py` | **C4 · C6** — as regras visuais conferidas na figura, não no código, **inclusive o rodapé cortado pela borda** | 10 casos: 6 reprovam, 4 passam |
| `python3 04_video/confere_amarracao.py` | **C9** — todo número falado tem linha na tabela, e o ritmo cabe nos tetos, no total e por bloco | `--planta` (número inventado) e `--planta-ritmo` reprovam; o roteiro anterior ao corte reprova |
| `python -m ruff check .` | engenharia — sem import morto, com padrão declarado | `pyproject.toml` |

Com o `.pbix`: `Conf · Divergentes` = 0 (**C3 · C6**, dentro do arquivo entregue) e `verifica_pbix.py` sobre o par `.pbit` + `.pbix`.

## Protocolo de autoavaliação — antes de cada entrega

Para cada critério, responder com evidência, não com opinião:

1. **Onde isso está?** Arquivo e seção. Se não houver, o critério não está atendido.
2. **Como um avaliador confirma em 2 minutos?** Comando que roda, tabela que abre, página que existe.
3. **Qual é o ponto mais fraco aqui?** Se não souber responder, ninguém testou o critério ainda.

## Estado consolidado

**Sete critérios atendidos e verificáveis hoje: C1, C2, C3, C4, C5, C7 e C8.** Os dois restantes — **C6 e C9** — são os dois artefatos que o enunciado exige, e estão **em construção**: a ordem fixada do projeto deixa o `.pbix` e a gravação por último, depois que todo o resto está medido e conferido.

**O que mudou nesta revisão, e por que a honestidade da autoavaliação importa.** Uma auditoria do material encontrou três declarações generosas nesta própria matriz, e elas foram corrigidas na origem, não na redação:

| Critério | O que a matriz dizia | O que foi feito |
|---|---|---|
| **C4** | dava o ML2 como entregue com o AUC | o AUC diz que o sinal é multivariado, não **quais** atributos o carregam. O ranking de importância passou a ser **gerado e publicado** (`tab25`, §6.3), com a ressalva metodológica que impede a leitura errada |
| **C5** | afirmava que o vídeo entrega tema, não só método | o roteiro **não dizia nenhum tema**. Passou a dizer, em 4:40–4:50 |
| **C9** | dava o roteiro como cronometrado em 6:50 | a soma dos tempos fecha em 6:50, mas a **fala** exige 4,3 palavras por segundo. O risco está agora declarado na linha de C9 |

Uma matriz que se dá por atendida onde não está custa mais caro do que a lacuna que ela esconde: quem avalia encontra a primeira e passa a conferir todas as outras.

*Criada em 01/10/2026, fechando a decisão D-7 · revisada em 31/10/2026 contra a auditoria do material.*

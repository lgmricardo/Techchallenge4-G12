# `docs/` — documentação de apoio

| Arquivo | O que é | Para quem |
|---|---|---|
| `technical_report_phase4_v1_powerbi.pdf` · `.docx` | o **relatório técnico completo** — o que defende o trabalho | avaliador · o grupo na defesa |
| `executive_summary_phase4_v1_powerbi.pdf` · `.docx` | **sumário executivo, 2 páginas** — a mensagem central, os três achados, as quatro mensagens e as cinco recomendações, **extraídos** do relatório | liderança · primeiro contato do avaliador |
| `defense_sheet_phase4_v1_powerbi.pdf` · `.md` | **folha de defesa, 1 página** — cada número falado no vídeo com base, *n*, a seção do relatório onde está e a regra que o protege | o grupo, ao vivo, na defesa |
| `relatorio_tecnico.md` | a **fonte** dos três acima; os `.pdf` e `.docx` são gerados dele | quem edita |
| `evidence/` | saída datada dos validadores | quem audita |

**Nada aqui é escrito à mão duas vezes.** O relatório sai de `relatorio_tecnico.md` por `src/monta_relatorio.py`; o sumário e a folha de defesa saem do mesmo `.md` e de `04_video/tab_roteiro_numeros.csv` por `src/gera_resumo.py` — que **falha** se o sumário trouxer um número que o corpo do relatório não traz, ou se um número falado no vídeo não estiver no relatório.

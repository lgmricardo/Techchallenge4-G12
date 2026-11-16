# Entrega 2 — Vídeo executivo

Meta do grupo: **6 minutos** (o enunciado admite até 7), simulando uma apresentação para a liderança da empresa.

Desde 12/11/2026 o roteiro segue o **Manual de Leitura do Dashboard** (`docs/manual_leitura_dashboard_v1.pdf`): abre com a preparação dos dados e o método e depois passa pelas páginas do Power BI, dizendo em cada uma o que ler e onde clicar. As telas citadas no roteiro usam a numeração dos itens do manual.

## O que vai aqui
| Arquivo | Descrição |
|---|---|
| `roteiro.md` | **a fonte da verdade** — texto falado e o que aparece na tela, com marcação de tempo segmento a segmento |
| `roteiro_video_v1.docx` · `.pdf` | o roteiro em Word e PDF, para ler e imprimir — **gerados** de `roteiro.md` por `python3 src/monta_roteiro.py`; não editar à mão |
| `storyboard.md` | o que aparece na tela em cada momento — **gerado** de `roteiro.md` por `gera_storyboard.py`; não editar à mão |
| `gera_storyboard.py` | extrai o storyboard do roteiro e **confere a cronometragem**: segmentos contínuos, somas iguais à duração de cada bloco, total dentro de 6:00. Se não fechar, falha em vez de gerar |
| `numeros_roteiro.py` | calcula todo número falado no vídeo, a partir da gold |
| `confere_amarracao.py` | confere o roteiro contra a tabela: todo número **falado** tem de existir nela, comparado por valor, e a fala tem de caber em 2,6 palavras por segundo. `--planta` prova que ele reprova; passar um roteiro por argumento confere uma versão antiga |
| `tab_roteiro_numeros.csv` | os números do vídeo, com base e *n* — **o que não está aqui não é dito** |
| `cartelas/` | artes e slides de apoio — **paleta v06** (T9) |

A gravação em si **não é versionada** (arquivo pesado). Publicar por link e registrar aqui.

## Os sete blocos exigidos
1. Contexto do problema · 2. Principais indicadores · 3. Principais insights · 4. Demonstração do dashboard · 5. Customer Insights · 6. Recomendações · 7. Conclusão executiva

**Encerra respondendo:** *"Quais são as principais mensagens que a liderança deve levar a partir desta análise?"*

## Limitações que precisam ser ditas em voz alta
- **Abertura (0:12–0:24):** mercado indiano, valores em rupia, sem conversão; volume de avaliações não é venda.
- **No início de Customer Insights (4:00–4:12):** a base traz no máximo 8 avaliações por produto — são os temas **visíveis na vitrine**, não a distribuição real das opiniões. Nenhuma frase deste bloco começa com "a maioria dos clientes".
- **Junto às recomendações (5:08–5:20):** não há variável de venda. Nenhuma recomendação em receita ou volume vendido.

## As duas medições do roteiro

A cronometragem soma os tempos escritos e fecha em 5:50, com 10 s de margem para 6:00; ela **não mede a fala**. A segunda medição é a fala: **748 palavras em 350 s = 2,14 por segundo** (≈ 2,4 lendo os numerais por extenso), abaixo do teto de apresentação executiva (2,6 p/s), o que deixa folga para pausas na demonstração ao vivo.

Qualquer alteração no roteiro precisa passar de novo por `confere_amarracao.py`, que reprova a fala se um número falado não estiver na tabela de amarração ou se o ritmo passar dos tetos, no total e por bloco. A medição que decide é a **leitura em voz alta, cronometrada**.

## Storytelling
Quatro elementos obrigatórios: **Personagem** (o herói é a liderança, nunca a marca) · **Ambiente** · **Conflito** · **Mensagem**.

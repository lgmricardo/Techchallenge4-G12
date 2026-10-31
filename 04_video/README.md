# Entrega 2 — Vídeo executivo

Até **7 minutos**, simulando uma apresentação para a liderança da empresa.

## O que vai aqui
| Arquivo | Descrição |
|---|---|
| `roteiro.md` | **a fonte da verdade** — texto falado e o que aparece na tela, com marcação de tempo segmento a segmento |
| `storyboard.md` | o que aparece na tela em cada momento — **gerado** de `roteiro.md` por `gera_storyboard.py`; não editar à mão |
| `gera_storyboard.py` | extrai o storyboard do roteiro e **confere a cronometragem**: segmentos contínuos, somas iguais à duração de cada bloco, total dentro de 7:00. Se não fechar, falha em vez de gerar |
| `numeros_roteiro.py` | calcula todo número falado no vídeo, a partir da gold |
| `confere_amarracao.py` | confere o roteiro contra a tabela: todo número **falado** tem de existir nela, comparado por valor, e a fala tem de caber em 2,6 palavras por segundo. `--planta` prova que ele reprova; passar um roteiro por argumento confere uma versão antiga |
| `tab_roteiro_numeros.csv` | os números do vídeo, com base e *n* — **o que não está aqui não é dito** |
| `cartelas/` | artes e slides de apoio — **paleta v06** (T9) |

A gravação em si **não é versionada** (arquivo pesado). Publicar por link e registrar aqui.

## Os sete blocos exigidos
1. Contexto do problema · 2. Principais indicadores · 3. Principais insights · 4. Demonstração do dashboard · 5. Customer Insights · 6. Recomendações · 7. Conclusão executiva

**Encerra respondendo:** *"Quais são as principais mensagens que a liderança deve levar a partir desta análise?"*

## Limitações que precisam ser ditas em voz alta
- **Abertura (≈10s):** mercado indiano, valores em rupia, sem conversão.
- **Imediatamente antes de Customer Insights:** a base traz no máximo 8 avaliações por produto — são os temas **visíveis na vitrine**, não a distribuição real das opiniões. Nenhuma frase deste bloco começa com "a maioria dos clientes".
- **Junto às recomendações:** não há variável de venda. Nenhuma recomendação em receita ou volume vendido.

## As duas medições do roteiro

A cronometragem soma os tempos escritos e fecha em 6:50; ela **não mede a fala**. A segunda medição é a fala: **1.000 palavras em 410 s = 2,44 por segundo** (≈ 2,9 lendo os numerais por extenso), dentro da faixa de apresentação executiva (2,3 a 2,6 p/s).

Qualquer alteração no roteiro precisa passar de novo por `confere_amarracao.py`, que reprova a fala se um número falado não estiver na tabela de amarração ou se o ritmo passar dos tetos, no total e por bloco. A medição que decide é a **leitura em voz alta, cronometrada**.

## Storytelling
Quatro elementos obrigatórios: **Personagem** (o herói é a liderança, nunca a marca) · **Ambiente** · **Conflito** · **Mensagem**.

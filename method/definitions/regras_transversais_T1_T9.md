# ⚖️ REGRAS TRANSVERSAIS T1–T9
**Valem para todas as perguntas do escopo, sem exceção. Não são pergunta — são requisito de construção.**
Versão harmonizada em 23/09/2026; substitui a redação anterior de T1–T7.
**T9 acrescentada em 24/09/2026**, por decisão de Ricardo: a paleta passa a valer em todo o material, não só no `.pbix`.

| # | Regra | Motivo |
|---|---|---|
| **T1** | Todo ranking por nota usa o **limite inferior de Wilson a 95%** — método fixado por D-3 em 01/10/2026; a média bayesiana foi descartada por exigir arbitrar um *prior* —, com o *n* de avaliações exibido ao lado. A ressalva é declarada: Wilson é um intervalo para proporção binomial, aplicado aqui à nota normalizada de 1–5 para 0–1, e isso é **aproximação deliberada** | sem correção, um produto com 5 avaliações lidera o ranking de "melhores produtos" |
| **T2** | **Nenhum grupo agregado — categoria, subcategoria, faixa ou cluster — com n < 30 é ranqueado ou comparado.** Supressão declarada no rodapé. **Listas nominais de produtos (Q5, Q6, QA5) não são grupos agregados** e não estão sujeitas ao piso; exibem o *n* de avaliações produto a produto | 5 das 9 categorias de nível 1 somam 7 produtos; sem a segunda frase, a regra eliminaria por engano o quadrante de 19 produtos |
| **T3** | Todo visual declara **fonte, base usada, *n* efetivo e limiar aplicado** | cinco bases convivem: 1.465 · 1.351 · 1.350 · 1.349 · 1.348 |
| **T4** | **Vedada linguagem causal.** Correlação, coeficiente e importância de variável indicam associação | "desconto alto causa nota baixa" é indefensável |
| **T5** | **Magnitude sempre junto com significância** | com n = 1.348, ρ = −0,132 é significativo e pequeno ao mesmo tempo |
| **T6** | `rating_count` é **volume de avaliações** — nunca vendas, receita ou demanda. **"Engajamento" é o rótulo de negócio de `rating_count`; "visibilidade" é conceito distinto.** D-1 fechou adotando volume abaixo da mediana como ***proxy* declarado de exposição** — declarado justamente por não ser visibilidade medida: a base não tem impressão, clique nem posição de busca. Fica **vedado** escrever "baixa visibilidade" em visual, slide ou frame; o rótulo publicado é *"bem avaliados com baixo volume de avaliações"* | proxy, não resultado de negócio; os dois termos vinham sendo usados como sinônimos |
| **T7** | **Vedado exibir `user_name` ou `user_id`** em visual, slide ou frame do vídeo | LGPD — dado pessoal |
| **T8** | Todo método textual declara a **unidade** (bloco de review ou review individual), **deduplica por `review_id`** e cita a **limitação de truncamento em 8 avaliações** | há 1.333 referências repetidas; sem a declaração, o corpus aparece 14% maior do que é |
| **T9** | **Toda saída visual do projeto usa exclusivamente a paleta v06** — `.pbix`, notebook, gráfico em Python, tabela, relatório, deck, vídeo, diagrama e qualquer arquivo gerado. A aplicação é sempre por **ferramenta**, nunca à mão: `tema_fase4_ambar_ardosia.json` no Power BI, `src/paleta.py` em Python. **Máximo de 5 séries** por visual; com 6, rótulo direto em teal e ardósia é obrigatório. Cor escolhida no seletor, herdada de template ou de biblioteca é descumprimento | o padrão só é padrão se valer fora do `.pbix`. A rubrica avalia dashboard **e** vídeo: se não parecerem o mesmo produto, a inconsistência é visível antes de qualquer número. E teal × ardósia ficam em ΔE 1,6 sob deuteranopia — indistinguíveis — o que torna o limite de séries uma regra de leitura, não de gosto |

## Ponto de verificação obrigatório antes de publicar

Checklist aplicado a cada página do `.pbix` e a cada bloco do vídeo:

- [ ] todo número tem base declarada (T3)
- [ ] todo ranking por nota está corrigido (T1)
- [ ] nenhum grupo abaixo de 30 foi ranqueado (T2)
- [ ] nenhuma frase afirma causa (T4)
- [ ] toda associação mostra magnitude e significância (T5)
- [ ] `rating_count` não foi chamado de venda ou demanda (T6)
- [ ] nenhum identificador de consumidor aparece (T7)
- [ ] todo corpus textual declara unidade e truncamento (T8)
- [ ] a saída usa a paleta v06 aplicada por tema ou módulo, e respeita o limite de séries (T9)

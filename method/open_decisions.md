# 🔸 REGISTRO DE DECISÕES

As oito decisões do projeto, **todas fechadas**. A coluna "bloqueia" registra o que cada uma bloqueava enquanto esteve aberta.

| # | Decisão | Bloqueia | Recomendação registrada |
|---|---|---|---|
| ~~D-1~~ | ~~Visibilidade~~ | — | ✅ **FECHADA em 24/09/2026:** visibilidade não é mensurável nesta base; adotado volume de avaliações abaixo da mediana como **proxy declarado de exposição**. Q6 fecha em **187 candidatos** por nota bruta — dos quais **61** sobrevivem à correção de Wilson e formam a lista acionável. Ver relatório §5.16 |
| ~~D-2~~ | ~~Fórmula de relevância~~ | — | ✅ **FECHADA em 24/09/2026:** matriz 2×2 sobre os cortes já operacionais (volume ≥ p90 × nota ≥ 4,3), sem limiar novo. Reproduz Q5=19 e Q6=187 e nomeia os quadrantes Âncora (41) e Cauda frágil (227). Ver relatório §5.16 |
| ~~D-3~~ | ~~`nota_corrigida`: Wilson ou média bayesiana~~ | — | ✅ **FECHADA em 01/10/2026:** adotado o **limite inferior de Wilson a 95%**. Não exige arbitrar *prior*, e já está materializado como coluna `nota_corrigida` no gold, no catálogo DAX (M07) e em todo ranking do relatório. A escolha é declarada com a ressalva metodológica: Wilson é um intervalo para proporção binomial, aplicado aqui à nota normalizada de 1–5 para 0–1 — é uma aproximação deliberada, e está dita no relatório |
| ~~D-4~~ | ~~Tema: promover as 4 cores da escala teal a tokens~~ | — | ✅ **FECHADA em 24/09/2026:** as 4 cores entraram na paleta v06 como escala categórica; não se criaram tokens novos. Ver `method/design_system/tokens_paleta_v06.md` |
| ~~D-5~~ | ~~`about_product`~~ | — | ✅ **FECHADA em 01/10/2026 — exclusão justificada:** a coluna descreve o que o vendedor *promete*, não o que o consumidor *percebe*. Customer Insights mede percepção, e misturar as duas fontes confundiria promessa com experiência. O enunciado **lista as Descrições Dos Produtos entre as cinco fontes do desafio**, e por isso a exclusão é respondida por extenso no relatório (§3.9): o que se perde é o confronto entre atributo anunciado e queixa recebida, e o que se ganha é não confundir promessa do vendedor com percepção do consumidor, que é o que Customer Insights mede. A coluna fica preservada na silver não versionada. Fica fora da camada gold, com este motivo registrado |
| ~~D-6~~ | ~~Confirmar com a instituição a data oficial de entrega~~ | — | ✅ **FECHADA em 12/10/2026** por decisão de Ricardo: a data não condiciona nenhum número, análise ou conclusão. O enunciado **não traz data nenhuma**; a de 17/11/2026 foi informada pelo grupo, e a procedência está declarada aqui |
| ~~D-7~~ | ~~Catálogo de medidas e matriz de aderência~~ | — | ✅ **FECHADA em 01/10/2026:** catálogo em `03_dashboard/medidas_dax.md` (**22 medidas**, M01–M22) e matriz em `method/definitions/matriz_aderencia_C1_C9.md` (9 critérios) |
| ~~D-8~~ | ~~Cobertura das perguntas de Customer Insights~~ | — | ✅ **FECHADA em 01/10/2026:** tabela de amarração no relatório (§7.1) e em `escopo_perguntas.md` §6 |

## Situação em 12/10/2026

**Oito de oito fechadas.** O arquivo chegou a zero, que é o estado para o qual ele existe.

| Fechadas em | Decisões |
|---|---|
| 24/09/2026 | D-1 · D-2 · D-4 |
| 01/10/2026 | D-3 · D-5 · D-7 · D-8 |
| 12/10/2026 | D-6 |

**A última a fechar foi a única externa, e o modo como fechou vale registrar.** As sete internas fecharam porque bastava decidir. D-6 dependia de resposta da instituição — e fechou quando se perguntou o que essa resposta mudaria no material. A resposta era nada: a data é metadado de entrega, e nenhum número, análise ou conclusão depende dela. Uma pendência externa que não condiciona o conteúdo não precisa ser esperada. Ver §8.6 do relatório.

## Regra
Nenhuma destas é decidida por iniciativa de quem revisa ou de quem constrói. São de Ricardo (Lei de Falkland). Apontar o risco é obrigação; decidir a mudança, não.

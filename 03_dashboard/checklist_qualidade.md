# Checklist de qualidade — F8

> **Gerado por `gera_checklist.py`. Não editar à mão.** Os números são medidos na gold e nas tabelas de resultado a cada execução, e conferidos contra a seção 6 do guia de montagem.

Marcar contra as **imagens exportadas na F8** (`03_dashboard/screenshots/`), uma página por vez. `—` = a regra não se aplica à página. **Qualquer célula sem marca impede o Portão C.** A versão para imprimir é `checklist_qualidade.pdf`.

| Página | T1 Wilson + n | T2 piso 30 | T3 rodapé | T4 sem causa | T5 ρ com p | T6 volume ≠ venda | T7 consumidor | T8 corpus | T9 paleta |
|---|---|---|---|---|---|---|---|---|---|
| **1 · Visão Executiva** | — | — | ☐ rodapé M21 · L5 sem símbolo | ☐ títulos sem causa | — | ☐ cartão 36.384 = volume | ☐ nenhum user_* | — | ☐ âmbar só no ponto de 80% |
| **2a · Categorias** | ☐ nota corrigida (T2) | ☐ só 4 categorias · rodapé 5 cat./7 prod./0,5% | ☐ rodapé M21 · L5 sem símbolo | ☐ títulos sem causa | — | ☐ participação no volume | ☐ nenhum user_* | — | ☐ sem âmbar · fones e climatização em laranja |
| **2b · Quadrantes** | ☐ 19 e 61 com Wilson e n | ☐ listas nominais = exceção declarada | ☐ rodapé M21 · L5 sem símbolo | ☐ títulos sem causa | — | ☐ vedado "baixa visibilidade" | ☐ tabelas sem consumidor | — | ☐ âmbar só no quadrante Q5 |
| **2c · Rankings** | ☐ top 10 Wilson ao lado do bruto | ☐ arquétipos n ≥ 268 | ☐ rodapé M21 · L5 sem símbolo | ☐ "convenção descritiva, não descoberta" | — | ☐ nenhuma venda | ☐ nenhum user_* | — | ☐ B × D em 2 séries |
| **3 · Preços** | ☐ QA1 por nota corrigida, n no rótulo | ☐ 5 faixas, todas n ≥ 30 | ☐ rodapé M21 · L5 sem símbolo | ☐ "associação, não causa" | ☐ ρ com p e n nos 4 pares | ☐ nenhuma venda | ☐ nenhum user_* | — | ☐ âmbar só em 81–100% · escala divergente |
| **4 · Customer Insights** | — | ☐ QA5: denominador 19 visível | ☐ rodapé M21 · L5 sem símbolo | ☐ títulos sem causa | ☐ Δ TF-IDF como magnitude | ☐ nenhuma venda | ☐ nenhum trecho de avaliação, nenhum user_* | ☐ caixa: até 8 por produto · bloco · dedup review_id | ☐ faixa média em cinza |
| **5 · Recomendações** | — | — | ☐ rodapé M21 · L5 sem símbolo | ☐ "triagem, não veredito" | ☐ AUC com o desvio ao lado | ☐ nada em receita | ☐ nenhum user_* | — | ☐ 1 âmbar |
| **Oculta · detalhamento** | ☐ Wilson e n na ficha | — | ☐ rodapé M21 · L5 sem símbolo | — | — | — | ☐ nenhum dado de consumidor | — | — |
| **Oculta · dica** | ☐ n e nota corrigida | — | — | — | — | — | — | — | — |
| **Oculta · Conferência** | — | — | ☐ rodapé da referência | — | — | — | — | — | ☐ 0 em favoravel, ≠ 0 em atencao |

## Os números que cada tela tem de mostrar

| Página | Números |
|---|---|
| **1 · Visão Executiva** | ☐ 4,10 · ☐ 49% · ☐ 1.795 · ☐ 4.740 · ☐ 36.384 · ☐ histograma 339 / 418 · ☐ 306 · ☐ 22,7% · ☐ 39 dos 306 · ☐ Âncora 41 · Risco 19 · Subexplorado 187 · Cauda frágil 227 · Intermediário 874 |
| **2a · Categorias** | ☐ 59,7% · 26,6% · 12,6% · 0,6% · ☐ Electronics sem variantes 53,1% · ☐ 8 subcategorias · 88,3% |
| **2b · Quadrantes** | ☐ 19 (Q5) · ☐ 187 funil · 61 acionáveis · ☐ cortes 36.384 · 4.740 · 4,0 · 4,3 |
| **2c · Rankings** | ☐ A 268 · B 335 · C 298 · D 447 · ☐ B × D: desconto 58% × 61% · ☐ avaliações 468 × 13.120 · ☐ nota 3,9 × 4,2 |
| **3 · Preços** | ☐ 899 · ☐ 1.795 · ☐ 49% · ☐ 81–100%: 3,906 (n = 51) · ☐ ρ Q3 = −0,150 (p = 3,1e-08) · ☐ ρ QA4 = +0,032 (p = 0,236) |
| **4 · Customer Insights** | ☐ 1.348 blocos · 10.588 referências · 9.255 reviews · ☐ 339 / 591 / 418 · ☐ até 8 por produto (média 7,85) · ☐ 19 blocos de Q5 |
| **5 · Recomendações** | ☐ 19 · 335 · 61 · ρ = −0,150 (p = 3,1e-08) · 97,2% · ☐ AUC 0,56 · 0,58 · 0,66 · 0,70 ± 0,01 · ☐ 8 limitações · 21 de 21 medidas (33 linhas conferidas) · ☐ caixa 'como estes números foram conferidos' (G-36) |
| **Oculta · Conferência** | ☐ Conf · Divergentes = 0 · ☐ 33 de 33 linhas |

## Em todas as páginas

- ☐ um único elemento em âmbar por página (T9)
- ☐ nenhuma pizza ou rosca
- ☐ no máximo 5 séries por visual
- ☐ nenhum visual de Python, de R ou de loja
- ☐ valores em rupia indiana, sem símbolo (L5)
- ☐ L1 dita na página 4; L4 e as 8 limitações na página 5
- ☐ `verifica_pbix.py` com saída 0 sobre o .pbit exportado do .pbix final
- ☐ página Conferência: Conf · Divergentes = 0

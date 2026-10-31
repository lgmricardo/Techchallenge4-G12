# 🎨 PADRÃO VISUAL — TABELA ÚNICA DE TOKENS (v06)
**Fonte única de cor do projeto.** Nenhuma cor fora desta tabela entra em **nenhum artefato**: `.pbix`, notebook, gráfico em Python, tabela, relatório, deck, vídeo, diagrama ou qualquer arquivo gerado (**regra T9**).
Aplicação sempre por ferramenta — `tema_fase4_ambar_ardosia.json` no Power BI, `src/paleta.py` em Python. Nunca pelo seletor de cor.
**24/09/2026 · substitui a v05.** Origem: prancha de padrão visual aprovada por Ricardo, com os hex extraídos por amostragem de pixel — não por estimativa.
Regra 60-30-10 · contrastes medidos por WCAG 2.1 (luminância relativa), não estimados.

> **O que mudou da v05 para a v06**
> - `serie_ameixa` `#6E5C7B` **sai** — a escala categórica passa a ter 6 séries, e ameixa não é uma delas.
> - `atencao_texto` `#B05607` **sai** — ver a Regra 1, reescrita.
> - `#FFFBF0` **sai** — a zebra de tabela passa a usar `canvas`.
> - As escalas **sequencial** e **divergente** deixam de ser informais e entram como tokens numerados.

---

## Base — 60%
| Token | Hex | Papel | Contraste sobre creme |
|---|---|---|---|
| `canvas` | `#FFF4D6` | fundo da página · zebra de tabela | — |
| `card` | `#FFFFFF` | fundo de visuais e KPIs | 1,10:1 |
| `divisor` | `#F0EADA` | bordas, faixas, linhas de tabela | 1,10:1 |

## Estrutura — 30%
| Token | Hex | Papel | Sobre creme | Sobre card | Texto |
|---|---|---|---|---|---|
| `tinta` | `#2A2F35` | texto primário, títulos, valores | **12,31:1** | 13,49:1 | ✅ AA |
| `secundario` | `#5B6770` | rótulos, eixos, legendas | **5,30:1** | 5,80:1 | ✅ AA |
| `grade` | `#9AA5B1` | grade, estado inativo | 2,28:1 | 2,50:1 | ❌ nunca |

## Chamadas — 10%
| Token | Hex | Papel | Sobre creme | Sobre card | Texto |
|---|---|---|---|---|---|
| `destaque` | `#F2C14E` | série em foco, marcador de insight | 1,53:1 | 1,68:1 | ❌ nunca |
| `favoravel` | `#1F6F6B` | leitura positiva | **5,41:1** | 5,92:1 | ✅ AA |
| `atencao` | `#DC6C09` | leitura negativa, ponto de atenção | 3,09:1 | 3,39:1 | ⚠️ só ≥18pt ou elemento gráfico |

## Escala categórica — máximo 6 séries
Ordem de atribuição no tema (`dataColors`). **A ordem não é estética: ela é o que decide se duas séries são distinguíveis.**

| # | Token | Hex | Sob deuteranopia | Sobre creme |
|---|---|---|---|---|
| 1 | `serie_ambar` | `#F2C14E` | `#D0D049` | 1,53:1 |
| 2 | `serie_azul` | `#3F5A7A` | `#53537A` | 6,49:1 · também **cor de link** |
| 3 | `serie_ardosia_clara` | `#9AA5B1` | `#A1A1B1` | 2,28:1 |
| 4 | `serie_laranja` | `#DC6C09` | `#989800` | 3,09:1 |
| 5 | `serie_teal` | `#1F6F6B` | `#5F5F6C` | 5,41:1 |
| 6 | `serie_ardosia` | `#5B6770` | `#636370` | 5,30:1 |

### Por que esta ordem, e não a da prancha
A prancha trazia `âmbar · teal · ardósia · laranja · azul · ardósia clara`. Medido em ΔE (CIE76) sobre a simulação de deuteranopia de Viénot, o par **teal × ardósia fica em ΔE 1,6** — abaixo do limiar de percepção humana, que é ≈ 2,3. Na ordem da prancha eles caem nas posições **2 e 3**, ou seja, **todo gráfico de 3 ou mais séries** nascia com duas cores indistinguíveis para um leitor com deuteranopia.

A reordenação empurra esse par para as posições 5 e 6. Pior separação do conjunto, por número de séries no visual:

| Séries no visual | Ordem da prancha | **Ordem v06** |
|---|---|---|
| 2 | ΔE 82,9 ✅ | **ΔE 94,2** ✅ |
| 3 | ΔE 1,6 ❌ | **ΔE 32,8** ✅ |
| 4 | ΔE 1,6 ❌ | **ΔE 20,5** ✅ |
| 5 | ΔE 1,6 ❌ | **ΔE 16,7** ✅ |
| 6 | ΔE 1,6 ❌ | ΔE 1,6 ❌ |

Nenhuma cor foi trocada — só a ordem de atribuição.

### ⚠️ Limite estrutural: 6 séries não é seguro
Teal e ardósia estão ambos na paleta, então **nenhuma ordem** resolve o caso de 6 séries: em algum momento os dois aparecem juntos. Isso não é defeito da ordem, é da composição da paleta.

**Regra:** visual com **até 5 séries** usa a escala normalmente. Visual com **6 séries** exige **rótulo direto** em teal e ardósia, ou agrupamento de categorias até caber em 5. Os outros 14 pares da paleta ficam todos em ΔE ≥ 16,7 sob deuteranopia — o problema é exclusivamente esse par.

## Escala sequencial teal — intensidade
Uso: uma variável contínua, sem ponto neutro (volume de avaliações, concentração).

| Passo | Hex | Sobre creme | Texto sobre o passo |
|---|---|---|---|
| 1 (mín.) | `#EAF3F2` | 1,03:1 | usar `tinta` |
| 2 | `#C6E0DD` | 1,27:1 | usar `tinta` |
| 3 | `#96C6C2` | 1,72:1 | usar `tinta` |
| 4 | `#5FA5A0` | 2,60:1 | usar `tinta` |
| 5 | `#1F6F6B` | 5,41:1 | usar `card` |
| 6 (máx.) | `#12504D` | 8,40:1 | usar `card` |

## Escala divergente — desvio em torno da mediana
Uso: desvio com sinal, com zero significativo (acima/abaixo da mediana da categoria).

| Passo | Hex | Leitura |
|---|---|---|
| 1 | `#DC6C09` | desvio negativo forte |
| 2 | `#EDA25C` | negativo moderado |
| 3 | `#F7D4AE` | negativo leve |
| 4 | `#FFF4D6` | **centro — na mediana** |
| 5 | `#9EC5C1` | positivo leve |
| 6 | `#6FA8A3` | positivo moderado |
| 7 | `#1F6F6B` | positivo forte |

> **Nenhum passo intermediário das duas escalas serve para texto.** Rótulo sobre preenchimento colorido segue a coluna da tabela acima.

---

## Regras sem exceção

1. **Laranja nunca em texto corrido.** `atencao` `#DC6C09` mede 3,09:1 sobre creme — abaixo do mínimo AA de 4,5:1. Ele vale para **elemento gráfico** e para **texto a partir de 18pt**. Rótulo e texto corrido de leitura negativa usam `tinta`; quando for indispensável dar cor ao caractere, use `favoravel`/`atencao` apenas no ícone ou no marcador ao lado, nunca na palavra.
   *(A v05 resolvia isso com um token `atencao_texto` `#B05607`. Ele não existe na prancha aprovada e foi removido — a regra acima cobre o mesmo caso sem acrescentar cor.)*
2. **Âmbar e laranja nunca como séries adjacentes** no mesmo visual — separação de 2,02:1, e ambos migram para o mesmo amarelo sob deuteranopia. Quando coexistirem, rótulo direto é obrigatório.
3. **O tema é importado antes do primeiro visual.** Cor aplicada à mão se sobrepõe ao tema e o padrão se perde.
4. **Regra dos 10%:** ao fechar cada página, conferir que há **um único** elemento em âmbar.
5. **Nunca escolher cor pelo seletor manual.** Toda cor sai desta tabela, pelo tema.
6. **Escala certa para o dado certo:** categórica para grupos sem ordem · sequencial para intensidade sem ponto neutro · divergente **só** quando o zero tem significado.

---

## Arquivo de tema

`tema_fase4_ambar_ardosia.json` — `"name": "Fase4_Ambar_Ardosia_v06"`. Conferido: **nenhum hex fora desta tabela**.

**Limitação do formato, não do padrão.** O JSON de tema do Power BI comporta apenas `minimum`/`center`/`maximum` para escala de cor — não há campo para uma rampa de 6 ou 7 passos. O tema carrega a **sequencial** nesse trio (`#EAF3F2` → `#96C6C2` → `#12504D`), que o Power BI interpola. Para a **divergente**, e para qualquer uso em faixas discretas, aplicar os hex desta página na formatação condicional do visual. Não é escolha manual de cor: os valores saem daqui.

---

*Contrastes recalculados em 24/09/2026 pela fórmula WCAG 2.1 (linearização sRGB, limiar 0,04045, coeficientes 0,2126/0,7152/0,0722). Hex extraídos da prancha por amostragem de pixel.*

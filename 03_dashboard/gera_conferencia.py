# -*- coding: utf-8 -*-
"""
Página de conferência do .pbix — 03_dashboard/conferencia_referencia.csv e
03_dashboard/conferencia_dax.md, gerados de valores_referencia.csv e medidas_dax.md.

POR QUE EXISTE
--------------
A reconciliação DAX × Python era conferência humana: abrir cada cartão e
comparar com a tabela de referência. Com uma pessoa só montando e revisando,
conferência humana é a que falha primeiro — e falha calada.

Esta página troca o olho por uma conta. O .pbix importa os valores de
referência como tabela, e uma medida recalcula cada um deles pelo DAX do
catálogo. A diferença aparece na tela, linha a linha, e um cartão conta as
divergências. **Zero é o único resultado aceitável**, e ele é refeito a cada
alteração do modelo até o congelamento — não uma vez só, na F4. A página é
montada LOGO DEPOIS das 22 medidas: o DAX não aceita referência a medida que
ainda não existe, e antes disso as medidas Conf ficariam em erro.

O QUE ELA CONFERE, ALÉM DO TOTAL
--------------------------------
Os 25 valores de referência são todos da base inteira — e no total, esquecer o
ALL de M14, M17, M18 ou M19 dá o MESMO número. A falta só aparece sob filtro.
Por isso há linhas avaliadas sob o filtro de uma categoria: com o ALL certo, o
corte M18 continua 36.384 em Electronics; sem ele, iria a 67.330,9. E uma linha
conta as linhas da Reviews, porque a medida M20 (DISTINCTCOUNT) não muda se a
deduplicação falhar.

POR QUE É GERADO
----------------
A medida de conferência cita o nome DAX EXATO de cada medida. Escrito à mão, o
primeiro renome no catálogo deixaria a conferência apontando para uma medida
que não existe — e o Power BI recusaria a medida de conferência. Gerado, o
renome quebra aqui, antes de chegar ao Power BI.

O que o script garante (e falha se não valer):
- as 25 linhas de valores_referencia.csv entram, e toda medida do catálogo com
  referência está nelas — exceto M21, que é texto (rodapé);
- as categorias existem na BaseAnalitica;
- as linhas sob filtro batem com valores_referencia_por_categoria.csv onde ele
  as tem, e os cortes M18/M19 sob filtro são iguais aos do total;
- percentuais vão na escala que o DAX devolve: DIVIDE gera fração (0,2515),
  a referência está em pontos percentuais (25,15).

Uso: python 03_dashboard/gera_conferencia.py
"""

import os
import sys

import pandas as pd

PASTA = os.path.dirname(os.path.abspath(__file__))
RAIZ = os.path.dirname(PASTA)
sys.path.insert(0, PASTA)
from modelo_esperado import nomes_dax  # noqa: E402

REFERENCIA = os.path.join(PASTA, "valores_referencia.csv")
POR_CATEGORIA = os.path.join(PASTA, "valores_referencia_por_categoria.csv")
GOLD = os.path.join(RAIZ, "00_data", "gold", "base_analitica.csv")
REVIEWS = os.path.join(RAIZ, "00_data", "gold", "reviews.csv")
SAIDA_CSV = os.path.join(PASTA, "conferencia_referencia.csv")
SAIDA_MD = os.path.join(PASTA, "conferencia_dax.md")

SEM_REFERENCIA = {"M21"}   # rodapé: texto composto de M01 e M18, conferidos
CONTEXTO = "Electronics"   # a maior categoria: o filtro que mais muda um número sem ALL


def tolerancia(medida, valor):
    """Tolerância POR LINHA, na escala do DAX.

    A única diferença legítima entre DAX e Python é de ponto flutuante (medido:
    ≤ 4,4e-16). Contagens e somas inteiras batem exatamente; frações e medianas
    decimais, a 1e-12 — o bastante para pegar um único produto trocado de
    categoria; a nota corrigida (M07), a 1e-8, porque vem do Power Query
    conferida a 1e-9 e a mediana tira a média de dois valores.
    """
    if medida == "M07":
        return 1e-8
    return 0.0 if float(valor).is_integer() else 1e-12


def br(x, casas=0):
    s = f"{x:,.{casas}f}"
    return s.replace(",", "§").replace(".", ",").replace("§", ".").replace("-", "−")


ref = pd.read_csv(REFERENCIA)
dax = nomes_dax()
g = pd.read_csv(GOLD)
rv = pd.read_csv(REVIEWS)
porcat = pd.read_csv(POR_CATEGORIA).set_index("categoria_n1")
N = len(g)

assert len(ref) == 25, f"valores_referencia.csv deveria ter 25 linhas, tem {len(ref)}"
com_ref = set(ref.medida) - {"M15s"}
assert com_ref | SEM_REFERENCIA == set(dax), (
    f"catálogo × referência divergem: só no catálogo {sorted(set(dax) - com_ref - SEM_REFERENCIA)}, "
    f"só na referência {sorted(com_ref - set(dax))}")
assert len(com_ref) == 21, f"deveriam ser 21 medidas com referência, são {len(com_ref)}"
assert CONTEXTO in set(g.categoria_n1)

linhas = []


def linha(chave, medida, nome, categoria, valor, publicado, percentual):
    linhas.append({
        "chave": chave, "medida": medida, "nome": nome,
        "medida_dax": dax.get(medida, ""), "categoria_n1": categoria,
        "valor_esperado": valor, "publicado": publicado,
        "escala": "fração (o DAX devolve DIVIDE)" if percentual else "unidade da medida",
        "tolerancia": tolerancia(medida, valor),
    })


# ---------------------------------------- os 25 valores de referência (total)
for _, r in ref.iterrows():
    categoria = ""
    if r.medida == "M15":
        categoria = r.nome.split(" · ")[-1]
        assert categoria in set(g.categoria_n1), f"categoria de M15 inexistente na base: {categoria}"
    percentual = str(r.unidade).strip() == "%"
    linha(f"M15 · {categoria}" if categoria else r.medida, r.medida, r.nome, categoria,
          r.valor / 100 if percentual else r.valor, r.publicado, percentual)

# ------------------------------- sob filtro de categoria: o ALL que o total esconde
e = g[g.categoria_n1 == CONTEXTO]
sub = e.groupby("categoria_n2").size()
total = {r.medida: r.valor for r in ref.itertuples()}
ctx = {
    "M08": (e.avaliacoes.median(), False, "volume mediano DENTRO da categoria — prova que o filtro chega"),
    "M09": ((e.satisfacao == "baixa").mean(), True, "denominador local: a fatia da categoria"),
    "M14": (e.pareto_80.sum() / N, True, "denominador com ALL: fatia da base inteira"),
    "M17": (sub[sub >= 30].sum() / N, True, "denominador com ALL: cobertura sobre a base inteira"),
    "M18": (float(g.avaliacoes.quantile(0.90)), False, "com ALL o corte NÃO muda com o filtro"),
    "M19": (float(g.avaliacoes.quantile(0.50)), False, "com ALL o corte NÃO muda com o filtro"),
}
# amarrações com o que já está publicado
assert ctx["M08"][0] == porcat.loc[CONTEXTO, "volume_mediano"], "M08 sob filtro × valores_referencia_por_categoria"
assert abs(100 * ctx["M09"][0] - porcat.loc[CONTEXTO, "satisfacao_baixa_pct"]) < 5e-4, "M09 sob filtro × por categoria"
assert ctx["M18"][0] == total["M18"] and ctx["M19"][0] == total["M19"], "cortes sob filtro ≠ cortes do total"
for medida, (valor, percentual, porque) in ctx.items():
    nome = ref.loc[ref.medida == medida, "nome"].iloc[0]
    publicado = (br(100 * valor, 1) + "%" if percentual else br(valor, 1 if valor % 1 else 0)) + f" — {porque}"
    linha(f"{medida} · {CONTEXTO}", medida, f"{nome} · sob filtro {CONTEXTO}", CONTEXTO, valor, publicado, percentual)

# ---------------------------------- a deduplicação da Reviews (T8), que M20 não vê
rv_e = rv.merge(g[["product_id", "categoria_n1"]], on="product_id", suffixes=("", "_base"))
assert len(rv) == total["M20"] == rv.review_id.nunique(), "reviews.csv precisa ter 9.255 linhas distintas"
linha("M20n", "M20n", "Linhas da Reviews — deduplicação por review_id (T8)", "", float(len(rv)),
      f"{br(len(rv))} — sem deduplicar seriam 10.588", False)
n_e = int((rv_e.categoria_n1_base == CONTEXTO).sum())
linha(f"M20n · {CONTEXTO}", "M20n", f"Linhas da Reviews · sob filtro {CONTEXTO}", CONTEXTO, float(n_e),
      f"{br(n_e)} — a regra de atribuição, nos 8 reviews compartilhados entre categorias", False)

conf = pd.DataFrame(linhas)
assert conf.chave.is_unique, "chave repetida na conferência"
N_LINHAS = len(conf)
conf.to_csv(SAIDA_CSV, index=False, encoding="utf-8", float_format="%.15g")

# ------------------------------------------------------------- o DAX gerado
ramos = []
for medida, nome in sorted(dax.items(), key=lambda kv: int(kv[0][1:])):
    if medida in SEM_REFERENCIA:
        continue
    ramos.append(f'            "{medida}", [{nome}],')
    if medida == "M15":
        ramos.append('            "M15s", DIVIDE (\n'
                     '                SUMX (\n'
                     '                    FILTER ( VALUES ( BaseAnalitica[categoria_n1] ), [Produtos Ativos] < 30 ),\n'
                     '                    [Volume Total de Avaliações]\n'
                     '                ),\n'
                     '                [Volume Total de Avaliações]\n'
                     '            ),')
    if medida == "M20":
        ramos.append('            "M20n", COUNTROWS ( Reviews ),')
ramos[-1] = ramos[-1].rstrip(",")
switch = "\n".join(ramos)

doc = f"""# Página de conferência — DAX × Python

> **Gerado por `gera_conferencia.py` a partir de `valores_referencia.csv`, `valores_referencia_por_categoria.csv` e `medidas_dax.md`. Não editar à mão** — alterou o catálogo ou a referência, rode o script de novo.

Página **oculta** do `.pbix`. Recalcula pelo DAX do catálogo **{N_LINHAS} valores** e mostra a diferença para o Python, linha a linha. **O cartão de divergências precisa mostrar zero** — antes de montar a primeira página (F4), a cada alteração do modelo, e no congelamento (F9).

**Montar logo depois das 22 medidas do catálogo, não antes.** As medidas `Conf ·` citam todas elas, e o DAX não aceita referência a medida que ainda não existe: enquanto faltar uma, a página fica em erro.

| Linhas | O que conferem |
|---|---|
| **25** de referência | as 21 medidas sobre a base inteira — M15 desdobrada nas 4 categorias elegíveis e na parcela suprimida por T2 |
| **6** sob filtro de **{CONTEXTO}** | M08, M09, M14, M17, M18 e M19 — o `ALL` que o total esconde: sem ele, M18 iria de 36.384 a 67.330,9 nesta categoria |
| **2** da `Reviews` | as linhas da tabela, no total e sob filtro — a deduplicação por `review_id` (T8), que o `DISTINCTCOUNT` de M20 não vê |

## 1 · Importar a tabela `Conferencia`

`03_dashboard/conferencia_referencia.csv`, em **UTF-8** e **cultura en-US**, como as tabelas de resultado, e **renomear a consulta para `Conferencia`** — o conector dá o nome do arquivo. Carrega no modelo, **sem relacionamento**. Tipos: `valor_esperado` e `tolerancia` **número decimal**; o resto texto.

| Coluna | O que é |
|---|---|
| `chave` | identificador único da linha — `M01` … `M22`, `M15 · <categoria>`, `M15s`, `<medida> · {CONTEXTO}`, `M20n` |
| `medida` · `nome` | código e nome do catálogo |
| `medida_dax` | nome exato da medida no `.pbix`; vazio nas linhas cuja expressão está na própria conferência (`M15s`, `M20n`) |
| `categoria_n1` | quando preenchida, a categoria é aplicada **como filtro** antes do cálculo — as linhas de M15 e as de contexto |
| `valor_esperado` | o valor do Python **na escala que o DAX devolve** — percentuais como fração |
| `publicado` | como o número aparece no relatório e no vídeo, ou o que a linha prova |
| `escala` | fração ou unidade da medida — para quem lê a tabela |
| `tolerancia` | por linha: **0** em contagens e somas, **1e-12** em frações e medianas decimais, **1e-8** na nota corrigida |

## 2 · As medidas de conferência

Em `_Medidas`, numa pasta de exibição **Conferência**. Não entram na contagem das 22 do catálogo.

```dax
Conf · Valor DAX =
VAR _Medida = SELECTEDVALUE ( Conferencia[medida] )
VAR _Categoria = SELECTEDVALUE ( Conferencia[categoria_n1] )
RETURN
    CALCULATE (
        SWITCH (
            _Medida,
{switch}
        ),
        REMOVEFILTERS ( BaseAnalitica ),
        REMOVEFILTERS ( Reviews ),
        FILTER (
            ALL ( BaseAnalitica[categoria_n1] ),
            LEN ( _Categoria ) = 0 || BaseAnalitica[categoria_n1] = _Categoria
        )
    )
```

```dax
Conf · Esperado =
SELECTEDVALUE ( Conferencia[valor_esperado] )
```

```dax
Conf · Diferença =
[Conf · Valor DAX] - [Conf · Esperado]
```

```dax
Conf · Situação =
IF (
    HASONEVALUE ( Conferencia[chave] ),
    SWITCH (
        TRUE (),
        ISBLANK ( [Conf · Valor DAX] ), "SEM VALOR",
        ABS ( [Conf · Diferença] ) <= SELECTEDVALUE ( Conferencia[tolerancia] ), "confere",
        "DIVERGE"
    )
)
```

```dax
Conf · Divergentes =
VAR _Linhas = {N_LINHAS}
RETURN
    COUNTROWS (
        FILTER (
            ALL ( Conferencia ),
            ISBLANK ( [Conf · Valor DAX] )
                || ABS ( [Conf · Diferença] ) > Conferencia[tolerancia]
        )
    )
        + ABS ( _Linhas - COUNTROWS ( ALL ( Conferencia ) ) )
        + 0
```

```dax
Conf · Conferidas =
{N_LINHAS} - [Conf · Divergentes]
```

**Por que `REMOVEFILTERS` e o filtro de categoria por linha.** A conferência é sempre contra um contexto conhecido: a base inteira, ou a base inteira filtrada pela categoria da linha. Um filtro de relatório criado depois não a altera. `LEN ( _Categoria ) = 0` cobre a célula vazia do CSV, que pode chegar como texto vazio e não como branco.

**Por que `ALL ( Conferencia )` e o número de linhas gravado.** Sem o `ALL`, clicar numa linha da tabela — a interação padrão filtra o cartão —, uma segmentação ou um filtro de página sobre `Conferencia` faria o cartão mostrar 0 com divergência presente. E se a importação vier truncada ou duplicada, a diferença para as {N_LINHAS} linhas esperadas conta como divergência.

**Por que `SEM VALOR` é divergência.** Uma medida que devolve vazio no contexto da linha — filtro errado, coluna de tipo errado — não tem diferença zero: tem valor faltando. (Renomear uma medida no Desktop atualiza as referências; apagá-la deixa as medidas `Conf ·` em erro, e a página não renderiza — reprovação igualmente visível.)

**`M15s` e `M20n` não têm medida no catálogo.** `M15s` é a parcela do volume das 5 categorias com n < 30, que o rodapé de M15 declara em texto (*"0,5% do volume suprimido"*). `M20n` conta as linhas da `Reviews`: se a deduplicação falhar, ela vai a 10.588 e o `DISTINCTCOUNT` de M20 continua 9.255.

**O que esta página não vê, e quem vê.** Um denominador escrito com `ALLSELECTED` no lugar de `ALL` dá o mesmo número aqui — não há segmentação na página. Quem pega é `verifica_pbix.py`, que compara a expressão de cada medida do arquivo com a do catálogo.

## 3 · A página

| Visual | Campos | Regra |
|---|---|---|
| **Cartão** | `Conf · Divergentes` | título *"Medidas divergentes — precisa ser 0"*; formatação condicional: 0 em `favoravel`, qualquer outro valor em `atencao` |
| Cartão | `Conf · Conferidas` | *"de {N_LINHAS} linhas conferidas"* |
| **Tabela** | `Conferencia[chave]` · `Conferencia[nome]` · `Conferencia[publicado]` · `Conf · Esperado` · `Conf · Valor DAX` · `Conf · Diferença` · `Conf · Situação` | ordenada por `chave`; **totais desligados**; `Conf · Situação` com formatação condicional; esperado e DAX com 6 casas |

*Formatar > Editar interações*: tabela → cartões = **Nenhum**. O `ALL` já protege o cartão; a interação desligada evita que alguém leia o cartão de conferidas filtrado.

Rodapé: *"Referência: `03_dashboard/valores_referencia.csv` e `valores_referencia_por_categoria.csv`, calculadas sobre a base analítica (n = 1.348) e as reviews individuais (n = 9.255) · tolerância por linha."*

**Ocultar a página** (botão direito na aba > *Ocultar página*). Ela fica no arquivo entregue: é a evidência, para quem abrir o `.pbix`, de que os números do dashboard são os do Python.

## 4 · Os {N_LINHAS} valores conferidos

| Chave | Medida no `.pbix` | Esperado (escala DAX) | Tolerância | Publicado / o que prova |
|---|---|---|---|---|
""" + "\n".join(
    f"| `{c.chave}` | {('`' + c.medida_dax + '`') if c.medida_dax else '*expressão na conferência*'} | "
    f"{c.valor_esperado:.10g} | {c.tolerancia:g} | {c.publicado} |"
    for c in conf.itertuples()) + "\n"

open(SAIDA_MD, "w", encoding="utf-8").write(doc)
print(f"  {SAIDA_CSV}")
print(f"  {SAIDA_MD}")
print(f"  {N_LINHAS} linhas · 25 de referência · {len(ctx)} sob filtro {CONTEXTO} · 2 da Reviews · "
      f"{(conf.escala.str.startswith('fração')).sum()} percentuais como fração")

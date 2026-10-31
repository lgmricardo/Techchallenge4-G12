# Página de conferência — DAX × Python

> **Gerado por `gera_conferencia.py` a partir de `valores_referencia.csv`, `valores_referencia_por_categoria.csv` e `medidas_dax.md`. Não editar à mão** — alterou o catálogo ou a referência, rode o script de novo.

Página **oculta** do `.pbix`. Recalcula pelo DAX do catálogo **33 valores** e mostra a diferença para o Python, linha a linha. **O cartão de divergências precisa mostrar zero** — antes de montar a primeira página (F4), a cada alteração do modelo, e no congelamento (F9).

**Montar logo depois das 22 medidas do catálogo, não antes.** As medidas `Conf ·` citam todas elas, e o DAX não aceita referência a medida que ainda não existe: enquanto faltar uma, a página fica em erro.

| Linhas | O que conferem |
|---|---|
| **25** de referência | as 21 medidas sobre a base inteira — M15 desdobrada nas 4 categorias elegíveis e na parcela suprimida por T2 |
| **6** sob filtro de **Electronics** | M08, M09, M14, M17, M18 e M19 — o `ALL` que o total esconde: sem ele, M18 iria de 36.384 a 67.330,9 nesta categoria |
| **2** da `Reviews` | as linhas da tabela, no total e sob filtro — a deduplicação por `review_id` (T8), que o `DISTINCTCOUNT` de M20 não vê |

## 1 · Importar a tabela `Conferencia`

`03_dashboard/conferencia_referencia.csv`, em **UTF-8** e **cultura en-US**, como as tabelas de resultado, e **renomear a consulta para `Conferencia`** — o conector dá o nome do arquivo. Carrega no modelo, **sem relacionamento**. Tipos: `valor_esperado` e `tolerancia` **número decimal**; o resto texto.

| Coluna | O que é |
|---|---|
| `chave` | identificador único da linha — `M01` … `M22`, `M15 · <categoria>`, `M15s`, `<medida> · Electronics`, `M20n` |
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
            "M01", [Produtos Ativos],
            "M02", [Volume Total de Avaliações],
            "M03", [Preço Mediano],
            "M04", [Preço de Tabela Mediano],
            "M05", [Desconto Mediano],
            "M06", [Nota Mediana],
            "M07", [Nota Corrigida Mediana],
            "M08", [Volume Mediano de Avaliações],
            "M09", [% Satisfação Baixa],
            "M10", [% Satisfação Alta],
            "M11", [Produtos Q5],
            "M12", [Produtos Q6],
            "M13", [Concentração Pareto 80%],
            "M14", [% Concentração Pareto 80%],
            "M15", [Participação da Categoria no Volume],
            "M15s", DIVIDE (
                SUMX (
                    FILTER ( VALUES ( BaseAnalitica[categoria_n1] ), [Produtos Ativos] < 30 ),
                    [Volume Total de Avaliações]
                ),
                [Volume Total de Avaliações]
            ),
            "M16", [Subcategorias acima do Piso],
            "M17", [Cobertura de Subcategoria acima do Piso],
            "M18", [Corte de Engajamento Alto],
            "M19", [Corte de Engajamento Baixo],
            "M20", [Reviews Individuais],
            "M20n", COUNTROWS ( Reviews ),
            "M22", [Produtos Q6 Acionáveis]
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
VAR _Linhas = 33
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
33 - [Conf · Divergentes]
```

**Por que `REMOVEFILTERS` e o filtro de categoria por linha.** A conferência é sempre contra um contexto conhecido: a base inteira, ou a base inteira filtrada pela categoria da linha. Um filtro de relatório criado depois não a altera. `LEN ( _Categoria ) = 0` cobre a célula vazia do CSV, que pode chegar como texto vazio e não como branco.

**Por que `ALL ( Conferencia )` e o número de linhas gravado.** Sem o `ALL`, clicar numa linha da tabela — a interação padrão filtra o cartão —, uma segmentação ou um filtro de página sobre `Conferencia` faria o cartão mostrar 0 com divergência presente. E se a importação vier truncada ou duplicada, a diferença para as 33 linhas esperadas conta como divergência.

**Por que `SEM VALOR` é divergência.** Uma medida que devolve vazio no contexto da linha — filtro errado, coluna de tipo errado — não tem diferença zero: tem valor faltando. (Renomear uma medida no Desktop atualiza as referências; apagá-la deixa as medidas `Conf ·` em erro, e a página não renderiza — reprovação igualmente visível.)

**`M15s` e `M20n` não têm medida no catálogo.** `M15s` é a parcela do volume das 5 categorias com n < 30, que o rodapé de M15 declara em texto (*"0,5% do volume suprimido"*). `M20n` conta as linhas da `Reviews`: se a deduplicação falhar, ela vai a 10.588 e o `DISTINCTCOUNT` de M20 continua 9.255.

**O que esta página não vê, e quem vê.** Um denominador escrito com `ALLSELECTED` no lugar de `ALL` dá o mesmo número aqui — não há segmentação na página. Quem pega é `verifica_pbix.py`, que compara a expressão de cada medida do arquivo com a do catálogo.

## 3 · A página

| Visual | Campos | Regra |
|---|---|---|
| **Cartão** | `Conf · Divergentes` | título *"Medidas divergentes — precisa ser 0"*; formatação condicional: 0 em `favoravel`, qualquer outro valor em `atencao` |
| Cartão | `Conf · Conferidas` | *"de 33 linhas conferidas"* |
| **Tabela** | `Conferencia[chave]` · `Conferencia[nome]` · `Conferencia[publicado]` · `Conf · Esperado` · `Conf · Valor DAX` · `Conf · Diferença` · `Conf · Situação` | ordenada por `chave`; **totais desligados**; `Conf · Situação` com formatação condicional; esperado e DAX com 6 casas |

*Formatar > Editar interações*: tabela → cartões = **Nenhum**. O `ALL` já protege o cartão; a interação desligada evita que alguém leia o cartão de conferidas filtrado.

Rodapé: *"Referência: `03_dashboard/valores_referencia.csv` e `valores_referencia_por_categoria.csv`, calculadas sobre a base analítica (n = 1.348) e as reviews individuais (n = 9.255) · tolerância por linha."*

**Ocultar a página** (botão direito na aba > *Ocultar página*). Ela fica no arquivo entregue: é a evidência, para quem abrir o `.pbix`, de que os números do dashboard são os do Python.

## 4 · Os 33 valores conferidos

| Chave | Medida no `.pbix` | Esperado (escala DAX) | Tolerância | Publicado / o que prova |
|---|---|---|---|---|
| `M01` | `Produtos Ativos` | 1348 | 0 | 1.348 |
| `M02` | `Volume Total de Avaliações` | 23801471 | 0 | 23.801.471 |
| `M03` | `Preço Mediano` | 899 | 0 | 899 |
| `M04` | `Preço de Tabela Mediano` | 1795 | 0 | 1.795 |
| `M05` | `Desconto Mediano` | 49 | 0 | 49 |
| `M06` | `Nota Mediana` | 4.1 | 1e-12 | 4,10 |
| `M07` | `Nota Corrigida Mediana` | 4.065163708 | 1e-08 | 4,065 |
| `M08` | `Volume Mediano de Avaliações` | 4740 | 0 | 4.740 |
| `M09` | `% Satisfação Baixa` | 0.2514836795 | 1e-12 | 25,1% (339 produtos) |
| `M10` | `% Satisfação Alta` | 0.3100890208 | 1e-12 | 31,0% (418 produtos) |
| `M11` | `Produtos Q5` | 19 | 0 | 19 |
| `M12` | `Produtos Q6` | 187 | 0 | 187 |
| `M22` | `Produtos Q6 Acionáveis` | 61 | 0 | 61 |
| `M13` | `Concentração Pareto 80%` | 306 | 0 | 306 |
| `M14` | `% Concentração Pareto 80%` | 0.2270029674 | 1e-12 | 22,7% |
| `M15 · Electronics` | `Participação da Categoria no Volume` | 0.5969564234 | 1e-12 | 59,7% |
| `M15 · Computers&Accessories` | `Participação da Categoria no Volume` | 0.2661676667 | 1e-12 | 26,6% |
| `M15 · Home&Kitchen` | `Participação da Categoria no Volume` | 0.1256257229 | 1e-12 | 12,6% |
| `M15 · OfficeProducts` | `Participação da Categoria no Volume` | 0.006288476876 | 1e-12 | 0,6% |
| `M15s` | *expressão na conferência* | 0.00496171014 | 1e-12 | 0,5% em 7 produtos / 5 categorias |
| `M16` | `Subcategorias acima do Piso` | 8 | 0 | 8 |
| `M17` | `Cobertura de Subcategoria acima do Piso` | 0.8827893175 | 1e-12 | 88,3% (1.190 produtos) |
| `M18` | `Corte de Engajamento Alto` | 36384 | 0 | 36.384 |
| `M19` | `Corte de Engajamento Baixo` | 4740 | 0 | 4.740 |
| `M20` | `Reviews Individuais` | 9255 | 0 | 9.255 |
| `M08 · Electronics` | `Volume Mediano de Avaliações` | 9129.5 | 1e-12 | 9.129,5 — volume mediano DENTRO da categoria — prova que o filtro chega |
| `M09 · Electronics` | `% Satisfação Baixa` | 0.2612244898 | 1e-12 | 26,1% — denominador local: a fatia da categoria |
| `M14 · Electronics` | `% Concentração Pareto 80%` | 0.1305637982 | 1e-12 | 13,1% — denominador com ALL: fatia da base inteira |
| `M17 · Electronics` | `Cobertura de Subcategoria acima do Piso` | 0.3204747774 | 1e-12 | 32,0% — denominador com ALL: cobertura sobre a base inteira |
| `M18 · Electronics` | `Corte de Engajamento Alto` | 36384 | 0 | 36.384 — com ALL o corte NÃO muda com o filtro |
| `M19 · Electronics` | `Corte de Engajamento Baixo` | 4740 | 0 | 4.740 — com ALL o corte NÃO muda com o filtro |
| `M20n` | *expressão na conferência* | 9255 | 0 | 9.255 — sem deduplicar seriam 10.588 |
| `M20n · Electronics` | *expressão na conferência* | 2925 | 0 | 2.925 — a regra de atribuição, nos 8 reviews compartilhados entre categorias |

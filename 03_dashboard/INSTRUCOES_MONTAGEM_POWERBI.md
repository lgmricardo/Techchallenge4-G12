# 🖥️ MONTAGEM NO POWER BI

**Tech Challenge Fase 4 · Grupo 12 · `TechChallenge4_G12.pbix`**

> **Este arquivo é só o que se executa no Power BI Desktop.**
>
> **Menus em português (Brasil).** Em inglês: Transformar dados = *Transform data* · Habilitar carga = *Enable load* · Resumir por = *Summarize by* · Classificar por coluna = *Sort by column* · Editar interações = *Edit interactions* · Indicadores = *Bookmarks*.

---

## Antes de começar

**Duas tabelas precisam existir.** São geradas no Python, fora desta montagem:

| Arquivo | Usado em |
|---|---|
| `02_results/tables/tab22_arquetipo_por_produto.csv` | **passo 11** do Power Query — sem ela a `BaseAnalitica` não fecha |
| `02_results/tables/tab23_qa5_temas.csv` | página **4**, visual da QA5 |

Se não estiverem lá, **pare e peça**. O passo 11 trava sem a primeira.

**A regra que explica o resto deste documento:** o Power BI refaz a preparação dos dados porque o critério C2 avalia a qualidade das transformações — importar a base pronta não mostra transformação nenhuma. Mas ML, NLP e p-valores entram como tabelas prontas, porque o Power BI os reproduziria com método diferente, e método diferente dá número diferente do relatório.

---

## 1 · Ambiente

1. **Repositório** numa pasta local de caminho curto, **fora do OneDrive** — sugestão `C:\TC4\Techchallenge4-G12`. Sem espaços nem acentos.
2. **O `amazon.csv` não vem no git** (contém dados pessoais). Baixar de `kaggle.com/datasets/karkavelrajaj/amazon-sales-dataset` e colocar em `00_data/bronze/`.
3. **Conferir o SHA-256:**
   ```powershell
   Get-FileHash 00_data\bronze\amazon.csv -Algorithm SHA256
   ```
   Esperado `4ba126c4ba8edd35e62e94ce1c853073d832de380184ab4f5f97d1e314882c77`.
   **Se divergir, parar** — nenhum número do material vale sobre outra base.
4. **Power BI Desktop** instalado ou atualizado; anotar a versão em *Ajuda > Sobre*. E **Python** com `pip install -r requirements.txt` (F0.5 do plano) — os passos 3.9 e 8 rodam `verifica_pbix.py` e `gera_checklist.py`.
5. **Criar** `03_dashboard/TechChallenge4_G12.pbix`. Em *Arquivo > Opções e configurações > Opções > Arquivo atual*:
   - *Carregamento de dados* → **desmarcar "Data/hora automática"** (a base não tem datas) **e "Detectar automaticamente novos relacionamentos após o carregamento dos dados"** — `arquetipo` e `n` têm o mesmo nome em mais de uma tabela, e a relação criada sozinha seria proibida;
   - *Configurações regionais* → localidade de importação **Inglês (Estados Unidos)**.
6. **Importar o tema ANTES do primeiro visual:** *Exibição > Temas > Procurar temas* → `method/design_system/tema_fase4_ambar_ardosia.json`. Salvar.

> ⚠️ **Os passos 5 e 6 são os dois que não dá para corrigir depois sem refazer trabalho.** Localidade errada faz `4.2` virar 42 e as notas viram lixo **em silêncio**. Tema importado depois do primeiro visual não se aplica ao que já existe — cor escolhida à mão se sobrepõe e o padrão se perde sem aviso.

---

## 2 · Power Query: do arquivo de origem à base analítica

Cada etapa recebe **nome descritivo**. É isso que o avaliador vê quando abre o Power Query — e é a evidência do critério C2.

| Consulta | Origem | Carrega | Resultado |
|---|---|---|---|
| `pPasta` | parâmetro de texto com o caminho do projeto | — | — |
| `bronze_amazon` | `00_data/bronze/amazon.csv` | **Não** | 1.465 × 17 (16 + `ordem_origem`) |
| `silver_produtos` | `bronze_amazon` | **Não** | 1.351 produtos |
| `gold_intermediaria` | `silver_produtos` | **Não** | 1.348 produtos |
| `BaseAnalitica` | `gold_intermediaria` + `tab22` | **Sim** | 1.348 × 25 |
| `Reviews` | `gold_intermediaria` | **Sim** | 9.255 × 5 |
| `tab22` | `02_results/tables/` | **Não** — só para a mesclagem do passo 11 | 1.348 × 2 |
| `tab03` `tab05` `tab07` `tab14` `tab23` | `02_results/tables/` | **Sim** | as linhas de cada arquivo |
| `Conferencia` | `03_dashboard/conferencia_referencia.csv` | **Sim**, **sem relação** | 33 × 9 |
| `gold_python` | `00_data/gold/base_analitica.csv` — o gabarito | **Não** | 1.348 × 17 |
| `qa_compara_gold` | `BaseAnalitica` × `gold_python` | **Não** | **zero linhas** |

> Os nomes **`BaseAnalitica`** e **`Reviews`** são obrigatórios: é como `medidas_dax.md` os referencia. Outro nome exige reescrever as 22 medidas.

**Antes do passo 1 — o parâmetro `pPasta`.** *Página Inicial > Gerenciar parâmetros > Novo parâmetro*: `pPasta`, tipo **Texto**, valor = a pasta do projeto (ex.: `C:\TC4\Techchallenge4-G12`). **Toda fonte** começa com `pPasta & "\00_data\..."` ou `pPasta & "\02_results\..."` — é o que faz *Atualizar* funcionar se a pasta mudar. Parâmetro nasce sem carga.

**Passo 0 — firewall de privacidade.** Antes de criar a mesclagem com `tab22`: *Arquivo > Opções > Arquivo atual > Privacidade* → **"Ignorar os níveis de privacidade"**. Sem isso o Power Query recusa combinar duas fontes locais e devolve erro de *formula firewall*.
*A opção trata de combinação de fontes no motor de consulta — não tem relação com dado pessoal, que é controlado pela carga desativada no passo 16.*

### `bronze_amazon`
1. Ler o CSV em **UTF-8**, aspas no padrão CSV, promover cabeçalhos, **manter tudo como texto**.
2. Adicionar índice **`ordem_origem`** começando em 0, **antes de qualquer classificação** — é o desempate da deduplicação.

### `silver_produtos`
3. Remover `user_id`, `user_name`, `img_link`, `product_link`, `about_product`, `review_title`, `review_content`. **`review_id` fica** — ele monta a tabela de reviews. **Renomear** `discounted_price` → `preco_desc` · `actual_price` → `preco_tab` · `discount_percentage` → `desconto` · `rating` → `nota` · `rating_count` → `avaliacoes` — são os nomes que as medidas e a `qa_compara_gold` usam.
4. Converter `preco_desc` e `preco_tab` removendo o separador de milhar e o símbolo da moeda, escrito no código como `Character.FromNumber(8377)` para que o glifo não apareça no fonte. **No mesmo passo, trocar esse caractere pela palavra `rupia` dentro de `product_name`** — `Text.Replace([product_name], Character.FromNumber(8377), "rupia")` —, que é o que a camada silver faz (L5, exceção 2). Sem isso, `qa_compara_gold` devolve a linha de `B08CF4SCNP` e o passo 15 não fecha em zero.
5. Converter `desconto` (sem `%`), `avaliacoes` (sem vírgulas) e `nota` com **cultura en-US**; erro vira **nulo** — é o que trata a nota inválida da origem. `avaliacoes` como **Número inteiro**; `desconto` e `nota` como **Número decimal** (os tipos de todas as colunas estão no passo 11).
6. Deduplicar por `product_id` com *Agrupar por*: em cada grupo fica a linha de **maior `avaliacoes`** e, no empate, a de **menor `ordem_origem`**. **Conferir 1.351.** Na expansão do agrupamento, **desmarcar** *Usar o nome da coluna original como prefixo* e **não expandir `product_id`** — ele já é a chave do grupo; senão nascem `product_id.1` e colunas com prefixo, que a `qa_compara_gold` acusa.

> ⚠️ **Não usar "Remover duplicatas" depois de classificar.** A ordem não é garantida, e **65 dos 92** produtos repetidos empatam no máximo — o resultado passaria a depender do algoritmo de ordenação.

### `gold_intermediaria`
7. Manter só produtos com `nota` e `avaliacoes` válidas → **1.348**.
8. Cortes sobre a base inteira: `List.Percentile` (modo padrão `ExcelInc`) e `List.Median`. **p90 = 36.384 · mediana = 4.740.**
9. Colunas derivadas:

| Coluna | Regra | Confere |
|---|---|---|
| `nota_corrigida` | Wilson 95% — fórmula abaixo | mediana **4,065** |
| `categoria_n1` | texto antes do primeiro `\|` | 9 valores |
| `categoria_n2` | os dois primeiros níveis unidos por `" \| "` | 29 valores |
| `engajamento` | `alto` ≥ 36.384 · `baixo` < 4.740 · senão `intermediario` | **alto 136 · intermediario 539 · baixo 673** |
| `satisfacao` | `baixa` < 4,0 · `alta` ≥ 4,3 · senão `media` | **baixa 339 · media 591 · alta 418** |
| `q5_risco_vitrine` | engajamento alto **e** nota < 4,0 | **19** |
| `q6_subexplorado` | nota ≥ 4,3 **e** avaliacoes < 4.740 | **187** |
| `faixa_desconto` | `[0,20]` `(20,40]` `(40,60]` `(60,80]` `(80,100]` — **fechados à direita, zero na primeira** — rotulados `0-20%` · `21-40%` · `41-60%` · `61-80%` · `81-100%` | **175 / 329 / 469 / 324 / 51** |
| `relevancia` | `Âncora` (alto+alta) · `Risco de vitrine (Q5)` · `Subexplorado (Q6)` · `Cauda frágil` (baixo+baixa) · `Intermediário` — **os rótulos da `tab17`**, para conferir rótulo a rótulo | **41 / 19 / 187 / 227 / 874** |
| `n_referencias` | quantidade de `review_id` do bloco | soma **10.588** |
| `faixa_ordem` `engaj_ordem` `satisf_ordem` | colunas de ordem, para a seção 3 | — |

10. `pareto_80`: ordenar por `avaliacoes` decrescente e marcar o produto enquanto o acumulado **antes dele** for menor que 80% do total — o que cruza a linha entra. Guardar `pareto_posicao` e `pareto_acumulado_pct`, que desenham a curva. **Conferir 306** (o 306º leva o acumulado a 80,018%).

```
nota_corrigida = 1 + 4 × [ p + z²/(2n) − z·√( p(1−p)/n + z²/(4n²) ) ] / [ 1 + z²/n ]

onde  p = (nota − 1) / 4 ·  n = avaliacoes ·  z = 1,96
```

### `BaseAnalitica`
11. Importar `02_results/tables/tab22_arquetipo_por_produto.csv` (UTF-8, cultura en-US) e **renomear a consulta para `tab22`** — o conector dá o nome do arquivo. Mesclar a `BaseAnalitica` com `tab22` por `product_id` — junção **externa esquerda** — e trazer só `arquetipo`, **desmarcando** *Usar o nome da coluna original como prefixo* (senão a coluna nasce `tab22.arquetipo`); remover `review_id` e `ordem_origem`, tipar todas as colunas. **Conferir: zero linhas com `arquetipo` vazio** — a `tab22` cobre os 1.348 produtos. **Tipos:** `avaliacoes` **Número inteiro**; `preco_desc`, `preco_tab`, `desconto`, `nota` e `nota_corrigida` **Número decimal** (`desconto` aceita inteiro: a origem só traz percentuais redondos); `q5_risco_vitrine`, `q6_subexplorado` e `pareto_80` **Verdadeiro/Falso** — é o que `verifica_pbix.py` confere.

### `Reviews`
12. Partir de `gold_intermediaria` **na ordem da gold** (`avaliacoes` decrescente, `ordem_origem` crescente), dividir `review_id` em **linhas** pela vírgula, aparar espaços.
13. Deduplicar por `review_id` mantendo a **primeira ocorrência nessa ordem**, com índice explícito — **759 `review_id` pertencem a mais de um produto**, e a base atribui cada um ao primeiro. **Conferir 9.255** (de 10.588 referências). **Manter só** `review_id`, `product_id`, `categoria_n1`, `nota` e `satisfacao` — **9.255 × 5**.

### Tabelas do Python e conferência
14. Importar `tab03`, `tab05`, `tab07`, `tab14`, `tab23` e `03_dashboard/conferencia_referencia.csv` em **UTF-8** e **cultura en-US**, e **renomear cada consulta para o nome curto** — `tab03`, `tab05`, `tab07`, `tab14`, `tab23`, `Conferencia`. O conector dá o nome do arquivo (`tab03_correlacoes`…), e as medidas e o verificador usam o curto. Nenhuma se relaciona com o modelo.
15. **`qa_compara_gold`:** ler `00_data/gold/base_analitica.csv` numa consulta **`gold_python`** (UTF-8, cultura en-US) e comparar a `BaseAnalitica` com ela por `product_id`, **coluna a coluna** — as 17 colunas da gold; as sete derivadas dos passos 9 e 10 e `arquetipo` ficam de fora, cada uma com a conferência do passo onde nasce —, tolerância `1e-9` em `nota_corrigida`. **Esperado: zero linhas.**
16. **Desativar a carga** de `bronze_amazon`, `silver_produtos`, `gold_intermediaria`, `tab22`, `gold_python` e `qa_compara_gold` (botão direito > *Habilitar carga*). Consulta nova nasce com carga ligada.

> ⚠️ **O passo 16 é o que impede o arquivo de guardar dados pessoais.** Com a carga ativa, `user_name` e o texto das avaliações são gravados dentro do `.pbix`, mesmo sem aparecer em visual nenhum.

**✅ Antes de seguir:** 1.465 → 1.351 → 1.348 → 9.255 reconciliados · `qa_compara_gold` com zero linhas · intermediárias sem carga.

---

## 3 · Modelo

1. Relação **`BaseAnalitica[product_id]` 1 → N `Reviews[product_id]`**, filtro em **direção única**. **É a única**: apagar qualquer outra que apareça na exibição de modelo.
2. `tab03`, `tab05`, `tab07`, `tab14`, `tab23` **sem relação**. Os visuais delas mostram resultados da base inteira e não respondem a filtro — **escrever isso no próprio visual**.
3. Criar tabela vazia **`_Medidas`** (*Inserir dados*) para abrigar todas as medidas.
4. Em **todas** as colunas numéricas: *Resumir por* = **Nenhum**.

> ⚠️ Soma automática de `avaliacoes` repete a contagem das variantes do mesmo produto. **Todo total sai de medida.**

5. *Classificar por coluna*: `faixa_desconto`, `engajamento` e `satisfacao` pelas colunas de ordem do passo 9.
6. Hierarquia `categoria_n1 > categoria_n2` para o detalhamento.
7. Formatos: preços **sem símbolo**, com separador de milhar (`1.099`). Desconto como `0"%"` — o valor já vai de 0 a 100, e o formato percentual do Power BI o multiplicaria de novo.
8. Ocultar colunas técnicas: colunas de ordem, `category` completa, `pareto_posicao` fora do visual da curva.
9. **Conferir o modelo pelo arquivo, não pelo olho:** *Arquivo > Exportar > Modelo do Power BI* → `03_dashboard/TechChallenge4_G12.pbit`, e rodar, da raiz do projeto, `python 03_dashboard/verifica_pbix.py 03_dashboard/TechChallenge4_G12.pbit 03_dashboard/TechChallenge4_G12.pbix` — **salvar o `.pbix` antes de exportar**. É o primeiro par real: se a seção 7 reprovar sem nenhuma mudança entre os dois, é diferença de formato, e o verificador precisa ser ajustado agora, não na entrega. Nesta altura as medidas e a página `Conferência` ainda não existem — **só as linhas de medidas (5) e a da página (6) podem falhar**. Qualquer outra falha (carga ligada, relação automática, coluna faltando) se corrige antes da seção 4.

---

## 4 · As 22 medidas, e a conferência

1. Criar as **22 medidas** de [`medidas_dax.md`](medidas_dax.md) (M01–M22) em `_Medidas`, **copiando cada expressão como está**. O catálogo já vem na notação que o DAX aceita (`#,##0` no `FORMAT`).
2. **Logo depois, a página oculta `Conferência`**, de [`conferencia_dax.md`](conferencia_dax.md): as 6 medidas `Conf ·` e a página. Só depois das 22: as medidas `Conf ·` citam todas, e o DAX não aceita referência a medida que ainda não existe — enquanto faltar uma, a página fica em erro. `Conf · Divergentes` tem de dar **0**.
3. Criar as **variantes T2**: `Participação da Categoria no Volume (T2)` e o mesmo padrão `IF([Produtos Ativos] >= 30, …, BLANK())` para M07, M09 e M10 e **para toda medida que uma página exibe por faixa, subcategoria ou arquétipo** (QA1, QA3, QA7 e os extras do passo 4.4).
   *Por que não só por categoria.* As segmentações das páginas 2a, 2b, 2c e 3 cruzam com qualquer eixo, e o grupo cai abaixo do piso sem aviso. **Medido na base analítica:** com *Home & Kitchen* selecionada, a faixa 81–100% fica com **n = 2**; com *OfficeProducts*, as cinco faixas ficam com 25 · 3 · 2 · 1 · 0; com *Computers & Accessories*, o arquétipo A fica com 19; com engajamento alto, A = 20, B = 0 e C = 25. Sem a variante, a página entregue compara grupos de n < 30 — que é exatamente o que T2 proíbe.
   *Alternativa aceita:* filtro de visual `[Produtos Ativos] >= 30`, ou desligar a interação daquela segmentação com aquele visual — mas então a escolha fica declarada no rodapé da página.
4. Criar as medidas que o catálogo não cobre, **cada uma conferida contra uma tabela do Python** — conferir **fora** do Power BI, abrindo o CSV; se importar algum, desligar a carga:

| Para | Medida | Confere contra |
|---|---|---|
| Q1 | produtos por quadrante (41 · 19 · 187 · 227 · 874) | `tab17_matriz_relevancia.csv` |
| QA1 | n, nota mediana, Wilson e volume mediano por faixa | `tab08_faixas_desconto.csv` |
| QA3 | `STDEV.S` e IQR (`PERCENTILEX.INC` 0,75 − 0,25) por subcategoria | `tab16_satisfacao_subcategoria.csv` |
| Q7 | blocos, referências e reviews por faixa (339 · 591 · 418; 10.588) | `tab06_corpus.csv` |
| QA7 | n e medianas por arquétipo | `tab05_arquetipos.csv` |
| Q8 | produtos do Pareto com nota < 4,0 (**39 de 306**) | citado na conclusão do vídeo |
| L8 | `Participação no Volume sem Variantes` (Electronics **53,1%**) | `tab18_relevancia_categoria.csv` + a leitura obrigatória de L8 |

**A medida de L8, por extenso.** A página 2a exige as **duas** versões da participação (com e sem variantes), e a segunda não sai de nenhuma medida do catálogo. Ela colapsa cada grupo de listagens variantes — mesmo par (`avaliacoes`, `nota`) **dentro da categoria** — a uma linha, nos dois lados da divisão:

```dax
Participação no Volume sem Variantes =
VAR Colapsada =
    SUMX (
        SUMMARIZE ( BaseAnalitica, BaseAnalitica[categoria_n1], BaseAnalitica[avaliacoes], BaseAnalitica[nota] ),
        BaseAnalitica[avaliacoes]
    )
VAR TotalColapsado =
    SUMX (
        SUMMARIZE ( ALL ( BaseAnalitica ), BaseAnalitica[categoria_n1], BaseAnalitica[avaliacoes], BaseAnalitica[nota] ),
        BaseAnalitica[avaliacoes]
    )
RETURN
    DIVIDE ( Colapsada, TotalColapsado )
```

*Por que `categoria_n1` entra no `SUMMARIZE`.* Quatro grupos de variantes atravessam categorias. Colapsando-os globalmente o valor vai a 53,116%; colapsando dentro da categoria, a 53,119%. Os dois exibem **53,1%**, e a segunda forma é a que a leitura de L8 descreve ("participação da categoria sem contar a mesma avaliação duas vezes"). Conferir contra `gera_checklist.py`, que publica o mesmo número.

5. **Conferir o total na página `Conferência`:** o cartão `Conf · Divergentes` tem de mostrar **0** — 33 de 33 linhas: as 21 medidas com referência no total, 6 sob filtro de categoria (o `ALL` que o total esconde) e 2 da `Reviews`. A tolerância é **por linha**, na escala do DAX: 0 em contagens e somas, 1e-12 em frações e medianas decimais, 1e-8 na nota corrigida — só diferença de ponto flutuante passa. A página fica no arquivo entregue e se refaz a cada alteração do modelo.
6. **Conferir o contexto filtrado** — é o passo que pega o erro real: matriz por `categoria_n1` contra [`valores_referencia_por_categoria.csv`](valores_referencia_por_categoria.csv). A coluna *Produtos* soma **1.341** e a *Participação* soma **99,5%**; os 7 produtos e 0,5% restantes são a supressão de T2.
   *Um `ALLSELECTED` no lugar de `ALL` não aparece nesta matriz sem segmentação: os dois dão 99,5%. Ele aparece com uma segmentação que exclua as 5 categorias pequenas — `ALL` mantém 99,5%, `ALLSELECTED` vai a 100% — e `verifica_pbix.py` o pega comparando a expressão com o catálogo.*

### As cinco armadilhas conhecidas

| Sintoma | Causa | Correção |
|---|---|---|
| M07 na casa dos trilhões | localidade pt-BR leu `4.0657` como inteiro | fonte em **English (United States)** |
| M11 / M12 / M13 / M22 devolvem 0 ou erro | booleanos importados como texto | tipar **Verdadeiro/Falso** no Power Query — não trocar a medida: o verificador compara a expressão com o catálogo |
| M18 muda ao clicar numa categoria | faltou `ALL` no `PERCENTILEX.INC` | o corte é da base inteira |
| M01 devolve 1.351 ou 1.465 | o modelo aponta para silver ou bronze | refazer a origem a partir de `gold_intermediaria` — **nunca** importar o CSV da gold no lugar: ele é o gabarito |
| Rodapé M21 exibe `1348,000` | formato em notação brasileira | na caixa de formato e no `FORMAT`, **notação invariante**: `#,##0` e `0.00` |

**✅ Antes de montar qualquer página:** `qa_compara_gold` com zero linhas · **`Conf · Divergentes` = 0** (33 de 33) · matriz por categoria batendo linha a linha.

---

## 5 · Grade e padrão das páginas

1. Página em **16:9 (1280 × 720)** — grava sem tarja em 1080p.
2. Ligar *Exibição > Linhas de grade* e *Ajustar à grade*, e montar **uma página modelo**:

| Zona | Altura (px) | Conteúdo |
|---|---|---|
| Cabeçalho | 0–64 | título escrito como achado · códigos das perguntas · navegador de páginas |
| Indicadores | 72–160 | até 4 cartões |
| Área principal | 168–640 | 2 a 3 visuais alinhados |
| Rodapé | 648–720 | **M21** (fonte, base, n filtrado, corte) + **L1, L4 e L5**, uma linha cada |

3. Inserir o **navegador de páginas** nativo (*Inserir > Botões > Navegador > Navegador de páginas*): atualiza-se sozinho conforme as páginas nascem.
4. **Duplicar a página modelo sete vezes:** Visão Executiva · 2a Categorias · 2b Quadrantes · 2c Rankings · Preços · Customer Insights · Recomendações. O rodapé M21 vale nas **sete**.
5. Título de cada visual **escrito como achado, com número** — *"19 produtos muito avaliados têm nota abaixo de 4,0"*, não *"Produtos por quadrante"*. Subtítulo com **base, n e limiar**.

---

## 6 · As páginas, visual por visual

Para **cada** visual: montar → título como achado e subtítulo com base/n/limiar → **conferir o número exibido antes de seguir**.

> **A tabela abaixo diz o quê; [`GUIA_GRAFICOS_POWERBI.md`](GUIA_GRAFICOS_POWERBI.md) diz o como.** Lá cada visual tem ficha própria (`G-01` a `G-35`) com a tabela, a coluna em cada poço do visual, a ordenação, os filtros, a interação e a formatação. Quem está montando trabalha com as duas abertas: esta tabela para saber o que a página precisa, a ficha para montar sem decidir nada.

Ao fechar cada página: um único âmbar · nenhuma pizza ou rosca · máximo 5 séries · rodapé M21 presente · **nenhum visual de Python, de R ou de loja externa**.

| Página | Para | Visual | Dados | Regra |
|---|---|---|---|---|
| **1 · Visão Executiva** | Q2 | 4 cartões | Nota 4,10 · Desconto 49% · Preço de tabela 1.795 · Volume 4.740 | sem símbolo de moeda |
| 1 | Q2 | cartão | corte de engajamento alto **36.384** (M18) | é volume de avaliações, nunca venda |
| 1 | Q4 | histograma de nota | compartimentos de 0,1; faixas baixa (339) e alta (418) por cor | rótulo direto |
| 1 | QA2 | curva de Pareto | posição × % acumulado, referência em 80%, cartões **306** e **22,7%** | o ponto de 80% é o **único âmbar** |
| 1 | Q8 | cartão | **39 dos 306** produtos do Pareto abaixo de 4,0 (12,7%) | — |
| 1 | Q1 | matriz 2 × 2 | `relevancia`: Âncora 41 · Risco 19 · Subexplorado 187 · Cauda frágil 227 | Intermediário (874) no rodapé |
| **2a · Categorias** | Q4 | barras horizontais | % Satisfação Baixa (T2) e Nota Corrigida (T2) nas 4 categorias | rodapé: 5 categorias, 7 produtos, 0,5% suprimidos |
| 2a | Q4 | barras horizontais | Participação no Volume (T2): 59,7 · 26,6 · 12,6 · 0,6% | versão sem variantes ao lado (Electronics **53,1%**) |
| 2a | QA3 | **barras de desvio-padrão** | as 8 subcategorias com n ≥ 30, da maior dispersão para a menor, **com o n no rótulo** | climatização e fones em **laranja**; sem âmbar |
| 2a | QA3 | tabela ao lado | desvio-padrão, IQR, % abaixo de 4,0 e n | rodapé: 8 subcategorias · 88,3% · piso n ≥ 30 |
| **2b · Quadrantes** | Q1 · Q5 | dispersão | avaliações (log) × nota, linhas em p90, mediana, 4,0 e 4,3 | quadrante Q5 em âmbar · **caixa "como ler"** |
| 2b | QA3 | dispersão por subcategoria | nota (Y) × subcategoria (X), um ponto por produto, só as 8 acima do piso | mostra **a forma**: fones deslocados, climatização espalhada |
| 2b | Q5 | tabela nominal | os **19**: produto, subcategoria, avaliações, nota, Wilson | lista nominal é exceção ao piso de 30 |
| 2b | Q6 | 2 cartões | **187** "funil de triagem" (M12) e **61** "lista acionável" (M22) | *"bem avaliados com baixo volume de avaliações"* — **vedado** "baixa visibilidade" |
| 2b | Q6 | tabela nominal | os **61**, por nota corrigida, com avaliações | — |
| **2c · Rankings** | QA6 | 2 tabelas lado a lado | top 10 por nota bruta × por Wilson, com n | a de Wilson é a homologada |
| 2c | QA7 | matriz | n e medianas: A 268 · B 335 · C 298 · D 447 | *"convenção descritiva, não descoberta"* |
| 2c | QA7 | múltiplos pequenos | B × D em desconto, volume e nota | 2 séries · título *"Desconto quase igual, resultado oposto"* |
| **3 · Preços** | Q3 | 3 cartões | Preço 899 · Preço de tabela 1.795 · Desconto 49% | sem símbolo |
| 3 | QA1 | colunas | nota corrigida por faixa, com n no rótulo e volume mediano | **âmbar na faixa 81–100%** (**3,906**; n = 51) · título: *"a única faixa abaixo de 4,0"* |
| 3 | Q3 · QA4 | barras em torno de zero | ρ dos 4 pares (`tab03`), com p e n no rótulo | magnitude junto com significância · escala divergente |
| 3 | QA4 | dispersão | preço de tabela (log) × nota | ρ = +0,032, p = 0,236 → **sem associação** |
| **4 · Customer Insights** | Q7 | caixa de texto no topo | no máximo **8 avaliações por produto** (média 7,85) | **dito na página**, não só no rodapé |
| 4 | Q7 | cartões + tabela | 1.348 blocos · 10.588 referências · 9.255 reviews; por faixa 339 · 591 · 418 | faixa intermediária em cinza, *"fora do contraste"* |
| 4 | Q7 | barras horizontais | n-gramas que mais separam notas baixas e altas (`tab14`) | unidade = bloco de review |
| 4 | QA5 | barras horizontais | temas dos 19 blocos de Q5 (`tab23`) | leitura qualitativa dirigida · 147 avaliações |
| 4 | — | caixa de texto | **as 4 perguntas de Customer Insights do enunciado**: o que valorizam · problemas frequentes · padrões positivos · temas negativos, com a pergunta do escopo que responde cada uma | torna a cobertura visível |
| **5 · Recomendações** | Q8 | 5 cartões de texto | uma recomendação cada, com seu número: 19 · 335 · 61 · **ρ = −0,150 (p = 3,1e-08; n = 1.348)** · 97,2% | nada em receita · **ρ nunca sem o p** (T5) |
| 5 | Q8 | barras | AUC por bloco (`tab07`, agrupada por variante): 0,56 · 0,58 · 0,66 · **0,70 ± 0,01** | *"triagem, não veredito"* |
| 5 | Q8 | caixa de texto | **as 8 limitações completas** + registro "21 de 21 medidas conferidas" | — |
| 5 | — | caixa de texto | **"Como estes números foram conferidos"**: Conferência com 33 valores recalculados em DAX · `verifica_pbix.py` provado em 36 casos · trava do sumário provada em 41 números plantados · B × D testado (efeito 0,134 no desconto, 0,670 na nota) | texto em `GUIA_GRAFICOS_POWERBI.md`, ficha **G-36** — rigor que o avaliador não vê se ninguém apontar |
| **Oculta** | — | detalhamento | ficha do produto: nota, Wilson, avaliações, preço, desconto, arquétipo, quadrante | nenhum dado de consumidor |
| **Oculta** | — | dica de ferramenta | n e nota corrigida ao passar o mouse | — |

---

## 7 · Navegação, filtros e interações

1. Navegador de páginas em todas as visíveis; botão **Voltar** nas ocultas.
2. Segmentações nas páginas **2a, 2b, 2c e 3**: categoria (hierarquia), faixa de desconto, engajamento, satisfação, arquétipo.
3. **Sincronizar segmentações** entre essas quatro (*Exibição > Sincronizar segmentações*). A **Visão Executiva fica sem segmentação** — é a fotografia da base inteira.
4. *Formatar > Editar interações*: **desligar o filtro cruzado** nos cartões de corte (M18, M19) e em **todos** os visuais alimentados pelas tabelas do Python.
5. **Detalhamento** por `product_id`: das listas de 19 e de 61, dos rankings e das dispersões para a página *Detalhe do produto*.
6. Ligar a **página de dica de ferramenta** aos visuais de produto.
7. **Indicadores:** estado inicial de cada página + botão *Redefinir filtros*; e os estados da demonstração do vídeo, para a gravação não depender de cliques ao vivo.
8. Testar cada botão com **Ctrl + clique** no Desktop.

---

## 8 · Antes de entregar o arquivo

A revisão não depende de outra pessoa: cada frente virou uma conferência que falha sozinha. Comandos rodados **da raiz do projeto**.

- [ ] `qa_compara_gold` com **zero linhas**
- [ ] Página `Conferência`: **`Conf · Divergentes` = 0** — 33 de 33 linhas
- [ ] Salvar o `.pbix` (Ctrl+S) e **só então** exportar o `.pbit` final, e rodar `python 03_dashboard/verifica_pbix.py 03_dashboard/TechChallenge4_G12.pbit 03_dashboard/TechChallenge4_G12.pbix` — **saída 0**. Exportar sem salvar deixa o `.pbix` entregue com o modelo antigo, e o verificador não tem como ver
- [ ] Exportar **uma imagem por página** para `03_dashboard/screenshots/` (`p1_visao_executiva.png`, `p2a_categorias.png`, …)
- [ ] `python 03_dashboard/gera_checklist.py` — reconfere os números contra este guia — e [`checklist_qualidade.pdf`](checklist_qualidade.pdf) impresso, **todas as células marcadas** contra as imagens
- [ ] *Analisador de desempenho* sem visual lento
- [ ] **Abrir sem a origem:** copiar o `.pbix` para outra pasta, **renomear a pasta `00_data/bronze/`** e abrir. Tem de exibir tudo (os dados vão embutidos); só *Atualizar* falha — é o cenário do avaliador
- [ ] **Atualizar com a origem:** desfazer a renomeação e *Atualizar* sem erro — `pPasta` aponta para a pasta do projeto

Depois disso o arquivo é congelado, antes da gravação.

---

## Números de conferência

| Grandeza | Valor |
|---|---|
| Reconciliação | 1.465 → 1.351 → **1.348**; 1.350 (nota válida) e 1.349 (volume válido) são bases **paralelas** a partir de 1.351 |
| Produtos · volume total | 1.348 · 23.801.471 |
| Preço mediano · de tabela · desconto | 899 · 1.795 · 49% |
| Nota mediana · corrigida · volume mediano | 4,10 · 4,065 · 4.740 |
| Cortes: p90 · mediana | 36.384 · 4.740 |
| Satisfação baixa · média · alta | 339 (25,1%) · 591 · 418 (31,0%) |
| Engajamento alto · intermediário · baixo | 136 · 539 · 673 |
| Quadrantes | Âncora 41 · Risco 19 · Subexplorado 187 · Cauda frágil 227 · Intermediário 874 |
| Q6 funil × acionável | 187 × **61** |
| Pareto 80% | 306 (22,7%) · **39 deles abaixo de 4,0** |
| Faixas de desconto | 175 · 329 · 469 · 324 · 51 |
| Subcategorias acima do piso | 8 de 29 · cobertura 88,3% (1.190) |
| Participação por categoria | 59,7 · 26,6 · 12,6 · 0,6% (soma 99,5%) |
| Electronics sem variantes | 59,7% → **53,1%** |
| Corpus | 1.348 blocos · 10.588 referências · **9.255** reviews |
| Blocos por faixa | 339 · 591 · 418 |
| Arquétipos A · B · C · D | 268 · 335 · 298 · 447 |
| Correlações (ρ, p) | desconto×nota −0,150 (3,1e-08) · desconto×volume −0,132 · preço×nota +0,032 (0,236) · volume×nota +0,193 |
| AUC por bloco | 0,556 · 0,583 · 0,658 · **0,704 ± 0,01** |

**Dispersão por subcategoria — a ordem das barras da página 2a:**

| Subcategoria | n | Desvio-padrão |
|---|---|---|
| Home & Kitchen · Heating, Cooling & Air Quality | 116 | **0,346** |
| Home & Kitchen · Kitchen & Home Appliances | 307 | 0,336 |
| Electronics · Wearable Technology | 62 | 0,326 |
| Electronics · Home Theater, TV & Video | 156 | 0,310 |
| Computers & Acc. · Networking Devices | 30 | 0,276 |
| Computers & Acc. · Accessories & Peripherals | 305 | 0,258 |
| Electronics · Headphones, Earbuds & Acc. | 63 | 0,224 |
| Electronics · Mobiles & Accessories | 151 | **0,194** |

---

## As nove regras, em uma linha cada

| # | Regra |
|---|---|
| **T1** | Todo ranking por nota usa a **nota corrigida de Wilson**, com o n ao lado |
| **T2** | Nenhum **grupo agregado** com n < 30 é ranqueado; supressão declarada. **Listas nominais são exceção** |
| **T3** | Todo visual declara **fonte, base, n efetivo e limiar** |
| **T4** | **Vedada linguagem causal** — correlação indica associação |
| **T5** | **Magnitude sempre junto com significância** |
| **T6** | `rating_count` é **volume de avaliações** — nunca vendas, receita ou demanda. **Vedado** "baixa visibilidade" |
| **T7** | **Vedado exibir `user_name` ou `user_id`** |
| **T8** | Todo método textual declara **unidade**, deduplica por `review_id` e cita o **truncamento em 8** |
| **T9** | Só a **paleta v06**, aplicada por tema · máximo 5 séries · com 6, rótulo direto |

**As três limitações que vão no rodapé de toda página:**
**L1** — máximo de 8 avaliações por produto (média 7,85): são os temas visíveis na vitrine, não a distribuição real.
**L4** — nenhuma variável de venda: nada em receita, volume vendido ou tendência.
**L5** — marketplace indiano, valores em rupia indiana, sem conversão e sem símbolo.

O texto completo das oito está em `method/limitations/limitacoes_obrigatorias.md`.

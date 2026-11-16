# `01_notebooks/` — a análise, em ordem

Executar nesta sequência. Cada um consome a saída do anterior.

| # | Notebook | Entrega |
|---|---|---|
| 01 | `01_eda.ipynb` | shape, tipos, nulos, duplicidade, outliers, distribuição. **As 8 limitações no cabeçalho** |
| 02 | `02_tratamento.ipynb` | deduplicação determinística, conversões, `00_data/gold/base_analitica.csv` |
| 03 | `03_medidas.ipynb` | cada medida com o valor de referência que o DAX terá de reproduzir |
| 04 | `04_analises.ipynb` | as 12 perguntas do relatório final, cortes, quadrantes, correlações, ML2 e ML4 |
| 05 | `05_nlp.ipynb` | corpus deduplicado por `review_id`, n-gramas e TF-IDF (`tab14`, página 4 do dashboard) · **QA5** — os 19 blocos de Q5 codificados por livro de códigos, sem TF-IDF (`tab23`) |
| 06 | `06_storytelling.ipynb` | figuras finais para o `.pbix` e para o vídeo |

## Cabeçalho obrigatório de cada notebook
Objetivo · entradas e saídas · código comentado · tratamento de exceções · **célula final de validação com reconciliação de contagens**.

## Primeira célula de código, sempre
```python
import sys; sys.path.insert(0, '../src')
from paleta import aplicar
aplicar()
```
Sem isso, os gráficos saem na paleta padrão da biblioteca — descumprimento de T9.

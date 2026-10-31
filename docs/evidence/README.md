# 🧾 `evidence/` — prova de que o controle rodou

Não basta dizer que o número confere. Aqui fica a **saída datada** de cada controle, para que a afirmação seja verificável sem reexecutar nada.

| Arquivo | O que é |
|---|---|
| `E01_validador.txt` | saída de `src/valida_base.py`, com data, versão do Python e o SHA-256 da base usada — **107 asserções, 0 falhas, 0 puladas** |
| `E02_paleta.txt` | saída de `src/paleta.py` — confere a paleta v06 contra o tema do Power BI |
| `E04_dicionario.txt` | saída de `src/valida_dicionario.py` — cruza o dicionário de dados com os artefatos, coluna a coluna |

`E03` (reconciliação medida a medida, valor em Python × valor em DAX) só pode existir com o `.pbix`: ele compara o valor que o Power BI exibe com o que o Python calculou, e sem o primeiro lado não há o que comparar. Será gerado junto com o arquivo.

## Como gerar

```bash
{ date; python3 --version; shasum -a 256 00_data/bronze/amazon.csv; python3 src/valida_base.py 00_data/bronze/amazon.csv; } > docs/evidence/E01_validador.txt
{ date; python3 --version; python3 src/paleta.py; } > docs/evidence/E02_paleta.txt
{ date; python3 --version; python3 src/valida_dicionario.py; } > docs/evidence/E04_dicionario.txt
```

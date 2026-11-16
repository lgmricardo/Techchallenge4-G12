# -*- coding: utf-8 -*-
"""
Prova de que a trava visual de `gera_figuras.py` reprova o que deve.

POR QUE ESTE ARQUIVO EXISTE
---------------------------
O projeto confere número e texto em seis comandos: 107 asserções sobre a base,
dicionário coluna a coluna, DAX comparado caractere a caractere, 41 números
plantados no sumário, 38 casos do verificador do `.pbix` e o lint. **Nenhum
deles olhava dentro de um PNG** — e foi exatamente por aí que passou um defeito
real: ao unificar a vírgula decimal dos eixos, o formatador foi aplicado também
a eixo de categoria, e `Electronics · Home&Kitchen · Computers&Accessories`
virou `8 · 7 · 6` na `fig05`; as faixas de desconto viraram `0 · 1 · 2 · 3 · 4`
na `fig07`. A figura saiu, o script terminou com código 0, os validadores
passaram, o relatório foi gerado e o commit foi feito.

A `confere_visual()` fechou esse ponto cego. Ela mora em `src/paleta.py` — o módulo
que os notebooks já importam por causa de T9 —, e é chamada pelo `gera_figuras.py` e
pelos seis notebooks, de modo que as **33 figuras** do projeto passam por ela. Mas uma trava só vale se reprovar —
e trava que nunca foi vista falhando é promessa, não garantia. Este script monta
uma figura com cada defeito, um por vez, e exige que a função acuse; monta uma
figura correta e exige que ela passe.

O que é coberto, e por quê cada um tem regra escrita:
  T3  — rodapé com fonte, base e *n*; sem ele nenhum número é rastreável
  T3/T6 — rodapé que a borda corta: a regra existe no código e some na imagem
  T9  — no máximo 5 séries na legenda · vedado pizza e rosca
  o defeito de 31/10/2026 — eixo de categoria com rótulo numérico

O que NÃO é coberto, de propósito: a regra do âmbar único. A cor âmbar é também
a primeira da escala categórica, e contá-la sem saber o papel de cada elemento
acusaria uso legítimo. Essa segue como conferência humana, no checklist da F8.

Uso: python src/testa_confere_visual.py
"""

import os
import sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.ticker import FuncFormatter  # noqa: E402

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


sys.path.insert(0, os.path.join(RAIZ, "src"))
from paleta import confere_visual  # noqa: E402


def rodape(fig):
    fig.text(0.01, 0.005, "Fonte: Kaggle · base analítica n = 1.348", fontsize=7)


# (nome, como montar a figura, deve reprovar?)
CASOS = [
    ("sem rodapé — T3",
     lambda fig, ax: ax.bar(["Electronics", "Home&Kitchen"], [490, 447]), True),

    ("pizza — T9",
     lambda fig, ax: (rodape(fig), ax.pie([490, 447, 373])), True),

    ("6 séries na legenda — T9",
     lambda fig, ax: (rodape(fig),
                      [ax.plot([1, 2], label=f"série {i}") for i in range(6)],
                      ax.legend()), True),

    ("eixo de categoria com rótulo numérico — o defeito de 31/10",
     lambda fig, ax: (rodape(fig),
                      ax.bar(["Electronics", "Home&Kitchen"], [490, 447]),
                      ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _p: str(int(v)))),
                      fig.canvas.draw()), True),

    ("o mesmo defeito, no eixo Y de um gráfico de barras horizontais",
     lambda fig, ax: (rodape(fig),
                      ax.barh(["Electronics", "Home&Kitchen"], [490, 447]),
                      ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _p: str(int(v)))),
                      fig.canvas.draw()), True),

    ("rodapé comprido demais, cortado pela borda — o defeito da cartela B × D",
     lambda fig, ax: (fig.text(0.5, 0.005, "Fonte: base analítica, n = 1.348 · " + "texto longo que não cabe no quadro · " * 6,
                               ha="center", fontsize=8),
                      ax.bar(["Electronics", "Home&Kitchen"], [490, 447]),
                      fig.canvas.draw()), True),

    ("rodapé em duas linhas, que cabe no quadro — a correção",
     lambda fig, ax: (fig.text(0.5, 0.03, "Fonte: base analítica, n = 1.348 · texto longo que agora cabe\n"
                               "segunda linha do rodapé", ha="center", fontsize=8),
                      ax.bar(["Electronics", "Home&Kitchen"], [490, 447]),
                      fig.canvas.draw()), False),

    ("5 séries na legenda — o limite, que é permitido",
     lambda fig, ax: (rodape(fig),
                      [ax.plot([1, 2], label=f"série {i}") for i in range(5)],
                      ax.legend()), False),

    ("eixo numérico com rótulo numérico — o caso correto",
     lambda fig, ax: (rodape(fig), ax.scatter([1, 2, 3], [4, 5, 6]), fig.canvas.draw()), False),

    ("figura correta, com nome de categoria no eixo",
     lambda fig, ax: (rodape(fig),
                      ax.bar(["Electronics", "Home&Kitchen"], [490, 447]),
                      fig.canvas.draw()), False),
]


resultados = []
for nome, montar, deve_reprovar in CASOS:
    fig, ax = plt.subplots()
    montar(fig, ax)
    try:
        confere_visual(fig, nome)
        reprovou, detalhe = False, ""
    except AssertionError as erro:
        reprovou, detalhe = True, str(erro)
    plt.close(fig)
    resultados.append((nome, reprovou, deve_reprovar, detalhe))

erros = 0
for nome, reprovou, deve_reprovar, detalhe in resultados:
    ok = reprovou == deve_reprovar
    erros += not ok
    esperado = "reprova" if deve_reprovar else "passa  "
    print(f"{'OK' if ok else 'ERRO':4s} | {esperado} · {nome}"
          + ("" if ok else f" — a trava {'reprovou' if reprovou else 'deixou passar'}"))
    if ok and reprovou:
        print(f"       └ {detalhe[:150]}")

print(f"\n{len(resultados)} casos · {erros} errados")
sys.exit(1 if erros else 0)

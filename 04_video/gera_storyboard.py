# -*- coding: utf-8 -*-
"""
Storyboard do vídeo — 04_video/storyboard.md, extraído de roteiro.md.

POR QUE É GERADO E NÃO ESCRITO
------------------------------
O roteiro já registra, segmento a segmento, o que é dito e o que aparece na
tela. Um storyboard escrito à parte seria uma segunda cópia da mesma
informação — e a primeira alteração no roteiro deixaria as duas divergentes,
que é a classe de defeito que este projeto mais encontrou nas revisões.

Este script lê a coluna "O que aparece na tela" de cada bloco do roteiro e
monta o storyboard a partir dela. A fonte da verdade é o roteiro; o
storyboard é uma VISÃO dele, focada no que a câmera mostra. Alterou o
roteiro, rode de novo.

Também confere a cronometragem: cada bloco precisa ter segmentos contínuos
que somem exatamente a duração declarada no título, e o total precisa caber
em 7:00. Se não couber, o script falha em vez de gerar um storyboard errado.

Uso: python 04_video/gera_storyboard.py
"""

import os
import re
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))
ROTEIRO = os.path.join(PASTA, "roteiro.md")
SAIDA = os.path.join(PASTA, "storyboard.md")
LIMITE = 7 * 60


def segundos(tempo):
    m, s = tempo.strip("* ").split(":")
    return int(m) * 60 + int(s)


def celulas(linha):
    """Divide uma linha de tabela markdown respeitando o pipe escapado `\\|`."""
    bruto = re.split(r"(?<!\\)\|", linha.strip().strip("|"))
    return [c.strip() for c in bruto]


def blocos(texto):
    """Devolve [(titulo, inicio, fim, [(ini, fim, tela), ...]), ...]."""
    saida = []
    for secao in re.split(r"\n(?=## )", texto):
        cab = secao.split("\n", 1)[0]
        m = re.search(r"^## (.+?) — (\d+:\d\d) a (\d+:\d\d)", cab)
        if not m:
            continue
        titulo = re.sub(r"\s+·\s+\*\*.*$", "", m.group(1)).strip()
        segmentos = []
        for linha in secao.split("\n"):
            if not linha.startswith("|"):
                continue
            c = celulas(linha)
            t = re.match(r"\*{0,2}(\d+:\d\d)[–-](\d+:\d\d)\*{0,2}$", c[0]) if c else None
            if t and len(c) >= 3:
                segmentos.append((t.group(1), t.group(2), c[2]))
        saida.append((titulo, m.group(2), m.group(3), segmentos))
    return saida


texto = open(ROTEIRO, encoding="utf-8").read()
lista = blocos(texto)

# ------------------------------------------------ conferência de cronometragem
erros = []
for titulo, ini, fim, segs in lista:
    if not segs:
        erros.append(f"{titulo}: nenhum segmento encontrado")
        continue
    if segs[0][0] != ini or segs[-1][1] != fim:
        erros.append(f"{titulo}: segmentos não começam/terminam nas bordas do bloco")
    for (a, b, _), (c, _d, _e) in zip(segs, segs[1:]):
        if b != c:
            erros.append(f"{titulo}: descontinuidade entre {b} e {c}")
    soma = sum(segundos(b) - segundos(a) for a, b, _ in segs)
    if soma != segundos(fim) - segundos(ini):
        erros.append(f"{titulo}: segmentos somam {soma}s, bloco declara "
                     f"{segundos(fim) - segundos(ini)}s")
# Os sete blocos exigidos pelo enunciado, na ordem. A cartela L1 é uma limitação dita em voz alta,
# não um bloco: antes ela era numerada como "5" e o storyboard dizia ter 8 blocos. E um bloco
# removido do roteiro passava sem que ninguém percebesse, porque só se conferiam os que existiam.
_numeros = [int(m.group(1)) for t, *_ in lista if (m := re.match(r"(\d+) ·", t))]
if _numeros != list(range(1, 8)):
    erros.append(f"o enunciado exige os blocos 1 a 7, na ordem; o roteiro tem {_numeros}")
fim_total = segundos(lista[-1][2])
if fim_total > LIMITE:
    erros.append(f"duração total {fim_total}s excede o limite de {LIMITE}s")
if erros:
    print("A cronometragem do roteiro não fecha — storyboard NÃO gerado:")
    for e in erros:
        print(f"  - {e}")
    sys.exit(1)

# ------------------------------------------------------------- o storyboard
partes = [
    "# 🎞️ STORYBOARD DO VÍDEO EXECUTIVO",
    "",
    "> **Gerado automaticamente a partir de `roteiro.md` por `gera_storyboard.py`. "
    "Não editar à mão** — alterou o roteiro, rode o script de novo. O roteiro é a "
    "fonte da verdade; este arquivo é a visão dele focada no que aparece na tela.",
    "",
    f"**Duração total: {fim_total // 60}:{fim_total % 60:02d} de 7:00** · "
    f"{len(_numeros)} blocos exigidos + {len(lista) - len(_numeros)} cartela de limitação (L1) · "
    f"{sum(len(s) for *_, s in lista)} segmentos · cronometragem conferida pelo script",
    "",
    "| # | Bloco | Início | Fim | Duração | Segmentos |",
    "|---|---|---|---|---|---|",
]
for titulo, ini, fim, segs in lista:
    d = segundos(fim) - segundos(ini)
    n = re.match(r"(\d+) ·", titulo)
    partes.append(f"| {n.group(1) if n else '—'} | {re.sub(r'^\d+ · ', '', titulo)} | {ini} | {fim} | {d // 60}:{d % 60:02d} | {len(segs)} |")
partes += ["", "---", ""]

for titulo, ini, fim, segs in lista:
    partes += [f"## {titulo} — {ini} a {fim}", "",
               "| Tempo | Duração | O que aparece na tela |", "|---|---|---|"]
    for a, b, tela in segs:
        partes.append(f"| {a}–{b} | {segundos(b) - segundos(a)} s | {tela} |")
    partes += ["", "---", ""]

partes += [
    "## Regras que valem para todo frame",
    "",
    "- **T3** — rodapé com fonte, base e *n* em todo frame que tem número.",
    "- **T7** — nenhum `user_id` ou `user_name` em nenhuma captura.",
    "- **T9** — paleta v06 aplicada por ferramenta; no máximo 5 séries por visual; "
    "**um único** elemento em âmbar por tela.",
    "- **L5** — nenhum símbolo monetário em tela; \"rupia indiana\" por extenso, "
    "e só quando necessário.",
    "",
    "A checklist completa de gravação está no fim de `roteiro.md`.",
    "",
]
open(SAIDA, "w", encoding="utf-8").write("\n".join(partes))
print(f"  {SAIDA}")
print(f"  {len(_numeros)} blocos + L1 · {sum(len(s) for *_, s in lista)} segmentos · "
      f"total {fim_total // 60}:{fim_total % 60:02d} — cronometragem conferida")

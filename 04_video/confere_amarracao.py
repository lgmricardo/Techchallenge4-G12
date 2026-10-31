# -*- coding: utf-8 -*-
"""
Confere a amarração e o ritmo do roteiro do vídeo.

POR QUE ESTE ARQUIVO EXISTE
---------------------------
O roteiro abre declarando que número falado sem linha em `tab_roteiro_numeros.csv` não
entra no vídeo. Era uma promessa sem verificação — e em 31/10/2026 ela estava quebrada em
três lugares ao mesmo tempo, num roteiro já revisado seis vezes:

  · "só 39 estão abaixo de 4,0 — **12,7%**, metade da taxa da base"  (bloco 7)
  · "as quatro primeiras ficam entre **4,02 e 4,14** de nota corrigida"  (bloco 6)
  · "declaro as duas porque a diferença é de **14%**"  (bloco 5)

O primeiro era verdadeiro e só não estava registrado — hoje está, e continua no vídeo. Os
outros dois saíram. A lição não é que faltou atenção: é que **conferência que depende de
atenção falha**. Este script faz a conferência.

O QUE ELE CONFERE
-----------------
1. **Amarração.** Todo token com dígito na coluna "O que é dito" existe nas colunas `valor`
   ou `n` de `tab_roteiro_numeros.csv`, comparado por valor numérico — a tabela guarda
   `p 2,4e-01` e a fala diz `0,24`. Só essas duas colunas: a primeira versão conferia o CSV
   inteiro, e o texto das colunas `indicador` e `regra` (T2, ML4, L5, QA3...) fazia qualquer
   "5" ou "4" passar como amarrado.
2. **Nenhum segmento descartado em silêncio.** Toda linha de tempo precisa ter fala entre
   aspas. Antes, uma célula sem aspas ou com aspas fora do padrão sumia da conferência e o
   script dizia OK sobre um roteiro que ele não leu.
3. **Ritmo, em duas medidas, total e por bloco.**
   · *palavras por segundo* — a contagem simples;
   · *palavras faladas por segundo* — com cada numeral lido por extenso. "1.348" são **seis**
     palavras ("mil trezentos e quarenta e oito"), não uma. A contagem simples subestimava
     justamente os blocos mais carregados de número: o roteiro tinha 2,46 p/s por ela e
     ≈ 2,9 pela segunda, e o bloco 5 chegava a 3,3.
   A segunda é uma **estimativa** — o conversor é aproximado — e só serve para não deixar um
   bloco denso passar por leve. **A leitura em voz alta, cronometrada, é a única medição que vale.**

O QUE ELE NÃO CONFERE, E POR QUÊ
--------------------------------
· **Número escrito em palavra** ("quatro arquétipos", "vinte e oito vezes"). Não é a classe
  de risco: quem escreve "vinte e oito" repete um número que já defendeu. Os três defeitos
  reais eram todos em dígito.
· **O sinal falado.** Se a fala diz "mais 0,150" onde a tabela guarda −0,150, passa: a
  comparação é por valor absoluto.
· **A coluna da tela.** Ela carrega rótulo de eixo, nome de arquivo e seção de relatório;
  conferi-la aqui acusaria `fig05` e `§7.7` como números soltos. A tela é conferida no
  checklist de gravação, com a figura na frente.

As isenções estão em `ISENTOS`, uma a uma, com o motivo escrito. Lista de isenção é onde uma
trava morre: se ela crescer, a trava virou enfeite.

Uso:  python3 04_video/confere_amarracao.py
      python3 04_video/confere_amarracao.py --planta           # número inventado: tem de reprovar
      python3 04_video/confere_amarracao.py --planta-ritmo     # bloco denso demais: tem de reprovar
      python3 04_video/confere_amarracao.py <outro_roteiro.md> # confere uma versão antiga
"""

import csv
import os
import re
import sys

PASTA = os.path.dirname(os.path.abspath(__file__))
TABELA = os.path.join(PASTA, "tab_roteiro_numeros.csv")
# Aceita um roteiro por argumento para que a prova desta trava seja reproduzível:
# `git show <commit>:04_video/roteiro.md` e rode contra a versão antiga.
_arg = [a for a in sys.argv[1:] if not a.startswith("--")]
ROTEIRO = _arg[0] if _arg else os.path.join(PASTA, "roteiro.md")

# Tetos de ritmo. Total: faixa de apresentação executiva em português. Por bloco: folga para
# a variação natural entre trechos, não para um bloco inteiro denso. Os de "faladas" valem
# ≈ 180 palavras por minuto no total.
TETO_TOTAL = 2.6
TETO_BLOCO = 2.7
TETO_FALADO_TOTAL = 3.0
TETO_FALADO_BLOCO = 3.15
TOLERANCIA = 1e-6

# Valor isento -> motivo. Não é "número que eu não quis registrar": é número que não
# é medição, e portanto não tem base nem n para declarar.
ISENTOS = {
    4.0: "limiar de satisfação — definição do projeto (T1), não medição",
    4.3: "corte de satisfação alta — definição do projeto, não medição",
    80.0: "os 80% são a definição do Pareto; o que é medido são os 306 produtos",
    3.0: "verbalização de p = 3,1e-08: 'três vezes dez elevado a menos oito'",
    10.0: "a base dez da mesma verbalização de p",
    8.0: "o expoente da mesma verbalização de p (e o máximo de avaliações, já na tabela)",
    5.0: "exemplo ilustrativo de Wilson: 'um produto com cinco avaliações'",
}

NUMERO = re.compile(r"\d[\d.,]*")
UNIDADES = ("zero um dois três quatro cinco seis sete oito nove dez onze doze treze quatorze "
            "quinze dezesseis dezessete dezoito dezenove").split()


def valores(texto):
    """Números pt-BR de um texto, como float. '1.348' -> 1348.0 · '52,4' -> 52.4."""
    saida = set()
    for cru in NUMERO.findall(texto):
        t = cru.rstrip(".,")
        if not t:
            continue
        try:
            saida.add(float(t.replace(".", "").replace(",", ".") if "," in t
                            else t.replace(".", "")))
        except ValueError:
            pass
    return saida


def valores_tabela():
    """O que a tabela afirma: colunas `valor` e `n`, incluindo o decimal por trás de `2,4e-01`."""
    saida = set()
    with open(TABELA, encoding="utf-8", newline="") as f:
        for linha in csv.DictReader(f):
            for campo in (linha["valor"], linha["n"]):
                saida |= valores(campo)
                for mantissa, expo in re.findall(r"(\d[\d,]*)e([+-]\d+)", campo):
                    saida.add(float(mantissa.replace(",", ".")) * 10 ** int(expo))
    return saida


def palavras_do_inteiro(n):
    """Quantas palavras tem o inteiro n lido em português: 348 -> 'trezentos e quarenta e oito' = 5."""
    if n < 20:
        return 1
    if n < 100:
        return 1 if n % 10 == 0 else 3
    if n < 1000:
        resto = n % 100
        return 1 if resto == 0 else 2 + palavras_do_inteiro(resto)
    mil, resto = divmod(n, 1000)
    p = 1 if mil == 1 else palavras_do_inteiro(mil) + 1
    if resto:
        p += (1 if resto < 100 or resto % 100 == 0 else 0) + palavras_do_inteiro(resto)
    return p


def palavras_do_token(tok):
    """Palavras faladas de um token numérico. '1.348' -> 6 · '52,4%' -> 8 · '3,1e-08' -> 6 (aprox.)."""
    pct = tok.endswith("%")
    t = tok.rstrip("%.,")
    if re.search(r"e[+-]", t):
        return 6
    try:
        if "," in t:
            inteiro, dec = t.split(",")
            p = palavras_do_inteiro(int(inteiro.replace(".", "") or 0)) + 1
            p += palavras_do_inteiro(int(dec)) if dec.strip("0") else len(dec)
        else:
            p = palavras_do_inteiro(int(t.replace(".", "")))
    except ValueError:
        return 1
    return p + (2 if pct else 0)          # "por cento"


def palavras_faladas(fala):
    total = 0
    for palavra in fala.split():
        if re.search(r"\d", palavra):
            total += sum(palavras_do_token(t) for t in re.findall(r"\d[\d.,]*%?", palavra))
        else:
            total += 1
    return total


# autoconferência do conversor: valores que se sabem de cabeça, para que um erro no
# próprio conversor não passe por rigor
assert palavras_do_inteiro(1348) == 6        # mil trezentos e quarenta e oito
assert palavras_do_inteiro(4740) == 5        # quatro mil setecentos e quarenta
assert palavras_do_inteiro(36384) == 9       # trinta e seis mil trezentos e oitenta e quatro
assert palavras_do_inteiro(13120) == 5       # treze mil cento e vinte


def fala_do_roteiro():
    """[(bloco, inicio, fim, segundos, texto_falado), ...] — só o que é dito."""
    texto = open(ROTEIRO, encoding="utf-8").read()
    saida = []
    for secao in re.split(r"\n(?=## )", texto):
        cab = secao.split("\n", 1)[0]
        m = re.search(r"^## (.+?) — (\d+:\d\d) a (\d+:\d\d)", cab)
        if not m:
            continue
        bloco = re.sub(r"\s+·\s+\*\*.*$", "", m.group(1)).strip()
        for linha in secao.split("\n"):
            if not linha.startswith("|"):
                continue
            c = [x.strip() for x in re.split(r"(?<!\\)\|", linha.strip().strip("|"))]
            t = re.match(r"\*{0,2}(\d+:\d\d)[–-](\d+:\d\d)\*{0,2}$", c[0]) if c else None
            if t and len(c) >= 3:
                dito = " ".join(re.findall(r"[“\"]([^“”\"]+)[”\"]", c[1]))
                ini, fim = (int(x.split(":")[0]) * 60 + int(x.split(":")[1])
                            for x in (t.group(1), t.group(2)))
                saida.append((bloco, t.group(1), t.group(2), fim - ini, dito))
    return saida


def main(plantar=None):
    tabela = valores_tabela()
    segmentos = fala_do_roteiro()
    assert segmentos, "nenhum segmento de fala encontrado no roteiro"
    if plantar == "numero":
        bloco, ini, fim, dur, dito = segmentos[0]
        segmentos[0] = (bloco, ini, fim, dur, dito + " E a margem foi de 73,4%.")
        print("PLANTA: '73,4%' injetado na fala do primeiro segmento\n")
    if plantar == "ritmo":
        bloco, ini, fim, dur, dito = segmentos[0]
        segmentos[0] = (bloco, ini, fim, dur, dito + " palavra" * 30)
        print("PLANTA: 30 palavras de enchimento no primeiro segmento\n")

    erros = []
    soltos, vazios = [], []
    por_bloco = {}                                   # bloco -> [palavras, faladas, segundos]
    for bloco, ini, fim, dur, dito in segmentos:
        if not dito.strip():
            vazios.append((bloco, ini, fim))
            continue
        acc = por_bloco.setdefault(bloco, [0, 0, 0])
        acc[0] += len(dito.split())
        acc[1] += palavras_faladas(dito)
        acc[2] += dur
        for v in valores(dito):
            if any(abs(v - t) < TOLERANCIA for t in tabela) or v in ISENTOS:
                continue
            soltos.append((bloco, ini, fim, v))

    palavras = sum(a[0] for a in por_bloco.values())
    faladas = sum(a[1] for a in por_bloco.values())
    segundos = sum(a[2] for a in por_bloco.values())
    print(f"Fala: {palavras} palavras em {segundos} s = {palavras / segundos:.2f} p/s (teto {TETO_TOTAL})")
    print(f"      lendo os numerais por extenso: ≈ {faladas} palavras = {faladas / segundos:.2f} p/s (teto {TETO_FALADO_TOTAL})")
    print(f"Tabela de amarração: {len(tabela)} valores distintos (colunas valor e n)")
    print(f"Isenções declaradas: {len(ISENTOS)}")
    for bloco, (p, f, sec) in por_bloco.items():
        marca = "  ◄ passa do teto" if p / sec > TETO_BLOCO or f / sec > TETO_FALADO_BLOCO else ""
        print(f"  {bloco[:40]:<42}{p / sec:>5.2f} → {f / sec:>5.2f} p/s{marca}")

    if palavras / segundos > TETO_TOTAL:
        erros.append(f"ritmo total {palavras / segundos:.2f} p/s acima do teto de {TETO_TOTAL}")
    if faladas / segundos > TETO_FALADO_TOTAL:
        erros.append(f"ritmo total lendo numerais {faladas / segundos:.2f} p/s acima do teto de {TETO_FALADO_TOTAL}")
    for bloco, (p, f, sec) in por_bloco.items():
        if p / sec > TETO_BLOCO:
            erros.append(f"bloco '{bloco}': {p / sec:.2f} p/s acima do teto por bloco de {TETO_BLOCO}")
        if f / sec > TETO_FALADO_BLOCO:
            erros.append(f"bloco '{bloco}': {f / sec:.2f} p/s lendo numerais, acima do teto por bloco de {TETO_FALADO_BLOCO}")
    for bloco, ini, fim in vazios:
        erros.append(f"segmento {ini}–{fim} ({bloco}) não tem fala entre aspas — não foi conferido")
    for bloco, ini, fim, v in soltos:
        erros.append(f"número sem amarração: {v:g} — falado em {ini}–{fim} ({bloco})")

    if erros:
        print("\nREPROVADO:")
        for e in erros:
            print(f"  - {e}")
        print("\nUm número falado sem linha em tab_roteiro_numeros.csv é afirmação "
              "pública sem lastro. Registre-o em numeros_roteiro.py ou tire-o da fala.")
        return 1
    print("\nOK — todo número falado tem linha na tabela, e o ritmo cabe nos tetos, no total e por bloco.")
    return 0


if __name__ == "__main__":
    plantar = "numero" if "--planta" in sys.argv else ("ritmo" if "--planta-ritmo" in sys.argv else None)
    codigo = main(plantar)
    if plantar:
        print("\n" + ("OK — a trava reprovou a planta." if codigo
                      else "ERRO — a trava deixou passar a planta."))
        sys.exit(0 if codigo else 1)
    sys.exit(codigo)

# -*- coding: utf-8 -*-
"""
Prova de que gera_resumo.py falha quando deve — e só quando deve.

As duas travas do gerador — "o sumário não afirma número que o corpo do
relatório não sustenta" e "todo número falado no vídeo está no relatório" — só
valem se reprovarem um número ERRADO. Este script copia o relatório e a tabela
de números do roteiro para uma pasta temporária, planta um número errado por
vez e exige que o gerador falhe; e roda o gerador sobre as cópias intactas,
exigindo que passe. Não toca no projeto.

Os plantios do sumário mudam o número SÓ no trecho do resumo, mantendo o corpo:
é exatamente a divergência resumo × corpo que a trava existe para pegar.

Uso: python src/testa_gera_resumo.py
"""

import csv
import os
import shutil
import subprocess
import sys
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GERADOR = os.path.join(RAIZ, "src", "gera_resumo.py")
RELATORIO = os.path.join(RAIZ, "docs", "relatorio_tecnico.md")
ROTEIRO = os.path.join(RAIZ, "04_video", "tab_roteiro_numeros.csv")
RESUMO = ("## Resumo Executivo", "## Artefatos e Links do Projeto")
RECOMENDACOES = ("## Recomendações para o Negócio", "## Referências")

# (descrição, trecho do relatório, texto certo, texto errado)
NO_SUMARIO = [
    ("fila de 19 → 21", RESUMO, "uma fila de 19 produtos", "uma fila de 21 produtos"),
    ("61 acionáveis → 62", RESUMO, "**61** depois da correção", "**62** depois da correção"),
    ("39 do Pareto → 41", RESUMO, "apenas **39 (12,7%)**", "apenas **41 (12,7%)**"),
    ("339 abaixo de 4,0 → 349", RESUMO, "(339 produtos, 25,1%)", "(349 produtos, 25,1%)"),
    ("25,1% → 26,1%", RESUMO, "(339 produtos, 25,1%)", "(339 produtos, 26,1%)"),
    ("Electronics 490 → 409", RECOMENDACOES, "Electronics (490)", "Electronics (409)"),
    ("desconto de B 58% → 85%", RESUMO, "idêntico: **58% e 61%**", "idêntico: **85% e 61%**"),
    ("58% e 61% → 57% e 62%", RESUMO, "idêntico: **58% e 61%**", "idêntico: **57% e 62%**"),
    ("nota de B 3,9 → 3,8", RESUMO, "(3,9 contra 4,2 dos demais)", "(3,8 contra 4,2 dos demais)"),
    ("truncamento 8 → 9", RESUMO, "no máximo 8 por produto", "no máximo 9 por produto"),
    ("p 3,1 → 3,0 × 10⁻⁸", RESUMO, "p = 3,1 × 10⁻⁸", "p = 3,0 × 10⁻⁸"),
    ("p 3,1 → 3,2 × 10⁻⁸", RESUMO, "p = 3,1 × 10⁻⁸", "p = 3,2 × 10⁻⁸"),
    ("expoente 10⁻⁸ → 10⁻⁹", RESUMO, "p = 3,1 × 10⁻⁸", "p = 3,1 × 10⁻⁹"),
    ("Pareto 306 → 316", RESUMO, "**306 produtos (22,7%)**", "**316 produtos (22,7%)**"),
    ("ρ −0,150 → −0,160", RESUMO, "**ρ = −0,150**", "**ρ = −0,160**"),
    ("ρ −0,150 → +0,150", RESUMO, "**ρ = −0,150**", "**ρ = +0,150**"),
    ("grupo B 335 → 336", RESUMO, "**B** (335 produtos)", "**B** (336 produtos)"),
    ("13.120 → 13.210", RESUMO, "**13.120 avaliações medianas**", "**13.210 avaliações medianas**"),
    ("782 → 728", RESUMO, "782 produtos", "728 produtos"),
    ("p 0,236 → 0,226", RESUMO, "(ρ = +0,032, p = 0,236)", "(ρ = +0,032, p = 0,226)"),
    ("Âncora 41 → 42", RESUMO, "**Âncora 41**", "**Âncora 42**"),
    ("funil 187 → 188", RECOMENDACOES, "devolve 187 candidatos", "devolve 188 candidatos"),
]

# (descrição, indicador, campo, valor errado)
NO_ROTEIRO = [
    ("categorias acima do piso 4 → 5", "categorias com n >= 30 (T2)", "valor", "5"),
    ("Q5 19 → 21", "Q5 — engajamento alto e nota < 4,0", "valor", "21"),
    ("Q6 acionável 61 → 62", "Q6 — lista acionável: funil já corrigido por Wilson", "valor", "62"),
    ("subcategorias 8 → 7", "subcategorias de nível 2 com n >= 30", "valor", "7"),
    ("desconto mediano 49% → 50%", "desconto mediano", "valor", "50%"),
    ("distância B × D 3 → 5 p.p.", "conflito B × D — distância de desconto", "valor", "5 p.p."),
    ("razão B × D 28x → 29x", "conflito B × D — razão de volume de avaliações", "valor", "29x"),
    ("28x com número estranho", "conflito B × D — razão de volume de avaliações", "valor", "28x · 987.654"),
    ("silhueta k=3 0,215 → 0,218", "silhueta k=3", "valor", "0,218"),
    ("fones 52,4% → 32,2%", "fones — produtos abaixo de 4,0", "valor", "32,2%"),
    ("nota do arquétipo A 4,2 → 4,1", "arquétipo A — n · desconto · avaliações · nota", "valor", "268 · 32% · 6.836 · 4,1"),
    ("p 3,1e-08 → 3,0e-08", "Spearman desconto × nota", "valor", "rho -0,150 · p 3,0e-08"),
    ("p 2,4e-01 → 2,3e-01", "Spearman preço de tabela × nota", "valor", "rho +0,032 · p 2,3e-01"),
    ("p 1,1e-06 → 1,15e-06", "Spearman desconto × engajamento", "valor", "rho -0,132 · p 1,15e-06"),
    ("n dos fones 63 → 36", "fones — produtos abaixo de 4,0", "n", "36"),
    ("n da faixa 0–20% 175 → 157", "faixa de desconto com maior nota corrigida (QA1)", "n", "157"),
    ("base Analítica → Bruta", "produtos na base analítica", "base", "Bruta"),
    ("n 1348 → 1300 numa linha da base inteira", "nota mediana", "n", "1300"),
]


def roda(pasta):
    ambiente = dict(os.environ, RESUMO_RELATORIO=os.path.join(pasta, "relatorio.md"),
                    RESUMO_ROTEIRO=os.path.join(pasta, "roteiro.csv"), RESUMO_SAIDA=pasta)
    return subprocess.run([sys.executable, GERADOR], capture_output=True, text=True, env=ambiente).returncode


def planta_relatorio(pasta, trecho, certo, errado):
    texto = open(RELATORIO, encoding="utf-8").read()
    i, j = texto.index(trecho[0]), texto.index(trecho[1])
    regiao = texto[i:j]
    assert certo in regiao, f"o texto certo não está no trecho: {certo}"
    open(os.path.join(pasta, "relatorio.md"), "w", encoding="utf-8").write(
        texto[:i] + regiao.replace(certo, errado, 1) + texto[j:])
    shutil.copy(ROTEIRO, os.path.join(pasta, "roteiro.csv"))


def planta_roteiro(pasta, indicador, campo, errado):
    linhas = list(csv.DictReader(open(ROTEIRO, encoding="utf-8")))
    alvo = [r for r in linhas if r["indicador"] == indicador]
    assert len(alvo) == 1, f"indicador não encontrado: {indicador}"
    alvo[0][campo] = errado
    with open(os.path.join(pasta, "roteiro.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(linhas[0]))
        w.writeheader()
        w.writerows(linhas)
    shutil.copy(RELATORIO, os.path.join(pasta, "relatorio.md"))


resultados = []
with tempfile.TemporaryDirectory() as tmp:
    shutil.copy(RELATORIO, os.path.join(tmp, "relatorio.md"))
    shutil.copy(ROTEIRO, os.path.join(tmp, "roteiro.csv"))
    resultados.append(("relatório e roteiro intactos", roda(tmp), 0))
    for desc, trecho, certo, errado in NO_SUMARIO:
        planta_relatorio(tmp, trecho, certo, errado)
        resultados.append((f"sumário · {desc}", roda(tmp), 1))
    for desc, indicador, campo, errado in NO_ROTEIRO:
        planta_roteiro(tmp, indicador, campo, errado)
        resultados.append((f"roteiro · {desc}", roda(tmp), 1))

erros = 0
for nome, obtido, esperado in resultados:
    ok = (obtido == 0) == (esperado == 0)
    erros += not ok
    print(f"{'OK' if ok else 'ERRO':4s} | {'passa  ' if esperado == 0 else 'reprova'} · {nome}"
          + ("" if ok else f" — saída {obtido}, esperada {'0' if esperado == 0 else '≠ 0'}"))
print(f"\n{len(resultados)} casos · {erros} errados")
sys.exit(1 if erros else 0)

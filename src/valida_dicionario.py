# -*- coding: utf-8 -*-
"""
Validação do DICIONÁRIO DE DADOS contra os artefatos reais — 01/10/2026.

POR QUE ESTE SCRIPT EXISTE
--------------------------
O dicionário descrevia seis campos derivados com nomes que o pipeline havia
abandonado: `desconto_recalculado`, `engajamento_alto`, `visibilidade_baixa`,
`satisfacao_baixa` e `subcategoria` não existiam em nenhum arquivo, e três
colunas que existem de verdade — `q5_risco_vitrine`, `faixa_desconto` e
`pareto_80` — não estavam documentadas. A divergência passou por três revisões
porque ninguém cruza um .md com um .csv a olho.

Este script cruza. Ele é deliberadamente separado de `valida_base.py`: aquele
verifica NÚMEROS e tem 107 asserções citadas em dez arquivos; este verifica
NOMES DE COLUNA, e misturar os dois obrigaria a atualizar aquela contagem a
cada mudança de esquema.

O QUE VERIFICA
--------------
1. Toda coluna que o dicionário declara existe no artefato em que ele a coloca.
2. Toda coluna que existe nos artefatos está documentada no dicionário.
3. As contagens de coluna por artefato (§3) conferem com os arquivos.
4. Nenhum arquivo versionado contém `user_id` ou `user_name` (T7).

Entrada : method/definitions/dicionario_de_dados.md + 00_data/
Saída   : relatório no console + código 0 (não há divergência) ou 1 (há)
Uso     : python src/valida_dicionario.py

Dependência: pandas.
"""

import os
import re
import sys
import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DICIONARIO = os.path.join(RAIZ, "method", "definitions", "dicionario_de_dados.md")

# Os artefatos que o dicionário §3 descreve. A CONTAGEM de colunas de cada um
# NÃO está aqui de propósito: ela é lida do próprio dicionário, para que o
# script verifique o que o documento afirma e não uma constante sua. Uma
# contagem escrita errada no .md tem de derrubar este validador.
ARTEFATOS = (
    "00_data/silver/produtos.csv",
    "00_data/silver/produtos_texto.csv",
    "00_data/gold/base_analitica.csv",
    "00_data/gold/reviews.csv",
)
PESSOAIS = ("user_id", "user_name")

falhas, avisos = [], []


def confere(descricao, obtido, esperado):
    ok = obtido == esperado
    marca = "OK  " if ok else "FALHA"
    print(f"{marca} | {descricao} obtido={obtido} esperado={esperado}")
    if not ok:
        falhas.append(f"{descricao}: obtido {obtido}, esperado {esperado}")


def secao(titulo):
    print(f"\n--- {titulo} " + "-" * max(0, 68 - len(titulo)))


# ---------------------------------------------------------------------------
if not os.path.exists(DICIONARIO):
    print(f"ERRO: dicionário não encontrado em {DICIONARIO}")
    sys.exit(1)

texto = open(DICIONARIO, encoding="utf-8").read()

# Colunas reais, por artefato
reais = {}
for rel in ARTEFATOS:
    caminho = os.path.join(RAIZ, rel)
    if not os.path.exists(caminho):
        print(f"ERRO: artefato ausente — {rel}. Rode src/prepara_dados.py primeiro.")
        sys.exit(1)
    reais[rel] = list(pd.read_csv(caminho, nrows=0).columns)

todas_reais = {c for cols in reais.values() for c in cols}

# ---------------------------------------------------------------------------
secao("1. CONTAGEM DE COLUNAS POR ARTEFATO (lida do dicionário §3)")
bloco3_pre = texto.split("## 3. Onde cada coluna vive")[1].split("## 4.")[0]
for rel in ARTEFATOS:
    linha = next((linha_ for linha_ in bloco3_pre.splitlines() if linha_.startswith("|") and rel in linha_), None)
    if linha is None:
        confere(f"{rel} descrita em §3", False, True)
        continue
    m = re.search(r"\*\*(\d+)\*\*", linha)
    if not m:
        confere(f"{rel}: §3 declara uma contagem de colunas", False, True)
        continue
    confere(f"{rel} (§3 declara {m.group(1)})", len(reais[rel]), int(m.group(1)))

# ---------------------------------------------------------------------------
# A leitura do dicionário é ESTRUTURAL, não por varredura de crases: só contam
# as posições em que um nome de coluna pode estar — a 1ª e a 2ª célula das
# tabelas de §1 e §2, e as listas de coluna de §3. Varrer todas as crases do
# arquivo produziria falso positivo em `alto`, `baixa`, `media` e nos demais
# VALORES de coluna categórica, que também aparecem em crase e não são colunas.
def celulas_de(bloco, indice):
    """Nomes em crase na n-ésima célula de cada linha de tabela do bloco."""
    achados = []
    for linha in bloco.splitlines():
        if not linha.startswith("|") or set(linha) <= set("|- "):
            continue
        partes = [c.strip() for c in linha.strip().strip("|").split("|")]
        if len(partes) > indice:
            achados += re.findall(r"`([a-z][a-z_0-9]*)`", partes[indice])
    return achados


bloco1 = texto.split("## 1. Colunas da origem")[1].split("## 2.")[0]
bloco2 = texto.split("## 2. Campos derivados")[1].split("## 3.")[0]
bloco3 = texto.split("## 3. Onde cada coluna vive")[1].split("## 4.")[0]

origem_decl = celulas_de(bloco1, 0)      # nome na origem
tratado_decl = celulas_de(bloco1, 1)     # nome no pipeline
derivados = celulas_de(bloco2, 0)        # campos derivados
por_artefato = {}                        # §3 — colunas listadas por arquivo
for linha in bloco3.splitlines():
    if not linha.startswith("|"):
        continue
    for rel in ARTEFATOS:
        if rel in linha:
            por_artefato[rel] = re.findall(r"`([a-z][a-z_0-9]*)`", linha)

secao("2. CAMPOS DERIVADOS DECLARADOS (§2) EXISTEM NA GOLD")
print(f"     ({len(derivados)} campos derivados declarados no dicionário)")
gold = reais["00_data/gold/base_analitica.csv"]
for campo in derivados:
    confere(f"`{campo}` existe na gold", campo in gold, True)

# ---------------------------------------------------------------------------
secao("3. §3 LISTA EXATAMENTE AS COLUNAS QUE O ARQUIVO TEM")
for rel, cols in reais.items():
    listadas = por_artefato.get(rel)
    if listadas is None:
        confere(f"{os.path.basename(rel)} listada em §3", False, True)
        continue
    # a gold é descrita por referência a §2 ("as 8 estruturadas + as 9 derivadas")
    if rel == "00_data/gold/base_analitica.csv":
        esperadas = set(tratado_decl) | set(derivados)
        confere("gold: toda coluna real é declarada em §1 ou §2",
                sorted(c for c in cols if c not in esperadas), [])
        continue
    confere(f"{os.path.basename(rel)}: colunas de §3 == colunas do arquivo",
            sorted(listadas), sorted(cols))

# ---------------------------------------------------------------------------
secao("4. NENHUM NOME FANTASMA EM POSIÇÃO DE COLUNA")
declarados = set(tratado_decl) | set(derivados)
for cols in por_artefato.values():
    declarados |= set(cols)
fantasmas = sorted(c for c in declarados if c not in todas_reais)
confere("nomes declarados como coluna e inexistentes", fantasmas, [])

secao("4b. TODA COLUNA DA ORIGEM APARECE EM §1")
bronze_esperado = {"product_id", "product_name", "category", "discounted_price",
                   "actual_price", "discount_percentage", "rating", "rating_count",
                   "about_product", "user_id", "user_name", "review_id",
                   "review_title", "review_content", "img_link", "product_link"}
confere("as 16 colunas da origem estão documentadas",
        sorted(bronze_esperado - set(origem_decl)), [])

# ---------------------------------------------------------------------------
secao("5. CONFORMIDADE T7 — DADO PESSOAL FORA DOS ARTEFATOS")
for rel, cols in reais.items():
    vazou = [c for c in PESSOAIS if c in cols]
    confere(f"{os.path.basename(rel)} sem coluna pessoal", vazou, [])

# ---------------------------------------------------------------------------
print("\n" + "=" * 78)
if falhas:
    print(f"DIVERGÊNCIAS ENTRE O DICIONÁRIO E OS DADOS: {len(falhas)}")
    for f in falhas:
        print(f"  - {f}")
    print("\nO dicionário descreve algo que os dados não têm — ou o contrário.")
    sys.exit(1)
print("Dicionário e artefatos conferem coluna a coluna. Nenhuma divergência.")
sys.exit(0)

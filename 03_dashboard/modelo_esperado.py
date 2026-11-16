# -*- coding: utf-8 -*-
"""
O modelo do .pbix, como ele TEM de ser — em um lugar só.

Lido por gera_modelo_de_dados.py (que desenha o diagrama) e por
verifica_pbix.py (que confere o arquivo entregue). Antes, o diagrama declarava
as colunas derivadas e o verificador precisaria declará-las de novo: duas
listas do mesmo fato, que é a classe de divergência que o projeto combate.

O que vem de arquivo é LIDO aqui (colunas da gold, cabeçalhos das tabelas de
resultado, nomes DAX do catálogo). O que só existe dentro do .pbix é DECLARADO
e conferido contra a fonte que o define: as colunas derivadas contra os passos
9 e 10 do guia de montagem; as medidas contra medidas_dax.md.
"""

import os
import re

import pandas as pd

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PASTA = os.path.join(RAIZ, "03_dashboard")
GOLD = os.path.join(RAIZ, "00_data", "gold")
TABELAS = os.path.join(RAIZ, "02_results", "tables")
GUIA = os.path.join(PASTA, "INSTRUCOES_MONTAGEM_POWERBI.md")
CATALOGO = os.path.join(PASTA, "medidas_dax.md")
CONFERENCIA_CSV = os.path.join(PASTA, "conferencia_referencia.csv")
CONFERENCIA_MD = os.path.join(PASTA, "conferencia_dax.md")

# Nomes das tabelas NO MODELO — são os que medidas_dax.md referencia.
BASE, REVIEWS = "BaseAnalitica", "Reviews"
CONFERENCIA, MEDIDAS = "Conferencia", "_Medidas"

# Colunas que a gold não tem, e de onde vêm. As derivadas só existem no .pbix.
DERIVADAS = [
    ("relevancia", "texto", "Power Query · passo 9"),
    ("n_referencias", "inteiro", "Power Query · passo 9"),
    ("faixa_ordem", "inteiro", "Power Query · passo 9"),
    ("engaj_ordem", "inteiro", "Power Query · passo 9"),
    ("satisf_ordem", "inteiro", "Power Query · passo 9"),
    ("pareto_posicao", "inteiro", "Power Query · passo 10"),
    ("pareto_acumulado_pct", "decimal", "Power Query · passo 10"),
]
MESCLADAS = {"arquetipo": "via tab22"}
ORIGEM = {nome: origem for nome, _, origem in DERIVADAS} | MESCLADAS

# Tabelas de resultado: o arquivo e o uso são especificação da montagem
# (seção 6 do guia); linhas e colunas são lidas do arquivo.
RESULTADO = [
    ("tab03", "tab03_correlacoes.csv", "página 3", "Spearman · Q3 e QA4"),
    ("tab05", "tab05_arquetipos.csv", "gabarito da 2c", "perfil dos arquétipos · QA7"),
    ("tab07", "tab07_ml2_blocos.csv", "página 5", "AUC por bloco · Q8"),
    ("tab14", "tab14_ngramas.csv", "página 4", "n-gramas e TF-IDF"),
    ("tab23", "tab23_qa5_temas.csv", "página 4", "eixos da QA5 · 19 blocos"),
]

# T7 e escopo: colunas que não podem existir em tabela nenhuma do modelo. O nome
# é normalizado (minúsculas, último segmento depois de ".", sem espaços) e
# casado por FRAGMENTO — "User_Name", "gold.user_name" e "username" caem todos.
FRAGMENTOS_PROIBIDOS = {
    "user": "dado pessoal (T7)",
    "review_content": "texto de avaliação — contém nome de consumidor (T7)",
    "review_title": "texto de avaliação — contém nome de consumidor (T7)",
    "about_product": "texto longo, fora do escopo do modelo",
    "_link": "sem uso analítico declarado",
}
PROIBIDAS = {
    "user_id": "dado pessoal (T7)",
    "user_name": "dado pessoal (T7)",
    "review_content": "texto de avaliação — contém nome de consumidor (T7)",
    "review_title": "texto de avaliação — contém nome de consumidor (T7)",
    "about_product": "texto longo, fora do escopo do modelo",
    "img_link": "sem uso analítico declarado",
    "product_link": "sem uso analítico declarado",
}

# As medidas da página de conferência (geradas por gera_conferencia.py).
MEDIDAS_CONFERENCIA = ["Conf · Valor DAX", "Conf · Esperado", "Conf · Diferença",
                       "Conf · Situação", "Conf · Divergentes", "Conf · Conferidas"]


# Tipos que o modelo precisa ter (TMSL dataType). Tipo errado não dá erro: dá
# número errado ou zero silencioso — booleano lido como texto zera M11–M13.
# Cada coluna aceita um conjunto de tipos. `desconto` aceita inteiro: a origem
# só traz percentuais redondos, e "Número inteiro" não muda nenhum número.
TIPOS = {
    BASE: {"q5_risco_vitrine": {"boolean"}, "q6_subexplorado": {"boolean"}, "pareto_80": {"boolean"},
           "avaliacoes": {"int64"}, "preco_desc": {"double"}, "preco_tab": {"double"},
           "desconto": {"double", "int64"}, "nota": {"double"}, "nota_corrigida": {"double"}},
    REVIEWS: {"nota": {"double"}},
    CONFERENCIA: {"valor_esperado": {"double"}, "tolerancia": {"double"}},
}
# A _Medidas pode ter UMA coluna de texto: a criada por "Inserir dados", cujo
# nome muda com o idioma do Desktop (Coluna1, Column1, Columna1, Spalte1…).
COLUNA_INSERIR_DADOS = re.compile(r"^\w+1$")


def normaliza_nome(nome):
    return str(nome).strip().split(".")[-1].replace(" ", "").casefold()


def normaliza_dax(expressao):
    """Expressão DAX comparável: sem comentários, sem espaço, sem caixa.

    O Power BI guarda o texto que foi digitado; o botão "Formatar DAX" muda só
    espaço e quebra de linha. Normalizado assim, o mesmo DAX dá o mesmo texto,
    e um ALL a menos dá texto diferente.
    """
    if isinstance(expressao, list):
        expressao = "\n".join(expressao)
    linhas = [linha_ for linha_ in str(expressao).split("\n") if not linha_.strip().startswith(("--", "//"))]
    return "".join("".join(linhas).split()).casefold()


def _blocos_dax(texto):
    """[(nome, expressão)] de cada bloco ```dax``` de um documento."""
    saida = []
    for bloco in re.findall(r"```dax\n(.*?)```", texto, flags=re.S):
        cabeca, _, corpo = bloco.strip().partition("\n")
        nome, _, resto = cabeca.partition("=")
        saida.append((nome.strip(), (resto.strip() + "\n" + corpo).strip()))
    return saida


def expressoes_catalogo():
    """{nome DAX: expressão} das 22 medidas — o primeiro bloco de cada seção M."""
    catalogo = open(CATALOGO, encoding="utf-8").read()
    saida = {}
    for secao in re.split(r"\n(?=## M\d)", catalogo)[1:]:
        nome, expr = _blocos_dax(secao)[0]
        saida[nome] = expr
    return saida


def expressoes_conferencia():
    """{nome: expressão} das medidas Conf, lidas de conferencia_dax.md."""
    return {n: e for n, e in _blocos_dax(open(CONFERENCIA_MD, encoding="utf-8").read())
            if n in MEDIDAS_CONFERENCIA}


def colunas_csv(caminho):
    return list(pd.read_csv(caminho, nrows=0).columns)


def conferir_derivadas_no_guia():
    """As derivadas precisam estar nos passos 9–10 do guia, com este nome exato."""
    guia = open(GUIA, encoding="utf-8").read()
    passos = guia[guia.index("\n9. "):guia.index("\n11. ")]
    ausentes = [n for n, _, _ in DERIVADAS if f"`{n}`" not in passos]
    assert not ausentes, f"colunas declaradas que o guia não cria nos passos 9–10: {ausentes}"


def nomes_dax():
    """{'M01': 'Produtos Ativos', ...} — a primeira expressão DAX de cada seção do catálogo."""
    catalogo = open(CATALOGO, encoding="utf-8").read()
    nomes = {}
    for secao in re.split(r"\n(?=## M\d)", catalogo)[1:]:
        cod = re.match(r"## (M\d+) ", secao).group(1)
        bloco = re.search(r"```dax\n(.*?)```", secao, flags=re.S)
        assert bloco, f"{cod} sem bloco DAX no catálogo"
        nomes[cod] = bloco.group(1).strip().split("\n")[0].rstrip(" =").strip()
    return nomes


def colunas_esperadas():
    """{tabela: [colunas]} do modelo carregado, sem a _Medidas (que não tem coluna)."""
    conferir_derivadas_no_guia()
    esperado = {
        BASE: colunas_csv(os.path.join(GOLD, "base_analitica.csv"))
              + [n for n, _, _ in DERIVADAS] + list(MESCLADAS),
        REVIEWS: colunas_csv(os.path.join(GOLD, "reviews.csv")),
        CONFERENCIA: colunas_csv(CONFERENCIA_CSV),
    }
    for nome, arquivo, _, _ in RESULTADO:
        esperado[nome] = colunas_csv(os.path.join(TABELAS, arquivo))
    return esperado

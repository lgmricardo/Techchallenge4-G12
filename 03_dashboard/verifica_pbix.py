# -*- coding: utf-8 -*-
"""
Conferência do arquivo entregue — o modelo dentro do .pbix é o modelo combinado?

POR QUE EXISTE
--------------
A revisão do .pbix era dividida entre quatro pessoas, nenhuma delas o montador.
Com uma pessoa só, quem monta é quem revisa, e a conferência que depende de
olhar é a primeira a falhar. Este script olha no lugar dela, e falha alto.

POR QUE LÊ O .pbit, E NÃO SÓ O .pbix
------------------------------------
Dentro do .pbix o modelo é gravado COMPRIMIDO. Procurar "user_name" nos bytes
do arquivo daria sempre "não encontrado" — um falso verde, que é pior do que
não ter a checagem. O modelo do Power BI (Arquivo > Exportar > Modelo do Power
BI) grava o MESMO esquema em texto: tabelas, colunas, tipos, relacionamentos e
a expressão de cada medida. É ele que este script lê.

E para que o .pbit não seja de outra versão, o .pbix entregue também é
passado. O script confere que ele é um .pbix de verdade, que o relatório é o
mesmo, que as consultas do Power Query são as mesmas — o código M e as chaves
de carga de cada consulta, decodificados do DataMashup (MS-QDEFF), porque os
bytes crus trazem um trecho cifrado com sal aleatório que muda a cada
gravação —, e que o .pbix não foi salvo depois da exportação. O que sobra sem
cobertura é mudança feita só no modelo e exportada sem salvar o .pbix; por
isso a regra é: salvar, e só então exportar.

O QUE CONFERE (cada linha falha por si)
--------------------------------------
1. T7 · nenhuma coluna pessoal ou de texto de avaliação em tabela nenhuma —
   pelo nome normalizado e por fragmento ("User_Name", "gold.user_name").
2. As tabelas carregadas são exatamente as do modelo combinado.
3. Colunas, tipos e origem: cada tabela com as colunas da especificação, as
   colunas-chave com o tipo certo, nenhuma coluna ou tabela calculada em DAX
   onde a preparação é do Power Query, e a _Medidas sem coluna de dado.
4. Exatamente UM relacionamento, BaseAnalitica[product_id] 1 → N
   Reviews[product_id], ativo, unidirecional e com essa cardinalidade.
5. As 22 medidas do catálogo e as 6 de conferência, com o nome exato e com a
   MESMA EXPRESSÃO do documento — um ALL a menos, um ALLSELECTED no lugar de
   ALL, reprova aqui, porque a página de conferência não enxerga isso.
6. A página "Conferência" existe e está oculta.
7. Com o .pbix: é o .pbix do qual o .pbit foi exportado.

Uso, da raiz do projeto:
    python 03_dashboard/verifica_pbix.py 03_dashboard/TechChallenge4_G12.pbit [03_dashboard/TechChallenge4_G12.pbix]
Saída 0 só se nenhuma linha falhar.
"""

import io
import json
import os
import struct
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import modelo_esperado as M  # noqa: E402

FALHAS, AVISOS = [], []
# Partes do relatório, que precisam ser iguais nos dois arquivos.
PARTES_RELATORIO = "Report/"
# Estado de navegação gravado no relatório: muda sem mudar o arquivo.
CHAVES_VOLATEIS = {"activeSectionIndex", "activePageName"}
# Folga entre salvar o .pbix e exportar o .pbit (relógio de arquivo; um clone
# do git grava os dois quase no mesmo instante).
FOLGA_SEGUNDOS = 60
# .pbix muito mais velho que o .pbit: o modelo pode ter mudado sem ser salvo.
ATRASO_SUSPEITO = 600


def linha(situacao, rotulo, detalhe=""):
    print(f"{situacao:5s}| {rotulo}" + (f" — {detalhe}" if detalhe else ""))
    if situacao == "FALHA":
        FALHAS.append(rotulo)
    elif situacao == "AVISO":
        AVISOS.append(rotulo)


def confere(rotulo, ok, detalhe=""):
    linha("OK" if ok else "FALHA", rotulo, "" if ok else detalhe)


def texto(dados):
    """As partes JSON do Power BI vêm em UTF-16 (com ou sem BOM) ou UTF-8."""
    if dados[:2] in (b"\xff\xfe", b"\xfe\xff"):
        return dados.decode("utf-16")
    if len(dados) > 1 and dados[1:2] == b"\x00":
        return dados.decode("utf-16-le")
    return dados.decode("utf-8-sig")


def abre(caminho, extensao, deve_ter, nao_deve_ter):
    if not caminho.lower().endswith(extensao):
        sys.exit(f"ERRO: {caminho} não termina em {extensao}.")
    try:
        zf = zipfile.ZipFile(caminho)
    except (FileNotFoundError, zipfile.BadZipFile) as erro:
        sys.exit(f"ERRO: não foi possível abrir {caminho}: {erro}")
    nomes = set(zf.namelist())
    if deve_ter not in nomes or nao_deve_ter in nomes:
        sys.exit(f"ERRO: {caminho} não tem a estrutura de um {extensao} do Power BI Desktop "
                 f"(precisa ter {deve_ter} e não ter {nao_deve_ter}).")
    return zf


def colunas_de(tabela):
    # A coluna interna de número de linha não é coluna do modelo.
    return [c for c in tabela.get("columns", []) if c.get("type") != "rowNumber"]


def sem_volateis(obj):
    if isinstance(obj, dict):
        return {k: sem_volateis(v) for k, v in obj.items() if k not in CHAVES_VOLATEIS}
    if isinstance(obj, list):
        return [sem_volateis(v) for v in obj]
    if isinstance(obj, str) and obj[:1] in "{[":
        try:                                   # o config do Layout clássico é JSON dentro de texto
            return sem_volateis(json.loads(obj))
        except ValueError:
            return obj
    return obj


def comparavel(nome, dados):
    if nome.startswith("Report/"):
        try:
            return sem_volateis(json.loads(texto(dados)))
        except ValueError:
            pass
    return dados


def decodifica_mashup(dados):
    """(código M, {(consulta, chave): valor} das chaves *Enabled) — formato MS-QDEFF.

    O DataMashup é: versão (4 bytes) · pacote OPC com Formulas/Section1.m ·
    permissões · metadados · vínculos de permissão (cifrados, mudam a cada
    gravação). Compara-se o que define as consultas: o M e as chaves de carga.
    """
    pos = 4

    def bloco():
        nonlocal pos
        (n,) = struct.unpack_from("<I", dados, pos)
        trecho = dados[pos + 4:pos + 4 + n]
        if len(trecho) != n:
            raise ValueError("bloco truncado")
        pos += 4 + n
        return trecho
    pacote, _permissoes, metadados = bloco(), bloco(), bloco()
    with zipfile.ZipFile(io.BytesIO(pacote)) as z:
        codigo = z.read("Formulas/Section1.m").decode("utf-8-sig")
    (n_xml,) = struct.unpack_from("<I", metadados, 4)
    raiz = ET.fromstring(metadados[8:8 + n_xml].decode("utf-8-sig"))
    chaves = {}
    for item in (el for el in raiz.iter() if el.tag.split("}")[-1] == "Item"):
        caminho = next((el.text or "" for el in item.iter() if el.tag.split("}")[-1] == "ItemPath"), "")
        for entrada in (el for el in item.iter() if el.tag.split("}")[-1] == "Entry"):
            if entrada.get("Type", "").endswith("Enabled"):
                chaves[(caminho, entrada.get("Type"))] = entrada.get("Value")
    return codigo, chaves


def primeira_diferenca(a, b, folga=30):
    i = next((k for k, (x, y) in enumerate(zip(a, b)) if x != y), min(len(a), len(b)))
    return f"…{a[max(0, i - folga):i + folga]}… × …{b[max(0, i - folga):i + folga]}…"


def paginas(zf):
    """[(nome, oculta)] nos dois formatos de relatório."""
    nomes = zf.namelist()
    saida = []
    if "Report/Layout" in nomes:                       # formato clássico
        for secao in json.loads(texto(zf.read("Report/Layout"))).get("sections", []):
            config = secao.get("config")
            config = json.loads(config) if isinstance(config, str) else (config or {})
            # o Desktop só grava a chave quando a página está oculta
            vis = secao.get("visibility", config.get("visibility"))
            saida.append((secao.get("displayName", ""), vis == 1))
    for nome in nomes:                                  # formato PBIR
        if nome.startswith("Report/definition/pages/") and nome.endswith("/page.json"):
            pagina = json.loads(texto(zf.read(nome)))
            saida.append((pagina.get("displayName", ""), pagina.get("visibility") == "HiddenInViewMode"))
    return saida


def main():
    if len(sys.argv) not in (2, 3):
        sys.exit("uso: python 03_dashboard/verifica_pbix.py ARQUIVO.pbit [ARQUIVO.pbix]")
    pbit_caminho = sys.argv[1]
    pbit = abre(pbit_caminho, ".pbit", "DataModelSchema", "DataModel")
    esquema = json.loads(texto(pbit.read("DataModelSchema")))
    modelo = esquema.get("model", esquema)
    tabelas = {t["name"]: t for t in modelo.get("tables", [])}
    esperado = M.colunas_esperadas()
    nomes_esperados = set(esperado) | {M.MEDIDAS}

    print(f"=== {os.path.basename(pbit_caminho)} · {len(tabelas)} tabelas no modelo ===\n")

    print("--- 1 · T7: colunas proibidas")
    achadas = []
    for t, tab in tabelas.items():
        for c in colunas_de(tab):
            nome = M.normaliza_nome(c["name"])
            for frag, motivo in M.FRAGMENTOS_PROIBIDOS.items():
                if frag in nome:
                    achadas.append(f"{t}[{c['name']}]: {motivo}")
                    break
    confere("nenhuma coluna pessoal ou de texto de avaliação no modelo", not achadas,
            "; ".join(achadas) + " → desativar a carga da consulta de origem (passo 16)")

    print("\n--- 2 · as tabelas carregadas")
    datas = sorted(t for t in tabelas if t.startswith(("LocalDateTable_", "DateTableTemplate_")))
    confere("nenhuma tabela de data automática", not datas,
            f"{len(datas)} encontradas → desmarcar 'Data/hora automática' e recarregar")
    extras = sorted(set(tabelas) - nomes_esperados - set(datas))
    confere("nenhuma tabela além do modelo combinado", not extras,
            f"a mais: {extras} → consulta com carga ligada (passo 16) ou consulta não renomeada (passo 14)")
    faltando = sorted(nomes_esperados - set(tabelas))
    confere("todas as tabelas do modelo presentes", not faltando, f"faltam: {faltando}")

    print("\n--- 3 · colunas, tipos e origem")
    for nome, cols in esperado.items():
        if nome not in tabelas:
            continue
        tab = tabelas[nome]
        reais = {c["name"]: c for c in colunas_de(tab)}
        a_mais, a_menos = sorted(set(reais) - set(cols)), sorted(set(cols) - set(reais))
        confere(f"{nome}: {len(cols)} colunas", not a_mais and not a_menos,
                f"tem {len(reais)} · a mais {a_mais} · faltando {a_menos}"
                + (" → expansão com prefixo? (passos 6 e 11)" if any("." in c for c in a_mais) else ""))
        tipos = M.TIPOS.get(nome, {})
        errados = [f"{c}: {reais[c].get('dataType')} (esperado {' ou '.join(sorted(tp))})"
                   for c, tp in tipos.items() if c in reais and reais[c].get("dataType") not in tp]
        if tipos:
            confere(f"{nome}: tipos das colunas-chave", not errados, "; ".join(errados))
        calculadas = sorted(c for c, col in reais.items() if col.get("type") == "calculated")
        tabela_calc = any((p.get("source") or {}).get("type") == "calculated" for p in tab.get("partitions", []))
        confere(f"{nome}: vem do Power Query, não de DAX", not calculadas and not tabela_calc,
                ("tabela calculada" if tabela_calc else f"colunas calculadas em DAX: {calculadas}")
                + " → a preparação é do Power Query (C2)")
        fonte = "\n".join("\n".join(x) if isinstance(x, list) else str(x)
                          for x in ((p.get("source") or {}).get("expression", "") for p in tab.get("partitions", [])))
        fonte_norm = fonte.replace("\\", "/").casefold()
        if nome in (M.BASE, M.REVIEWS):
            if not fonte.strip():
                linha("AVISO", f"{nome}: consulta M não legível no .pbit", "conferir à mão que não lê a gold")
            else:
                confere(f"{nome}: construída a partir do bronze, não importada da gold",
                        "00_data/gold" not in fonte_norm and "base_analitica.csv" not in fonte_norm
                        and "reviews.csv" not in fonte_norm,
                        "a consulta lê a camada gold → refazer a partir de gold_intermediaria; a gold é só o gabarito")
        if nome == M.CONFERENCIA:
            if not fonte.strip():
                linha("AVISO", "Conferencia: consulta M não legível no .pbit", "conferir à mão que lê conferencia_referencia.csv")
            else:
                confere("Conferencia: lida de conferencia_referencia.csv", "conferencia_referencia.csv" in fonte_norm,
                        "a consulta não lê o arquivo gerado por gera_conferencia.py")
    if M.MEDIDAS in tabelas:
        cols_med = colunas_de(tabelas[M.MEDIDAS])
        aceitas = [c for c in cols_med if M.COLUNA_INSERIR_DADOS.match(c["name"]) and c.get("dataType", "string") == "string"]
        sobra = [c["name"] for c in cols_med if c not in aceitas[:1]]
        confere(f"{M.MEDIDAS} sem coluna de dado", not sobra,
                f"colunas: {sobra} → só a coluna criada por Inserir dados é aceita")

    print("\n--- 4 · relacionamentos")
    rels = modelo.get("relationships", [])

    def descreve(r):
        return f"{r.get('fromTable')}[{r.get('fromColumn')}] → {r.get('toTable')}[{r.get('toColumn')}]"
    certa = [r for r in rels
             if {(r.get("fromTable"), r.get("fromColumn")), (r.get("toTable"), r.get("toColumn"))}
             == {(M.REVIEWS, "product_id"), (M.BASE, "product_id")}]
    confere("exatamente um relacionamento no modelo", len(rels) == 1,
            f"{len(rels)}: " + "; ".join(descreve(r) for r in rels)
            + " → apagar os criados pela detecção automática")
    confere(f"o relacionamento é {M.BASE}[product_id] 1 → N {M.REVIEWS}[product_id]", len(certa) == 1,
            "não encontrado")
    if certa:
        r = certa[0]
        confere("lado N em Reviews", r.get("fromTable") == M.REVIEWS, f"invertido: {descreve(r)}")
        confere("cardinalidade um para muitos",
                r.get("fromCardinality", "many") == "many" and r.get("toCardinality", "one") == "one",
                f"de {r.get('fromCardinality', 'many')} para {r.get('toCardinality', 'one')}")
        confere("filtro unidirecional", r.get("crossFilteringBehavior", "oneDirection") != "bothDirections",
                "está bidirecional")
        confere("relacionamento ativo", r.get("isActive", True) is not False, "está inativo")

    print("\n--- 5 · medidas: nome e expressão")
    medidas = {m["name"]: (t, m.get("expression", "")) for t, tab in tabelas.items()
               for m in tab.get("measures", [])}
    for rotulo, documento in (("catálogo (medidas_dax.md)", M.expressoes_catalogo()),
                              ("conferência (conferencia_dax.md)", M.expressoes_conferencia())):
        faltam = sorted(n for n in documento if n not in medidas)
        confere(f"as {len(documento)} medidas do {rotulo}, com o nome exato", not faltam, f"faltam: {faltam}")
        diferentes = {n: primeira_diferenca(M.normaliza_dax(medidas[n][1]), M.normaliza_dax(expr))
                      for n, expr in documento.items()
                      if n in medidas and M.normaliza_dax(medidas[n][1]) != M.normaliza_dax(expr)}
        confere(f"as do {rotulo} com a expressão do documento", not diferentes,
                "; ".join(f"{n}: arquivo {d}" for n, d in sorted(diferentes.items()))
                + " → copiar a expressão do documento como está")
    fora = sorted({t for t, _ in medidas.values() if t != M.MEDIDAS})
    confere(f"todas as medidas moram em {M.MEDIDAS}", not fora, f"medidas em: {fora}")

    print("\n--- 6 · a página de conferência")
    pags = paginas(pbit)
    conf = [oculta for nome, oculta in pags if nome.strip().lower() in ("conferência", "conferencia")]
    if not pags:
        linha("AVISO", "páginas do relatório não legíveis neste formato", "conferir a página à mão")
    else:
        confere("página 'Conferência' existe", bool(conf), f"páginas: {[n for n, _ in pags]}")
        if conf:
            confere("página 'Conferência' oculta", conf[0], "está visível → botão direito na aba > Ocultar página")

    if len(sys.argv) == 3:
        print("\n--- 7 · o .pbit é do .pbix entregue")
        pbix_caminho = sys.argv[2]
        pbix = abre(pbix_caminho, ".pbix", "DataModel", "DataModelSchema")
        a = {n: pbit.read(n) for n in pbit.namelist() if n.startswith(PARTES_RELATORIO)}
        b = {n: pbix.read(n) for n in pbix.namelist() if n.startswith(PARTES_RELATORIO)}
        confere("o .pbix tem relatório e consultas", bool(b) and "DataMashup" in pbix.namelist(),
                "partes ausentes no .pbix")
        diferentes = sorted(n for n in set(a) | set(b)
                            if comparavel(n, a.get(n, b"")) != comparavel(n, b.get(n, b"")))
        confere("relatório idêntico nos dois arquivos", not diferentes,
                f"diferem: {diferentes[:5]} → salvar o .pbix e exportar o .pbit de novo")
        try:
            m_a, carga_a = decodifica_mashup(pbit.read("DataMashup"))
            m_b, carga_b = decodifica_mashup(pbix.read("DataMashup"))
        except (KeyError, ValueError, struct.error, zipfile.BadZipFile, ET.ParseError) as erro:
            linha("AVISO", "consultas do Power Query não decodificadas", f"{erro} — comparar à mão")
        else:
            confere("código M das consultas idêntico nos dois arquivos", m_a == m_b,
                    "diferem → salvar o .pbix e exportar o .pbit de novo")
            difs = sorted(f"{k[0]} {k[1]}: {carga_a.get(k)} × {carga_b.get(k)}"
                          for k in set(carga_a) | set(carga_b) if carga_a.get(k) != carga_b.get(k))
            confere("carga de cada consulta idêntica nos dois arquivos", not difs,
                    "; ".join(difs[:5]) + " → a carga mudou depois da exportação (passo 16)")
        atraso = os.path.getmtime(pbix_caminho) - os.path.getmtime(pbit_caminho)
        confere(".pbix não foi salvo depois da exportação do .pbit", atraso <= FOLGA_SEGUNDOS,
                f"salvo {atraso:.0f} s depois → salvar, exportar o .pbit de novo e rodar sobre os arquivos "
                "originais (cópia e download mudam a data do arquivo)")
        if -atraso > ATRASO_SUSPEITO:
            linha("AVISO", f".pbix salvo {-atraso / 60:.0f} min antes da exportação",
                  "se algo mudou depois do último salvamento, salvar o .pbix e exportar o .pbit de novo")
    else:
        linha("AVISO", "sem o .pbix, não há como saber se este .pbit é do arquivo entregue",
              "passar o .pbix como segundo argumento")

    print("\n" + "=" * 78)
    print(f"Falhas: {len(FALHAS)}. Avisos: {len(AVISOS)}.")
    if FALHAS:
        print("O arquivo NÃO está pronto para entrega.")
        sys.exit(1)
    print("O modelo do arquivo é o modelo combinado." + (" Ler os avisos." if AVISOS else ""))


if __name__ == "__main__":
    main()

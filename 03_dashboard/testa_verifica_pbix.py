# -*- coding: utf-8 -*-
"""
Prova de que verifica_pbix.py falha quando deve — e só quando deve.

Uma checagem que nunca foi vista falhar não é checagem. Este script fabrica
.pbit e .pbix sintéticos a partir do modelo combinado — o esquema TMSL em
UTF-16, com tipos, partições e a expressão de cada medida, como o Power BI
grava —, planta um defeito por arquivo e exige: o modelo certo passa, cada
defeito reprova. E prova o outro lado: variações legítimas (estado de
navegação, a coluna padrão de "Inserir dados", o formato PBIR) não reprovam.
Roda em pasta temporária; não toca no projeto.

O formato real do .pbit só se confirma com o primeiro arquivo exportado pelo
Power BI Desktop — por isso o guia manda rodar verifica_pbix.py já no fim da
montagem do modelo (seção 3), e não só no congelamento.

Uso: python 03_dashboard/testa_verifica_pbix.py
"""

import copy
import io
import json
import os
import struct
import subprocess
import sys
import tempfile
import zipfile

PASTA = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PASTA)
import modelo_esperado as M  # noqa: E402

VERIFICA = os.path.join(PASTA, "verifica_pbix.py")
LAYOUT = {"config": json.dumps({"activeSectionIndex": 0}),
          "sections": [{"displayName": "Visão Executiva", "config": "{}"},
                       {"displayName": "Conferência", "config": json.dumps({"visibility": 1})}]}
CODIGO_M = ("section Section1;\nshared bronze_amazon = let Fonte = Csv.Document(...) in Fonte;\n"
            "shared BaseAnalitica = let Fonte = gold_intermediaria in Fonte;")
CARGA = {"bronze_amazon": "l0", "silver_produtos": "l0", "gold_intermediaria": "l0", "BaseAnalitica": "l1"}


def mashup(codigo=CODIGO_M, carga=CARGA, vinculos=b"\x01dpapi-sal-A", atualizado="2026-11-12T10:00:00"):
    """DataMashup no formato MS-QDEFF: versão · pacote · permissões · metadados · vínculos cifrados."""
    pacote = io.BytesIO()
    with zipfile.ZipFile(pacote, "w") as z:
        z.writestr("Formulas/Section1.m", codigo)
        z.writestr("Config/Package.xml", "<Package/>")
    itens = "".join(
        f"<Item><ItemLocation><ItemType>Formula</ItemType><ItemPath>Section1/{q}</ItemPath></ItemLocation>"
        f'<StableEntries><Entry Type="FillEnabled" Value="{v}" />'
        f'<Entry Type="FillLastUpdated" Value="d{atualizado}" /></StableEntries></Item>'
        for q, v in carga.items())
    xml = f"<LocalPackageMetadataFile><Items>{itens}</Items></LocalPackageMetadataFile>".encode("utf-8")
    metadados = struct.pack("<II", 0, len(xml)) + xml + struct.pack("<I", 0)

    def bloco(b):
        return struct.pack("<I", len(b)) + b
    return (struct.pack("<I", 0) + bloco(pacote.getvalue()) + bloco(b"<Permissions/>")
            + bloco(metadados) + bloco(vinculos))


MASHUP = mashup()
FONTES = {M.BASE: "let Fonte = gold_intermediaria in Fonte",
          M.REVIEWS: "let Fonte = gold_intermediaria in Fonte",
          M.CONFERENCIA: 'Csv.Document(File.Contents(pPasta & "\\03_dashboard\\conferencia_referencia.csv"))'}


def modelo_certo():
    tabelas = []
    for nome, cols in M.colunas_esperadas().items():
        tipos = {c: sorted(tp)[0] for c, tp in M.TIPOS.get(nome, {}).items()}
        fonte = FONTES.get(nome, f'Csv.Document(File.Contents(pPasta & "\\02_results\\tables\\{nome}.csv"))')
        tabelas.append({"name": nome,
                        "columns": [{"name": c, "dataType": tipos.get(c, "string")} for c in cols]
                        + [{"name": "RowNumber-2662979B", "type": "rowNumber"}],
                        "partitions": [{"name": nome, "source": {"type": "m", "expression": fonte.split("\n")}}]})
    medidas = [{"name": n, "expression": e.split("\n")}
               for n, e in list(M.expressoes_catalogo().items()) + list(M.expressoes_conferencia().items())]
    tabelas.append({"name": M.MEDIDAS, "columns": [{"name": "Coluna1", "dataType": "string"}], "measures": medidas})
    return {"model": {"tables": tabelas, "relationships": [
        {"fromTable": M.REVIEWS, "fromColumn": "product_id", "toTable": M.BASE, "toColumn": "product_id"}]}}


def grava(caminho, esquema=None, layout=LAYOUT, mashup=MASHUP, pbir=False, modelo_binario=False):
    with zipfile.ZipFile(caminho, "w") as zf:
        if esquema is not None:
            zf.writestr("DataModelSchema", json.dumps(esquema, ensure_ascii=False).encode("utf-16-le"))
        if modelo_binario:
            zf.writestr("DataModel", b"\x00xpress9 comprimido")
        if pbir:
            for i, (nome, oculta) in enumerate([("Visão Executiva", False), ("Conferência", layout)]):
                pagina = {"displayName": nome} | ({"visibility": "HiddenInViewMode"} if oculta else {})
                zf.writestr(f"Report/definition/pages/p{i}/page.json", json.dumps(pagina).encode("utf-8"))
        else:
            zf.writestr("Report/Layout", json.dumps(layout, ensure_ascii=False).encode("utf-16-le"))
        if mashup is not None:          # None: formato atual do Desktop, sem a parte DataMashup
            zf.writestr("DataMashup", mashup)


def tabela(esquema, nome):
    return next(t for t in esquema["model"]["tables"] if t["name"] == nome)


def coluna(esquema, nome_tabela, nome_coluna):
    return next(c for c in tabela(esquema, nome_tabela)["columns"] if c["name"] == nome_coluna)


def medida(esquema, nome):
    return next(m for m in tabela(esquema, M.MEDIDAS)["measures"] if m["name"] == nome)


def troca_expr(esquema, nome, velho, novo):
    m = medida(esquema, nome)
    texto = "\n".join(m["expression"])
    assert velho in texto, f"{nome}: '{velho}' não está na expressão"
    m["expression"] = texto.replace(velho, novo).split("\n")


DEFEITOS = [
    ("bronze carregado com user_name (T7)", lambda v: v["model"]["tables"].append(
        {"name": "bronze_amazon", "columns": [{"name": "user_id"}, {"name": "user_name"}]})),
    ("coluna pessoal com outra caixa na _Medidas (T7)", lambda v: tabela(v, M.MEDIDAS)["columns"].append(
        {"name": "User_Name", "dataType": "string"})),
    ("coluna de dado na _Medidas", lambda v: tabela(v, M.MEDIDAS)["columns"].append(
        {"name": "autor", "dataType": "string"})),
    ("tab22 carregada como tabela", lambda v: v["model"]["tables"].append(
        {"name": "tab22", "columns": [{"name": "product_id"}, {"name": "arquetipo"}]})),
    ("consulta não renomeada (tab03_correlacoes)", lambda v: tabela(v, "tab03").update(name="tab03_correlacoes")),
    ("tabela de data automática", lambda v: v["model"]["tables"].append(
        {"name": "LocalDateTable_1", "columns": [{"name": "Date"}]})),
    ("expansão com prefixo (tab22.arquetipo)", lambda v: coluna(v, M.BASE, "arquetipo").update(
        name="tab22.arquetipo")),
    ("coluna derivada faltando", lambda v: tabela(v, M.BASE).update(
        columns=[c for c in tabela(v, M.BASE)["columns"] if c["name"] != "pareto_posicao"])),
    ("booleano importado como texto", lambda v: coluna(v, M.BASE, "q5_risco_vitrine").update(dataType="string")),
    ("derivada como coluna calculada em DAX", lambda v: coluna(v, M.BASE, "relevancia").update(type="calculated")),
    ("Reviews como tabela calculada", lambda v: tabela(v, M.REVIEWS).update(
        partitions=[{"name": "r", "source": {"type": "calculated", "expression": "..."}}])),
    ("tabela de resultado esquecida", lambda v: v["model"]["tables"].remove(tabela(v, "tab23"))),
    ("BaseAnalitica importada da gold", lambda v: tabela(v, M.BASE)["partitions"][0]["source"].update(
        expression=['Csv.Document(File.Contents(pPasta & "\\00_data\\gold\\base_analitica.csv"))'])),
    ("Conferencia que não lê o arquivo gerado", lambda v: tabela(v, M.CONFERENCIA)["partitions"][0]["source"].update(
        expression=["#table({}, {})"])),
    ("relação criada pela detecção automática", lambda v: v["model"]["relationships"].append(
        {"fromTable": M.BASE, "fromColumn": "arquetipo", "toTable": "tab05", "toColumn": "arquetipo"})),
    ("relacionamento bidirecional", lambda v: v["model"]["relationships"][0].update(
        crossFilteringBehavior="bothDirections")),
    ("relacionamento muitos-para-muitos", lambda v: v["model"]["relationships"][0].update(
        toCardinality="many")),
    ("medida do catálogo renomeada", lambda v: medida(v, "Produtos Ativos").update(name="Produtos Ativos (novo)")),
    ("M18 sem ALL — o erro que o total esconde", lambda v: troca_expr(
        v, "Corte de Engajamento Alto", "ALL ( BaseAnalitica )", "BaseAnalitica")),
    ("M15 com ALLSELECTED no lugar de ALL", lambda v: troca_expr(
        v, "Participação da Categoria no Volume", "ALL ( BaseAnalitica[categoria_n1] )",
        "ALLSELECTED ( BaseAnalitica[categoria_n1] )")),
    ("Conf · Divergentes sem ALL ( Conferencia )", lambda v: troca_expr(
        v, "Conf · Divergentes", "ALL ( Conferencia ),\n", "Conferencia,\n")),
]


def roda(*args):
    return subprocess.run([sys.executable, VERIFICA, *args], capture_output=True, text=True).returncode


certo = modelo_certo()
resultados = []
with tempfile.TemporaryDirectory() as tmp:
    def arquivo(nome, **kw):
        caminho = os.path.join(tmp, nome)
        grava(caminho, **kw)
        return caminho

    pbit = arquivo("certo.pbit", esquema=certo)
    pbix = arquivo("certo.pbix", modelo_binario=True)
    os.utime(pbix, (os.path.getmtime(pbit) - 10,) * 2)       # salvo antes da exportação
    resultados.append(("modelo combinado, .pbit do mesmo .pbix", roda(pbit, pbix), 0))

    sal = arquivo("outro_sal.pbix", modelo_binario=True,
                  mashup=mashup(vinculos=b"\x01dpapi-sal-B-diferente", atualizado="2026-11-12T10:05:00"))
    os.utime(sal, (os.path.getmtime(pbit) - 10,) * 2)
    resultados.append(("vínculos cifrados e datas de atualização diferentes (par legítimo)", roda(pbit, sal), 0))
    idioma = copy.deepcopy(certo)
    tabela(idioma, M.MEDIDAS)["columns"] = [{"name": "Columna1", "dataType": "string"}]
    resultados.append(("coluna de Inserir dados em outro idioma", roda(arquivo("idioma.pbit", esquema=idioma)), 0))
    inteiro = copy.deepcopy(certo)
    coluna(inteiro, M.BASE, "desconto").update(dataType="int64")
    resultados.append(("desconto como Número inteiro", roda(arquivo("inteiro.pbit", esquema=inteiro)), 0))
    ilegivel = arquivo("ilegivel.pbix", modelo_binario=True, mashup=b"\x00\x00\x00\x00curto")
    os.utime(ilegivel, (os.path.getmtime(pbit) - 10,) * 2)
    resultados.append(("consultas não decodificáveis — passa com aviso", roda(pbit, ilegivel), 0))

    atual_t = arquivo("atual.pbit", esquema=certo, mashup=None)
    atual_x = arquivo("atual.pbix", modelo_binario=True, mashup=None)
    os.utime(atual_x, (os.path.getmtime(atual_t) - 10,) * 2)
    resultados.append(("formato atual do Desktop, sem DataMashup nos dois — passa com aviso",
                       roda(atual_t, atual_x), 0))

    navegou = arquivo("navegou.pbix", modelo_binario=True,
                      layout=LAYOUT | {"config": json.dumps({"activeSectionIndex": 1})})
    os.utime(navegou, (os.path.getmtime(pbit) - 10,) * 2)
    resultados.append(("só a página ativa diferente (estado de navegação)", roda(pbit, navegou), 0))
    resultados.append(("formato PBIR, página oculta", roda(arquivo("pbir.pbit", esquema=certo, pbir=True, layout=True)), 0))

    for i, (nome, altera) in enumerate(DEFEITOS):
        v = copy.deepcopy(certo)
        altera(v)
        resultados.append((nome, roda(arquivo(f"defeito_{i}.pbit", esquema=v)), 1))

    visivel = copy.deepcopy(LAYOUT)
    visivel["sections"][1]["config"] = "{}"
    resultados.append(("página Conferência visível (clássico)", roda(arquivo("vis.pbit", esquema=certo, layout=visivel)), 1))
    resultados.append(("página Conferência visível (PBIR)", roda(arquivo("vis_pbir.pbit", esquema=certo, pbir=True, layout=False)), 1))

    outro = arquivo("outro_relatorio.pbix", modelo_binario=True,
                    layout={"sections": [{"displayName": "Conferência", "config": "{}"}]})
    os.utime(outro, (os.path.getmtime(pbit) - 10,) * 2)
    resultados.append((".pbix com outro relatório", roda(pbit, outro), 1))
    carga = arquivo("carga_religada.pbix", modelo_binario=True, mashup=mashup(carga=CARGA | {"bronze_amazon": "l1"}))
    os.utime(carga, (os.path.getmtime(pbit) - 10,) * 2)
    resultados.append((".pbix com a carga do bronze religada", roda(pbit, carga), 1))
    outro_m = arquivo("outro_m.pbix", modelo_binario=True, mashup=mashup(codigo=CODIGO_M + "\nshared x = 1;"))
    os.utime(outro_m, (os.path.getmtime(pbit) - 10,) * 2)
    resultados.append((".pbix com código M diferente", roda(pbit, outro_m), 1))
    sem_m = arquivo("sem_consultas.pbix", modelo_binario=True, mashup=None)
    os.utime(sem_m, (os.path.getmtime(pbit) - 10,) * 2)
    resultados.append((".pbix sem as consultas, ao lado de .pbit que as tem", roda(pbit, sem_m), 1))
    depois = arquivo("salvo_depois.pbix", modelo_binario=True)
    os.utime(depois, (os.path.getmtime(pbit) + 3600,) * 2)
    resultados.append((".pbix salvo depois da exportação", roda(pbit, depois), 1))
    resultados.append((".pbit passado no lugar do .pbix", roda(pbit, arquivo("falso.pbix", esquema=certo)), 1))
    resultados.append((".pbix passado no lugar do .pbit", roda(pbix), 1))

erros = 0
for nome, obtido, esperado in resultados:
    ok = obtido == esperado
    erros += not ok
    print(f"{'OK' if ok else 'ERRO':4s} | {'passa  ' if esperado == 0 else 'reprova'} · {nome}"
          + ("" if ok else f" — saída {obtido}, esperada {esperado}"))
print(f"\n{len(resultados)} casos · {erros} errados")
sys.exit(1 if erros else 0)

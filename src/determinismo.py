# -*- coding: utf-8 -*-
"""
Saídas binárias reprodutíveis — o mesmo conteúdo gera os mesmos bytes.

POR QUE EXISTE
--------------
O projeto inteiro se apoia em "gerado, não escrito": quem duvida de um número
roda o gerador de novo. Mas PDF e DOCX gravam a HORA da geração — o reportlab
põe data e identificador do momento, o pikepdf um identificador novo ao
linearizar, e o .docx a hora em cada arquivo interno do pacote. Resultado:
rodar de novo, sem mudar nada, mudava todos os binários. Isso suja o histórico
do git a cada execução e tira o valor da verificação mais simples que existe —
"rodei de novo e nada mudou".

Aqui as três fontes de variação ficam fixas. A data gravada é a da versão do
material, não a do relógio.
"""

import datetime
import zipfile

DATA_FIXA = datetime.datetime(2026, 10, 25)


def fixar_reportlab():
    """Data fixa e identificador do documento derivado do conteúdo."""
    from reportlab import rl_config
    rl_config.invariant = 1


def datar_pdf(caminho):
    """Grava a data da versão nos metadados do PDF, e relineariza.

    `rl_config.invariant` torna o arquivo reprodutível zerando a data — os PDF saíam
    com 01/01/2000, enquanto este módulo promete a data da versão. Aqui ela volta, fixa.
    Só o docinfo: `open_metadata()` do pikepdf regrava o XMP com a hora do relógio e
    tiraria a reprodutibilidade.
    """
    import pikepdf
    carimbo = DATA_FIXA.strftime("D:%Y%m%d%H%M%S+00'00'")
    with pikepdf.open(caminho, allow_overwriting_input=True) as pdf:
        pdf.docinfo["/CreationDate"] = carimbo
        pdf.docinfo["/ModDate"] = carimbo
        pdf.save(caminho, linearize=True, deterministic_id=True)


def fixar_propriedades(cp):
    """Datas de criação e modificação do .docx na data da versão."""
    cp.created = cp.modified = DATA_FIXA
    cp.last_printed = DATA_FIXA
    cp.revision = 1


def fixar_docx(caminho):
    """Regrava o pacote .docx com a hora de cada parte fixa e a ordem estável."""
    with zipfile.ZipFile(caminho) as z:
        partes = [(i, z.read(i.filename)) for i in z.infolist()]
    with zipfile.ZipFile(caminho, "w") as z:
        for info, dados in partes:
            nova = zipfile.ZipInfo(info.filename, date_time=DATA_FIXA.timetuple()[:6])
            nova.compress_type = info.compress_type
            nova.external_attr = info.external_attr
            z.writestr(nova, dados)

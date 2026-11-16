# -*- coding: utf-8 -*-
"""
Monta o roteiro do vídeo executivo em .docx e .pdf a partir de `04_video/roteiro.md`.

Usa o mesmo gerador do Manual de Leitura do Dashboard (`src/monta_manual.py`),
com outra capa e sem sumário: os dois documentos saem com a mesma identidade
visual (paleta v06, regra T9). O roteiro .md continua sendo a fonte da verdade;
alterou o texto, rode este script de novo.

Uso:  python3 src/monta_roteiro.py
Saída: 04_video/roteiro_video_<VERSAO>.docx · .pdf
"""

import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import monta_manual as mm

MD = os.path.join(mm.RAIZ, "04_video", "roteiro.md")
VERSAO = "v1"
OUT = os.path.join(mm.RAIZ, "04_video", f"roteiro_video_{VERSAO}.docx")
OUT_PDF = os.path.join(mm.RAIZ, "04_video", f"roteiro_video_{VERSAO}.pdf")

# As duas linhas em negrito abaixo do título do .md vão para a capa, não para o corpo.
CAPA_NO_MD = ("**Tech Challenge Fase 4", "**Duração-alvo")


def pula(tipo, cont):
    return tipo == "h1" or (tipo == "par" and cont.startswith(CAPA_NO_MD))


def main():
    bruto = open(MD, encoding="utf-8").read()
    m = re.search(r"^\*\*(Duração-alvo:[^*]+)\*\*", bruto, re.M)
    if not m:
        sys.exit("ERRO: o roteiro não declara a linha **Duração-alvo: …** abaixo do título.")
    cfg = {
        "out_docx": OUT,
        "out_pdf": OUT_PDF,
        "titulo": "Roteiro do Vídeo Executivo — Tech Challenge Fase 4 — Grupo 12",
        "palavras": "Tech Challenge; Fase 4; vídeo executivo; roteiro; Power BI",
        "capa": "Roteiro do Vídeo Executivo",
        "rodape": "Tech Challenge Fase 4 · Grupo 12 · Roteiro do Vídeo Executivo",
        "sumario": False,
        "quebra_h2": False,
        "pula": pula,
    }
    itens = mm.blocos(bruto, base=os.path.dirname(MD))
    mm.gerar_docx(itens, m.group(1).strip(), cfg)
    mm.gerar_pdf(itens, m.group(1).strip(), cfg)


if __name__ == "__main__":
    main()

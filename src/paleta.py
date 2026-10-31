# -*- coding: utf-8 -*-
"""
Paleta oficial do Tech Challenge Fase 4 — v06. Fonte executável da cor.

Por que este arquivo existe
---------------------------
A regra T9 determina que a paleta vale em **todo** artefato do projeto, não só
no `.pbix`: notebook, gráfico em Python, tabela, deck, vídeo, diagrama e
qualquer arquivo gerado. Uma regra que só existe em documento não é cumprida —
é torcida. Este módulo torna a paleta aplicável em uma linha:

    from paleta import aplicar
    aplicar()                      # configura o matplotlib para o padrão v06

E torna o descumprimento detectável:

    python3 paleta.py    # confere contra o tema .json e a tabela v06

Fonte da verdade: `method/design_system/tokens_paleta_v06.md`. Este arquivo **replica**
aqueles valores e falha se divergir do `tema_fase4_ambar_ardosia.json`.
"""

import json
import os
import re
import sys

# ---------------------------------------------------------------------------
# Tokens — espelham method/design_system/tokens_paleta_v06.md
# ---------------------------------------------------------------------------
BASE = {
    "canvas": "#FFF4D6",      # fundo da página · zebra de tabela
    "card": "#FFFFFF",        # fundo de visuais e KPIs
    "divisor": "#F0EADA",     # bordas, faixas, linhas de tabela
}

ESTRUTURA = {
    "tinta": "#2A2F35",       # texto primário — 12,31:1 sobre creme
    "secundario": "#5B6770",  # rótulos, eixos, legendas — 5,30:1
    "grade": "#9AA5B1",       # grade, inativo — 2,28:1, NUNCA em texto
}

CHAMADAS = {
    "destaque": "#F2C14E",    # foco narrativo — 1,53:1, NUNCA em texto
    "favoravel": "#1F6F6B",   # leitura positiva — 5,41:1
    "atencao": "#DC6C09",     # leitura negativa — 3,09:1, só gráfico ou ≥18pt
}

# Ordem obrigatória. Teal e ardósia ficam em 5º e 6º porque são
# indistinguíveis entre si sob deuteranopia (ΔE 1,6). Não reordenar.
CATEGORICA = [
    "#F2C14E",  # 1 âmbar
    "#3F5A7A",  # 2 azul-ardósia (também cor de link)
    "#9AA5B1",  # 3 ardósia clara
    "#DC6C09",  # 4 laranja
    "#1F6F6B",  # 5 teal
    "#5B6770",  # 6 ardósia
]

SEQUENCIAL = ["#EAF3F2", "#C6E0DD", "#96C6C2", "#5FA5A0", "#1F6F6B", "#12504D"]

DIVERGENTE = ["#DC6C09", "#EDA25C", "#F7D4AE", "#FFF4D6", "#9EC5C1", "#6FA8A3", "#1F6F6B"]

#: Séries acima deste número exigem rótulo direto (ver T9 e tokens v06).
MAX_SERIES_SEGURO = 5

TODOS = sorted(set(
    list(BASE.values()) + list(ESTRUTURA.values()) + list(CHAMADAS.values())
    + CATEGORICA + SEQUENCIAL + DIVERGENTE
))


# ---------------------------------------------------------------------------
# Aplicação
# ---------------------------------------------------------------------------
def aplicar(tamanho_base=10, fundo="canvas"):
    """Configura o matplotlib no padrão v06. Chamar antes do primeiro gráfico.

    fundo="canvas" (padrão) → creme, o fundo de página do dashboard.
    fundo="card"            → branco, para figura que vai em documento impresso.
    Os dois são tokens da paleta v06, então a escolha não fere T9.
    """
    import matplotlib as mpl
    from cycler import cycler

    if fundo not in BASE:
        raise ValueError(f"fundo deve ser um token de BASE: {list(BASE)}")
    cor_fundo = BASE[fundo]

    mpl.rcParams.update({
        "figure.facecolor": cor_fundo,
        "savefig.facecolor": cor_fundo,
        "axes.facecolor": BASE["card"],
        "axes.edgecolor": BASE["divisor"],
        "axes.labelcolor": ESTRUTURA["secundario"],
        "axes.titlecolor": ESTRUTURA["tinta"],
        "axes.grid": True,
        "axes.axisbelow": True,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "grid.color": ESTRUTURA["grade"],
        "grid.alpha": 0.35,
        "grid.linewidth": 0.6,
        "text.color": ESTRUTURA["tinta"],
        "xtick.color": ESTRUTURA["secundario"],
        "ytick.color": ESTRUTURA["secundario"],
        "font.size": tamanho_base,
        "axes.titlesize": tamanho_base + 3,
        "legend.frameon": False,
        "axes.prop_cycle": cycler(color=CATEGORICA),
    })
    return mpl.rcParams


def mapa_sequencial():
    """Colormap contínuo da escala sequencial teal."""
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list("fase4_sequencial", SEQUENCIAL)


def mapa_divergente():
    """Colormap contínuo da escala divergente, centrada no creme."""
    from matplotlib.colors import LinearSegmentedColormap
    return LinearSegmentedColormap.from_list("fase4_divergente", DIVERGENTE)


def cor_do_texto_sobre(fundo_hex):
    """Devolve `tinta` ou `card`, o que tiver contraste AA sobre o fundo dado."""
    return ESTRUTURA["tinta"] if contraste(ESTRUTURA["tinta"], fundo_hex) >= 4.5 else BASE["card"]


def contraste(a, b):
    """Razão de contraste WCAG 2.1 entre dois hex."""
    def lum(h):
        vals = [int(h.lstrip("#")[i:i + 2], 16) / 255 for i in (0, 2, 4)]
        vals = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in vals]
        return 0.2126 * vals[0] + 0.7152 * vals[1] + 0.0722 * vals[2]
    x, y = sorted([lum(a), lum(b)], reverse=True)
    return (x + 0.05) / (y + 0.05)


# Um rótulo de eixo que é só número: dígito, espaço, separador e sinal.
# Serve a dois usos — decidir se o eixo pode receber vírgula decimal, e
# detectar o eixo de categoria cujo nome foi apagado.
SO_NUMERO = re.compile(r"^[\s\-−+]?[\d\s.,]*$")


def rodape(fig, texto, corpo=7.0, x=0.01, y=0.012):
    """T3 — rodapé de fonte, base e n, **quebrado na largura da figura**.

    POR QUE ESTA FUNÇÃO É CENTRAL. Cada notebook e o gerador de figuras tinham o seu
    `rodape()`, todos de uma linha só. Com `bbox_inches="tight"`, rodapé mais largo que o
    quadro não é cortado: ele ALARGA a imagem. Em `fig07` e `fig13` o gráfico passou a
    ocupar 60% da imagem, encostado à esquerda, e no relatório a figura é reduzida à
    largura da página — o gráfico encolhe junto. Sem `tight` (a cartela do vídeo) o mesmo
    rodapé é cortado de fato, e a definição de B e a cláusula T6 sumiam da imagem.

    A quebra é medida, não estimada: desenha, lê a caixa do texto e estreita até caber.
    Linhas explícitas (`\n`) do chamador são respeitadas.
    """
    import textwrap

    folga = fig.get_figwidth() * 72 * 0.96
    largura = max(30, int(folga / (corpo * 0.55)))
    while True:
        linhas = []
        for trecho in texto.split("\n"):
            linhas += textwrap.wrap(trecho, largura) or [""]
        t = fig.text(x, y, "\n".join(linhas), fontsize=corpo, color=ESTRUTURA["secundario"],
                     ha="left", va="bottom", linespacing=1.45)
        fig.canvas.draw()
        if t.get_window_extent(fig.canvas.get_renderer()).x1 <= fig.bbox.x1 * 0.985 or largura <= 30:
            break
        t.remove()
        largura = int(largura * 0.92)
    # espaço sob o eixo proporcional ao que o rodapé ocupou — nunca menos que o piso atual
    altura = (len(linhas) * corpo * 1.45 + 16) / (fig.get_figheight() * 72)
    fig.subplots_adjust(bottom=max(fig.subplotpars.bottom, altura + 0.14))
    return t


def confere_visual(fig, nome):
    """As regras visuais do projeto, conferidas na figura — não no código que a desenha.

    POR QUE EXISTE. Todo o aparato de verificação deste projeto confere número e texto:
    107 asserções sobre a base, dicionário coluna a coluna, DAX comparado caractere a
    caractere, 41 números plantados no sumário. **Nenhuma parte dele olhava dentro de um
    PNG** — e foi por aí que passou o defeito que motivou esta função: ao unificar a
    vírgula decimal dos eixos, o formatador foi aplicado também a eixo de categoria, e
    `Electronics · Home&Kitchen · Computers&Accessories` virou `8 · 7 · 6` na fig05.
    A figura saiu, o script terminou com 0, os validadores passaram e o commit foi feito.

    O que se confere aqui é só o que a figura mostra, e só o que tem regra escrita:

    - **T3** — rodapé com fonte, base e *n*. Sem ele o número não é rastreável.
    - **T9** — no máximo 5 séries na legenda; vedado pizza e rosca.
    - **o defeito acima** — eixo de categoria que saiu com rótulo numérico.
    - **rodapé cortado pela borda** — o rodapé que sai do quadro. Foi o que a
      cartela do conflito B × D mostrava: o rodapé, centralizado e comprido demais, perdia
      o começo ("B = ..., n 335") e o fim ("volume de avaliações, não vendas — T6"). T3 e T6
      estavam escritas, mas só **no código**; na imagem, a parte que as cumpria não aparecia.

    Deixa de fora, de propósito, a regra do âmbar único: a cor âmbar também é a primeira
    da escala categórica, e contá-la sem saber o papel de cada elemento acusaria uso
    legítimo. Essa continua sendo conferência de olho humano, e está no checklist da F8.
    """
    from matplotlib.patches import Wedge

    faltas = []
    textos = [t.get_text() for t in fig.texts]
    if not any(t.startswith("Fonte:") for t in textos):
        faltas.append("sem rodapé de fonte, base e n (T3)")

    for eixo in fig.axes:
        if any(isinstance(a, Wedge) for a in eixo.patches):
            faltas.append("usa pizza ou rosca, vedado em T9")
        legenda = eixo.get_legend()
        if legenda is not None and len(legenda.get_texts()) > 5:
            faltas.append(f"{len(legenda.get_texts())} séries na legenda; T9 admite 5")
        for escala in (eixo.xaxis, eixo.yaxis):
            if escala.get_converter() is None:
                continue                      # eixo numérico: rótulo numérico é o certo
            rotulos = [t.get_text() for t in escala.get_ticklabels() if t.get_text()]
            if rotulos and all(SO_NUMERO.match(r) for r in rotulos):
                faltas.append(f"o eixo {escala.axis_name} é de categoria e saiu com rótulo "
                              f"numérico {rotulos[:4]} — o nome da categoria foi apagado")
    # O rodapé de fonte que escapa do quadro. Mede o retângulo que ele ocupa na figura
    # desenhada (`get_window_extent`), não o comprimento da string, porque é o que o leitor
    # vê. O alvo é só o rodapé — o que carrega T3 e T6. Título comprido e rótulo de eixo são
    # outra classe, cosmética, e conferi-los acusaria figura legível e quebraria o fluxo.
    fig.canvas.draw()
    limite = fig.bbox
    for t in fig.texts:
        if not t.get_text().strip().startswith("Fonte:"):
            continue
        caixa = t.get_window_extent(fig.canvas.get_renderer())
        if caixa.x0 < limite.x0 - 1 or caixa.x1 > limite.x1 + 1 or caixa.y0 < limite.y0 - 1 or caixa.y1 > limite.y1 + 1:
            faltas.append("rodapé de fonte cortado pela borda da figura — a parte que cumpre T3/T6 não aparece")
    assert not faltas, f"{nome}: " + " · ".join(sorted(set(faltas)))


def checar_series(n):
    """Avisa quando o número de séries ultrapassa o que a paleta suporta."""
    if n > len(CATEGORICA):
        raise ValueError(
            f"{n} séries: a escala categórica tem {len(CATEGORICA)}. "
            "Agrupe categorias — T9 veda inventar cor.")
    if n > MAX_SERIES_SEGURO:
        print(f"AVISO: {n} séries usa teal e ardósia juntos (ΔE 1,6 sob "
              "deuteranopia). Rótulo direto é obrigatório — ver tokens v06.",
              file=sys.stderr)
    return True


# ---------------------------------------------------------------------------
# Autoconferência
# ---------------------------------------------------------------------------
def conferir(caminho_tema=None):
    """Confere este módulo contra o tema .json. Devolve a lista de divergências."""
    raiz = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    caminho_tema = caminho_tema or os.path.join(raiz, "method", "design_system", "tema_fase4_ambar_ardosia.json")
    falhas = []
    try:
        with open(caminho_tema, encoding="utf-8") as fh:
            tema = json.load(fh)
    except FileNotFoundError:
        return [f"tema não encontrado em {caminho_tema}"]

    if tema.get("dataColors") != CATEGORICA:
        falhas.append(f"dataColors do tema {tema.get('dataColors')} ≠ CATEGORICA {CATEGORICA}")
    for chave, esperado in [("background", BASE["canvas"]), ("backgroundNeutral", BASE["card"]),
                            ("backgroundLight", BASE["divisor"]), ("foreground", ESTRUTURA["tinta"]),
                            ("foregroundNeutralSecondary", ESTRUTURA["secundario"]),
                            ("foregroundNeutralTertiary", ESTRUTURA["grade"]),
                            ("good", CHAMADAS["favoravel"]), ("bad", CHAMADAS["atencao"]),
                            ("tableAccent", CHAMADAS["destaque"]),
                            ("minimum", SEQUENCIAL[0]), ("maximum", SEQUENCIAL[-1])]:
        if tema.get(chave) != esperado:
            falhas.append(f"tema['{chave}'] = {tema.get(chave)}, esperado {esperado}")

    import re
    with open(caminho_tema, encoding="utf-8") as fh:
        no_tema = {h.upper() for h in re.findall(r"#[0-9A-Fa-f]{6}", fh.read())}
    fora = sorted(no_tema - {c.upper() for c in TODOS})
    if fora:
        falhas.append(f"cores no tema fora da paleta v06: {fora}")
    return falhas


if __name__ == "__main__":
    print("Paleta Fase 4 — v06")
    print(f"  categórica : {len(CATEGORICA)} séries (seguro até {MAX_SERIES_SEGURO})")
    print(f"  sequencial : {len(SEQUENCIAL)} passos")
    print(f"  divergente : {len(DIVERGENTE)} passos")
    print(f"  total      : {len(TODOS)} cores distintas")
    problemas = conferir()
    if problemas:
        print("\nDIVERGÊNCIAS:")
        for p in problemas:
            print(f"  - {p}")
        sys.exit(1)
    print("\nConfere com tema_fase4_ambar_ardosia.json. Nenhuma cor fora da paleta.")
    sys.exit(0)

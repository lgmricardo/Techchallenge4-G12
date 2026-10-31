# -*- coding: utf-8 -*-
"""
Os dois artefatos enxutos — sumário executivo (2 páginas) e folha de defesa (1 página).

POR QUE EXISTEM
---------------
O relatório técnico tem mais de cem páginas e é o que DEFENDE o trabalho. Dois
leitores precisam de outra coisa: a liderança (e o avaliador, no primeiro
contato) quer o que fazer e por quê, em duas páginas; e o grupo, na defesa ao
vivo, quer achar em segundos o número que acabou de falar, com a base, o n, a
seção onde ele mora e a regra que o protege.

POR QUE SÃO GERADOS
-------------------
Um resumo escrito à mão é uma segunda cópia dos mesmos números, e a primeira
alteração no relatório deixaria as duas divergentes. Aqui nada é reescrito:

- o SUMÁRIO EXECUTIVO é extraído do relatório — Resumo Executivo, as quatro
  mensagens para a liderança e as cinco recomendações. E o script FALHA se o
  resumo trouxer um número que o corpo do relatório (fora do próprio resumo)
  não traz: resumo que afirma o que o corpo não sustenta é o defeito clássico.
- a FOLHA DE DEFESA lê os números falados no vídeo de
  04_video/tab_roteiro_numeros.csv (valor, base, n, regra) e localiza cada um
  no relatório. O script FALHA se um número falado não existir no relatório —
  número que não está no material escrito não pode ser defendido.

Uso: python src/gera_resumo.py
"""

import csv
import os
import re
import sys

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "src"))
from paleta import BASE, ESTRUTURA  # noqa: E402
from determinismo import datar_pdf, fixar_docx, fixar_propriedades, fixar_reportlab  # noqa: E402

# As três variáveis de ambiente existem para testa_gera_resumo.py, que roda o gerador
# sobre cópias com números plantados, numa pasta temporária.
RELATORIO = os.environ.get("RESUMO_RELATORIO", os.path.join(RAIZ, "docs", "relatorio_tecnico.md"))
ROTEIRO_NUMEROS = os.environ.get("RESUMO_ROTEIRO", os.path.join(RAIZ, "04_video", "tab_roteiro_numeros.csv"))
GUIA = os.path.join(RAIZ, "03_dashboard", "INSTRUCOES_MONTAGEM_POWERBI.md")
LIMITACOES = os.path.join(RAIZ, "method", "limitations", "limitacoes_obrigatorias.md")
FONTES = os.path.join(RAIZ, "src", "fonts")
SAIDA = os.environ.get("RESUMO_SAIDA", os.path.join(RAIZ, "docs"))
SAIDA_SUMARIO = os.path.join(SAIDA, "executive_summary_phase4_v1_powerbi")
SAIDA_DEFESA = os.path.join(SAIDA, "defense_sheet_phase4_v1_powerbi")

texto = open(RELATORIO, encoding="utf-8").read()
LINHAS = texto.split("\n")


# --------------------------------------------- números, sem identificadores
SUPER = str.maketrans("⁻⁰¹²³⁴⁵⁶⁷⁸⁹", "-0123456789")
# O sinal só vale quando não vem colado num dígito ou letra: "0-20%" é faixa, não −20.
SINAL = r"(?:(?<![\w])[−-])?"
NUM = re.compile(SINAL + r"\d{1,3}(?:\.\d{3})+(?:,\d+)?|" + SINAL + r"\d+(?:,\d+)?(?:e[−-]\d+)?")


def limpa(s):
    """Tira do texto o que tem dígito mas não é número: código, remissão, hash, data."""
    s = re.sub(r"\s*×\s*10([⁻⁰¹²³⁴⁵⁶⁷⁸⁹]+)", lambda m: "e" + m.group(1).translate(SUPER), s)
    s = re.sub(r"\b\d+\s*[–-]\s*\d+\s*%", " ", s)       # faixa ("21–40%") é rótulo, não contagem
    s = re.sub(r"\b(?:[Ff]iguras?|[Ss]eç(?:ão|ões)|[Tt]abelas?|[Pp]assos?|[Ff]ases?|[Pp]áginas?)\s+\d+(?:\.\d+)?", " ", s)
    for padrao in (r"`[^`]*`", r"!\[[^\]]*\]\([^)]*\)", r"\]\([^)]*\)", r"\b[0-9a-f]{16,}\b",
                   r"§\s?\d+(?:\.\d+)*", r"\b(?:QA|Q|T|L|ML|M|D-|R|E|C|F|P)\d+\b", r"\b(?:fig|tab)\d+\w*",
                   r"\bp\d{2}\b", r"\b\d{1,2}/\d{1,2}(?:/\d{2,4})?\b", r"\b(?:19|20)\d{2}\b"):
        s = re.sub(padrao, " ", s)
    return s


def tokens(s):
    return [m.group(0) for m in NUM.finditer(limpa(s))]


def valor(tok):
    """(número, casas decimais, é inteiro, é científico, algarismos significativos)."""
    t = tok.replace("−", "-")
    mant, _, exp = t.partition("e")
    casas = len(mant.split(",")[1]) if "," in mant else 0
    v = float(mant.replace(".", "").replace(",", ".")) * (10 ** int(exp) if exp else 1)
    sig = len(mant.replace("-", "").replace(".", "").replace(",", "").lstrip("0"))
    return v, casas, (casas == 0 and not exp), bool(exp), sig


def bate(token, outro):
    """O número `outro`, do relatório, é o mesmo `token` na precisão em que o token é exibido?"""
    v, casas, inteiro, cientifico, sig = valor(token)
    r, casas_r, inteiro_r, cientifico_r, sig_r = valor(outro)
    if inteiro:                       # inteiro só casa com o mesmo inteiro
        return inteiro_r and r == v
    if cientifico:                    # p-valor: os algarismos significativos exibidos
        if not sig <= sig_r <= sig + 1:
            return False
        return v != 0 and f"{r:.{sig - 1}e}" == f"{v:.{sig - 1}e}"
    # o número do relatório pode ter UMA casa a mais (0,622 sustenta 0,62), não duas:
    # 4,094 é a nota corrigida da linha vizinha, não sustenta a nota 4,1
    return (cientifico_r or casas <= casas_r <= casas + 1) and f"{r:.{casas}f}" == f"{v:.{casas}f}"


# ---------------------------------------------- palavras de uma afirmação
VAZIAS = {"para", "como", "mais", "menos", "entre", "sobre", "produtos", "produto", "base", "esse", "essa", "isso",
          "este", "esta", "quando", "onde", "pela", "pelo", "porque", "também", "ainda", "cada", "todo", "toda",
          "todos", "todas", "apenas", "quase", "muito", "mesmo", "outro", "outra", "dois", "duas", "três", "quatro",
          "cinco", "seis", "sete", "oito", "nove", "aqui", "ser", "são", "está", "estão", "foram", "sido", "tem",
          "têm", "fica", "ficam", "dele", "dela", "deles", "delas", "nesta", "neste", "desta", "deste", "após",
          "disponíveis", "cerca", "partir", "contra", "seja", "pode", "podem", "deve", "sem", "com", "nunca"}
_ALIASES = {"fones": ["headphones", "earbuds", "audio"], "climatizacao": ["heating", "cooling"],
            "categorias": ["familias"]}
POR_EXTENSO = {"3": "três", "28": "vinte e oito"}


def achatado(s):
    import unicodedata
    s = unicodedata.normalize("NFKD", s.casefold())
    return "".join(c for c in s if c.isalnum())


def raiz(w):
    """A raiz da palavra: sem plural e sem a vogal de gênero, até 6 caracteres — "mediano" e
    "mediana", "máximo" e "máxima", "avaliação" e "avaliações" ficam iguais."""
    w = re.sub(r"[aoe]$", "", re.sub(r"s$", "", achatado(w)))
    return w[:6]


ALIASES = {raiz(k): [raiz(a) for a in v] for k, v in _ALIASES.items()}


def palavras(s):
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", s)          # "OfficeProducts" → "Office Products"
    return {raiz(w) for w in re.findall(r"[A-Za-zÀ-ú]{4,}", s) if w.casefold() not in VAZIAS}


PALAVRA = re.compile(r"[A-Za-zÀ-ú]{4,}")


def sequencia(s):
    """Palavras e números na ordem do texto: [(“p”, palavra) | (“n”, número)]."""
    s = re.sub(r"(?<=[a-z])(?=[A-Z])", " ", limpa(s))
    itens = []
    for m in re.finditer(PALAVRA.pattern + "|" + NUM.pattern, s):
        g = m.group(0)
        if PALAVRA.fullmatch(g):
            if g.casefold() not in VAZIAS:
                itens.append(("p", raiz(g)))
        else:
            itens.append(("n", g))
    return itens


def ocorrencias(s, janela=8):
    """[(número, palavras a até `janela` itens dele)] — o contexto local de cada número."""
    itens = sequencia(s)
    saida = []
    for k, (tipo, v) in enumerate(itens):
        if tipo == "n":
            perto = {w for t_, w in itens[max(0, k - janela):k + janela + 1] if t_ == "p"}
            saida.append((v, perto))
    return saida


def casa_palavra(chave, unidade):
    return chave in unidade or any(a in unidade for a in ALIASES.get(chave, []))  # chaves já são raízes


def celulas(linha):
    return [c.strip() for c in re.split(r"(?<!\\)\|", linha.strip().strip("|"))]


# ------------------------------------------- o relatório em unidades
SEP = re.compile(r"^\|[\s:|-]+\|$")
UNIDADES = []          # (seção, título, números, palavras, é linha de tabela, texto)
secao, titulo, cabecalho = "—", "", ""
for k, ln in enumerate(LINHAS):
    m = re.match(r"^#{2,3} (?:(\d+(?:\.\d+)?)\.? )?(.*)$", ln)
    if m:
        secao = f"§{m.group(1)}" if m.group(1) else m.group(2).strip()
        titulo, cabecalho = m.group(2), ""
        continue
    if not ln.strip() or ln.startswith("#") or SEP.match(ln.strip()):
        continue
    if ln.startswith("|"):
        if k + 1 < len(LINHAS) and SEP.match(LINHAS[k + 1].strip()):
            cabecalho = ln                       # o cabeçalho dá contexto às linhas, não é suporte
            continue
        # numa linha de tabela, o contexto de cada número é a linha inteira mais o cabeçalho
        ctx = palavras(cabecalho + " " + ln)
        UNIDADES.append((secao, titulo, tokens(ln), ctx, True, ln, [(n, ctx) for n in tokens(ln)]))
        continue
    cabecalho = ""
    if ln.lstrip().startswith(("![", "> **Gerado")):
        continue                                 # legenda de figura não sustenta número
    # (a linha "*Fonte:" sustenta: com códigos e arquivos já limpos, ela declara base, n e taxas)
    UNIDADES.append((secao, titulo, tokens(ln), palavras(ln), False, ln, ocorrencias(ln)))

# O corpo que sustenta o sumário: as seções numeradas, menos a §10.3, que é
# cópia literal das quatro mensagens — suporte nela seria circular.
CORPO = [u for u in UNIDADES if u[0].startswith("§") and u[0] != "§10.3"]

# Palavra que aparece em muitos parágrafos ("nota", "desconto") não prova contexto.
# Conta só a palavra RARA no relatório — em até 2% das unidades.
from collections import Counter  # noqa: E402
FREQUENCIA = Counter(w for u in UNIDADES for w in u[3])
RARA = max(3, int(0.02 * len(UNIDADES)))


def raras(conjunto):
    return {w for w in conjunto if FREQUENCIA.get(w, 0) <= RARA}


# ------------------------------------------------- o sumário executivo
def trecho(titulo_inicio, titulo_fim):
    i = texto.index(titulo_inicio)
    return texto[i:texto.index(titulo_fim, i + 1)]


resumo = trecho("## Resumo Executivo", "### As duas definições que o grupo fechou")
definicoes = trecho("### As duas definições que o grupo fechou", "### As quatro mensagens para a liderança")
mensagens = trecho("### As quatro mensagens para a liderança", "## Artefatos e Links do Projeto")
recomendacoes = trecho("## Recomendações para o Negócio", "## Referências")
SUMARIO = [resumo, definicoes, mensagens, recomendacoes]


def afirmacoes(md):
    """[(afirmação, cabeçalho)] — cada frase de parágrafo e cada linha de tabela, com o cabeçalho dela."""
    saida, cab = [], ""
    for k, ln in enumerate(md.split("\n")):
        if not ln.strip() or ln.startswith("#") or SEP.match(ln.strip()) or ln.strip() == "---":
            continue
        if ln.startswith("|"):
            if cab == "":
                cab = ln
                continue
            saida.append((ln, cab))
            continue
        cab = ""
        ln = re.sub(r"^\*\*\d+\s*[·.]\s*", "**", ln)          # numeração de lista não é número
        for frase in re.split(r"(?<=[.;!?])\s+(?=[A-ZÁÉÍÓÚ*\"“(])", ln):
            saida.append((frase, ""))
    return saida


# 782 = produtos de B + D: as parcelas precisam estar NAS LINHAS DOS GRUPOS da tabela de arquétipos.
DERIVADOS = {"782": (("B", "335"), ("D", "447"))}
for total, parcelas in DERIVADOS.items():
    for grupo, parcela in parcelas:
        assert any(u[4] and re.search(rf"\|\s*\**{grupo}\s*—", u[5]) and any(bate(parcela, n) for n in u[2])
                   for u in CORPO), f"{total}: a parcela {parcela} não está na linha do grupo {grupo}"
    assert sum(valor(p_)[0] for _, p_ in parcelas) == valor(total)[0], f"{total} ≠ soma das parcelas"
# As parcelas já foram conferidas na linha exata do seu grupo — mais forte que o contexto da frase.
CONFERIDOS_NA_LINHA = {p_ for parcelas in DERIVADOS.values() for _, p_ in parcelas}

_ESPECIFICIDADE = {}


def especificidade(tok):
    """Em quantos parágrafos do corpo o número aparece — 1.348 aparece em 124, 12,7 em um."""
    if tok not in _ESPECIFICIDADE:
        _ESPECIFICIDADE[tok] = sum(any(bate(tok, n) for n in u[2]) for u in CORPO)
    return _ESPECIFICIDADE[tok]


# "39 (12,7%)": o número e o seu parêntese são UMA afirmação — o par tem de estar junto no corpo.
PAR = re.compile(r"(" + NUM.pattern + r")\**\s*\(\s*\**(" + NUM.pattern + r")")


def pares(frase):
    return {a: b for a, b in PAR.findall(limpa(frase))}


def evidencia(comuns, co_numeros):
    """Quanto um parágrafo do corpo prova que fala da MESMA coisa que a frase do sumário.
    Palavra rara em comum prova sozinha (3). Palavra comum vale 1 — "nota", "avaliações" estão
    em centenas de parágrafos. Outro número da frase presente no parágrafo vale 2 se for raro no
    relatório e 1 se for comum ("1.348", "4,0", "2" estão em dezenas). Sustenta com 3 ou mais, e
    sempre com ao menos uma palavra em comum."""
    if not comuns:
        return 0
    pontos = 3 * len(raras(comuns)) + len(comuns - raras(comuns))
    return pontos + sum(2 if especificidade(o) <= RARA else 1 for o in co_numeros)


def sustentado(tok, perto, outros, parceiro=None):
    """O número aparece no corpo num parágrafo com evidência suficiente de ser a mesma afirmação.
    Se o número traz um parêntese ("39 (12,7%)"), o parágrafo tem de trazer o parêntese também."""
    for u in CORPO:
        if parceiro and not any(bate(parceiro, m) for m in u[2]):
            continue
        co = {o for o in outros if any(bate(o, m) for m in u[2])}
        for n, ctx in u[6]:
            if bate(tok, n) and evidencia({c for c in perto if casa_palavra(c, ctx)}, co) >= 3:
                return True
    return False


def ocorrencias_tabela(cab, linha):
    """Numa linha de tabela do sumário, o contexto de um número é a vizinhança dele na CÉLULA,
    mais o rótulo da linha (1ª célula) e o título da coluna — não a linha inteira, que mistura
    o que cada célula afirma."""
    titulos, cels = celulas(cab), celulas(linha)
    saida = []
    for j, c in enumerate(cels):
        rotulo = palavras(cels[0] + " " + (titulos[j] if j < len(titulos) else ""))
        saida += [(n, perto | rotulo, tokens(c)) for n, perto in ocorrencias(c)]
    return saida


sem_suporte = []
for parte in SUMARIO:
    for frase, cab in afirmacoes(parte):
        e_tabela = frase.startswith("|")
        numeros = tokens(frase)
        par = pares(frase)
        # na tabela, os "outros números" são os da mesma célula — a linha mistura afirmações
        itens = ocorrencias_tabela(cab, frase) if e_tabela else [(n, p_, numeros) for n, p_ in ocorrencias(frase)]
        for tok, perto, vizinhos in itens:
            if tok in DERIVADOS or tok in CONFERIDOS_NA_LINHA:
                continue
            outros = [o for o in vizinhos if o != tok and o not in DERIVADOS]
            if not sustentado(tok, perto, outros, par.get(tok)):
                sem_suporte.append(f"{tok} em “{frase[:70]}…”")
assert not sem_suporte, "o sumário afirma números que o corpo do relatório não sustenta:\n  " + "\n  ".join(sem_suporte)

# --------------------------------------------------- a folha de defesa
roteiro = list(csv.DictReader(open(ROTEIRO_NUMEROS, encoding="utf-8")))
roteiro.sort(key=lambda r: int(r["bloco_do_video"].split()[0]))      # ordem dos blocos do vídeo
CODIGO = re.compile(r"\b(?:QA\d|Q\d|ML\d)\b")


def numeros_da_linha(r):
    v = re.sub(r"\brho\b|p\.p\.", " ", r["valor"]).replace("x", " ").replace("+-", " ")
    return tokens(v)


def satisfeito(tok, u):
    return any(bate(tok, n) for n in u[2]) or (tok in POR_EXTENSO and POR_EXTENSO[tok] in u[5].casefold())


def candidatas(r):
    toks = numeros_da_linha(r)
    chaves = palavras(r["indicador"])
    # o número escrito no próprio indicador ("as 3 maiores", "nota < 4,0") também é parte da afirmação
    num_indicador = tokens(re.sub(r"\bk\s*=\s*\d+", " ", r["indicador"]))
    n = int(r["n"])
    n_tok = f"{n:,}".replace(",", ".")
    codigos = set(CODIGO.findall(r["indicador"] + " " + r["regra"]))
    comum = any(especificidade(t_) > 3 for t_ in toks if t_ not in POR_EXTENSO)
    tamanho_de_base = [valor(t_)[0] for t_ in toks] == [n]      # "1.348 produtos": o valor é o próprio n
    k_ind = re.search(r"\bk\s*=\s*(\d+)", r["indicador"])
    saida = []
    for u in UNIDADES:
        if not u[0].startswith("§") or u[0] == "§10.3":
            continue
        if not all(satisfeito(t, u) for t in toks):
            continue
        # o título da seção é contexto de todo parágrafo dela: "Estado: respondida. Sim — 19 produtos."
        # responde à pergunta do título "Q5 · Existem produtos com alto engajamento e baixa avaliação?"
        titulo_u = palavras(u[1])
        no_titulo = {c for c in chaves if casa_palavra(c, titulo_u)}
        casadas = {c for c in chaves if casa_palavra(c, u[3])} | no_titulo
        numeros_casados = [t_ for t_ in num_indicador if satisfeito(t_, u)]
        if not casadas and not numeros_casados:
            continue
        codigo_aqui = bool(codigos & set(CODIGO.findall(u[5] + " " + u[1])))
        if codigos and not codigo_aqui:
            continue                                   # linha de Q5 só se sustenta onde se fala de Q5
        # Numa tabela, a linha cuja PRIMEIRA célula é o nome do grupo e que traz o valor é a
        # medição dele — "| Electronics | 490 | sim |" não é citação de passagem. Isso vale 2,
        # como uma palavra rara: sem isso, a regra dependia de "Electronics" ser rara no
        # relatório, e bastou a §7.7 citar a categoria seis vezes para o suporte sumir.
        rotulo_casa = u[4] and any(casa_palavra(c, palavras(celulas(u[5])[0])) for c in chaves)
        # número comum no relatório ("50%", "5", "0,62"): a régua do sumário, um ponto abaixo — a
        # linha do roteiro já exige todos os números do valor no mesmo parágrafo, o código e o n.
        # O código do indicador no parágrafo (ou no título da seção) vale 2.
        if comum and not tamanho_de_base and \
                evidencia(casadas, numeros_casados) + 2 * codigo_aqui + 2 * rotulo_casa < 2:
            continue
        if k_ind and not all(re.search(rf"k\s*=\s*{k_ind.group(1)}\s*→\s*\**\s*{re.escape(t_)}", u[5])
                             for t_ in toks if "," in t_):
            continue                                   # silhueta: o valor tem de vir colado ao k certo
        por_extenso = any(t_ in POR_EXTENSO and POR_EXTENSO[t_] in u[5].casefold() for t_ in toks)
        if not u[4] and not por_extenso and not no_titulo and not any(
                any(bate(t_, m_) for t_ in toks) and any(casa_palavra(c, ctx) for c in chaves) for m_, ctx in u[6]):
            continue                                   # em prosa, o número tem de estar PERTO das palavras
        if n != 1348 and n_tok not in toks and not any(bate(n_tok, x) for x in u[2]):
            continue                                   # subconjunto: o n tem de estar junto
        analitico = bool(re.match(r"§[2-9]\.", u[0]))
        nota = (len(codigos & set(CODIGO.findall(u[1]))), len(no_titulo), len(raras(casadas)),
                rotulo_casa, len(casadas) + len(numeros_casados), u[4], analitico)
        saida.append((nota, u[0]))
    return sorted(saida, reverse=True)


# Onde a heurística escolhe uma seção que só CITA o número, a seção que o MEDE é
# declarada aqui — e conferida: ela precisa passar pelas mesmas exigências.
SECAO_DECLARADA = {
    "produtos na base analítica": "§2.4",
    "categorias de nível 1 na base": "§2.6",
    "produtos nas categorias abaixo do piso": "§2.6",
    "cobertura das 3 maiores categorias": "§2.6",
    "produtos em Electronics": "§2.6",
    "produtos em Home&Kitchen": "§2.6",
    "produtos em Computers&Accessories": "§2.6",
    "produtos em OfficeProducts": "§2.6",
    "preço de tabela mediano (rupia, sem conversão)": "§2.5",
    "produtos com nota < 4,0": "§4.5",
    "taxa da base abaixo de 4,0 — para comparação": "§5.18",
    "referências de avaliação na base": "§7.3",
    "nota mediana": "§2.5",
    "desconto mediano": "§2.5",
    "volume mediano de avaliações": "§4.3",
    "corte de engajamento alto (p90 de avaliações)": "§4.3",
    "produtos com nota >= 4,3": "§4.5",
    "Spearman desconto × engajamento": "§5.5",
    "Spearman engajamento × nota": "§5.5",
    "Q6 — funil: nota >= 4,3 e volume abaixo da mediana": "§5.8",
    "conflito B × D — distância de desconto": "§5.17",
    "avaliações por produto — média e máximo": "§7.5",
    "fones — produtos abaixo de 4,0": "§5.18",
    "climatização — produtos abaixo de 4,0": "§5.18",
}
# Quando a frase que mede o número traz, ao lado, outro número do mesmo tipo — "apenas 4 alcançam
# 30 produtos, e as outras 5 somam 7"; "o p de QA4 vai de 0,236 para 0,228" sem desempate —,
# estar no parágrafo não basta: o número tem de estar NA POSIÇÃO em que é medido. Os grupos da
# expressão trazem os números na ordem em que o roteiro os lista.
ANCORAS = {
    "categorias com n >= 30 (T2)": ("§2.6", r"apenas (\d+) alcançam 30 produtos"),
    "Spearman preço de tabela × nota": (
        "§5.14", r"\|\s*\*\*Preço de tabela × nota\*\*\s*\|\s*\*\*([+−-]?\d+,\d+)\*\*\s*\|\s*\*\*(\d+,\d+)\*\*"),
}


def ancorado(r):
    secao_a, expressao = ANCORAS[r["indicador"]]
    toks = numeros_da_linha(r)
    for u in UNIDADES:
        if u[0] != secao_a:
            continue
        for m in re.finditer(expressao, u[5]):
            medidos = [t_ for g_ in m.groups() for t_ in tokens(g_)]
            if len(medidos) == len(toks) and all(bate(a, b) for a, b in zip(toks, medidos)):
                return True
    return False


# A base e o n precisam ser coerentes entre si: cada base oficial tem o seu n.
BASES = {"Bruta": 1465, "Produtos": 1351}
defesa, nao_achados = [], []
for r in roteiro:
    n_linha = int(r["n"])
    if (r["base"] in BASES and n_linha != BASES[r["base"]]) or (r["base"] == "Analítica" and n_linha > 1348) \
            or r["base"] not in set(BASES) | {"Analítica"}:
        nao_achados.append(f"{r['indicador']}: base {r['base']} incoerente com n = {n_linha}")
        continue
    cands = candidatas(r)
    if not cands:
        nao_achados.append(f"{r['indicador']} = {r['valor']}")
        continue
    escolhida = cands[0][1]
    if r["indicador"] in ANCORAS:
        if not ancorado(r):
            nao_achados.append(f"{r['indicador']} = {r['valor']}: fora da posição em que o relatório o mede "
                               f"({ANCORAS[r['indicador']][0]})")
            continue
        escolhida = ANCORAS[r["indicador"]][0]
    declarada = SECAO_DECLARADA.get(r["indicador"])
    if declarada:
        assert declarada in {c[1] for c in cands}, \
            f"seção declarada {declarada} não sustenta '{r['indicador']}' (candidatas: {sorted({c[1] for c in cands})})"
        escolhida = declarada
    defesa.append({**r, "secao": escolhida})
assert not nao_achados, "números falados no vídeo que o relatório não sustenta:\n  " + "\n  ".join(nao_achados)
usadas = {r["indicador"] for r in roteiro}
assert set(SECAO_DECLARADA) | set(ANCORAS) <= usadas, \
    f"seção declarada para indicador inexistente: {(set(SECAO_DECLARADA) | set(ANCORAS)) - usadas}"
assert not set(SECAO_DECLARADA) & set(ANCORAS), "indicador declarado duas vezes"

regras = {}
guia = open(GUIA, encoding="utf-8").read()
for m in re.finditer(r"^\| \*\*(T\d)\*\* \| (.+?) \|$", guia, flags=re.M):
    regras[m.group(1)] = re.sub(r"[*`]", "", m.group(2))
for m in re.finditer(r"^## (L\d)\. (.+)$", open(LIMITACOES, encoding="utf-8").read(), flags=re.M):
    regras[m.group(1)] = m.group(2).strip()
assert len(regras) == 17, f"esperadas 9 regras e 8 limitações, achadas {len(regras)}"


def exibe(v):
    """O valor como o material escreve: ρ, separador de milhar, menos tipográfico, traço de faixa, ±."""
    v = v.replace("rho ", "ρ ").replace("+-", "±").replace(">=", "≥").replace("<=", "≤")
    v = re.sub(r"(?<=\d)-(?=\d)", "–", v)                       # faixa
    v = re.sub(r"(?<![\w])-(?=\d)", "−", v)                       # sinal
    v = re.sub(r"e-(?=\d)", "e−", v)
    return re.sub(r"(?<![\d.,])(\d{4,})(?![\d,])", lambda m: f"{int(m.group(1)):,}".replace(",", "."), v)


# ------------------------------------------------------------ desenho
from reportlab.lib import colors  # noqa: E402
from reportlab.lib.fonts import addMapping  # noqa: E402
from reportlab.lib.pagesizes import A4, landscape  # noqa: E402
from reportlab.lib.styles import ParagraphStyle  # noqa: E402
from reportlab.lib.units import cm  # noqa: E402
from reportlab.pdfbase import pdfmetrics  # noqa: E402
from reportlab.pdfbase.ttfonts import TTFont  # noqa: E402
from reportlab.platypus import KeepTogether, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle  # noqa: E402
from pypdf import PdfReader  # noqa: E402

fixar_reportlab()

for nome, arq in [("DejaVu", "DejaVuSans.ttf"), ("DejaVu-Bold", "DejaVuSans-Bold.ttf"),
                  ("DejaVu-Obl", "DejaVuSans-Oblique.ttf"), ("DejaVu-BoldObl", "DejaVuSans-BoldOblique.ttf"),
                  ("DejaVuMono", "DejaVuSansMono.ttf")]:
    pdfmetrics.registerFont(TTFont(nome, os.path.join(FONTES, arq)))
addMapping("DejaVu", 0, 0, "DejaVu")
addMapping("DejaVu", 1, 0, "DejaVu-Bold")
addMapping("DejaVu", 0, 1, "DejaVu-Obl")
addMapping("DejaVu", 1, 1, "DejaVu-BoldObl")
TINTA, SEC = colors.HexColor(ESTRUTURA["tinta"]), colors.HexColor(ESTRUTURA["secundario"])
GRADE, DIVISOR = colors.HexColor(ESTRUTURA["grade"]), colors.HexColor(BASE["divisor"])


CREDITOS = ("Tech Challenge Fase 4 · POSTECH DTAT · Grupo 12 — Efraim Oliveira · Érica Tarsis · Ricardo Moraes · "
            "Rodrigo Bernardino · Thiago Galvão. Extraído do relatório técnico v1; cada § remete à seção que sustenta "
            "o número. Base analítica: n = 1.348 produtos · 9.255 avaliações.")
RODAPE = ("Fonte: Amazon Sales Dataset (Kaggle) · base analítica n = 1.348 · valores em rupia indiana, sem conversão (L5) · "
          "volume de avaliações, nunca vendas (T6/L4)")


def sem_quebra(s):
    """ "ρ = −0,150" e "p = 0,236" não quebram na linha."""
    return re.sub(r"(?<![\w])([ρpnk]) = ", "\\1\u00a0=\u00a0", s)


def rico(s):
    s = sem_quebra(s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;"))
    s = re.sub(r"\*\*([^*]+)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)", r"<i>\1</i>", s)
    return re.sub(r"`([^`]+)`", r'<font face="DejaVuMono">\1</font>', s)


def blocos(md):
    """[(tipo, conteúdo)] — título, parágrafo ou tabela."""
    saida, i, L = [], 0, md.split("\n")
    while i < len(L):
        ln = L[i].rstrip()
        if not ln.strip() or ln.strip() == "---":
            i += 1
            continue
        if ln.startswith("#"):
            saida.append(("titulo", ln.lstrip("#").strip()))
            i += 1
        elif ln.startswith("|"):
            linhas = []
            while i < len(L) and L[i].startswith("|"):
                linhas.append(celulas(L[i]))
                i += 1
            saida.append(("tabela", [linhas[0]] + linhas[2:]))
        else:
            saida.append(("paragrafo", ln.strip()))
            i += 1
    return saida


# ------------------------------------------------- sumário · PDF
corpo_st = ParagraphStyle("c", fontName="DejaVu", fontSize=9.1, leading=12.1, textColor=TINTA, spaceAfter=4.5)
h_st = ParagraphStyle("h", fontName="DejaVu-Bold", fontSize=11.2, leading=14, textColor=TINTA, spaceBefore=6, spaceAfter=3,
                      keepWithNext=1)
cel_st = ParagraphStyle("t", fontName="DejaVu", fontSize=8, leading=9.8, textColor=TINTA)
cab_st = ParagraphStyle("tc", parent=cel_st, fontName="DejaVu-Bold", textColor=colors.white)
tit_st = ParagraphStyle("tt", fontName="DejaVu-Bold", fontSize=15, leading=18, textColor=TINTA)
sub_st = ParagraphStyle("st", fontName="DejaVu", fontSize=8.2, leading=10.5, textColor=SEC, spaceAfter=6)
LARGURA = A4[0] - 3.2 * cm

fluxo = [Paragraph("Sumário Executivo — Amazon Product Performance &amp; Customer Insights", tit_st),
         Paragraph(rico(CREDITOS), sub_st)]
for parte in SUMARIO:
    for tipo, cont in blocos(parte):
        if tipo == "titulo":
            fluxo.append(Paragraph(rico(cont.replace("Resumo Executivo", "Resumo")), h_st))
        elif tipo == "paragrafo":
            fluxo.append(Paragraph(rico(cont), corpo_st))
        else:
            n_col = len(cont[0])
            dados = [[Paragraph(rico(c), cab_st) for c in cont[0]]] + \
                    [[Paragraph(rico(c), cel_st) for c in lin[:n_col]] for lin in cont[1:]]
            t = Table(dados, colWidths=[LARGURA * f for f in (0.30, 0.38, 0.32)][:n_col], repeatRows=1)
            t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), TINTA),
                                   ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, DIVISOR]),
                                   ("GRID", (0, 0), (-1, -1), 0.4, GRADE), ("VALIGN", (0, 0), (-1, -1), "TOP"),
                                   ("TOPPADDING", (0, 0), (-1, -1), 2.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 2.5)]))
            # cabeçalho sozinho no pé da página não serve: a tabela vai inteira para a página seguinte
            fluxo += [KeepTogether([t]), Spacer(1, 5)]


def rodape(canvas, doc):
    canvas.saveState()
    canvas.setFont("DejaVu", 6.8)
    canvas.setFillColor(SEC)
    canvas.drawCentredString(A4[0] / 2, 0.9 * cm, RODAPE)
    canvas.drawRightString(A4[0] - 1.6 * cm, A4[1] - 0.8 * cm, f"Sumário executivo · {doc.page}/2")
    canvas.restoreState()


SimpleDocTemplate(SAIDA_SUMARIO + ".pdf", pagesize=A4, leftMargin=1.6 * cm, rightMargin=1.6 * cm,
                  topMargin=1.4 * cm, bottomMargin=1.5 * cm, title="Sumário Executivo — Tech Challenge Fase 4",
                  author="Grupo 12 — POSTECH DTAT").build(fluxo, onFirstPage=rodape, onLaterPages=rodape)
datar_pdf(SAIDA_SUMARIO + ".pdf")
paginas_sumario = len(PdfReader(SAIDA_SUMARIO + ".pdf").pages)
assert paginas_sumario <= 2, f"o sumário executivo precisa caber em 2 páginas; saiu com {paginas_sumario}"

# ------------------------------------------------- sumário · DOCX
from docx import Document  # noqa: E402
from docx.enum.text import WD_ALIGN_PARAGRAPH  # noqa: E402
from docx.oxml import OxmlElement  # noqa: E402
from docx.oxml.ns import qn  # noqa: E402
from docx.shared import Cm, Pt  # noqa: E402


def runs(paragrafo, s, tamanho):
    for pedaco in re.split(r"(\*\*[^*]+\*\*|(?<!\*)\*[^*]+\*(?!\*)|`[^`]+`)", s):
        if not pedaco:
            continue
        negrito, italico = pedaco.startswith("**"), pedaco.startswith("*") and not pedaco.startswith("**")
        r = paragrafo.add_run(sem_quebra(pedaco.strip("*`")))
        r.bold, r.italic = negrito, italico
        r.font.size = Pt(tamanho)


doc = Document()
for s in doc.sections:
    s.left_margin = s.right_margin = Cm(1.6)
    s.top_margin = s.bottom_margin = Cm(1.4)
doc.styles["Normal"].font.name = "Calibri"
doc.add_heading("Sumário Executivo — Amazon Product Performance & Customer Insights", level=1)
runs(doc.add_paragraph(), CREDITOS, 8.5)
# o mesmo rodapé do PDF, com o número da página
rodape_docx = doc.sections[0].footer.paragraphs[0]
rodape_docx.alignment = WD_ALIGN_PARAGRAPH.CENTER
runs(rodape_docx, RODAPE + " · página ", 7)
campo = OxmlElement("w:fldSimple")
campo.set(qn("w:instr"), "PAGE")
rodape_docx._p.append(campo)
for parte in SUMARIO:
    for tipo, cont in blocos(parte):
        if tipo == "titulo":
            doc.add_heading(cont.replace("Resumo Executivo", "Resumo"), level=2)
        elif tipo == "paragrafo":
            runs(doc.add_paragraph(), cont, 9)
        else:
            t = doc.add_table(rows=0, cols=len(cont[0]))
            t.style = "Table Grid"
            for i, lin in enumerate(cont):
                cells = t.add_row().cells
                for j, c in enumerate(lin[:len(cont[0])]):
                    cells[j].text = ""
                    runs(cells[j].paragraphs[0], f"**{c}**" if i == 0 and not c.startswith("**") else c, 8)
cp = doc.core_properties
cp.author, cp.title = "Grupo 12 — POSTECH DTAT", "Sumário Executivo — Tech Challenge Fase 4"
cp.comments = ""
fixar_propriedades(cp)
doc.save(SAIDA_SUMARIO + ".docx")
fixar_docx(SAIDA_SUMARIO + ".docx")

# --------------------------------------------- folha de defesa · PDF + MD
d_cel = ParagraphStyle("d", fontName="DejaVu", fontSize=6.1, leading=6.8, textColor=TINTA)
d_cab = ParagraphStyle("dc", parent=d_cel, fontName="DejaVu-Bold", textColor=colors.white)
d_val = ParagraphStyle("dv", parent=d_cel, fontName="DejaVu-Bold")
dados = [[Paragraph(c, d_cab) for c in ("Bloco", "Valor falado", "Indicador", "Base · n", "Onde está", "Regra que o protege")]]
bloco_anterior = None
inicio_bloco = []
for i, r in enumerate(defesa, start=1):
    bloco = r["bloco_do_video"]
    if bloco != bloco_anterior:
        inicio_bloco.append(i)
    dados.append([Paragraph(rico(bloco) if bloco != bloco_anterior else "", d_cel),
                  Paragraph(rico(exibe(r["valor"])), d_val),
                  Paragraph(rico(exibe(r["indicador"])), d_cel),
                  Paragraph(f"{r['base']} · {exibe(r['n'])}", d_cel),
                  Paragraph(r["secao"], d_cel),
                  Paragraph(rico(exibe(r["regra"])) or "—", d_cel)])
    bloco_anterior = bloco
larg = [2.75 * cm, 3.7 * cm, 6.6 * cm, 2.2 * cm, 1.5 * cm, 10.95 * cm]        # soma 27,7 cm
tabela = Table(dados, colWidths=larg, repeatRows=1)
estilo = [("BACKGROUND", (0, 0), (-1, 0), TINTA), ("GRID", (0, 0), (-1, -1), 0.3, GRADE),
          ("VALIGN", (0, 0), (-1, -1), "TOP"),
          ("TOPPADDING", (0, 0), (-1, -1), 0.55), ("BOTTOMPADDING", (0, 0), (-1, -1), 0.55),
          ("LEFTPADDING", (0, 0), (-1, -1), 2.2), ("RIGHTPADDING", (0, 0), (-1, -1), 2.2)]
for k, ini in enumerate(inicio_bloco):
    if k % 2:
        fim = (inicio_bloco[k + 1] - 1) if k + 1 < len(inicio_bloco) else len(defesa)
        estilo.append(("BACKGROUND", (0, ini), (-1, fim), DIVISOR))
tabela.setStyle(TableStyle(estilo))
# A legenda traz só os códigos que a folha usa — os demais estão no relatório (§8.2).
usados = {c for r in defesa for c in re.findall(r"\b[TL]\d\b", r["regra"])}
legenda = " · ".join(f"<b>{k}</b> {v}" for k, v in sorted(regras.items(), key=lambda kv: (kv[0][0] != "T", kv[0]))
                     if k in usados)
d_tit = ParagraphStyle("dt", fontName="DejaVu-Bold", fontSize=11.5, leading=13.5, textColor=TINTA)
d_sub = ParagraphStyle("ds", fontName="DejaVu", fontSize=6.3, leading=7.6, textColor=SEC)
SimpleDocTemplate(SAIDA_DEFESA + ".pdf", pagesize=landscape(A4), leftMargin=1 * cm, rightMargin=1 * cm,
                  topMargin=0.55 * cm, bottomMargin=0.45 * cm, title="Folha de defesa — Tech Challenge Fase 4",
                  author="Grupo 12 — POSTECH DTAT").build([
    Paragraph(f"Folha de defesa — os {len(defesa)} números falados no vídeo, e onde cada um se sustenta", d_tit),
    Paragraph("Fonte: 04_video/tab_roteiro_numeros.csv · cada número localizado no relatório técnico v1 (§ = seção) · "
              "gerada por src/gera_resumo.py, que falha se um número falado não estiver no relatório.", d_sub),
    Spacer(1, 3), tabela, Spacer(1, 3), Paragraph(legenda, d_sub)])
datar_pdf(SAIDA_DEFESA + ".pdf")
paginas_defesa = len(PdfReader(SAIDA_DEFESA + ".pdf").pages)
assert paginas_defesa == 1, f"a folha de defesa precisa caber em 1 página; saiu com {paginas_defesa}"

md = [f"# Folha de defesa — os {len(defesa)} números falados no vídeo", "",
      "> **Gerada por `src/gera_resumo.py`. Não editar à mão.** Lê `04_video/tab_roteiro_numeros.csv` e localiza cada "
      "número no relatório técnico; falha se um número falado não estiver no relatório. Para imprimir: "
      "`defense_sheet_phase4_v1_powerbi.pdf`.", "",
      "| Bloco | Valor falado | Indicador | Base · n | Onde está | Regra que o protege |", "|---|---|---|---|---|---|"]
for r in defesa:
    md.append(f"| {r['bloco_do_video']} | **{exibe(r['valor'])}** | {exibe(r['indicador'])} | "
              f"{r['base']} · {exibe(r['n'])} | {r['secao']} | {exibe(r['regra']) or '—'} |")
md += ["", "**Regras e limitações citadas:** " + " · ".join(f"**{k}** {v}" for k, v in
       sorted(regras.items(), key=lambda kv: (kv[0][0] != "T", kv[0])) if k in usados), ""]
open(SAIDA_DEFESA + ".md", "w", encoding="utf-8").write("\n".join(md))

print(f"  {SAIDA_SUMARIO}.pdf · {paginas_sumario} páginas · .docx")
print(f"  {SAIDA_DEFESA}.pdf · {paginas_defesa} página · .md · {len(defesa)} números localizados")

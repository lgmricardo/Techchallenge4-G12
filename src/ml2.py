# -*- coding: utf-8 -*-
"""
ML2 — validação do modelo de atributos associados à baixa satisfação.

POR QUE ESTE ARQUIVO EXISTE
---------------------------
O ML2 era calculado em TRÊS lugares (`gera_figuras.py`, `04_analises.ipynb` e
`numeros_roteiro.py`), cada um com a sua cópia da validação cruzada. Três cópias do
mesmo cálculo é a classe de defeito que este projeto mais encontrou: bastava uma delas
mudar para que figura, notebook e tabela do vídeo publicassem AUCs diferentes.

E havia um defeito dentro da cópia, comum às três. A validação era
`StratifiedKFold(5, shuffle=True)`, que sorteia produto por produto. Só que a L8 declara
que **254 produtos (96 grupos) são listagens-gêmeas**: variantes do mesmo anúncio,
com exatamente o mesmo par `(rating_count, rating)`. O alvo do ML2 é `nota < 4,0` e
`avaliacoes` é preditor — então, quando uma gêmea cai no treino e a outra no teste, o
modelo recebe de graça o rótulo que deveria prever. É vazamento de dado, e o AUC
publicado (0,75) estava inflado.

Medido em 31/10/2026, mesma especificação, só trocando o corte das partições:

    bloco                     ingênua   agrupada
    volume                      0,620      0,556   ← quase acaso
    comerciais                  0,624      0,585
    comerciais + categoria      0,691      ver tab27
    completo                    0,746      0,705

A correção é agrupar: **todas as gêmeas de um anúncio ficam na mesma partição**.
`StratifiedGroupKFold` mantém a proporção do alvo e o embaralhamento, e nunca separa um
grupo. O grupo é definido pela mesma regra da L8 — o par `(avaliacoes, nota)` repetido —,
de modo que o ML2 passa a obedecer à limitação que o projeto já declarava.
"""

from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedGroupKFold, StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

SEMENTE = 42
ARVORES = 300
PARTICOES = 5
LIMIAR = 4.0          # alvo: nota < 4,0 — o mesmo limiar de todos os cortes operacionais


def grupos_de_variantes(base):
    """Um identificador por anúncio: produtos com o mesmo par (avaliacoes, nota) são gêmeos (L8)."""
    return base.groupby(["avaliacoes", "nota"]).ngroup().to_numpy()


def alvo(base):
    return (base.nota < LIMIAR).astype(int)


def monta(num, categ):
    """Pipeline com o pré-processamento DENTRO de cada partição — nada é ajustado no teste."""
    passos = [("n", StandardScaler(), num)]
    if categ:
        passos.append(("c", OneHotEncoder(handle_unknown="ignore"), categ))
    return Pipeline([("pre", ColumnTransformer(passos)),
                     ("rf", RandomForestClassifier(n_estimators=ARVORES, random_state=SEMENTE))])


def auc(base, num, categ, agrupar=True):
    """Escores de AUC por partição. `agrupar=False` reproduz a validação ingênua, só para medir o vazamento."""
    y = alvo(base)
    colunas = list(num) + list(categ)
    if agrupar:
        cv = StratifiedGroupKFold(PARTICOES, shuffle=True, random_state=SEMENTE)
        return cross_val_score(monta(num, categ), base[colunas], y, cv=cv,
                               groups=grupos_de_variantes(base), scoring="roc_auc")
    cv = StratifiedKFold(PARTICOES, shuffle=True, random_state=SEMENTE)
    return cross_val_score(monta(num, categ), base[colunas], y, cv=cv, scoring="roc_auc")

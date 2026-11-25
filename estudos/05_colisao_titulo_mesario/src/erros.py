#!/usr/bin/env python3
"""
erros.py -- modelo de erro de digitacao de 12 digitos e taxa de "erro que gera titulo valido" (p2).

Tipos de erro (um evento por digitacao errada):
  sub   : substituicao de um digito por qualquer outro (9 alternativas, uniforme)
  adj   : substituicao por digito vizinho no teclado da urna (layout 1-2-3 / 4-5-6 / 7-8-9 / 0)
  trans : transposicao de digitos adjacentes (ab -> ba, a != b)
  salto : transposicao com salto (abc -> cba, a != c)
  gemeo : erro gemeo (aa -> bb)
Mistura a priori (Verhoeff, 1969, apud Gallian, 1991): substituicao 79,1%, transposicao adjacente 10,2%,
transposicao com salto 0,8%, gemeo 0,6%; o restante (9,3%) e alocado a 'adj'. A mistura e recalibrada com
os quase-duplicados observados dentro da mesma secao (ver classificar_par).
"""
import itertools
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parsing import titulo_valido  # noqa: E402

MISTURA_PRIORI = {"sub": 0.791, "adj": 0.093, "trans": 0.102, "salto": 0.008, "gemeo": 0.006}
TECLADO = {"1": "24", "2": "135", "3": "26", "4": "157", "5": "2468", "6": "359",
           "7": "48", "8": "5790", "9": "68", "0": "8"}


def vizinhos(t, tipo):
    """Lista de todos os resultados possiveis (equiprovaveis) de um erro do tipo dado sobre o titulo t."""
    out = []
    L = len(t)
    if tipo == "sub":
        for i in range(L):
            for c in "0123456789":
                if c != t[i]:
                    out.append(t[:i] + c + t[i + 1:])
    elif tipo == "adj":
        for i in range(L):
            for c in TECLADO[t[i]]:
                out.append(t[:i] + c + t[i + 1:])
    elif tipo == "trans":
        for i in range(L - 1):
            if t[i] != t[i + 1]:
                out.append(t[:i] + t[i + 1] + t[i] + t[i + 2:])
    elif tipo == "salto":
        for i in range(L - 2):
            if t[i] != t[i + 2]:
                out.append(t[:i] + t[i + 2] + t[i + 1] + t[i] + t[i + 3:])
    elif tipo == "gemeo":
        for i in range(L - 1):
            if t[i] == t[i + 1]:
                for c in "0123456789":
                    if c != t[i]:
                        out.append(t[:i] + c + c + t[i + 2:])
    return out


def p2_titulo(t, tipo):
    v = vizinhos(t, tipo)
    if not v:
        return 0.0, 0
    k = sum(titulo_valido(x) for x in v)
    return k / len(v), len(v)


def classificar_par(a, b):
    """Classifica a relacao entre dois titulos de 12 digitos: tipo de erro unico que leva a em b, ou None."""
    if a == b or len(a) != len(b):
        return None
    dif = [i for i in range(len(a)) if a[i] != b[i]]
    if len(dif) == 1:
        i = dif[0]
        return "adj" if b[i] in TECLADO[a[i]] else "sub"
    if len(dif) == 2:
        i, j = dif
        if j == i + 1 and a[i] == b[j] and a[j] == b[i]:
            return "trans"
        if j == i + 1 and a[i] == a[j] and b[i] == b[j]:
            return "gemeo"
        if j == i + 2 and a[i] == b[j] and a[j] == b[i]:
            return "salto"
    return None


if __name__ == "__main__":
    import csv
    import collections
    import statistics
    regs = list(csv.DictReader(open(sys.argv[1], encoding="utf-8")))
    tit = sorted({r["titulo"] for r in regs})
    print("titulos unicos:", len(tit))
    p2 = {}
    for tp in MISTURA_PRIORI:
        p2[tp] = statistics.mean(p2_titulo(t, tp)[0] for t in tit)
        print(f"p2[{tp}] = {p2[tp]:.5f}")
    pbar = sum(MISTURA_PRIORI[k] * p2[k] for k in p2)
    print(f"p2 ponderado (mistura a priori) = {pbar:.5f}")
    # quase-duplicados dentro da mesma secao
    por_sec = collections.defaultdict(set)
    for r in regs:
        por_sec[(r["uf"], r["mun"], r["zona"], r["secao"])].add(r["titulo"])
    c = collections.Counter()
    for s, ts in por_sec.items():
        for a, b in itertools.combinations(sorted(ts), 2):
            k = classificar_par(a, b)
            if k:
                c[k] += 1
    print("quase-duplicados na mesma secao (erro unico):", dict(c), "total", sum(c.values()))

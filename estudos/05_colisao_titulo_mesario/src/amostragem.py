#!/usr/bin/env python3
"""
amostragem.py -- sorteio estratificado por UF com semente fixa e ordem aninhada.

Cada secao do catalogo oficial de 2026 recebe uma posicao aleatoria dentro da sua UF (permutacao com
semente SEMENTE). A amostra de fracao f e formada pelas primeiras ceil(f * N_h) secoes de cada UF
(alocacao proporcional => amostra autoponderada; peso = N_h / n_h). Como a ordem e fixa, o piloto e a
amostra principal sao aninhados e ampliar a amostra nao exige novo sorteio.

Uso: python amostragem.py ordem            -> data/processed/ordem_sorteio.csv
     python amostragem.py amostra F SAIDA  -> CSV com as secoes sorteadas (turno 1 e 2)
"""
import csv
import glob
import json
import math
import os
import random
import sys

SEMENTE = 20261004
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
ORDEM = os.path.join(ROOT, "data", "processed", "ordem_sorteio.csv")


def quadro():
    rows = []
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "raw", "catalogo", "*-p3220-cs.json"))):
        d = json.load(open(f, encoding="utf-8"))
        uf = d["abr"][0]["cd"]
        for m in d["abr"][0]["mu"]:
            for z in m["zon"]:
                for s in z["sec"]:
                    rows.append((uf, m["cd"], z["cd"], s["ns"]))
    rows.sort()
    return rows


def ordem():
    rng = random.Random(SEMENTE)
    rows = quadro()
    por_uf = {}
    for r in rows:
        por_uf.setdefault(r[0], []).append(r)
    with open(ORDEM, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["uf", "mun", "zona", "secao", "pos_uf", "N_uf"])
        for uf in sorted(por_uf):
            lst = por_uf[uf]
            rng.shuffle(lst)
            for i, r in enumerate(lst):
                w.writerow([*r, i, len(lst)])
    print(len(rows), "secoes no quadro;", "semente", SEMENTE)


def amostra(f, saida):
    out = []
    for r in csv.DictReader(open(ORDEM, encoding="utf-8")):
        n_h = math.ceil(f * int(r["N_uf"]))
        if int(r["pos_uf"]) < n_h:
            for t in (1, 2):
                out.append(dict(turno=t, uf=r["uf"], mun=r["mun"], zona=r["zona"], secao=r["secao"],
                                N_uf=r["N_uf"], n_uf=n_h, peso=int(r["N_uf"]) / n_h, semente=SEMENTE, fracao=f))
    with open(saida, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(len(out) // 2, "secoes x 2 turnos ->", saida)


if __name__ == "__main__":
    if sys.argv[1] == "ordem":
        ordem()
    else:
        amostra(float(sys.argv[2]), sys.argv[3])

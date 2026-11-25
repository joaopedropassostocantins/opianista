#!/usr/bin/env python3
"""
poder.py -- analise de poder (Fase 1) a partir do piloto (fracao 0,4% das secoes, 1T 2026).

Sob o nulo (erro de digitacao), as colisoes esperadas numa amostra aleatoria de fracao f escalam com f^2:
  lambda0(f) = U(f) * |T(f)| / M,   U(f) = A(f) * p_err * p2,   A e |T| proporcionais a f.
Teste: Poisson exato unilateral, alfa = 0,05. Poder = P(X >= c | 2*lambda0), c = menor k com P(X>=k|lambda0)<=0,05.
"""
import json
import os
import sys

import pandas as pd
from scipy.stats import poisson

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def poder_razao(l0, razao=2.0, alfa=0.05):
    if l0 <= 0:
        return 0.0, None
    c = 0
    while poisson.sf(c - 1, l0) > alfa:
        c += 1
    return float(poisson.sf(c - 1, razao * l0)), c


def l0_minimo(alvo=0.80):
    l0 = 0.1
    while poder_razao(l0)[0] < alvo:
        l0 += 0.1
    return round(l0, 1)


if __name__ == "__main__":
    L = pd.read_csv(os.path.join(ROOT, "data/processed/piloto_logs_2026_t1.csv"))
    R = pd.read_csv(os.path.join(ROOT, "data/processed/piloto_registros_2026_t1.csv"), dtype=str)
    n_sec_piloto = len(L)
    frac_piloto = n_sec_piloto / 499_000
    I, Rg, J = L.n_invalido.sum(), L.n_registrado.sum(), L.n_ja_registrado.sum()
    A = I + Rg + J
    p_inv = I / A
    p2 = float(sys.argv[1]) if len(sys.argv) > 1 else 0.01336
    p_err = p_inv / (1 - p2)
    T_sec = R.groupby(["uf", "mun", "zona", "secao"]).titulo.nunique().sum() / n_sec_piloto
    M = 158_000_000  # ordem de grandeza do eleitorado 2026 (substituido pelo valor exato no relatorio)
    S = 499_000
    # calibracao empirica: quase-duplicados com erro unico dentro da mesma secao no piloto
    quase_dup = int(sys.argv[2]) if len(sys.argv) > 2 else 2
    u_emp = quase_dup / Rg
    out = dict(secoes_piloto=n_sec_piloto, tentativas=int(A), invalidas=int(I), p_inv=p_inv, p2=p2,
               p_err=p_err, titulos_unicos_por_secao=T_sec, quase_dup_piloto=quase_dup,
               taxa_titulo_valido_errado_via1=p_err * p2, taxa_titulo_valido_errado_empirica=u_emp,
               l0_minimo_para_poder80=l0_minimo())
    linhas = []
    for f in (0.05, 0.10, 0.20, 0.30, 0.50, 1.0):
        A_f, T_f = A / n_sec_piloto * S * f, T_sec * S * f
        for nome, taxa in (("via1_ingenua", p_err * p2), ("calibrada_quase_dup", u_emp)):
            l0 = A_f * taxa * T_f / M
            pw, c = poder_razao(l0)
            linhas.append(dict(f=f, calibracao=nome, lambda0_total=round(l0, 3), corte=c, poder_razao2=round(pw, 3)))
    out["tabela"] = linhas
    os.makedirs(os.path.join(ROOT, "registro"), exist_ok=True)
    json.dump(out, open(os.path.join(ROOT, "registro", "poder.json"), "w"), indent=2, default=float)
    print(json.dumps(out, indent=2, default=float))

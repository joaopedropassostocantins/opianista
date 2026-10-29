#!/usr/bin/env python3
"""
H1c do protocolo v1.1 (secao 6.3) e analise exploratoria H1b-L (emenda 02).

H1c: dL(s) = alfa_local + beta * A(s) + gama * X(s) + e(s), e o mesmo para dF, com
dL e dF medidos sobre o comparecimento, efeitos fixos de local de votacao (ou de zona,
se o cadastro de locais nao estiver disponivel) e erros-padrao agrupados por zona.

A(s) = media dos escores z (em TO) do maior D(s,w) e do maior K(s,2T,w) entre J1, J2 e J3.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import statsmodels.api as sm

AQUI = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("pianista", AQUI / "pianista.py")
pz = importlib.util.module_from_spec(_spec)
sys.modules["pianista"] = pz
_spec.loader.exec_module(pz)

LULA, FLAVIO = "v13", "v22"


def carregar_bu(caminho: Path) -> pd.DataFrame:
    b = pd.read_csv(caminho, dtype={"municipio": str, "zona": str, "secao": str})
    b["chave"] = b["uf"] + "-" + b["municipio"] + "-" + b["zona"] + "-" + b["secao"]
    for c in (LULA, FLAVIO, "branco", "nulo", "comparecimento", "aptos", "bu_sem_biometria", "bu_por_biografia"):
        if c not in b:
            b[c] = 0
        b[c] = pd.to_numeric(b[c], errors="coerce").fillna(0)
    return b.set_index("chave")


def indice_anomalia(t2: pd.DataFrame, t1: pd.DataFrame) -> pd.DataFrame:
    ds = []
    for j in pz.FINAIS:
        d = pz.triplo(t2, t1, j)["D"].rename(j)
        ds.append(d)
    dmax = pd.concat(ds, axis=1).max(axis=1)
    kmax = t2[[f"K_{j}" for j in pz.FINAIS]].max(axis=1)
    out = pd.DataFrame({"Dmax": dmax}).join(kmax.rename("Kmax"), how="inner")
    z = lambda s: (s - s.mean()) / s.std(ddof=0) if s.std(ddof=0) > 0 else s * 0.0
    out["A"] = (z(out["Dmax"]) + z(out["Kmax"])) / 2
    return out


def regressao(df: pd.DataFrame, y: str, fe: str) -> dict:
    cols = ["A", "comp_taxa_1", "comp_taxa_2", "aptos", "nb_1"]
    d = df.dropna(subset=[y] + cols + [fe, "zona_id"]).copy()
    # efeitos fixos por desvio da media do grupo (within)
    for c in [y] + cols:
        d[c + "_w"] = d[c] - d.groupby(fe)[c].transform("mean")
    X = d[[c + "_w" for c in cols]]
    X = X.loc[:, X.std() > 0]
    m = sm.OLS(d[y + "_w"], X).fit(cov_type="cluster", cov_kwds={"groups": pd.factorize(d["zona_id"])[0]})
    beta, ep = float(m.params.get("A_w", np.nan)), float(m.bse.get("A_w", np.nan))
    return {"beta": beta, "ep_cluster_zona": ep, "p_bilateral": float(m.pvalues.get("A_w", np.nan)),
            "ic95": [beta - 1.96 * ep, beta + 1.96 * ep], "n_secoes": int(len(d)), "efeitos_fixos": fe,
            "n_grupos_fe": int(d[fe].nunique())}


def comprimento_maximo(df: pd.DataFrame, limiar: float, janela: str) -> pd.Series:
    out = {}
    for chave, g in df.groupby("chave", sort=False):
        m = pz.na_janela(g["seg"], janela).to_numpy()
        seg, nb = g["seg"].to_numpy()[m], g["nb"].to_numpy()[m]
        melhor = atual = 0
        for i in range(seg.size):
            if not nb[i]:
                atual = 0
            elif atual == 0 or seg[i] - seg[i - 1] > limiar:
                atual = 1
            else:
                atual += 1
            melhor = max(melhor, atual)
        out[chave] = melhor
    return pd.Series(out)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--t26-2", type=Path, required=True)
    ap.add_argument("--t26-1", type=Path, required=True)
    ap.add_argument("--t22-2", type=Path, required=True)
    ap.add_argument("--t22-1", type=Path, required=True)
    ap.add_argument("--bu-1", type=Path, required=True)
    ap.add_argument("--bu-2", type=Path, required=True)
    ap.add_argument("--locais", type=Path, default=None)
    ap.add_argument("--dtstar", type=float, required=True)
    ap.add_argument("--saida", type=Path, required=True)
    args = ap.parse_args(argv)

    dfs = {n: pz.carregar(getattr(args, n)) for n in ("t26_2", "t26_1", "t22_2", "t22_1")}
    tab = {n: pz.tabela_secoes(d, args.dtstar) for n, d in dfs.items()}
    ind = indice_anomalia(tab["t26_2"], tab["t26_1"])
    b1, b2 = carregar_bu(args.bu_1), carregar_bu(args.bu_2)
    comum = ind.index.intersection(b1.index).intersection(b2.index)
    d = ind.loc[comum].copy()
    d["dL"] = b2.loc[comum, LULA] / b2.loc[comum, "comparecimento"] - b1.loc[comum, LULA] / b1.loc[comum, "comparecimento"]
    d["dF"] = b2.loc[comum, FLAVIO] / b2.loc[comum, "comparecimento"] - b1.loc[comum, FLAVIO] / b1.loc[comum, "comparecimento"]
    d["comp_taxa_1"] = b1.loc[comum, "comparecimento"] / b1.loc[comum, "aptos"].replace(0, np.nan)
    d["comp_taxa_2"] = b2.loc[comum, "comparecimento"] / b2.loc[comum, "aptos"].replace(0, np.nan)
    d["aptos"] = b2.loc[comum, "aptos"]
    d["nb_1"] = (b1.loc[comum, "bu_sem_biometria"] + b1.loc[comum, "bu_por_biografia"]) / b1.loc[comum, "comparecimento"]
    partes = pd.Series(comum, index=comum).str.split("-", expand=True)
    d["zona_id"] = partes[0] + "-" + partes[1] + "-" + partes[2]
    fe = "zona_id"
    if args.locais is not None and args.locais.is_file():
        loc = pd.read_csv(args.locais, dtype=str)
        loc["chave"] = loc["SG_UF"] + "-" + loc["CD_MUNICIPIO"].str.zfill(5) + "-" + loc["NR_ZONA"].str.zfill(4) + "-" + loc["NR_SECAO"].str.zfill(4)
        loc = loc.drop_duplicates("chave").set_index("chave")
        d["local_id"] = (d["zona_id"] + "-" + loc["NR_LOCAL_VOTACAO"].reindex(d.index).astype(str))
        d.loc[loc["NR_LOCAL_VOTACAO"].reindex(d.index).isna(), "local_id"] = np.nan
        if d["local_id"].notna().mean() > 0.9:
            fe = "local_id"
    res = {"H1c-Lula": regressao(d, "dL", fe), "H1c-Flavio": regressao(d, "dF", fe),
           "secoes_no_indice": int(len(ind)), "secoes_com_bu_nos_dois_turnos": int(len(comum))}
    # limite de materialidade: votos implicados pelo maior efeito plausivel
    res["controle_votos_TO"] = {"Lula_1T": int(b1[LULA].sum()), "Flavio_1T": int(b1[FLAVIO].sum()),
                                "Lula_2T": int(b2[LULA].sum()), "Flavio_2T": int(b2[FLAVIO].sum()),
                                "comparecimento_1T": int(b1["comparecimento"].sum()), "comparecimento_2T": int(b2["comparecimento"].sum())}
    # H1b-L exploratoria
    expl = {}
    for j in pz.FINAIS:
        L = {n: comprimento_maximo(dfs[n], args.dtstar, j) for n in dfs}
        def dif(a, b):
            c = L[a].index.intersection(L[b].index)
            return float((L[a].loc[c] - L[b].loc[c]).mean()) if len(c) else float("nan")
        expl[j] = {"Lmax_medio": {n: float(L[n].mean()) for n in L},
                   "secoes_Lmax_ge_5": {n: int((L[n] >= 5).sum()) for n in L},
                   "dif_2T_1T_2026": dif("t26_2", "t26_1"), "dif_2T_1T_2022": dif("t22_2", "t22_1")}
    res["H1b_L_exploratoria"] = expl
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(res, indent=2, ensure_ascii=False, default=float), encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False, default=float))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

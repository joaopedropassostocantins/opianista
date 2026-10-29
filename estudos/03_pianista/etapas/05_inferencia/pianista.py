#!/usr/bin/env python3
"""
Estudo 03 - hipotese do mesario pianista: calculos do protocolo v1.1.

Entrada: CSVs gzip produzidos por etapas/02_parser/eventos.py, uma linha por
habilitacao (uf, periodo, municipio, zona, secao, seg, modo).

Subcomandos:
  dtstar   - limiar dt* (percentil 1, tipo 7) dos intervalos entre habilitacoes
             biometricas consecutivas na janela J0 de um periodo de calibracao.
  poder    - diagnostico de poder por injecao de insercoes sinteticas.
  testes   - H1a, H1b e H1d (H1c e calculado em modulo proprio, com BU).

Parametros fixados pelo protocolo v1.1 (secao 2): janelas, efeito minimo de
5 p.p. e 2 rajadas, FDR q = 0,05, seed 20261025, 10.000 replicas.
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

SEED = 20261025
B = 10_000
EFEITO_MIN = 0.05
RAJADAS_MIN = 2
Q_FDR = 0.05
MIN_INTERVALOS_DTSTAR = 100_000
NB_MODOS = ("NB_SEM", "NB_MAN")
MIN_SECOES = 30       # minimo de secoes para um teste nacional ser estimavel
MIN_CLUSTERS = 10     # minimo de zonas (clusters) para o bootstrap

JANELAS = {
    "J0": (9 * 3600, 15 * 3600),            # 09h00:00 - 14h59:59
    "J1": (16 * 3600, 17 * 3600),           # 16h00:00 - 16h59:59
    "J2": (17 * 3600, 17 * 3600 + 49 * 60),  # 17h00:00 - 17h48:59
    "J3": (17 * 3600 + 49 * 60, 19 * 3600 + 1),  # 17h49:00 - 19h00:00
}
FINAIS = ("J1", "J2", "J3")


# ----------------------------------------------------------------------------- dados

def carregar(caminho: Path) -> pd.DataFrame:
    df = pd.read_csv(caminho, dtype={"municipio": str, "zona": str, "secao": str})
    df = df[df["secao"].notna() & (df["secao"] != "")]
    df["chave"] = df["uf"] + "-" + df["municipio"] + "-" + df["zona"] + "-" + df["secao"]
    df["cluster"] = df["uf"] + "-" + df["municipio"] + "-" + df["zona"]
    # Software de 2026 (VOTA 10.23) nao registra "O eleitor nao possui biometria": a habilitacao sem
    # biometria cadastrada fica sem marcador (DESC). Validado contra o BU do 1T 2026 de TO (emenda 02).
    em_2026 = df["periodo"].astype(str).str.contains("2026")
    df.loc[em_2026 & (df["modo"] == "DESC"), "modo"] = "NB_SEM"
    df["nb"] = df["modo"].isin(NB_MODOS)
    df = df.sort_values(["chave", "seg"], kind="stable").reset_index(drop=True)
    return df


def na_janela(seg: pd.Series, janela: str) -> pd.Series:
    ini, fim = JANELAS[janela]
    return (seg >= ini) & (seg < fim)


# ----------------------------------------------------------------------------- dt*

def intervalos_biometricos_j0(df: pd.DataFrame) -> np.ndarray:
    """Intervalos entre habilitacoes consecutivas da mesma secao, ambas BIO, ambas em J0."""
    sub = df.copy()
    sub["prox_seg"] = sub.groupby("chave")["seg"].shift(-1)
    sub["prox_modo"] = sub.groupby("chave")["modo"].shift(-1)
    ok = (
        (sub["modo"] == "BIO")
        & (sub["prox_modo"] == "BIO")
        & na_janela(sub["seg"], "J0")
        & na_janela(sub["prox_seg"].fillna(-1), "J0")
    )
    return (sub.loc[ok, "prox_seg"] - sub.loc[ok, "seg"]).to_numpy(dtype=float)


def dtstar(df: pd.DataFrame) -> dict:
    dts = intervalos_biometricos_j0(df)
    resultado = {"n_intervalos": int(dts.size), "minimo_exigido": MIN_INTERVALOS_DTSTAR}
    if dts.size < MIN_INTERVALOS_DTSTAR:
        resultado["dtstar"] = None
        resultado["situacao"] = "NAO ESTIMADO: intervalos insuficientes"
        return resultado
    resultado["dtstar"] = float(np.quantile(dts, 0.01, method="linear"))
    resultado["quantis"] = {str(q): float(np.quantile(dts, q, method="linear")) for q in (0.001, 0.005, 0.01, 0.05, 0.25, 0.5)}
    resultado["situacao"] = "ESTIMADO"
    return resultado


# ----------------------------------------------------------------------------- rajadas

def contar_rajadas(seg: np.ndarray, nb: np.ndarray, limiar: float) -> int:
    """Rajadas: >= 3 habilitacoes consecutivas, todas NB, intervalos internos <= limiar, sem sobreposicao."""
    k = 0
    comprimento = 0
    for i in range(seg.size):
        if not nb[i]:
            if comprimento >= 3:
                k += 1
            comprimento = 0
            continue
        if comprimento == 0:
            comprimento = 1
        elif seg[i] - seg[i - 1] <= limiar:
            comprimento += 1
        else:
            if comprimento >= 3:
                k += 1
            comprimento = 1
    if comprimento >= 3:
        k += 1
    return k


# ----------------------------------------------------------------------------- tabela por secao

def tabela_secoes(df: pd.DataFrame, limiar: float) -> pd.DataFrame:
    """Por secao: N_H e N_NB por janela, K por janela final, intervalos de J0."""
    linhas = []
    for chave, g in df.groupby("chave", sort=False):
        seg = g["seg"].to_numpy()
        nb = g["nb"].to_numpy()
        reg = {"chave": chave, "cluster": g["cluster"].iat[0], "municipio": g["municipio"].iat[0],
               "zona": g["zona"].iat[0]}
        for j in JANELAS:
            m = na_janela(g["seg"], j).to_numpy()
            reg[f"H_{j}"] = int(m.sum())
            reg[f"NB_{j}"] = int(nb[m].sum())
            if j in FINAIS:
                reg[f"K_{j}"] = contar_rajadas(seg[m], nb[m], limiar)
        linhas.append(reg)
    return pd.DataFrame(linhas).set_index("chave")


def intervalos_j0_por_secao(df: pd.DataFrame) -> dict[str, np.ndarray]:
    saida = {}
    for chave, g in df.groupby("chave", sort=False):
        s = g.loc[na_janela(g["seg"], "J0"), "seg"].to_numpy()
        saida[chave] = np.diff(s).astype(float) if s.size > 1 else np.array([], dtype=float)
    return saida


# ----------------------------------------------------------------------------- H1a

def triplo(t2: pd.DataFrame, t1: pd.DataFrame, janela: str) -> pd.DataFrame:
    """D(s,w) = [r(2T,w) - r(2T,J0)] - [r(1T,w) - r(1T,J0)] para secoes com denominadores validos."""
    comum = t2.index.intersection(t1.index)
    a, b = t2.loc[comum], t1.loc[comum]
    ok = (a[f"H_{janela}"] > 0) & (a["H_J0"] > 0) & (b[f"H_{janela}"] > 0) & (b["H_J0"] > 0)
    a, b = a[ok], b[ok]
    r = lambda t, j: t[f"NB_{j}"] / t[f"H_{j}"]
    d = (r(a, janela) - r(a, "J0")) - (r(b, janela) - r(b, "J0"))
    return pd.DataFrame({"D": d, "peso": a[f"H_{janela}"], "cluster": a["cluster"],
                         "municipio": a["municipio"]})


def media_ponderada(d: pd.DataFrame) -> float:
    return float(np.average(d["D"], weights=d["peso"])) if len(d) else float("nan")


def estimavel(d: pd.DataFrame) -> bool:
    return len(d) >= MIN_SECOES and d["cluster"].nunique() >= MIN_CLUSTERS


def teste_unilateral(delta: float, boot: np.ndarray, ok: bool) -> tuple[float, float, list[float]]:
    if not ok or not np.isfinite(delta):
        return float("nan"), float("nan"), [float("nan"), float("nan")]
    se = float(np.nanstd(boot, ddof=1))
    if not np.isfinite(se) or se < 1e-9:
        return se, float("nan"), [float("nan"), float("nan")]
    p = float(1 - stats.norm.cdf(delta / se))
    return se, p, [float(np.nanquantile(boot, 0.025)), float(np.nanquantile(boot, 0.975))]


def bootstrap_cluster(d: pd.DataFrame, rng: np.random.Generator, reps: int = B) -> np.ndarray:
    """Reamostragem de clusters (zona) com reposicao; estatistica = media ponderada de D."""
    if not len(d):
        return np.full(reps, np.nan)
    soma = d.assign(dw=d["D"] * d["peso"]).groupby("cluster")[["dw", "peso"]].sum()
    dw, w = soma["dw"].to_numpy(), soma["peso"].to_numpy()
    idx = rng.integers(0, len(soma), size=(reps, len(soma)))
    return dw[idx].sum(axis=1) / w[idx].sum(axis=1)


def h1a(t26_2, t26_1, t22_2, t22_1, rng) -> dict:
    res = {}
    for j in FINAIS:
        d26, d22 = triplo(t26_2, t26_1, j), triplo(t22_2, t22_1, j)
        m26, m22 = media_ponderada(d26), media_ponderada(d22)
        b26, b22 = bootstrap_cluster(d26, rng), bootstrap_cluster(d22, rng)
        ok26 = estimavel(d26)
        comparavel_2022 = estimavel(d22) and (len(d22) >= 500 if j == "J3" else True)
        if comparavel_2022:
            delta, boot = m26 - m22, b26 - b22
        else:
            delta, boot = m26, b26
        se, p, ic = teste_unilateral(delta, boot, ok26)
        res[j] = {"n_secoes_2026": len(d26), "n_secoes_2022": len(d22), "media_2026": m26, "media_2022": m22,
                  "delta": delta, "ep_bootstrap": se, "ic95": ic, "p_unilateral": p,
                  "estimavel": ok26,
                  "comparacao_2022": "sim" if comparavel_2022 else "nao (rebaixado a exploratorio)",
                  "materialmente_relevante": bool(np.isfinite(ic[0]) and ic[0] >= EFEITO_MIN)}
    return res


# ----------------------------------------------------------------------------- H1a: sinalizacao por secao

def _ab_cluster(n: np.ndarray, x: np.ndarray) -> tuple[float, float]:
    """Beta-binomial empirico (metodo dos momentos) para um conjunto de secoes."""
    ok = n > 0
    if ok.sum() < 3:
        return 1.0, 1.0
    p = x[ok] / n[ok]
    m = np.average(p, weights=n[ok])
    v = np.average((p - m) ** 2, weights=n[ok])
    nbar = n[ok].mean()
    v_entre = max(v - m * (1 - m) / nbar, 1e-6)
    soma = max(m * (1 - m) / v_entre - 1, 0.5)
    return max(m * soma, 0.05), max((1 - m) * soma, 0.05)


def prob_excesso(t2, t1, janela: str, rng, draws: int = 4000) -> pd.Series:
    """P(D(s,w) >= 5 p.p. | dados): betas por secao com priors estimados no cluster (zona)."""
    comum = t2.index.intersection(t1.index)
    a, b = t2.loc[comum], t1.loc[comum]
    ok = (a[f"H_{janela}"] > 0) & (b[f"H_{janela}"] > 0) & (a["H_J0"] > 0) & (b["H_J0"] > 0)
    a, b = a[ok], b[ok]
    out = pd.Series(np.nan, index=a.index)
    for cl, idx in a.groupby("cluster").groups.items():
        partes = []
        for t in (a, b):
            for j in (janela, "J0"):
                n = t.loc[idx, f"H_{j}"].to_numpy(float)
                x = t.loc[idx, f"NB_{j}"].to_numpy(float)
                al, be = _ab_cluster(n, x)
                partes.append(rng.beta(al + x[:, None], be + (n - x)[:, None], size=(len(idx), draws)))
        d = (partes[0] - partes[1]) - (partes[2] - partes[3])
        out.loc[idx] = (d >= EFEITO_MIN).mean(axis=1)
    return out


# ----------------------------------------------------------------------------- H1b

def p_secao_rajadas(seg_j0_dt: np.ndarray, n: int, m_nb: int, k_obs: int, limiar: float, rng, reps: int = B) -> float:
    """P(K_sim >= K_obs), intervalos sorteados de J0 da propria secao e ordem NB/BIO permutada."""
    if k_obs == 0:
        return 1.0
    if seg_j0_dt.size == 0 or n < 3 or m_nb < 3:
        return float("nan")
    dt = rng.choice(seg_j0_dt, size=(reps, n - 1), replace=True)
    seg = np.concatenate([np.zeros((reps, 1)), np.cumsum(dt, axis=1)], axis=1)
    nb = np.zeros((reps, n), dtype=bool)
    nb[:, :m_nb] = True
    nb = rng.permuted(nb, axis=1)
    ks = np.fromiter((contar_rajadas(seg[i], nb[i], limiar) for i in range(reps)), dtype=int, count=reps)
    return float((ks >= k_obs).mean())


def bh(p: pd.Series) -> pd.Series:
    v = p.dropna()
    if v.empty:
        return pd.Series(np.nan, index=p.index)
    q = stats.false_discovery_control(v.to_numpy(), method="bh")
    return pd.Series(q, index=v.index).reindex(p.index)


def prop_k(t: pd.DataFrame, j: str) -> pd.DataFrame:
    return pd.DataFrame({"flag": (t[f"K_{j}"] >= RAJADAS_MIN).astype(float), "cluster": t["cluster"]})


def h1b(t26_2, t26_1, t22_2, t22_1, rng) -> dict:
    res = {}
    for j in FINAIS:
        def dif(t2, t1):
            comum = t2.index.intersection(t1.index)
            a, b = prop_k(t2.loc[comum], j), prop_k(t1.loc[comum], j)
            return pd.DataFrame({"D": a["flag"] - b["flag"], "peso": 1.0, "cluster": a["cluster"]})
        d26, d22 = dif(t26_2, t26_1), dif(t22_2, t22_1)
        m26, m22 = media_ponderada(d26), media_ponderada(d22)
        boot = bootstrap_cluster(d26, rng) - bootstrap_cluster(d22, rng)
        delta = m26 - m22
        se, p, ic = teste_unilateral(delta, boot, estimavel(d26) and estimavel(d22))
        res[j] = {"n_secoes_2026": len(d26), "n_secoes_2022": len(d22), "dif_2026": m26, "dif_2022": m22,
                  "delta": delta, "ep_bootstrap": se, "ic95": ic, "p_unilateral": p,
                  "secoes_K2_2026_2T": int((t26_2[f"K_{j}"] >= RAJADAS_MIN).sum()),
                  "secoes_K2_2026_1T": int((t26_1[f"K_{j}"] >= RAJADAS_MIN).sum())}
    return res


# ----------------------------------------------------------------------------- H1d

def h1d(flag_a: pd.Series, flag_b: pd.Series, municipio: pd.Series, rng, reps: int = B) -> dict:
    idx = flag_a.index.intersection(flag_b.index)
    fa, fb, mu = flag_a.loc[idx].astype(bool), flag_b.loc[idx].astype(bool), municipio.loc[idx]
    obs = int((fa & fb).sum())
    grupos = [np.flatnonzero((mu == m).to_numpy()) for m in mu.unique()]
    fb_arr, fa_arr = fb.to_numpy(), fa.to_numpy()
    sims = np.empty(reps, dtype=int)
    for r in range(reps):
        perm = fb_arr.copy()
        for g in grupos:
            perm[g] = rng.permutation(perm[g])
        sims[r] = int((fa_arr & perm).sum())
    return {"conjuntas_observadas": obs, "esperado_sob_independencia": float(sims.mean()),
            "p_unilateral": float((sims >= obs).mean()), "n_secoes": int(len(idx)),
            "sinalizadas_H1a": int(fa.sum()), "sinalizadas_H1b": int(fb.sum())}


# ----------------------------------------------------------------------------- poder

def injetar(df: pd.DataFrame, chaves: np.ndarray, k: int, rng, padrao: str = "bloco") -> pd.DataFrame:
    """Insere k habilitacoes NB_MAN em J1 das secoes sorteadas.

    padrao 'bloco': uma unica sequencia com intervalos de 5 a 15 s.
    padrao 'fragmentado': grupos de 4 com intervalos de 5 a 15 s, separados por 3 a 6 min.
    """
    novos = []
    ini, fim = JANELAS["J1"]
    base = df.drop_duplicates("chave").set_index("chave")
    for c in chaves:
        if padrao == "bloco":
            passos = rng.integers(5, 16, size=k)
        else:
            passos = np.array([rng.integers(180, 361) if (i > 0 and i % 4 == 0) else rng.integers(5, 16) for i in range(k)])
        t0 = rng.integers(ini, max(ini + 1, fim - int(passos.sum()) - 1))
        segs = t0 + np.cumsum(passos)
        r = base.loc[c]
        for s in segs:
            novos.append({"uf": r["uf"], "periodo": r["periodo"], "municipio": r["municipio"], "zona": r["zona"],
                          "secao": r["secao"], "seg": int(s), "modo": "NB_MAN", "chave": c,
                          "cluster": r["cluster"], "nb": True})
    out = pd.concat([df, pd.DataFrame(novos)], ignore_index=True)
    return out.sort_values(["chave", "seg"], kind="stable").reset_index(drop=True)


def poder(alvo: pd.DataFrame, antes: pd.DataFrame, limiar: float, rng, n_secoes: int, ks=(5, 10, 20, 50),
          reps_secao: int = 2000, padrao: str = "bloco") -> dict:
    """Sensibilidade da sinalizacao por secao (H1a e H1b) e falsos positivos, injetando no 'alvo'."""
    t_antes = tabela_secoes(antes, limiar)
    t_base = tabela_secoes(alvo, limiar)
    ivals = intervalos_j0_por_secao(alvo)
    elegiveis = t_base.index.intersection(t_antes.index)
    elegiveis = elegiveis[(t_base.loc[elegiveis, "H_J1"] > 0) & (t_base.loc[elegiveis, "H_J0"] > 0)
                          & (t_antes.loc[elegiveis, "H_J1"] > 0) & (t_antes.loc[elegiveis, "H_J0"] > 0)]
    sorteio = rng.choice(np.asarray(elegiveis), size=min(n_secoes, len(elegiveis)), replace=False)
    controle = np.setdiff1d(np.asarray(elegiveis), sorteio)
    pa_base = prob_excesso(t_base, t_antes, "J1", rng)
    fp_a = float((pa_base.reindex(controle).dropna() >= 0.95).mean())
    res = {"padrao": padrao, "secoes_injetadas": int(len(sorteio)), "falso_positivo_H1a": fp_a, "por_k": {}}
    for k in ks:
        df_k = injetar(alvo, sorteio, k, rng, padrao)
        t_k = tabela_secoes(df_k[df_k["chave"].isin(sorteio)], limiar)
        pa = prob_excesso(t_k, t_antes.loc[sorteio], "J1", rng)
        sens_a = float((pa.dropna() >= 0.95).mean())
        pb_inj = pd.Series({c: p_secao_rajadas(ivals[c], int(t_k.at[c, "H_J1"]), int(t_k.at[c, "NB_J1"]),
                                                int(t_k.at[c, "K_J1"]), limiar, rng, reps_secao) for c in sorteio})
        pb_ctl = pd.Series({c: p_secao_rajadas(ivals[c], int(t_base.at[c, "H_J1"]), int(t_base.at[c, "NB_J1"]),
                                                int(t_base.at[c, "K_J1"]), limiar, rng, reps_secao) for c in controle})
        q = bh(pd.concat([pb_inj, pb_ctl]))
        k_inj = t_k.loc[sorteio, "K_J1"] >= RAJADAS_MIN
        k_ctl = t_base.loc[controle, "K_J1"] >= RAJADAS_MIN
        fb_inj = k_inj & (q.loc[sorteio] <= Q_FDR)
        fb_ctl = k_ctl & (q.loc[controle] <= Q_FDR)
        sens_b = float(fb_inj.mean())
        res["por_k"][str(k)] = {"sensibilidade_H1a": sens_a, "sensibilidade_H1b": sens_b,
                                "falso_positivo_H1b": float(fb_ctl.mean()),
                                "sensibilidade_conjunta": float(((pa.reindex(sorteio) >= 0.95) & fb_inj).mean())}
    detect = [int(k) for k, v in res["por_k"].items() if max(v["sensibilidade_H1a"], v["sensibilidade_H1b"]) >= 0.80]
    res["menor_k_poder_080"] = min(detect) if detect else None
    return res


# ----------------------------------------------------------------------------- CLI

def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = ap.add_subparsers(dest="cmd", required=True)
    a = sub.add_parser("dtstar")
    a.add_argument("--calibracao", type=Path, required=True)
    a.add_argument("--saida", type=Path, required=True)
    b = sub.add_parser("poder")
    b.add_argument("--alvo", type=Path, required=True, help="periodo que recebe as injecoes (ex.: 2T2022)")
    b.add_argument("--antes", type=Path, required=True, help="periodo de comparacao da mesma secao (ex.: 1T2022)")
    b.add_argument("--dtstar", type=float, required=True)
    b.add_argument("--secoes", type=int, default=300)
    b.add_argument("--padrao", choices=("bloco", "fragmentado"), default="bloco")
    b.add_argument("--saida", type=Path, required=True)
    c = sub.add_parser("testes")
    c.add_argument("--t26-2", type=Path, required=True)
    c.add_argument("--t26-1", type=Path, required=True)
    c.add_argument("--t22-2", type=Path, required=True)
    c.add_argument("--t22-1", type=Path, required=True)
    c.add_argument("--dtstar", type=float, required=True)
    c.add_argument("--excluir", type=Path, default=None, help="lista de chaves de secao a excluir (amostra exposta)")
    c.add_argument("--saida", type=Path, required=True)
    c.add_argument("--secoes-sinalizadas", type=Path, required=True)
    args = ap.parse_args(argv)
    rng = np.random.default_rng(SEED)

    if args.cmd == "dtstar":
        res = dtstar(carregar(args.calibracao))
    elif args.cmd == "poder":
        res = poder(carregar(args.alvo), carregar(args.antes), args.dtstar, rng, args.secoes, padrao=args.padrao)
    else:
        dfs = {n: carregar(getattr(args, n)) for n in ("t26_2", "t26_1", "t22_2", "t22_1")}
        if args.excluir is not None:
            fora = set(Path(args.excluir).read_text().split())
            dfs = {n: d[~d["chave"].isin(fora)] for n, d in dfs.items()}
        tab = {n: tabela_secoes(d, args.dtstar) for n, d in dfs.items()}
        res = {"dtstar": args.dtstar,
               "controle": {n: {"secoes": int(len(t)), "habilitacoes": int(sum(t[f"H_{j}"].sum() for j in JANELAS)),
                                "DESC": int((dfs[n]["modo"] == "DESC").sum())} for n, t in tab.items()},
               "H1a": h1a(tab["t26_2"], tab["t26_1"], tab["t22_2"], tab["t22_1"], rng),
               "H1b": h1b(tab["t26_2"], tab["t26_1"], tab["t22_2"], tab["t22_1"], rng)}
        ivals = intervalos_j0_por_secao(dfs["t26_2"])
        flags_a, flags_b = [], []
        sinal = []
        for j in FINAIS:
            pa = prob_excesso(tab["t26_2"], tab["t26_1"], j, rng)
            t = tab["t26_2"]
            pb = pd.Series({c: p_secao_rajadas(ivals.get(c, np.array([])), int(t.at[c, f"H_{j}"]),
                                                int(t.at[c, f"NB_{j}"]), int(t.at[c, f"K_{j}"]), args.dtstar, rng)
                            for c in t.index})
            qb = bh(pb)
            fa = (pa >= 0.95).reindex(t.index, fill_value=False)
            fb = ((t[f"K_{j}"] >= RAJADAS_MIN) & (qb <= Q_FDR)).fillna(False)
            flags_a.append(fa)
            flags_b.append(fb)
            sinal.append(pd.DataFrame({"janela": j, "P_excesso_5pp": pa.reindex(t.index), "K": t[f"K_{j}"],
                                       "q_rajadas": qb, "flag_H1a": fa, "flag_H1b": fb}))
        fa_any = pd.concat(flags_a, axis=1).any(axis=1)
        fb_any = pd.concat(flags_b, axis=1).any(axis=1)
        res["H1d"] = h1d(fa_any, fb_any, tab["t26_2"]["municipio"], rng)
        familia = {f"H1a-{j}": res["H1a"][j]["p_unilateral"] for j in FINAIS}
        familia.update({f"H1b-{j}": res["H1b"][j]["p_unilateral"] for j in FINAIS})
        familia["H1d"] = res["H1d"]["p_unilateral"]
        ps = pd.Series(familia)
        res["familia_S_PIANISTA_q_bh"] = bh(ps).to_dict()
        res["observacao"] = "H1c-Lula e H1c-Flavio entram na familia quando calculados (modulo com BU); q-valores serao recalculados com os 9 testes."
        sin = pd.concat(sinal)
        sin = sin[sin["flag_H1a"] | sin["flag_H1b"]]
        args.secoes_sinalizadas.parent.mkdir(parents=True, exist_ok=True)
        sin.to_csv(args.secoes_sinalizadas)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    args.saida.write_text(json.dumps(res, indent=2, ensure_ascii=False, default=float), encoding="utf-8")
    print(json.dumps(res, indent=2, ensure_ascii=False, default=float)[:4000])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

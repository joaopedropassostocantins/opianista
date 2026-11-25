#!/usr/bin/env python3
"""
painel.py -- painel local obrigatorio de toda secao com colisao, teste conjunto e veredito de local (emenda 06).

Universo do painel: todas as secoes dos municipios em que houve colisao (necessario para o teste conjunto).
Fontes: log bruto do cache seletivo (criterio "painel"), boletim de urna web do 1o e do 2o turno (votos.py),
registros de presenca do censo (2026 e 2022).

Metricas por secao (todas pre-registradas):
  m1 variacao da abstencao, 2o turno menos 1o turno (BU)
  m2 taxa de habilitacao sem biometria = 1 - "Tipo de habilitação do eleitor [biométrica]" / "Eleitor foi habilitado"
  m3 taxa de habilitacao autorizada por mesario ("Mesário <T> habilitou o eleitor") / habilitados
  m4 taxa de "não é eleitor da seção" entre os mesarios registrados
  m5 movimento de cada finalista (variacao da fatia de cada um, 1o para 2o turno; outlier se qualquer um for)
  m6 taxa de liberacao manual ("Solicitação de dado pessoal do eleitor para habilitação manual") / habilitados
  m7 rajada (so secoes com colisao): votos nos 15 min seguintes ao registro contestado contra as janelas de
     15 min da propria secao no dia
  porta estreita: fracao de mesarios eleitores da secao com biometria nao coincidente; sozinha nao classifica;
     comparada tambem com a taxa do 2o turno de 2022 na mesma UF e mesmo modelo de urna
Vizinhas: demais secoes do mesmo local de votacao, sem colisao; se o local tiver menos de 5 secoes, mesma zona
  e mesmo modelo de urna, sem colisao.
Outlier: |z| > 3, z robusto = (x - mediana) / max(1,4826 * MAD, piso); piso binomial para taxas
  (sqrt(p0 (1 - p0) / n), p0 = mediana limitada a [1/2n, 1 - 1/2n]) e desvio-padrao das vizinhas para variacoes.
Secao anomala (para o teste conjunto): >= 2 outliers entre m1-m6, ou 1 outlier entre m1-m6 e porta estreita
  outlier. Para o veredito de local de secao com colisao, m7 tambem conta (anomala_com_rajada).
Teste conjunto: proporcao de secoes com colisao anomalas contra permutacao dos rotulos de colisao dentro de
  municipio x modelo de urna, 10.000 vezes (semente 20261025).
Veredito de local: G1 (colisao e anomala) "acidente nao chega neste local"; G2 (colisao e normal) "compativel
  com acidente, desde que o total nacional caiba no intervalo". Nenhuma familia por default.
A varredura nacional sem colisao (G3) NAO e feita neste estudo: e a pergunta do Estudo 03.

Uso: python painel.py ANO [--turno 2] [--reps 10000]
"""
import argparse
import glob
import json
import os
import sys

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parsing import ler_logd, metricas_painel  # noqa: E402
from votos import urls_bweb, baixar, ler_presidente  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SEC = ["uf", "mun", "zona", "secao"]
LIMIAR = 3.0
MIN_LOCAL = 5
METRICAS = ["m1_var_abstencao", "m2_sem_biometria", "m3_hab_por_mesario", "m4_nao_eleitor", "m5a_var_finalista_A",
            "m5b_var_finalista_B", "m6_liberacao_manual"]
TAXAS = {"m2_sem_biometria": "habilitados", "m3_hab_por_mesario": "habilitados", "m6_liberacao_manual": "habilitados",
         "m4_nao_eleitor": "n_mesarios", "porta_estreita": "n_mesarios_eleitores"}


def ler(padrao):
    fs = sorted(glob.glob(padrao))
    return pd.concat([pd.read_csv(f, dtype=str) for f in fs], ignore_index=True) if fs else pd.DataFrame()


def z_robusto(x, viz, n=None):
    viz = np.asarray([v for v in viz if v == v], dtype=float)
    if x != x or len(viz) < 2:
        return np.nan
    med = float(np.median(viz))
    mad = 1.4826 * float(np.median(np.abs(viz - med)))
    if n is not None and n > 0:
        p0 = min(max(med, 1 / (2 * n)), 1 - 1 / (2 * n))
        piso = (p0 * (1 - p0) / n) ** 0.5
    else:
        piso = float(np.std(viz, ddof=1)) if len(viz) > 1 else 0.0
    esc = max(mad, piso, 1e-9)
    return (x - med) / esc


def rajada(horas, ts_contestado):
    """Votos em [t, t+900) contra as janelas de 15 min do dia da propria secao (z robusto)."""
    if not horas or ts_contestado is None:
        return np.nan, np.nan
    h = np.asarray(horas)
    ini, fim = h.min(), h.max()
    janelas = [((h >= a) & (h < a + 900)).sum() for a in range(int(ini), int(fim) + 1, 900)]
    obs = int(((h >= ts_contestado) & (h < ts_contestado + 900)).sum())
    return obs, z_robusto(obs, janelas)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ano", type=int)
    ap.add_argument("--turno", type=int, default=2)
    ap.add_argument("--reps", type=int, default=10000)
    ap.add_argument("--semente", type=int, default=20261025)
    a = ap.parse_args()
    saida = os.path.join(ROOT, "data", "outputs", f"{a.ano}_t{a.turno}")
    col = pd.read_csv(os.path.join(saida, "colisoes.csv"), dtype=str).fillna("")
    col = col[col.exclusao == ""]
    trat, ts_contest = set(), {}
    for p in ("a", "b"):
        for r in col.to_dict("records"):
            s = "-".join(r[f"{k}_{p}"] for k in SEC)
            trat.add(s)
            ts = [x for x in r[f"ts_{p}"].split("|") if x]
            if ts:
                hh, mm, ss = ts[0][11:19].split(":")
                ts_contest.setdefault(s, int(hh) * 3600 + int(mm) * 60 + int(ss))
    muns = {tuple(s.split("-")[:2]) for s in trat}
    geo = pd.read_csv(os.path.join(ROOT, "data", "processed", f"geo_{a.ano}.csv"), dtype=str)
    geo["sec"] = geo[SEC].agg("-".join, axis=1)
    geo = geo[[(u, m) in muns for u, m in zip(geo.uf, geo.mun)]]
    L = ler(os.path.join(ROOT, "data", "censo", f"logs_{a.ano}_t{a.turno}_s*.csv"))
    L["sec"] = L[SEC].agg("-".join, axis=1)
    modelo = L.dropna(subset=["modelo"]).groupby("sec").modelo.first().to_dict()
    R = ler(os.path.join(ROOT, "data", "censo", f"registros_{a.ano}_t{a.turno}_s*.csv"))
    R["sec"] = R[SEC].agg("-".join, axis=1)
    o = R.drop_duplicates(["sec", "titulo"])
    mes = o.groupby("sec").agg(n_mesarios=("titulo", "size"),
                               nao_eleitor=("eleitor_secao", lambda x: (x == "0").sum()),
                               n_mesarios_eleitores=("eleitor_secao", lambda x: (x == "1").sum()))
    porta = o[(o.eleitor_secao == "1") & (o.biometria == "nao_coincide")].groupby("sec").size()
    mes["porta_n"] = porta.reindex(mes.index, fill_value=0)
    # porta no 2T de 2022, por UF e modelo de urna
    R22 = ler(os.path.join(ROOT, "data", "censo", "registros_2022_t2_s*.csv"))
    L22 = ler(os.path.join(ROOT, "data", "censo", "logs_2022_t2_s*.csv"))
    porta22 = {}
    if len(R22):
        R22["sec"] = R22[SEC].agg("-".join, axis=1)
        L22["sec"] = L22[SEC].agg("-".join, axis=1)
        o22 = R22.drop_duplicates(["sec", "titulo"])
        o22 = o22[o22.eleitor_secao == "1"].copy()
        o22["modelo"] = o22.sec.map(L22.dropna(subset=["modelo"]).groupby("sec").modelo.first())
        porta22 = o22.assign(p=(o22.biometria == "nao_coincide")).groupby(["uf", "modelo"]).p.mean().to_dict()
    # BU: abstencao e finalistas
    urls = urls_bweb(a.ano)
    destdir = os.path.join(ROOT, "data", "raw", "bweb")
    bu = {}
    for uf in sorted({u for u, _ in muns}):
        d1 = ler_presidente(baixar(urls[("1t", uf)], destdir, os.path.join(destdir, "manifesto_bweb.csv")))
        d2 = ler_presidente(baixar(urls[("2t", uf)], destdir, os.path.join(destdir, "manifesto_bweb.csv")))
        cand = sorted(d2[d2.DS_TIPO_VOTAVEL.str.lower() == "nominal"].groupby("NR_VOTAVEL").QT_VOTOS.sum()
                      .sort_values(ascending=False).index[:2].tolist())
        for t, dd in ((1, d1), (2, d2)):
            dd = dd.copy()
            dd["sec"] = dd[SEC].agg("-".join, axis=1)
            g = dd.groupby("sec")
            comp = g.QT_COMPARECIMENTO.first()
            for s in comp.index:
                bu.setdefault(s, {})[f"comp{t}"] = float(comp[s])
            for i, c in enumerate(cand):
                v = dd[dd.NR_VOTAVEL == c].groupby("sec").QT_VOTOS.sum()
                for s in comp.index:
                    bu[s][f"v{i}_{t}"] = float(v.get(s, 0))
        z = __import__("zipfile").ZipFile(baixar(urls[("2t", uf)], destdir, os.path.join(destdir, "manifesto_bweb.csv")))
        nm = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
        ap2 = pd.read_csv(__import__("io").BytesIO(z.read(nm)), sep=";", encoding="latin-1", dtype=str,
                          usecols=["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "QT_APTOS"]).drop_duplicates()
        ap2["sec"] = ap2.SG_UF.str.lower() + "-" + ap2.CD_MUNICIPIO.str.zfill(5) + "-" + ap2.NR_ZONA.str.zfill(4) + "-" + ap2.NR_SECAO.str.zfill(4)
        for s, v in zip(ap2.sec, pd.to_numeric(ap2.QT_APTOS)):
            bu.setdefault(s, {})["aptos"] = float(v)
    # metricas do log (cache)
    base = os.path.join(ROOT, "data", "raw", f"cache_{a.ano}_t{a.turno}")
    linhas = []
    for r in geo.to_dict("records"):
        s = r["sec"]
        fs = [f for f in glob.glob(os.path.join(base, r["uf"], r["mun"], r["zona"], r["secao"], "*"))
              if f.endswith((".jez", ".logjez"))]
        mtr = None
        for f in fs:
            txt, _ = ler_logd(f)
            m = metricas_painel(txt, a.ano, a.turno)
            if mtr is None:
                mtr = m
            else:
                for k in m:
                    mtr[k] = mtr[k] + m[k]
        b = bu.get(s, {})
        x = dict(sec=s, uf=r["uf"], mun=r["mun"], zona=r["zona"], secao=r["secao"], local=r["local"],
                 modelo=modelo.get(s, ""), colisao=s in trat, log_no_cache=mtr is not None)
        if mtr:
            hab = max(mtr["habilitados"], 1)
            x.update(habilitados=mtr["habilitados"], m2_sem_biometria=1 - mtr["habilitados_biometricos"] / hab,
                     m3_hab_por_mesario=mtr["habilitados_por_mesario"] / hab,
                     m6_liberacao_manual=mtr["liberacoes_manuais"] / hab)
            if s in trat:
                x["m7_votos_15min"], x["m7_z"] = rajada(mtr["horarios_votos"], ts_contest.get(s))
        if b.get("aptos") and "comp1" in b and "comp2" in b:
            x["m1_var_abstencao"] = (1 - b["comp2"] / b["aptos"]) - (1 - b["comp1"] / b["aptos"])
            for i, k in enumerate(("m5a_var_finalista_A", "m5b_var_finalista_B")):
                x[k] = b.get(f"v{i}_2", 0) / max(b["comp2"], 1) - b.get(f"v{i}_1", 0) / max(b["comp1"], 1)
        if s in mes.index:
            mm = mes.loc[s]
            x.update(n_mesarios=int(mm.n_mesarios), n_mesarios_eleitores=int(mm.n_mesarios_eleitores),
                     m4_nao_eleitor=mm.nao_eleitor / max(mm.n_mesarios, 1),
                     porta_estreita=(mm.porta_n / mm.n_mesarios_eleitores) if mm.n_mesarios_eleitores else np.nan,
                     porta_2022_mesma_uf_modelo=porta22.get((r["uf"], modelo.get(s, ""))))
        linhas.append(x)
    P = pd.DataFrame(linhas)
    P["local_key"] = P.uf + "-" + P.mun + "-" + P.zona + "-" + P.local.astype(str)
    tam_local = P.groupby("local_key").size()
    zs = []
    for r in P.to_dict("records"):
        if tam_local[r["local_key"]] >= MIN_LOCAL:
            viz = P[(P.local_key == r["local_key"]) & (~P.colisao) & (P.sec != r["sec"])]
            criterio = "mesmo_local"
        else:
            viz = P[(P.uf == r["uf"]) & (P.mun == r["mun"]) & (P.zona == r["zona"]) & (P.modelo == r["modelo"]) &
                    (~P.colisao) & (P.sec != r["sec"])]
            criterio = "mesma_zona_e_modelo"
        z = dict(sec=r["sec"], criterio_vizinhas=criterio, n_vizinhas=len(viz))
        for m in METRICAS + ["porta_estreita"]:
            n = r.get(TAXAS[m]) if m in TAXAS else None
            z[f"z_{m}"] = z_robusto(r.get(m, np.nan), viz[m].values if m in viz else [], n)
        zs.append(z)
    P = P.merge(pd.DataFrame(zs), on="sec")
    out = lambda m: P[f"z_{m}"].abs() > LIMIAR
    P["outlier_m1"], P["outlier_m2"], P["outlier_m3"] = out("m1_var_abstencao"), out("m2_sem_biometria"), out("m3_hab_por_mesario")
    P["outlier_m4"], P["outlier_m6"] = out("m4_nao_eleitor"), out("m6_liberacao_manual")
    P["outlier_m5"] = out("m5a_var_finalista_A") | out("m5b_var_finalista_B")
    P["outlier_porta"] = out("porta_estreita")
    P["outlier_m7"] = P.get("m7_z", pd.Series(np.nan, index=P.index)).abs() > LIMIAR
    P["n_outliers_m1_m6"] = P[["outlier_m1", "outlier_m2", "outlier_m3", "outlier_m4", "outlier_m5", "outlier_m6"]].sum(axis=1)
    P["anomala"] = (P.n_outliers_m1_m6 >= 2) | ((P.n_outliers_m1_m6 >= 1) & P.outlier_porta)
    P["anomala_com_rajada"] = ((P.n_outliers_m1_m6 + P.outlier_m7.astype(int)) >= 2) | (
        ((P.n_outliers_m1_m6 + P.outlier_m7.astype(int)) >= 1) & P.outlier_porta)
    P["painel_completo"] = P.log_no_cache & P.m1_var_abstencao.notna()
    P.to_csv(os.path.join(saida, "painel_local.csv"), index=False)
    # veredito de local
    C = P[P.colisao].copy()
    C["grupo"] = np.where(C.anomala_com_rajada, "G1_colisao_e_anomala", "G2_colisao_e_normal")
    C["veredito_local"] = np.where(C.anomala_com_rajada, "acidente_nao_chega_neste_local",
                                   "compativel_com_acidente_se_o_total_nacional_couber_no_intervalo")
    C.to_csv(os.path.join(saida, "painel_colisoes.csv"), index=False)
    # teste conjunto: permutacao dos rotulos de colisao dentro de municipio x modelo
    Q = P[P.painel_completo].copy()
    Q["estrato"] = Q.uf + "-" + Q.mun + "-" + Q.modelo
    obs = int(Q[Q.colisao].anomala.sum())
    rng = np.random.default_rng(a.semente)
    grupos = [(g.anomala.values, int(g.colisao.sum())) for _, g in Q.groupby("estrato") if g.colisao.any()]
    perm = np.zeros(a.reps, dtype=int)
    for i in range(a.reps):
        perm[i] = sum(int(an[rng.permutation(len(an))[:k]].sum()) for an, k in grupos)
    base_taxa = float(Q[~Q.colisao].anomala.mean()) if (~Q.colisao).any() else None
    res = dict(secoes_com_colisao=int(Q.colisao.sum()), secoes_com_colisao_anomalas=obs,
               proporcao_anomala=(obs / Q.colisao.sum()) if Q.colisao.sum() else None,
               taxa_anomala_sem_colisao_mesmos_estratos=base_taxa, esperado_permutacao=float(perm.mean()),
               p_permutacao=float((perm >= obs).mean()), reps=a.reps,
               razao_teste_conjunto=(obs / perm.mean()) if perm.mean() > 0 else None,
               secoes_com_colisao_sem_painel_completo=int((P.colisao & ~P.painel_completo).sum()),
               G1=int((C.grupo == "G1_colisao_e_anomala").sum()), G2=int((C.grupo == "G2_colisao_e_normal").sum()),
               nota=("G3 (varredura nacional sem colisao) nao e feito neste estudo; e a pergunta do Estudo 03. "
                     "Ausencia de colisao nao inocenta as demais secoes do pais."))
    json.dump(res, open(os.path.join(saida, "teste_conjunto.json"), "w"), indent=2, default=float, ensure_ascii=False)
    print(json.dumps(res, indent=2, default=float, ensure_ascii=False))


if __name__ == "__main__":
    main()

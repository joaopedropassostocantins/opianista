#!/usr/bin/env python3
"""
simulacao.py -- colisoes de titulo no registro de presenca de mesario: observado x nulo de digitacao.

Uso: python simulacao.py ANO TURNO [--reps 10000] [--semente 20261004] [--entrada DIR] [--saida DIR]

Entradas: data/censo/registros_<ANO>_t<T>_s*.csv, data/censo/logs_<ANO>_t<T>_s*.csv,
          data/processed/geo_<ANO>.csv (coordenadas por secao; eleitorado M)
Saidas (DIR de saida, padrao outputs/<ANO>_t<T>/):
  colisoes.csv, quase_duplicados.csv, parametros.json, tabela_faixas.csv, nulo_resumo.json

Definicoes (congeladas em registro/PRE_REGISTRO.md):
  registro      = linha "Mesário <T> registrado" no dia do turno, aplicacao VOTA, fase Oficial
  ocorrencia    = par (titulo, secao) com >= 1 registro
  colisao       = par nao ordenado de secoes distintas com a mesma ocorrencia de titulo, no mesmo turno
  excluida      = colisao em que as duas pontas compartilham id de urna ou hash de linha (replicacao por
                  contingencia/restart), ou envolvendo log com relogio inconsistente
  quase-duplicado = dois titulos distintos registrados na MESMA secao que diferem por um unico erro
                  (substituicao, transposicao adjacente, transposicao com salto, gemeo)
"""
import argparse
import glob
import itertools
import json
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np
import pandas as pd
from scipy.stats import chi2, poisson

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parsing import titulo_valido  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
TIPOS = ["sub_corpo", "sub_uf", "sub_dv", "trans", "salto", "gemeo"]
FAIXA_DIST = [("A_<1km", 0, 1), ("B_1-50km", 1, 50), ("C_>50km", 50, 1e9)]
FAIXA_INT = [("<60s", 0, 60), ("1-30min", 60, 1800), ("30min-4h", 1800, 14400), (">4h", 14400, 1e12)]
SEC = ["uf", "mun", "zona", "secao"]


# ------------------------------------------------------------------ utilidades
def faixa(v, faixas):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "ND"
    for nome, a, b in faixas:
        if a <= v < b:
            return nome
    return "ND"


def haversine(la1, lo1, la2, lo2):
    r = 6371.0088
    p1, p2 = np.radians(la1), np.radians(la2)
    dp, dl = p2 - p1, np.radians(lo2 - lo1)
    a = np.sin(dp / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * r * np.arcsin(np.sqrt(a))


def garwood(o, alfa=0.05):
    lo = 0.0 if o == 0 else chi2.ppf(alfa / 2, 2 * o) / 2
    hi = chi2.ppf(1 - alfa / 2, 2 * (o + 1)) / 2
    return lo, hi


def tipo_erro(a, b):
    """Tipo de erro unico que transforma a em b (simetrico), ou None."""
    dif = [i for i in range(12) if a[i] != b[i]]
    if len(dif) == 1:
        i = dif[0]
        return "sub_corpo" if i < 8 else ("sub_uf" if i < 10 else "sub_dv")
    if len(dif) == 2:
        i, j = dif
        if j == i + 1 and a[i] == b[j] and a[j] == b[i]:
            return "trans"
        if j == i + 1 and a[i] == a[j] and b[i] == b[j]:
            return "gemeo"
    if len(dif) == 2 and dif[1] == dif[0] + 2:
        i, j = dif
        if a[i] == b[j] and a[j] == b[i]:
            return "salto"
    return None


def vizinhos(t, tp):
    out = []
    if tp.startswith("sub"):
        rng = {"sub_corpo": range(0, 8), "sub_uf": range(8, 10), "sub_dv": range(10, 12)}[tp]
        for i in rng:
            for c in "0123456789":
                if c != t[i]:
                    out.append(t[:i] + c + t[i + 1:])
    elif tp == "trans":
        out = [t[:i] + t[i + 1] + t[i] + t[i + 2:] for i in range(11) if t[i] != t[i + 1]]
    elif tp == "salto":
        out = [t[:i] + t[i + 2] + t[i + 1] + t[i] + t[i + 3:] for i in range(10) if t[i] != t[i + 2]]
    elif tp == "gemeo":
        for i in range(11):
            if t[i] == t[i + 1]:
                out += [t[:i] + c + c + t[i + 2:] for c in "0123456789" if c != t[i]]
    return out


def n_vizinhos(t, tp):
    if tp == "sub_corpo":
        return 72
    if tp in ("sub_uf", "sub_dv"):
        return 18
    if tp == "trans":
        return sum(t[i] != t[i + 1] for i in range(11))
    if tp == "salto":
        return sum(t[i] != t[i + 2] for i in range(10))
    return 9 * sum(t[i] == t[i + 1] for i in range(11))


def pares_um_erro(titulos):
    """Todos os pares (a, b) de titulos do conjunto que diferem por um unico erro (via chaves de mascara)."""
    s = pd.Series(sorted(set(titulos)))
    pares = set()
    arr = s.values
    for i in range(12):  # substituicao na posicao i
        k = s.str[:i] + "_" + s.str[i + 1:]
        g = pd.DataFrame({"k": k.values, "t": arr})
        dup = g[g.k.duplicated(keep=False)]
        for _, grp in dup.groupby("k").t:
            for a, b in itertools.combinations(sorted(grp), 2):
                pares.add((a, b))
    for i in range(11):  # transposicao adjacente e gemeo nas posicoes i, i+1
        par = s.str[i:i + 2]
        ordenado = par.map(lambda x: "".join(sorted(x)))
        k1 = s.str[:i] + "_" + ordenado + "_" + s.str[i + 2:]
        gem = (par.str[0] == par.str[1]).values
        k2 = (s.str[:i] + "_gem_" + s.str[i + 2:]).where(gem, None)
        for k in (k1, k2):
            g = pd.DataFrame({"k": k.values, "t": arr}).dropna()
            dup = g[g.k.duplicated(keep=False)]
            for _, grp in dup.groupby("k").t:
                for a, b in itertools.combinations(sorted(grp), 2):
                    if tipo_erro(a, b):
                        pares.add((a, b))
    for i in range(10):  # transposicao com salto i, i+2
        ext = s.str[i] + s.str[i + 2]
        ordenado = ext.map(lambda x: "".join(sorted(x)))
        k = s.str[:i] + "_" + ordenado + s.str[i + 1] + "_" + s.str[i + 3:]
        g = pd.DataFrame({"k": k.values, "t": arr})
        dup = g[g.k.duplicated(keep=False)]
        for _, grp in dup.groupby("k").t:
            for a, b in itertools.combinations(sorted(grp), 2):
                if tipo_erro(a, b):
                    pares.add((a, b))
    return pares


# ------------------------------------------------------------------ carga
def carregar(ano, turno, entrada):
    R = pd.concat([pd.read_csv(f, dtype=str) for f in sorted(glob.glob(
        os.path.join(entrada, f"registros_{ano}_t{turno}_s*.csv")))], ignore_index=True)
    L = pd.concat([pd.read_csv(f, dtype=str) for f in sorted(glob.glob(
        os.path.join(entrada, f"logs_{ano}_t{turno}_s*.csv")))], ignore_index=True)
    for c in ["n_registrado", "n_ja_registrado", "n_invalido", "n_pedido", "n_conf_ok", "n_conf_nao",
              "relogio_inconsistente", "fase_nao_oficial"]:
        L[c] = pd.to_numeric(L[c], errors="coerce").fillna(0).astype(int)
    for c in SEC:
        R[c] = R[c].str.zfill({"uf": 2, "mun": 5, "zona": 4, "secao": 4}[c])
        L[c] = L[c].str.zfill({"uf": 2, "mun": 5, "zona": 4, "secao": 4}[c])
    return R, L


def preparar(R, L):
    L = L.drop_duplicates(SEC + ["arquivo"], keep="last")
    com_log = L[L.erro.isna() & L.sha256.notna()]
    inc = com_log[com_log.relogio_inconsistente == 1]
    chave_inc = set(map(tuple, inc[SEC + ["arquivo"]].values))
    R = R.drop_duplicates(SEC + ["arquivo", "hash_linha", "ts", "titulo"])
    R["_inc"] = [tuple(x) in chave_inc for x in R[SEC + ["arquivo"]].values]
    R_ok = R[~R._inc].copy()
    R_ok["sec"] = R_ok[SEC].agg("-".join, axis=1)
    R_ok["t_s"] = pd.to_datetime(R_ok.ts, format="%d/%m/%Y %H:%M:%S").astype("int64") // 10**9
    den = dict(
        secoes_quadro=int(L[SEC].drop_duplicates().shape[0]),
        secoes_sem_arquivo=int(L[L.erro.isin(["sem_arquivo_404", "aux_sem_log"])][SEC].drop_duplicates().shape[0]),
        logs_validos=int(len(com_log)),
        logs_relogio_inconsistente=int(len(inc)),
        logs_erro_leitura=int(L.erro.notna().sum() - L.erro.isin(["sem_arquivo_404", "aux_sem_log"]).sum()),
        secoes_com_log=int(com_log[SEC].drop_duplicates().shape[0]),
        registros_N=int(len(R_ok)),
        ocorrencias_titulo_secao=int(R_ok[["titulo", "sec"]].drop_duplicates().shape[0]),
        titulos_unicos=int(R_ok.titulo.nunique()),
        tentativas_invalidas_DV=int(com_log.n_invalido.sum()),
        ja_registrado=int(com_log.n_ja_registrado.sum()),
        conferencias_biometricas_coincide=int(com_log.n_conf_ok.sum()),
        conferencias_biometricas_nao_coincide=int(com_log.n_conf_nao.sum()),
        registros_titulo_DV_invalido=int((~R_ok.titulo.map(titulo_valido)).sum()),
    )
    return R_ok, den


# ------------------------------------------------------------------ medicao da taxa de erro
def medir_erros(R_ok):
    occ = R_ok.groupby(["sec", "titulo"]).agg(n=("ts", "size")).reset_index()
    por_sec = occ.groupby("sec").titulo.apply(list)
    linhas = []
    for sec, ts in por_sec.items():
        if len(ts) < 2:
            continue
        for a, b in itertools.combinations(sorted(ts), 2):
            tp = tipo_erro(a, b)
            if tp:
                linhas.append(dict(sec=sec, titulo_a=a, titulo_b=b, tipo=tp))
    qd = pd.DataFrame(linhas, columns=["sec", "titulo_a", "titulo_b", "tipo"])
    # probabilidade de o erro ficar visivel como quase-duplicado: o mesmo mesario precisa ter sido
    # registrado ao menos mais uma vez na secao (com o titulo correto). Estimada pela fracao de
    # ocorrencias (titulo, secao) com >= 2 registros entre as ocorrencias sem quase-duplicado.
    envolvidos = set(zip(qd.sec, qd.titulo_a)) | set(zip(qd.sec, qd.titulo_b))
    limpo = occ[[(s, t) not in envolvidos for s, t in zip(occ.sec, occ.titulo)]]
    d = float((limpo.n >= 2).mean()) if len(limpo) else float("nan")
    return qd, d


def p2_por_tipo(titulos, amostra=200000, semente=1):
    rng = np.random.default_rng(semente)
    tt = list(titulos)
    if len(tt) > amostra:
        tt = list(rng.choice(tt, amostra, replace=False))
    out = {}
    for tp in TIPOS:
        v = n = 0
        for t in tt:
            nb = vizinhos(t, tp)
            n += len(nb)
            v += sum(titulo_valido(x) for x in nb)
        out[tp] = v / n if n else 0.0
    return out


# ------------------------------------------------------------------ colisoes observadas
def colisoes_observadas(R_ok, geo, qd):
    m0 = R_ok.groupby("titulo").sec.nunique()
    R_ok = R_ok[R_ok.titulo.isin(m0[m0 >= 2].index)]
    g = R_ok.groupby(["titulo", "sec"]).agg(
        uf=("uf", "first"), mun=("mun", "first"), zona=("zona", "first"), secao=("secao", "first"),
        ts_lista=("t_s", lambda x: sorted(set(x))), ts_txt=("ts", lambda x: "|".join(sorted(set(x)))),
        urnas=("id_urna", lambda x: set(x)), hashes=("hash_linha", lambda x: set(x)),
        eleitor=("eleitor_secao", "max"), biometria=("biometria", lambda x: "|".join(sorted(set(x.dropna())))),
        n_reg=("ts", "size")).reset_index()
    mult = g.groupby("titulo").sec.nunique()
    g = g[g.titulo.isin(mult[mult >= 2].index)]
    qd_idx = defaultdict(set)
    for r in qd.itertuples():
        qd_idx[(r.sec, r.titulo_a)].add(r.titulo_b)
        qd_idx[(r.sec, r.titulo_b)].add(r.titulo_a)
    geo_i = geo.set_index("sec")
    linhas = []
    for t, grp in g.groupby("titulo"):
        for a, b in itertools.combinations(grp.to_dict("records"), 2):
            la1, lo1 = (geo_i.lat.get(a["sec"], np.nan), geo_i.lon.get(a["sec"], np.nan))
            la2, lo2 = (geo_i.lat.get(b["sec"], np.nan), geo_i.lon.get(b["sec"], np.nan))
            dist = float(haversine(la1, lo1, la2, lo2)) if not any(map(np.isnan, [la1, lo1, la2, lo2])) else np.nan
            mesmo_local = (geo_i.local.get(a["sec"]) == geo_i.local.get(b["sec"])
                           and a["mun"] == b["mun"] and a["zona"] == b["zona"])
            if np.isnan(dist) and mesmo_local:
                dist = 0.0
            dts = [abs(x - y) for x in a["ts_lista"] for y in b["ts_lista"]]
            delta = min(dts)
            excl = ""
            if a["urnas"] & b["urnas"]:
                excl = "mesma_urna(contingencia/replicacao)"
            elif a["hashes"] & b["hashes"]:
                excl = "linha_identica(replicacao)"
            qa, qb = qd_idx.get((a["sec"], t), set()), qd_idx.get((b["sec"], t), set())
            dono_a = a["eleitor"] == "1" and "coincide" in a["biometria"].split("|")
            dono_b = b["eleitor"] == "1" and "coincide" in b["biometria"].split("|")
            fd = faixa(dist, FAIXA_DIST)
            if excl:
                classe = "excluida_" + excl
            elif qa or qb:
                classe = "erro_digitacao_evidenciado"
            elif fd == "A_<1km":
                classe = "mesmo_predio_<1km"
            elif dono_a or dono_b:
                classe = "dono_conferido_por_biometria_em_uma_ponta"
            else:
                classe = "residuo_sem_explicacao_no_log"
            linhas.append(dict(
                titulo=t, uf_a=a["uf"], mun_a=a["mun"], zona_a=a["zona"], secao_a=a["secao"],
                uf_b=b["uf"], mun_b=b["mun"], zona_b=b["zona"], secao_b=b["secao"],
                ts_a=a["ts_txt"], ts_b=b["ts_txt"], delta_s=delta, faixa_intervalo=faixa(delta, FAIXA_INT),
                distancia_km=None if np.isnan(dist) else round(dist, 3), faixa_distancia=fd,
                mesmo_local_votacao=bool(mesmo_local),
                eleitor_secao_a=a["eleitor"], eleitor_secao_b=b["eleitor"],
                biometria_a=a["biometria"], biometria_b=b["biometria"],
                quase_dup_na_secao_a="|".join(sorted(qa)), quase_dup_na_secao_b="|".join(sorted(qb)),
                tipo_erro_a="|".join(sorted({tipo_erro(t, x) for x in qa})),
                tipo_erro_b="|".join(sorted({tipo_erro(t, x) for x in qb})),
                n_registros_a=a["n_reg"], n_registros_b=b["n_reg"],
                exclusao=excl, classificacao=classe))
    return pd.DataFrame(linhas)


# ------------------------------------------------------------------ nulo: via 2 (simulacao)
def preparar_alvos(R_ok, geo):
    """Pares (fonte -> alvo) entre titulos efetivamente registrados que distam um unico erro."""
    titulos = R_ok.titulo.unique()
    pares = pares_um_erro(titulos)
    occ = R_ok.groupby(["titulo", "sec"]).t_s.min().reset_index()
    secs_de = occ.groupby("titulo").apply(lambda d: list(zip(d.sec, d.t_s)), include_groups=False).to_dict()
    viz = defaultdict(list)  # fonte -> [(alvo, tipo)]
    for a, b in pares:
        tp = tipo_erro(a, b)
        viz[a].append((b, tp))
        viz[b].append((a, tp))
    return viz, secs_de


def simular(R_ok, geo, E, pesos, reps, semente, viz, secs_de):
    """Cada erro: fonte = evento de registro sorteado uniformemente; tipo ~ pesos; resultado uniforme entre
    os vizinhos do tipo. Conta colisoes (alvo registrado em secao diferente da fonte)."""
    rng = np.random.default_rng(semente)
    ev = R_ok[["titulo", "sec", "t_s"]].to_numpy()
    N = len(ev)
    tipos = list(pesos)
    w = np.array([pesos[k] for k in tipos], dtype=float)
    w = w / w.sum()
    # pre-calculo: para cada evento-fonte com algum vizinho registrado, P(acerto | tipo) e lista de alvos
    geo_i = geo.set_index("sec")
    lat, lon = geo_i.lat.to_dict(), geo_i.lon.to_dict()
    uf_de = geo_i.uf.to_dict()
    fontes, prob, alvo_lista = [], [], []
    for i, (t, s, ts) in enumerate(ev):
        if t not in viz:
            continue
        por_tipo = defaultdict(list)
        for b, tp in viz[t]:
            por_tipo[tp].append(b)
        for k, tp in enumerate(tipos):
            if tp in por_tipo:
                nv = n_vizinhos(t, tp)
                if nv == 0:
                    continue
                cols = []
                for b in por_tipo[tp]:
                    for s2, ts2 in secs_de.get(b, []):
                        if s2 != s:
                            d = (haversine(lat.get(s, np.nan), lon.get(s, np.nan), lat.get(s2, np.nan),
                                           lon.get(s2, np.nan)))
                            cols.append((b, s, s2, faixa(float(d), FAIXA_DIST), faixa(abs(ts - ts2), FAIXA_INT),
                                         uf_de.get(s, s[:2])))
                fontes.append(i)
                prob.append(w[k] * len(por_tipo[tp]) / nv)  # P(tipo) * P(cair num alvo registrado | tipo)
                alvo_lista.append((cols, len(por_tipo[tp])))
    prob = np.array(prob) / N  # probabilidade por erro de escolher esta fonte e acertar um alvo
    p_tot = prob.sum()
    lam = E * p_tot
    nomes_d = [f[0] for f in FAIXA_DIST] + ["ND"]
    nomes_i = [f[0] for f in FAIXA_INT] + ["ND"]
    cont = np.zeros((reps, len(nomes_d), len(nomes_i)), dtype=np.int32)
    conc_max_secao = np.zeros(reps, dtype=np.int32)
    uf_cont = defaultdict(lambda: np.zeros(reps, dtype=np.int32))
    if p_tot > 0:
        pcond = prob / p_tot
        for r in range(reps):
            k = rng.binomial(int(E), p_tot)
            if k == 0:
                continue
            esc = rng.choice(len(pcond), size=k, p=pcond)
            secs = Counter()
            for j in esc:
                cols, nalvos = alvo_lista[j]
                alvo = rng.integers(nalvos)
                alvos = sorted({c[0] for c in cols})
                if alvo >= len(alvos):
                    continue
                for c in cols:
                    if c[0] == alvos[alvo]:
                        cont[r, nomes_d.index(c[3]), nomes_i.index(c[4])] += 1
                        secs[c[1]] += 1
                        uf_cont[c[5]][r] += 1
            conc_max_secao[r] = max(secs.values()) if secs else 0
    return dict(lambda_total=float(lam), cont=cont, nomes_d=nomes_d, nomes_i=nomes_i,
                conc_max_secao=conc_max_secao, uf_cont={k: v for k, v in uf_cont.items()})


# ------------------------------------------------------------------ via 3 (segunda ordem)
def via3(R_ok, E, pesos, reps, semente, T_set):
    """Dois erros distintos caindo no MESMO titulo valido que nao pertence a nenhum mesario registrado,
    em secoes diferentes. Monte Carlo com geracao explicita do numero digitado."""
    rng = np.random.default_rng(semente + 3)
    ev = R_ok[["titulo", "sec"]].to_numpy()
    tipos = list(pesos)
    w = np.array([pesos[k] for k in tipos], dtype=float)
    w = w / w.sum()
    total = 0
    reps_v = int(max(50, min(reps, 5_000_000 // max(1, int(E)))))
    for _ in range(reps_v):
        idx = rng.integers(len(ev), size=int(E))
        tps = rng.choice(len(tipos), size=int(E), p=w)
        alvo = defaultdict(set)
        for i, k in zip(idx, tps):
            t, s = ev[i]
            nb = vizinhos(t, tipos[k])
            if not nb:
                continue
            x = nb[rng.integers(len(nb))]
            if titulo_valido(x) and x not in T_set:
                alvo[x].add(s)
        total += sum(math.comb(len(v), 2) for v in alvo.values() if len(v) >= 2)
    return total / reps_v, reps_v


# ------------------------------------------------------------------ principal
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ano", type=int)
    ap.add_argument("turno", type=int)
    ap.add_argument("--reps", type=int, default=10000)
    ap.add_argument("--semente", type=int, default=20261004)
    ap.add_argument("--entrada", default=os.path.join(ROOT, "data", "censo"))
    ap.add_argument("--saida", default=None)
    ap.add_argument("--geo", default=None)
    a = ap.parse_args()
    saida = a.saida or os.path.join(ROOT, "outputs", f"{a.ano}_t{a.turno}")
    os.makedirs(saida, exist_ok=True)

    R, L = carregar(a.ano, a.turno, a.entrada)
    R_ok, den = preparar(R, L)
    geo = pd.read_csv(a.geo or os.path.join(ROOT, "data", "processed", f"geo_{a.ano if a.ano != 2024 else 2024}.csv"),
                      dtype={"uf": str, "mun": str, "zona": str, "secao": str, "local": str})
    geo["sec"] = geo[SEC].agg("-".join, axis=1)
    M = float(geo.qt_eleitor.sum())

    # --- taxa de erro medida
    qd, d = medir_erros(R_ok)
    qd.to_csv(os.path.join(saida, "quase_duplicados.csv"), index=False)
    p2k = p2_por_tipo(R_ok.titulo.unique())
    obs_k = qd.tipo.value_counts().to_dict()
    # distribuicao de TODOS os erros: proporcional a observados / p2 (o quase-duplicado so mostra erros validos)
    bruto = {k: obs_k.get(k, 0) / p2k[k] for k in TIPOS if p2k[k] > 0}
    if sum(bruto.values()) == 0:
        bruto = {"sub_corpo": 0.791 * 8 / 12, "sub_uf": 0.791 * 2 / 12, "sub_dv": 0.791 * 2 / 12,
                 "trans": 0.102, "salto": 0.008, "gemeo": 0.006}
    tot = sum(bruto.values())
    pesos = {k: v / tot for k, v in bruto.items()}
    p2w = sum(pesos[k] * p2k[k] for k in pesos)
    U_obs = len(qd)
    U_est = U_obs / d if d and d > 0 else float("nan")
    N = den["registros_N"]
    E = U_est / p2w
    p1 = E / N
    q = den["titulos_unicos"] / M
    # alternativa (limite superior): tentativas DV-invalidas tratadas como erros de 12 digitos
    E_inv = den["tentativas_invalidas_DV"] / (1 - p2w)
    par = dict(ano=a.ano, turno=a.turno, **den, M_eleitorado=M, q=q,
               quase_duplicados=U_obs, quase_dup_por_tipo=obs_k, prob_visibilidade_d=d,
               titulos_validos_errados_estimados=U_est, p2_por_tipo=p2k, pesos_tipo_erro=pesos, p2_ponderado=p2w,
               erros_totais_E=E, p1=p1, E_alternativo_invalidos=E_inv, p1_alternativo=E_inv / N,
               via1_colisoes_esperadas=N * p1 * p2w * q)
    # --- observado
    col = colisoes_observadas(R_ok, geo, qd)
    col.to_csv(os.path.join(saida, "colisoes.csv"), index=False)
    # --- nulo via 2 + sensibilidade
    viz, secs_de = preparar_alvos(R_ok, geo)
    cenarios = {"central": E, "p1_x0.5": 0.5 * E, "p1_x2": 2 * E, "p1_invalidos_DV": E_inv}
    res = {}
    for nome, e in cenarios.items():
        reps = a.reps if nome == "central" else max(2000, a.reps // 5)
        sim = simular(R_ok, geo, round(e), pesos, reps, a.semente, viz, secs_de)
        res[nome] = sim
    v3, v3_reps = via3(R_ok, round(E), pesos, a.reps, a.semente, set(R_ok.titulo.unique()))
    par["via3_segunda_ordem_esperado"] = v3
    par["via3_reps"] = v3_reps
    # --- tabela por faixa (observado = colisoes nao excluidas)
    obs = col[col.exclusao == ""] if len(col) else col
    sim = res["central"]
    linhas = []
    for di, dn in enumerate(sim["nomes_d"]):
        for ii, inn in enumerate(sim["nomes_i"] + ["TOTAL"]):
            if inn == "TOTAL":
                s = sim["cont"][:, di, :].sum(axis=1)
                o = int((obs.faixa_distancia == dn).sum()) if len(obs) else 0
            else:
                s = sim["cont"][:, di, ii]
                o = int(((obs.faixa_distancia == dn) & (obs.faixa_intervalo == inn)).sum()) if len(obs) else 0
            e = float(s.mean())
            lo, hi = garwood(o)
            q_lo, q_hi = np.quantile(s, [0.025, 0.975])
            p_sup = float((s >= o).mean())
            row = dict(faixa_distancia=dn, faixa_intervalo=inn, observado=o, esperado_via2=e,
                       nulo_IC95_inf=float(q_lo), nulo_IC95_sup=float(q_hi), p_sim_obs_maior_igual=p_sup,
                       razao=o / e if e > 0 else None, razao_IC95_inf=lo / e if e > 0 else None,
                       razao_IC95_sup=hi / e if e > 0 else None)
            for nome in ("p1_x0.5", "p1_x2", "p1_invalidos_DV"):
                ss = res[nome]["cont"][:, di, :].sum(axis=1) if inn == "TOTAL" else res[nome]["cont"][:, di, ii]
                row[f"esperado_{nome}"] = float(ss.mean())
                row[f"nulo_IC95_sup_{nome}"] = float(np.quantile(ss, 0.975))
            linhas.append(row)
    tab = pd.DataFrame(linhas)
    tab.to_csv(os.path.join(saida, "tabela_faixas.csv"), index=False)
    # --- concentracao
    conc = {}
    if len(obs):
        por_sec = Counter(list(obs.uf_a + "-" + obs.mun_a + "-" + obs.zona_a + "-" + obs.secao_a) +
                          list(obs.uf_b + "-" + obs.mun_b + "-" + obs.zona_b + "-" + obs.secao_b))
        n_sec_env = len(por_sec)
        conc["secoes_envolvidas"] = n_sec_env
        conc["fracao_secoes_envolvidas"] = n_sec_env / den["secoes_com_log"]
        conc["max_colisoes_por_secao_obs"] = int(max(por_sec.values()))
        x = np.array(list(por_sec.values()) + [0] * (den["secoes_com_log"] - n_sec_env))
        conc["indice_dispersao_por_secao"] = float(x.var(ddof=1) / x.mean()) if x.mean() > 0 else None
        conc["p_sim_max_por_secao"] = float((sim["conc_max_secao"] >= conc["max_colisoes_por_secao_obs"]).mean())
        uf_obs = Counter(obs.uf_a)
        ufs = sorted(set(uf_obs) | set(sim["uf_cont"]))
        esp = np.array([sim["uf_cont"].get(u, np.zeros(1)).mean() for u in ufs])
        o_uf = np.array([uf_obs.get(u, 0) for u in ufs])
        if esp.sum() > 0:
            esp_n = esp / esp.sum() * o_uf.sum()
            m = esp_n > 0
            conc["chi2_uf"] = float((((o_uf[m] - esp_n[m]) ** 2) / esp_n[m]).sum())
            conc["gl_uf"] = int(m.sum() - 1)
            conc["p_chi2_uf"] = float(chi2.sf(conc["chi2_uf"], max(1, conc["gl_uf"])))
            conc["uf_fora_do_suporte_do_nulo"] = {u: int(uf_obs.get(u, 0)) for u, e in zip(ufs, esp) if e == 0 and uf_obs.get(u, 0)}
        conc["uf_observado"] = dict(uf_obs)
    par["concentracao"] = conc
    par["nulo"] = {k: dict(lambda_total=v["lambda_total"],
                           media_sim_total=float(v["cont"].sum(axis=(1, 2)).mean())) for k, v in res.items()}
    par["classificacao_casos"] = col.classificacao.value_counts().to_dict() if len(col) else {}
    json.dump(par, open(os.path.join(saida, "parametros.json"), "w"), indent=2, default=float, ensure_ascii=False)
    print(json.dumps(par, indent=2, default=float, ensure_ascii=False))
    print(tab.to_string())


if __name__ == "__main__":
    main()

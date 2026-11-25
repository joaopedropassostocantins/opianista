#!/usr/bin/env python3
"""
probabilidade_uf.py -- EXPLORATORIO (nao faz parte do teste congelado). Probabilidade, por UF, de um erro de
digitacao no registro de mesario gerar colisao com outro mesario, com os componentes MEDIDOS nos logs.
Nao usa contagem de colisoes observadas (so parametros do nulo).

Cadeia por UF de emissao do titulo (prefixo u, digitos 9-10):
  P(colisao | erro) = sum_k w_k * P(valido E dentro da faixa emitida | tipo k, u) * dens_u
    w_k     : distribuicao de todos os erros por tipo (quase-duplicados observados / p2_k)
    faixa   : corpo (digitos 1-8) <= R_u, maior corpo de titulo observado com prefixo u
    dens_u  : m_u / R_u = titulos de mesario com prefixo u por numero emitido (densidade de mesarios)
  E_u = N_u * p1 * P(colisao | erro)
    N_u     : registros de presenca na UF (secoes com log * registros por secao medidos)
    p1      : erros por registro, medido = U / p2 / N, com U = quase-duplicados / visibilidade

Validacao: nas UFs com censo completo, a densidade modelada e comparada com a fracao EMPIRICA de vizinhos
validos que sao titulos de mesario registrados (Via 2 restrita a fonte da UF). Resultado: o modelo de
densidade (m_u / R_u) subestima em 10 a 100 vezes, porque titulos vizinhos sao emitidos no mesmo lugar e
epoca e os mesarios se aglomeram numericamente. As colunas E_* usam o h EMPIRICO agregado; a coluna
E_modelo_densidade fica so como registro do modelo refutado.

Uso: python probabilidade_uf.py DIR_CENSO PILOTO_REGISTROS.csv CATALOGO_DIR SAIDA_DIR
"""
import glob
import itertools
import json
import math
import os
import sys
from collections import Counter, defaultdict

import numpy as np
import pandas as pd
from scipy.stats import chi2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parsing import titulo_valido  # noqa: E402
from simulacao import TIPOS, tipo_erro, vizinhos, n_vizinhos  # noqa: E402

PREFIXO_UF = {"01": "sp", "02": "mg", "03": "rj", "04": "rs", "05": "ba", "06": "pr", "07": "ce", "08": "pe",
              "09": "sc", "10": "go", "11": "ma", "12": "pb", "13": "pa", "14": "es", "15": "pi", "16": "rn",
              "17": "al", "18": "mt", "19": "ms", "20": "df", "21": "se", "22": "am", "23": "ro", "24": "ac",
              "25": "ap", "26": "rr", "27": "to", "28": "zz"}
UF_PREFIXO = {v: k for k, v in PREFIXO_UF.items()}
SEMENTE = 20261004


def garwood(o):
    return (0.0 if o == 0 else chi2.ppf(0.025, 2 * o) / 2), chi2.ppf(0.975, 2 * (o + 1)) / 2


def main(dir_censo, piloto, catalogo, saida):
    os.makedirs(saida, exist_ok=True)
    rng = np.random.default_rng(SEMENTE)
    # ---------- 1. p1 medido no censo (quase-duplicados), apenas UFs com secoes processadas
    R = pd.concat([pd.read_csv(f, dtype=str) for f in glob.glob(os.path.join(dir_censo, "registros_2026_t1_s*.csv"))])
    L = pd.concat([pd.read_csv(f, dtype=str) for f in glob.glob(os.path.join(dir_censo, "logs_2026_t1_s*.csv"))])
    L["relogio_inconsistente"] = pd.to_numeric(L.relogio_inconsistente, errors="coerce").fillna(0)
    ruins = set(map(tuple, L[L.relogio_inconsistente == 1][["uf", "mun", "zona", "secao", "arquivo"]].values))
    R = R[[tuple(x) not in ruins for x in R[["uf", "mun", "zona", "secao", "arquivo"]].values]]
    R["sec"] = R.uf + "-" + R.mun + "-" + R.zona + "-" + R.secao
    N_med = len(R)
    occ = R.groupby(["sec", "titulo"]).size().rename("n").reset_index()
    qd = []
    for sec, ts in occ.groupby("sec").titulo:
        for a, b in itertools.combinations(sorted(ts), 2):
            tp = tipo_erro(a, b)
            if tp:
                qd.append((sec, a, b, tp))
    env = {(s, a) for s, a, b, t in qd} | {(s, b) for s, a, b, t in qd}
    limpo = occ[[(s, t) not in env for s, t in zip(occ.sec, occ.titulo)]]
    d = float((limpo.n >= 2).mean())
    tipos_obs = Counter(t for *_, t in qd)
    # ---------- 2. titulos de referencia (piloto nacional + censo parcial)
    P = pd.read_csv(piloto, dtype=str)
    todos = pd.concat([P[["uf", "titulo"]], R[["uf", "titulo"]]]).drop_duplicates("titulo")
    todos["pref"] = todos.titulo.str[8:10]
    todos["corpo"] = todos.titulo.str[:8].astype(int)
    R_u = todos.groupby("pref").corpo.max().to_dict()
    # p2 e fracao valida-dentro-da-faixa por prefixo e tipo (ate 1.500 titulos por prefixo)
    p2_uk, pin_uk = defaultdict(dict), defaultdict(dict)
    for u, g in todos.groupby("pref"):
        tt = g.titulo.values
        if len(tt) > 1500:
            tt = rng.choice(tt, 1500, replace=False)
        for k in TIPOS:
            n = v = vin = 0
            for t in tt:
                for x in vizinhos(t, k):
                    n += 1
                    if titulo_valido(x):
                        v += 1
                        if int(x[:8]) <= R_u[u]:
                            vin += 1
            p2_uk[u][k] = v / n if n else 0.0
            pin_uk[u][k] = vin / n if n else 0.0
    p2_nac = {k: float(np.mean([p2_uk[u][k] for u in p2_uk])) for k in TIPOS}
    bruto = {k: tipos_obs.get(k, 0) / p2_nac[k] for k in TIPOS if p2_nac[k] > 0}
    if sum(bruto.values()) == 0 or len(qd) < 10:
        bruto = {"sub_corpo": 0.791 * 8 / 12, "sub_uf": 0.791 * 2 / 12, "sub_dv": 0.791 * 2 / 12,
                 "trans": 0.102, "salto": 0.008, "gemeo": 0.006}
    w = {k: bruto.get(k, 0.0) / sum(bruto.values()) for k in TIPOS}
    p2w = sum(w[k] * p2_nac[k] for k in w)
    U = len(qd) / d
    E_med = U / p2w
    p1 = E_med / N_med
    lo, hi = garwood(len(qd))
    p1_ic = (lo / d / p2w / N_med, hi / d / p2w / N_med)
    inval = pd.to_numeric(L.n_invalido, errors="coerce").fillna(0).sum()
    p1_inval = inval / (1 - p2w) / N_med
    # ---------- 3. mesarios por prefixo (m_u) e registros por UF (N_u), projecao nacional
    reg_por_sec_piloto = len(P) / P[["uf", "mun", "zona", "secao"]].drop_duplicates().shape[0]
    tit_por_sec_piloto = P.groupby(["uf", "mun", "zona", "secao"]).titulo.nunique().mean()
    secoes_uf = {}
    for f in glob.glob(os.path.join(catalogo, "*-p3220-cs.json")):
        dd = json.load(open(f, encoding="utf-8"))
        secoes_uf[dd["abr"][0]["cd"]] = sum(len(z["sec"]) for m in dd["abr"][0]["mu"] for z in m["zon"])
    frac_com_log = 1 - 0.039  # secoes agregadas sem arquivo (piloto: 81/2.081)
    share = pd.crosstab(P.uf, P.titulo.str[8:10], normalize="index")
    m_u = defaultdict(float)
    for uf_sec, n_sec in secoes_uf.items():
        if uf_sec in share.index:
            for pref, s in share.loc[uf_sec].items():
                m_u[pref] += n_sec * frac_com_log * tit_por_sec_piloto * s
    # ---------- 4. validacao empirica nas UFs com censo completo
    T_set = set(R.titulo)
    secs_de = R.groupby("titulo").sec.apply(set).to_dict()
    completas = [u for u in ("ac", "al", "am", "ap")]
    valid = {}
    for uf in completas:
        u = UF_PREFIXO[uf]
        src = R[(R.uf == uf) & (R.titulo.str[8:10] == u)][["titulo", "sec"]].drop_duplicates()
        h_emp = 0.0
        for t, s in src.values:
            for k in TIPOS:
                nv = n_vizinhos(t, k)
                if nv == 0:
                    continue
                hits = sum(1 for x in vizinhos(t, k) if x in T_set and (secs_de[x] - {s}))
                h_emp += w[k] * hits / nv
        h_emp /= max(1, len(src))
        h_mod = sum(w[k] * pin_uk[u][k] for k in TIPOS) * m_u[u] / R_u[u]
        valid[uf] = dict(h_empirico=h_emp, h_modelo=h_mod, fontes=len(src))
    # ---------- 5. tabela por UF
    # h empirico agregado (media ponderada pelas fontes das UFs com censo completo); limite inferior, pois
    # titulos de mesario com o mesmo prefixo registrados em UFs ainda nao processadas nao entram em T
    h_emp_pool = sum(v["h_empirico"] * v["fontes"] for v in valid.values()) / sum(v["fontes"] for v in valid.values())
    linhas = []
    for uf in sorted(secoes_uf):
        u = UF_PREFIXO[uf]
        if u not in R_u:
            continue
        N_u = secoes_uf[uf] * frac_com_log * reg_por_sec_piloto
        p_valido = sum(w[k] * p2_uk[u][k] for k in TIPOS)
        p_val_faixa = sum(w[k] * pin_uk[u][k] for k in TIPOS)
        dens = m_u[u] / R_u[u]
        h = p_val_faixa * dens
        linhas.append(dict(uf=uf.upper(), prefixo=u, secoes=secoes_uf[uf], registros_N=round(N_u),
                           mesarios_prefixo_m=round(m_u[u]), faixa_emitida_R=R_u[u],
                           P1_erro_vira_valido=p_valido, P1b_valido_e_emitido=p_val_faixa,
                           P2_densidade_mesario=dens, P_colisao_por_erro=h,
                           E_modelo_densidade=N_u * p1 * h,
                           h_empirico_uf=valid.get(uf, {}).get("h_empirico"),
                           E_p1_x0_5=N_u * 0.5 * p1 * h_emp_pool, E_central=N_u * p1 * h_emp_pool,
                           E_p1_x2=N_u * 2 * p1 * h_emp_pool, E_p1_invalidos=N_u * p1_inval * h_emp_pool))
    tab = pd.DataFrame(linhas).sort_values("E_central", ascending=False)
    tot = tab[["registros_N", "E_modelo_densidade", "E_p1_x0_5", "E_central", "E_p1_x2", "E_p1_invalidos"]].sum()
    tab.to_csv(os.path.join(saida, "probabilidade_por_uf.csv"), index=False)
    res = dict(registros_medidos=N_med, quase_duplicados=len(qd), tipos_quase_dup=dict(tipos_obs),
               visibilidade_d=d, p2_por_tipo_nacional=p2_nac, pesos_tipo=w, p2_ponderado=p2w,
               p1_medido=p1, p1_IC95=p1_ic, p1_por_invalidos=p1_inval,
               registros_por_secao=reg_por_sec_piloto, titulos_mesario_por_secao=tit_por_sec_piloto,
               validacao_modelo=valid, h_empirico_agregado=h_emp_pool, total_brasil=tot.to_dict())
    json.dump(res, open(os.path.join(saida, "probabilidade_por_uf.json"), "w"), indent=2, default=float)
    print(json.dumps(res, indent=2, default=float))
    pd.set_option("display.width", 250)
    print(tab.to_string(index=False, float_format=lambda x: f"{x:.3g}"))


if __name__ == "__main__":
    main(*sys.argv[1:5])

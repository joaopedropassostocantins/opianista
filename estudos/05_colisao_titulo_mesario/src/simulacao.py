#!/usr/bin/env python3
"""
simulacao.py (v2) -- colisao de titulo no registro de presenca de mesario, 2o turno.

Uso: python simulacao.py ANO [--turno 2] [--reps 10000] [--semente 20261025]
       [--entrada data/censo] [--geo data/processed/geo_<ANO>.csv] [--saida data/outputs/<ANO>_t2]

Saidas (com titulo em claro; ficam em data/, fora do Git; versoes publicaveis via pseudonimizar.py):
  colisoes.csv, bloqueios.csv, quase_duplicados.csv, p1_por_caminho.csv, D_por_uf.csv, D_por_zona.csv,
  tabela_faixas.csv, tabela_uf.csv, parametros.json (inclui o veredito pela regra pre-registrada)

Definicoes (protocolos/04_emenda_estudo05_2t_20261125.md):
  registro  : "Mesário <T> registrado", VOTA, data do turno, fase Oficial
  colisao   : mesmo titulo registrado em duas secoes diferentes no turno (par nao ordenado de secoes)
  bloqueio  : "Mesário <T> já registrado" (a urna recusa titulo ja registrado nela); nunca somado a colisao
  excluidas : pontas com a mesma urna ou a mesma linha (replicacao por contingencia/restart); logs com
              relogio inconsistente; linhas fora da fase Oficial
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
from scipy.stats import chi2

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parsing import DATAS, titulo_valido  # noqa: E402
from densidade import (TIPOS, CAMINHO, tipo_erro, tipo_erro_dir, vizinhos, p2_por_tipo,  # noqa: E402
                       quase_duplicados, medir_p1, medir_D, vizinhos_registrados, aplicar_loo)

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
FAIXA_DIST = [("A_<1km", 0, 1), ("B_1-50km", 1, 50), ("C_>50km", 50, 1e9)]
FAIXA_INT = [("<60s", 0, 60), ("1-30min", 60, 1800), ("30min-4h", 1800, 14400), (">4h", 14400, 1e12)]
SEC = ["uf", "mun", "zona", "secao"]
CASO_NOMINAL = ("ba", "PORTO SEGURO", "ba", "CASA NOVA")
ESTRATOS = [("G_eleitorado>=10mi", 10_000_000, 10**12), ("M_eleitorado_4-10mi", 4_000_000, 10_000_000),
            ("P_eleitorado<4mi", 0, 4_000_000)]  # emenda 05: estratos por eleitorado
PERIODOS = [("manha_<12h", 0, 12), ("tarde_12-17h", 12, 17), ("pos_17h", 17, 24)]
LIMIAR_POS9H = 0.05   # emenda 05: acima de 5% dos registros apos 9h, faixas de intervalo estratificadas por periodo
VEL_MAX_KMH = 120.0   # familia 2 eliminada se a distancia exigir velocidade acima disso no intervalo
LIMIAR_TESTE_UF = 3.0


def periodo(t_s):
    h = int((t_s // 3600) % 24)
    return next(n for n, a, b in PERIODOS if a <= h < b)


def faixa(v, faixas):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "ND"
    for nome, a, b in faixas:
        if a <= v < b:
            return nome
    return "ND"


def haversine(la1, lo1, la2, lo2):
    p1, p2 = np.radians(la1), np.radians(la2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lo2 - lo1) / 2) ** 2
    return 2 * 6371.0088 * np.arcsin(np.sqrt(a))


def garwood(o):
    return (0.0 if o == 0 else chi2.ppf(0.025, 2 * o) / 2), chi2.ppf(0.975, 2 * (o + 1)) / 2


def ler(padrao):
    fs = sorted(glob.glob(padrao))
    return pd.concat([pd.read_csv(f, dtype=str) for f in fs], ignore_index=True) if fs else pd.DataFrame()


def zfill(df):
    for c, n in (("uf", 2), ("mun", 5), ("zona", 4), ("secao", 4)):
        if c in df.columns:
            df[c] = df[c].str.zfill(n)
    return df


# ------------------------------------------------------------------ carga e limpeza
def carregar(ano, turno, entrada):
    R = zfill(ler(os.path.join(entrada, f"registros_{ano}_t{turno}_s*.csv")))
    L = zfill(ler(os.path.join(entrada, f"logs_{ano}_t{turno}_s*.csv")))
    B = zfill(ler(os.path.join(entrada, f"bloqueios_{ano}_t{turno}_s*.csv")))
    for c in ["n_registrado", "n_ja_registrado", "n_invalido", "n_pedido", "n_conf_ok", "n_conf_nao",
              "relogio_inconsistente", "fase_nao_oficial"]:
        L[c] = pd.to_numeric(L[c], errors="coerce").fillna(0).astype(int)
    return R, L, B


def preparar(R, L, B, ano, turno):
    data = DATAS[(ano, turno)]
    L = L.drop_duplicates(SEC + ["arquivo"], keep="last")
    sem = L.erro.isin(["sem_arquivo_404", "aux_sem_log"])
    com_log = L[L.erro.isna() & L.sha256.notna()]
    inc = com_log[com_log.relogio_inconsistente == 1]
    chave_inc = set(map(tuple, inc[SEC + ["arquivo"]].values))
    R = R.drop_duplicates(SEC + ["arquivo", "hash_linha", "ts", "titulo"])
    R = R[R.ts.str.startswith(data)]
    R_ok = R[[tuple(x) not in chave_inc for x in R[SEC + ["arquivo"]].values]].copy()
    R_ok["sec"] = R_ok[SEC].agg("-".join, axis=1)
    # segundos desde 1970 independentemente da resolucao interna do pandas (ns no 2.x, us no 3.x); correcao da
    # emenda 07: a versao anterior dividia por 10**9 e, com datetime64[us], encolhia todos os intervalos 1.000 vezes
    R_ok["t_s"] = ((pd.to_datetime(R_ok.ts, format="%d/%m/%Y %H:%M:%S") - pd.Timestamp("1970-01-01"))
                   .dt.total_seconds().round().astype("int64"))
    if len(B):
        B = B.drop_duplicates(SEC + ["arquivo", "hash_linha", "ts", "titulo"])
        B = B[B.ts.str.startswith(data)]
        B = B[[tuple(x) not in chave_inc for x in B[SEC + ["arquivo"]].values]].copy()
        B["sec"] = B[SEC].agg("-".join, axis=1)
    den = dict(
        escopo=f"{turno}o turno de {ano}, {data}",
        secoes_quadro=int(L[SEC].drop_duplicates().shape[0]),
        secoes_sem_arquivo=int(L[sem][SEC].drop_duplicates().shape[0]),
        logs_validos=int(len(com_log)),
        logs_relogio_inconsistente=int(len(inc)),
        logs_erro_leitura=int((L.erro.notna() & ~sem).sum()),
        secoes_com_log=int(com_log[SEC].drop_duplicates().shape[0]),
        registros_N=int(len(R_ok)),
        ocorrencias_titulo_secao=int(R_ok[["titulo", "sec"]].drop_duplicates().shape[0]),
        titulos_unicos=int(R_ok.titulo.nunique()),
        tentativas_invalidas=int(com_log.n_invalido.sum()),
        bloqueios_ja_registrado=int(len(B)),
        conferencias_biometricas_coincide=int(com_log.n_conf_ok.sum()),
        conferencias_biometricas_nao_coincide=int(com_log.n_conf_nao.sum()),
        registros_titulo_DV_invalido=int((~R_ok.titulo.map(titulo_valido)).sum()),
        registros_nao_eleitor_da_secao=float((R_ok.eleitor_secao == "0").mean()),
    )
    tent = den["tentativas_invalidas"] + den["registros_N"] + den["bloqueios_ja_registrado"]
    den["taxa_rejeicao_DV"] = den["tentativas_invalidas"] / tent if tent else None
    return R_ok, B, den


# ------------------------------------------------------------------ observado
def tabela_secoes(R_ok):
    return R_ok.groupby(["titulo", "sec"]).agg(
        uf=("uf", "first"), mun=("mun", "first"), zona=("zona", "first"), secao=("secao", "first"),
        ts_lista=("t_s", lambda x: sorted(set(x))), ts_txt=("ts", lambda x: "|".join(sorted(set(x)))),
        urnas=("id_urna", lambda x: set(x)), hashes=("hash_linha", lambda x: set(x)),
        eleitor=("eleitor_secao", "max"), biometria=("biometria", lambda x: "|".join(sorted(set(x.dropna())))),
        n_reg=("ts", "size")).reset_index()


def colisoes_observadas(R_ok, geo, qd, nomes_mun, modelo_sec=None):
    m0 = R_ok.groupby("titulo").sec.nunique()
    g = tabela_secoes(R_ok[R_ok.titulo.isin(m0[m0 >= 2].index)])
    n_mes = R_ok.groupby("sec").titulo.nunique().to_dict()
    qd_idx = defaultdict(set)
    for r in qd.itertuples():
        qd_idx[(r.sec, r.titulo_a)].add(r.titulo_b)
        qd_idx[(r.sec, r.titulo_b)].add(r.titulo_a)
    gi = geo.set_index("sec")
    tit_sec = R_ok.groupby("sec").titulo.apply(set).to_dict()
    modelo_sec = modelo_sec or {}
    linhas = []
    for t, grp in g.groupby("titulo"):
        for a, b in itertools.combinations(grp.to_dict("records"), 2):
            la1, lo1, la2, lo2 = (gi.lat.get(a["sec"], np.nan), gi.lon.get(a["sec"], np.nan),
                                  gi.lat.get(b["sec"], np.nan), gi.lon.get(b["sec"], np.nan))
            dist = float(haversine(la1, lo1, la2, lo2)) if not np.isnan([la1, lo1, la2, lo2]).any() else np.nan
            mesmo_local = (a["mun"] == b["mun"] and a["zona"] == b["zona"]
                           and gi.local.get(a["sec"]) == gi.local.get(b["sec"]))
            if np.isnan(dist) and mesmo_local:
                dist = 0.0
            delta, ta, tb = min((abs(x - y), x, y) for x in a["ts_lista"] for y in b["ts_lista"])
            compart = len((tit_sec.get(a["sec"], set()) & tit_sec.get(b["sec"], set())) - {t})
            v_kmh = (dist / (delta / 3600.0)) if (not np.isnan(dist) and delta > 0) else (np.inf if delta == 0 and dist > 0 else 0.0)
            excl = ("mesma_urna(contingencia/replicacao)" if a["urnas"] & b["urnas"] else
                    "linha_identica(replicacao)" if a["hashes"] & b["hashes"] else "")
            qa, qb = qd_idx.get((a["sec"], t), set()), qd_idx.get((b["sec"], t), set())
            nc_a, nc_b = "nao_coincide" in a["biometria"], "nao_coincide" in b["biometria"]
            dono_a = a["eleitor"] == "1" and "coincide" in a["biometria"].split("|")
            dono_b = b["eleitor"] == "1" and "coincide" in b["biometria"].split("|")
            fd = faixa(dist, FAIXA_DIST)
            if excl:
                classe = "excluida_" + excl
            elif qa or qb:
                classe = "erro_digitacao_evidenciado_por_quase_duplicado"
            elif nc_a or nc_b:
                classe = "erro_digitacao_indicado_por_biometria_nao_coincidente"
            elif fd == "A_<1km":
                classe = "mesmo_predio_<1km"
            elif dono_a or dono_b:
                classe = "dono_conferido_por_biometria_em_uma_ponta"
            else:
                classe = "residuo_sem_explicacao_no_log"
            na, nb = nomes_mun.get((a["uf"], a["mun"]), ""), nomes_mun.get((b["uf"], b["mun"]), "")
            nominal = {(a["uf"], na), (b["uf"], nb)} == {(CASO_NOMINAL[0], CASO_NOMINAL[1]), (CASO_NOMINAL[2], CASO_NOMINAL[3])}
            linhas.append(dict(
                titulo=t, uf_a=a["uf"], mun_a=a["mun"], municipio_a=na, zona_a=a["zona"], secao_a=a["secao"],
                uf_b=b["uf"], mun_b=b["mun"], municipio_b=nb, zona_b=b["zona"], secao_b=b["secao"],
                ts_a=a["ts_txt"], ts_b=b["ts_txt"], delta_s=delta, faixa_intervalo=faixa(delta, FAIXA_INT),
                distancia_km=None if np.isnan(dist) else round(dist, 3), faixa_distancia=fd,
                mesmo_local_votacao=bool(mesmo_local), eleitor_secao_a=a["eleitor"], eleitor_secao_b=b["eleitor"],
                biometria_a=a["biometria"], biometria_b=b["biometria"],
                quase_dup_na_secao_a="|".join(sorted(qa)), quase_dup_na_secao_b="|".join(sorted(qb)),
                tipo_erro_a="|".join(sorted({tipo_erro(t, x) for x in qa})),
                tipo_erro_b="|".join(sorted({tipo_erro(t, x) for x in qb})),
                n_registros_a=a["n_reg"], n_registros_b=b["n_reg"],
                periodo=periodo(max(ta, tb)), local_a=gi.local.get(a["sec"]), local_b=gi.local.get(b["sec"]),
                modelo_urna_a=modelo_sec.get(a["sec"], ""), modelo_urna_b=modelo_sec.get(b["sec"], ""),
                outros_titulos_compartilhados=compart, velocidade_exigida_kmh=v_kmh,
                mesarios_secao_a=n_mes.get(a["sec"]), mesarios_secao_b=n_mes.get(b["sec"]),
                convocacao_individual="nao_verificavel(base_publica_agregada_por_zona)",
                caso_nominal_porto_seguro_casa_nova=nominal, exclusao=excl, classificacao=classe))
    return pd.DataFrame(linhas)


JANELA_REINICIO_S = 30 * 60   # congelado (emenda 05): reinicio ate 30 min antes, sem voto computado entre
JANELA_REDIGITACAO_S = 10 * 60  # congelado (emenda 05): mesmo titulo, mesma urna, sem voto entre, ate 10 min
JANELAS_REINICIO_SENS = (15 * 60, 60 * 60)  # sensibilidade (ressalva 1): a classe 2 nao pode se mover
# emenda 05: sem teto para a classe 4; ela nao entra na razao e e descrita como residuo


def classificar_bloqueios(B, R_ok, ctx=None, janela_reinicio=None):
    """Classes, em ordem de precedencia:
      1 bloqueio_pos_reinicio        reinicio (partida do logd posterior a primeira do dia) ate 30 min antes,
                                     sem voto computado entre o reinicio e o bloqueio
      2 erro_digitacao_para_outro_mesario_da_secao   ha na secao titulo registrado X != T tal que T resulta
                                     de X por um erro unico (classe usada na validacao cruzada, emenda 04)
      3 redigitacao_imediata         mesmo titulo registrado na mesma urna ate 10 min antes, sem voto entre
      4 redigitacao_ciclo_posterior  demais (mesmo titulo ja registrado, re-registro em outro ciclo)
    Sem o contexto do cache (ctx), as classes 1 e 3 nao sao avaliaveis e ficam marcadas como tal.
    Coluna classe_regra_temporal: aplica so o criterio temporal do prompt (pos_reinicio / redigitacao <=10 min /
    bloqueio_por_erro), para comparacao."""
    if not len(B):
        return pd.DataFrame()
    reg_sec = R_ok.groupby("sec").titulo.apply(set).to_dict()
    cidx = {}
    if ctx is not None and len(ctx):
        for r in ctx.to_dict("records"):
            cidx[(r["sec"], r["hash_linha"])] = r
    out = []
    for r in B.to_dict("records"):
        regs = reg_sec.get(r["sec"], set())
        origem = sorted(x for x in regs if x != r["titulo"] and tipo_erro_dir(x, r["titulo"]))
        r["titulo_registrado_na_secao"] = r["titulo"] in regs
        r["titulos_vizinhos_registrados"] = "|".join(origem)
        r["tipo_erro"] = "|".join(sorted({tipo_erro_dir(x, r["titulo"]) for x in origem}))
        c = cidx.get((r["sec"], r["hash_linha"]))
        num = lambda v: float(v) if v not in ("", None) and v == v else None
        if c is not None:
            sr, vr = num(c.get("seg_desde_reinicio")), num(c.get("votos_desde_reinicio"))
            sg, vg = num(c.get("seg_desde_registro")), num(c.get("votos_desde_registro"))
            jr = JANELA_REINICIO_S if janela_reinicio is None else janela_reinicio
            pos_rein = sr is not None and sr <= jr and (vr or 0) == 0
            vd = num(c.get("votos_no_dia_ate_bloqueio"))
            r["padrao_pre_primeiro_voto_15_60min"] = bool(vd == 0 and sg is not None and 900 <= sg <= 3600)
            redig = sg is not None and sg <= JANELA_REDIGITACAO_S and (vg or 0) == 0
            r.update(contexto_disponivel=True, seg_desde_reinicio=sr, votos_desde_reinicio=vr,
                     seg_desde_registro=sg, votos_desde_registro=vg)
        else:
            pos_rein = redig = None
            r.update(contexto_disponivel=False)
        if pos_rein:
            classe = "bloqueio_pos_reinicio"
        elif origem:
            classe = "erro_digitacao_para_outro_mesario_da_secao"
        elif redig:
            classe = "redigitacao_imediata"
        elif c is None:
            classe = "redigitacao_do_mesmo_titulo(sem_contexto)"
        else:
            classe = "redigitacao_ciclo_posterior"
        r["classificacao"] = classe
        r["classe_regra_temporal"] = ("bloqueio_pos_reinicio" if pos_rein else "redigitacao" if redig
                                      else "bloqueio_por_erro" if c is not None else "sem_contexto")
        out.append(r)
    return pd.DataFrame(out)


# ------------------------------------------------------------------ nulo (simulacao)
def preparar_simulacao(R_ok, geo, pesos, viz):
    ev = R_ok[["titulo", "sec", "t_s"]].to_numpy()
    secs_de = R_ok.groupby("titulo").apply(lambda d: sorted(set(zip(d.sec, d.t_s))), include_groups=False).to_dict()
    gi = geo.set_index("sec")
    lat, lon, uf_de = gi.lat.to_dict(), gi.lon.to_dict(), gi.uf.to_dict()
    loc_de = {k: f"{k.rsplit('-', 1)[0]}-{v}" for k, v in gi.local.to_dict().items()}
    nviz_cache = {}
    prob, alvos_l = [], []
    for t, s, ts in ev:
        if t not in viz:
            continue
        por_tipo = defaultdict(list)
        for b, tp in viz[t]:
            por_tipo[tp].append(b)
        for tp, alvos in por_tipo.items():
            if pesos.get(tp, 0) == 0:
                continue
            if (t, tp) not in nviz_cache:
                nviz_cache[(t, tp)] = len(vizinhos(t, tp))
            nv = nviz_cache[(t, tp)]
            if nv == 0:
                continue
            res = []
            for b in alvos:
                outros = [(s2, ts2) for s2, ts2 in secs_de[b] if s2 != s]
                mesma = any(s2 == s for s2, _ in secs_de[b])
                cols = []
                for s2, ts2 in outros:
                    d = float(haversine(lat.get(s, np.nan), lon.get(s, np.nan), lat.get(s2, np.nan), lon.get(s2, np.nan)))
                    cols.append((s, s2, faixa(d, FAIXA_DIST), faixa(abs(ts - ts2), FAIXA_INT), uf_de.get(s, s[:2]),
                                 periodo(max(ts, ts2)), loc_de.get(s, s), loc_de.get(s2, s2)))
                res.append((cols, mesma))
            prob.append(pesos[tp] * len(alvos) / nv)
            alvos_l.append(res)
    return np.array(prob), alvos_l, len(ev)


def simular(prep, E, reps, semente):
    prob, alvos_l, N = prep
    rng = np.random.default_rng(semente)
    nd = [f[0] for f in FAIXA_DIST] + ["ND"]
    ni = [f[0] for f in FAIXA_INT] + ["ND"]
    cont = np.zeros((reps, len(nd), len(ni)), dtype=np.int32)
    npr = [p[0] for p in PERIODOS]
    cont_per = np.zeros((reps, len(nd), len(npr)), dtype=np.int32)
    bloq = np.zeros(reps, dtype=np.int32)
    maxsec = np.zeros(reps, dtype=np.int32)
    maxloc = np.zeros(reps, dtype=np.int32)
    uf_cont = defaultdict(lambda: np.zeros(reps, dtype=np.int32))
    p = prob / N
    p_tot = float(p.sum())
    if p_tot > 0 and E > 0:
        pc = p / p_tot
        for r in range(reps):
            k = rng.binomial(int(E), min(1.0, p_tot))
            if k == 0:
                continue
            secs, locs = Counter(), Counter()
            for j in rng.choice(len(pc), size=k, p=pc):
                cols, mesma = alvos_l[j][rng.integers(len(alvos_l[j]))]
                if mesma:
                    bloq[r] += 1
                    continue
                for s, s2, fd, fi, uf, pr, l1, l2 in cols:
                    cont[r, nd.index(fd), ni.index(fi)] += 1
                    cont_per[r, nd.index(fd), npr.index(pr)] += 1
                    secs[s] += 1
                    secs[s2] += 1
                    locs[l1] += 1
                    if l2 != l1:
                        locs[l2] += 1
                    uf_cont[uf][r] += 1
            maxsec[r] = max(secs.values()) if secs else 0
            maxloc[r] = max(locs.values()) if locs else 0
    return dict(lambda_total=float(E * p_tot), cont=cont, cont_per=cont_per, bloq=bloq, maxsec=maxsec,
                maxloc=maxloc, nd=nd, ni=ni, npr=npr, uf_cont=dict(uf_cont))


def via3(R_ok, E, pesos, semente, T_set):
    rng = np.random.default_rng(semente + 3)
    ev = R_ok[["titulo", "sec"]].to_numpy()
    tipos = [k for k in TIPOS if pesos.get(k, 0) > 0]
    w = np.array([pesos[k] for k in tipos])
    w = w / w.sum()
    reps = int(max(50, min(2000, 3_000_000 // max(1, int(E)))))
    tot = 0
    for _ in range(reps):
        alvo = defaultdict(set)
        for i, k in zip(rng.integers(len(ev), size=int(E)), rng.choice(len(tipos), size=int(E), p=w)):
            t, s = ev[i]
            nb = vizinhos(t, tipos[k])
            x = nb[rng.integers(len(nb))] if nb else None
            if x and titulo_valido(x) and x not in T_set:
                alvo[x].add(s)
        tot += sum(math.comb(len(v), 2) for v in alvo.values() if len(v) >= 2)
    return tot / reps, reps


# ------------------------------------------------------------------ principal
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ano", type=int)
    ap.add_argument("--turno", type=int, default=2)
    ap.add_argument("--reps", type=int, default=10000)
    ap.add_argument("--semente", type=int, default=20261025)
    ap.add_argument("--entrada", default=os.path.join(ROOT, "data", "censo"))
    ap.add_argument("--geo", default=None)
    ap.add_argument("--catalogo", default=os.path.join(ROOT, "data", "raw", "catalogo"))
    ap.add_argument("--saida", default=None)
    ap.add_argument("--loo", dest="loo", action="store_true", default=True,
                    help="leave-one-out: D e p1 sem os titulos em colisao (padrao)")
    ap.add_argument("--sem-loo", dest="loo", action="store_false")
    ap.add_argument("--ignorar-trava", action="store_true",
                    help="apenas para testes sinteticos: permite escrever colisoes sem o commit de parametros")
    ap.add_argument("--somente-parametros", action="store_true",
                    help="calcula p1, D e o nulo e para, sem abrir colisoes observadas (congelamento)")
    a = ap.parse_args()
    saida = a.saida or os.path.join(ROOT, "data", "outputs", f"{a.ano}_t{a.turno}")
    os.makedirs(saida, exist_ok=True)
    R, L, B = carregar(a.ano, a.turno, a.entrada)
    R_ok, B, den = preparar(R, L, B, a.ano, a.turno)
    den["nota_N"] = ("N = registros de presenca em secoes principais com log lido (agregadas sem arquivo proprio "
                     "nao tem urna; ver reconciliacao em registro/reconciliacao_N_2t2026.md)")
    geo = pd.read_csv(a.geo or os.path.join(ROOT, "data", "processed", f"geo_{a.ano}.csv"),
                      dtype={"uf": str, "mun": str, "zona": str, "secao": str, "local": str})
    geo["sec"] = geo[SEC].agg("-".join, axis=1)
    nomes_mun, corte = {}, []
    for f in glob.glob(os.path.join(a.catalogo, "*-p3221-cs.json")) if a.ano == 2026 else []:
        d = json.load(open(f, encoding="utf-8"))
        corte.append(f"{d['dg']} {d['hg']}")
        for m in d["abr"][0]["mu"]:
            nomes_mun[(d["abr"][0]["cd"], m["cd"])] = m["nm"]
    den["data_corte_catalogo"] = max(corte, key=lambda x: (x[6:10], x[3:5], x[:2], x[11:])) if corte else None
    N = den["registros_N"]

    # ---- p1 por caminho (rastro: quase-duplicados) e p2
    qd, d = quase_duplicados(R_ok)
    qd.to_csv(os.path.join(saida, "quase_duplicados.csv"), index=False)
    R_d, qd_p1, loo = aplicar_loo(R_ok, qd, a.loo)
    p2k = p2_por_tipo(R_d.titulo.unique())
    m = medir_p1(R_ok, qd_p1, d, p2k, N)
    pesos, p1 = m["pesos"], m["p1"]
    pd.DataFrame([dict(tipo=k, caminho=CAMINHO[k], quase_duplicados=m["obs_por_tipo"].get(k, 0), p2=p2k[k],
                       erros_estimados=m["E_por_tipo"][k], p1=m["p1_por_tipo"][k], peso=pesos[k]) for k in TIPOS]
                 ).to_csv(os.path.join(saida, "p1_por_caminho.csv"), index=False)
    R_ok["uf_sec"] = R_ok.uf
    qd["uf"] = qd.sec.str[:2]
    taxa_uf = (qd.groupby("uf").size() / R_ok.groupby("uf").size()).fillna(0)
    por_sec = qd.groupby("sec").size().reindex(R_ok.sec.unique(), fill_value=0)
    # ---- densidade local D (vizinhos registrados como mesarios do turno)
    viz = vizinhos_registrados(R_d)
    Ddf = medir_D(R_d, pesos, viz)
    w_ev = R_d.groupby(["titulo", "sec"]).size().rename("n").reset_index()
    Ddf = Ddf.merge(w_ev, on=["titulo", "sec"])
    D = float((Ddf.D_outra_secao * Ddf.n).sum() / Ddf.n.sum()) if len(Ddf) else 0.0
    Dm = float((Ddf.D_mesma_secao * Ddf.n).sum() / Ddf.n.sum()) if len(Ddf) else 0.0
    agg = lambda g: pd.Series(dict(registros=g.n.sum(), D=(g.D_outra_secao * g.n).sum() / g.n.sum(),
                                   D_mesma_secao=(g.D_mesma_secao * g.n).sum() / g.n.sum()))
    D_uf = Ddf.groupby("uf").apply(agg, include_groups=False).reset_index()
    D_uf["esperado_N_p1_D"] = D_uf.registros * p1 * D_uf.D
    D_uf.to_csv(os.path.join(saida, "D_por_uf.csv"), index=False)
    Ddf.groupby(["uf", "zona"]).apply(agg, include_groups=False).reset_index().to_csv(
        os.path.join(saida, "D_por_zona.csv"), index=False)
    qd = qd.drop(columns=["uf"])
    via1 = N * p1 * D

    # ---- horarios do registro de presenca (histograma de 15 min; primeiro registro da mesa x posteriores)
    R_h = R_ok.sort_values("t_s").copy()
    R_h["ordem_na_mesa"] = R_h.groupby("sec").cumcount() + 1
    R_h["bin15"] = pd.to_datetime(R_h.t_s, unit="s").dt.floor("15min").dt.strftime("%H:%M")
    hst = R_h.assign(tipo=np.where(R_h.ordem_na_mesa == 1, "primeiro_registro_da_mesa", "registros_posteriores")
                     ).groupby(["bin15", "tipo"]).size().unstack(fill_value=0).reset_index()
    hst.to_csv(os.path.join(saida, "horarios_registro.csv"), index=False)
    hora = (R_h.t_s // 3600) % 24
    hist = dict(fracao_apos_9h=float((hora >= 9).mean()), fracao_apos_17h=float((hora >= 17).mean()),
                limiar=LIMIAR_POS9H, estratificar_por_periodo=bool((hora >= 9).mean() > LIMIAR_POS9H))

    # ---- nulo: simulacao e sensibilidade
    prep = preparar_simulacao(R_d, geo, pesos, viz)
    E = N * p1
    cen = {"central": E, "p1_x0.5_ou_D_x0.5": 0.5 * E, "D_x1.5": 1.5 * E, "p1_x2": 2 * E,
           "p1_pelas_tentativas_invalidas": den["tentativas_invalidas"] / (1 - m["p2_ponderado"])}
    sims = {k: simular(prep, round(v), a.reps if k == "central" else max(2000, a.reps // 5), a.semente)
            for k, v in cen.items()}
    v3, v3r = via3(R_ok, round(E), pesos, a.semente, set(R_ok.titulo))
    S = sims["central"]
    nulo = dict(**den, **loo, p1=p1, p1_por_tipo=m["p1_por_tipo"], pesos_caminho=pesos, p2_por_tipo=p2k,
                p2_ponderado=m["p2_ponderado"], quase_duplicados=len(qd), visibilidade_d=d, D=D, D_mesma_secao=Dm,
                via1_esperado_N_p1_D=via1, via3_segunda_ordem=v3,
                via2={k: dict(media_colisoes=float(v["cont"].sum(axis=(1, 2)).mean()),
                              IC95_colisoes=np.quantile(v["cont"].sum(axis=(1, 2)), [0.025, 0.975]).tolist(),
                              media_bloqueios=float(v["bloq"].mean())) for k, v in sims.items()},
                via2_por_faixa_distancia={nd: dict(media=float(S["cont"][:, i, :].sum(axis=1).mean()),
                                                   IC95=np.quantile(S["cont"][:, i, :].sum(axis=1), [0.025, 0.975]).tolist())
                                          for i, nd in enumerate(S["nd"])},
                via2_por_uf={u: float(v.mean()) for u, v in S["uf_cont"].items()},
                via2_por_faixa_e_periodo={f"{nd}|{pn}": float(S["cont_per"][:, i, j].mean())
                                          for i, nd in enumerate(S["nd"]) for j, pn in enumerate(S["npr"])},
                horarios=hist,
                exclusoes_loo="titulos em colisao e titulos de quase-duplicados de p1 fora de D; pares com titulo em colisao fora de p1")
    json.dump(nulo, open(os.path.join(saida, "parametros_nulo.json"), "w"), indent=2, default=float, ensure_ascii=False)
    if a.somente_parametros:
        print(json.dumps(nulo, indent=2, default=float, ensure_ascii=False))
        return

    # ---- observado (so depois do commit dos parametros; ver emenda 05, secao de congelamento)
    marca = os.path.join(ROOT, "registro", f"parametros_{a.turno}t{a.ano}.sha256")
    if not a.ignorar_trava and not os.path.exists(marca):
        raise SystemExit(f"trava: {marca} ausente; commite os parametros antes de escrever colisoes")
    modelo_sec = L.assign(sec=L[SEC].agg("-".join, axis=1)).dropna(subset=["modelo"]).groupby("sec").modelo.agg(
        lambda x: "|".join(sorted(set(x)))).to_dict() if "modelo" in L.columns else {}
    # indicio de digitacao no teste de caso: so o erro aceito (emenda 07)
    col = colisoes_observadas(R_ok, geo, qd[qd.erro_aceito] if len(qd) else qd, nomes_mun, modelo_sec)
    col.to_csv(os.path.join(saida, "colisoes.csv"), index=False)
    p_ctx = os.path.join(a.entrada, f"bloqueios_contexto_{a.ano}_t{a.turno}.csv")
    ctx = pd.read_csv(p_ctx, dtype=str) if os.path.exists(p_ctx) else None
    if ctx is not None:
        ctx = zfill(ctx)
        ctx["sec"] = ctx[SEC].agg("-".join, axis=1)
    blq = classificar_bloqueios(B, R_ok, ctx)
    c2 = "erro_digitacao_para_outro_mesario_da_secao"
    sens_janela = {}
    if len(blq):
        for jr in JANELAS_REINICIO_SENS:
            bj = classificar_bloqueios(B, R_ok, ctx, janela_reinicio=jr)
            blq[f"classificacao_janela_{jr // 60}min"] = bj.classificacao.values
        sens_janela = {f"{jr // 60}min": int((blq[f"classificacao_janela_{jr // 60}min"] == c2).sum())
                       for jr in JANELAS_REINICIO_SENS}
        sens_janela["30min"] = int((blq.classificacao == c2).sum())
        sens_janela["classe2_estavel"] = len(set(v for k, v in sens_janela.items() if k.endswith("min"))) == 1
    blq.to_csv(os.path.join(saida, "bloqueios.csv"), index=False)
    obs = col[col.exclusao == ""] if len(col) else pd.DataFrame(columns=[
        "faixa_distancia", "faixa_intervalo", "periodo", "uf_a", "mun_a", "zona_a", "secao_a", "uf_b", "mun_b",
        "zona_b", "secao_b", "local_a", "local_b"])
    n_blq_erro = int((blq.classificacao == c2).sum()) if len(blq) else 0
    desc_blq = {}
    if len(blq):
        desc_blq = dict(por_classe=blq.classificacao.value_counts().to_dict(),
                        por_regra_temporal=blq.classe_regra_temporal.value_counts().to_dict(),
                        classe4_por_momento=blq[blq.classificacao == "redigitacao_ciclo_posterior"].momento.value_counts().to_dict(),
                        padrao_pre_primeiro_voto_15_60min=int(blq.get("padrao_pre_primeiro_voto_15_60min",
                                                                      pd.Series(dtype=bool)).fillna(False).astype(bool).sum()))

    def linha(nome, s_arr, o):
        e = float(s_arr.mean())
        lo, hi = garwood(o)
        q = np.quantile(s_arr, [0.025, 0.975])
        return dict(unidade=nome, observado=o, esperado=e, nulo_IC95_inf=float(q[0]), nulo_IC95_sup=float(q[1]),
                    p_sim_maior_igual=float((s_arr >= o).mean()), razao=o / e if e > 0 else None,
                    razao_IC95_inf=lo / e if e > 0 else None, razao_IC95_sup=hi / e if e > 0 else None,
                    razao_sobre_limite_superior=(o / float(q[1])) if q[1] > 0 else (float("inf") if o > 0 else 0.0))

    linhas = []
    for di, dn in enumerate(S["nd"]):
        for ii, inn in enumerate(S["ni"] + ["TOTAL"]):
            if inn == "TOTAL":
                arr = {k: v["cont"][:, di, :].sum(axis=1) for k, v in sims.items()}
                o = int((obs.faixa_distancia == dn).sum())
            else:
                arr = {k: v["cont"][:, di, ii] for k, v in sims.items()}
                o = int(((obs.faixa_distancia == dn) & (obs.faixa_intervalo == inn)).sum())
            r = linha(f"{dn}|{inn}", arr["central"], o)
            r.update(faixa_distancia=dn, faixa_intervalo=inn)
            for k in cen:
                if k != "central":
                    r[f"nulo_IC95_sup_{k}"] = float(np.quantile(arr[k], 0.975))
                    r[f"esperado_{k}"] = float(arr[k].mean())
            linhas.append(r)
    tab = pd.DataFrame(linhas)
    tab.to_csv(os.path.join(saida, "tabela_faixas.csv"), index=False)
    tot_sim = S["cont"].sum(axis=(1, 2))
    linha_total = linha("TOTAL(todas_as_faixas,descritivo)", tot_sim, int(len(obs)))
    tab_per = None
    if hist["estratificar_por_periodo"]:
        lp = []
        for di, dn in enumerate(S["nd"]):
            for pi, pn in enumerate(S["npr"]):
                o = int(((obs.faixa_distancia == dn) & (obs.periodo == pn)).sum()) if len(obs) else 0
                r = linha(f"{dn}|{pn}", S["cont_per"][:, di, pi], o)
                r.update(faixa_distancia=dn, periodo=pn)
                lp.append(r)
        tab_per = pd.DataFrame(lp)
        tab_per.to_csv(os.path.join(saida, "tabela_faixas_por_periodo.csv"), index=False)

    # ---- UF e estratos por eleitorado (teste individual so onde a expectativa central passa de 3)
    eleit_uf = geo.groupby("uf").qt_eleitor.sum().to_dict()
    uf_obs = Counter(obs.uf_a) if len(obs) else Counter()
    uf_rows = []
    for uf in sorted(set(eleit_uf) | set(S["uf_cont"])):
        arr = S["uf_cont"].get(uf, np.zeros(a.reps, dtype=np.int32))
        r = linha(uf, arr, int(uf_obs.get(uf, 0)))
        r["testado_individualmente"] = r["esperado"] > LIMIAR_TESTE_UF
        r["eleitorado"] = eleit_uf.get(uf, 0)
        r["estrato"] = next(n for n, lo, hi in ESTRATOS if lo <= eleit_uf.get(uf, 0) < hi)
        r["D_uf"] = float(D_uf.set_index("uf").D.get(uf, np.nan)) if len(D_uf) else None
        uf_rows.append(r)
    for n, lo, hi in ESTRATOS:
        ufs = [u for u in eleit_uf if lo <= eleit_uf[u] < hi and not any(
            x["unidade"] == u and x["testado_individualmente"] for x in uf_rows)]
        arr = sum((S["uf_cont"].get(u, np.zeros(a.reps, dtype=np.int32)) for u in ufs), np.zeros(a.reps, dtype=np.int32))
        r = linha(n, arr, int(sum(uf_obs.get(u, 0) for u in ufs)))
        r["testado_individualmente"] = r["esperado"] > LIMIAR_TESTE_UF
        r["estrato"] = n
        r["ufs"] = "|".join(sorted(ufs))
        uf_rows.append(r)
    tab_uf = pd.DataFrame(uf_rows)
    tab_uf.to_csv(os.path.join(saida, "tabela_uf.csv"), index=False)
    ufs_ind = tab_uf[~tab_uf.unidade.str.contains("_")]
    from scipy.stats import spearmanr
    taxa_obs_uf = ufs_ind.observado / ufs_ind.unidade.map(R_ok.groupby("uf").size()).clip(lower=1)
    rho = spearmanr(ufs_ind.D_uf, taxa_obs_uf, nan_policy="omit") if len(obs) else None
    previsao_densidade = dict(spearman_D_uf_vs_colisoes_por_registro=(float(rho.statistic) if rho is not None else None),
                              p=(float(rho.pvalue) if rho is not None else None))

    # ---- dispersao e concentracao (secao, local de votacao, UF)
    conc = {}
    if len(obs):
        sa = obs.uf_a + "-" + obs.mun_a + "-" + obs.zona_a + "-" + obs.secao_a
        sb = obs.uf_b + "-" + obs.mun_b + "-" + obs.zona_b + "-" + obs.secao_b
        cs = Counter(list(sa) + list(sb))
        la = obs.uf_a + "-" + obs.mun_a + "-" + obs.zona_a + "-" + obs.local_a.astype(str)
        lb = obs.uf_b + "-" + obs.mun_b + "-" + obs.zona_b + "-" + obs.local_b.astype(str)
        cl = Counter(list(la) + [y for x, y in zip(la, lb) if x != y])
        n_locais = geo.assign(k=geo.uf + "-" + geo.mun + "-" + geo.zona + "-" + geo.local.astype(str)).k.nunique()
        x = np.array(list(cs.values()) + [0] * (den["secoes_com_log"] - len(cs)))
        conc = dict(secoes_envolvidas=len(cs), fracao_secoes_envolvidas=len(cs) / den["secoes_com_log"],
                    max_por_secao=int(max(cs.values())),
                    p_sim_max_por_secao=float((S["maxsec"] >= max(cs.values())).mean()),
                    indice_dispersao_por_secao=float(x.var(ddof=1) / x.mean()),
                    locais_envolvidos=len(cl), fracao_locais_envolvidos=len(cl) / n_locais,
                    max_por_local=int(max(cl.values())),
                    p_sim_max_por_local=float((S["maxloc"] >= max(cl.values())).mean()))
        ufs_all = sorted(set(uf_obs) | set(S["uf_cont"]))
        e_all = np.array([S["uf_cont"].get(u, np.zeros(1)).mean() for u in ufs_all])
        o_all = np.array([uf_obs.get(u, 0) for u in ufs_all])
        if e_all.sum() > 0:
            e_n = e_all / e_all.sum() * o_all.sum()
            mm = e_n > 0
            conc["chi2_uf"] = float((((o_all[mm] - e_n[mm]) ** 2) / e_n[mm]).sum())
            conc["gl_uf"] = int(mm.sum() - 1)
            conc["p_chi2_uf"] = float(chi2.sf(conc["chi2_uf"], max(1, conc["gl_uf"])))
            conc["casos_em_uf_sem_suporte_no_nulo"] = int(o_all[~mm].sum())
    achado_conc = bool(conc) and (
        (conc["fracao_secoes_envolvidas"] < 0.05 and conc["p_sim_max_por_secao"] < 0.05) or
        (conc["fracao_locais_envolvidos"] < 0.05 and conc["p_sim_max_por_local"] < 0.05) or
        conc.get("p_chi2_uf", 1) < 0.05)

    # ---- validacao cruzada: so a classe 2 (emenda 05; sem teto para a classe 4)
    q_b = {k: np.quantile(v["bloq"], [0.025, 0.975]).tolist() for k, v in sims.items()}
    lo_b = min(q_b[k][0] for k in ("p1_x0.5_ou_D_x0.5", "central", "D_x1.5", "p1_x2"))
    hi_b = max(q_b[k][1] for k in ("p1_x0.5_ou_D_x0.5", "central", "D_x1.5", "p1_x2"))
    dentro = bool(lo_b <= n_blq_erro <= hi_b)
    valid = dict(numerador="somente classe 2 (erro_digitacao_para_outro_mesario_da_secao)",
                 classe2_observada=n_blq_erro, classe2_esperada=float(S["bloq"].mean()),
                 classe2_IC95_por_cenario=q_b, faixa_aceitacao=[lo_b, hi_b], classe2_dentro_do_previsto=dentro,
                 sensibilidade_janela_reinicio=sens_janela, descricao_bloqueios=desc_blq,
                 razao_classe2_por_colisao_prevista=float(S["bloq"].mean() / max(1e-12, tot_sim.mean())),
                 razao_classe2_por_colisao_observada=(n_blq_erro / len(obs)) if len(obs) else None)

    # ---- vereditos (emenda 05): mecanismo (condicionado a validacao) e magnitude (sempre)
    vered = {}
    for fd in ("A_<1km", "B_1-50km", "C_>50km", "ND"):
        r = tab[(tab.faixa_distancia == fd) & (tab.faixa_intervalo == "TOTAL")].iloc[0].to_dict()
        excesso = r["observado"] > r["nulo_IC95_sup"]
        if not dentro:
            mec = "modelo_de_digitacao_rejeitado(classe2_fora_do_previsto)"
        elif excesso:
            mec = "mecanismo_existe_mas_nao_chega:excesso_de_volume"
        else:
            mec = "acidente_explica_o_volume"
        frag = any((r["observado"] > r[f"nulo_IC95_sup_{k}"]) != excesso for k in ("p1_x0.5_ou_D_x0.5", "D_x1.5", "p1_x2"))
        mag = r["razao_sobre_limite_superior"]
        vered[fd] = dict(
            veredito_mecanismo=mec, fragil_na_sensibilidade=frag, observado=r["observado"], esperado=r["esperado"],
            nulo_IC95=[r["nulo_IC95_inf"], r["nulo_IC95_sup"]], razao_O_E=r["razao"],
            razao_IC95=[r["razao_IC95_inf"], r["razao_IC95_sup"]],
            veredito_magnitude=(f"o observado excede o maximo explicavel por este mecanismo em {mag:.2f} vezes"
                                if excesso else f"o observado corresponde a {mag:.2f} do maximo explicavel por este mecanismo"),
            magnitude_e_piso=not dentro,
            observacao=("faixa A: veredito proprio; casos nao explicados caso a caso em teste_caso.py" if fd == "A_<1km"
                        else "faixa sem coordenada, descritiva" if fd == "ND" else ""))
    for r in tab_uf[tab_uf.testado_individualmente].to_dict("records"):
        vered[f"unidade:{r['unidade']}"] = dict(observado=r["observado"], esperado=r["esperado"],
                                                 nulo_IC95=[r["nulo_IC95_inf"], r["nulo_IC95_sup"]],
                                                 excesso=r["observado"] > r["nulo_IC95_sup"])
    vered["concentracao"] = dict(achado_de_concentracao=achado_conc,
                                 nota="nao e absorvido pelo veredito de volume")
    excesso_agregado = any(vered[f]["veredito_mecanismo"].startswith("mecanismo_existe") for f in ("B_1-50km", "C_>50km"))
    vered["familia_1_nulo_mal_especificado"] = ("eliminada" if dentro and excesso_agregado else "compativel")

    par = dict(**den, **loo, p1=p1, p1_IC95_quase_dup=([garwood(len(qd_p1))[0] / d / m["p2_ponderado"] / N,
                                                 garwood(len(qd_p1))[1] / d / m["p2_ponderado"] / N]
                                                if m["p2_ponderado"] > 0 and len(qd_p1) else None),
               p1_por_tipo=m["p1_por_tipo"], pesos_caminho=pesos, p2_por_tipo=p2k, p2_ponderado=m["p2_ponderado"],
               quase_duplicados=len(qd), quase_duplicados_usados_em_p1=len(qd_p1),
               quase_dup_por_tipo=m["obs_por_tipo"], visibilidade_d=d,
               quase_dup_por_mil_registros_por_uf=(taxa_uf * 1000).round(3).to_dict(),
               quase_dup_indice_dispersao_por_secao=float(por_sec.var() / por_sec.mean()) if por_sec.mean() > 0 else None,
               D=D, D_mesma_secao=Dm, via1_esperado_N_p1_D=via1,
               via2={k: dict(lambda_total=v["lambda_total"], media_colisoes=float(v["cont"].sum(axis=(1, 2)).mean()),
                             media_bloqueios=float(v["bloq"].mean())) for k, v in sims.items()},
               via1_via2_divergencia=abs(via1 - tot_sim.mean()) / max(1e-12, tot_sim.mean()),
               via3_segunda_ordem=v3, via3_reps=v3r, total_descritivo=linha_total,
               validacao_bloqueio=valid, concentracao=conc, horarios=hist, previsao_densidade=previsao_densidade,
               classificacao_colisoes=col.classificacao.value_counts().to_dict() if len(col) else {},
               classificacao_bloqueios=blq.classificacao.value_counts().to_dict() if len(blq) else {},
               caso_nominal=(col[col.caso_nominal_porto_seguro_casa_nova].drop(columns=["titulo"]).to_dict("records")
                             if len(col) else []),
               veredito=vered)
    json.dump(par, open(os.path.join(saida, "parametros.json"), "w"), indent=2, default=float, ensure_ascii=False)
    print(json.dumps({k: par[k] for k in ("escopo", "registros_N", "p1", "D", "via1_esperado_N_p1_D", "veredito",
                                          "validacao_bloqueio")}, indent=2, default=float, ensure_ascii=False))
    print("proximo passo: python src/cache_brutos.py", a.ano, a.turno, "colisoes ; python src/teste_caso.py", a.ano)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
densidade.py -- modelo de erro de digitacao do titulo (12 digitos) e medicao, nos registros do 2o turno,
de (a) p1 por caminho de erro e (b) densidade local D de titulos de mesario entre os vizinhos do original.

Caminhos de erro (um evento por digitacao errada):
  sub_uf     substituicao de um digito do prefixo de UF (posicoes 9-10)
  sub_corpo  substituicao de um digito do corpo sequencial (posicoes 1-8)
  sub_dv     substituicao de um digito verificador (posicoes 11-12)
  trans      transposicao de digitos adjacentes
  omissao    omissao de um digito, completada por um digito extra no fim, ou por zero a esquerda
  outros     transposicao com salto (abc -> cba) e erro gemeo (aa -> bb)

Leave-one-out (LOO, ligado por padrao): D e p1 sao medidos SEM os titulos envolvidos em colisoes (titulo
registrado em 2 ou mais secoes do turno). Sem isso, cada colisao real entraria no conjunto-alvo e no rastro
de erro, inflando D e p1 justamente onde ocorre e abafando um eventual excesso.

Uso como modulo (simulacao.py) ou:
  python densidade.py ANO [--turno 2] [--loo | --sem-loo]   -> data/outputs/<ano>_t<turno>/densidade_parametros.json
"""
import itertools
import os
import sys
from collections import Counter, defaultdict

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parsing import titulo_valido  # noqa: E402

TIPOS = ["sub_uf", "sub_corpo", "sub_dv", "trans", "omissao", "salto", "gemeo"]
CAMINHO = {"sub_uf": "sub_uf", "sub_corpo": "sub_corpo", "sub_dv": "sub_dv", "trans": "trans",
           "omissao": "omissao", "salto": "outros", "gemeo": "outros"}


def tipo_erro_dir(a, b):
    """Tipo do erro unico que transforma o titulo pretendido a no titulo digitado b, ou None."""
    if a == b or len(a) != 12 or len(b) != 12:
        return None
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
        if j == i + 2 and a[i] == b[j] and a[j] == b[i]:
            return "salto"
    for i in range(11):
        if a[:i] + a[i + 1:] == b[:11]:
            return "omissao"
    if b[0] == "0":
        for i in range(12):
            if a[:i] + a[i + 1:] == b[1:]:
                return "omissao"
    return None


def tipo_erro(a, b):
    """Versao simetrica (para pares nao ordenados)."""
    return tipo_erro_dir(a, b) or tipo_erro_dir(b, a)


def vizinhos(t, tp):
    out = []
    if tp.startswith("sub"):
        rng = {"sub_corpo": range(0, 8), "sub_uf": range(8, 10), "sub_dv": range(10, 12)}[tp]
        for i in rng:
            out += [t[:i] + c + t[i + 1:] for c in "0123456789" if c != t[i]]
    elif tp == "trans":
        out = [t[:i] + t[i + 1] + t[i] + t[i + 2:] for i in range(11) if t[i] != t[i + 1]]
    elif tp == "salto":
        out = [t[:i] + t[i + 2] + t[i + 1] + t[i] + t[i + 3:] for i in range(10) if t[i] != t[i + 2]]
    elif tp == "gemeo":
        for i in range(11):
            if t[i] == t[i + 1]:
                out += [t[:i] + c + c + t[i + 2:] for c in "0123456789" if c != t[i]]
    elif tp == "omissao":
        for i in range(11):
            out += [t[:i] + t[i + 1:] + c for c in "0123456789"]
        out += ["0" + t[:i] + t[i + 1:] for i in range(12)]
        out = [x for x in out if x != t]
    return out


def p2_por_tipo(titulos, n_max=20000, semente=20261025):
    rng = np.random.default_rng(semente)
    tt = list(titulos)
    if len(tt) > n_max:
        tt = list(rng.choice(tt, n_max, replace=False))
    out = {}
    for tp in TIPOS:
        v = n = 0
        for t in tt:
            nb = vizinhos(t, tp)
            n += len(nb)
            v += sum(titulo_valido(x) for x in nb)
        out[tp] = v / n if n else 0.0
    return out


def _pares_por_chave(s, chaves_a, chaves_b=None):
    pares = set()
    if chaves_b is None:
        g = pd.DataFrame({"k": chaves_a.values, "t": s.values}).dropna()
        dup = g[g.k.duplicated(keep=False)]
        for _, grp in dup.groupby("k").t:
            for a, b in itertools.combinations(sorted(set(grp)), 2):
                pares.add((a, b))
    else:
        ga = pd.DataFrame({"k": chaves_a.values, "a": s.values}).dropna()
        gb = pd.DataFrame({"k": chaves_b.values, "b": s.values}).dropna()
        m = ga.merge(gb, on="k")
        for a, b in zip(m.a, m.b):
            if a != b:
                pares.add(tuple(sorted((a, b))))
    return pares


def pares_um_erro(titulos):
    """Todos os pares nao ordenados de titulos do conjunto que distam um unico erro (qualquer tipo)."""
    s = pd.Series(sorted(set(titulos)))
    cand = set()
    for i in range(12):
        cand |= _pares_por_chave(s, s.str[:i] + "_" + s.str[i + 1:])
    for i in range(11):
        par = s.str[i:i + 2]
        cand |= _pares_por_chave(s, s.str[:i] + "_" + par.map(lambda x: "".join(sorted(x))) + "_" + s.str[i + 2:])
        gem = (par.str[0] == par.str[1])
        cand |= _pares_por_chave(s, (s.str[:i] + "_g_" + s.str[i + 2:]).where(gem, None))
    for i in range(10):
        ext = (s.str[i] + s.str[i + 2]).map(lambda x: "".join(sorted(x)))
        cand |= _pares_por_chave(s, s.str[:i] + "_" + ext + s.str[i + 1] + "_" + s.str[i + 3:])
    for i in range(12):  # omissao: a sem o digito i == b sem o ultimo digito, ou b sem o zero inicial
        dele = s.str[:i] + s.str[i + 1:]
        if i < 11:
            cand |= _pares_por_chave(s, dele, s.str[:11])
        cand |= _pares_por_chave(s, dele, s.str[1:].where(s.str[0] == "0", None))
    return {(a, b) for a, b in cand if tipo_erro(a, b)}


# ------------------------------------------------------------------ medicoes no 2o turno
def titulos_em_colisao(R_ok):
    """Titulos registrados em duas ou mais secoes do turno (conjunto excluido pelo LOO)."""
    n = R_ok.groupby("titulo").sec.nunique()
    return set(n[n >= 2].index)


def aplicar_loo(R_ok, qd, loo=True):
    """Devolve (R_para_D, qd_para_p1, resumo). R_para_D exclui todos os registros de titulos em colisao;
    qd_para_p1 exclui pares de quase-duplicados em que algum dos dois titulos esteja em colisao."""
    if not loo:
        return R_ok, qd, dict(loo=False, titulos_excluidos=0, registros_excluidos=0, pares_quase_dup_excluidos=0)
    ex = titulos_em_colisao(R_ok)
    R_d = R_ok[~R_ok.titulo.isin(ex)]
    m = qd.titulo_a.isin(ex) | qd.titulo_b.isin(ex) if len(qd) else pd.Series([], dtype=bool)
    return R_d, qd[~m] if len(qd) else qd, dict(loo=True, titulos_excluidos=len(ex),
                                                 registros_excluidos=int(len(R_ok) - len(R_d)),
                                                 pares_quase_dup_excluidos=int(m.sum()) if len(qd) else 0)


def quase_duplicados(R_ok):
    """Pares de titulos distintos registrados na MESMA secao a um unico erro (rastro do erro aceito)."""
    occ = R_ok.groupby(["sec", "titulo"]).size().rename("n").reset_index()
    linhas = []
    for sec, ts in occ.groupby("sec").titulo:
        if len(ts) < 2:
            continue
        for a, b in itertools.combinations(sorted(ts), 2):
            tp = tipo_erro(a, b)
            if tp:
                linhas.append(dict(sec=sec, titulo_a=a, titulo_b=b, tipo=tp, caminho=CAMINHO[tp]))
    qd = pd.DataFrame(linhas, columns=["sec", "titulo_a", "titulo_b", "tipo", "caminho"])
    env = set(zip(qd.sec, qd.titulo_a)) | set(zip(qd.sec, qd.titulo_b))
    limpo = occ[[(s, t) not in env for s, t in zip(occ.sec, occ.titulo)]]
    d = float((limpo.n >= 2).mean()) if len(limpo) else float("nan")
    return qd, d


def medir_p1(R_ok, qd, d, p2k, N):
    """p1 por caminho: E_k = quase-duplicados_k / d / p2_k ; p1_k = E_k / N. Caminho com p2 = 0 nao e
    mensuravel pelo rastro e nao gera numero valido (irrelevante para colisao)."""
    obs = qd.tipo.value_counts().to_dict()
    E_k = {k: (obs.get(k, 0) / d / p2k[k]) if p2k[k] > 0 else float("nan") for k in TIPOS}
    E = sum(v for v in E_k.values() if v == v)
    w = {k: (E_k[k] / E if E_k[k] == E_k[k] and E > 0 else 0.0) for k in TIPOS}
    if E == 0:  # sem rastro: pesos a priori (Verhoeff, 1969) apenas para nao zerar a simulacao
        w = {"sub_uf": 0.13, "sub_corpo": 0.53, "sub_dv": 0.13, "trans": 0.10, "omissao": 0.09, "salto": 0.01,
             "gemeo": 0.01}
    return dict(obs_por_tipo=obs, E_por_tipo=E_k, pesos=w, E_total=E, p1=E / N,
                p1_por_tipo={k: (E_k[k] / N if E_k[k] == E_k[k] else None) for k in TIPOS},
                p2_ponderado=sum(w[k] * p2k[k] for k in TIPOS))


def medir_D(R_ok, pesos, viz_reg):
    """D por evento-fonte: P(vizinho do caminho k e titulo de mesario do 2T registrado em OUTRA secao),
    ponderado pelos caminhos; e D_mesma: idem na MESMA secao (vira bloqueio). Devolve DataFrame por
    ocorrencia (titulo, secao) e o dicionario de alvos para a simulacao."""
    secs_de = R_ok.groupby("titulo").sec.apply(lambda x: sorted(set(x))).to_dict()
    occ = R_ok[["titulo", "sec", "uf", "zona"]].drop_duplicates(["titulo", "sec"])
    nviz = {}
    linhas = []
    for t, s, uf, zona in occ.values:
        d_out = d_same = 0.0
        if t in viz_reg:
            por_tipo = defaultdict(list)
            for b, tp in viz_reg[t]:
                por_tipo[tp].append(b)
            for tp, alvos in por_tipo.items():
                if pesos.get(tp, 0) == 0:
                    continue
                key = (t, tp)
                if key not in nviz:
                    nviz[key] = len(vizinhos(t, tp))
                nv = nviz[key]
                if nv == 0:
                    continue
                out = sum(1 for b in alvos if set(secs_de[b]) - {s})
                same = sum(1 for b in alvos if s in secs_de[b])
                d_out += pesos[tp] * out / nv
                d_same += pesos[tp] * same / nv
        linhas.append((t, s, uf, zona, d_out, d_same))
    return pd.DataFrame(linhas, columns=["titulo", "sec", "uf", "zona", "D_outra_secao", "D_mesma_secao"])


def vizinhos_registrados(R_ok):
    pares = pares_um_erro(R_ok.titulo.unique())
    viz = defaultdict(list)
    for a, b in pares:
        ta, tb = tipo_erro_dir(a, b), tipo_erro_dir(b, a)
        if ta:
            viz[a].append((b, ta))   # a pretendido, b digitado
        if tb:
            viz[b].append((a, tb))
    return viz


def main():
    import argparse
    import json
    ap = argparse.ArgumentParser()
    ap.add_argument("ano", type=int)
    ap.add_argument("--turno", type=int, default=2)
    ap.add_argument("--loo", dest="loo", action="store_true", default=True)
    ap.add_argument("--sem-loo", dest="loo", action="store_false")
    ap.add_argument("--entrada", default=None)
    ap.add_argument("--saida", default=None)
    a = ap.parse_args()
    import simulacao as sim
    root = sim.ROOT
    R, L, B = sim.carregar(a.ano, a.turno, a.entrada or os.path.join(root, "data", "censo"))
    R_ok, B, den = sim.preparar(R, L, B, a.ano, a.turno)
    qd, d = quase_duplicados(R_ok)
    R_d, qd_p1, loo = aplicar_loo(R_ok, qd, a.loo)
    p2k = p2_por_tipo(R_d.titulo.unique())
    m = medir_p1(R_ok, qd_p1, d, p2k, den["registros_N"])
    Ddf = medir_D(R_d, m["pesos"], vizinhos_registrados(R_d))
    n = R_d.groupby(["titulo", "sec"]).size().rename("n").reset_index()
    Ddf = Ddf.merge(n, on=["titulo", "sec"])
    D = float((Ddf.D_outra_secao * Ddf.n).sum() / Ddf.n.sum()) if len(Ddf) else 0.0
    out = dict(**den, **loo, p1=m["p1"], p1_por_tipo=m["p1_por_tipo"], pesos=m["pesos"], p2=p2k, D=D,
               esperado_N_p1_D=den["registros_N"] * m["p1"] * D)
    saida = a.saida or os.path.join(root, "data", "outputs", f"{a.ano}_t{a.turno}")
    os.makedirs(saida, exist_ok=True)
    json.dump(out, open(os.path.join(saida, "densidade_parametros.json"), "w"), indent=2, default=float)
    print(json.dumps(out, indent=2, default=float))


if __name__ == "__main__":
    main()

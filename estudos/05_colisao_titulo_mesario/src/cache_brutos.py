#!/usr/bin/env python3
"""
cache_brutos.py -- cache seletivo dos logs originais (fora do Git), montado APOS o censo.

O censo nao mantem os brutos (cerca de 50 GB por turno). Este script baixa de novo apenas as secoes
sinalizadas, confere cada arquivo contra o SHA-256 gravado no censo (prova de identidade com o arquivo
contado) e grava em data/raw/cache_<ano>_t<turno>/<uf>/<mun>/<zona>/<secao>/<arquivo>.

Criterios (emenda 05):
  bloqueios  secoes com ao menos um "Mesário <T> já registrado" no turno  -> tambem gera
             data/censo/bloqueios_contexto_<ano>_t<turno>.csv (reinicio, votos e registro anterior)
  erro_alto  secoes com taxa de rejeicao (tentativas invalidas / tentativas) acima de 4x a mediana da UF
  colisoes   secoes envolvidas em colisoes; SO depois do commit dos parametros congelados (etapa 5c)

Uso: python cache_brutos.py ANO TURNO {bloqueios|erro_alto|colisoes} [--workers 16]
"""
import csv
import hashlib
import os
import sys
import threading
from concurrent.futures import ThreadPoolExecutor

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from censo import http  # noqa: E402
from parsing import ler_logd, contexto_bloqueios  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CENSO = os.path.join(ROOT, "data", "censo")
SEC = ["uf", "mun", "zona", "secao"]
lock = threading.Lock()


def ler(padrao):
    import glob
    fs = sorted(glob.glob(os.path.join(CENSO, padrao)))
    return pd.concat([pd.read_csv(f, dtype=str) for f in fs], ignore_index=True) if fs else pd.DataFrame()


def secoes_alvo(ano, turno, criterio):
    L = ler(f"logs_{ano}_t{turno}_s*.csv")
    L = L[L.sha256.notna()].drop_duplicates(SEC + ["arquivo"], keep="last")
    if criterio == "bloqueios":
        B = ler(f"bloqueios_{ano}_t{turno}_s*.csv")
        alvo = set(map(tuple, B[SEC].values))
    elif criterio == "erro_alto":
        for c in ("n_invalido", "n_registrado", "n_ja_registrado"):
            L[c] = pd.to_numeric(L[c], errors="coerce").fillna(0)
        g = L.groupby(SEC)[["n_invalido", "n_registrado", "n_ja_registrado"]].sum().reset_index()
        g["taxa"] = g.n_invalido / (g.n_invalido + g.n_registrado + g.n_ja_registrado).clip(lower=1)
        med = g.groupby("uf").taxa.median()
        g = g[g.taxa > 4 * g.uf.map(med).clip(lower=1e-9)]
        alvo = set(map(tuple, g[SEC].values))
    elif criterio == "colisoes":
        marca = os.path.join(ROOT, "registro", "parametros_2t2026.sha256")
        if not os.path.exists(marca):
            raise SystemExit("parametros ainda nao congelados (etapa 5c): cache de colisoes bloqueado")
        R = ler(f"registros_{ano}_t{turno}_s*.csv")
        R["sec"] = R[SEC].agg("-".join, axis=1)
        n = R.groupby("titulo").sec.nunique()
        alvo = set(map(tuple, R[R.titulo.isin(n[n >= 2].index)][SEC].drop_duplicates().values))
    else:
        raise SystemExit("criterio desconhecido")
    return L[[tuple(x) in alvo for x in L[SEC].values]]


def main(ano, turno, criterio, workers=16):
    alvo = secoes_alvo(ano, turno, criterio)
    base = os.path.join(ROOT, "data", "raw", f"cache_{ano}_t{turno}")
    p_ctx = os.path.join(CENSO, f"bloqueios_contexto_{ano}_t{turno}.csv")
    p_man = os.path.join(base, "manifesto_cache.csv")
    os.makedirs(base, exist_ok=True)
    feitos = set()
    if os.path.exists(p_man):
        feitos = {r["arquivo_local"] for r in csv.DictReader(open(p_man, encoding="utf-8"))}
    campos_ctx = SEC + ["arquivo", "titulo", "ts", "id_urna", "hash_linha", "reinicio_ts", "seg_desde_reinicio",
                        "votos_desde_reinicio", "registro_ts", "seg_desde_registro", "votos_desde_registro"]
    fctx = open(p_ctx, "a", newline="", encoding="utf-8")
    wctx = csv.DictWriter(fctx, campos_ctx)
    if os.path.getsize(p_ctx) == 0:
        wctx.writeheader()
    fman = open(p_man, "a", newline="", encoding="utf-8")
    wman = csv.DictWriter(fman, SEC + ["arquivo", "arquivo_local", "url", "sha256_censo", "sha256_cache", "confere",
                                       "criterio"])
    if os.path.getsize(p_man) == 0:
        wman.writeheader()
    cont = {"ok": 0, "divergente": 0, "falha": 0, "ja_feito": 0}

    def um(r):
        rel = os.path.join(r["uf"], r["mun"], r["zona"], r["secao"], r["arquivo"])
        if rel in feitos:
            cont["ja_feito"] += 1
            return
        dest = os.path.join(base, rel)
        try:
            dados = open(dest, "rb").read() if os.path.exists(dest) else http(r["url"].split("#")[0])
        except Exception:
            with lock:
                cont["falha"] += 1
            return
        h = hashlib.sha256(dados).hexdigest()
        if not os.path.exists(dest):
            os.makedirs(os.path.dirname(dest), exist_ok=True)
            open(dest, "xb").write(dados)
        linhas = []
        if criterio == "bloqueios":
            txt, _ = ler_logd(dados)
            linhas = [dict({k: r[k] for k in SEC}, arquivo=r["arquivo"], **c) for c in contexto_bloqueios(txt, ano, turno)]
        with lock:
            wman.writerow(dict({k: r[k] for k in SEC}, arquivo=r["arquivo"], arquivo_local=rel, url=r["url"],
                               sha256_censo=r["sha256"], sha256_cache=h, confere=h == r["sha256"], criterio=criterio))
            wctx.writerows(linhas)
            cont["ok" if h == r["sha256"] else "divergente"] += 1

    with ThreadPoolExecutor(workers) as ex:
        list(ex.map(um, alvo.to_dict("records")))
    fctx.close()
    fman.close()
    print(criterio, len(alvo), "arquivos-alvo;", cont)


if __name__ == "__main__":
    a = sys.argv
    main(int(a[1]), int(a[2]), a[3], int(a[a.index("--workers") + 1]) if "--workers" in a else 16)

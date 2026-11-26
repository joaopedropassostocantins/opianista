#!/usr/bin/env python3
"""
votos.py -- cruzamento complementar com o movimento de votos (emenda 05; nao e o teste principal).

Desfecho: variacao, por secao, da margem entre os dois candidatos do 2o turno presidencial, do 1o para o 2o
turno: delta = margem_2T - margem_1T, margem = (votos_A - votos_B) / comparecimento. Tambem se reportam as
variacoes de cada candidato em separado (simetria).
Tratamento: secoes envolvidas em colisao (nao excluidas).
Controle: as demais secoes do MESMO local de votacao (mesma UF, municipio, zona e NR_LOCAL_VOTACAO), sem colisao.
Teste de outlier: z = (delta_secao - media_vizinhas) / dp_vizinhas; outlier se |z| > 3, com >= 3 vizinhas.
Leitura congelada: nao confirma digitacao nem prova manipulacao; diz se as secoes com colisao se comportam
como as vizinhas. Nao ve alteracao que atinja os dois turnos por igual, nem alteracao so no 2o turno sem
rastro relativo ao 1o.
Tambem grava, por secao, urna efetivada e codigos de carga/flashcard do 2o turno (discriminador da familia 4).

Fonte: boletim de urna web, dadosabertos.tse.jus.br (pacote resultados-2026-boletim-de-urna), por UF.
Uso: python votos.py 2026
"""
import argparse
import csv
import hashlib
import io
import json
import os
import sys
import time
import urllib.request
import zipfile

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from censo import http  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SEC = ["uf", "mun", "zona", "secao"]
LIMIAR_Z = 3.0
MIN_VIZINHAS = 3


def urls_bweb(ano):
    api = f"https://dadosabertos.tse.jus.br/api/3/action/package_show?id=resultados-{ano}-boletim-de-urna"
    with urllib.request.urlopen(urllib.request.Request(api, headers={"User-Agent": "pesquisa-academica"}), timeout=60) as r:
        res = json.load(r)["result"]["resources"]
    out = {}
    for x in res:
        u = x["url"]
        if not u.endswith(".zip"):
            continue
        nome = os.path.basename(u)
        partes = nome.split("_")
        if len(partes) >= 4 and partes[0].lower() == "bweb":
            out[(partes[1].lower(), partes[2].lower())] = u   # (1t|2t, uf) -> url (a ultima publicada prevalece)
    return out


def baixar(url, destdir, manifesto):
    os.makedirs(destdir, exist_ok=True)
    dest = os.path.join(destdir, os.path.basename(url))
    if not os.path.exists(dest):
        dados = http(url)
        open(dest, "xb").write(dados)
        with open(manifesto, "a", newline="") as fh:
            csv.writer(fh).writerow([os.path.basename(url), hashlib.sha256(dados).hexdigest(), len(dados), url,
                                     time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())])
    return dest


def ler_presidente(path):
    z = zipfile.ZipFile(path)
    nm = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
    cols = ["SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "NR_LOCAL_VOTACAO", "DS_CARGO_PERGUNTA", "QT_COMPARECIMENTO",
            "DS_TIPO_VOTAVEL", "NR_VOTAVEL", "QT_VOTOS", "NR_URNA_EFETIVADA", "CD_CARGA_1_URNA_EFETIVADA",
            "CD_CARGA_2_URNA_EFETIVADA", "CD_FLASHCARD_URNA_EFETIVADA", "DS_TIPO_URNA"]
    df = pd.read_csv(io.BytesIO(z.read(nm)), sep=";", encoding="latin-1", dtype=str, usecols=cols)
    df = df[df.DS_CARGO_PERGUNTA.str.upper() == "PRESIDENTE"].copy()
    df["uf"] = df.SG_UF.str.lower()
    df["mun"] = df.CD_MUNICIPIO.str.zfill(5)
    df["zona"] = df.NR_ZONA.str.zfill(4)
    df["secao"] = df.NR_SECAO.str.zfill(4)
    df["QT_VOTOS"] = pd.to_numeric(df.QT_VOTOS)
    df["QT_COMPARECIMENTO"] = pd.to_numeric(df.QT_COMPARECIMENTO)
    return df


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ano", type=int)
    ap.add_argument("--turno", type=int, default=2)
    a = ap.parse_args()
    saida = os.path.join(ROOT, "data", "outputs", f"{a.ano}_t{a.turno}")
    col = pd.read_csv(os.path.join(saida, "colisoes.csv"), dtype=str).fillna("")
    col = col[col.exclusao == ""]
    trat = set()
    for p in ("a", "b"):
        trat |= set(col[[f"uf_{p}", f"mun_{p}", f"zona_{p}", f"secao_{p}"]].agg("-".join, axis=1))
    ufs = sorted({s.split("-")[0] for s in trat})
    urls = urls_bweb(a.ano)
    destdir = os.path.join(ROOT, "data", "raw", "bweb")
    man = os.path.join(destdir, "manifesto_bweb.csv")
    linhas, carga = [], []
    for uf in ufs:
        d1 = ler_presidente(baixar(urls[("1t", uf)], destdir, man))
        d2 = ler_presidente(baixar(urls[("2t", uf)], destdir, man))
        cand = (d2[d2.DS_TIPO_VOTAVEL.str.lower() == "nominal"].groupby("NR_VOTAVEL").QT_VOTOS.sum()
                .sort_values(ascending=False).index[:2].tolist())
        A, B = sorted(cand)

        def margem(df):
            g = df.groupby(SEC + ["NR_LOCAL_VOTACAO"])
            comp = g.QT_COMPARECIMENTO.first()
            va = df[df.NR_VOTAVEL == A].groupby(SEC + ["NR_LOCAL_VOTACAO"]).QT_VOTOS.sum().reindex(comp.index, fill_value=0)
            vb = df[df.NR_VOTAVEL == B].groupby(SEC + ["NR_LOCAL_VOTACAO"]).QT_VOTOS.sum().reindex(comp.index, fill_value=0)
            return pd.DataFrame({"comp": comp, "sa": va / comp.clip(lower=1), "sb": vb / comp.clip(lower=1)})
        m1, m2 = margem(d1), margem(d2)
        m = m2.join(m1, lsuffix="_2t", rsuffix="_1t", how="inner").reset_index()
        m["sec"] = m[SEC].agg("-".join, axis=1)
        m["delta"] = (m.sa_2t - m.sb_2t) - (m.sa_1t - m.sb_1t)
        m["delta_A"] = m.sa_2t - m.sa_1t
        m["delta_B"] = m.sb_2t - m.sb_1t
        m["local_key"] = m.uf + "-" + m.mun + "-" + m.zona + "-" + m.NR_LOCAL_VOTACAO
        m_idx = m.set_index("sec")
        por_local = m.groupby("local_key").sec.apply(list).to_dict()
        for s in sorted(x for x in trat if x.startswith(uf + "-")):
            if s not in m_idx.index:
                linhas.append(dict(sec=s, situacao="secao_sem_bu_em_um_dos_turnos"))
                continue
            r = m_idx.loc[s]
            if isinstance(r, pd.DataFrame):
                r = r.iloc[0]
            vizs = [x for x in por_local.get(r.local_key, []) if x not in trat and x != s]
            vd = m_idx.loc[vizs, "delta"] if vizs else pd.Series(dtype=float)
            n = len(vizs)
            mu, dp = (float(vd.mean()), float(vd.std(ddof=1))) if n >= 2 else (np.nan, np.nan)
            z = (r.delta - mu) / dp if n >= MIN_VIZINHAS and dp and dp > 0 else np.nan
            linhas.append(dict(sec=s, local=r.NR_LOCAL_VOTACAO, candidato_A=A, candidato_B=B, n_vizinhas=n,
                               vizinhas="|".join(vizs), delta_margem=r.delta, delta_A=r.delta_A, delta_B=r.delta_B,
                               media_vizinhas=mu, dp_vizinhas=dp, z=z,
                               outlier_3dp=bool(abs(z) > LIMIAR_Z) if z == z else False,
                               situacao="ok" if n >= MIN_VIZINHAS else "vizinhas_insuficientes"))
        c2 = d2.drop_duplicates(SEC)
        c2 = c2[c2[SEC].agg("-".join, axis=1).isin(trat)]
        for r in c2.to_dict("records"):
            carga.append(dict(sec="-".join(r[k] for k in SEC), urna_efetivada=r["NR_URNA_EFETIVADA"],
                              carga1=r["CD_CARGA_1_URNA_EFETIVADA"], carga2=r["CD_CARGA_2_URNA_EFETIVADA"],
                              flashcard=r["CD_FLASHCARD_URNA_EFETIVADA"], tipo_urna=r["DS_TIPO_URNA"]))
    out = pd.DataFrame(linhas)
    if len(carga):
        out = out.merge(pd.DataFrame(carga), on="sec", how="left")
    out.to_csv(os.path.join(saida, "votos_outlier.csv"), index=False)
    print(out.drop(columns=["vizinhas"], errors="ignore").to_string(index=False))


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""Analise do 2T2026 pelo protocolo E05-0 com as emendas 01 e 02 (P-I, classe I).

Entradas: CSV de horarios_secao.py do 2T2026 (presidente em votos_cargo,
governador em votos_cargo2) e, como referencia, os CSV do 2T2024. Saida: JSON
com todos os numeros do relatorio preliminar.

Horarios convertidos para Brasilia por municipio (brasilia_offsets). Secoes no
exterior (ZZ) ficam fora dos contrastes: la a votacao segue a hora local.
TO fica fora das analises confirmatorias (emenda 02) e entra so como sensibilidade.
Exige --liberado-d4 (decisao registrada em protocolos/REGISTRO.md).
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import sys
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent
_spec = importlib.util.spec_from_file_location("contraste_local", ROOT / "contraste_local.py")
con = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(con)

OFICIAL = {"lula_13": 64256232, "flavio_22": 59826041, "margem": 4430191,
           "secoes_apos_17h": 497333, "secoes_apos_17h10": 24268, "secoes_apos_19h": 6766,
           "votos_apos_17h": 34393, "votos_17h_18h": 32399, "votos_18h_19h": 1981, "votos_apos_19h": 13,
           "votos_apos_17h_secoes_encerradas_apos_19h": 4773}


def read(paths):
    rows = []
    for p in paths:
        with open(p, encoding="utf-8") as fp:
            rows.extend(csv.DictReader(fp))
    return rows


def holm(pvals: dict) -> dict:
    items = sorted(pvals.items(), key=lambda kv: kv[1])
    m, out, running = len(items), {}, 0.0
    for i, (k, p) in enumerate(items):
        running = max(running, min(1.0, (m - i) * p))
        out[k] = running
    return out


def pvalue(beta, se):
    if not se or se != se:
        return float("nan")
    z = abs(beta / se)
    return math.erfc(z / math.sqrt(2))


def contrast(rows, limiar, controle, candidato, coluna, excluir):
    units, lost, winners = con.build_units(rows, "ultimo_voto_log", limiar, candidato, True,
                                           controle, coluna, excluir)
    res = con.fe_contrast(units)
    res.update({"limiar": limiar, "controle": controle or "complemento", "candidato": candidato,
                "coluna": coluna, "ufs_excluidas": list(excluir), "perdas": lost,
                "secoes_usadas": len(units), "tratadas_total": sum(u["T"] for u in units),
                "votos_validos_tratadas": sum(u["w"] for u in units if u["T"])})
    if res.get("estimavel"):
        res["p_bilateral"] = pvalue(res["beta"], res["se_cluster"])
    return res


def describe(rows, offsets, label):
    n = len(rows)
    def bt(r, f):
        t = r.get(f, "")
        return con.minutes(t) - 60 * offsets.get((r["uf"], r["municipio"]), 0) if t else None
    out = {"rotulo": label, "secoes": n}
    for f in ("ultimo_voto_log", "fechamento_bu"):
        ts = [bt(r, f) for r in rows if r["uf"] != "ZZ"]
        ts = [t for t in ts if t is not None]
        out[f] = {"n": len(ts), **{f"apos_{h}": sum(1 for t in ts if t > con.minutes(h + ":00"))
                                   for h in ("17:00", "17:10", "18:00", "19:00")}}
        out[f]["frac_apos_17:00"] = out[f]["apos_17:00"] / len(ts) if ts else None
    faixas = {"17h_18h": 0, "18h_19h": 0, "apos_19h": 0}
    com_hist = 0
    for r in rows:
        if r["uf"] == "ZZ" or not r.get("votos_por_hora_log"):
            continue
        com_hist += 1
        off = offsets.get((r["uf"], r["municipio"]), 0)
        for h, c in json.loads(r["votos_por_hora_log"]).items():
            hb = int(h) - off
            if hb == 17:
                faixas["17h_18h"] += c
            elif hb == 18:
                faixas["18h_19h"] += c
            elif hb >= 19:
                faixas["apos_19h"] += c
    # Sem histograma (extracao anterior ao campo) a contagem e NAO DISPONIVEL, nunca zero.
    out["votos_apos_17h_brasilia"] = sum(faixas.values()) if com_hist else None
    out["votos_por_faixa_brasilia"] = faixas if com_hist else None
    out["secoes_com_histograma"] = com_hist
    comp = [int(r["comparecimento"]) for r in rows if r.get("comparecimento")]
    out["comparecimento_medio_secao"] = sum(comp) / len(comp) if comp else None
    out["coerencia"] = defaultdict(int)
    for r in rows:
        out["coerencia"][con.coherence_failure(r) or "ok"] += 1
    return out


def totals(rows, col):
    t = defaultdict(int)
    for r in rows:
        if r.get(col):
            for k, v in json.loads(r[col]).items():
                t[k] += v
    return dict(t)


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--h2026", nargs="+", required=True)
    p.add_argument("--h2024", nargs="+", required=True)
    p.add_argument("--liberado-d4", required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args(argv)
    r26, r24 = read(a.h2026), read(a.h2024)
    off26, off24 = con.brasilia_offsets(r26), con.brasilia_offsets(r24)
    res = {"liberacao_d4": a.liberado_d4, "oficial": OFICIAL}
    res["descritivo_2026"] = describe(r26, off26, "2T2026")
    res["descritivo_2024"] = describe(r24, off24, "2T2024")
    pres = totals(r26, "votos_cargo")
    res["totais_presidente_bu"] = pres
    res["dif_oficial"] = {"13": pres.get("13", 0) - OFICIAL["lula_13"], "22": pres.get("22", 0) - OFICIAL["flavio_22"]}
    res["offsets_nao_zero_2026"] = {"/".join(k): v for k, v in off26.items() if v}
    conf = ("TO", "ZZ")
    c = {}
    c["primario_19h"] = contrast(r26, "19:00:00", "17:00:00", "13", "votos_cargo", conf)
    c["secundario_17h10"] = contrast(r26, "17:10:00", "17:00:00", "13", "votos_cargo", conf)
    c["fila_17h"] = contrast(r26, "17:00:00", "", "13", "votos_cargo", conf)
    c["sens_com_TO_19h"] = contrast(r26, "19:00:00", "17:00:00", "13", "votos_cargo", ("ZZ",))
    c["governador_19h"] = contrast(r26, "19:00:00", "17:00:00", "vencedor", "votos_cargo2", conf)
    c["governador_fila_17h"] = contrast(r26, "17:00:00", "", "vencedor", "votos_cargo2", conf)
    c["placebo_2024_fila_17h"] = contrast(r24, "17:00:00", "", "vencedor", "votos_cargo", ())
    ps = {k: c[k]["p_bilateral"] for k in ("primario_19h", "secundario_17h10") if c[k].get("estimavel")}
    res["holm"] = holm(ps) if ps else {}
    res["contrastes"] = c
    for k in ("primario_19h", "secundario_17h10", "fila_17h"):
        v = c[k].get("votos_validos_tratadas", 0)
        res.setdefault("materialidade", {})[k] = {
            "votos_validos_coorte": v,
            "fracao_minima_para_inverter": (OFICIAL["margem"] + 1) / (2 * v) if v else None}
    a.out.write_text(json.dumps(res, ensure_ascii=False, indent=2, default=dict), "utf-8")
    print(json.dumps({k: res[k] for k in ("dif_oficial", "holm")}, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

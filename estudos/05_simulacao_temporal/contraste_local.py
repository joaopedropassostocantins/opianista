#!/usr/bin/env python3
"""Contraste exploratorio dentro do local de votacao (placebo, classe I).

Junta: saida de pipeline_placebo.py (votos por secao), saida de horarios_secao.py
(horarios do relogio da urna) e o CSV oficial votacao_secao (NR_LOCAL_VOTACAO).
Estima y_s = alpha_local + beta * T_s, ponderado por votos validos, com erro-padrao
agrupado por local (CR1). T_s = 1 se o horario escolhido for posterior ao limiar.

Resultado EXPLORATORIO: os horarios vem do relogio da urna (classe I) e o periodo
e placebo. Nao e teste confirmatorio do Estudo 05. Bloqueia 2T2026 (D4).
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import math
import sys
import zipfile
from collections import defaultdict
from pathlib import Path


def minutes(t: str) -> float:
    h, m, s = map(int, t.split(":"))
    return h * 60 + m + s / 60


def local_ids(zip_path: Path, year: int, turn: int) -> dict:
    out = {}
    with zipfile.ZipFile(zip_path) as z:
        member = [n for n in z.namelist() if n.lower().endswith(".csv")][0]
        with z.open(member) as b:
            for row in csv.DictReader(io.TextIOWrapper(b, encoding="cp1252", newline=""), delimiter=";"):
                if int(row["ANO_ELEICAO"]) == year and int(row["NR_TURNO"]) == turn:
                    key = (str(int(row["CD_MUNICIPIO"])), str(int(row["NR_ZONA"])), str(int(row["NR_SECAO"])))
                    out[key] = (key[0], key[1], row["NR_LOCAL_VOTACAO"].strip())
    return out


def fe_contrast(units: list[dict]) -> dict:
    """WLS com efeito fixo de local via demeaning ponderado; SE agrupado CR1."""
    by_local = defaultdict(list)
    for u in units:
        by_local[u["local"]].append(u)
    informative = {k: v for k, v in by_local.items() if len({u["T"] for u in v}) == 2}
    rows = []
    for v in informative.values():
        w = sum(u["w"] for u in v)
        ybar = sum(u["w"] * u["y"] for u in v) / w
        tbar = sum(u["w"] * u["T"] for u in v) / w
        rows.extend((u["local"], u["w"], u["y"] - ybar, u["T"] - tbar) for u in v)
    sxx = sum(w * t * t for _, w, _, t in rows)
    if not rows or sxx == 0:
        return {"estimavel": False, "locais_informativos": len(informative)}
    beta = sum(w * t * y for _, w, y, t in rows) / sxx
    score = defaultdict(float)
    for local, w, y, t in rows:
        score[local] += w * t * (y - beta * t)
    g, n = len(score), len(rows)
    k = 1 + len(informative)
    adj = (g / (g - 1)) * ((n - 1) / max(n - k, 1)) if g > 1 else float("nan")
    se = math.sqrt(adj * sum(s * s for s in score.values())) / sxx if g > 1 else float("nan")
    return {"estimavel": True, "beta": beta, "se_cluster": se,
            "ic95": [beta - 1.96 * se, beta + 1.96 * se],
            "locais_informativos": g, "secoes_informativas": n,
            "secoes_tratadas": sum(1 for r in rows if r[3] > 0)}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--placebo", type=Path, required=True)
    p.add_argument("--horarios", type=Path, required=True)
    p.add_argument("--votacao-secao", type=Path, required=True)
    p.add_argument("--campo", default="ultimo_voto_log")
    p.add_argument("--limiar", default="17:00:00")
    p.add_argument("--candidato", required=True, help="numero do candidato no desfecho")
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args(argv)
    placebo = json.loads(a.placebo.read_text("utf-8"))
    if placebo["period"] == "2T2026":
        print("BLOQUEADO: D4", file=sys.stderr)
        return 2
    year, turn = (2024, 2) if placebo["period"] == "2T2024" else (2026, 1)
    locs = local_ids(a.votacao_secao, year, turn)
    times = {(r["municipio"], r["zona"], r["secao"]): r for r in csv.DictReader(a.horarios.open(encoding="utf-8"))}
    cut = minutes(a.limiar)
    units, lost = [], defaultdict(int)
    for s in placebo["sections"]:
        key = (str(int(s["municipio"])), str(int(s["zona"])), str(int(s["secao"])))
        if key not in locs:
            lost["sem_local"] += 1; continue
        t = times.get(key, {}).get(a.campo, "")
        if not t:
            lost["sem_horario"] += 1; continue
        if s["votes_valid"] == 0:
            lost["sem_validos"] += 1; continue
        units.append({"local": locs[key], "w": s["votes_valid"], "T": int(minutes(t) > cut),
                      "y": s["votes_by_number"].get(a.candidato, 0) / s["votes_valid"]})
    res = fe_contrast(units)
    res.update({"periodo": placebo["period"], "campo_horario": a.campo, "limiar": a.limiar,
                "candidato": a.candidato, "secoes_usadas": len(units), "perdas": dict(lost),
                "tratadas_total": sum(u["T"] for u in units),
                "classe_relogio": "I (urna)", "status": "EXPLORATORIO_PLACEBO"})
    a.out.write_text(json.dumps(res, ensure_ascii=False, indent=2), "utf-8")
    print(json.dumps(res, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

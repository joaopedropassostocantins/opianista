#!/usr/bin/env python3
"""Contraste exploratorio dentro do local de votacao (placebo, classe I).

Entrada: um ou mais CSV gerados por horarios_secao.py (votos da imagem do BU,
local de votacao e horarios do relogio da urna). Estima
y_s = alpha_local + beta * T_s, ponderado por votos validos, com erro-padrao
agrupado por local (CR1). T_s = 1 se o horario escolhido for posterior ao limiar.
Desfecho: fracao de um candidato fixo, ou do vencedor de cada municipio
(--candidato vencedor), nos votos validos da secao (todos os votos da secao).

Resultado EXPLORATORIO: os horarios vem do relogio da urna (classe I).
Nao e teste confirmatorio do Estudo 05. Recusa entradas do 2T2026 (D4).
"""
from __future__ import annotations

import argparse
import csv
import json
import math
import sys
from collections import defaultdict
from pathlib import Path


def minutes(t: str) -> float:
    h, m, s = map(int, t.split(":"))
    return h * 60 + m + s / 60


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


def load_rows(paths: list[Path], liberado_d4: bool = False) -> list[dict]:
    rows = []
    for path in paths:
        if not liberado_d4 and ("2026_2t" in path.name.lower() or "2t2026" in path.name.lower()):
            raise ValueError("Entrada do 2T2026 bloqueada (D4).")
        with path.open(encoding="utf-8") as fp:
            rows.extend(csv.DictReader(fp))
    return rows


def coherence_failure(r: dict) -> str:
    """Verificacoes 1 a 3 da emenda 01 do E05-0; retorna o motivo ou ''."""
    needed = ("comparecimento", "votos_computados_log", "fechamento_bu",
              "encerramento_confirmado_log", "ultimo_voto_log", "bu_gerado_log")
    if any(not r.get(k) for k in needed):
        return "incoerente_campo_ausente"
    if int(r["votos_computados_log"]) != int(r["comparecimento"]):
        return "incoerente_log_x_bu"
    if abs(minutes(r["fechamento_bu"]) - minutes(r["encerramento_confirmado_log"])) > 2 / 60:
        return "incoerente_fechamento"
    if not (r["ultimo_voto_log"] <= r["encerramento_confirmado_log"] <= r["bu_gerado_log"]):
        return "incoerente_ordem"
    return ""


def build_units(rows: list[dict], campo: str, limiar: str, candidato: str,
                coerencia: bool = True, controle: str = "", coluna_votos: str = "votos_cargo",
                excluir_uf: tuple = ()) -> tuple[list, dict, dict]:
    """controle: se informado, so entram como nao tratadas as secoes com campo <= controle;
    secoes entre controle e limiar ficam fora do contraste (emenda 01, secao 1.3)."""
    cut = minutes(limiar)
    ctrl = minutes(controle) if controle else None
    lost: dict[str, int] = defaultdict(int)
    parsed = []
    for r in rows:
        if r.get("uf") in excluir_uf:
            lost["uf_excluida"] += 1; continue
        if coerencia:
            motivo = coherence_failure(r)
            if motivo:
                lost[motivo] += 1; continue
        if not r.get(coluna_votos):
            lost["sem_votos_bu"] += 1; continue
        if not r.get("local"):
            lost["sem_local"] += 1; continue
        if not r.get(campo):
            lost["sem_horario"] += 1; continue
        t = minutes(r[campo])
        if ctrl is not None and ctrl < t <= cut:
            lost["entre_controle_e_limiar"] += 1; continue
        votes = json.loads(r[coluna_votos])
        valid = sum(votes.values())
        if valid == 0:
            lost["sem_validos"] += 1; continue
        parsed.append((r, votes, valid))
    winners = {}
    if candidato == "vencedor":
        tally: dict[tuple, dict] = defaultdict(lambda: defaultdict(int))
        for r, votes, _ in parsed:
            for k, v in votes.items():
                tally[(r["uf"], r["municipio"])][k] += v
        winners = {m: max(t, key=t.get) for m, t in tally.items()}
    units = []
    for r, votes, valid in parsed:
        target = winners[(r["uf"], r["municipio"])] if candidato == "vencedor" else candidato
        units.append({"local": (r["uf"], r["municipio"], r["zona"], r["local"]), "w": valid,
                      "T": int(minutes(r[campo]) > cut), "y": votes.get(target, 0) / valid,
                      "municipio": (r["uf"], r["municipio"])})
    return units, dict(lost), {"/".join(k): v for k, v in winners.items()}


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--horarios", type=Path, nargs="+", required=True)
    p.add_argument("--campo", default="ultimo_voto_log")
    p.add_argument("--limiar", default="17:00:00")
    p.add_argument("--candidato", default="vencedor", help="numero do candidato ou 'vencedor'")
    p.add_argument("--rotulo", default="placebo")
    p.add_argument("--sem-coerencia", action="store_true", help="desliga as verificacoes da emenda 01")
    p.add_argument("--controle", default="", help="ultimo horario admitido no controle, ex.: 17:00:00")
    p.add_argument("--coluna-votos", default="votos_cargo", help="votos_cargo ou votos_cargo2")
    p.add_argument("--excluir-uf", default="", help="UFs separadas por virgula")
    p.add_argument("--liberado-d4", default="", help="referencia da decisao que liberou o 2T2026")
    p.add_argument("--status", default="EXPLORATORIO_PLACEBO")
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args(argv)
    try:
        rows = load_rows(a.horarios, bool(a.liberado_d4))
    except (OSError, ValueError) as e:
        print("BLOQUEADO:", e, file=sys.stderr)
        return 2
    excl = tuple(x.strip().upper() for x in a.excluir_uf.split(",") if x.strip())
    units, lost, winners = build_units(rows, a.campo, a.limiar, a.candidato, not a.sem_coerencia,
                                       a.controle, a.coluna_votos, excl)
    res = fe_contrast(units)
    per_mun = defaultdict(lambda: [0, 0])
    for u in units:
        per_mun["/".join(u["municipio"])][0] += 1
        per_mun["/".join(u["municipio"])][1] += u["T"]
    res.update({"rotulo": a.rotulo, "campo_horario": a.campo, "limiar": a.limiar,
                "candidato": a.candidato, "secoes_usadas": len(units), "perdas": lost,
                "tratadas_total": sum(u["T"] for u in units),
                "municipios": len(per_mun),
                "municipios_com_tratadas": sum(1 for v in per_mun.values() if v[1]),
                "controle": a.controle or "complemento do limiar", "coluna_votos": a.coluna_votos,
                "ufs_excluidas": list(excl), "cohorte_votos_validos_tratadas": sum(u["w"] for u in units if u["T"]),
                "classe_relogio": "I (urna)", "status": a.status})
    a.out.write_text(json.dumps(res, ensure_ascii=False, indent=2), "utf-8")
    print(json.dumps(res, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

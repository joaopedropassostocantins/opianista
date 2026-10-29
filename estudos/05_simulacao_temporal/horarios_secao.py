#!/usr/bin/env python3
"""Extrai horarios por secao dos arquivos transmitidos para totalizacao (TSE).

Le o ZIP oficial "bu_imgbu_logjez_rdv_vscmr_<ano>_<turno>_<UF>.zip" e, para cada
secao, extrai da imagem do BU e do log da urna (log.jez -> logd.dat):

- abertura e fechamento da UE declarados na imagem do BU;
- primeiro e ultimo "O voto do eleitor foi computado" na data da eleicao;
- "Procedimento de encerramento confirmado" e geracao do bu.dat;
- local de votacao, comparecimento e votos do cargo escolhido (imagem do BU).

Todos esses horarios vem do RELOGIO DA PROPRIA URNA (classe I do pre-registro
E05-0). Nao sao fonte externa. Linhas com titulo de eleitor ou CPF nunca sao
copiadas para a saida. Bloqueia 2T2026, salvo com --liberado-d4 (decisao D4).
Biblioteca padrao Python 3.11+.
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
import zipfile
from pathlib import Path

NAME = re.compile(r"^o\d+([a-z]{2})(\d{5})(\d{4})(\d{4})-(log\.jez|imgbu\.dat)$")
BLOCKED_ZIP = re.compile(r"_2026_2t_", re.I)
OUT_FIELDS = ("uf", "municipio", "zona", "secao", "local", "comparecimento", "votos_cargo",
              "brancos", "nulos", "total_apurado", "votos_cargo2", "abertura_bu", "fechamento_bu",
              "primeiro_voto_log", "ultimo_voto_log", "encerramento_confirmado_log",
              "bu_gerado_log", "votos_computados_log", "votos_apos_17h_log", "votos_apos_19h_log",
              "votos_por_hora_log",
              "fonte_relogio")


class Blocked(RuntimeError):
    pass


def imgbu_times(text: str) -> tuple[str, str]:
    a = re.search(r"Hor.rio de abertura\s+(\d{2}:\d{2}:\d{2})", text)
    f = re.search(r"Hor.rio de fechamento\s+(\d{2}:\d{2}:\d{2})", text)
    return (a.group(1) if a else "", f.group(1) if f else "")


def imgbu_votes(text: str, cargo: str) -> dict:
    """Votos do cargo na imagem do BU; cargo como impresso (ex.: PREFEITO, PRESIDENTE)."""
    out = {"local": "", "comparecimento": "", "votos_cargo": "", "brancos": "", "nulos": "",
           "total_apurado": ""}
    loc = re.search(r"Local de Vota..o\s+(\d+)", text)
    com = re.search(r"Comparecimento\s+(\d+)", text)
    out["local"] = str(int(loc.group(1))) if loc else ""
    out["comparecimento"] = int(com.group(1)) if com else ""
    block = re.search(r"-{3,}" + re.escape(cargo) + r"-{3,}(.*?)Total Apurado\s+(\d+)", text, re.S)
    if not block:
        return out
    body = block.group(1)
    votes = {}
    for m in re.finditer(r"^\s+\S.*?\s(\d{1,5})\s+(\d{4,})\s*$", body, re.M):
        votes[str(int(m.group(1)))] = votes.get(str(int(m.group(1))), 0) + int(m.group(2))
    b = re.search(r"^Brancos\s+(\d+)", body, re.M)
    n = re.search(r"^Nulos\s+(\d+)", body, re.M)
    out.update({"votos_cargo": json.dumps(votes, sort_keys=True), "brancos": int(b.group(1)) if b else 0,
                "nulos": int(n.group(1)) if n else 0, "total_apurado": int(block.group(2))})
    return out


def log_times(lines: list[str], date: str) -> dict:
    """date no formato dd/mm/aaaa; considera apenas eventos desse dia."""
    votes: list[str] = []
    closed = generated = ""
    for line in lines:
        if not line.startswith(date):
            continue
        parts = line.split("\t")
        if len(parts) < 5:
            continue
        hhmmss, msg = parts[0][11:19], parts[4]
        if msg == "O voto do eleitor foi computado":
            votes.append(hhmmss)
        elif msg == "Procedimento de encerramento confirmado" and not closed:
            closed = hhmmss
        elif msg.startswith("Gerando arquivo de resultado [bu.dat] + [In") and not generated:
            generated = hhmmss
    per_hour: dict[str, int] = {}
    for v in votes:
        per_hour[v[:2]] = per_hour.get(v[:2], 0) + 1
    return {"votos_por_hora_log": json.dumps(per_hour, sort_keys=True),
            "votos_apos_17h_log": sum(1 for v in votes if v > "17:00:00"),
            "votos_apos_19h_log": sum(1 for v in votes if v > "19:00:00"),
            "primeiro_voto_log": min(votes) if votes else "",
            "ultimo_voto_log": max(votes) if votes else "",
            "encerramento_confirmado_log": closed, "bu_gerado_log": generated,
            "votos_computados_log": len(votes)}


def ymd(ddmmyyyy: str) -> str:
    return ddmmyyyy[6:10] + ddmmyyyy[3:5] + ddmmyyyy[0:2]


def check_isolation(lines: list[str], max_date: str) -> None:
    """Aborta se algum evento do log for posterior a max_date (dd/mm/aaaa)."""
    limit = ymd(max_date)
    for line in lines:
        if re.match(r"\d{2}/\d{2}/\d{4}", line) and ymd(line[:10]) > limit:
            raise Blocked("Log contem evento posterior a " + max_date + ": recurso nao isolado.")


def extract(path: Path, date: str, cargo: str = "PREFEITO", max_date: str = "",
            turno_bu: str = "", cargo2: str = "", liberado_d4: bool = False) -> list[dict]:
    if BLOCKED_ZIP.search(path.name) and not liberado_d4:
        raise Blocked("Arquivo do 2T2026 bloqueado pela decisao D4.")
    rows: dict[tuple, dict] = {}
    with zipfile.ZipFile(path) as z:
        for name in z.namelist():
            m = NAME.match(name)
            if not m:
                continue
            uf, mun, zona, secao, kind = m.groups()
            key = (uf.upper(), str(int(mun)), str(int(zona)), str(int(secao)))
            row = rows.setdefault(key, {"uf": key[0], "municipio": key[1], "zona": key[2],
                                        "secao": key[3], "fonte_relogio": "urna (classe I)"})
            data = z.read(name)
            if kind == "imgbu.dat":
                text = data.decode("latin1")
                if turno_bu and turno_bu not in text:
                    raise Blocked("Imagem do BU sem a marca '" + turno_bu + "': recurso nao isolado.")
                row["abertura_bu"], row["fechamento_bu"] = imgbu_times(text)
                row.update(imgbu_votes(text, cargo))
                if cargo2:
                    row["votos_cargo2"] = imgbu_votes(text, cargo2)["votos_cargo"]
            else:
                with zipfile.ZipFile(io.BytesIO(data)) as inner:
                    text = inner.read("logd.dat").decode("latin1")
                lines = text.splitlines()
                if max_date:
                    check_isolation(lines, max_date)
                row.update(log_times(lines, date))
    return [rows[k] for k in sorted(rows)]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip", type=Path, required=True)
    p.add_argument("--data-eleicao", required=True, help="dd/mm/aaaa")
    p.add_argument("--cargo", default="PREFEITO", help="nome do cargo como impresso no BU")
    p.add_argument("--data-maxima", default="", help="dd/mm/aaaa; aborta se o log passar dela")
    p.add_argument("--turno-bu", default="", help="texto exigido na imagem do BU, ex.: '1º Turno'")
    p.add_argument("--cargo2", default="", help="segundo cargo, ex.: GOVERNADOR")
    p.add_argument("--liberado-d4", default="", help="referencia da decisao que liberou o 2T2026")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", args.data_eleicao):
        print("BLOQUEADO: data no formato dd/mm/aaaa", file=sys.stderr)
        return 2
    try:
        rows = extract(args.zip, args.data_eleicao, args.cargo.upper(), args.data_maxima, args.turno_bu,
                       args.cargo2.upper(), bool(args.liberado_d4))
    except (Blocked, OSError, zipfile.BadZipFile, KeyError) as e:
        print("BLOQUEADO:", e, file=sys.stderr)
        return 2
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with args.out.open("w", newline="", encoding="utf-8") as fp:
        w = csv.DictWriter(fp, fieldnames=OUT_FIELDS, extrasaction="ignore")
        w.writeheader()
        w.writerows(rows)
    print("OK:", len(rows), "secoes; horarios do relogio da urna (classe I)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""Extrai horarios por secao dos arquivos transmitidos para totalizacao (TSE).

Le o ZIP oficial "bu_imgbu_logjez_rdv_vscmr_<ano>_<turno>_<UF>.zip" e, para cada
secao, extrai da imagem do BU e do log da urna (log.jez -> logd.dat):

- abertura e fechamento da UE declarados na imagem do BU;
- primeiro e ultimo "O voto do eleitor foi computado" na data da eleicao;
- "Procedimento de encerramento confirmado" e geracao do bu.dat.

Todos esses horarios vem do RELOGIO DA PROPRIA URNA (classe I do pre-registro
E05-0). Nao sao fonte externa. Linhas com titulo de eleitor ou CPF nunca sao
copiadas para a saida. Bloqueia 2T2026 (decisao D4).
Biblioteca padrao Python 3.11+.
"""
from __future__ import annotations

import argparse
import csv
import io
import re
import sys
import zipfile
from pathlib import Path

NAME = re.compile(r"^o\d+([a-z]{2})(\d{5})(\d{4})(\d{4})-(log\.jez|imgbu\.dat)$")
BLOCKED_ZIP = re.compile(r"_2026_2t_", re.I)
OUT_FIELDS = ("uf", "municipio", "zona", "secao", "abertura_bu", "fechamento_bu",
              "primeiro_voto_log", "ultimo_voto_log", "encerramento_confirmado_log",
              "bu_gerado_log", "votos_computados_log", "fonte_relogio")


class Blocked(RuntimeError):
    pass


def imgbu_times(text: str) -> tuple[str, str]:
    a = re.search(r"Hor.rio de abertura\s+(\d{2}:\d{2}:\d{2})", text)
    f = re.search(r"Hor.rio de fechamento\s+(\d{2}:\d{2}:\d{2})", text)
    return (a.group(1) if a else "", f.group(1) if f else "")


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
    return {"primeiro_voto_log": min(votes) if votes else "",
            "ultimo_voto_log": max(votes) if votes else "",
            "encerramento_confirmado_log": closed, "bu_gerado_log": generated,
            "votos_computados_log": len(votes)}


def extract(path: Path, date: str) -> list[dict]:
    if BLOCKED_ZIP.search(path.name):
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
                row["abertura_bu"], row["fechamento_bu"] = imgbu_times(data.decode("latin1"))
            else:
                with zipfile.ZipFile(io.BytesIO(data)) as inner:
                    text = inner.read("logd.dat").decode("latin1")
                row.update(log_times(text.splitlines(), date))
    return [rows[k] for k in sorted(rows)]


def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--zip", type=Path, required=True)
    p.add_argument("--data-eleicao", required=True, help="dd/mm/aaaa")
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    if not re.fullmatch(r"\d{2}/\d{2}/\d{4}", args.data_eleicao):
        print("BLOQUEADO: data no formato dd/mm/aaaa", file=sys.stderr)
        return 2
    try:
        rows = extract(args.zip, args.data_eleicao)
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

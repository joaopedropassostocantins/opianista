#!/usr/bin/env python3
"""Pipeline fail-closed para validar CSV de voto por seção em 2T2024 / 1T2026.

Somente arquivos LOCAIS com manifesto de origem e SHA-256. Sem download.
Nunca abre 2T2026. Não executa teste confirmatório de horário sem fonte externa.
Biblioteca padrão Python 3.11+; nenhuma informação identificável de eleitor.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import re
import sys
import zipfile
from collections import defaultdict
from pathlib import Path

ALLOWED = {"2T2024": (2024, 2, 11), "1T2026": (2026, 1, 1)}
FIELDS = ("ANO_ELEICAO", "NR_TURNO", "SG_UF", "CD_MUNICIPIO",
          "NR_ZONA", "NR_SECAO", "CD_CARGO", "NR_VOTAVEL", "QT_VOTOS")
FILE_CAP = 1_500_000_000  # máximo explícito, recusar arquivo não verificado
BAD_PATTERN = re.compile(r"(?:^|[^A-Za-z0-9])2T[\s_-]*2026(?:$|[^A-Za-z0-9])|2026[\s_-]*2T", re.I)

class Blocked(RuntimeError):
    """Arquivo, origem, período ou contrato incompatível: não prosseguir."""

def guard_period(period: str, source: str = "") -> tuple[int, int, int]:
    if period not in ALLOWED:
        raise Blocked("Período bloqueado: somente 2T2024 e 1T2026 são permitidos.")
    if BAD_PATTERN.search(source):
        raise Blocked("Arquivo/manifesto menciona 2T2026; bloqueado pela decisão D4.")
    return ALLOWED[period]

def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for part in iter(lambda: fp.read(1024*1024), b""):
            h.update(part)
    return h.hexdigest()

def load_manifest(path: Path, period: str) -> dict:
    guard_period(period, str(path))
    obj = json.loads(path.read_text("utf-8"))
    if not isinstance(obj, dict):
        raise Blocked("Manifesto deve ser objeto JSON.")
    for k in ("period", "isolated", "sha256", "origin_url", "license", "resource_id"):
        if k not in obj:
            raise Blocked("Manifesto sem campo " + k)
    if obj["period"] != period or obj["isolated"] is not True:
        raise Blocked("Manifesto não comprova período ISOLADO e correspondente.")
    if not re.fullmatch(r"[0-9a-f]{64}", str(obj["sha256"])):
        raise Blocked("SHA-256 inválido.")
    if BAD_PATTERN.search(json.dumps(obj, ensure_ascii=False)):
        raise Blocked("Metadados incluem 2T2026: não abrir.")
    if not str(obj["origin_url"]).startswith("https://"):
        raise Blocked("Origem oficial HTTPS obrigatória.")
    return obj

def read_csv_text(path: Path, expected: str) -> str:
    if path.stat().st_size > FILE_CAP:
        raise Blocked("Arquivo muito grande; revisão manual.")
    if path.suffix.lower() == ".zip":
        with zipfile.ZipFile(path) as z:
            members = [x for x in z.infolist()
                       if not x.is_dir() and x.filename.lower().endswith(".csv")]
            if len(members) != 1:
                raise Blocked("ZIP precisa conter exatamente um CSV; escolha recurso isolado.")
            member = members[0]
            if BAD_PATTERN.search(member.filename) or member.file_size > FILE_CAP:
                raise Blocked("Membro bloqueado ou tamanho excessivo.")
            raw = z.read(member)
    elif path.suffix.lower() == ".csv":
        raw = path.read_bytes()
    else:
        raise Blocked("Somente .csv ou .zip com CSV único.")
    for encoding in ("utf-8-sig", "cp1252"):
        try:
            return raw.decode(encoding)
        except UnicodeDecodeError:
            pass
    raise Blocked("Codificação CSV desconhecida.")

def normalize(rows: list[dict], period: str) -> dict:
    year, turn, job = guard_period(period)
    grouped: dict[tuple, dict] = defaultdict(lambda: {
        "by_number": defaultdict(int), "blank": 0, "null": 0,
        "technical_null": 0, "other_valid": 0})
    seen = 0
    valid_ufs = set("AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO ZZ".split())
    for row in rows:
        seen += 1
        try:
            ry, rt, cargo = int(row["ANO_ELEICAO"]), int(row["NR_TURNO"]), int(row["CD_CARGO"])
            vote, qty = int(row["NR_VOTAVEL"]), int(row["QT_VOTOS"])
        except (KeyError, ValueError, TypeError) as e:
            raise Blocked("Campo obrigatório malformado.") from e
        # Testar período antes de selecionar cargo; CSV misto é rejeitado por inteiro.
        if ry != year or rt != turn:
            raise Blocked("CSV contém outro ano/turno (possível mistura 2T2026). Descartar.")
        if qty < 0 or vote < 0:
            raise Blocked("Votos negativos ou código inválido.")
        if cargo != job:
            continue
        uf = row["SG_UF"].strip().upper()
        if uf not in valid_ufs:
            raise Blocked("UF desconhecida.")
        key = (uf, row["CD_MUNICIPIO"].strip(), row["NR_ZONA"].strip(),
               row["NR_SECAO"].strip())
        if not all(key):
            raise Blocked("Identificador de seção incompleto.")
        v = grouped[key]
        if vote == 95:
            v["blank"] += qty
        elif vote == 96:
            v["null"] += qty
        elif vote == 97:
            v["technical_null"] += qty
        else:
            v["by_number"][vote] += qty
    sections = []
    for (uf, mun, zone, section), value in sorted(grouped.items()):
        by = dict(value["by_number"])
        total_valid = sum(by.values())
        total = total_valid + value["blank"] + value["null"] + value["technical_null"]
        sections.append({
            "uf":uf,"municipio":mun,"zona":zone,"secao":section,
            "votes_valid":total_valid,"votes_total":total,
            "blank":value["blank"],"null":value["null"],
            "technical_null":value["technical_null"],
            "votes_by_number":{str(k):by[k] for k in sorted(by)},
            "local_id":None,"closure_status":"indeterminado"
        })
    return {"period":period,"input_rows":seen,"sections":sections,
            "section_count":len(sections),
            "total_votes":sum(x["votes_total"] for x in sections),
            "total_valid":sum(x["votes_valid"] for x in sections),
            "temporal_test":"NAO_ESTIMAVEL_SEM_FONTE_EXTERNA_E_LOCAL_DE_VOTACAO"}

def parse_file(path: Path, manifest_path: Path, period: str) -> dict:
    guard_period(period, str(path))
    manifest = load_manifest(manifest_path, period)
    if not path.is_file():
        raise Blocked("CSV/ZIP inexistente.")
    found = sha256(path)
    if found != manifest["sha256"]:
        raise Blocked("SHA-256 não corresponde ao manifesto: abortar ANTES do parser.")
    text = read_csv_text(path, period)
    reader = csv.DictReader(io.StringIO(text), delimiter=";")
    if not reader.fieldnames or set(FIELDS) - set(reader.fieldnames):
        raise Blocked("CSV sem cabeçalho TSE obrigatório; recusar mapeamento presumido.")
    obj = normalize(list(reader), period)
    obj["provenance"] = {k:manifest[k] for k in ("period","origin_url","resource_id","license","sha256")}
    return obj

def main(argv=None) -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--period", required=True)
    p.add_argument("--csv", type=Path, required=True)
    p.add_argument("--manifest", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    args = p.parse_args(argv)
    try:
        obj = parse_file(args.csv, args.manifest, args.period)
        # Não fazer output parcial quando o contrato falhar.
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(json.dumps(obj, ensure_ascii=False, indent=2), "utf-8")
        print("OK:", obj["period"], obj["section_count"], "seções; teste de horário NÃO ESTIMÁVEL")
        return 0
    except (Blocked, OSError, csv.Error, json.JSONDecodeError, zipfile.BadZipFile) as e:
        print("BLOQUEADO:", e, file=sys.stderr)
        return 2

if __name__ == "__main__":
    raise SystemExit(main())

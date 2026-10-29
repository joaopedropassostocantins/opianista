#!/usr/bin/env python3
"""
Coleta inicial de fontes e arquivos eleitorais oficiais do TSE.

Etapa 1 do Estudo 03 - Hipótese do mesário pianista.

O script começa em modo de descoberta: consulta a API CKAN oficial do Portal
 de Dados Abertos do TSE, registra os conjuntos e recursos encontrados e não
baixa arquivos até que a opção --download seja informada.

Princípios:
- não presume URLs de recursos; URLs são obtidas da API e registradas;
- registra SHA-256 de cada arquivo baixado;
- não interpreta eventos de urna nem expõe dados pessoais;
- não substitui a validação humana das fontes, da licença ou da comparabilidade;
- usa somente a biblioteca padrão do Python 3.11+.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from dataclasses import dataclass, asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SEED = 20261025
DEFAULT_CKAN_ACTION = "https://dadosabertos.tse.jus.br/api/3/action"
DEFAULT_RESULTS_URL = "https://resultados.tse.jus.br/oficial/app/index.html"
DEFAULT_PERIODS = ("2T2026", "1T2026", "2T2022", "2T2018")
ALL_UFS = (
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG",
    "MS", "MT", "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR",
    "RS", "SC", "SE", "SP", "TO",
)
SEARCH_TERMS = {
    "2T2026": ("Resultados 2026", "Boletim de Urna 2026", "arquivos transmitidos 2026"),
    "1T2026": ("Resultados 2026", "Boletim de Urna 2026", "arquivos transmitidos 2026"),
    "2T2022": ("Resultados 2022", "Boletim de Urna 2022", "arquivos transmitidos 2022"),
    "2T2018": ("Resultados 2018", "Boletim de Urna 2018", "arquivos transmitidos 2018"),
}

USER_AGENT = "opianista-etapa1-coleta/0.1 (pesquisa reprodutivel; contato no repositorio)"


class CollectionError(RuntimeError):
    """Erro operacional que deve ser registrado sem inventar cobertura."""


@dataclass
class ResourceRecord:
    turno: str
    ano: str
    uf: str
    tipo: str
    conjunto: str
    recurso: str
    url: str
    arquivo_local: str
    sha256: str
    assinatura: str
    status: str
    observacao: str


@dataclass
class SourceRecord:
    consulta_utc: str
    periodo: str
    termo: str
    package_id: str
    package_name: str
    package_url: str
    resource_name: str
    resource_url: str
    resource_format: str
    resource_size: str
    license_id: str
    status: str
    observacao: str


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


def normalize_period(value: str) -> tuple[str, str]:
    match = re.fullmatch(r"([12])T(20\d{2})", value.upper().strip())
    if not match:
        raise argparse.ArgumentTypeError("período deve seguir o formato 1T2026 ou 2T2026")
    return match.group(1), match.group(2)


def normalize_ufs(value: str) -> tuple[str, ...]:
    if value.lower() == "todas":
        return ALL_UFS
    ufs = tuple(sorted({item.strip().upper() for item in value.split(",") if item.strip()}))
    invalid = sorted(set(ufs) - set(ALL_UFS))
    if invalid:
        raise argparse.ArgumentTypeError("UF(s) inválida(s): " + ", ".join(invalid))
    if not ufs:
        raise argparse.ArgumentTypeError("informe ao menos uma UF ou use 'todas'")
    return ufs


def api_url(action_base: str, action: str) -> str:
    return action_base.rstrip("/") + "/" + action.lstrip("/")


def request_json(url: str, timeout: int) -> dict[str, Any]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/json"})
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            payload = json.loads(response.read().decode("utf-8"))
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise CollectionError(f"falha na consulta oficial: {url}: {exc}") from exc
    if not payload.get("success"):
        raise CollectionError(f"API oficial retornou falha: {url}")
    return payload


def download_file(url: str, destination: Path, timeout: int, max_bytes: int | None) -> tuple[str, int]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    destination.parent.mkdir(parents=True, exist_ok=True)
    temporary = destination.with_suffix(destination.suffix + ".part")
    digest = hashlib.sha256()
    total = 0
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response, temporary.open("wb") as handle:
            while True:
                chunk = response.read(1024 * 1024)
                if not chunk:
                    break
                total += len(chunk)
                if max_bytes is not None and total > max_bytes:
                    raise CollectionError(f"arquivo excede --max-bytes: {url}")
                handle.write(chunk)
                digest.update(chunk)
        temporary.replace(destination)
    except Exception:
        temporary.unlink(missing_ok=True)
        raise
    return digest.hexdigest(), total


def safe_filename(value: str, fallback: str = "recurso") -> str:
    cleaned = re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")
    return cleaned[:180] or fallback


def infer_turn_year(period: str) -> tuple[str, str]:
    turn, year = normalize_period(period)
    return turn, year


def infer_type(name: str, package_name: str) -> str:
    text = f"{name} {package_name}".lower()
    if "registro digital" in text or re.search(r"\brdv\b", text):
        return "RDV"
    if "boletim" in text or re.search(r"\bbu\b", text):
        return "BU"
    if "log" in text:
        return "LOG"
    if "eleitor" in text:
        return "ELEITORADO"
    if "seç" in text or "sec" in text:
        return "SECOES"
    if "substit" in text or "conting" in text:
        return "SUBSTITUICAO"
    if "manual" in text:
        return "VOTACAO_MANUAL"
    if "ocorr" in text or "ata" in text:
        return "OCORRENCIAS"
    return "OUTRO"


def resource_matches_uf(resource: dict[str, Any], uf: str) -> bool:
    text = " ".join(str(resource.get(key, "")) for key in ("name", "description", "url")).upper()
    return bool(re.search(rf"(?:^|[^A-Z]){re.escape(uf)}(?:$|[^A-Z])", text))


def iter_packages(action_base: str, term: str, rows: int, timeout: int) -> Iterable[dict[str, Any]]:
    query = urllib.parse.urlencode({"q": term, "rows": rows})
    payload = request_json(api_url(action_base, "package_search") + "?" + query, timeout)
    yield from payload["result"].get("results", [])


def discover(
    action_base: str,
    periods: tuple[str, ...],
    ufs: tuple[str, ...],
    rows: int,
    timeout: int,
) -> tuple[list[SourceRecord], list[dict[str, Any]]]:
    timestamp = utc_now()
    records: list[SourceRecord] = []
    packages: list[dict[str, Any]] = []
    seen_packages: set[str] = set()
    for period in periods:
        for term in SEARCH_TERMS[period]:
            for package in iter_packages(action_base, term, rows, timeout):
                package_id = str(package.get("id", ""))
                if not package_id or package_id in seen_packages:
                    continue
                seen_packages.add(package_id)
                packages.append(package)
                package_url = package.get("url") or ""
                if not package_url:
                    package_url = "https://dadosabertos.tse.jus.br/dataset/" + str(package.get("name", ""))
                resources = package.get("resources", [])
                for resource in resources:
                    resource_url = str(resource.get("url", ""))
                    if not resource_url:
                        continue
                    selected_ufs = [uf for uf in ufs if resource_matches_uf(resource, uf)]
                    uf_value = ",".join(selected_ufs) if selected_ufs else "TODAS_OU_NAO_IDENTIFICADA"
                    records.append(SourceRecord(
                        consulta_utc=timestamp,
                        periodo=period,
                        termo=term,
                        package_id=package_id,
                        package_name=str(package.get("title") or package.get("name") or ""),
                        package_url=package_url,
                        resource_name=str(resource.get("name") or ""),
                        resource_url=resource_url,
                        resource_format=str(resource.get("format") or ""),
                        resource_size=str(resource.get("size") or ""),
                        license_id=str(package.get("license_id") or package.get("license_title") or ""),
                        status="DESCOBERTO",
                        observacao=f"UF(s) inferidas apenas pelo nome/descrição: {uf_value}; validar manualmente.",
                    ))
    return records, packages


def write_csv(path: Path, rows: Iterable[Any]) -> None:
    rows = list(rows)
    path.parent.mkdir(parents=True, exist_ok=True)
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    fieldnames = list(asdict(rows[0]).keys())
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(asdict(row) for row in rows)


def write_sources(path: Path, records: list[SourceRecord], action_base: str, results_url: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as handle:
        handle.write("# Fontes descobertas — Etapa 1\n\n")
        handle.write(f"Consulta UTC: `{utc_now()}`\n\n")
        handle.write("Portal CKAN consultado: " + action_base + "\n\n")
        handle.write("Portal Resultados para validação complementar: " + results_url + "\n\n")
        handle.write("As URLs abaixo foram retornadas pela API oficial. A presença de uma URL não comprova ainda integridade, comparabilidade, cobertura ou licença suficiente.\n\n")
        for index, record in enumerate(records, start=1):
            handle.write(f"{index}. **{record.periodo} — {record.package_name} — {record.resource_name or '(sem nome)'}**\n")
            handle.write(f"   - Conjunto: {record.package_url}\n")
            handle.write(f"   - Recurso: {record.resource_url}\n")
            handle.write(f"   - Formato: `{record.resource_format}`; tamanho informado: `{record.resource_size}`\n")
            handle.write(f"   - Licença declarada: `{record.license_id or 'não informada'}`\n")
            handle.write(f"   - Status: `{record.status}`; {record.observacao}\n\n")
        if not records:
            handle.write("Nenhum recurso foi descoberto. Registrar o erro de consulta antes de prosseguir.\n")


def maybe_download(
    records: list[SourceRecord],
    download_dir: Path,
    inventory_path: Path,
    timeout: int,
    max_bytes: int | None,
) -> list[ResourceRecord]:
    inventory: list[ResourceRecord] = []
    seen_urls: set[str] = set()
    for record in records:
        if record.resource_url in seen_urls:
            continue
        seen_urls.add(record.resource_url)
        filename = safe_filename(Path(urllib.parse.urlparse(record.resource_url).path).name or record.resource_name)
        turn, year = infer_turn_year(record.periodo)
        destination = download_dir / year / f"{turn}T" / filename
        signature_status = "NAO_VERIFICADA"
        status = "DESCOBERTO_NAO_BAIXADO"
        sha256 = ""
        observation = record.observacao
        try:
            sha256, byte_count = download_file(record.resource_url, destination, timeout, max_bytes)
            status = "BAIXADO"
            observation = f"bytes={byte_count}; " + observation
        except CollectionError as exc:
            status = "ERRO_DOWNLOAD"
            observation = f"{observation} Erro: {exc}"
        inventory.append(ResourceRecord(
            turno=turn,
            ano=year,
            uf="TODAS_OU_NAO_IDENTIFICADA",
            tipo=infer_type(record.resource_name, record.package_name),
            conjunto=record.package_name,
            recurso=record.resource_name,
            url=record.resource_url,
            arquivo_local=str(destination) if status == "BAIXADO" else "",
            sha256=sha256,
            assinatura=signature_status,
            status=status,
            observacao=observation,
        ))
    write_csv(inventory_path, inventory)
    return inventory


def write_discovery_inventory(path: Path, records: list[SourceRecord]) -> None:
    rows = [ResourceRecord(
        turno=infer_turn_year(record.periodo)[0],
        ano=infer_turn_year(record.periodo)[1],
        uf="TODAS_OU_NAO_IDENTIFICADA",
        tipo=infer_type(record.resource_name, record.package_name),
        conjunto=record.package_name,
        recurso=record.resource_name,
        url=record.resource_url,
        arquivo_local="",
        sha256="",
        assinatura="NAO_VERIFICADA",
        status="DESCOBERTO_NAO_BAIXADO",
        observacao=record.observacao,
    ) for record in records]
    write_csv(path, rows)


def parse_args(argv: list[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--portal-api", default=DEFAULT_CKAN_ACTION, help="URL da API CKAN oficial")
    parser.add_argument("--resultados-url", default=DEFAULT_RESULTS_URL, help="URL oficial do Portal Resultados")
    parser.add_argument("--uf", default="todas", help="todas ou lista separada por vírgulas, por exemplo TO,AC")
    parser.add_argument("--periodos", default=",".join(DEFAULT_PERIODS), help="períodos separados por vírgula")
    parser.add_argument("--rows", type=int, default=50, help="máximo de conjuntos por consulta")
    parser.add_argument("--timeout", type=int, default=60, help="timeout de cada requisição, em segundos")
    parser.add_argument("--max-bytes", type=int, default=None, help="limite opcional por arquivo baixado")
    parser.add_argument("--download", action="store_true", help="baixar recursos descobertos; sem isso, apenas descobrir")
    parser.add_argument("--output-dir", type=Path, default=Path(__file__).resolve().parent, help="diretório de saídas")
    parser.add_argument("--data-dir", type=Path, default=None, help="diretório dos arquivos baixados")
    parser.add_argument("--user-agent", default=USER_AGENT, help=argparse.SUPPRESS)
    return parser.parse_args(argv)


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv or sys.argv[1:])
    ufs = normalize_ufs(args.uf)
    periods = tuple(item.strip().upper() for item in args.periodos.split(",") if item.strip())
    for period in periods:
        normalize_period(period)
        if period not in SEARCH_TERMS:
            raise SystemExit(f"período sem estratégia de descoberta: {period}")
    # D4 do PLANEJAMENTO: um recurso de 2026 pode misturar 1T/2T.
    # Nunca permitir download a partir das buscas ambíguas deste coletor.
    if args.download and any(p in ("2T2026", "1T2026") for p in periods):
        raise SystemExit("BLOQUEADO D4: download de 2026 (1T ou 2T) por busca CKAN ambígua. "
                         "Use pipeline_placebo.py com arquivo de 1T isolado e manifesto SHA-256; "
                         "2T2026 segue vedado até GATE 1.6.")
    if args.rows < 1 or args.timeout < 1:
        raise SystemExit("--rows e --timeout devem ser positivos")

    output_dir = args.output_dir.resolve()
    data_dir = (args.data_dir or Path(__file__).resolve().parents[4] / "data" / "coleta_03").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"Consulta oficial: {args.portal_api}")
    print(f"Escopo UF: {','.join(ufs)}; períodos: {','.join(periods)}; seed: {SEED}")
    try:
        source_records, packages = discover(args.portal_api, periods, ufs, args.rows, args.timeout)
    except CollectionError as exc:
        error_path = output_dir / "erro_coleta.txt"
        error_path.write_text(f"UTC: {utc_now()}\nErro: {exc}\n", encoding="utf-8")
        print(f"ERRO: {exc}", file=sys.stderr)
        return 2

    sources_path = output_dir / "fontes.md"
    inventory_path = output_dir / "inventario.csv"
    write_sources(sources_path, source_records, args.portal_api, args.resultados_url)
    if args.download:
        inventory = maybe_download(
            source_records,
            data_dir,
            inventory_path,
            args.timeout,
            args.max_bytes,
        )
    else:
        write_discovery_inventory(inventory_path, source_records)
        inventory = []

    metadata_path = output_dir / "descoberta.json"
    metadata_path.write_text(json.dumps({
        "consulta_utc": utc_now(),
        "seed": SEED,
        "portal_api": args.portal_api,
        "portal_resultados": args.resultados_url,
        "ufs": list(ufs),
        "periodos": list(periods),
        "modo": "download" if args.download else "discovery_only",
        "pacotes": packages,
        "recursos_encontrados": len(source_records),
        "recursos_baixados": len([row for row in inventory if row.status == "BAIXADO"]),
        "observacao": "Metadados e URLs ainda exigem validação humana; cobertura inferior a 95% deve interromper a Etapa 1.",
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Recursos descobertos: {len(source_records)}")
    print(f"Inventário: {inventory_path}")
    print(f"Fontes: {sources_path}")
    print(f"Metadados: {metadata_path}")
    if not args.download:
        print("Modo discovery-only: use --download somente após validar fontes, licenças e escopo.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

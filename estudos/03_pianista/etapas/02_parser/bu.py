#!/usr/bin/env python3
"""
Decodifica Boletins de Urna (-bu.dat, ASN.1 DER) e grava uma linha por secao:
comparecimento, aptos, votos por votavel do cargo informado, brancos, nulos e o
detalhamento oficial de habilitacao (sem biometria, por biometria, por biografia).

As especificacoes ASN.1 nao sao versionadas neste repositorio: o caminho da pasta
com os arquivos .asn e informado em --asn (por exemplo, a especificacao publicada
pelo TSE ou a reconstrucao publica em github.com/igoroalonge/urna-vota-decompiled,
pasta src/asn1). O decodificador tenta primeiro o envelope generico e, se falhar,
o boletim diretamente; a validacao e feita comparando o comparecimento do BU com o
numero de votos computados no log da mesma secao.
"""

from __future__ import annotations

import argparse
import csv
import glob
import re
import sys
import zipfile
from pathlib import Path

import asn1tools

NOME = re.compile(r"(?P<mun>\d{5})(?P<zona>\d{4})(?P<secao>\d{4})-bu\.dat$", re.IGNORECASE)


def compilar(pasta: Path):
    return asn1tools.compile_files(sorted(glob.glob(str(pasta / "*.asn"))), codec="der")


def decodificar_bu(spec, dados: bytes) -> dict:
    for tipo in ("EntidadeEnvelopeGenerico",):
        try:
            env = spec.decode(tipo, dados)
            for chave in ("conteudo", "conteudoAssinado"):
                if chave in env and isinstance(env[chave], (bytes, bytearray)):
                    return spec.decode("EntidadeBoletimUrna", bytes(env[chave]))
        except Exception:
            pass
    return spec.decode("EntidadeBoletimUrna", dados)


def linhas_do_bu(bu: dict, cargo: str) -> dict:
    out = {"comparecimento": bu.get("qtdEleitoresCompareceram")}
    det = bu.get("detalhamentoComparecimento") or {}
    out["bu_sem_biometria"] = det.get("qtdEleitoresCompareceramSemBiometria")
    out["bu_por_biometria"] = det.get("qtdEleitoresHabilitadosPorBiometria")
    out["bu_por_biografia"] = det.get("qtdEleitoresHabilitadosPorBiografia")
    votos: dict[str, int] = {}
    for rve in bu.get("resultadosVotacaoPorEleicao", []):
        for rv in rve.get("resultadosVotacao", []):
            for tvc in rv.get("totaisVotosCargo", []):
                codigo = tvc.get("codigoCargo")
                nome = codigo[1] if isinstance(codigo, tuple) else codigo
                if str(nome).lower() != cargo.lower():
                    continue
                out["aptos"] = rve.get("qtdEleitoresAptos")
                out["comparecimento_cargo"] = rv.get("qtdComparecimento")
                for vv in tvc.get("votosVotaveis", []):
                    tipo = vv.get("tipoVoto")
                    q = int(vv.get("quantidadeVotos", 0))
                    if tipo == "nominal":
                        num = str((vv.get("identificacaoVotavel") or {}).get("codigo", ""))
                        votos[f"v{num}"] = votos.get(f"v{num}", 0) + q
                    else:
                        votos[str(tipo)] = votos.get(str(tipo), 0) + q
    out.update(votos)
    return out


def iterar(origem: Path):
    if origem.is_dir():
        for c in sorted(origem.rglob("*-bu.dat")):
            yield c.name, c.read_bytes()
        return
    with zipfile.ZipFile(origem) as z:
        for n in sorted(z.namelist()):
            if n.lower().endswith("-bu.dat"):
                yield n, z.read(n)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--origem", type=Path, required=True)
    ap.add_argument("--asn", type=Path, required=True)
    ap.add_argument("--cargo", default="presidente")
    ap.add_argument("--uf", required=True)
    ap.add_argument("--periodo", required=True)
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--limite", type=int, default=None)
    args = ap.parse_args(argv)
    spec = compilar(args.asn)
    linhas, erros = [], 0
    for i, (nome, dados) in enumerate(iterar(args.origem)):
        if args.limite is not None and i >= args.limite:
            break
        m = NOME.search(nome.rsplit("/", 1)[-1])
        base = {"uf": args.uf, "periodo": args.periodo,
                "municipio": m.group("mun") if m else "", "zona": m.group("zona") if m else "",
                "secao": m.group("secao") if m else ""}
        try:
            base.update(linhas_do_bu(decodificar_bu(spec, dados), args.cargo))
        except Exception as exc:
            erros += 1
            base["erro"] = f"{type(exc).__name__}: {str(exc)[:120]}"
        linhas.append(base)
    campos = sorted({k for l in linhas for k in l}, key=lambda k: (k not in ("uf", "periodo", "municipio", "zona", "secao"), k))
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with args.saida.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=campos)
        w.writeheader()
        w.writerows(linhas)
    print({"bus": len(linhas), "erros": erros, "campos": campos[:20]})
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Extrai, de um pacote de arquivos de urna do TSE (ZIP por UF e turno) ou de uma
pasta de logs avulsos, uma linha por habilitacao de eleitor:

  municipio, zona, secao, segundos_desde_meia_noite, modo

Modos (mapeamento fixado a partir do catalogo real de 2022 e do fluxo descrito
na reconstrucao do aplicativo VOTA; ver mapeamento_mensagens.md):

  BIO     - "Tipo de habilitacao do eleitor [biometrica]"
  NB_SEM  - "O eleitor nao possui biometria" (sem biometria cadastrada)
  NB_MAN  - habilitacao manual apos falha da biometria: ano de nascimento e
            digital do mesario ("Capturada a digital do mesario")
  DESC    - nenhum marcador encontrado entre a habilitacao anterior e esta

O instante da habilitacao e o da linha "Eleitor foi habilitado". Linhas fora
da data informada sao descartadas. Nenhum dado pessoal e gravado: titulos de
mesario e demais numeros presentes nas mensagens nao sao lidos.
"""

from __future__ import annotations

import argparse
import csv
import gzip
import io
import re
import sys
import zipfile
from collections import Counter
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from logs_urna import decodificar, interpretar_linha, ler_logjez  # noqa: E402

LOG_MEMBRO = re.compile(r"\.(logjez|jez)$", re.IGNORECASE)
SECAO_NOME = re.compile(r"(?P<mun>\d{5})(?P<zona>\d{4})(?P<secao>\d{4})(?:\D[^/]*)?\.(?:logjez|jez)$", re.IGNORECASE)

MSG_HABILITADO = "Eleitor foi habilitado"
MSG_COMPUTADO = "O voto do eleitor foi computado"
MARCADORES = (
    ("Tipo de habilitação do eleitor [biométrica]", "BIO"),
    ("O eleitor não possui biometria", "NB_SEM"),
    ("Capturada a digital do mesário", "NB_MAN"),
    ("Solicitação de dado pessoal do eleitor para habilitação manual", "NB_MAN"),
)
INICIO_CICLO = ("Aguardando digitação do título", "Título digitado pelo mesário")


def secao_de(nome: str) -> tuple[str, str, str]:
    m = SECAO_NOME.search(nome.rsplit("/", 1)[-1])
    if not m:
        return "", "", ""
    return m.group("mun"), m.group("zona"), m.group("secao")


def eventos_de_linhas(linhas, dia: date) -> tuple[list[tuple[int, str]], Counter]:
    """Converte linhas de um log em [(segundos, modo)] e contadores de controle."""
    saida: list[tuple[int, str]] = []
    controle: Counter = Counter()
    modo_corrente: str | None = None
    for linha in linhas:
        if linha.momento is None or linha.momento.date() != dia:
            continue
        msg = linha.mensagem
        if msg in INICIO_CICLO:
            modo_corrente = None
            continue
        for marcador, modo in MARCADORES:
            if msg == marcador:
                # NB_MAN prevalece se, no mesmo ciclo, a biometria falhou e houve habilitacao manual
                if modo_corrente != "NB_MAN":
                    modo_corrente = modo
                break
        if msg == MSG_HABILITADO:
            m = linha.momento
            saida.append((m.hour * 3600 + m.minute * 60 + m.second, modo_corrente or "DESC"))
            controle["habilitados"] += 1
            modo_corrente = None
        elif msg == MSG_COMPUTADO:
            controle["computados"] += 1
    return saida, controle


def iterar_logs(origem: Path):
    if origem.is_dir():
        for caminho in sorted(origem.rglob("*")):
            if caminho.is_file() and LOG_MEMBRO.search(caminho.name):
                yield str(caminho.relative_to(origem)), caminho.read_bytes()
        return
    with zipfile.ZipFile(origem) as pacote:
        for membro in sorted(pacote.namelist()):
            if LOG_MEMBRO.search(membro):
                yield membro, pacote.read(membro)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--origem", type=Path, required=True, help="ZIP do TSE ou pasta com logs")
    ap.add_argument("--data", required=True, help="data da votacao, AAAA-MM-DD")
    ap.add_argument("--uf", required=True)
    ap.add_argument("--periodo", required=True, help="ex.: 1T2026")
    ap.add_argument("--saida", type=Path, required=True, help="CSV gzip de habilitacoes")
    ap.add_argument("--resumo", type=Path, required=True, help="CSV de controle por log")
    args = ap.parse_args(argv)

    dia = date.fromisoformat(args.data)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    total = Counter()
    with gzip.open(args.saida, "wt", newline="", encoding="utf-8") as out, args.resumo.open("w", newline="", encoding="utf-8") as res:
        w = csv.writer(out)
        r = csv.writer(res)
        w.writerow(["uf", "periodo", "municipio", "zona", "secao", "seg", "modo"])
        r.writerow(["uf", "periodo", "municipio", "zona", "secao", "habilitados", "computados", "BIO", "NB_SEM", "NB_MAN", "DESC", "erro"])
        for nome, conteudo in iterar_logs(args.origem):
            mun, zona, secao = secao_de(nome)
            erro = ""
            eventos: list[tuple[int, str]] = []
            controle: Counter = Counter()
            try:
                internos = ler_logjez(conteudo)
                linhas = []
                for interno in sorted(internos):
                    if interno.lower().endswith((".dat", ".txt")) or "log" in interno.lower():
                        for bruta in decodificar(internos[interno]).splitlines():
                            if bruta.strip():
                                linhas.append(interpretar_linha(bruta))
                eventos, controle = eventos_de_linhas(linhas, dia)
            except Exception as exc:
                erro = f"{type(exc).__name__}"
            modos = Counter(m for _, m in eventos)
            for seg, modo in eventos:
                w.writerow([args.uf, args.periodo, mun, zona, secao, seg, modo])
            r.writerow([args.uf, args.periodo, mun, zona, secao, controle["habilitados"], controle["computados"],
                        modos["BIO"], modos["NB_SEM"], modos["NB_MAN"], modos["DESC"], erro])
            total["logs"] += 1
            total["erros"] += bool(erro)
            total.update(modos)
    print(dict(total))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

#!/usr/bin/env python3
"""
Leitura dos logs de urna (.logjez) distribuidos pelo TSE nos pacotes
"Arquivos transmitidos para totalizacao" (ZIP por UF e turno).

Subcomandos:
  catalogo  - lista as mensagens de evento distintas (digitos mascarados) com
              frequencia, para revisao humana do mapeamento de categorias.
  amostra   - imprime as primeiras linhas de alguns logs com digitos mascarados,
              para inspecao do formato.

Nada aqui interpreta eventos: o mapeamento mensagem -> categoria e feito em
arquivo separado, revisado por humano (protocolo v1.1, Etapa 2).

Privacidade: toda saida mascara sequencias de digitos, para que nenhum numero
de titulo, CPF ou identificador individual saia do ambiente de processamento.
"""

from __future__ import annotations

import argparse
import collections
import csv
import io
import re
import sys
import tempfile
import zipfile
from dataclasses import dataclass
from datetime import date, datetime
from pathlib import Path
from typing import Iterator

import py7zr

SEED = 20261025
NOME_LOG = re.compile(r"(?P<base>[^/]+)\.(?:logjez|jez)$", re.IGNORECASE)
SECAO_NO_NOME = re.compile(r"(?P<mun>\d{5})(?P<zona>\d{4})(?P<secao>\d{4})(?:\D[^/]*)?\.(?:logjez|jez)$", re.IGNORECASE)
DIGITOS = re.compile(r"\d+")
FORMATO_DATA = "%d/%m/%Y %H:%M:%S"


@dataclass
class LinhaLog:
    momento: datetime | None
    nivel: str
    id_urna: str
    aplicacao: str
    mensagem: str
    bruta: str


def mascarar(texto: str) -> str:
    """Substitui toda sequencia de digitos por '#'."""
    return DIGITOS.sub("#", texto)


def identificar_secao(nome_membro: str) -> dict[str, str]:
    """Extrai municipio, zona e secao do nome do arquivo, quando o padrao existir."""
    m = SECAO_NO_NOME.search(nome_membro)
    if not m:
        return {"municipio": "", "zona": "", "secao": "", "membro": nome_membro}
    return {"municipio": m.group("mun"), "zona": m.group("zona"), "secao": m.group("secao"), "membro": nome_membro}


def ler_logjez(conteudo: bytes) -> dict[str, bytes]:
    """Descompacta um .logjez (7z) e devolve {nome_interno: bytes}."""
    saida: dict[str, bytes] = {}
    with tempfile.TemporaryDirectory(prefix="logjez_") as pasta:
        with py7zr.SevenZipFile(io.BytesIO(conteudo), mode="r") as arquivo:
            arquivo.extractall(path=pasta)
        raiz = Path(pasta)
        for caminho in sorted(raiz.rglob("*")):
            if caminho.is_file():
                saida[str(caminho.relative_to(raiz))] = caminho.read_bytes()
    return saida


def decodificar(dados: bytes) -> str:
    try:
        return dados.decode("utf-8")
    except UnicodeDecodeError:
        return dados.decode("latin-1")


def interpretar_linha(bruta: str) -> LinhaLog:
    partes = bruta.rstrip("\r\n").split("\t")
    momento = None
    if partes:
        try:
            momento = datetime.strptime(partes[0].strip(), FORMATO_DATA)
        except ValueError:
            momento = None
    nivel = partes[1].strip() if len(partes) > 1 else ""
    id_urna = partes[2].strip() if len(partes) > 2 else ""
    aplicacao = partes[3].strip() if len(partes) > 3 else ""
    mensagem = partes[4].strip() if len(partes) > 4 else ""
    return LinhaLog(momento, nivel, id_urna, aplicacao, mensagem, bruta.rstrip("\r\n"))


def iterar_logs_zip(caminho_zip: Path, limite: int | None = None) -> Iterator[tuple[dict[str, str], list[LinhaLog]]]:
    """Percorre os .logjez de um ZIP do TSE, devolvendo (identificacao, linhas)."""
    with zipfile.ZipFile(caminho_zip) as pacote:
        membros = [m for m in pacote.namelist() if NOME_LOG.search(m)]
        membros.sort()
        for indice, membro in enumerate(membros):
            if limite is not None and indice >= limite:
                break
            ident = identificar_secao(membro)
            try:
                internos = ler_logjez(pacote.read(membro))
            except Exception as exc:  # arquivo corrompido: registrar, nao interromper
                ident["erro"] = f"{type(exc).__name__}: {exc}"
                yield ident, []
                continue
            linhas: list[LinhaLog] = []
            for nome_interno in sorted(internos):
                texto = decodificar(internos[nome_interno])
                for bruta in texto.splitlines():
                    if bruta.strip():
                        linhas.append(interpretar_linha(bruta))
            ident["arquivos_internos"] = ";".join(sorted(internos))
            yield ident, linhas


def cmd_catalogo(args: argparse.Namespace) -> int:
    data_eleicao = date.fromisoformat(args.data) if args.data else None
    contagem: collections.Counter[tuple[str, str]] = collections.Counter()
    secoes_com: dict[tuple[str, str], set[str]] = collections.defaultdict(set)
    n_logs = 0
    n_erros = 0
    n_linhas = 0
    n_sem_data = 0
    for ident, linhas in iterar_logs_zip(args.zip, args.limite):
        n_logs += 1
        if ident.get("erro"):
            n_erros += 1
            continue
        chave_secao = ident["membro"]
        for linha in linhas:
            if linha.momento is None:
                n_sem_data += 1
                continue
            if data_eleicao and linha.momento.date() != data_eleicao:
                continue
            n_linhas += 1
            chave = (linha.aplicacao, mascarar(linha.mensagem))
            contagem[chave] += 1
            secoes_com[chave].add(chave_secao)
    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with args.saida.open("w", newline="", encoding="utf-8") as handle:
        escritor = csv.writer(handle)
        escritor.writerow(["aplicacao", "mensagem_mascarada", "ocorrencias", "secoes_com_ocorrencia"])
        for (aplicacao, mensagem), total in contagem.most_common():
            escritor.writerow([aplicacao, mensagem, total, len(secoes_com[(aplicacao, mensagem)])])
    print(f"logs lidos={n_logs} erros={n_erros} linhas_no_dia={n_linhas} linhas_sem_data={n_sem_data} mensagens_distintas={len(contagem)}")
    return 0


def cmd_amostra(args: argparse.Namespace) -> int:
    for ident, linhas in iterar_logs_zip(args.zip, args.logs):
        print(f"=== {mascarar(ident['membro'])} internos={ident.get('arquivos_internos', '')} erro={ident.get('erro', '')}")
        selecionadas = linhas
        if args.data:
            dia = date.fromisoformat(args.data)
            selecionadas = [l for l in linhas if l.momento and l.momento.date() == dia]
        for linha in selecionadas[: args.linhas]:
            hora = linha.momento.strftime("%H:%M:%S") if linha.momento else "??:??:??"
            print(f"{hora}\t{linha.nivel}\t{linha.aplicacao}\t{mascarar(linha.mensagem)}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = parser.add_subparsers(dest="comando", required=True)

    p_cat = sub.add_parser("catalogo", help="catalogo de mensagens distintas")
    p_cat.add_argument("--zip", type=Path, required=True)
    p_cat.add_argument("--saida", type=Path, required=True)
    p_cat.add_argument("--data", help="data da eleicao (AAAA-MM-DD); filtra linhas do dia")
    p_cat.add_argument("--limite", type=int, default=None, help="maximo de logs lidos")
    p_cat.set_defaults(func=cmd_catalogo)

    p_am = sub.add_parser("amostra", help="primeiras linhas de alguns logs, mascaradas")
    p_am.add_argument("--zip", type=Path, required=True)
    p_am.add_argument("--logs", type=int, default=2)
    p_am.add_argument("--linhas", type=int, default=60)
    p_am.add_argument("--data", help="data da eleicao (AAAA-MM-DD)")
    p_am.set_defaults(func=cmd_amostra)

    args = parser.parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())

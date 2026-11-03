#!/usr/bin/env python3
"""Diagnostico descritivo de habilitacoes ao longo de TODO o dia (sem limite 17h/19h).

Esta ferramenta NAO executa testes confirmatorios do Estudo 03 e NAO abre
dados do 2T2026. Usa CSV normalizado de periodo historico autorizado, com
origem revisada e hash conferido. Nao atribui voto ou identidade a horario.
"""
from __future__ import annotations

import argparse
import csv
import gzip
import hashlib
import json
import re
from collections import Counter, defaultdict
from pathlib import Path

PERIODOS_PERMITIDOS = frozenset({"SINTETICO", "1T2026", "1T2022", "2T2022", "2T2024"})
MODOS = frozenset({"BIO", "NB_SEM", "NB_MAN", "DESC"})
OBRIGATORIOS = frozenset({"uf", "periodo", "municipio", "zona", "secao", "seg", "modo"})

class Bloqueado(ValueError):
    """Dados nao elegiveis ou estrutura invalida: abortar, sem saida parcial."""


def validar_preflight(periodo: str, caminho: Path) -> None:
    """Checagem antes de abrir conteudo; NAO certifica proveniencia da fonte."""
    if periodo not in PERIODOS_PERMITIDOS:
        raise Bloqueado("Periodo vedado ou desconhecido; 2T2026 requer nova aprovacao.")
    rotulo = re.sub(r"[^a-z0-9]", "", str(caminho).lower())
    if "2t2026" in rotulo or "20262t" in rotulo:
        raise Bloqueado("Referencia a 2T2026: bloqueio preventivo.")


def contar_rajadas(eventos: list[tuple[int, str]], dt: float) -> int:
    """Sequencias de 3+ NB conhecidas, consecutivas e separadas por <= dt segundos."""
    if dt < 0:
        raise Bloqueado("dt* precisa ser nao negativo.")
    grupos, tamanho, anterior = 0, 0, None
    for segundo, modo in eventos:
        if modo not in ("NB_SEM", "NB_MAN"):
            if tamanho >= 3:
                grupos += 1
            tamanho, anterior = 0, None
            continue
        if tamanho and anterior is not None and 0 <= segundo - anterior <= dt:
            tamanho += 1
        else:
            if tamanho >= 3:
                grupos += 1
            tamanho = 1
        anterior = segundo
    return grupos + int(tamanho >= 3)


def analisar_linhas(linhas, periodo: str, dt: float | None = None) -> dict:
    if periodo not in PERIODOS_PERMITIDOS:
        raise Bloqueado("Periodo bloqueado ANTES da leitura de registros.")
    secoes = defaultdict(list)
    for linha in linhas:
        if linha.get("periodo") != periodo:
            raise Bloqueado("Mistura de periodos: recusar dataset completo.")
        if not OBRIGATORIOS.issubset(linha):
            raise Bloqueado("Campos essenciais ausentes.")
        try:
            segundo = int(linha["seg"])
        except (TypeError, ValueError) as exc:
            raise Bloqueado("Segundo malformado.") from exc
        if not 0 <= segundo < 86400:
            raise Bloqueado("Segundo fora do dia civil; requer tratamento de data.")
        modo = linha["modo"]
        if modo not in MODOS:
            raise Bloqueado("Modalidade nao reconhecida; nao inferir biometria.")
        chave = tuple(linha[k] for k in ("uf", "municipio", "zona", "secao"))
        if not all(chave):
            raise Bloqueado("Identificacao de secao incompleta.")
        secoes[chave].append((segundo, modo))
    relatorio = []
    for chave, eventos in sorted(secoes.items()):
        eventos.sort(key=lambda e: e[0])
        contagens = Counter(m for _, m in eventos)
        por_hora = defaultdict(lambda: {"habilitacoes": 0, "nb_observadas": 0, "desc": 0})
        for segundo, modo in eventos:
            r = por_hora[f"{segundo // 3600:02d}"]
            r["habilitacoes"] += 1
            r["nb_observadas"] += int(modo in ("NB_SEM", "NB_MAN"))
            r["desc"] += int(modo == "DESC")
        relatorio.append({
            "secao": dict(zip(("uf", "municipio", "zona", "secao"), chave)),
            "primeira_habilitacao_seg": eventos[0][0],
            "ultima_habilitacao_seg": eventos[-1][0],
            "eventos_habilitacao_dia_inteiro": len(eventos),
            "bio": contagens["BIO"],
            "sem_biometria_observada": contagens["NB_SEM"] + contagens["NB_MAN"],
            "modo_indeterminado": contagens["DESC"],
            "horas": dict(sorted(por_hora.items())),
            "registros_no_mesmo_segundo": sum(eventos[i][0] == eventos[i-1][0] for i in range(1, len(eventos))),
            "rajadas_nb": contar_rajadas(eventos, dt) if dt is not None else None,
        })
    return {
        "periodo": periodo,
        "tipo": "DESCRITIVO_EXPLORATORIO_NAO_CONFIRMATORIO",
        "limite": "Primeiro/ultimo evento de habilitacao, NAO horario do ultimo voto.",
        "cobertura": "Nao certificada sem reconciliacao com BU, log completo e abertura da secao.",
        "dtstar": dt,
        "secoes": relatorio,
        "total_secoes": len(relatorio),
        "total_habilitacoes": sum(x["eventos_habilitacao_dia_inteiro"] for x in relatorio),
        "total_modo_indeterminado": sum(x["modo_indeterminado"] for x in relatorio),
    }


def sha256(caminho: Path) -> str:
    h = hashlib.sha256()
    with caminho.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--entrada", type=Path, required=True)
    parser.add_argument("--periodo", required=True)
    parser.add_argument("--sha256", required=True, help="Hash de fonte externa validada, nao autodeclarada.")
    parser.add_argument("--dtstar", type=float)
    parser.add_argument("--saida", type=Path, required=True)
    args = parser.parse_args()
    try:
        validar_preflight(args.periodo, args.entrada)
        if not re.fullmatch(r"[0-9a-f]{64}", args.sha256):
            raise Bloqueado("Hash SHA-256 obrigatorio.")
        if sha256(args.entrada) != args.sha256:
            raise Bloqueado("Hash divergente; abortar antes do parser.")
        op = gzip.open if str(args.entrada).endswith(".gz") else open
        with op(args.entrada, "rt", encoding="utf-8", newline="") as f:
            leitor = csv.DictReader(f)
            if not leitor.fieldnames or not OBRIGATORIOS.issubset(leitor.fieldnames):
                raise Bloqueado("CSV normalizado sem campos obrigatorios.")
            resultado = analisar_linhas(leitor, args.periodo, args.dtstar)
        resultado["sha256_entrada"] = args.sha256
        args.saida.parent.mkdir(parents=True, exist_ok=True)
        args.saida.write_text(json.dumps(resultado, indent=2, ensure_ascii=False), encoding="utf-8")
        print(json.dumps({"status": "OK_EXPLORATORIO", "secoes": resultado["total_secoes"]}))
        return 0
    except (Bloqueado, OSError, UnicodeError, csv.Error) as exc:
        print("BLOQUEADO:", str(exc))
        return 2


if __name__ == "__main__":
    raise SystemExit(main())

"""Contrato de esquema da pagina de resumos digitais (hashes) - F2.

A pagina real ainda nao foi aberta. Este modulo DECLARA o que se espera dela e
recusa (HALT) qualquer divergencia na primeira coleta. Nada aqui e inferido da
pagina; cada premissa tem origem registrada e pode ser derrubada pela F1.

Ordem obrigatoria (CONCILIACAO, secao 8): verificar a estrutura (colunas e
dimensao UF) ANTES de extrair qualquer hash.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from modelos import AUSENTE_PUBLICADO, HashEntry, Halt

UFS_27 = (
    "AC", "AL", "AM", "AP", "BA", "CE", "DF", "ES", "GO", "MA", "MG", "MS", "MT",
    "PA", "PB", "PE", "PI", "PR", "RJ", "RN", "RO", "RR", "RS", "SC", "SE", "SP", "TO",
)

CONTRATO = {
    "versao": "0.1",
    # Premissa P1 (PLANO, secoes 6 e 7): 15 sistemas. A confirmar no art. 3o da
    # Res. 23.673 em F1. Atencao: a lista de nomes do PLANO (F2) tem 16 itens.
    "n_sistemas": 15,
    # Premissa P2: 27 UFs. Se a pagina trouxer o exterior (ZZ), sao 28 e a
    # regra dispara HALT ate decisao humana.
    "ufs": UFS_27,
    # Premissa P3: hash em hexadecimal de 64 (SHA-256) ou 128 (SHA-512)
    # caracteres. Base64 ou outro formato => HALT e revisao do contrato.
    "hash_regex": r"^(?:[0-9a-f]{64}|[0-9a-f]{128})$",
    # Premissa P4: a tabela tem colunas identificaveis como sistema, UF e hash.
    "colunas": {
        "sistema": ("sistema", "programa", "aplicativo"),
        "uf": ("uf", "estado", "unidade da federacao"),
        "hash": ("hash", "resumo digital", "resumo"),
    },
    # Marcadores aceitos de ausencia declarada pela fonte (insumo de R02).
    "marcadores_ausencia": ("nao se aplica", "-", "n/a"),
}


@dataclass(frozen=True)
class Tabela:
    """Tabela generica extraida da pagina (ou da fixture), antes de interpretar."""
    fonte: str
    turno: int
    cabecalho: list[str]
    linhas: list[list[str]]


def _normalizar(texto: str) -> str:
    tabela = str.maketrans("áàâãéêíóôõúçÁÀÂÃÉÊÍÓÔÕÚÇ", "aaaaeeioooucAAAAEEIOOOUC")
    return " ".join(texto.translate(tabela).strip().lower().split())


def verificar_estrutura(tab: Tabela) -> dict[str, int]:
    """Primeira verificacao da coleta: conta colunas e localiza sistema, UF e hash.

    Retorna o indice de cada coluna. HALT se a dimensao UF nao existir
    (F2_SEM_DIMENSAO_UF) ou se qualquer coluna for ambigua ou ausente.
    """
    cab = [_normalizar(c) for c in tab.cabecalho]
    if not cab:
        raise Halt("F2_TABELA_VAZIA", f"{tab.fonte}: sem cabecalho")
    indices: dict[str, int] = {}
    for papel, nomes in CONTRATO["colunas"].items():
        achados = [i for i, c in enumerate(cab) if c in nomes]
        if papel == "uf" and not achados:
            raise Halt(
                "F2_SEM_DIMENSAO_UF",
                f"{tab.fonte}: {len(cab)} colunas {tab.cabecalho}; sem coluna de UF. "
                "R01/R02 sem objeto; reabrir o desenho da F2 (CONCILIACAO, secao 8).",
            )
        if len(achados) != 1:
            raise Halt("F2_COLUNA_" + papel.upper(), f"{tab.fonte}: coluna {papel} encontrada {len(achados)} vezes em {tab.cabecalho}")
        indices[papel] = achados[0]
    for n, linha in enumerate(tab.linhas):
        if len(linha) != len(cab):
            raise Halt("F2_LINHA_IRREGULAR", f"{tab.fonte}: linha {n} com {len(linha)} celulas, cabecalho com {len(cab)}")
    return indices


def extrair(tab: Tabela) -> list[HashEntry]:
    """Converte a tabela em HashEntry, aplicando o contrato celula a celula."""
    idx = verificar_estrutura(tab)
    padrao = re.compile(CONTRATO["hash_regex"])
    entradas: list[HashEntry] = []
    vistos: set[tuple[str, str]] = set()
    for n, linha in enumerate(tab.linhas):
        sistema = linha[idx["sistema"]].strip()
        uf = linha[idx["uf"]].strip().upper()
        bruto = linha[idx["hash"]].strip()
        if not sistema:
            raise Halt("F2_CELULA_VAZIA", f"{tab.fonte}: linha {n} sem sistema")
        if uf not in CONTRATO["ufs"]:
            raise Halt("F2_UF_DESCONHECIDA", f"{tab.fonte}: linha {n} UF {uf!r} fora das 27 (premissa P2)")
        if not bruto:
            raise Halt("F2_CELULA_VAZIA", f"{tab.fonte}: linha {n} ({sistema}, {uf}) sem hash")
        if _normalizar(bruto) in CONTRATO["marcadores_ausencia"]:
            valor = AUSENTE_PUBLICADO
        else:
            valor = bruto.lower()
            if not padrao.match(valor):
                raise Halt("F2_FORMATO_HASH", f"{tab.fonte}: linha {n} ({sistema}, {uf}) hash fora do formato (premissa P3)")
        if (sistema, uf) in vistos:
            raise Halt("F2_DUPLICADO", f"{tab.fonte}: ({sistema}, {uf}) repetido")
        vistos.add((sistema, uf))
        entradas.append(HashEntry(sistema=sistema, uf=uf, turno=tab.turno, hash=valor))
    verificar_matriz(entradas, tab.fonte)
    return sorted(entradas)


def verificar_matriz(entradas: list[HashEntry], fonte: str) -> None:
    """Gate F2: matriz completa sistema x UF, sem celula faltante."""
    sistemas = sorted({e.sistema for e in entradas})
    if len(sistemas) != CONTRATO["n_sistemas"]:
        raise Halt("F2_N_SISTEMAS", f"{fonte}: {len(sistemas)} sistemas, contrato exige {CONTRATO['n_sistemas']} (premissa P1)")
    ufs = sorted({e.uf for e in entradas})
    if tuple(ufs) != tuple(sorted(CONTRATO["ufs"])):
        faltam = sorted(set(CONTRATO["ufs"]) - set(ufs))
        raise Halt("F2_N_UFS", f"{fonte}: {len(ufs)} UFs; faltam {faltam}")
    presentes = {(e.sistema, e.uf) for e in entradas}
    vazias = [(s, u) for s in sistemas for u in CONTRATO["ufs"] if (s, u) not in presentes]
    if vazias:
        raise Halt("F2_MATRIZ_INCOMPLETA", f"{fonte}: {len(vazias)} celulas sem valor, primeira {vazias[0]}")

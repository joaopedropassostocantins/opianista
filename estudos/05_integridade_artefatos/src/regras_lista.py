"""Regras R01-R04 sobre a lista de hashes (F2), com tetos das emendas E1, E2 e E6.

Camada de todo achado: L1.2 (saida publicada pelo TSE). Teto: B com
anterioridade provada; C sem ela (E2). G4 sempre falso: a lista nao liga o
software lacrado ao executado na urna (C12/E6).
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass

from modelos import AUSENTE_PUBLICADO, Achado, HashEntry

LIMITE_R04 = (
    "R04 detecta alteracao da LISTA PUBLICADA, nao do software na urna. "
    "Se o software da urna foi alterado e a lista nao, R04 nao ve."
)
ORDEM_BUSCA_ANTERIORIDADE = ("wayback", "archive_today", "documento_datado", "cerimonia_04_09_2026")


@dataclass(frozen=True)
class Coleta:
    """Uma coleta propria da pagina, ja carimbada (ancora de R03)."""
    rotulo: str
    coleta_utc: str
    etag: str
    sha256: str
    carimbo_ok: bool


@dataclass(frozen=True)
class Captura:
    """Captura de terceiro anterior ao pleito (ancora de R04)."""
    origem: str  # um de ORDEM_BUSCA_ANTERIORIDADE
    data_captura_utc: str
    entradas: tuple[HashEntry, ...]


def _teto(anterioridade: str) -> str:
    return "B" if anterioridade == "provada" else "C"


def r01_r02(entradas: list[HashEntry], ancora: str, anterioridade: str) -> list[Achado]:
    """R01: hashes distintos do mesmo sistema entre UFs, mesmo turno.
    R02: sistema presente em uma UF e declarado ausente em outra."""
    por_sistema: dict[tuple[int, str], dict[str, list[str]]] = defaultdict(lambda: defaultdict(list))
    for e in entradas:
        por_sistema[(e.turno, e.sistema)][e.hash].append(e.uf)
    achados: list[Achado] = []
    for (turno, sistema), grupos in sorted(por_sistema.items()):
        hashes = sorted(h for h in grupos if h != AUSENTE_PUBLICADO)
        if len(hashes) > 1:
            maioria = max(hashes, key=lambda h: (len(grupos[h]), h))
            for h in hashes:
                if h == maioria:
                    continue
                achados.append(Achado(
                    regra="R01", camada="L1.2", classe_teto=_teto(anterioridade), turno=turno,
                    sistema=sistema, ufs=grupos[h],
                    observado=f"hash {h[:16]}... em {sorted(grupos[h])} difere de {maioria[:16]}... em {len(grupos[maioria])} UF(s)",
                    ancora=[ancora], confundidor="sistema nao se aplica a UF",
                    anterioridade=anterioridade,
                ))
        if AUSENTE_PUBLICADO in grupos and hashes:
            achados.append(Achado(
                regra="R02", camada="L1.2", classe_teto="C", turno=turno, sistema=sistema,
                ufs=grupos[AUSENTE_PUBLICADO],
                observado=f"declarado ausente em {sorted(grupos[AUSENTE_PUBLICADO])}, presente em outras UFs",
                ancora=[ancora], confundidor="UF com pleito suplementar", anterioridade=anterioridade,
            ))
    return achados


def r03(coletas: list[Coleta], ancora: str) -> list[Achado]:
    """R03: ETag ou conteudo muda entre coletas proprias carimbadas.
    Nao prova anterioridade (E2): serve so para mudanca posterior a 1a coleta."""
    validas = sorted((c for c in coletas if c.carimbo_ok), key=lambda c: c.coleta_utc)
    achados: list[Achado] = []
    for a, b in zip(validas, validas[1:]):
        if a.etag != b.etag or a.sha256 != b.sha256:
            achados.append(Achado(
                regra="R03", camada="L1.2", classe_teto="C", turno=0, sistema="(pagina)", ufs=[],
                observado=f"{a.rotulo} ({a.coleta_utc}, etag {a.etag}) -> {b.rotulo} ({b.coleta_utc}, etag {b.etag})",
                ancora=[ancora, a.rotulo, b.rotulo], confundidor="republicacao legitima",
            ))
    return achados


def anterioridade_de(capturas: list[Captura], data_pleito_utc: str = "2026-10-25T00:00:00Z") -> tuple[str, Captura | None]:
    """Aplica a ordem obrigatoria de busca (E2). Retorna ('provada', captura)
    pela primeira origem, na ordem, com captura anterior ao pleito."""
    for origem in ORDEM_BUSCA_ANTERIORIDADE:
        candidatas = sorted(
            (c for c in capturas if c.origem == origem and c.data_captura_utc < data_pleito_utc),
            key=lambda c: c.data_captura_utc, reverse=True,
        )
        if candidatas:
            return "provada", candidatas[0]
    return "nao_provada", None


def r04(atuais: list[HashEntry], capturas: list[Captura], ancora: str) -> tuple[str, list[Achado]]:
    """R04: hash publicado hoje difere do publicado antes do pleito.
    Sem captura anterior: ('nao_provada', []) e o chamador marca R04 como ausente."""
    estado, captura = anterioridade_de(capturas)
    if captura is None:
        return estado, []
    antes = {(e.turno, e.sistema, e.uf): e.hash for e in captura.entradas}
    achados: list[Achado] = []
    for e in sorted(atuais):
        h0 = antes.get((e.turno, e.sistema, e.uf))
        if h0 is not None and h0 != e.hash:
            achados.append(Achado(
                regra="R04", camada="L1.2", classe_teto="B", turno=e.turno, sistema=e.sistema, ufs=[e.uf],
                observado=f"antes ({captura.origem}, {captura.data_captura_utc}) {h0[:16]}...; hoje {e.hash[:16]}...",
                ancora=[ancora, f"{captura.origem}:{captura.data_captura_utc}"],
                confundidor="republicacao legitima com nova versao de sistema",
                limite_declarado=LIMITE_R04, anterioridade=estado,
            ))
    return estado, achados

"""Tipos comuns do Estudo 05: HALT, entrada de hash e achado.

Nenhuma decisao de julgamento aqui: so estruturas e serializacao deterministica.
"""

from __future__ import annotations

import hashlib
import json
from dataclasses import asdict, dataclass, field


class Halt(Exception):
    """Parada obrigatoria (PLANO, secao 7). Nunca capturar para seguir adiante."""

    def __init__(self, codigo: str, detalhe: str) -> None:
        super().__init__(f"HALT {codigo}: {detalhe}")
        self.codigo = codigo
        self.detalhe = detalhe


AUSENTE_PUBLICADO = "AUSENTE_PUBLICADO"
"""Marcador de sistema declarado ausente pela propria fonte (insumo de R02).
Celula vazia por falha de leitura nao usa este marcador: gera HALT."""


@dataclass(frozen=True, order=True)
class HashEntry:
    sistema: str
    uf: str
    turno: int
    hash: str  # hexadecimal minusculo ou AUSENTE_PUBLICADO


@dataclass
class Achado:
    regra: str
    camada: str
    classe_teto: str
    turno: int
    sistema: str
    ufs: list[str]
    observado: str
    ancora: list[str]
    confundidor: str
    limite_declarado: str = ""
    anterioridade: str = "nao_aplicavel"
    g1: bool = True
    g2: bool = True
    g3: bool = True
    g4: bool = False
    o_que_falta: str = "ligacao publica entre a lista de hashes e o software executado na urna"
    id: str = field(default="")

    def __post_init__(self) -> None:
        self.ufs = sorted(self.ufs)
        self.ancora = sorted(self.ancora)
        if not self.id:
            chave = f"{self.regra}|{self.turno}|{self.sistema}|{','.join(self.ufs)}|{self.observado}"
            self.id = "F05-" + hashlib.sha256(chave.encode("utf-8")).hexdigest()[:12]


def serializar(achados: list[Achado]) -> str:
    """JSON Lines ordenado e com chaves ordenadas: mesma entrada, mesmos bytes."""
    linhas = sorted((asdict(a) for a in achados), key=lambda d: (d["regra"], d["sistema"], d["id"]))
    return "".join(json.dumps(d, ensure_ascii=True, sort_keys=True) + "\n" for d in linhas)

"""Gera as fixtures SINTETICAS da F2. Nenhum valor vem da pagina real do TSE.

Nomes de sistema (SIS01..SIS15) e hashes (sha256 de texto fixo) sao ficticios.
Saida deterministica: rodar duas vezes produz os mesmos bytes.

Uso: python3 -I src/gerar_fixtures.py fixtures/
"""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from contrato_pagina import UFS_27  # noqa: E402

AVISO = "FIXTURE SINTETICA - valores ficticios, nao derivados de pagina do TSE"
SISTEMAS = [f"SIS{i:02d}" for i in range(1, 16)]
CABECALHO = ["Sistema", "UF", "Resumo digital"]


def h(texto: str) -> str:
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def tabela_limpa(sistemas=SISTEMAS, ufs=UFS_27) -> list[list[str]]:
    return [[s, u, h(f"{s}|versao-unica")] for s in sistemas for u in ufs]


def gravar(destino: Path, nome: str, turno: int, linhas, cabecalho=CABECALHO, extra=None) -> None:
    dados = {"aviso": AVISO, "fonte": f"fixture:{nome}", "turno": turno, "cabecalho": cabecalho, "linhas": linhas}
    if extra:
        dados.update(extra)
    (destino / f"{nome}.json").write_text(json.dumps(dados, ensure_ascii=True, indent=1, sort_keys=True) + "\n", encoding="utf-8")


def main(argv: list[str]) -> int:
    destino = Path(argv[1] if len(argv) > 1 else "fixtures")
    destino.mkdir(parents=True, exist_ok=True)
    limpa = tabela_limpa()
    gravar(destino, "f2_controle_limpa", 2, limpa)

    # (a) divergencia plantada: SIS07 em RR com hash diferente.
    a = [list(l) for l in limpa]
    for l in a:
        if l[0] == "SIS07" and l[1] == "RR":
            l[2] = h("SIS07|versao-plantada")
    gravar(destino, "f2_a_divergencia_uf", 2, a, extra={"esperado": {"R01": [["SIS07", ["RR"]]]}})

    # (b) ausencia declarada plantada: SIS11 ausente em AP.
    b = [list(l) for l in limpa]
    for l in b:
        if l[0] == "SIS11" and l[1] == "AP":
            l[2] = "Nao se aplica"
    gravar(destino, "f2_b_ausente_uf", 2, b, extra={"esperado": {"R02": [["SIS11", ["AP"]]]}})

    # (c) lista com 14 sistemas: deve dar HALT F2_N_SISTEMAS.
    gravar(destino, "f2_c_14_sistemas", 2, tabela_limpa(SISTEMAS[:14]), extra={"esperado": {"HALT": "F2_N_SISTEMAS"}})

    # (d) sem dimensao UF (hash agregado por sistema): HALT F2_SEM_DIMENSAO_UF.
    gravar(destino, "f2_d_sem_uf", 2, [[s, h(f"{s}|versao-unica")] for s in SISTEMAS],
           cabecalho=["Sistema", "Resumo digital"], extra={"esperado": {"HALT": "F2_SEM_DIMENSAO_UF"}})

    # (e) linha do exterior (ZZ): HALT F2_UF_DESCONHECIDA (premissa P2).
    gravar(destino, "f2_e_exterior_zz", 2, limpa + [[s, "ZZ", h(f"{s}|versao-unica")] for s in SISTEMAS],
           extra={"esperado": {"HALT": "F2_UF_DESCONHECIDA"}})

    # (f) celula vazia por falha de leitura: HALT F2_CELULA_VAZIA.
    f = [list(l) for l in limpa]
    f[40][2] = ""
    gravar(destino, "f2_f_celula_vazia", 2, f, extra={"esperado": {"HALT": "F2_CELULA_VAZIA"}})

    # R04: captura anterior ao pleito com SIS03/MG diferente do publicado hoje.
    antes = [list(l) for l in limpa]
    for l in antes:
        if l[0] == "SIS03" and l[1] == "MG":
            l[2] = h("SIS03|versao-anterior")
    gravar(destino, "r04_captura_wayback_20261010", 2, antes,
           extra={"origem": "wayback", "data_captura_utc": "2026-10-10T12:00:00Z",
                  "esperado": {"R04": [["SIS03", ["MG"]]]}})
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

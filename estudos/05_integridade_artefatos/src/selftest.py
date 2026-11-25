"""Selftest da F2 (PLANO, secao 8, adaptado as emendas).

Casos:
  T1 controle limpo: nenhum achado.
  T2 (a) divergencia plantada: exatamente um R01 em SIS07/RR, teto C sem anterioridade.
  T3 (b) ausencia plantada: exatamente um R02 em SIS11/AP.
  T4 (c) 14 sistemas: HALT F2_N_SISTEMAS.
  T5 (d) sem dimensao UF: HALT F2_SEM_DIMENSAO_UF.
  T6 (e) exterior ZZ: HALT F2_UF_DESCONHECIDA.
  T7 (f) celula vazia: HALT F2_CELULA_VAZIA.
  T8 R04 com captura anterior: um R04 em SIS03/MG, teto B, limite declarado.
  T9 R04 sem captura: anterioridade nao_provada e R01 limitado a C.
  T10 R03: mudanca de ETag entre coletas carimbadas; coleta sem carimbo ignorada.
  T11 determinismo: duas execucoes produzem os mesmos bytes.
  T12 contrato E3: codigo do Estudo 03 no commit fixado confere.

Uso: python3 -I src/selftest.py fixtures/   (sai com 1 em qualquer falha)
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import adapter_estudo03  # noqa: E402
from contrato_pagina import Tabela, extrair  # noqa: E402
from modelos import Halt, serializar  # noqa: E402
from regras_lista import Captura, Coleta, r01_r02, r03, r04  # noqa: E402

FALHAS: list[str] = []


def caso(nome: str, condicao: bool, detalhe: str = "") -> None:
    print(("OK   " if condicao else "FALHA") + f" {nome}" + (f" - {detalhe}" if detalhe and not condicao else ""))
    if not condicao:
        FALHAS.append(nome)


def tabela(fx: Path, nome: str) -> Tabela:
    d = json.loads((fx / f"{nome}.json").read_text(encoding="utf-8"))
    return Tabela(fonte=d["fonte"], turno=d["turno"], cabecalho=d["cabecalho"], linhas=d["linhas"])


def espera_halt(fx: Path, nome: str, codigo: str) -> None:
    try:
        extrair(tabela(fx, nome))
    except Halt as h:
        caso(f"{nome}: HALT {codigo}", h.codigo == codigo, f"recebido {h.codigo}")
        return
    caso(f"{nome}: HALT {codigo}", False, "nenhum HALT")


def rodar_f2(fx: Path, nome: str, capturas: list[Captura]) -> tuple[str, str]:
    entradas = extrair(tabela(fx, nome))
    estado, achados_r04 = r04(entradas, capturas, ancora=f"fixture:{nome}")
    achados = r01_r02(entradas, ancora=f"fixture:{nome}", anterioridade=estado) + achados_r04
    return estado, serializar(achados)


def main(argv: list[str]) -> int:
    fx = Path(argv[1] if len(argv) > 1 else "fixtures")

    _, s = rodar_f2(fx, "f2_controle_limpa", [])
    caso("T1 controle limpo sem achado", s == "", s)

    _, s = rodar_f2(fx, "f2_a_divergencia_uf", [])
    linhas = [json.loads(l) for l in s.splitlines()]
    caso("T2 R01 unico em SIS07/RR", [(l["regra"], l["sistema"], l["ufs"]) for l in linhas] == [("R01", "SIS07", ["RR"])], s)
    caso("T2 R01 sem anterioridade tem teto C e G4 falso",
         all(l["classe_teto"] == "C" and l["g4"] is False and l["camada"] == "L1.2" for l in linhas))

    _, s = rodar_f2(fx, "f2_b_ausente_uf", [])
    linhas = [json.loads(l) for l in s.splitlines()]
    caso("T3 R02 unico em SIS11/AP", [(l["regra"], l["sistema"], l["ufs"]) for l in linhas] == [("R02", "SIS11", ["AP"])], s)

    espera_halt(fx, "f2_c_14_sistemas", "F2_N_SISTEMAS")
    espera_halt(fx, "f2_d_sem_uf", "F2_SEM_DIMENSAO_UF")
    espera_halt(fx, "f2_e_exterior_zz", "F2_UF_DESCONHECIDA")
    espera_halt(fx, "f2_f_celula_vazia", "F2_CELULA_VAZIA")

    cap_tab = tabela(fx, "r04_captura_wayback_20261010")
    meta = json.loads((fx / "r04_captura_wayback_20261010.json").read_text(encoding="utf-8"))
    captura = Captura(origem=meta["origem"], data_captura_utc=meta["data_captura_utc"], entradas=tuple(extrair(cap_tab)))
    estado, s = rodar_f2(fx, "f2_controle_limpa", [captura])
    linhas = [json.loads(l) for l in s.splitlines()]
    caso("T8 R04 unico em SIS03/MG", estado == "provada" and [(l["regra"], l["sistema"], l["ufs"]) for l in linhas] == [("R04", "SIS03", ["MG"])], s)
    caso("T8 R04 teto B com limite declarado", all(l["classe_teto"] == "B" and "nao do software na urna" in l["limite_declarado"] for l in linhas))

    tardia = Captura(origem="wayback", data_captura_utc="2026-11-01T00:00:00Z", entradas=captura.entradas)
    estado, s = rodar_f2(fx, "f2_a_divergencia_uf", [tardia])
    linhas = [json.loads(l) for l in s.splitlines()]
    caso("T9 captura posterior ao pleito nao prova anterioridade", estado == "nao_provada")
    caso("T9 R01 limitado a C", linhas and all(l["classe_teto"] == "C" for l in linhas))

    coletas = [
        Coleta("c1", "2026-11-26T10:00:00Z", '"e1"', "aa", True),
        Coleta("c2", "2026-11-27T10:00:00Z", '"e1"', "aa", True),
        Coleta("cx", "2026-11-27T12:00:00Z", '"zz"', "ff", False),
        Coleta("c3", "2026-12-03T10:00:00Z", '"e2"', "bb", True),
    ]
    r = r03(coletas, "pagina_hashes")
    caso("T10 R03 unico entre c2 e c3", len(r) == 1 and "c2" in r[0].observado and "c3" in r[0].observado, str(r))

    s1 = rodar_f2(fx, "f2_a_divergencia_uf", [captura])
    s2 = rodar_f2(fx, "f2_a_divergencia_uf", [captura])
    caso("T11 determinismo", s1 == s2 and s1[1] != "")

    try:
        hashes = adapter_estudo03.verificar_contrato()
        caso("T12 contrato E3 do Estudo 03", True)
        print("     pino", adapter_estudo03.PINO_COMMIT[:7], json.dumps(hashes, sort_keys=True))
    except Halt as h:
        caso("T12 contrato E3 do Estudo 03", False, str(h))

    print(f"{'VERDE' if not FALHAS else 'VERMELHO'}: {len(FALHAS)} falha(s)")
    return 1 if FALHAS else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))

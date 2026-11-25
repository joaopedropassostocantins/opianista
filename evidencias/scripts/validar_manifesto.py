#!/usr/bin/env python3
"""Valida manifestos de evidencia contra as regras de AGENTS.md.

Uso: python3 -I evidencias/scripts/validar_manifesto.py evidencias/artefatos

Verifica campos obrigatorios e a coerencia entre camada, gate e classe.
Somente biblioteca padrao. Retorna codigo 1 se houver erro.
"""

import json
import sys
from pathlib import Path

ORDEM = ["A", "B", "C", "D"]
CAMPOS = ["slug", "camada", "classe", "autor", "artefato", "hashes",
          "carimbo", "arquivado", "gate", "faltas"]
PENDENTE = "<preencher>"


def teto(m: dict) -> str:
    """Classe maxima admissivel pelas regras do contrato."""
    g = m["gate"]
    if not (g.get("G1") and g.get("G2") and g.get("G3")):
        return "indicios_fracos"
    limite = 0
    if m["camada"] == "L3":
        limite = max(limite, ORDEM.index("C"))
    if not g.get("G4"):
        limite = max(limite, ORDEM.index("B"))
    build = m.get("build_reproduzivel", {})
    if not build.get("reproduzido"):
        limite = max(limite, ORDEM.index("B"))
    carimbo = m["carimbo"]
    if PENDENTE in (carimbo.get("genTime"), carimbo.get("rekor_index")):
        limite = max(limite, ORDEM.index("B"))
    return ORDEM[limite]


def validar(caminho: Path) -> list[str]:
    erros: list[str] = []
    try:
        m = json.loads(caminho.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return [f"{caminho}: JSON invalido ({exc})"]
    faltando = [c for c in CAMPOS if c not in m]
    if faltando:
        return [f"{caminho}: campos ausentes {faltando}"]
    if m["camada"] not in ("L1", "L2", "L3"):
        erros.append(f"{caminho}: camada invalida {m['camada']!r}")
    for g in ("G1", "G2", "G3", "G4"):
        if not isinstance(m["gate"].get(g), bool):
            erros.append(f"{caminho}: gate.{g} deve ser booleano")
    if erros:
        return erros
    if not m["gate"]["G4"] and not m["gate"].get("G4_motivo"):
        erros.append(f"{caminho}: G4 falso exige G4_motivo")
    classe = m["classe"]
    maximo = teto(m)
    if maximo == "indicios_fracos":
        if classe != "indicios_fracos":
            erros.append(f"{caminho}: falha em G1-G3 exige classe indicios_fracos")
    elif classe == "indicios_fracos":
        pass
    elif classe not in ORDEM:
        erros.append(f"{caminho}: classe invalida {classe!r}")
    elif ORDEM.index(classe) < ORDEM.index(maximo):
        erros.append(f"{caminho}: classe {classe} acima do teto {maximo}")
    pasta = caminho.parent.parent.name
    if pasta != classe:
        erros.append(f"{caminho}: esta em artefatos/{pasta}, mas classe = {classe}")
    if caminho.parent.name != m["slug"]:
        erros.append(f"{caminho}: diretorio {caminho.parent.name} difere do slug {m['slug']}")
    return erros


def main() -> int:
    raiz = Path(sys.argv[1] if len(sys.argv) > 1 else "evidencias/artefatos")
    arquivos = sorted(raiz.glob("*/*/manifesto.json"))
    todos: list[str] = []
    for arq in arquivos:
        todos.extend(validar(arq))
    for e in todos:
        print("ERRO", e)
    print(f"{len(arquivos)} manifesto(s), {len(todos)} erro(s)")
    return 1 if todos else 0


if __name__ == "__main__":
    sys.exit(main())

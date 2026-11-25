"""Adaptador unico para o codigo do Estudo 03 (emenda E3).

- Le o codigo-fonte do objeto Git do commit fixado, nunca da arvore de trabalho.
- Teste de contrato: hash do blob e funcoes/argumentos esperados (via AST,
  sem importar dependencias). Divergencia = HALT. Proibido contornar.
- Atualizar o pino exige linha nova em DECISOES.md e nova execucao do teste.
"""

from __future__ import annotations

import ast
import hashlib
import subprocess
import types
from pathlib import Path

from modelos import Halt

PINO_COMMIT = "6adf40d1130d2e3391fbea083f0eba9651dc86fa"
BASE = "estudos/03_pianista/etapas/02_parser"

# Contrato: sha256 do arquivo no commit fixado e assinatura das funcoes usadas.
CONTRATO = {
    "logs_urna.py": {
        "sha256": "8e1f3eb5930a713d46859a941a7444af933b3a19fbd64c326175d7a08faf9792",
        "funcoes": {
            "mascarar": ["texto"],
            "ler_logjez": ["conteudo"],
            "decodificar": ["dados"],
            "interpretar_linha": ["bruta"],
        },
    },
    "bu.py": {
        "sha256": "a5474d86739e87b068a8fe6eaa63248024835654c013dd4860f5a59c210d6e99",
        "funcoes": {
            "compilar": ["pasta"],
            "decodificar_bu": ["spec", "dados"],
            "linhas_do_bu": ["bu", "cargo"],
        },
    },
}


def _raiz_repo() -> Path:
    saida = subprocess.run(["git", "rev-parse", "--show-toplevel"], cwd=Path(__file__).parent,
                           capture_output=True, text=True, check=True)
    return Path(saida.stdout.strip())


def ler_fonte(arquivo: str, commit: str = PINO_COMMIT) -> bytes:
    proc = subprocess.run(["git", "show", f"{commit}:{BASE}/{arquivo}"], cwd=_raiz_repo(), capture_output=True)
    if proc.returncode != 0:
        raise Halt("E3_COMMIT_INDISPONIVEL", f"{commit}:{arquivo} nao encontrado ({proc.stderr.decode(errors='replace').strip()})")
    return proc.stdout


def verificar_contrato(contrato: dict | None = None, commit: str = PINO_COMMIT) -> dict[str, str]:
    """Retorna {arquivo: sha256}. HALT na primeira divergencia."""
    contrato = contrato or CONTRATO
    hashes: dict[str, str] = {}
    for arquivo, esperado in contrato.items():
        fonte = ler_fonte(arquivo, commit)
        h = hashlib.sha256(fonte).hexdigest()
        hashes[arquivo] = h
        if not esperado["sha256"]:
            raise Halt("E3_PINO_SEM_HASH", f"{arquivo}: sha256 nao congelado no contrato (obtido {h})")
        if esperado["sha256"] != h:
            raise Halt("E3_HASH_DIVERGENTE", f"{arquivo}: {h} != {esperado['sha256']}")
        arvore = ast.parse(fonte)
        defs = {n.name: [a.arg for a in n.args.args] for n in arvore.body if isinstance(n, ast.FunctionDef)}
        for nome, args in esperado["funcoes"].items():
            if nome not in defs:
                raise Halt("E3_FUNCAO_AUSENTE", f"{arquivo}: {nome} nao existe no commit {commit[:7]}")
            if defs[nome] != args:
                raise Halt("E3_ASSINATURA_DIVERGENTE", f"{arquivo}: {nome}{tuple(defs[nome])} != {tuple(args)}")
    return hashes


def carregar(arquivo: str) -> types.ModuleType:
    """Importa o modulo do commit fixado, depois de verificar o contrato.
    Requer as dependencias do Estudo 03 (py7zr para logs, asn1tools para BU)."""
    verificar_contrato({arquivo: CONTRATO[arquivo]})
    fonte = ler_fonte(arquivo)
    modulo = types.ModuleType(f"estudo03_{arquivo[:-3]}")
    modulo.__file__ = f"{PINO_COMMIT[:7]}:{BASE}/{arquivo}"
    exec(compile(fonte, modulo.__file__, "exec"), modulo.__dict__)  # noqa: S102 - codigo do proprio repositorio, commit fixado
    return modulo

# Evidencias

Repositorio de evidencias sobre software de manipulacao de resultados no
2o turno de 2026, sob o contrato `AGENTS.md`.

| Arquivo | Funcao |
|---------|--------|
| `AGENTS.md` | Contrato de evidencia: camadas, gate G1-G4, classes, carimbo, build, arquivamento |
| `manifesto.schema.json` | Schema do `manifesto.json` de cada item |
| `INVENTARIO.md` | Classificacao corrente e caminho para classe A |
| `scripts/coletar.sh` | SHA-256 + RFC 3161 + Rekor, cria o diretorio do item |
| `scripts/rechecar.sh` | Rechecagem de ETag/hash da fonte (24 h e 7 dias) |
| `scripts/validar_manifesto.py` | Bloqueia classe acima do teto permitido |
| `artefatos/<classe>/<slug>/` | Metadados, hashes e carimbos; arquivo bruto fica em `bruto/` (fora do Git) |

Fluxo:

```
bash evidencias/scripts/coletar.sh <arquivo> <classe> <slug> <url>
# preencher manifesto.json e gate.md
python3 -I evidencias/scripts/validar_manifesto.py evidencias/artefatos
```

Requisitos: openssl, curl; `rekor-cli` (Sigstore) para o log de transparencia.

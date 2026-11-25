#!/usr/bin/env bash
# Fallback da decisao D3 (proponente, 2026-11-25): coleta F1 na maquina do
# proponente se a liberacao de hosts nao sair em 48 h. Reproduzido como
# recebido. Requer curl, openssl, zstd; ots opcional.
set -euo pipefail
OUT="l1_$(date -u +%Y%m%dT%H%M%SZ)"; mkdir -p "$OUT"; cd "$OUT"
UA='estudo05/0.1 (+contato no autor.md)'
URLS=(
"https://www.tse.jus.br/eleicoes/urna-eletronica/seguranca-da-urna/hash/resumos-digitais-hashes-das-eleicoes-2026-1o-e-2o-turnos"
"https://www.tse.jus.br/eleicoes/urna-eletronica/seguranca-da-urna/hash"
"https://www.tse.jus.br/eleicoes/urna-eletronica/seguranca-da-urna/apresentacao-digital-e-lacracao"
"https://www.tse.jus.br/legislacao/compilada/res/2021/resolucao-no-23-673-14-de-dezembro-de-2021"
)
for i in "${!URLS[@]}"; do
  curl -sSL -A "$UA" -D "h$i.txt" -o "f$i" "${URLS[$i]}" || echo "FALHA f$i" > "f$i.erro"
  [ -f "f$i" ] || continue
  sha256sum "f$i" > "f$i.sha256"; sha512sum "f$i" > "f$i.sha512"
  openssl ts -query -data "f$i" -sha256 -cert -out "f$i.tsq" 2>/dev/null || continue
  for t in 1 2 3; do curl -sS -f -H 'Content-Type: application/timestamp-query' \
      --data-binary "@f$i.tsq" https://freetsa.org/tsr > "f$i.tsr" 2>/dev/null && break; sleep $((t*20)); done
  [ -s "f$i.tsr" ] || { echo incompleto > "f$i.stamp"; continue; }
  command -v ots >/dev/null && ots stamp "f$i" >/dev/null 2>&1 || true
done
cd ..; tar --sort=name --mtime=@0 --owner=0 --group=0 --numeric-owner -cf - "$OUT" | zstd -19 > "$OUT.tar.zst"
sha256sum "$OUT.tar.zst"

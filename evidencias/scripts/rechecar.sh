#!/usr/bin/env bash
# Rechecagem da fonte apos 24 h e 7 dias (AGENTS.md, secao 6).
# Uso: rechecar.sh <diretorio_do_item>
# Le fonte.url, grava ETag, Last-Modified e SHA-256 do conteudo atual em
# rechecagens.log, para comparacao com a coleta original.
set -euo pipefail

DIR="$1"
URL="$(head -n1 "$DIR/fonte.url")"
AGORA="$(date -u +%Y-%m-%dT%H:%M:%SZ)"
TMP="$(mktemp -d)"
trap 'rm -rf "$TMP"' EXIT

curl -sS -L -D "$TMP/cab" -o "$TMP/corpo" "$URL"
ETAG="$(grep -i '^etag:' "$TMP/cab" | tail -n1 | tr -d '\r' | cut -d' ' -f2- || true)"
LM="$(grep -i '^last-modified:' "$TMP/cab" | tail -n1 | tr -d '\r' | cut -d' ' -f2- || true)"
H="$(sha256sum "$TMP/corpo" | awk '{print $1}')"

printf '%s\tetag=%s\tlast_modified=%s\tsha256=%s\n' "$AGORA" "${ETAG:-}" "${LM:-}" "$H" \
  >> "$DIR/rechecagens.log"
tail -n1 "$DIR/rechecagens.log"

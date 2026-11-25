#!/usr/bin/env bash
# Coleta com carimbo de tempo de terceiro (AGENTS.md, secao 4).
# Uso: coletar.sh <arquivo> <classe> <slug> <url_fonte>
# Cria evidencias/artefatos/<classe>/<slug>/ com sha256, requisicao e resposta
# RFC 3161, entrada Rekor (se rekor-cli existir), fonte.url e coleta.utc.
# O arquivo bruto e copiado para bruto/, que o Git ignora.
set -euo pipefail

if [ "$#" -ne 4 ]; then
  echo "uso: $0 <arquivo> <classe A|B|C|D|indicios_fracos> <slug> <url_fonte>" >&2
  exit 2
fi

ARQ="$1"; CLASSE="$2"; SLUG="$3"; FONTE="$4"
TSA_URL="${TSA_URL:-https://freetsa.org/tsr}"
BASE="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$BASE/artefatos/$CLASSE/$SLUG"
NOME="$(basename "$ARQ")"

case "$CLASSE" in A|B|C|D|indicios_fracos) ;; *) echo "classe invalida: $CLASSE" >&2; exit 2;; esac
[ -f "$ARQ" ] || { echo "arquivo nao encontrado: $ARQ" >&2; exit 2; }

mkdir -p "$DEST/bruto"

# 1. Hash antes de qualquer outra acao.
DIGEST="$(sha256sum "$ARQ" | awk '{print $1}')"
echo "$DIGEST  $NOME" > "$DEST/$NOME.sha256"
date -u +%Y-%m-%dT%H:%M:%SZ > "$DEST/coleta.utc"
printf '%s\n' "$FONTE" > "$DEST/fonte.url"
cp -p "$ARQ" "$DEST/bruto/$NOME"
echo "sha256 $DIGEST"

# 2. Token RFC 3161 sobre o digest.
openssl ts -query -digest "$DIGEST" -sha256 -cert -no_nonce -out "$DEST/$NOME.tsq" 2>/dev/null \
  || openssl ts -query -data "$ARQ" -sha256 -cert -out "$DEST/$NOME.tsq"
if curl -sS --fail -H "Content-Type: application/timestamp-query" \
     --data-binary @"$DEST/$NOME.tsq" "$TSA_URL" -o "$DEST/$NOME.tsr"; then
  openssl ts -reply -in "$DEST/$NOME.tsr" -text > "$DEST/$NOME.tsr.txt" 2>&1 || true
  grep -E "Time stamp:|Accuracy:" "$DEST/$NOME.tsr.txt" || true
else
  echo "AVISO: TSA indisponivel ($TSA_URL); item sem carimbo nao passa de C" >&2
  rm -f "$DEST/$NOME.tsr"
fi

# 3. Log de transparencia.
if command -v rekor-cli >/dev/null 2>&1; then
  rekor-cli upload --artifact "$ARQ" --format json > "$DEST/rekor.json" \
    || echo "AVISO: falha no upload ao Rekor" >&2
else
  echo "AVISO: rekor-cli ausente; registrar no Rekor antes de promover a A ou B" >&2
fi

echo "coleta gravada em $DEST"
echo "proximo passo: preencher $DEST/manifesto.json e gate.md, depois validar_manifesto.py"

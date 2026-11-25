#!/usr/bin/env bash
# Coleta com carimbo de tempo de terceiro (AGENTS.md v1.1, secao 4).
# Uso: coletar.sh <arquivo> <classe> <slug> <url_fonte>
# Cria evidencias/artefatos/<classe>/<slug>/ com sha256, sha512, requisicao,
# resposta e verificacao RFC 3161, OpenTimestamps, assinatura minisign do
# coletor, entrada Rekor e stamp.status. Degrada sem falhar: o que faltar fica
# listado em stamp.status (coleta incompleta nao passa de C).
# Variaveis: TSA_URL, TSA_CERT_URL, TSA_CA_URL, MINISIGN_KEY (chave privada,
# fora do Git), TSA_TENTATIVAS (padrao 5).
set -euo pipefail

if [ "$#" -ne 4 ]; then
  echo "uso: $0 <arquivo> <classe A|B|C|D|indicios_fracos> <slug> <url_fonte>" >&2
  exit 2
fi

ARQ="$1"; CLASSE="$2"; SLUG="$3"; FONTE="$4"
TSA_URL="${TSA_URL:-https://freetsa.org/tsr}"
TSA_CERT_URL="${TSA_CERT_URL:-https://freetsa.org/files/tsa.crt}"
TSA_CA_URL="${TSA_CA_URL:-https://freetsa.org/files/cacert.pem}"
TSA_TENTATIVAS="${TSA_TENTATIVAS:-5}"
BASE="$(cd "$(dirname "$0")/.." && pwd)"
DEST="$BASE/artefatos/$CLASSE/$SLUG"
NOME="$(basename "$ARQ")"
FALTAS=()

case "$CLASSE" in A|B|C|D|indicios_fracos) ;; *) echo "classe invalida: $CLASSE" >&2; exit 2;; esac
[ -f "$ARQ" ] || { echo "arquivo nao encontrado: $ARQ" >&2; exit 2; }

mkdir -p "$DEST/bruto" "$BASE/tsa"

# 1. Hashes antes de qualquer outra acao.
DIGEST="$(sha256sum "$ARQ" | awk '{print $1}')"
echo "$DIGEST  $NOME" > "$DEST/$NOME.sha256"
sha512sum "$ARQ" | awk -v n="$NOME" '{print $1"  "n}' > "$DEST/$NOME.sha512"
date -u +%Y-%m-%dT%H:%M:%SZ > "$DEST/coleta.utc"
printf '%s\n' "$FONTE" > "$DEST/fonte.url"
echo "v1.1" > "$DEST/contrato"
cp -p "$ARQ" "$DEST/bruto/$NOME"
echo "sha256 $DIGEST"

# 2. RFC 3161 com retentativa e verificacao obrigatoria.
openssl ts -query -digest "$DIGEST" -sha256 -cert -out "$DEST/$NOME.tsq"
TSR_OK=0
for t in $(seq 1 "$TSA_TENTATIVAS"); do
  if curl -sS --fail -H "Content-Type: application/timestamp-query" \
       --data-binary @"$DEST/$NOME.tsq" "$TSA_URL" -o "$DEST/$NOME.tsr"; then
    TSR_OK=1; break
  fi
  echo "TSA tentativa $t falhou" >&2
  [ "$t" -lt "$TSA_TENTATIVAS" ] && sleep $((t * 15))
done
if [ "$TSR_OK" -eq 1 ]; then
  openssl ts -reply -in "$DEST/$NOME.tsr" -text > "$DEST/$NOME.tsr.txt" 2>&1 || true
  [ -s "$BASE/tsa/tsa.crt" ] || curl -sS --fail "$TSA_CERT_URL" -o "$BASE/tsa/tsa.crt" || true
  [ -s "$BASE/tsa/cacert.pem" ] || curl -sS --fail "$TSA_CA_URL" -o "$BASE/tsa/cacert.pem" || true
  ( cd "$BASE/tsa" && sha256sum tsa.crt cacert.pem > certs.sha256 2>/dev/null ) || true
  if openssl ts -verify -in "$DEST/$NOME.tsr" -queryfile "$DEST/$NOME.tsq" \
       -CAfile "$BASE/tsa/cacert.pem" -untrusted "$BASE/tsa/tsa.crt" \
       > "$DEST/$NOME.tsr.verify" 2>&1; then
    grep -E "Time stamp:|Accuracy:" "$DEST/$NOME.tsr.txt" || true
  else
    echo "AVISO: TSR nao verificou; tratado como ausente" >&2
    FALTAS+=("tsr_nao_verificado")
  fi
else
  echo "AVISO: TSA indisponivel ($TSA_URL) apos $TSA_TENTATIVAS tentativas" >&2
  rm -f "$DEST/$NOME.tsr"
  FALTAS+=("tsr")
fi

# 3. Log de transparencia.
if command -v rekor-cli >/dev/null 2>&1 && \
   rekor-cli upload --artifact "$ARQ" --format json > "$DEST/rekor.json" 2>/dev/null; then
  :
else
  rm -f "$DEST/rekor.json"
  FALTAS+=("rekor")
fi

# 4a. OpenTimestamps.
if command -v ots >/dev/null 2>&1 && cp "$ARQ" "$DEST/$NOME.otsin" && \
   ots stamp "$DEST/$NOME.otsin" >/dev/null 2>&1; then
  mv "$DEST/$NOME.otsin.ots" "$DEST/$NOME.ots"
else
  FALTAS+=("ots")
fi
rm -f "$DEST/$NOME.otsin"

# 4b. Assinatura do coletor.
if [ -n "${MINISIGN_KEY:-}" ] && command -v minisign >/dev/null 2>&1 && \
   minisign -S -s "$MINISIGN_KEY" -m "$DEST/$NOME.sha512" -x "$DEST/$NOME.sha512.minisig" >/dev/null; then
  :
else
  FALTAS+=("minisign")
fi

# 4c. Situacao do carimbo. Completo exige TSR verificado e Rekor.
FALTA_ESSENCIAL=0
for f in "${FALTAS[@]:-}"; do
  case "$f" in tsr|tsr_nao_verificado|rekor) FALTA_ESSENCIAL=1;; esac
done
if [ "$FALTA_ESSENCIAL" -eq 0 ]; then
  STATUS="completo"
  [ "${#FALTAS[@]}" -gt 0 ] && STATUS="completo; complementos ausentes: ${FALTAS[*]}"
else
  STATUS="incompleto: ${FALTAS[*]}"
fi
echo "$STATUS" > "$DEST/stamp.status"

echo "stamp.status: $STATUS"
echo "coleta gravada em $DEST"
echo "proximo passo: preencher manifesto.json (contrato v1.1) e gate.md, depois validar_manifesto.py"

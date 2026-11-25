#!/usr/bin/env bash
# Ponto de entrada do Estudo 05. Subcomandos implementados: fixtures, selftest.
set -euo pipefail
cd "$(dirname "$0")"
case "${1:-}" in
  fixtures) python3 -I src/gerar_fixtures.py fixtures ;;
  selftest)
    for f in src/*.py; do python3 -I -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$f"; done
    python3 -I src/selftest.py fixtures ;;
  *) echo "uso: $0 {fixtures|selftest}" >&2; exit 2 ;;
esac

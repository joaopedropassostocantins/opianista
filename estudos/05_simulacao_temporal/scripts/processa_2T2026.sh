#!/bin/bash
cd /home/user/opianista
M=data/2026_2t/horarios/manifesto.tsv
for uf in "$@"; do
  out=data/2026_2t/horarios/horarios_2T2026_${uf}.csv
  [ -s "$out" ] && continue
  mkdir data/2026_2t/arq/lock_$uf 2>/dev/null || continue
  url="https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/arqurnatot/bu_imgbu_logjez_rdv_vscmr_2026_2t_${uf}.zip"
  z=data/2026_2t/arq/bu_imgbu_logjez_rdv_vscmr_2026_2t_${uf}.zip
  [ -f data/2026_2t/arq/$uf.zip ] && mv data/2026_2t/arq/$uf.zip "$z"
  lm=$(curl -sSI "$url" | grep -i last-modified | cut -d' ' -f2- | tr -d '\r')
  ok=0
  for i in 1 2 3 4 5; do curl -sS --fail -C - -o "$z" "$url" && { ok=1; break; }; sleep $((2**i)); done
  if [ $ok = 1 ]; then
    sha=$(sha256sum "$z" | cut -d' ' -f1)
    python3 -I estudos/05_simulacao_temporal/horarios_secao.py --zip "$z" --data-eleicao 25/10/2026 \
      --cargo PRESIDENTE --cargo2 GOVERNADOR --turno-bu "2° Turno" --liberado-d4 "REGISTRO.md 2026-10-29" --out "$out" && \
      printf "%s\t%s\t%s\t%s\n" "$uf" "$url" "$lm" "$sha" >> $M
  fi
  rm -f "$z"; rmdir data/2026_2t/arq/lock_$uf
  echo "$(date -u +%H:%M:%S) $uf ok=$ok"
done

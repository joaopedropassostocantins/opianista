#!/bin/bash
# uso: worker.sh UF1 UF2 ... ; trava por UF com mkdir atomico
cd /home/user/opianista
M=data/2024/horarios/manifesto.tsv
for uf in "$@"; do
  out=data/2024/horarios/horarios_2T2024_${uf}.csv
  [ -s "$out" ] && continue
  mkdir data/2024/arqurna/lock_$uf 2>/dev/null || continue
  url="https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2024/arqurnatot/bu_imgbu_logjez_rdv_vscmr_2024_2t_${uf}.zip"
  z=data/2024/arqurna/bu_imgbu_logjez_rdv_vscmr_2024_2t_${uf}.zip
  lm=$(curl -sSI "$url" | grep -i last-modified | cut -d' ' -f2- | tr -d '\r')
  ok=0
  for i in 1 2 3 4; do curl -sS --fail -C - -o "$z" "$url" && { ok=1; break; }; sleep $((2**i)); done
  if [ $ok = 1 ]; then
    sha=$(sha256sum "$z" | cut -d' ' -f1)
    python3 -I estudos/05_simulacao_temporal/horarios_secao.py --zip "$z" --data-eleicao 27/10/2024 --cargo PREFEITO --turno-bu "2º Turno" --out "$out" && \
      printf "%s\t%s\t%s\t%s\n" "$uf" "$url" "$lm" "$sha" >> $M
  fi
  rm -f "$z"; rmdir data/2024/arqurna/lock_$uf
  echo "$(date -u +%H:%M:%S) $uf ok=$ok"
done

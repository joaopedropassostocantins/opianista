#!/usr/bin/env python3
"""
Download dos logs de urna (2026) a partir de resultados.tse.jus.br.

Uso:
  python download.py catalogo                 # baixa os catalogos de secoes (27 UF + ZZ, 1T e 2T)
  python download.py logs AMOSTRA.csv [--workers 6]

Regras:
  - Nunca sobrescreve arquivo existente (se existir, apenas confere o SHA-256 no manifesto).
  - Registra SHA-256 de todo arquivo baixado em data/raw/manifesto_sha256.csv (append-only).
"""
import csv
import hashlib
import json
import os
import sys
import threading
import time
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE = "https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna"
PLEITOS = {"1": "3220", "2": "3221"}
UFS = ("ac al am ap ba ce df es go ma mg ms mt pa pb pe pi pr rj rn ro rr rs sc se sp to zz").split()
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(ROOT, "data", "raw")
MANIFEST = os.path.join(RAW, "manifesto_sha256.csv")
_lock = threading.Lock()


def get(url, tries=6):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "pesquisa-academica"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            last = e
            if e.code == 404:
                raise
        except Exception as e:  # rede
            last = e
        time.sleep(1.5 * (2 ** k))
    raise last


def save(path, data, url):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    h = hashlib.sha256(data).hexdigest()
    if os.path.exists(path):
        with open(path, "rb") as f:
            old = hashlib.sha256(f.read()).hexdigest()
        if old != h:
            # nunca sobrescreve: grava a versao divergente ao lado
            path = path + f".divergente.{h[:12]}"
            if os.path.exists(path):
                return h
        else:
            return h
    with open(path, "xb") as f:
        f.write(data)
    with _lock:
        new = not os.path.exists(MANIFEST)
        with open(MANIFEST, "a", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["arquivo", "sha256", "bytes", "url", "baixado_em_utc"])
            w.writerow([os.path.relpath(path, RAW), h, len(data), url,
                        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())])
    return h


def catalogo():
    out = os.path.join(RAW, "catalogo")
    for turno, p in PLEITOS.items():
        for uf in UFS:
            path = os.path.join(out, f"{uf}-p{p}-cs.json")
            if os.path.exists(path):
                continue
            url = f"{BASE}/{p}/config/{uf}/{uf}-p00{p}-cs.json"
            save(path, get(url), url)
            time.sleep(0.3)


def baixar_secao(turno, uf, mun, zona, secao):
    p = PLEITOS[str(turno)]
    d = f"{BASE}/{p}/dados/{uf}/{mun}/{zona}/{secao}"
    base_local = os.path.join(RAW, "logs", f"t{turno}", uf, mun, zona, secao)
    aux_path = os.path.join(base_local, "aux.json")
    if os.path.exists(aux_path):
        aux_bytes = open(aux_path, "rb").read()
    else:
        url = f"{d}/p00{p}-{uf}-m{mun}-z{zona}-s{secao}-aux.json"
        aux_bytes = get(url)
        save(aux_path, aux_bytes, url)
    aux = json.loads(aux_bytes.decode("utf-8"))
    n = 0
    for hh in aux.get("hashes", []):
        for a in hh.get("arq", []):
            if a.get("tp") != "log":
                continue
            lp = os.path.join(base_local, hh["hash"][:16], a["nm"])
            if not os.path.exists(lp):
                url = f"{d}/{hh['hash']}/{a['nm']}"
                save(lp, get(url), url)
            n += 1
    return n


def logs(amostra_csv, workers=6):
    rows = list(csv.DictReader(open(amostra_csv, encoding="utf-8")))
    ok = falhas = 0
    with ThreadPoolExecutor(workers) as ex:
        fut = {ex.submit(baixar_secao, r["turno"], r["uf"], r["mun"], r["zona"], r["secao"]): r for r in rows}
        for i, f in enumerate(as_completed(fut), 1):
            r = fut[f]
            try:
                f.result()
                ok += 1
            except Exception as e:
                falhas += 1
                with _lock, open(os.path.join(RAW, "falhas_download.csv"), "a") as fh:
                    fh.write(f"{r['turno']},{r['uf']},{r['mun']},{r['zona']},{r['secao']},{type(e).__name__}:{e}\n")
            if i % 500 == 0:
                print(f"{i}/{len(rows)} ok={ok} falhas={falhas}", flush=True)
    print(f"fim ok={ok} falhas={falhas}")


if __name__ == "__main__":
    if sys.argv[1] == "catalogo":
        catalogo()
    elif sys.argv[1] == "logs":
        w = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 6
        logs(sys.argv[2], w)

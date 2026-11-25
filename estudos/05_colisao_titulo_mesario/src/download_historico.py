#!/usr/bin/env python3
"""
download_historico.py -- quadro amostral e download dos logs de 2022 e 2024 (anos homologados usados como
parametro), a partir dos pacotes por UF do CDN do TSE, lendo so as entradas .logjez via HTTP Range.

  python download_historico.py quadro ANO          -> data/processed/quadro_<ANO>.csv (secoes com log, 1T e 2T)
  python download_historico.py amostra ANO F       -> registro/amostra_<ANO>.csv (mesma semente, mesma regra)
  python download_historico.py logs ANO [--workers N]

Pacote: https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes<ANO>/arqurnatot/
        bu_imgbu_logjez_rdv_vscmr_<ANO>_<t>t_<UF>.zip
Nome da entrada: o00<PLEITO>-<MUN5><ZONA4><SECAO4>.logjez
"""
import csv
import hashlib
import math
import os
import random
import struct
import sys
import threading
import time
import urllib.request
import zipfile
import zlib
from concurrent.futures import ThreadPoolExecutor, as_completed

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from zip_remoto import HTTPRangeFile  # noqa: E402
from amostragem import SEMENTE  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
RAW = os.path.join(ROOT, "data", "raw")
MANIFEST = os.path.join(RAW, "manifesto_sha256.csv")
UFS = ("AC AL AM AP BA CE DF ES GO MA MG MS MT PA PB PE PI PR RJ RN RO RR RS SC SE SP TO ZZ").split()
_lock = threading.Lock()


def url_pacote(ano, t, uf):
    return (f"https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes{ano}/arqurnatot/"
            f"bu_imgbu_logjez_rdv_vscmr_{ano}_{t}t_{uf}.zip")


def quadro(ano):
    out = os.path.join(ROOT, "data", "processed", f"quadro_{ano}.csv")
    with open(out, "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh)
        w.writerow(["turno", "uf", "mun", "zona", "secao", "entrada", "offset", "csize", "usize", "metodo", "url"])
        for t in (1, 2):
            for uf in UFS:
                u = url_pacote(ano, t, uf)
                try:
                    z = zipfile.ZipFile(HTTPRangeFile(u))
                except Exception as e:
                    print("sem pacote", ano, t, uf, type(e).__name__)
                    continue
                n = 0
                for zi in z.infolist():
                    nm = os.path.basename(zi.filename)
                    if not nm.endswith(".logjez"):
                        continue
                    cod = nm.split("-")[1].split(".")[0]
                    w.writerow([t, uf.lower(), cod[0:5], cod[5:9], cod[9:13], zi.filename, zi.header_offset,
                                zi.compress_size, zi.file_size, zi.compress_type, u])
                    n += 1
                print(ano, t, uf, n, flush=True)


def amostra(ano, f):
    rows = list(csv.DictReader(open(os.path.join(ROOT, "data", "processed", f"quadro_{ano}.csv"), encoding="utf-8")))
    rng = random.Random(SEMENTE + ano)
    out = []
    for t in ("1", "2"):
        por_uf = {}
        for r in rows:
            if r["turno"] == t:
                por_uf.setdefault(r["uf"], []).append(r)
        for uf in sorted(por_uf):
            lst = sorted(por_uf[uf], key=lambda r: (r["mun"], r["zona"], r["secao"], r["entrada"]))
            rng.shuffle(lst)
            n_h = math.ceil(f * len(lst))
            for r in lst[:n_h]:
                out.append(dict(r, N_uf=len(lst), n_uf=n_h, peso=len(lst) / n_h, semente=SEMENTE + ano, fracao=f))
    saida = os.path.join(ROOT, "registro", f"amostra_{ano}.csv")
    with open(saida, "w", newline="", encoding="utf-8") as fh:
        w = csv.DictWriter(fh, fieldnames=list(out[0].keys()))
        w.writeheader()
        w.writerows(out)
    print(len(out), "entradas ->", saida)


def _range(url, a, b, tries=6):
    last = None
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={"Range": f"bytes={a}-{b}", "User-Agent": "pesquisa-academica"})
            with urllib.request.urlopen(req, timeout=120) as r:
                return r.read()
        except Exception as e:
            last = e
            time.sleep(1.5 * 2 ** k)
    raise last


def baixar_entrada(ano, r):
    dest = os.path.join(RAW, f"logs{ano}", f"t{r['turno']}", r["uf"], r["mun"], r["zona"], r["secao"],
                        os.path.basename(r["entrada"]))
    if os.path.exists(dest):
        return
    off, cs = int(r["offset"]), int(r["csize"])
    blob = _range(r["url"], off, off + 30 + 1024 + cs)
    sig, _, _, metodo, _, _, _, _, _, ln, le = struct.unpack("<IHHHHHIIIHH", blob[:30])
    assert sig == 0x04034B50, "cabecalho local invalido"
    dados = blob[30 + ln + le: 30 + ln + le + cs]
    if metodo == 8:
        dados = zlib.decompress(dados, -15)
    elif metodo != 0:
        raise ValueError(f"metodo {metodo}")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    with open(dest, "xb") as fh:
        fh.write(dados)
    h = hashlib.sha256(dados).hexdigest()
    with _lock, open(MANIFEST, "a", newline="") as fh:
        csv.writer(fh).writerow([os.path.relpath(dest, RAW), h, len(dados), r["url"] + "#" + r["entrada"],
                                 time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())])


def logs(ano, workers=8):
    rows = list(csv.DictReader(open(os.path.join(ROOT, "registro", f"amostra_{ano}.csv"), encoding="utf-8")))
    ok = falhas = 0
    with ThreadPoolExecutor(workers) as ex:
        fut = {ex.submit(baixar_entrada, ano, r): r for r in rows}
        for i, f in enumerate(as_completed(fut), 1):
            try:
                f.result()
                ok += 1
            except Exception as e:
                falhas += 1
                r = fut[f]
                with _lock, open(os.path.join(RAW, f"falhas_download_{ano}.csv"), "a") as fh:
                    fh.write(f"{r['turno']},{r['uf']},{r['entrada']},{type(e).__name__}:{e}\n")
            if i % 1000 == 0:
                print(f"{i}/{len(rows)} ok={ok} falhas={falhas}", flush=True)
    print(f"fim ok={ok} falhas={falhas}")


if __name__ == "__main__":
    cmd, ano = sys.argv[1], int(sys.argv[2])
    if cmd == "quadro":
        quadro(ano)
    elif cmd == "amostra":
        amostra(ano, float(sys.argv[3]))
    elif cmd == "logs":
        w = int(sys.argv[sys.argv.index("--workers") + 1]) if "--workers" in sys.argv else 8
        logs(ano, w)

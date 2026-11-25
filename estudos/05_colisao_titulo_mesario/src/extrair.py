#!/usr/bin/env python3
"""
extrair.py -- percorre os logs baixados (2026) e grava:
  data/processed/registros_<ano>_t<turno>.csv  (um registro de mesario por linha)
  data/processed/logs_<ano>_t<turno>.csv       (resumo por arquivo de log, com SHA-256)

Uso: python extrair.py ANO TURNO [LISTA_SECOES.csv]   (ANO = 2026, 2022 ou 2024)
"""
import csv
import glob
import os
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parsing import ler_logd, parse_log  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def proc(args):
    f, ano, turno = args
    parts = f.split(os.sep)
    i = parts.index(f"t{turno}")
    uf, mun, zona, secao = parts[i + 1:i + 5]
    try:
        txt, h = ler_logd(f)
        regs, res = parse_log(txt, ano, turno)
        err = ""
    except Exception as e:  # arquivo corrompido
        regs, res, h, err = [], {}, "", f"{type(e).__name__}:{e}"
    chave = dict(uf=uf, mun=mun, zona=zona, secao=secao, arquivo=os.path.basename(f))
    return [dict(chave, **r) for r in regs], dict(chave, sha256=h, erro=err, **res)


def main(ano, turno, lista=None):
    pasta = "logs" if ano == 2026 else f"logs{ano}"
    padrao = "*.jez" if ano == 2026 else "*.logjez"
    fs = sorted(glob.glob(os.path.join(ROOT, "data", "raw", pasta, f"t{turno}", "**", padrao), recursive=True))
    if lista:
        keep = {(r["uf"], r["mun"], r["zona"], r["secao"]) for r in csv.DictReader(open(lista, encoding="utf-8"))
                if r["turno"] == str(turno)}
        fs = [f for f in fs if tuple(f.split(os.sep)[f.split(os.sep).index(f"t{turno}") + 1:][:4]) in keep]
    out = os.path.join(ROOT, "data", "processed")
    fr = open(os.path.join(out, f"registros_{ano}_t{turno}.csv"), "w", newline="", encoding="utf-8")
    fl = open(os.path.join(out, f"logs_{ano}_t{turno}.csv"), "w", newline="", encoding="utf-8")
    wr = wl = None
    with Pool(4) as pool:
        for regs, res in pool.imap_unordered(proc, [(f, ano, turno) for f in fs], chunksize=16):
            if wl is None:
                wl = csv.DictWriter(fl, fieldnames=["uf", "mun", "zona", "secao", "arquivo", "sha256", "erro",
                                                    "n_registrado", "n_ja_registrado", "n_invalido", "n_pedido",
                                                    "relogio_inconsistente", "motivo_relogio", "modelo", "ids_urna",
                                                    "n_linhas_dia", "fase_nao_oficial"])
                wl.writeheader()
            wl.writerow(res)
            for r in regs:
                if wr is None:
                    wr = csv.DictWriter(fr, fieldnames=list(r.keys()))
                    wr.writeheader()
                wr.writerow(r)
    fr.close()
    fl.close()
    print(len(fs), "logs processados")


if __name__ == "__main__":
    main(int(sys.argv[1]), int(sys.argv[2]), sys.argv[3] if len(sys.argv) > 3 else None)

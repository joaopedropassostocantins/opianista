#!/usr/bin/env python3
"""
censo.py -- coleta CENSITARIA dos logs de urna, com parsing em fluxo.

Para cada secao do quadro oficial: baixa o(s) log(s), calcula SHA-256 do arquivo original, extrai os
registros de mesario (parsing.py) e grava em CSV. O arquivo bruto NAO e mantido em disco (o censo de um
turno ocupa ~50 GB); a preservacao do original e garantida por URL + SHA-256 no manifesto, o que permite
baixa-lo de novo e provar que e o mesmo byte a byte. Arquivos brutos ja presentes em disco (Fase 0,
piloto) sao lidos do disco e preservados. As secoes envolvidas em colisoes sao baixadas de novo ao final
(coletar_brutos.py) e conferidas contra o hash.

Uso:
  python censo.py 2026 TURNO SHARD NSHARDS [--threads 8]
  python censo.py 2022 TURNO SHARD NSHARDS [--threads 6]   (le data/processed/quadro_2022.csv)
Retomavel: secoes ja presentes em logs_<ano>_t<turno>_s<shard>.csv sao puladas.
"""
import csv
import glob
import hashlib
import json
import os
import struct
import sys
import threading
import time
import urllib.error
import urllib.request
import zlib
from concurrent.futures import ThreadPoolExecutor

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parsing import ler_logd, parse_log  # noqa: E402

ROOT = os.path.abspath(os.environ.get("ESTUDO05_ROOT") or os.path.join(os.path.dirname(__file__), ".."))
OUT = os.path.join(ROOT, "data", "censo")
BASE26 = "https://resultados.tse.jus.br/oficial/ele2026/arquivo-urna"
PLEITO26 = {1: "3220", 2: "3221"}
CAMPOS_REG = ["uf", "mun", "zona", "secao", "arquivo", "titulo", "ts", "id_urna", "hash_linha", "momento",
              "eleitor_secao", "biometria", "bio_ref"]
CAMPOS_BLQ = ["uf", "mun", "zona", "secao", "arquivo", "titulo", "ts", "id_urna", "hash_linha", "momento",
              "antecedente"]
CAMPOS_LOG = ["uf", "mun", "zona", "secao", "arquivo", "url", "sha256", "bytes", "erro", "n_registrado",
              "n_ja_registrado", "n_invalido", "n_pedido", "n_conf_ok", "n_conf_nao", "relogio_inconsistente",
              "motivo_relogio", "modelo", "ids_urna", "n_linhas_dia", "fase_nao_oficial"]
lock = threading.Lock()


def http(url, rng=None, tries=7):
    last = None
    for k in range(tries):
        try:
            h = {"User-Agent": "pesquisa-academica"}
            if rng:
                h["Range"] = f"bytes={rng[0]}-{rng[1]}"
            with urllib.request.urlopen(urllib.request.Request(url, headers=h), timeout=90) as r:
                return r.read()
        except urllib.error.HTTPError as e:
            if e.code == 404:
                raise
            last = e
        except Exception as e:
            last = e
        time.sleep(min(60, 2 * 2 ** k))
    raise last


def tarefas_2026(turno):
    for f in sorted(glob.glob(os.path.join(ROOT, "data", "raw", "catalogo", f"*-p{PLEITO26[turno]}-cs.json"))):
        d = json.load(open(f, encoding="utf-8"))
        uf = d["abr"][0]["cd"]
        for m in d["abr"][0]["mu"]:
            for z in m["zon"]:
                for s in z["sec"]:
                    yield dict(uf=uf, mun=m["cd"], zona=z["cd"], secao=s["ns"])


def arquivos_2026(t, turno):
    """Devolve lista de (nome, url, bytes)."""
    p = PLEITO26[turno]
    d = f"{BASE26}/{p}/dados/{t['uf']}/{t['mun']}/{t['zona']}/{t['secao']}"
    local = os.path.join(ROOT, "data", "raw", "logs", f"t{turno}", t["uf"], t["mun"], t["zona"], t["secao"])
    aux_local = os.path.join(local, "aux.json")
    aux = open(aux_local, "rb").read() if os.path.exists(aux_local) else \
        http(f"{d}/p00{p}-{t['uf']}-m{t['mun']}-z{t['zona']}-s{t['secao']}-aux.json")
    out = []
    for hh in json.loads(aux.decode("utf-8")).get("hashes", []):
        for a in hh.get("arq", []):
            if a.get("tp") != "log":
                continue
            url = f"{d}/{hh['hash']}/{a['nm']}"
            lp = os.path.join(local, hh["hash"][:16], a["nm"])
            out.append((a["nm"], url, open(lp, "rb").read() if os.path.exists(lp) else http(url)))
    return out


def arquivos_hist(t):
    off, cs = int(t["offset"]), int(t["csize"])
    blob = http(t["url"], (off, off + 30 + 1024 + cs))
    sig, _, _, metodo, _, _, _, _, _, ln, le = struct.unpack("<IHHHHHIIIHH", blob[:30])
    if sig != 0x04034B50:
        raise ValueError("cabecalho local invalido")
    dados = blob[30 + ln + le: 30 + ln + le + cs]
    if metodo == 8:
        dados = zlib.decompress(dados, -15)
    return [(os.path.basename(t["entrada"]), t["url"] + "#" + t["entrada"], dados)]


def main(ano, turno, shard, nshards, threads):
    os.makedirs(OUT, exist_ok=True)
    tag = f"{ano}_t{turno}_s{shard}"
    p_reg, p_log = os.path.join(OUT, f"registros_{tag}.csv"), os.path.join(OUT, f"logs_{tag}.csv")
    p_fal = os.path.join(OUT, f"falhas_{tag}.csv")
    p_blq = os.path.join(OUT, f"bloqueios_{tag}.csv")
    feitos = set()
    if os.path.exists(p_log):
        for r in csv.DictReader(open(p_log, encoding="utf-8")):
            feitos.add((r["uf"], r["mun"], r["zona"], r["secao"]))
    if ano == 2026:
        todas = list(tarefas_2026(turno))
    else:
        todas = [r for r in csv.DictReader(open(os.path.join(ROOT, "data", "processed", f"quadro_{ano}.csv"),
                                                encoding="utf-8")) if r["turno"] == str(turno)]
    minhas = [t for i, t in enumerate(todas) if i % nshards == shard
              and (t["uf"], t["mun"], t["zona"], t["secao"]) not in feitos]
    print(tag, "total", len(todas), "pendentes neste shard", len(minhas), flush=True)
    freg = open(p_reg, "a", newline="", encoding="utf-8")
    flog = open(p_log, "a", newline="", encoding="utf-8")
    fblq = open(p_blq, "a", newline="", encoding="utf-8")
    wreg, wlog = csv.DictWriter(freg, CAMPOS_REG), csv.DictWriter(flog, CAMPOS_LOG)
    wblq = csv.DictWriter(fblq, CAMPOS_BLQ)
    if os.path.getsize(p_blq) == 0:
        wblq.writeheader()
    if os.path.getsize(p_reg) == 0:
        wreg.writeheader()
    if os.path.getsize(p_log) == 0:
        wlog.writeheader()
    cont = {"ok": 0, "sem_arquivo": 0, "falha": 0}

    def um(t):
        chave = {k: t[k] for k in ("uf", "mun", "zona", "secao")}
        try:
            arqs = arquivos_2026(t, turno) if ano == 2026 else arquivos_hist(t)
        except urllib.error.HTTPError as e:
            if e.code == 404:
                with lock:
                    wlog.writerow(dict(chave, erro="sem_arquivo_404"))
                    cont["sem_arquivo"] += 1
                return
            raise
        except Exception as e:
            with lock, open(p_fal, "a") as fh:
                fh.write(json.dumps(dict(chave, erro=f"{type(e).__name__}:{e}")) + "\n")
                cont["falha"] += 1
            return
        linhas_reg, linhas_log, linhas_blq = [], [], []
        for nome, url, dados in arqs:
            h = hashlib.sha256(dados).hexdigest()
            try:
                txt, _ = ler_logd(dados)
                regs, res = parse_log(txt, ano, turno)
                err = ""
            except Exception as e:
                regs, res, err = [], {}, f"{type(e).__name__}:{e}"
            base = dict(chave, arquivo=nome)
            linhas_blq += [dict(base, **b) for b in res.pop("bloqueios", [])]
            linhas_log.append(dict(base, url=url, sha256=h, bytes=len(dados), erro=err, **res))
            linhas_reg += [dict(base, **r) for r in regs]
        if not arqs:
            linhas_log.append(dict(chave, erro="aux_sem_log"))
        with lock:
            wreg.writerows(linhas_reg)
            wblq.writerows(linhas_blq)
            wlog.writerows(linhas_log)
            cont["ok"] += 1

    t0 = time.time()
    with ThreadPoolExecutor(threads) as ex:
        for i, _ in enumerate(ex.map(um, minhas), 1):
            if i % 2000 == 0:
                with lock:
                    freg.flush()
                    fblq.flush()
                    flog.flush()
                el = time.time() - t0
                print(f"{tag} {i}/{len(minhas)} {cont} {i / el:.1f}/s", flush=True)
    freg.close()
    fblq.close()
    flog.close()
    print(tag, "fim", cont, flush=True)


if __name__ == "__main__":
    a = sys.argv
    th = int(a[a.index("--threads") + 1]) if "--threads" in a else 8
    main(int(a[1]), int(a[2]), int(a[3]), int(a[4]), th)

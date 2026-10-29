#!/usr/bin/env python3
"""
Baixa arquivos de urna por secao do Portal Resultados do TSE, para os pleitos
cujos pacotes por UF ainda nao estao no Portal de Dados Abertos (2o turno de
2026: pleito 3221; 1o turno de 2026: pleito 3220).

Estrutura de caminhos lida do arquivo oficial ele-c.json (Portal Resultados):
  config: <base>/<ambiente>/<ciclo>/arquivo-urna/<cd_pleito>/config/<uf>/<uf>-p<pleito 6 dig>-cs.json
  dados:  <base>/<ambiente>/<ciclo>/arquivo-urna/<cd_pleito>/dados/<uf>/<municipio>/<zona>/<secao>/<hash>/<arquivo>

Trava do protocolo v1.1: o 2o turno de 2026 so e baixado com uma emenda que
registre dt* e o diagnostico de poder (--emenda-liberacao-2t2026).
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

BASE = "https://resultados.tse.jus.br"
AMBIENTE = "oficial"
UA = "opianista-resultados-secoes/0.1 (pesquisa reprodutivel)"
PLEITOS_BLOQUEADOS = {"3221"}


def baixar(url: str, tentativas: int = 4, timeout: int = 60) -> bytes:
    ultimo = None
    for i in range(tentativas):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": UA})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            ultimo = exc
            time.sleep(1.5 * (i + 1))
    raise RuntimeError(f"falha ao baixar {url}: {ultimo}")


def secoes_do_config(cfg: dict) -> list[dict]:
    """Percorre abr -> mu -> zon -> sec -> hash; devolve uma entrada por secao com o hash escolhido."""
    saida = []
    for abr in cfg.get("abr", []):
        for mu in abr.get("mu", []):
            for zon in mu.get("zon", []):
                for sec in zon.get("sec", []):
                    hashes = sec.get("hash", []) or []
                    totalizados = [h for h in hashes if str(h.get("st", "")).lower().startswith("totaliz")]
                    escolhido = (totalizados or hashes or [None])[-1]
                    saida.append({
                        "municipio": str(mu.get("cd", "")), "zona": str(zon.get("cd", "")),
                        "secao": str(sec.get("ns", "")),
                        "hash": None if escolhido is None else str(escolhido.get("hash", "")),
                        "situacao": None if escolhido is None else str(escolhido.get("st", "")),
                        "arquivos": [] if escolhido is None else list(escolhido.get("nmarq", []) or []),
                        "n_hashes": len(hashes),
                    })
    return saida


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--uf", required=True)
    ap.add_argument("--pleito", required=True, help="3220 (1T 2026) ou 3221 (2T 2026)")
    ap.add_argument("--ciclo", default="ele2026")
    ap.add_argument("--extensoes", default="logjez,jez,imgbu", help="extensoes a baixar, separadas por virgula")
    ap.add_argument("--saida", type=Path, required=True)
    ap.add_argument("--manifesto", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--so-config", action="store_true", help="baixa apenas o config e descreve a estrutura")
    ap.add_argument("--emenda-liberacao-2t2026", type=Path, default=None)
    args = ap.parse_args(argv)

    uf = args.uf.lower()
    pleito = str(int(args.pleito))
    raiz = f"{BASE}/{AMBIENTE}/{args.ciclo}/arquivo-urna/{pleito}"
    url_cfg = f"{raiz}/config/{uf}/{uf}-p{int(pleito):06d}-cs.json"
    cfg_bytes = baixar(url_cfg)
    args.saida.mkdir(parents=True, exist_ok=True)
    (args.saida / f"{uf}-p{int(pleito):06d}-cs.json").write_bytes(cfg_bytes)
    cfg = json.loads(cfg_bytes.decode("utf-8"))
    secoes = secoes_do_config(cfg)
    extensoes = tuple("." + e.strip().lower() for e in args.extensoes.split(",") if e.strip())
    exemplos = sorted({a.rsplit(".", 1)[-1] for s in secoes[:200] for a in s["arquivos"]})
    resumo = {"url_config": url_cfg, "sha256_config": hashlib.sha256(cfg_bytes).hexdigest(),
              "secoes": len(secoes), "sem_hash": sum(1 for s in secoes if not s["hash"]),
              "situacoes": sorted({str(s["situacao"]) for s in secoes}),
              "extensoes_disponiveis": exemplos, "chaves_topo": sorted(cfg.keys())}
    print(json.dumps(resumo, ensure_ascii=False))
    if args.so_config:
        args.manifesto.write_text(json.dumps(resumo, ensure_ascii=False, indent=2), encoding="utf-8")
        return 0

    if pleito in PLEITOS_BLOQUEADOS:
        emenda = args.emenda_liberacao_2t2026
        if emenda is None or not emenda.is_file():
            raise SystemExit("2T 2026 bloqueado: informe --emenda-liberacao-2t2026 (protocolo v1.1)")
        texto = emenda.read_text(encoding="utf-8")
        if "dt*" not in texto or "poder" not in texto.lower():
            raise SystemExit("a emenda informada nao registra dt* e o diagnostico de poder")

    tarefas = []
    for s in secoes:
        if not s["hash"]:
            continue
        for nome in s["arquivos"]:
            if nome.lower().endswith(extensoes):
                url = f"{raiz}/dados/{uf}/{s['municipio']}/{s['zona']}/{s['secao']}/{s['hash']}/{nome}"
                tarefas.append((url, args.saida / "arquivos" / nome))
    registros, falhas = [], 0
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futuros = {pool.submit(baixar, url): (url, destino) for url, destino in tarefas}
        for fut in as_completed(futuros):
            url, destino = futuros[fut]
            try:
                dados = fut.result()
                destino.parent.mkdir(parents=True, exist_ok=True)
                destino.write_bytes(dados)
                registros.append({"url": url, "arquivo": destino.name, "bytes": len(dados),
                                  "sha256": hashlib.sha256(dados).hexdigest()})
            except Exception as exc:
                falhas += 1
                registros.append({"url": url, "arquivo": destino.name, "erro": str(exc)[:200]})
    resumo.update({"arquivos_pedidos": len(tarefas), "falhas": falhas})
    args.manifesto.write_text(json.dumps({"resumo": resumo, "arquivos": sorted(registros, key=lambda r: r["arquivo"])},
                                         ensure_ascii=False, indent=1), encoding="utf-8")
    print(json.dumps(resumo, ensure_ascii=False))
    return 0 if falhas == 0 else 3


if __name__ == "__main__":
    raise SystemExit(main())

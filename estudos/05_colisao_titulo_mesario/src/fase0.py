#!/usr/bin/env python3
"""
fase0.py -- Fase 0 do 2o turno de 2026: vocabulario do log, com exemplo de linha e posicao dos campos.

Sorteia 30 secoes (6 em cada uma de TO, SP, BA, RS e AM; semente 20261025) do catalogo do 2o turno
(pleito 3221), baixa os logs (originais preservados em data/raw/fase0_2t, SHA-256 no manifesto), e gera:
  registro/fase0_2t_vocabulario.md   dicionario de mensagens com exemplo e posicao
  registro/fase0_2t_sequencias.csv   sequencias de mensagens por tentativa de registro de mesario
  registro/fase0_2t_amostra.csv      secoes sorteadas
Os titulos que aparecem nos exemplos sao mascarados (apenas os 2 primeiros e os 4 ultimos digitos
substituidos por 'X'), de modo que nenhum titulo completo vai para o Git.

Uso: python fase0.py
"""
import csv
import hashlib
import json
import os
import random
import re
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from censo import http, BASE26  # noqa: E402
from parsing import ler_logd  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SEMENTE = 20261025
UFS = ["to", "sp", "ba", "rs", "am"]
DATA2T = "25/10/2026"
PADROES = [
    ("inicio_registro_mesario", r"^Operador indagado se ocorrerá registro de mesários$|^Registrando mesários"),
    ("digitacao_titulo_mesario", r"^Pedido de leitura da biometria do mesário \d{12}$"),
    ("registro_presenca_mesario", r"^Mesário \d{12} registrado$"),
    ("nao_e_eleitor_da_secao", r"^Mesário \d{12} não é eleitor da seção$"),
    ("e_eleitor_da_secao", r"^Mesário \d{12} é eleitor da seção$"),
    ("bloqueio_ja_registrado", r"^Mesário \d{12} já registrado$"),
    ("titulo_invalido_mesario", r"^Digitado título inválido para o registro de mesário$"),
    ("biometria_coincide", r"^Realizada a conferência da biometria do mesário$"),
    ("biometria_nao_coincide", r"^Digital capturada não corresponde a digital do eleitor"),
    ("limite_mesarios", r"^Limite de mesários registrados atingido"),
    ("habilitacao_eleitor", r"^Eleitor foi habilitado$"),
    ("identificador_eleitor", r"^Identificador digitado pelo mesário foi"),
    ("titulo_invalido_eleitor", r"^Identificador do eleitor digitado inválido$"),
    ("mesario_habilitou_eleitor", r"^Mesário \d{12} habilitou o eleitor$"),
    ("biometria_eleitor_nao_e_do_mesario", r"^Biometria coletada não é do mesário"),
    ("reinicio_logd", r"^Início das operações do logd$|^Urna ligada em"),
    ("contingencia_ou_troca", r"(?i)conting|substitu|Identificação do Modelo de Urna"),
    ("fase_ue", r"^Fase da UE:"),
    ("encerramento_titulo", r"^Título digitado para encerramento"),
]


def mascarar(txt):
    return re.sub(r"\b(\d{2})(\d{6})(\d{4})\b", lambda m: "XX" + m.group(2) + "XXXX", txt)


def main():
    rng = random.Random(SEMENTE)
    secoes = []
    for uf in UFS:
        d = json.load(open(os.path.join(ROOT, "data", "raw", "catalogo", f"{uf}-p3221-cs.json"), encoding="utf-8"))
        todas = sorted((m["cd"], z["cd"], s["ns"]) for m in d["abr"][0]["mu"] for z in m["zon"] for s in z["sec"])
        for mun, zona, sec in rng.sample(todas, 6):
            secoes.append(dict(uf=uf, mun=mun, zona=zona, secao=sec))
    os.makedirs(os.path.join(ROOT, "registro"), exist_ok=True)
    with open(os.path.join(ROOT, "registro", "fase0_2t_amostra.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, ["uf", "mun", "zona", "secao", "semente"])
        w.writeheader()
        w.writerows(dict(s, semente=SEMENTE) for s in secoes)
    voc, ex, seqs, datas = Counter(), {}, Counter(), Counter()
    man = []
    for s in secoes:
        d = f"{BASE26}/3221/dados/{s['uf']}/{s['mun']}/{s['zona']}/{s['secao']}"
        try:
            aux = json.loads(http(f"{d}/p003221-{s['uf']}-m{s['mun']}-z{s['zona']}-s{s['secao']}-aux.json"))
        except Exception:
            man.append(dict(s, arquivo="", sha256="", url="sem_arquivo"))
            continue
        for hh in aux.get("hashes", []):
            for a in hh.get("arq", []):
                if a.get("tp") != "log":
                    continue
                url = f"{d}/{hh['hash']}/{a['nm']}"
                dados = http(url)
                dest = os.path.join(ROOT, "data", "raw", "fase0_2t", a["nm"])
                os.makedirs(os.path.dirname(dest), exist_ok=True)
                if not os.path.exists(dest):
                    open(dest, "xb").write(dados)
                man.append(dict(s, arquivo=a["nm"], sha256=hashlib.sha256(dados).hexdigest(), url=url))
                txt, _ = ler_logd(dados)
                seq = None
                for n, ln in enumerate(txt.splitlines(), 1):
                    p = ln.split("\t")
                    if len(p) < 5:
                        continue
                    datas[p[0][:10]] += 1
                    msg = p[4]
                    for nome, rx in PADROES:
                        if re.search(rx, msg):
                            k = (nome, p[3], p[0][:10] == DATA2T)
                            voc[k] += 1
                            ex.setdefault(k, (a["nm"], n, mascarar(ln)))
                    if p[3] != "VOTA" or not p[0].startswith(DATA2T):
                        continue
                    norm = re.sub(r"\d{12}", "<T>", re.sub(r"Digital capturada não corresponde.*", "<NAO_CORRESPONDE>", msg))
                    if msg.startswith("Pedido de leitura da biometria do mesário") or msg.endswith("registro de mesário"):
                        if seq:
                            seqs[" > ".join(seq)] += 1
                        seq = [norm]
                    elif seq is not None:
                        if "continua registrando" in msg or "encerrou ciclo" in msg or "finaliza registro" in msg:
                            seqs[" > ".join(seq)] += 1
                            seq = None
                        elif re.search("Mesário|Digital|biometria|Limite", msg):
                            seq.append(norm)
    with open(os.path.join(ROOT, "registro", "fase0_2t_manifesto.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, ["uf", "mun", "zona", "secao", "arquivo", "sha256", "url"])
        w.writeheader()
        w.writerows(man)
    with open(os.path.join(ROOT, "registro", "fase0_2t_sequencias.csv"), "w", newline="") as fh:
        w = csv.writer(fh)
        w.writerow(["n", "sequencia"])
        for k, v in seqs.most_common():
            w.writerow([v, k])
    linhas = ["# FASE 0 - VOCABULARIO DO LOG, 2o TURNO DE 2026 (25/10/2026)", "",
              f"Amostra: 30 secoes de {', '.join(u.upper() for u in UFS)} (semente {SEMENTE}); "
              f"{len([m for m in man if m['arquivo']])} arquivos de log. Titulos mascarados nos exemplos.", "",
              "Formato da linha (separador TAB): campo 1 = data e hora (dd/mm/aaaa hh:mm:ss); campo 2 = nivel "
              "(INFO, ALERTA, ERRO); campo 3 = identificador da urna; campo 4 = aplicacao (VOTA, GAP, SCUE, ATUE, "
              "LOGD); campo 5 = mensagem; campo 6 = hash da linha. O titulo, quando presente, e a sequencia de 12 "
              "digitos dentro do campo 5.", "",
              "| Evento | Aplicacao | No dia do 2T? | Ocorrencias | Arquivo:linha | Exemplo |", "|---|---|---|---|---|---|"]
    for (nome, app, dia), v in sorted(voc.items()):
        arq, n, ln = ex[(nome, app, dia)]
        linhas.append(f"| {nome} | {app} | {'sim' if dia else 'nao'} | {v} | {arq}:{n} | `{ln.replace('|', '/')[:160]}` |")
    linhas += ["", "Datas presentes nos logs do 2T (linhas por data):", ""]
    linhas += [f"- {k}: {v}" for k, v in sorted(datas.items(), key=lambda x: x[0][6:] + x[0][3:5] + x[0][:2])]
    open(os.path.join(ROOT, "registro", "fase0_2t_vocabulario.md"), "w", encoding="utf-8").write("\n".join(linhas) + "\n")
    print("\n".join(linhas[:60]))
    print(seqs.most_common(15))


if __name__ == "__main__":
    main()

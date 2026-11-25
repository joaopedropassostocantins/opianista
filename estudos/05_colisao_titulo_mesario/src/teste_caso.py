#!/usr/bin/env python3
"""
teste_caso.py -- teste de caso de cada colisao (emenda 05), com o log bruto do cache seletivo.

Entradas: data/outputs/<ano>_t<turno>/colisoes.csv (simulacao.py), parametros.json (validacao e excesso),
          data/raw/cache_<ano>_t<turno>/ (logs originais conferidos por SHA-256), data/censo/registros_*.csv,
          data/outputs/<ano>_t<turno>/votos_outlier.csv (votos.py; opcional).
Saidas:   data/outputs/<ano>_t<turno>/colisoes_caso.csv e teste_caso_resumo.json

Regras congeladas:
  Faixa A (<1 km). Cada caso e "nao_explicado" ate prova em contrario. Prova:
    explicado_por_digitacao     ha quase-duplicado do titulo em uma das pontas;
    explicado_por_substituicao  na ponta de destino (registro mais tardio do par) o registro ocorreu num ciclo
                                "durante a votacao" OU a mesa de destino abriu com menos de 3 mesarios no ciclo
                                "antes"; E o intervalo e compativel com deslocamento a pe:
                                delta >= max(60 s, distancia_m / 1,4 m/s).
  Familias (ordem da mais estreita para a mais ampla; marca-se a primeira compativel; se nenhuma,
  "nao_classificado"; nunca a familia 6 por default):
    F0 erro_de_digitacao           compativel se ha quase-duplicado em uma ponta.
    F1 nulo_mal_especificado        eliminada para todos os casos se a classe 2 esta dentro do previsto e ha
                                    excesso agregado (parametros.json); compativel caso contrario.
    F2 procedimento_nao_documentado eliminada se o par exige velocidade > 120 km/h (mesma pessoa nas duas pontas).
    F3 erro_sistematico_software    eliminada se ha mensagem de digitacao ("Pedido de leitura da biometria do
                                    mesário T") nas duas pontas, ou se modelo/versao da urna diferem entre as pontas.
    F4 carga_ou_midia_compartilhada eliminada se as duas secoes nao compartilham nenhum outro titulo E os codigos
                                    de carga e de flashcard (boletim de urna web) diferem entre as pontas.
    F5 digitacao_intencional        eliminada se ha quase-duplicado (erro a uma distancia de titulo da secao).
    F6 registro_ficticio            compativel so com sinal positivo: falta de mensagem de digitacao numa ponta,
                                    assinatura divergente, lacuna > 300 s antes do registro, ou voto atipico
                                    (> 3 desvios das vizinhas do mesmo local); eliminada sem nenhum desses sinais.
Uso: python teste_caso.py ANO [--turno 2]
"""
import argparse
import glob
import json
import os
import sys

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from parsing import ler_logd, caso_contexto  # noqa: E402

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SEC = ["uf", "mun", "zona", "secao"]
FAMILIAS = ["F0_erro_de_digitacao", "F1_nulo_mal_especificado", "F2_procedimento_nao_documentado",
            "F3_erro_sistematico_software", "F4_carga_ou_midia_compartilhada", "F5_digitacao_intencional",
            "F6_registro_ficticio"]
VEL_MAX_KMH = 120.0
VEL_PE_MS = 1.4


def dist_edicao(a, b):
    """Damerau-Levenshtein restrita (transposicao adjacente)."""
    d = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        d[i][0] = i
    for j in range(len(b) + 1):
        d[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            c = 0 if a[i - 1] == b[j - 1] else 1
            d[i][j] = min(d[i - 1][j] + 1, d[i][j - 1] + 1, d[i - 1][j - 1] + c)
            if i > 1 and j > 1 and a[i - 1] == b[j - 2] and a[i - 2] == b[j - 1]:
                d[i][j] = min(d[i][j], d[i - 2][j - 2] + 1)
    return d[len(a)][len(b)]


def contexto_ponta(base, uf, mun, zona, secao, ano, turno, titulo):
    fs = sorted(glob.glob(os.path.join(base, uf, mun, zona, secao, "*")))
    fs = [f for f in fs if f.endswith((".jez", ".logjez"))]
    if not fs:
        return dict(cache="ausente")
    melhor = None
    for f in fs:
        txt, _ = ler_logd(f)
        c = caso_contexto(txt, ano, turno, titulo)
        if c.get("ts_primeiro_registro"):
            melhor = c
            break
        melhor = melhor or c
    melhor["cache"] = "presente"
    return melhor


def familias(c, agregado):
    """Devolve (compativeis, eliminadas, mais_estreita) segundo as regras congeladas do cabecalho."""
    comp, elim = [], []
    qd = bool(c["quase_dup_na_secao_a"]) or bool(c["quase_dup_na_secao_b"])
    (comp if qd else elim).append(FAMILIAS[0])
    (elim if agregado["f1_eliminada"] else comp).append(FAMILIAS[1])
    v = c.get("velocidade_exigida_kmh")
    (elim if (v is not None and float(v) > VEL_MAX_KMH) else comp).append(FAMILIAS[2])
    difere = ((c.get("modelo_bruto_a") and c.get("modelo_bruto_b") and c["modelo_bruto_a"] != c["modelo_bruto_b"]) or
              (c.get("versao_a") and c.get("versao_b") and c["versao_a"] != c["versao_b"]))
    (elim if ((c.get("digitacao_a") is True and c.get("digitacao_b") is True) or difere) else comp).append(FAMILIAS[3])
    mesma_carga = bool(c.get("mesma_carga_ou_flashcard"))
    (elim if (int(c.get("outros_titulos_compartilhados") or 0) == 0 and not mesma_carga) else comp).append(FAMILIAS[4])
    (elim if qd else comp).append(FAMILIAS[5])
    sinal6 = (c.get("digitacao_a") is False or c.get("digitacao_b") is False or
              c.get("assinatura_a") == "divergente" or c.get("assinatura_b") == "divergente" or
              c.get("lacuna_a") is True or c.get("lacuna_b") is True or bool(c.get("voto_atipico")))
    (comp if sinal6 else elim).append(FAMILIAS[6])
    estreita = next((f for f in FAMILIAS if f in comp), "nao_classificado")
    return comp, elim, estreita


def prova_faixa_a(c, mesa_antes):
    if c["faixa_distancia"] != "A_<1km":
        return ""
    if c["quase_dup_na_secao_a"] or c["quase_dup_na_secao_b"]:
        return "explicado_por_digitacao"
    destino = "b" if c.get("ts_ref_b", 0) >= c.get("ts_ref_a", 0) else "a"
    sec_dest = "-".join(str(c[f"{k}_{destino}"]) for k in SEC)
    ciclo_dest = c.get(f"ciclo_{destino}", "")
    incompleta = mesa_antes.get(sec_dest, 0) < 3
    dist_m = float(c["distancia_km"] or 0) * 1000
    a_pe = float(c["delta_s"]) >= max(60.0, dist_m / VEL_PE_MS)
    if (ciclo_dest == "durante" or incompleta) and a_pe:
        return "explicado_por_substituicao"
    return "nao_explicado"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("ano", type=int)
    ap.add_argument("--turno", type=int, default=2)
    ap.add_argument("--saida", default=None)
    a = ap.parse_args()
    saida = a.saida or os.path.join(ROOT, "data", "outputs", f"{a.ano}_t{a.turno}")
    col = pd.read_csv(os.path.join(saida, "colisoes.csv"), dtype=str).fillna("")
    par = json.load(open(os.path.join(saida, "parametros.json"), encoding="utf-8"))
    agregado = dict(f1_eliminada=par["veredito"].get("familia_1_nulo_mal_especificado") == "eliminada")
    vo = os.path.join(saida, "votos_outlier.csv")
    atip, carga = set(), {}
    if os.path.exists(vo):
        v = pd.read_csv(vo, dtype=str).fillna("")
        atip = set(v[v.outlier_3dp.str.lower() == "true"].sec)
        for r in v.to_dict("records"):
            carga[r["sec"]] = (r.get("carga1", ""), r.get("carga2", ""), r.get("flashcard", ""))
    R = pd.concat([pd.read_csv(f, dtype=str) for f in glob.glob(os.path.join(ROOT, "data", "censo",
                                                                             f"registros_{a.ano}_t{a.turno}_s*.csv"))])
    R["sec"] = R[SEC].agg("-".join, axis=1)
    mesa_antes = R[R.momento == "antes"].groupby("sec").titulo.nunique().to_dict()
    tit_sec = R.groupby("sec").titulo.apply(set).to_dict()
    base = os.path.join(ROOT, "data", "raw", f"cache_{a.ano}_t{a.turno}")
    out = []
    for c in col.to_dict("records"):
        for p in ("a", "b"):
            ctx = contexto_ponta(base, c[f"uf_{p}"], c[f"mun_{p}"], c[f"zona_{p}"], c[f"secao_{p}"], a.ano, a.turno,
                                 c["titulo"])
            c[f"cache_{p}"] = ctx.get("cache")
            c[f"digitacao_{p}"] = ctx.get("mensagem_digitacao")
            c[f"biometria_bruta_{p}"] = ctx.get("biometria")
            c[f"lacuna_{p}"] = ctx.get("lacuna_acima_limite")
            c[f"lacuna_s_{p}"] = ctx.get("lacuna_antes_s")
            c[f"assinatura_{p}"] = ctx.get("assinatura")
            c[f"versao_{p}"] = ctx.get("versao_aplicacao")
            c[f"modelo_bruto_{p}"] = ctx.get("modelo_urna")
            c[f"ciclo_{p}"] = ctx.get("ciclo")
            sec = "-".join(c[f"{k}_{p}"] for k in SEC)
            outros = tit_sec.get(sec, set()) - {c["titulo"]}
            c[f"dist_edicao_min_{p}"] = min((dist_edicao(c["titulo"], x) for x in outros), default=None)
            ts = [x for x in c[f"ts_{p}"].split("|") if x]
            c[f"ts_ref_{p}"] = pd.to_datetime(ts[0], format="%d/%m/%Y %H:%M:%S").timestamp() if ts else 0
            c[f"voto_atipico_{p}"] = sec in atip
        c["voto_atipico"] = c["voto_atipico_a"] or c["voto_atipico_b"]
        ka = carga.get("-".join(c[f"{k}_a"] for k in SEC), ("", "", ""))
        kb = carga.get("-".join(c[f"{k}_b"] for k in SEC), ("", "", ""))
        c["carga_a"], c["carga_b"] = "|".join(ka), "|".join(kb)
        c["mesma_carga_ou_flashcard"] = any(x and x == y for x, y in zip(ka, kb))
        c["faixa_A_prova"] = prova_faixa_a(c, mesa_antes)
        if c["exclusao"]:
            c["familias_compativeis"], c["familias_eliminadas"], c["familia_mais_estreita"] = "", "", "excluida"
        else:
            comp, elim, est = familias(c, agregado)
            c["familias_compativeis"], c["familias_eliminadas"], c["familia_mais_estreita"] = "|".join(comp), "|".join(elim), est
        out.append(c)
    df = pd.DataFrame(out)
    df.to_csv(os.path.join(saida, "colisoes_caso.csv"), index=False)
    ok = df[df.exclusao == ""] if len(df) else df
    res = dict(colisoes=len(df), nao_excluidas=len(ok),
               familia_mais_estreita=ok.familia_mais_estreita.value_counts().to_dict() if len(ok) else {},
               faixa_A=ok[ok.faixa_distancia == "A_<1km"].faixa_A_prova.value_counts().to_dict() if len(ok) else {},
               cache_ausente=int(((df.cache_a == "ausente") | (df.cache_b == "ausente")).sum()) if len(df) else 0,
               caso_nominal=ok[ok.caso_nominal_porto_seguro_casa_nova.astype(str) == "True"].drop(
                   columns=["titulo"]).to_dict("records") if len(ok) else [])
    json.dump(res, open(os.path.join(saida, "teste_caso_resumo.json"), "w"), indent=2, default=str, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k != "caso_nominal"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

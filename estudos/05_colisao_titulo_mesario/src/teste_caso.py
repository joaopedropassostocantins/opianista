#!/usr/bin/env python3
"""
teste_caso.py -- teste de caso de cada colisao (emenda 05), com o log bruto do cache seletivo.

Entradas: data/outputs/<ano>_t<turno>/colisoes.csv (simulacao.py), parametros.json (validacao e excesso),
          data/raw/cache_<ano>_t<turno>/ (logs originais conferidos por SHA-256), data/censo/registros_*.csv,
          data/outputs/<ano>_t<turno>/votos_outlier.csv (votos.py; opcional).
Saidas:   data/outputs/<ano>_t<turno>/colisoes_caso.csv e teste_caso_resumo.json

Regras congeladas (emenda 06, substituem as da emenda 05):
  Faixa A (<1 km). Estado "nao_explicado" ate prova; o quase-duplicado NAO tira o caso desse estado. Estados:
    substituicao_compativel  na ponta de destino (registro mais tardio) o registro ocorreu num ciclo "durante a
                             votacao" OU a mesa de destino abriu com menos de 3 mesarios; E delta >= max(60 s,
                             distancia_m / 1,4 m/s);
    nao_explicado            demais casos. O campo indicio_de_digitacao registra se ha quase-duplicado.
  Rotulo do caso:
    F0 (erro de digitacao) so cai quando o titulo pretendido e conhecido e a distancia de edicao ate o numero
    gravado e grande. O unico titulo pretendido observavel e o quase-duplicado (segunda digitacao correta), que
    tem distancia 1; logo F0 nunca cai por ausencia de quase-duplicado.
    Com quase-duplicado: rotulo F0. Sem quase-duplicado: rotulo "nao_classificado_entre_F0_e_F5", com a razao de
    verossimilhanca contra o acidente (1 - d), d = probabilidade de o erro ficar visivel (parametros).
    Nunca F5 por falta de quase-duplicado; a separacao F0/F5 e agregada (teste binomial da fracao de colisoes
    com quase-duplicado contra d).
  Familias F1-F6 listadas como compativeis ou eliminadas:
    F1 nulo mal especificado       eliminada se a classe 2 esta dentro do previsto e ha excesso agregado.
    F2 procedimento nao documentado eliminada se a velocidade exigida passa de 120 km/h.
    F3 erro sistematico de software eliminada se ha mensagem de digitacao nas duas pontas (so F3), ou se modelo
                                    ou versao da urna diferem.
    F4 carga ou midia compartilhada compativel se o codigo de carga 1 ou o numero da urna efetivada (unicos por
                                    urna) coincidem entre as pontas, ou se 2+ outros titulos se repetem juntos;
                                    o flashcard (compartilhado por desenho, grupos de ate 34 urnas no AC) nao conta.
    F5 digitacao intencional        compativel sempre que nao houver titulo pretendido conhecido.
    F6 registro ficticio            compativel so com sinal positivo: uma ponta sem mensagem de digitacao (sem
                                    leitura de biometria), assinatura divergente, lacuna > 300 s antes do registro,
                                    ou secao anomala no painel local (G1). Nunca por default.
  Biometria da mesma pessoa nas duas pontas nao e observavel (a urna so compara com o cadastro da propria secao).
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
    """Devolve (compativeis, eliminadas, rotulo) segundo as regras congeladas da emenda 06."""
    comp, elim = [], []
    qd = bool(c["quase_dup_na_secao_a"]) or bool(c["quase_dup_na_secao_b"])
    comp.append(FAMILIAS[0])  # F0 nunca cai sem titulo pretendido conhecido com distancia grande
    (elim if agregado["f1_eliminada"] else comp).append(FAMILIAS[1])
    v = c.get("velocidade_exigida_kmh")
    (elim if (v not in (None, "") and float(v) > VEL_MAX_KMH) else comp).append(FAMILIAS[2])
    difere = ((c.get("modelo_bruto_a") and c.get("modelo_bruto_b") and c["modelo_bruto_a"] != c["modelo_bruto_b"]) or
              (c.get("versao_a") and c.get("versao_b") and c["versao_a"] != c["versao_b"]))
    (elim if ((c.get("digitacao_a") is True and c.get("digitacao_b") is True) or difere) else comp).append(FAMILIAS[3])
    f4 = bool(c.get("mesma_carga1_ou_urna")) or int(c.get("outros_titulos_compartilhados") or 0) >= 2
    (comp if f4 else elim).append(FAMILIAS[4])
    comp.append(FAMILIAS[5])
    sinal6 = (c.get("digitacao_a") is False or c.get("digitacao_b") is False or
              c.get("assinatura_a") == "divergente" or c.get("assinatura_b") == "divergente" or
              c.get("lacuna_a") is True or c.get("lacuna_b") is True or bool(c.get("g1_em_alguma_ponta")))
    (comp if sinal6 else elim).append(FAMILIAS[6])
    rotulo = FAMILIAS[0] if qd else "nao_classificado_entre_F0_e_F5"
    return comp, elim, rotulo


def prova_faixa_a(c, mesa_antes):
    """Estado da faixa A: substituicao_compativel ou nao_explicado (o quase-duplicado nao tira do estado)."""
    if c["faixa_distancia"] != "A_<1km":
        return ""
    destino = "b" if c.get("ts_ref_b", 0) >= c.get("ts_ref_a", 0) else "a"
    sec_dest = "-".join(str(c[f"{k}_{destino}"]) for k in SEC)
    ciclo_dest = c.get(f"ciclo_{destino}", "")
    incompleta = mesa_antes.get(sec_dest, 0) < 3
    dist_m = float(c["distancia_km"] or 0) * 1000
    a_pe = float(c["delta_s"]) >= max(60.0, dist_m / VEL_PE_MS)
    return "substituicao_compativel" if (ciclo_dest == "durante" or incompleta) and a_pe else "nao_explicado"


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
    d_vis = float(par.get("visibilidade_d") or 0.0)
    pc = os.path.join(saida, "painel_colisoes.csv")
    g1 = set()
    if os.path.exists(pc):
        pcd = pd.read_csv(pc, dtype=str)
        g1 = set(pcd[pcd.grupo == "G1_colisao_e_anomala"].sec)
    vo = os.path.join(saida, "votos_outlier.csv")
    atip, carga = set(), {}
    if os.path.exists(vo):
        v = pd.read_csv(vo, dtype=str).fillna("")
        atip = set(v[v.outlier_3dp.str.lower() == "true"].sec)
        for r in v.to_dict("records"):
            carga[r["sec"]] = (r.get("carga1", ""), r.get("urna_efetivada", ""))
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
        ka = carga.get("-".join(c[f"{k}_a"] for k in SEC), ("", ""))
        kb = carga.get("-".join(c[f"{k}_b"] for k in SEC), ("", ""))
        c["carga1_urna_a"], c["carga1_urna_b"] = "|".join(ka), "|".join(kb)
        c["mesma_carga1_ou_urna"] = any(x and x == y for x, y in zip(ka, kb))
        c["g1_em_alguma_ponta"] = ("-".join(c[f"{k}_a"] for k in SEC) in g1) or ("-".join(c[f"{k}_b"] for k in SEC) in g1)
        qd = bool(c["quase_dup_na_secao_a"]) or bool(c["quase_dup_na_secao_b"])
        c["indicio_de_digitacao"] = qd
        c["razao_verossimilhanca_contra_acidente"] = None if qd else (1 / max(1e-9, 1 - d_vis))
        c["faixa_A_estado"] = prova_faixa_a(c, mesa_antes)
        if c["exclusao"]:
            c["familias_compativeis"], c["familias_eliminadas"], c["rotulo"] = "", "", "excluida"
        else:
            comp, elim, est = familias(c, agregado)
            c["familias_compativeis"], c["familias_eliminadas"], c["rotulo"] = "|".join(comp), "|".join(elim), est
        out.append(c)
    df = pd.DataFrame(out)
    df.to_csv(os.path.join(saida, "colisoes_caso.csv"), index=False)
    ok = df[df.exclusao == ""] if len(df) else df
    from scipy.stats import binomtest
    n_qd = int(ok.indicio_de_digitacao.sum()) if len(ok) else 0
    bt = binomtest(n_qd, len(ok), d_vis, alternative="less") if len(ok) and 0 < d_vis < 1 else None
    res = dict(colisoes=len(df), nao_excluidas=len(ok),
               rotulo=ok.rotulo.value_counts().to_dict() if len(ok) else {},
               separacao_agregada_F0_F5=dict(
                   colisoes_com_quase_duplicado=n_qd, fracao_observada=(n_qd / len(ok)) if len(ok) else None,
                   fracao_esperada_sob_acidente=d_vis, p_binomial_menor=(bt.pvalue if bt else None),
                   leitura=("fracao muito abaixo de d (p < 0,05): o conjunto nao tem a forma do erro de digitacao"
                            if bt and bt.pvalue < 0.05 else "compativel com a forma do erro de digitacao")),
               faixa_A=ok[ok.faixa_distancia == "A_<1km"].faixa_A_estado.value_counts().to_dict() if len(ok) else {},
               cache_ausente=int(((df.cache_a == "ausente") | (df.cache_b == "ausente")).sum()) if len(df) else 0,
               caso_nominal=ok[ok.caso_nominal_porto_seguro_casa_nova.astype(str) == "True"].drop(
                   columns=["titulo"]).to_dict("records") if len(ok) else [])
    json.dump(res, open(os.path.join(saida, "teste_caso_resumo.json"), "w"), indent=2, default=str, ensure_ascii=False)
    print(json.dumps({k: v for k, v in res.items() if k != "caso_nominal"}, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()

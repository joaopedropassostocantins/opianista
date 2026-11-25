#!/usr/bin/env python3
"""Teste das regras congeladas de familia e da prova da faixa A (teste_caso.py), com casos construidos."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from teste_caso import familias, prova_faixa_a  # noqa: E402

BASE = dict(quase_dup_na_secao_a="", quase_dup_na_secao_b="", velocidade_exigida_kmh=10.0, digitacao_a=True,
            digitacao_b=True, outros_titulos_compartilhados=0, mesma_carga_ou_flashcard=False, assinatura_a="conferida",
            assinatura_b="conferida", lacuna_a=False, lacuna_b=False, voto_atipico=False, modelo_bruto_a="UE2020",
            modelo_bruto_b="UE2020", versao_a="10.23", versao_b="10.23")
CASOS = [
    ("quase-duplicado -> F0", dict(quase_dup_na_secao_a="X"), dict(f1_eliminada=True), "F0_erro_de_digitacao"),
    ("sem excesso agregado -> F1", {}, dict(f1_eliminada=False), "F1_nulo_mal_especificado"),
    ("800 km em 22 s, digitacao nas duas pontas, sem carga comum, sem quase-dup -> F5 (F2, F3, F4 eliminadas)",
     dict(velocidade_exigida_kmh=800 / (22 / 3600)), dict(f1_eliminada=True), "F5_digitacao_intencional"),
    ("800 km em 22 s com quase-duplicado -> F0", dict(velocidade_exigida_kmh=800 / (22 / 3600),
                                                     quase_dup_na_secao_b="Y"), dict(f1_eliminada=True),
     "F0_erro_de_digitacao"),
    ("mesmo predio, velocidade baixa -> F2", dict(velocidade_exigida_kmh=0.5), dict(f1_eliminada=True),
     "F2_procedimento_nao_documentado"),
    ("sem mensagem de digitacao numa ponta, longe -> F3", dict(velocidade_exigida_kmh=5000, digitacao_b=False),
     dict(f1_eliminada=True), "F3_erro_sistematico_software"),
    ("mesma carga, longe, digitacao nas duas -> F4", dict(velocidade_exigida_kmh=5000, mesma_carga_ou_flashcard=True),
     dict(f1_eliminada=True), "F4_carga_ou_midia_compartilhada"),
    ("so voto atipico, longe -> F5 antes de F6 (F5 compativel sem quase-dup)",
     dict(velocidade_exigida_kmh=5000, voto_atipico=True), dict(f1_eliminada=True), "F5_digitacao_intencional"),
]


def main():
    ok = True
    for nome, extra, agr, esperado in CASOS:
        c = dict(BASE, **extra)
        comp, elim, est = familias(c, agr)
        bom = est == esperado
        print(("OK  " if bom else "FALHA"), nome, "| obtido:", est)
        ok &= bom
    # F6 nunca por default: sem sinal positivo, F6 eliminada
    c = dict(BASE, velocidade_exigida_kmh=5000)
    comp, elim, est = familias(c, dict(f1_eliminada=True))
    bom = "F6_registro_ficticio" in elim
    print(("OK  " if bom else "FALHA"), "F6 eliminada sem sinal positivo")
    ok &= bom
    # faixa A
    fa = dict(faixa_distancia="A_<1km", quase_dup_na_secao_a="", quase_dup_na_secao_b="", ts_ref_a=0, ts_ref_b=100,
              uf_a="ba", mun_a="1", zona_a="1", secao_a="1", uf_b="ba", mun_b="1", zona_b="1", secao_b="2",
              ciclo_a="antes", ciclo_b="durante", distancia_km=0.05, delta_s=100)
    for nome, extra, mesa, esp in (
            ("A: destino em ciclo durante, 100 s a pe -> substituicao", {}, {"ba-1-1-2": 4}, "explicado_por_substituicao"),
            ("A: 22 s, mesa completa, ciclo antes -> nao explicado", dict(delta_s=22, ciclo_b="antes"), {"ba-1-1-2": 4},
             "nao_explicado"),
            ("A: quase-duplicado -> digitacao", dict(quase_dup_na_secao_b="Y"), {}, "explicado_por_digitacao")):
        r = prova_faixa_a(dict(fa, **extra), mesa)
        bom = r == esp
        print(("OK  " if bom else "FALHA"), nome, "| obtido:", r)
        ok &= bom
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

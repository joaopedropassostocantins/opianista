#!/usr/bin/env python3
"""Teste das regras congeladas de rotulo/familias e do estado da faixa A (emenda 06)."""
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "src"))
from teste_caso import familias, prova_faixa_a  # noqa: E402

BASE = dict(quase_dup_na_secao_a="", quase_dup_na_secao_b="", velocidade_exigida_kmh=10.0, digitacao_a=True,
            digitacao_b=True, outros_titulos_compartilhados=0, mesma_carga1_ou_urna=False, assinatura_a="conferida",
            assinatura_b="conferida", lacuna_a=False, lacuna_b=False, g1_em_alguma_ponta=False,
            modelo_bruto_a="UE2020", modelo_bruto_b="UE2020", versao_a="10.23", versao_b="10.23")
AG = dict(f1_eliminada=True)


def caso(nome, extra, esperado_rotulo=None, comp=(), elim=(), agr=AG):
    c = dict(BASE, **extra)
    cp, el, rot = familias(c, agr)
    ok = (esperado_rotulo is None or rot == esperado_rotulo) and all(f in cp for f in comp) and all(f in el for f in elim)
    print(("OK  " if ok else "FALHA"), nome, "| rotulo:", rot, "| compat:", ",".join(x[:2] for x in cp),
          "| elim:", ",".join(x[:2] for x in el))
    return ok


def main():
    ok = True
    v800 = 800 / (22 / 3600)
    ok &= caso("sem quase-dup -> nao classificado entre F0 e F5 (nunca F5 sozinho)", dict(velocidade_exigida_kmh=v800),
               "nao_classificado_entre_F0_e_F5", comp=("F0_erro_de_digitacao", "F5_digitacao_intencional"),
               elim=("F2_procedimento_nao_documentado", "F3_erro_sistematico_software", "F6_registro_ficticio"))
    ok &= caso("com quase-dup -> F0", dict(quase_dup_na_secao_b="Y"), "F0_erro_de_digitacao")
    ok &= caso("digitacao nas duas pontas elimina F3 e so F3", {}, comp=("F0_erro_de_digitacao", "F5_digitacao_intencional"),
               elim=("F3_erro_sistematico_software",))
    ok &= caso("flashcard igual nao conta; carga1/urna diferentes e sem titulos repetidos -> F4 eliminada", {},
               elim=("F4_carga_ou_midia_compartilhada",))
    ok &= caso("carga1 ou urna efetivada igual -> F4 compativel", dict(mesma_carga1_ou_urna=True),
               comp=("F4_carga_ou_midia_compartilhada",))
    ok &= caso("dois outros titulos repetidos juntos -> F4 compativel", dict(outros_titulos_compartilhados=2),
               comp=("F4_carga_ou_midia_compartilhada",))
    ok &= caso("ponta sem digitacao/biometria abre F6", dict(digitacao_b=False), comp=("F6_registro_ficticio",))
    ok &= caso("G1 no painel abre F6", dict(g1_em_alguma_ponta=True), comp=("F6_registro_ficticio",))
    ok &= caso("sem sinal positivo -> F6 eliminada (nunca default)", {}, elim=("F6_registro_ficticio",))
    ok &= caso("sem excesso agregado -> F1 compativel", {}, comp=("F1_nulo_mal_especificado",),
               agr=dict(f1_eliminada=False))
    fa = dict(faixa_distancia="A_<1km", quase_dup_na_secao_a="", quase_dup_na_secao_b="", ts_ref_a=0, ts_ref_b=100,
              uf_a="ba", mun_a="1", zona_a="1", secao_a="1", uf_b="ba", mun_b="1", zona_b="1", secao_b="2",
              ciclo_a="antes", ciclo_b="durante", distancia_km=0.05, delta_s=100)
    for nome, extra, mesa, esp in (
            ("A: destino em ciclo durante, 100 s a pe -> substituicao_compativel", {}, {"ba-1-1-2": 4},
             "substituicao_compativel"),
            ("A: 22 s, mesa completa, ciclo antes -> nao_explicado", dict(delta_s=22, ciclo_b="antes"), {"ba-1-1-2": 4},
             "nao_explicado"),
            ("A: quase-dup nao tira de nao_explicado", dict(quase_dup_na_secao_b="Y", delta_s=22, ciclo_b="antes"),
             {"ba-1-1-2": 4}, "nao_explicado")):
        r = prova_faixa_a(dict(fa, **extra), mesa)
        print(("OK  " if r == esp else "FALHA"), nome, "| obtido:", r)
        ok &= r == esp
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

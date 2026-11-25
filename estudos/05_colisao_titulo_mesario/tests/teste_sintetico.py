#!/usr/bin/env python3
"""
Teste sintetico do pipeline (sem dados reais): gera secoes e mesarios ficticios com titulos validos,
planta (1) um erro de digitacao que cai no titulo de mesario de outra secao, com o titulo correto
registrado depois na mesma secao (quase-duplicado), (2) uma colisao no mesmo predio, (3) uma colisao
replicada pela mesma urna (deve ser excluida) e (4) um residuo sem explicacao. Confere a classificacao.
"""
import csv
import os
import random
import subprocess
import sys
import tempfile

AQUI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(AQUI, "..", "src"))
from parsing import titulo_valido  # noqa: E402


def titulo_aleatorio(rng, uf="27"):
    while True:
        corpo = "".join(rng.choice("0123456789") for _ in range(8))
        for dv in range(100):
            t = corpo + uf + f"{dv:02d}"
            if titulo_valido(t):
                return t


def vizinho_valido(t):
    for i in range(12):
        for c in "0123456789":
            x = t[:i] + c + t[i + 1:]
            if x != t and titulo_valido(x):
                return x
    return None


def main():
    rng = random.Random(7)
    td = tempfile.mkdtemp()
    regs, logs, geo = [], [], []
    secs = []
    for z in range(1, 41):
        sec = dict(uf="to", mun="73130", zona="0033", secao=f"{z:04d}")
        secs.append(sec)
        lat = -10.0 - (z // 10) * 1.0  # grupos de 10 secoes por "cidade" (1 grau ~ 111 km)
        geo.append(dict(sec, lat=lat, lon=-48.0, local=str(1000 + z // 2), agregada="Principal", principal=-1,
                        qt_eleitor=300))
    mesarios = {i: [titulo_aleatorio(rng) for _ in range(4)] for i in range(40)}
    # (1) erro de digitacao: na secao 0 um mesario digita o titulo de um mesario da secao 25
    alvo, certo = mesarios[25][0], None
    while certo is None:
        alvo = titulo_aleatorio(rng)
        certo = vizinho_valido(alvo)
    mesarios[25][0] = alvo
    mesarios[0][0] = certo
    # (2) mesmo predio: titulo da secao 2 tambem registrado na secao 3 (mesmo local 1001)
    # (3) replicacao: secao 6 replica linha da secao 7 (mesma urna)
    # (4) residuo: titulo da secao 12 registrado na secao 35 (cidade diferente), sem quase-duplicado
    for i, sec in enumerate(secs):
        arq = f"log{i}.jez"
        urna = f"0{i:07d}"
        ts = ["25/10/2026 07:10:00", "25/10/2026 17:10:00"]
        for k, t in enumerate(mesarios[i]):
            for j, hora in enumerate(ts):
                regs.append(dict(sec, arquivo=arq, titulo=t, ts=hora[:-2] + f"{k:02d}", id_urna=urna,
                                 hash_linha=f"H{i}{k}{j}", momento="antes" if j == 0 else "apos",
                                 eleitor_secao="0", biometria="sem_conferencia", bio_ref=""))
        logs.append(dict(sec, arquivo=arq, url="x", sha256="0" * 64, bytes=1, erro="", n_registrado=8,
                         n_ja_registrado=0, n_invalido=2, n_pedido=8, n_conf_ok=0, n_conf_nao=0,
                         relogio_inconsistente=0, motivo_relogio="", modelo="UE2020", ids_urna=urna,
                         n_linhas_dia=100, fase_nao_oficial=0))

    def extra(i, t, urna, hl, hora="25/10/2026 08:00:00"):
        regs.append(dict(secs[i], arquivo=f"log{i}.jez", titulo=t, ts=hora, id_urna=urna, hash_linha=hl,
                         momento="antes", eleitor_secao="0", biometria="sem_conferencia", bio_ref=""))

    extra(0, alvo, "00000000", "ERRO1")                 # (1)
    extra(3, mesarios[2][1], "00000003", "MESMO_PREDIO")  # (2)
    extra(6, mesarios[7][1], "00000007", "H710")        # (3) mesma urna e mesma linha
    extra(35, mesarios[12][2], "00000035", "RESIDUO")   # (4)
    # bloqueios: (5) erro de digitacao que cai em outro mesario da mesma secao; (6) redigitacao do mesmo titulo
    alvo_b, viz_b = None, None
    while viz_b is None:
        alvo_b = titulo_aleatorio(rng)
        viz_b = vizinho_valido(alvo_b)
    mesarios[30][0], mesarios[30][1] = alvo_b, viz_b
    for i in (30,):
        for k, t in enumerate(mesarios[i][:2]):
            for j, hora in enumerate(["25/10/2026 07:10:00", "25/10/2026 17:10:00"]):
                regs[:] = [r for r in regs if not (r["secao"] == secs[i]["secao"] and r["ts"] == hora[:-2] + f"{k:02d}")]
                regs.append(dict(secs[i], arquivo=f"log{i}.jez", titulo=t, ts=hora[:-2] + f"{k:02d}",
                                 id_urna=f"0{i:07d}", hash_linha=f"B{i}{k}{j}", momento="antes",
                                 eleitor_secao="0", biometria="sem_conferencia", bio_ref=""))
    blq = [dict(secs[30], arquivo="log30.jez", titulo=alvo_b, ts="25/10/2026 07:12:00", id_urna="00000030",
                hash_linha="BLQ1", momento="antes", antecedente="pedido_biometria"),
           dict(secs[31], arquivo="log31.jez", titulo=mesarios[31][0], ts="25/10/2026 15:00:00", id_urna="00000031",
                hash_linha="BLQ2", momento="durante", antecedente="pedido_biometria"),
           dict(secs[32], arquivo="log32.jez", titulo=mesarios[32][0], ts="25/10/2026 07:40:00", id_urna="00000032",
                hash_linha="BLQ3", momento="antes", antecedente="pedido_biometria"),
           dict(secs[33], arquivo="log33.jez", titulo=mesarios[33][0], ts="25/10/2026 07:13:00", id_urna="00000033",
                hash_linha="BLQ4", momento="antes", antecedente="pedido_biometria")]
    # contexto do cache: BLQ1 tem registro do mesmo titulo 2 min antes (a evidencia de erro deve prevalecer);
    # BLQ2 re-registro horas depois com votos no meio; BLQ3 reinicio 10 min antes sem voto; BLQ4 redigitacao 3 min
    ctx = []
    for i, h, sr, vr, sg, vg in ((30, "BLQ1", "", "", 120, 0), (31, "BLQ2", "", "", 28000, 250),
                                 (32, "BLQ3", 600, 0, 1800, 0), (33, "BLQ4", "", "", 180, 0)):
        ctx.append(dict(secs[i], arquivo=f"log{i}.jez", titulo="", ts="", id_urna="", hash_linha=h, reinicio_ts="",
                        seg_desde_reinicio=sr, votos_desde_reinicio=vr, registro_ts="", seg_desde_registro=sg,
                        votos_desde_registro=vg))
    os.makedirs(os.path.join(td, "censo"))
    for nome, rows in (("registros_2026_t2_s0.csv", regs), ("logs_2026_t2_s0.csv", logs),
                       ("bloqueios_2026_t2_s0.csv", blq), ("bloqueios_contexto_2026_t2.csv", ctx)):
        with open(os.path.join(td, "censo", nome), "w", newline="") as fh:
            w = csv.DictWriter(fh, list(rows[0]))
            w.writeheader()
            w.writerows(rows)
    with open(os.path.join(td, "geo.csv"), "w", newline="") as fh:
        w = csv.DictWriter(fh, list(geo[0]))
        w.writeheader()
        w.writerows(geo)
    out = os.path.join(td, "out")
    subprocess.run([sys.executable, "-I", os.path.join(AQUI, "..", "src", "simulacao.py"), "2026",
                    "--reps", "200", "--ignorar-trava", "--catalogo", td, "--entrada", os.path.join(td, "censo"), "--geo", os.path.join(td, "geo.csv"),
                    "--saida", out], check=True, stdout=subprocess.DEVNULL)
    col = list(csv.DictReader(open(os.path.join(out, "colisoes.csv"))))
    cls = {r["titulo"]: r["classificacao"] for r in col}
    esperado = {alvo: "erro_digitacao_evidenciado_por_quase_duplicado", mesarios[2][1]: "mesmo_predio_<1km",
                mesarios[7][1]: "excluida_mesma_urna(contingencia/replicacao)",
                mesarios[12][2]: "residuo_sem_explicacao_no_log"}
    ok = True
    for t, c in esperado.items():
        r = cls.get(t)
        print(("OK  " if r == c else "FALHA"), t, "esperado:", c, "obtido:", r)
        ok &= r == c
    print("colisoes detectadas:", len(col), "(esperadas 4)")
    d1 = next((r for r in col if r["titulo"] == alvo), {})
    dt_ok = d1.get("delta_s") == "3000" and d1.get("faixa_intervalo") == "30min-4h"
    print(("OK  " if dt_ok else "FALHA"), "intervalo da colisao plantada: delta", d1.get("delta_s"), "(esperado 3000 s),",
          d1.get("faixa_intervalo"), "(esperado 30min-4h)")
    ok &= dt_ok
    ok &= len(col) == 4
    import json as _json
    par = _json.load(open(os.path.join(out, "parametros.json")))
    loo_ok = par.get("loo") is True and par.get("titulos_excluidos") == 4 and par.get("pares_quase_dup_excluidos") == 1
    print(("OK  " if loo_ok else "FALHA"), "LOO: titulos excluidos", par.get("titulos_excluidos"),
          "(esperado 4); pares quase-dup excluidos", par.get("pares_quase_dup_excluidos"), "(esperado 1)")
    ok &= loo_ok
    b = {r["hash_linha"]: r["classificacao"] for r in csv.DictReader(open(os.path.join(out, "bloqueios.csv")))}
    for h, c in (("BLQ1", "erro_digitacao_para_outro_mesario_da_secao"), ("BLQ2", "redigitacao_ciclo_posterior"),
                 ("BLQ3", "bloqueio_pos_reinicio"), ("BLQ4", "redigitacao_imediata")):
        print(("OK  " if b.get(h) == c else "FALHA"), "bloqueio", h, "esperado:", c, "obtido:", b.get(h))
        ok &= b.get(h) == c
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
"""
parsing.py -- extrai, de logs de urna (logd.dat), os registros de presenca de mesario.

Formatos suportados:
  2026: <...>-log.jez  = ZIP contendo logd.dat (Latin-1)
  2022/2024: <...>.logjez = 7z contendo logd.dat (Latin-1)

Linha do log: DATA HORA \t NIVEL \t ID_URNA \t APLICACAO \t MENSAGEM \t HASH_LINHA

Dicionario de campos (Fase 0; strings identicas em 2022, 2024 e 2026):
  inicio do registro ......... "Operador indagado se ocorrerá registro de mesários"
                               "Registrando mesários (antes|durante|após) a votação"
  digitacao/pedido ........... "Pedido de leitura da biometria do mesário <T>"
  registro (UNIDADE) ......... "Mesário <T> registrado"
  bloqueio na secao .......... "Mesário <T> já registrado"   (v2: gravado com titulo, hora, urna,
                               momento e evento antecedente; a urna recusa o titulo ja registrado nela)
  erro de digitacao (DV) ..... "Digitado título inválido para o registro de mesário"
  vinculo com a secao ........ "Mesário <T> é eleitor da seção" / "Mesário <T> não é eleitor da seção"
  habilitacao de eleitor ..... "Eleitor foi habilitado" (titulo do eleitor NAO e gravado no log)
  titulo invalido de ELEITOR . "Título inválido" / "Identificador do eleitor digitado inválido" (nao entra em p1)
  encerramento ............... "Título digitado para encerramento: <T>" (2026)
  conferencia biometrica ..... "Realizada a conferência da biometria do mesário"            (coincide)
                               "Digital capturada não corresponde a digital do eleitor: ..." (nao coincide)
                               So ocorre quando o titulo digitado E eleitor da secao; o registro prossegue
                               mesmo com "não corresponde" (a urna nao bloqueia).

Regras de exclusao aplicadas aqui (definidas antes de ver resultados):
  - somente aplicacao VOTA, somente linhas com data igual a data oficial do turno;
  - somente sessoes cuja "Fase da UE" mais recente seja "Oficial" (exclui treinamento/simulado);
  - log com relogio inconsistente: registro de mesario fora de 05:00-23:59 do dia do turno, ou
    retrocesso > 300 s entre linhas VOTA consecutivas do dia do turno -> marcado e excluido da analise.
"""
import hashlib
import io
import re
import sys
import zipfile
from collections import Counter
from datetime import datetime

DATAS = {
    (2026, 1): "04/10/2026", (2026, 2): "25/10/2026",
    (2022, 1): "02/10/2022", (2022, 2): "30/10/2022",
    (2024, 1): "06/10/2024", (2024, 2): "27/10/2024",
}

R_REG = re.compile(r"^Mesário (\d{12}) registrado$")
R_JA = re.compile(r"^Mesário (\d{12}) já registrado$")
R_PED = re.compile(r"^Pedido de leitura da biometria do mesário (\d{12})$")
R_ELE = re.compile(r"^Mesário (\d{12}) (é|não é) eleitor da seção$")
R_FASE = re.compile(r"Fase da UE: (\w+)")
R_MODELO = re.compile(r"Identificação do Modelo de Urna: (UE\d+)")
R_BIO = re.compile(r"^Biometria do mesário (\d{12}) encontrada nos arquivos coletados \((\d+)\)$")
M_INV = "Digitado título inválido para o registro de mesário"
M_CONF_OK = "Realizada a conferência da biometria do mesário"
P_CONF_NAO = "Digital capturada não corresponde a digital do eleitor"
M_FASES = {"Registrando mesários antes da votação": "antes",
           "Registrando mesários durante a votação": "durante",
           "Registrando mesários após a votação": "apos"}


def ler_logd(path_or_bytes):
    """Devolve (texto_latin1, sha256_do_arquivo_original)."""
    data = path_or_bytes if isinstance(path_or_bytes, (bytes, bytearray)) else open(path_or_bytes, "rb").read()
    h = hashlib.sha256(data).hexdigest()
    if data[:2] == b"PK":
        z = zipfile.ZipFile(io.BytesIO(data))
        nm = [n for n in z.namelist() if n.endswith("logd.dat")] or z.namelist()
        return z.read(nm[0]).decode("latin-1"), h
    if data[:6] == b"7z\xbc\xaf\x27\x1c":
        import py7zr
        import tempfile
        with tempfile.TemporaryDirectory() as td:
            with py7zr.SevenZipFile(io.BytesIO(data)) as z:
                z.extractall(td)
            import glob
            fs = glob.glob(td + "/**/logd.dat", recursive=True) or glob.glob(td + "/**/*", recursive=True)
            return open(fs[0], "rb").read().decode("latin-1"), h
    raise ValueError("formato desconhecido")


def parse_log(texto, ano, turno):
    """Extrai registros de mesario do dia do turno. Devolve (lista_registros, resumo_dict)."""
    data_turno = DATAS[(ano, turno)]
    regs, eleitor, bio = [], {}, {}
    res = dict(n_registrado=0, n_ja_registrado=0, n_invalido=0, n_pedido=0,
               relogio_inconsistente=0, motivo_relogio="", modelo="", ids_urna=set(),
               n_linhas_dia=0, fase_nao_oficial=0, n_conf_ok=0, n_conf_nao=0)
    conf = ""
    bloqueios = []
    ultimo_evento = ""
    fase = None
    fase_reg = None
    ult_ts = None
    for ln in texto.splitlines():
        p = ln.split("\t")
        if len(p) < 5:
            continue
        msg = p[4]
        m = R_FASE.search(msg)
        if m:
            fase = m.group(1)
        m = R_MODELO.search(msg)
        if m:
            res["modelo"] = m.group(1)
        if p[3] != "VOTA" or not p[0].startswith(data_turno):
            continue
        if fase is not None and fase != "Oficial":
            res["fase_nao_oficial"] += 1
            continue
        res["n_linhas_dia"] += 1
        res["ids_urna"].add(p[2])
        try:
            ts = datetime.strptime(p[0], "%d/%m/%Y %H:%M:%S")
        except ValueError:
            res["relogio_inconsistente"] = 1
            res["motivo_relogio"] = "timestamp_ilegivel"
            continue
        if ult_ts is not None and (ult_ts - ts).total_seconds() > 300:
            res["relogio_inconsistente"] = 1
            res["motivo_relogio"] = "retrocesso>300s"
        ult_ts = ts if ult_ts is None or ts > ult_ts else ult_ts
        if msg in M_FASES:
            fase_reg = M_FASES[msg]
            continue
        if msg == M_INV:
            res["n_invalido"] += 1
            ultimo_evento = "titulo_invalido"
            continue
        m = R_PED.match(msg)
        if m:
            res["n_pedido"] += 1
            ultimo_evento = "pedido_biometria"
            conf = "sem_conferencia"
            continue
        if msg == M_CONF_OK:
            conf = "coincide"
            res["n_conf_ok"] += 1
            continue
        if msg.startswith(P_CONF_NAO):
            conf = "nao_coincide"
            res["n_conf_nao"] += 1
            continue
        m = R_ELE.match(msg)
        if m:
            eleitor[m.group(1)] = 1 if m.group(2) == "é" else 0
            continue
        m = R_BIO.match(msg)
        if m:
            bio.setdefault(m.group(1), m.group(2))
            continue
        m = R_JA.match(msg)
        if m:
            res["n_ja_registrado"] += 1
            bloqueios.append(dict(titulo=m.group(1), ts=p[0], id_urna=p[2],
                                  hash_linha=p[5] if len(p) > 5 else "", momento=fase_reg or "",
                                  antecedente=ultimo_evento))
            continue
        m = R_REG.match(msg)
        if m:
            t = m.group(1)
            if not (5 <= ts.hour <= 23):
                res["relogio_inconsistente"] = 1
                res["motivo_relogio"] = "registro_fora_05-23h"
            regs.append(dict(titulo=t, ts=p[0], id_urna=p[2], hash_linha=p[5] if len(p) > 5 else "",
                             momento=fase_reg or "", eleitor_secao=eleitor.get(t, -1), biometria=conf))
            conf = ""
            res["n_registrado"] += 1
            ultimo_evento = "registrado"
    for r in regs:
        r["bio_ref"] = bio.get(r["titulo"], "")
    res["ids_urna"] = "|".join(sorted(res["ids_urna"]))
    res["bloqueios"] = bloqueios  # lista; consumidores devem remove-la antes de gravar o resumo
    return regs, res


# ---------- digito verificador do titulo de eleitor ----------
def titulo_valido(t):
    """Algoritmo publico do DV do titulo (12 digitos: 8 sequenciais + 2 UF + 2 DV).
    UF 01 (SP) e 02 (MG): resto 0 -> DV 1. Resto 10 -> DV 0. UF valida: 01..28."""
    if len(t) != 12 or not t.isdigit():
        return False
    d = [int(c) for c in t]
    uf = d[8] * 10 + d[9]
    if not 1 <= uf <= 28:
        return False
    s1 = sum(d[i] * (i + 2) for i in range(8)) % 11
    dv1 = 0 if s1 == 10 else s1
    if s1 == 0 and uf in (1, 2):
        dv1 = 1
    s2 = (d[8] * 7 + d[9] * 8 + dv1 * 9) % 11
    dv2 = 0 if s2 == 10 else s2
    if s2 == 0 and uf in (1, 2):
        dv2 = 1
    return d[10] == dv1 and d[11] == dv2


if __name__ == "__main__":
    ano, turno = int(sys.argv[1]), int(sys.argv[2])
    for f in sys.argv[3:]:
        txt, h = ler_logd(f)
        regs, res = parse_log(txt, ano, turno)
        print(f, h[:16], res)
        for r in regs:
            print("  ", r, titulo_valido(r["titulo"]))


# ---------- contexto dos bloqueios (lido do cache seletivo de brutos; Etapa 2 da emenda 05)
M_LOGD_INICIO = "Início das operações do logd"
M_VOTO = "O voto do eleitor foi computado"


def contexto_bloqueios(texto, ano, turno):
    """Para cada "Mesário <T> já registrado" do dia do turno, devolve o contexto temporal na mesma urna:
      reinicio_ts      : ultimo "Início das operações do logd" do dia ANTERIOR ao bloqueio e POSTERIOR ao
                         primeiro do dia (a primeira partida da manha nao e reinicio)
      votos_desde_reinicio : votos computados entre esse reinicio e o bloqueio
      registro_ts      : ultimo "Mesário <T> registrado" do mesmo titulo antes do bloqueio
      votos_desde_registro : votos computados entre esse registro e o bloqueio
    """
    data = DATAS[(ano, turno)]
    out = []
    partidas = []
    votos = []
    ult_reg = {}
    for ln in texto.splitlines():
        p = ln.split("\t")
        if len(p) < 5 or not p[0].startswith(data):
            continue
        msg = p[4]
        try:
            ts = datetime.strptime(p[0], "%d/%m/%Y %H:%M:%S")
        except ValueError:
            continue
        if p[3] == "LOGD" and msg.startswith(M_LOGD_INICIO):
            partidas.append(ts)
            continue
        if p[3] != "VOTA":
            continue
        if msg == M_VOTO:
            votos.append(ts)
            continue
        m = R_REG.match(msg)
        if m:
            ult_reg[(m.group(1), p[2])] = ts
            continue
        m = R_JA.match(msg)
        if m:
            t = m.group(1)
            rein = [x for x in partidas[1:] if x <= ts]
            r_ts = rein[-1] if rein else None
            g_ts = ult_reg.get((t, p[2]))
            out.append(dict(
                titulo=t, ts=p[0], id_urna=p[2], hash_linha=p[5] if len(p) > 5 else "",
                reinicio_ts=r_ts.strftime("%d/%m/%Y %H:%M:%S") if r_ts else "",
                seg_desde_reinicio=(ts - r_ts).total_seconds() if r_ts else "",
                votos_desde_reinicio=sum(1 for v in votos if r_ts and r_ts <= v <= ts) if r_ts else "",
                registro_ts=g_ts.strftime("%d/%m/%Y %H:%M:%S") if g_ts else "",
                seg_desde_registro=(ts - g_ts).total_seconds() if g_ts else "",
                votos_desde_registro=sum(1 for v in votos if g_ts and g_ts <= v <= ts) if g_ts else "",
                votos_no_dia_ate_bloqueio=sum(1 for v in votos if v <= ts)))
    return out


# ---------- contexto de cada ponta de uma colisao (teste de caso; emenda 05)
R_VERSAO = re.compile(r"Versão da aplicação: (.+)$")
R_ASSIN = re.compile(r"^Verificação de assinatura .*\[(\w+)\]$")
LACUNA_S = 300  # lacuna no log imediatamente antes do registro: mais de 300 s sem nenhuma linha


def caso_contexto(texto, ano, turno, titulo):
    data = DATAS[(ano, turno)]
    versao = modelo = ""
    assin = Counter()
    ult_ts = None
    ciclo = ""
    pedido = False
    bio = ""
    regs_antes = set()
    out = None
    for ln in texto.splitlines():
        p = ln.split("\t")
        if len(p) < 5:
            continue
        msg = p[4]
        m = R_VERSAO.search(msg)
        if m:
            versao = m.group(1)
        m = R_MODELO.search(msg)
        if m:
            modelo = m.group(1)
        if not p[0].startswith(data):
            continue
        try:
            ts = datetime.strptime(p[0], "%d/%m/%Y %H:%M:%S")
        except ValueError:
            continue
        m = R_ASSIN.match(msg)
        if m:
            assin[m.group(1)] += 1
        if p[3] == "VOTA":
            if msg in M_FASES:
                ciclo = M_FASES[msg]
            mp = R_PED.match(msg)
            if mp:
                pedido = mp.group(1) == titulo
                bio = ""
            elif msg == M_CONF_OK and pedido:
                bio = "coincide"
            elif msg.startswith(P_CONF_NAO) and pedido:
                bio = "nao_coincide"
            mr = R_REG.match(msg)
            if mr:
                if mr.group(1) == titulo and out is None:
                    out = dict(ts_primeiro_registro=p[0], ciclo=ciclo, mensagem_digitacao=pedido,
                               biometria=bio or ("sem_conferencia" if pedido else ""),
                               lacuna_antes_s=(ts - ult_ts).total_seconds() if ult_ts else None,
                               lacuna_acima_limite=bool(ult_ts and (ts - ult_ts).total_seconds() > LACUNA_S),
                               mesarios_registrados_antes=len(regs_antes - {titulo}),
                               mesa_incompleta=len(regs_antes - {titulo}) < 3)
                regs_antes.add(mr.group(1))
                pedido = False
        ult_ts = ts
    out = out or dict(ts_primeiro_registro="", ciclo="", mensagem_digitacao=None, biometria="",
                      lacuna_antes_s=None, lacuna_acima_limite=None, mesarios_registrados_antes=None,
                      mesa_incompleta=None)
    out.update(versao_aplicacao=versao, modelo_urna=modelo,
               assinatura=("divergente" if any(k != "SUCESSO" for k in assin) else
                           "conferida" if assin else "sem_verificacao_no_dia"))
    return out

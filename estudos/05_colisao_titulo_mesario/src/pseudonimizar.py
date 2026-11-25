#!/usr/bin/env python3
"""
pseudonimizar.py -- gera versoes publicaveis das saidas de simulacao.py, sem titulo de eleitor em claro.

Cada titulo e substituido por HMAC-SHA256(chave, titulo), truncado em 16 hexadecimais. A igualdade entre
titulos e preservada (a mesma pessoa/numero recebe o mesmo pseudonimo), o que basta para auditar
colisoes; o numero original nao e recuperavel sem a chave. A chave fica em data/chave_pseudonimo.bin
(fora do Git, gerada uma vez com secrets.token_bytes(32)). O tipo de erro e a posicao do digito
divergente sao mantidos, pois nao identificam a pessoa.

Uso: python pseudonimizar.py DIR_ENTRADA DIR_SAIDA
"""
import hashlib
import hmac
import os
import secrets
import sys

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
CHAVE = os.path.join(ROOT, "data", "chave_pseudonimo.bin")
COLUNAS_TITULO = ["titulo", "titulo_a", "titulo_b", "quase_dup_na_secao_a", "quase_dup_na_secao_b"]


def chave():
    os.makedirs(os.path.dirname(CHAVE), exist_ok=True)
    if not os.path.exists(CHAVE):
        with open(CHAVE, "xb") as fh:
            fh.write(secrets.token_bytes(32))
    return open(CHAVE, "rb").read()


def pseud(valor, k):
    if not isinstance(valor, str) or not valor:
        return valor
    return "|".join(hmac.new(k, v.encode(), hashlib.sha256).hexdigest()[:16] for v in valor.split("|"))


def posicoes(a, b):
    if not isinstance(a, str) or not isinstance(b, str) or len(a) != 12 or len(b) != 12:
        return ""
    return ",".join(str(i + 1) for i in range(12) if a[i] != b[i])


def main(entrada, saida):
    k = chave()
    os.makedirs(saida, exist_ok=True)
    for nome in sorted(os.listdir(entrada)):
        src = os.path.join(entrada, nome)
        if nome.endswith(".csv"):
            df = pd.read_csv(src, dtype=str)
            if "titulo_a" in df.columns and "titulo_b" in df.columns:
                df["posicoes_divergentes"] = [posicoes(a, b) for a, b in zip(df.titulo_a, df.titulo_b)]
            if "titulo" in df.columns:
                df["uf_do_titulo"] = df.titulo.str[8:10]
            for c in COLUNAS_TITULO:
                if c in df.columns:
                    df[c] = df[c].map(lambda v: pseud(v, k))
            df.to_csv(os.path.join(saida, nome), index=False)
        elif nome.endswith(".json"):
            with open(src, encoding="utf-8") as fi, open(os.path.join(saida, nome), "w", encoding="utf-8") as fo:
                fo.write(fi.read())
    print("pseudonimizado:", entrada, "->", saida)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])

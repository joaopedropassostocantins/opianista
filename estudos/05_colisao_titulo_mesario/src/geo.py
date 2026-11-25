#!/usr/bin/env python3
"""
geo.py -- coordenadas e eleitorado por secao (dadosabertos.tse.jus.br, eleitorado_local_votacao_<ANO>).
Saida: data/processed/geo_<ANO>.csv  (uf, mun, zona, secao, lat, lon, local, agregada, principal, qt_eleitor)
"""
import io
import os
import sys
import zipfile

import pandas as pd

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def main(ano):
    z = zipfile.ZipFile(os.path.join(ROOT, "data", "raw", "aux", f"eleitorado_local_votacao_{ano}.zip"))
    nm = [n for n in z.namelist() if n.endswith("BRASIL.csv")] or [n for n in z.namelist() if n.endswith(".csv")]
    cols = ["NR_TURNO", "SG_UF", "CD_MUNICIPIO", "NR_ZONA", "NR_SECAO", "DS_TIPO_SECAO_AGREGADA",
            "NR_SECAO_PRINCIPAL", "NR_LOCAL_VOTACAO", "NR_LATITUDE", "NR_LONGITUDE", "QT_ELEITOR_SECAO"]
    df = pd.read_csv(io.BytesIO(z.read(nm[0])), sep=";", encoding="latin-1", usecols=cols, dtype=str)
    df = df[df.NR_TURNO == "1"].copy()
    out = pd.DataFrame({
        "uf": df.SG_UF.str.lower(),
        "mun": df.CD_MUNICIPIO.str.zfill(5),
        "zona": df.NR_ZONA.str.zfill(4),
        "secao": df.NR_SECAO.str.zfill(4),
        "lat": pd.to_numeric(df.NR_LATITUDE.str.replace(",", "."), errors="coerce"),
        "lon": pd.to_numeric(df.NR_LONGITUDE.str.replace(",", "."), errors="coerce"),
        "local": df.NR_LOCAL_VOTACAO,
        "agregada": df.DS_TIPO_SECAO_AGREGADA,
        "principal": df.NR_SECAO_PRINCIPAL,
        "qt_eleitor": pd.to_numeric(df.QT_ELEITOR_SECAO, errors="coerce"),
    })
    bad = (out.lat.abs() < 1e-9) | (out.lat == -1) | (out.lon == -1) | out.lat.isna() | out.lon.isna()
    out.loc[bad, ["lat", "lon"]] = float("nan")
    out = out.drop_duplicates(["uf", "mun", "zona", "secao"])
    out.to_csv(os.path.join(ROOT, "data", "processed", f"geo_{ano}.csv"), index=False)
    print(ano, len(out), "secoes; sem coordenada:", int(out.lat.isna().sum()),
          "; eleitorado (M):", int(out.qt_eleitor.sum()))


if __name__ == "__main__":
    main(int(sys.argv[1]))

#!/usr/bin/env python3
"""Testes offline de horarios_secao.py e contraste_local.py com dados sinteticos."""
import importlib.util
import io
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


hor = load("horarios_secao")
con = load("contraste_local")

LOG = "\n".join([
    "06/10/2024 16:59:00\tINFO\t1\tVOTA\tO voto do eleitor foi computado\tX",
    "27/10/2024 08:01:00\tINFO\t1\tVOTA\tO voto do eleitor foi computado\tX",
    "27/10/2024 17:02:10\tINFO\t1\tVOTA\tO voto do eleitor foi computado\tX",
    "27/10/2024 17:03:00\tINFO\t1\tVOTA\tTitulo digitado para encerramento: 012345678901\tX",
    "27/10/2024 17:03:05\tINFO\t1\tVOTA\tProcedimento de encerramento confirmado\tX",
    "27/10/2024 17:05:00\tINFO\t1\tVOTA\tGerando arquivo de resultado [bu.dat] + [Início]\tX",
])
IMG = "Horário de abertura           08:00:01\nHorário de fechamento         17:03:05\n"


def urn_zip(path: Path, prefix="o00453to7344000290104"):
    inner = io.BytesIO()
    with zipfile.ZipFile(inner, "w") as z:
        z.writestr("logd.dat", LOG.encode("latin1"))
    with zipfile.ZipFile(path, "w") as z:
        z.writestr(prefix + "-log.jez", inner.getvalue())
        z.writestr(prefix + "-imgbu.dat", IMG.encode("latin1"))
        z.writestr("leiame.pdf", b"x")


class HorariosTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)

    def tearDown(self):
        self.tmp.cleanup()

    def test_extracts_only_election_day_and_no_personal_data(self):
        z = self.path / "bu_imgbu_logjez_rdv_vscmr_2024_2t_TO.zip"
        urn_zip(z)
        out = self.path / "h.csv"
        self.assertEqual(hor.main(["--zip", str(z), "--data-eleicao", "27/10/2024", "--out", str(out)]), 0)
        text = out.read_text("utf-8")
        self.assertNotIn("012345678901", text)
        row = hor.extract(z, "27/10/2024")[0]
        self.assertEqual((row["municipio"], row["zona"], row["secao"]), ("73440", "29", "104"))
        self.assertEqual(row["primeiro_voto_log"], "08:01:00")
        self.assertEqual(row["ultimo_voto_log"], "17:02:10")
        self.assertEqual(row["votos_computados_log"], 2)
        self.assertEqual(row["fechamento_bu"], "17:03:05")
        self.assertEqual(row["encerramento_confirmado_log"], "17:03:05")
        self.assertEqual(row["bu_gerado_log"], "17:05:00")

    def test_blocks_2t2026_zip(self):
        z = self.path / "bu_imgbu_logjez_rdv_vscmr_2026_2t_TO.zip"
        urn_zip(z)
        out = self.path / "h.csv"
        self.assertEqual(hor.main(["--zip", str(z), "--data-eleicao", "25/10/2026", "--out", str(out)]), 2)
        self.assertFalse(out.exists())


class ContrasteTests(unittest.TestCase):
    def test_constant_within_local_shift_is_recovered(self):
        units = []
        for loc in range(10):
            base = 0.4 + 0.02 * loc
            for i in range(4):
                treated = int(i == 0)
                units.append({"local": loc, "w": 100 + i, "T": treated,
                              "y": base + 0.05 * treated + 0.001 * i})
        res = con.fe_contrast(units)
        self.assertTrue(res["estimavel"])
        self.assertAlmostEqual(res["beta"], 0.05 - 0.0015, delta=0.002)
        self.assertEqual(res["locais_informativos"], 10)

    def test_coherence_checks_of_amendment_01(self):
        ok = {"comparecimento": "2", "votos_computados_log": "2", "fechamento_bu": "17:03:05",
              "encerramento_confirmado_log": "17:03:04", "ultimo_voto_log": "17:02:10",
              "bu_gerado_log": "17:05:00"}
        self.assertEqual(con.coherence_failure(ok), "")
        self.assertEqual(con.coherence_failure({**ok, "votos_computados_log": "3"}), "incoerente_log_x_bu")
        self.assertEqual(con.coherence_failure({**ok, "fechamento_bu": "17:03:09"}), "incoerente_fechamento")
        self.assertEqual(con.coherence_failure({**ok, "ultimo_voto_log": "17:04:00"}), "incoerente_ordem")
        self.assertEqual(con.coherence_failure({**ok, "bu_gerado_log": ""}), "incoerente_campo_ausente")

    def test_winner_outcome_is_per_municipality(self):
        rows = []
        for mun, win in (("1", "10"), ("2", "20")):
            for i, t in enumerate(("16:59:00", "17:01:00")):
                rows.append({"uf": "TO", "municipio": mun, "zona": "1", "local": "9",
                             "votos_cargo": json.dumps({"10": 60 if win == "10" else 40, "20": 40 if win == "10" else 60}),
                             "ultimo_voto_log": t})
        units, lost, winners = con.build_units(rows, "ultimo_voto_log", "17:00:00", "vencedor", coerencia=False)
        self.assertEqual(winners, {"TO/1": "10", "TO/2": "20"})
        self.assertTrue(all(abs(u["y"] - 0.6) < 1e-9 for u in units))

    def test_locals_without_both_classes_do_not_contribute(self):
        units = [{"local": 1, "w": 1, "T": 1, "y": 0.9}, {"local": 1, "w": 1, "T": 1, "y": 0.8},
                 {"local": 2, "w": 1, "T": 0, "y": 0.1}]
        self.assertFalse(con.fe_contrast(units)["estimavel"])


if __name__ == "__main__":
    unittest.main()

"""Testes da trava do coletor do Estudo 03 (versao incorporada pelo PR #4).

O bloqueio generico de 2026 (D4) foi substituido por duas regras: o turno passa a ser
identificado pelo proprio recurso, o que elimina a ambiguidade 1T/2T da busca CKAN, e o
2T 2026 so e baixado com uma emenda que registre dt* e o diagnostico de poder. Os testes
rodam sem rede.
"""
import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path

MODULE = Path(__file__).resolve().parents[1] / "03_pianista" / "etapas" / "01_coleta" / "coleta.py"
spec = importlib.util.spec_from_file_location("original_collector", MODULE)
mod = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = mod
spec.loader.exec_module(mod)


def registro(periodo: str, url: str):
    return mod.SourceRecord("t", periodo, "x", "p", "P", "u", "r", url, "ZIP", "", "cc-by", "DESCOBERTO", "")


class CollectorGuardTests(unittest.TestCase):
    def test_turno_vem_do_recurso_e_nao_do_termo_de_busca(self):
        r = lambda u, n="": {"url": u, "name": n}
        self.assertEqual(mod.detect_period(r("https://x/bu_imgbu_logjez_rdv_vscmr_2026_1t_TO.zip")), "1T2026")
        self.assertEqual(mod.detect_period(r("https://x/bu_imgbu_logjez_rdv_vscmr_2026_2t_TO.zip")), "2T2026")
        self.assertEqual(mod.detect_period(r("https://x/y.zip", "TO - Segundo turno - 2022")), "2T2022")
        self.assertIsNone(mod.detect_period(r("https://x/y.zip", "sem informacao")))

    def test_2t2026_nunca_baixado_sem_emenda(self):
        with tempfile.TemporaryDirectory() as temp:
            d = Path(temp)
            inv = mod.maybe_download([registro("2T2026", "https://x/a_2026_2t_TO.zip")], d, d / "inv.csv", 5, None)
            self.assertEqual(inv, [])
            self.assertFalse((d / "2026").exists())

    def test_emenda_sem_dtstar_e_rejeitada(self):
        with tempfile.TemporaryDirectory() as temp:
            emenda = Path(temp) / "emenda.md"
            emenda.write_text("texto sem os parametros exigidos", encoding="utf-8")
            with self.assertRaises(SystemExit):
                mod.main(["--download", "--periodos", "2T2026", "--output-dir", str(Path(temp) / "out"),
                          "--emenda-liberacao-2t2026", str(emenda)])

    def test_emenda_inexistente_e_rejeitada(self):
        with tempfile.TemporaryDirectory() as temp:
            with self.assertRaises(SystemExit):
                mod.main(["--download", "--periodos", "2T2026", "--output-dir", str(Path(temp) / "out"),
                          "--emenda-liberacao-2t2026", str(Path(temp) / "nao_existe.md")])


if __name__ == "__main__":
    unittest.main()

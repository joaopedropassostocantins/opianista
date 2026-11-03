"""Testes sinteticos do diagnostico integral (sem nenhum dado eleitoral real)."""
import importlib.util
import unittest
from pathlib import Path

caminho = Path(__file__).with_name("dia_integral.py")
spec = importlib.util.spec_from_file_location("dia_integral", caminho)
modulo = importlib.util.module_from_spec(spec)
spec.loader.exec_module(modulo)

def linha(seg, modo="BIO", periodo="SINTETICO", secao="101"):
    return {"uf": "TO", "periodo": periodo, "municipio": "123", "zona": "1",
            "secao": secao, "seg": str(seg), "modo": modo}

class TesteDiaIntegral(unittest.TestCase):
    def test_cobertura_8h_15h_e_depois_das_19h(self):
        eventos = [linha(8*3600+4), linha(15*3600+35), linha(19*3600+25)]
        r = modulo.analisar_linhas(eventos, "SINTETICO")
        s = r["secoes"][0]
        self.assertEqual(s["eventos_habilitacao_dia_inteiro"], 3)
        self.assertEqual(list(s["horas"]), ["08", "15", "19"])

    def test_intervalos_nao_reiniciam_na_troca_de_hora(self):
        eventos = [linha(8*3600+3598, "NB_MAN"), linha(9*3600, "NB_SEM"),
                   linha(9*3600+2, "NB_SEM")]
        r = modulo.analisar_linhas(eventos, "SINTETICO", dt=2)
        self.assertEqual(r["secoes"][0]["rajadas_nb"], 1)

    def test_desconhecido_nao_se_torna_nb(self):
        r = modulo.analisar_linhas([linha(29000, "DESC")], "SINTETICO", dt=60)
        s = r["secoes"][0]
        self.assertEqual(s["sem_biometria_observada"], 0)
        self.assertEqual(s["modo_indeterminado"], 1)

    def test_2t2026_bloqueado_antes_da_leitura(self):
        class NaoPodeLer:
            def __iter__(self):
                raise AssertionError("NAO PODE LER")
        with self.assertRaises(modulo.Bloqueado):
            modulo.analisar_linhas(NaoPodeLer(), "2T2026")
        with self.assertRaises(modulo.Bloqueado):
            modulo.validar_preflight("1T2026", Path("recurso_2026_2t_TO.csv"))

    def test_nao_aceita_periodo_misto(self):
        with self.assertRaises(modulo.Bloqueado):
            modulo.analisar_linhas([linha(30000, periodo="2T2026")], "SINTETICO")

    def test_nao_reduz_votos_a_habilitacoes(self):
        r = modulo.analisar_linhas([linha(34000)], "SINTETICO")
        self.assertIn("NAO horario do ultimo voto", r["limite"])

    def test_segundo_invalido(self):
        with self.assertRaises(modulo.Bloqueado):
            modulo.analisar_linhas([linha(90000)], "SINTETICO")

if __name__ == "__main__":
    unittest.main()

#!/usr/bin/env python3
"""Testes offline, sem leitura de qualquer dado real de 2T2026."""
import hashlib
import importlib.util
import json
import tempfile
import unittest
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent
SPEC = importlib.util.spec_from_file_location("pipeline_placebo", ROOT / "pipeline_placebo.py")
pipe = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(pipe)
HEADER = "ANO_ELEICAO;NR_TURNO;SG_UF;CD_MUNICIPIO;NR_ZONA;NR_SECAO;CD_CARGO;NR_VOTAVEL;QT_VOTOS\n"
def row(year, turn, section, cargo, candidate, amount):
    return f"{year};{turn};TO;100;1;{section};{cargo};{candidate};{amount}\n"

class PlaceboTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.path = Path(self.tmp.name)
    def tearDown(self):
        self.tmp.cleanup()
    def fixture(self, period="2T2024", bytes_data=None, suffix=".csv"):
        data = bytes_data or (HEADER + row(2024,2,10,11,40,35)
               + row(2024,2,10,11,50,30) + row(2024,2,10,11,95,2)
               + row(2024,2,10,11,96,3) + row(2024,2,11,11,40,42)
               + row(2024,2,11,11,50,39)).encode("cp1252")
        f = self.path / ("placebo" + suffix)
        f.write_bytes(data)
        m = {"period":period, "isolated":True, "sha256":hashlib.sha256(data).hexdigest(),
             "origin_url":"https://cdn.tse.jus.br/ficticio/apenas-teste",
             "resource_id":"recurso-ficticio", "license":"TEST_FIXTURE"}
        manifest = self.path / "manifest.json"
        manifest.write_text(json.dumps(m), "utf-8")
        return f, manifest
    def test_normal_2024_all_votes_by_section(self):
        f,m=self.fixture()
        output=pipe.parse_file(f,m,"2T2024")
        self.assertEqual(output["section_count"],2)
        self.assertEqual(output["total_votes"],151)
        self.assertEqual(output["total_valid"],146)
        self.assertEqual(output["temporal_test"],"NAO_ESTIMAVEL_SEM_FONTE_EXTERNA_E_LOCAL_DE_VOTACAO")
        self.assertTrue(all(x["closure_status"]=="indeterminado" for x in output["sections"]))
        self.assertEqual(output["sections"][0]["votes_by_number"],{"40":35,"50":30})
    def test_normal_2026_first_round_only(self):
        data=(HEADER+row(2026,1,12,1,13,51)+row(2026,1,12,1,22,48)+row(2026,1,12,1,55,9)).encode()
        f,m=self.fixture("1T2026",data)
        result=pipe.parse_file(f,m,"1T2026")
        self.assertEqual(result["total_valid"],108)
        self.assertEqual(result["sections"][0]["votes_by_number"]["55"],9)
    def test_ban_2026_second_round_period_before_opening(self):
        f,m=self.fixture()
        with self.assertRaises(pipe.Blocked):
            pipe.parse_file(f,m,"2T2026")
    def test_reject_mixed_turns_even_when_manifest_claims_first(self):
        data=(HEADER+row(2026,1,12,1,13,51)+row(2026,2,12,1,13,99)).encode()
        f,m=self.fixture("1T2026",data)
        with self.assertRaisesRegex(pipe.Blocked, "outro ano/turno"):
            pipe.parse_file(f,m,"1T2026")
    def test_reject_unisolated_manifest(self):
        f,m=self.fixture()
        payload=json.loads(m.read_text())
        payload["isolated"]=False
        m.write_text(json.dumps(payload))
        with self.assertRaises(pipe.Blocked):
            pipe.parse_file(f,m,"2T2024")
    def test_reject_wrong_digest_before_parser(self):
        f,m=self.fixture()
        f.write_bytes(b"outro arquivo")
        with self.assertRaisesRegex(pipe.Blocked, "SHA-256"):
            pipe.parse_file(f,m,"2T2024")
    def test_reject_explicit_2t2026_filename_even_if_label_2024(self):
        f,m=self.fixture()
        target=self.path/"boletim_2T2026.csv"
        f.rename(target)
        with self.assertRaises(pipe.Blocked):
            pipe.parse_file(target,m,"2T2024")
    def test_reject_2026_mixed_resource_metadata(self):
        f,m=self.fixture("1T2026")
        payload=json.loads(m.read_text())
        payload["origin_url"]="https://cdn.tse.jus.br/2026_2T_arquivo.csv"
        m.write_text(json.dumps(payload))
        with self.assertRaises(pipe.Blocked):
            pipe.parse_file(f,m,"1T2026")
    def test_zip_one_csv_only(self):
        data=(HEADER+row(2024,2,10,11,40,35)).encode()
        f=self.path/"safe.zip"
        with zipfile.ZipFile(f,"w") as z:
            z.writestr("safe.csv", data)
        _,m=self.fixture()
        payload=json.loads(m.read_text())
        payload["sha256"]=hashlib.sha256(f.read_bytes()).hexdigest()
        m.write_text(json.dumps(payload))
        out=pipe.parse_file(f,m,"2T2024")
        self.assertEqual(out["total_votes"],35)
    def test_no_output_on_error(self):
        f,m=self.fixture()
        out=self.path/"result.json"
        code=pipe.main(["--period","2T2026","--csv",str(f),"--manifest",str(m),"--out",str(out)])
        self.assertEqual(code,2)
        self.assertFalse(out.exists())

if __name__=="__main__":
    unittest.main()

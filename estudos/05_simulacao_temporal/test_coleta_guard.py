import importlib.util
import tempfile
import unittest
from pathlib import Path

MODULE=Path(__file__).resolve().parents[1]/"03_pianista"/"etapas"/"01_coleta"/"coleta.py"
import sys
s=importlib.util.spec_from_file_location("original_collector",MODULE)
mod=importlib.util.module_from_spec(s)
sys.modules[s.name]=mod
s.loader.exec_module(mod)

class CollectorGuardTests(unittest.TestCase):
    def test_default_download_is_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/"out"
            with self.assertRaisesRegex(SystemExit,"BLOQUEADO D4"):
                mod.main(["--download","--output-dir",str(out)])
            self.assertFalse(out.exists(),"Bloqueio ocorre antes de escrita/discovery")
    def test_explicit_1t2026_download_blocked_as_resource_ambiguous(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/"out"
            with self.assertRaisesRegex(SystemExit,"BLOQUEADO D4"):
                mod.main(["--download","--periodos","1T2026","--output-dir",str(out)])
            self.assertFalse(out.exists())
    def test_explicit_2t2026_download_blocked(self):
        with tempfile.TemporaryDirectory() as temp:
            out=Path(temp)/"out"
            with self.assertRaisesRegex(SystemExit,"BLOQUEADO D4"):
                mod.main(["--download","--periodos","2T2026","--output-dir",str(out)])
            self.assertFalse(out.exists())
if __name__=="__main__": unittest.main()

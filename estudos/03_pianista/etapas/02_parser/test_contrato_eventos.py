import importlib.util
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

HERE=Path(__file__).resolve().parent
spec=importlib.util.spec_from_file_location("contract",HERE/"contrato_eventos.py")
m=importlib.util.module_from_spec(spec)
import sys
sys.modules[spec.name]=m
spec.loader.exec_module(m)

def e(clock,kind="BIO_VALID",period="1T2026",section="TO-1"):
    return m.NormalizedEvent(period,section,datetime.fromisoformat("2026-10-04T"+clock+"-03:00"),kind,1)

class ContractTests(unittest.TestCase):
    def test_j0_filter_and_own_section(self):
        events=[e("08:59:59"),e("09:00:00"),e("09:00:00"),e("09:00:10"),
                e("14:59:59"),e("15:00:00"),e("09:00:15",section="TO-2")]
        dt=m.biometric_intervals_j0(events)
        self.assertEqual(dt,[0.0,10.0,21589.0])
    def test_type7_including_ties(self):
        self.assertAlmostEqual(m.linear_quantile([0,0,10,20],0.01),0.0)
        self.assertAlmostEqual(m.linear_quantile([0,10,20,30],0.5),15.0)
        self.assertRaises(ValueError,m.linear_quantile,[],0.01)
    def test_dt_star_requires_100k_in_production(self):
        obj=m.dt_star([e("09:00:00"),e("09:00:02")])
        self.assertEqual(obj["status"],"NAO_ESTIMAVEL")
        self.assertIsNone(obj["dt_star_seconds"])
        result=m.dt_star([e("09:00:00"),e("09:00:02")],minimum=1)
        self.assertEqual(result["dt_star_seconds"],2.0)
    def test_no_biometric_assumption(self):
        ev=[e("09:00:00","HAB_MANUAL"),e("09:00:10","VOTO_FIM")]
        self.assertEqual(m.biometric_intervals_j0(ev),[])
        self.assertEqual(m.catalog(ev),{"HAB_MANUAL":1,"VOTO_FIM":1})
    def test_reject_2026_second_turn(self):
        with self.assertRaises(ValueError):e("09:00:00",period="2T2026")
    def test_timestamp_timezone_is_required(self):
        with self.assertRaises(ValueError):
            m.NormalizedEvent("1T2026","TO-1",datetime(2026,10,4,9,0,0),"BIO_VALID",1)
    def test_2024_placebo_cannot_enter_dt_star(self):
        with self.assertRaises(ValueError):
            m.biometric_intervals_j0([e("09:00:00",period="2T2024")])

if __name__=="__main__":unittest.main()

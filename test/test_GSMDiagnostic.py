import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection
from src.DLMS_SPODES.cosem_interface_classes.gsm_diagnostic import SignalQuality


class TestType(unittest.TestCase):
    def test_SignalQuality(self):
        sq = SignalQuality(2)
        self.assertEqual(sq.report, "-109 dBm(2)", "report 2")
        sq.set(30)
        self.assertEqual(sq.report, "-53 dBm(30)", "report 30")

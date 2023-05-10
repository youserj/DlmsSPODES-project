import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview
from src.DLMS_SPODES.version import AppVersion


class TestType(unittest.TestCase):

    def test_ScalerUnitType(self):
        su = cdt.ScalUnitType((0, 27))
        print(su)
        value = cdt.DoubleLong(1.2, scaler_unit=su)
        a = str(value)
        print(value, value.report)

import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection
from src.DLMS_SPODES.version import AppVersion
from src.DLMS_SPODES.cosem_interface_classes.overview import ClassID, Version
from src.DLMS_SPODES import exceptions as exc


class TestType(unittest.TestCase):

    def test_NTPSetup(self):
        obj = collection.NTPSetup("0.0.25.10.0.255")
        obj.set_attr(2, False)
        obj.set_attr(3, bytearray(b'1234'))
        obj.set_attr(5, 0)
        obj.set_attr(6, [(1, bytearray(b'123'))])
        # obj.set_attr(7, False)
        print(obj)

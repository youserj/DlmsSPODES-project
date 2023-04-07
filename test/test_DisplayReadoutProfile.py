import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview


class TestType(unittest.TestCase):

    def test_Data(self):
        obj = collection.impl.profile_generic.SPODES3DisplayReadout("0.0.21.0.1.255")
        print(obj)
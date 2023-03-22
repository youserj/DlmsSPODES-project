import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection


class TestType(unittest.TestCase):

    def test_Data(self):
        obj = collection.Data("0.0.0.1.0.255")
        obj.set_attr(2, cdt.Unsigned(8).encoding)
        a = obj.get_attr(2)
        a.set(3)
        print(obj.value)

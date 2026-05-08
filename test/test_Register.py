import unittest
from src.DLMS_SPODES.types import cdt, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview
from src.DLMS_SPODES.cosem_interface_classes import implementations as impl


class TestType(unittest.TestCase):

    def test_Register(self):
        obj = collection.Register(b"\x01\x00\x00\x01\x00\xff")
        obj.set_attr(2, cdt.Integer(8).encoding)
        obj.set_attr(3, (1, 6))
        a = obj.get_attr(2)
        print(obj.value)
        dt = obj.get_attr_element(2).DATA_TYPE
        print(dt)
        print(isinstance(dt, ut.CHOICE))

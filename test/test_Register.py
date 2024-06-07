import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview
from src.DLMS_SPODES.cosem_interface_classes import implementations as impl
from src.DLMS_SPODES.version import AppVersion


class TestType(unittest.TestCase):

    def test_Register(self):
        obj = collection.Register("1.0.0.1.0.255")
        obj.set_attr(2, cdt.Integer(8).encoding)
        obj.set_attr(3, (1, 6))
        a = obj.get_attr(2)
        print(obj.value, obj.get_scaler_unit(2))


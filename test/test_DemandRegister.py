import unittest
from src.DLMS_SPODES.types import cdt, cst, ut, cosemClassID as classID
from src.DLMS_SPODES.cosem_interface_classes import collection
from src.DLMS_SPODES.cosem_interface_classes import implementations as impl
from src.DLMS_SPODES.version import AppVersion


class TestType(unittest.TestCase):

    def test_Data(self):
        obj = collection.DemandRegisterVer0("1.0.1.4.0.255")
        self.assertEqual(obj.CLASS_ID, classID.DEMAND_REGISTER, "class_ID")
        self.assertEqual(obj.get_attr_length(), 9, "attributes amount")
        obj.set_attr(2, cdt.Unsigned(8).encoding)
        self.assertRaises(ValueError, obj.set_attr, 3, cdt.LongUnsigned(8).encoding, "raising for other type assign")
        self.assertEqual(obj.last_average_value, None, "check for None value")
        print(obj.current_average_value, obj.last_average_value)

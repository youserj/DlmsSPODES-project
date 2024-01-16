import unittest
from itertools import count
from src.DLMS_SPODES.types.common_data_types import encode_length
from src.DLMS_SPODES.cosem_interface_classes import ic, collection
from src.DLMS_SPODES.types import cdt, cst, ut, implementations as impl, choices
from src.DLMS_SPODES import relation_to_OBIS, enums
from src.DLMS_SPODES.cosem_interface_classes.collection import Collection


class TestType(unittest.TestCase):
    def test_show_names(self):
        for s in cdt.Structure.__subclasses__():
            print(s.__name__, s(), cdt.get_type_name(s))
            for el in s.ELEMENTS:
                print(F"{el.NAME}: {el}")

    def test_WeekProfile(self):
        from src.DLMS_SPODES.cosem_interface_classes.activity_calendar import WeekProfile
        value = WeekProfile(("00", 1, 1, 1, 1, 1, 1, 1))
        self.assertEqual(value.decode(), (b'\x00', 1, 1, 1, 1, 1, 1, 1), "check decoding")
        print(value.decode()[1:])
        a = value[0]
        print(a)

    def test_KPZPingTestSetup(self):
        col = collection.Collection()
        obj = col.add(
            class_id=ut.CosemClassId(1),
            version=cdt.Unsigned(0),
            logical_name=cst.LogicalName("0.128.154.0.0.255"))
        obj.set_attr(2, 2)
        obj.set_attr(2, b'\x02\x04\x12\x00\x08\x09\x06\x00\x00\x01\x00\x00\xff\x0f\x02\x12\x00\x00')
        print(obj)

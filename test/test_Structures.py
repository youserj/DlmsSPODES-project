import unittest
from itertools import count
from src.DLMS_SPODES.types.common_data_types import encode_length
from src.DLMS_SPODES.cosem_interface_classes import ic, collection
from src.DLMS_SPODES.types import cdt, cst, ut, implementations as impl, choices
from src.DLMS_SPODES import relation_to_OBIS, enums
from src.DLMS_SPODES.cosem_interface_classes.collection import Collection


class TestType(unittest.TestCase):
    def test_WeekProfile(self):
        from src.DLMS_SPODES.cosem_interface_classes.activity_calendar import WeekProfile
        value = WeekProfile(("00", 1, 1, 1, 1, 1, 1, 1))
        self.assertEqual(value.decode(), (b'\x00', 1, 1, 1, 1, 1, 1, 1), "check decoding")
        print(value.decode()[1:])

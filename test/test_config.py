import datetime
import unittest
import inspect
from itertools import count
from src.DLMS_SPODES.types.common_data_types import encode_length
from src.DLMS_SPODES.cosem_interface_classes import ic, collection
from src.DLMS_SPODES.types import cdt, cst, ut, implementations as impl, choices
from src.DLMS_SPODES import relation_to_OBIS, enums
from src.DLMS_SPODES.config_parser import get_message, get_values


class TestType(unittest.TestCase):
    def test_get_message(self):
        self.assertEqual("hello world", get_message('hello world'), "simple test")
        print(get_message("$or$"))
        self.assertEqual(get_message("$or$"), "или", "check translate to rus")
        self.assertEqual(get_message("$$or$$"), "$or$", "check translate to rus")
        print(get_message("–113 dBm $or$ $less$(0)"))

    def test_firmwares(self):
        from src.DLMS_SPODES.firmwares import get_firmware

        firmwares = get_firmware(b"KPZ")
        print(firmwares)

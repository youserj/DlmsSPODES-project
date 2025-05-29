import unittest
from src.DLMS_SPODES.config_parser import get_message
from src.DLMS_SPODES.firmwares import get_firmware


class TestType(unittest.TestCase):
    def test_get_message(self):
        self.assertEqual("hello world", get_message('hello world'), "simple test")
        print(get_message("$or$"))
        self.assertEqual(get_message("$or$"), "или", "check translate to rus")
        self.assertEqual(get_message("$$or$$"), "$or$", "check translate to rus")
        print(get_message("–113 dBm $or$ $less$(0)"))

    def test_firmwares(self):
        firmwares = get_firmware(b"KPZ")
        print(firmwares)

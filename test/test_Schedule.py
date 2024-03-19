import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview
from src.DLMS_SPODES.cosem_interface_classes import implementations as impl
from src.DLMS_SPODES.version import AppVersion


class TestType(unittest.TestCase):

    def test_Data(self):
        obj = collection.Schedule("0.0.12.0.0.255")
        data = bytes.fromhex("01 04 02 0a 12 00 01 03 00 09 06 00 00 0a 00 64 ff 12 00 01 09 04 00 00 00 ff 12 00 01 04 07 e2 04 01 80 09 05 ff ff 01 01 ff 09 05 ff ff 01 01 ff 02 0a 12 00 02 03 00 09 06 00 00 0a 00 64 ff 12 00 02 09 04 00 00 00 ff 12 00 01 04 07 e2 04 02 80 09 05 ff ff 01 01 ff 09 05 ff ff 01 01 ff 02 0a 12 00 03 03 00 09 06 00 00 0a 00 64 ff 12 00 03 09 04 00 00 00 ff 12 00 01 04 07 e2 04 02 c0 09 05 ff ff 01 01 ff 09 05 ff ff 01 01 ff 02 0a 12 00 04 03 00 09 06 00 00 0a 00 64 ff 12 00 04 09 04 00 00 00 ff 12 00 01 04 07 e2 04 03 80 09 05 ff ff 01 01 ff 09 05 ff ff 01 01 ff")
        obj.set_attr(2, data)
        a = obj.get_attr(2)
        print(obj.entries)

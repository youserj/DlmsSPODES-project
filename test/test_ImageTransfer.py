import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview, ic
from src.DLMS_SPODES.cosem_interface_classes import implementations as impl
from src.DLMS_SPODES.version import AppVersion


class TestType(unittest.TestCase):

    def test_set_image_block_transfer(self):
        col = collection.get_collection(
            manufacturer=b"KPZ",
            server_type=cdt.OctetString("4d324d5f33"),
            server_ver=AppVersion.from_str("1.4.15"))
        obj: collection.ImageTransfer = col.get_object("0.0.44.0.0.255")
        obj.image_block_transfer.set((2, bytearray(b"1234")))
        print(obj)


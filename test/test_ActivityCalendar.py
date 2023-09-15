import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection
from src.DLMS_SPODES.version import AppVersion
from src.DLMS_SPODES.cosem_interface_classes.overview import ClassID, Version
from src.DLMS_SPODES import exceptions as exc


class TestType(unittest.TestCase):

    def test_Limiter(self):
        col = collection.get_collection(
            manufacturer=b"KPZ",
            server_type=cdt.OctetString("4d324d5f33"),
            server_ver=AppVersion.from_str("1.4.15"))


        col = collection.Collection()
        col.set_manufacturer(b'KPZ')
        col.set_server_ver(0, AppVersion(1, 4, 0))
        col.set_spec()
        tem = col.add(class_id=ClassID.REGISTER,
                version=Version.V0,
                logical_name=cst.LogicalName("0.0.96.9.0.255"))
        tem.set_attr(2, bytes.fromhex('10 00 1b'))
        lim = col.add(class_id=ClassID.LIMITER,
                version=Version.V0,
                logical_name=cst.LogicalName("0.0.17.0.5.255"))
        # lim.set_attr(3, bytes.fromhex('11 00 00 00 00'))
        self.assertRaises(exc.EmptyObj, lim.set_attr, 3, bytes.fromhex('11 00 00 00 00'))
        lim.set_attr(2, bytes.fromhex('02 03 12 00 03 09 06 00 00 60 09 00 ff 0f 02'))
        print(col, lim)

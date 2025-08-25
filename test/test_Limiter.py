import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection
from src.DLMS_SPODES.cosem_interface_classes.overview import ClassID, VERSION_0
from src.DLMS_SPODES import exceptions as exc


class TestType(unittest.TestCase):

    def test_Limiter(self):
        col = collection.Collection()
        col.set_manufacturer(b'KPZ')
        col.set_firm_ver(0, AppVersion(1, 4, 0))
        col.spec_map = col.get_spec()
        tem = col.add(class_id=ClassID.REGISTER,
                version=VERSION_0,
                logical_name=cst.LogicalName.from_obis("0.0.96.9.0.255"))
        tem.set_attr(2, bytes.fromhex('10 00 1b'))
        lim = col.add(class_id=ClassID.LIMITER,
                version=VERSION_0,
                logical_name=cst.LogicalName.from_obis("0.0.17.0.5.255"))
        # lim.set_attr(3, bytes.fromhex('11 00 00 00 00'))
        self.assertRaises(exc.EmptyObj, lim.set_attr, 3, bytes.fromhex('11 00 00 00 00'))
        lim.set_attr(2, bytes.fromhex('02 03 12 00 03 09 06 00 00 60 09 00 ff 0f 02'))
        print(col, lim)

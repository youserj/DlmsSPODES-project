import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview
from src.DLMS_SPODES import cosem_interface_classes
from src.DLMS_SPODES.version import AppVersion
from src.DLMS_SPODES.ITE_exceptions import NeedUpdate, NoObject
from src.DLMS_SPODES.cosem_interface_classes import reports


class TestType(unittest.TestCase):

    def test_report(self):
        col = collection.get_collection(
            manufacturer=b"KPZ",
            server_type=cdt.OctetString("4d324d5f33"),
            server_ver=AppVersion.from_str("1.4.15"))
        print(col)
        obj = col.get_object("0.0.1.0.0.255")
        obj.set_attr(2, "01.09.2023")
        obj.set_attr(3, 180)
        rep = reports.get_obj_report(
            obj=obj,
            attr_index_par={2: None,
                            3: None})
        print(rep)
        obj = col.get_object("0.0.96.1.0.255")
        obj.set_attr(2, "30313233")
        rep = reports.get_obj_report(
            obj=obj,
            attr_index_par={2: None})
        print(rep)
        obj = col.get_object("0.0.13.0.0.255")
        obj.set_attr(5, [
            [0, [("10:00", "1.1.1.1.1.1", 1)]], [1, [("12:00", "1.1.1.1.1.1", 2), ("14:00", "1.1.1.1.1.1", 3)]]])
        rep = reports.get_obj_report(
            obj=obj,
            attr_index_par={
                3: None,
                4: None,
                5: None
            })
        print(rep)

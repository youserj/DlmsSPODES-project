import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview
from src.DLMS_SPODES.cosem_interface_classes import implementations as impl
from src.DLMS_SPODES.version import AppVersion


class TestType(unittest.TestCase):

    def test_get_index_and_attr(self):
        obj = collection.Data("0.0.0.1.0.255")
        obj.set_attr(2, cdt.Unsigned(8).encoding)
        self.assertEqual(2, len(list(obj.get_index_with_attributes())), "return amount")

    def test_copy(self):
        col = collection.Collection()
        col.from_xml("09054d324d5f33_0906312e342e3130.typ")
        obj = col.get_object("0.0.1.0.0.255")
        obj.set_attr(2, cst.OctetStringDateTime("1.1.23"))
        print(obj)
        obj = col.get_object("0.0.22.0.0.255")
        print(obj)
        obj.windows_size_transmit.set(2)
        new_obj = obj.copy()
        print(new_obj)

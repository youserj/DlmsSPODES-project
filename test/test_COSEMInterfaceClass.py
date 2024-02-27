import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview, ic
from src.DLMS_SPODES.cosem_interface_classes import implementations as impl
from src.DLMS_SPODES.version import AppVersion
from itertools import chain


class TestType(unittest.TestCase):

    def test_get_index_and_attr(self):
        obj = collection.Data("0.0.0.1.0.255")
        obj.set_attr(2, cdt.Unsigned(8).encoding)
        self.assertEqual(2, len(list(obj.get_index_with_attributes())), "return amount")

    def test_nothing(self):
        col = collection.get_collection(
            manufacturer=b"KPZ",
            server_type=cdt.OctetString("4d324d5f33"),
            server_ver=AppVersion.from_str("1.4.15"))
        obj = col.get_object("0.0.96.1.4.255")
        print(obj)

    def test_ICAElement(self):
        el = ic.ICAElement(
            NAME="name",
            DATA_TYPE=cdt.OctetString,
            min=1,
            max=100,
            classifier=ic.Classifier.NOT_SPECIFIC)

        el2 = el.get_change(
            classifier=ic.Classifier.STATIC)
        print(el)
        print(el2)

    def test_Exceptions(self):
        raise ic.ObjectValidationError(ln=cst.LogicalName("1.1.1.1.1.1"), i=2, message="some error")

    def test_am_names(self):
        for c in ic.COSEMInterfaceClasses.__subclasses__():
            print(c)
            try:
                for i in chain(c.A_ELEMENTS, c.M_ELEMENTS):
                    print(F"{i}")
            except AttributeError as e:
                print(F"skip {c}: {e}")

    def test_encode(self):
        clock = collection.Clock("0.0.1.0.0.255")
        tz = clock.encode(3, 4)
        self.assertEqual(tz.encoding, b'\x10\x00\x04')
        data = collection.Data("0.0.96.1.1.255")
        value = data.encode(2, "4")
        self.assertEqual(value, None)

    def test_get_attr(self):
        data = collection.Data("0.0.96.1.1.255")
        data.get_attr(3)
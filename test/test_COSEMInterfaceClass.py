import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview, ic
from itertools import chain


class TestType(unittest.TestCase):

    def test_get_index_and_attr(self):
        obj = collection.Data("0.0.0.1.0.255")
        obj.set_attr(2, cdt.Unsigned(8).encoding)
        self.assertEqual(2, len(list(obj.get_index_with_attributes())), "return amount")

    def test_ICAElement(self):
        el = ic.ICAElement(
            i=1,
            NAME="name",
            DATA_TYPE=cdt.OctetString,
            min=1,
            max=100,
            classifier=ic.Classifier.NOT_SPECIFIC)

        el2 = el.get_change(
            classifier=ic.Classifier.STATIC)
        print(el)
        print(el2)

    def test_am_names(self):
        for c in ic.IC.__subclasses__():
            print(c)
            try:
                for i in chain(c.A_ELEMENTS, c.M_ELEMENTS):
                    print(F"{i}")
            except AttributeError as e:
                print(F"skip {c}: {e}")

    def test_ICparse(self):
        from src.DLMS_SPODES.cosem_interface_classes import clock

        clock_ = collection.Clock(b'\x00\x00\x01\x00\x00\xff')
        tz = clock_.parse(3, "4", clock.TimeZone).unwrap()
        self.assertEqual(tz.encoding, b'\x10\x00\x04')
        data = collection.Data(b"\x00\x00\x60\x01\x01\xff")
        value = data.parse(2, "5:4", cdt.DoubleLong).unwrap()
        self.assertEqual(value.encoding, b'\x05\x00\x00\x00\x04')

    def test_get_attr(self):
        data = collection.Data("0.0.96.1.1.255")
        data.get_attr(3)
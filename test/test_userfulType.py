import unittest
from src.DLMS_SPODES.types import cdt, cst, useful_types as ut


class TestType(unittest.TestCase):
    def test_CHOICE(self):

        class TestChoice(ut.CHOICE):
            TYPE = cdt.CommonDataType
            ELEMENTS = {0: ut.SequenceElement('0 a', cdt.NullData),
                        15: ut.SequenceElement('1 d', cdt.Integer),
                        3: ut.SequenceElement('second', cdt.ScalUnitType),
                        4: ut.SequenceElement('3', cdt.Integer)}

        choice = TestChoice()
        a = choice.get_types()

    def test_Digital(self):
        value = ut.CosemClassId(1)
        self.assertEqual(value, 1, "compare with build-in <int>")

    def test_CosemAttributeDescriptor(self):
        value = ut.CosemAttributeDescriptor((8, "0.1.1.0.0.255", 2))
        value2 = ut.CosemAttributeDescriptor((8, (0, 0, 1, 0, 0, 255), b'\x02'))
        print(value, value2, F"{value=}", value.contents)
        print(id(value.attribute_id), id(value2.attribute_id))

    def test_CosemObjectInstanceId(self):
        self.assertEqual(ut.CosemObjectInstanceId("0.1.1.0.0.255").contents, b'\x00\x01\x01\x00\x00\xff', "check from str")
        self.assertEqual(ut.CosemObjectInstanceId(b'\x00\x00\x01\x00\x00\xff').contents, b'\x00\x00\x01\x00\x00\xff', "check from bytes")
        self.assertEqual(ut.CosemObjectInstanceId((0, 1, 1, 0, 0, 0xff)).contents, b'\x00\x01\x01\x00\x00\xff', "check tuple")

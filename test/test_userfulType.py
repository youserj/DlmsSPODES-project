import unittest
from dataclasses import dataclass
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
        self.assertEqual(int(value), 1, "compare with build-in <int>")
        print(str(value))

    def test_CosemAttributeDescriptor(self):
        value = ut.CosemAttributeDescriptor((8, "0.1.1.0.0.255", 2))
        value2 = ut.CosemAttributeDescriptor((8, (0, 0, 1, 0, 0, 255), b'\x02'))
        print(value, value2, F"{value=}", value.contents)
        print(id(value.attribute_id), id(value2.attribute_id))

    def test_CosemObjectInstanceId(self):
        self.assertEqual(ut.CosemObjectInstanceId("0.1.1.0.0.255").contents, b'\x00\x01\x01\x00\x00\xff', "check from str")
        self.assertEqual(ut.CosemObjectInstanceId(b'\x00\x00\x01\x00\x00\xff').contents, b'\x00\x00\x01\x00\x00\xff', "check from bytes")
        self.assertEqual(ut.CosemObjectInstanceId((0, 1, 1, 0, 0, 0xff)).contents, b'\x00\x01\x01\x00\x00\xff', "check tuple")

    def test_CosemClassId(self):
        value = ut.CosemClassId(1)
        self.assertEqual(1, int(value), "check decode")
        for v in range(2**16):
            str(ut.CosemClassId(v))

    def test_Data(self):
        data = ut.Data()
        a = data(cdt.Integer(10).encoding)
        print(a)

    def test_Null(self):
        value = ut.Null()
        print(value)
        self.assertEqual(value.contents, b'', "default init")

    def test_boolean(self):
        value = ut.Boolean(False)
        print(value.contents)

    def test_SEQUENCE(self):

        @dataclass(frozen=True)
        class MySeq(ut.SEQUENCE):
            a: ut.Unsigned8
            b: ut.Unsigned16

        value = MySeq(a=ut.Unsigned8(1), b=ut.Unsigned16(4))
        print(value.contents)

    def test_Octet_string(self):
        value = ut.OCTET_STRING.from_contents(b'\x021234')
        print(value.contents)

    def test_OPTIONAL(self):
        class OctetOptional(ut.OPTIONAL):
            TYPE = ut.OCTET_STRING

        value = OctetOptional(ut.OCTET_STRING.from_str('hello'))
        print(value.contents)

    def test_invoke_id_and_priority(self):
        s_c = ut.service_class.UNCONFIRMED
        print(s_c)
        value = ut.InvokeIdAndPriority(0, ut.service_class.UNCONFIRMED, ut.priority.HIGH)
        value2 = ut.InvokeIdAndPriority.from_contents(b'\x24')
        print(value2)


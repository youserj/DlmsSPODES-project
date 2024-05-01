import unittest
from dataclasses import dataclass
from src.DLMS_SPODES.types import cdt, cst, useful_types as ut, cosemClassID as classID, serviceClass, priority


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
        self.assertEqual((value := ut.CosemObjectInstanceId.from_str("0.1.1.0.0.255")).contents, b'\x00\x01\x01\x00\x00\xff', "check from str")
        self.assertEqual(ut.CosemObjectInstanceId(b'\x00\x00\x01\x00\x00\xff').contents, b'\x00\x00\x01\x00\x00\xff', "check from bytes")
        print(str(value))

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
        value = ut.BOOLEAN(False)
        print(value.contents)

    def test_SEQUENCE(self):

        @dataclass(frozen=True)
        class MySeq(ut.Sequence):
            a: ut.Unsigned8
            b: ut.Unsigned16

        value = MySeq(a=ut.Unsigned8(1), b=ut.Unsigned16(4))
        print(value.contents)

    def test_Octet_string(self):
        value = ut.OctetString.from_contents(b'\x021234')
        print(value.contents)

    def test_OPTIONAL(self):
        class OctetOptional(ut.SequenceOptional):
            TYPE = ut.OctetString

        value = OctetOptional(ut.OctetString.from_str('hello'))
        print(value.contents)

    def test_invoke_id_and_priority(self):
        value = ut.InvokeIdAndPriority(4, serviceClass.UNCONFIRMED, priority.NORMAL)
        value2 = ut.InvokeIdAndPriority.from_contents(b'\x84')
        print(value == value2)
        self.assertEqual(value, value2, "compare new and <from contents>")

    def test_cosemAttributeDescriptor(self):
        value = ut.CosemAttributeDescriptor(
            classID.DATA,
            ut.CosemObjectInstanceId.from_str("0.0.4.0.0.255"),
            ut.CosemObjectAttributeId(2))
        self.assertEqual(value.contents, b'\x00\x01\x00\x00\x04\x00\x00\xff\x02', "from_build_in")
        value = ut.CosemAttributeDescriptor.from_contents(b'\x00\x01\x00\x00\x04\x00\x00\xff\x02')
        print(value)

    def test_OPTIONAL2(self):
        new = ut.OPTIONAL(ut.OctetString)
        self.assertEqual(new(ut.OctetString(b'1123')).contents, b'\x01\x041123', "from value")
        self.assertEqual(new().contents, b'\x00', "as optional")
        self.assertEqual(new.from_contents(b'\x00134'), new(), "as optional")
        self.assertEqual(new.from_contents(b'\x02\x0345678'), new(ut.OctetString(b'456')), "as optional")

    def test_sequence(self):
        @dataclass
        class Myseq(ut.Sequence):
            a: ut.NULL
            b: ut.Integer8

        value = Myseq(ut.NULL, b=ut.Integer8(1))
        print(value)

    def test_choice(self):
        # class Data(ut.Choice):
        #     ELEMENTS = (
        #         ut.ChoiceElement(
        #             name="null-data",
        #             tag=0,
        #             type=ut.Null),
        #         ut.ChoiceElement(
        #             name="boolean",
        #             tag=3,
        #             type=ut.BOOLEAN)
        #     )

        self.assertRaises(ValueError, ut.Data, ut.Integer16(1))
        self.assertEqual(ut.Data(ut.NULL), ut.Data.from_str("0 ..."))
        self.assertEqual(ut.Data.from_contents(b'\x00').value, ut.NULL, "Data from contents")
        self.assertEqual(ut.Data.from_contents(b'\x03\x01').value, ut.BOOLEAN(True), "Data from contents")
        a = ut.Data.from_contents(b'\x03\x01')
        print(a)
        b = ut.Data(ut.TRUE)
        print(b.contents)

    def test_bitstring(self):
        value = ut.BitString([1, 1, 0])
        self.assertEqual(value, ut.BitString.from_str("110"), "by string")
        value2 = ut.BitString.from_str("1001000101110100011010")
        value3 = ut.BitString.from_contents(b'\x16\x91th')
        print(value.contents)

    def test_OCTET_STRING(self):
        @dataclass
        class MySeq(ut.Sequence):
            a: ut.OCTET_STRING()
            b: ut.OCTET_STRING(4)

        value = MySeq(a=ut.OctetString(b'1'), b=4)
        print(value)

    def test_DataTime(self):
        value = ut.Data
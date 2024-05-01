import sys
import unittest
from src.DLMS_SPODES.types import cosem_pdu as pdu
from src.DLMS_SPODES.types.byte_buffer import ByteBuffer


class TestType(unittest.TestCase):
    def test_Null(self):
        value = pdu.NULL_
        print(value)

    def test_Boolean(self):
        buf = pdu.Buffer(memoryview(b'\x01\x00'))
        value = pdu.BOOLEAN.get(buf)
        print(value)

    def test_int(self):
        value = pdu.Integer8.from_int(125)
        print(value)
        value2 = pdu.Integer8.from_int(123)
        print(value == value2)

    def test_octet_string(self):
        value = pdu.OctetString.from_str("hello")
        print(value, bytes(value.contents))
        value = pdu.OctetString4.default()
        print(value)

    def test_to_buf(self):
        buf = pdu.Buffer(memoryview(bytearray(100)))
        value = pdu.OctetString.from_str("hello")
        value.put(buf)
        pdu.Integer8.default().put(buf)
        value.put(buf)
        print(str(buf), buf.buf.hex(' '))
        buf.pos = 0
        print(str(buf), buf.buf.hex(' '))
        value2 = pdu.OctetString.get(buf)
        print(value2)
        value3 = pdu.Unsigned16.get(buf)
        print(value3)
        print(str(buf), buf.buf.hex(' '))

    def test_simple_sequence(self):
        class MySeq(pdu.Sequence):
            x: pdu.Integer8
            y: pdu.Unsigned16

        value = MySeq.default()
        print(value.x)
        buf = pdu.Buffer(memoryview(b'1234'))
        value = MySeq.get(buf)
        print(value)
        value = MySeq.from_str("1 4")
        print(value)
        buf = pdu.Buffer(memoryview(bytearray(10)))
        value.put(buf)
        print(buf)

    def test_Optional(self):
        opt = pdu.OPTIONAL(pdu.Integer8)
        value = opt.from_str("13")
        buf = pdu.Buffer(memoryview(bytearray(10)))
        value.put(buf)
        print(value)
        buf = pdu.Buffer(memoryview(b'\x041234'))
        value = pdu.OPTIONAL(pdu.Integer8).get(buf)
        print(value)

    def test_choice(self):
        value = pdu.Data.from_str("5 4")
        print(value)
        value = pdu.Data(pdu.Integer64.from_int(1030))
        buf = pdu.Buffer(memoryview(bytearray(10)))
        value.put(buf)
        print(bytes(buf), buf)
        buf.pos = 0
        value = pdu.Data.get(buf)
        print(value)


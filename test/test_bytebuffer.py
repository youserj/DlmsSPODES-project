import unittest
from src.DLMS_SPODES.types.byte_buffer import ByteBuffer


class TestType(unittest.TestCase):
    def test_ByteBuffer(self):
        buf = ByteBuffer.allocate(100)
        buf.write(b'124')
        print(buf, bytes(buf))
        new_buf = buf.frozen()
        print(new_buf)
        x = buf.read(4)
        print(bytes(x))
        y = buf.read(0)
        print(F"{y=} {bytes(y)}")
        buf.read(96)
        print(buf)
        buf.read()
        print(new_buf)

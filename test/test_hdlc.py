import unittest
from src.DLMS_SPODES.hdlc import frame


class TestType(unittest.TestCase):
    def test_Address(self):
        ad1 = frame.Address(
            upper_address=0x1,
            lower_address=None)
        self.assertEqual(ad1.content, b'\x03', "upper only")
        ad2 = frame.Address(content=b'\x07')
        self.assertEqual((ad2.upper, ad2.lower), (3, None), "1length from content")
        ad3 = frame.Address(
            upper_address=0x1,
            lower_address=0,
            length=2
        )
        self.assertEqual(ad3.content, b'\x02\x01', "upper only")
        self.assertEqual((ad3.upper, ad3.lower), (1, 0), "lower set to 0")
        ad4 = frame.Address(
            upper_address=0x1,
            lower_address=0x10,
            length=4
        )
        self.assertEqual(ad4.content, b'\x00\x02\x00\x21', "rise to 4")
        ad5 = frame.Address(
            upper_address=0x100,
            lower_address=0x10,
            length=4
        )
        self.assertEqual(ad5.content, b'\x04\x00\x00\x21', "4 length address")

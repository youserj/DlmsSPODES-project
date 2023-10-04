import unittest
from src.DLMS_SPODES.hdlc import frame


class TestType(unittest.TestCase):
    def test_Address(self):
        ad1 = frame.Address(
            upper_address=0x04,
            lower_address=None)
        print(ad1, ad1.content.hex())
        ad2 = frame.Address(content=b'\x07')
        print(ad2, ad2.content.hex(), ad2.lower, ad2.upper)

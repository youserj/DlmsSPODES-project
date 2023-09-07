import unittest
from src.DLMS_SPODES.hdlc.negotiation import Negotiation


class TestType(unittest.TestCase):

    def test_Negotiation(self):
        value = Negotiation()
        self.assertEqual(Negotiation().content, b'', "empty info")
        self.assertEqual(Negotiation(max_info_receive=200).info, b'\x81\x80\x03\x06\x01\xc8', "receive")
        self.assertEqual(Negotiation(200, 259).info, b'\x81\x80\x07\x05\x01\xc8\x06\x02\x01\x03', "recv200_tr259")
        self.assertEqual(bytes(value.SNRM), b'', "empty SNRM")
        value.set_from_UA(b'\x81\x80\x03\x06\x01\xc9')
        self.assertEqual(value.max_info_transmit, 201, "tr change check")
        self.assertEqual(bytes(value.SNRM), b'\x81\x80\x03\x05\x01\xc9', "change SNRM")
        # set from empty UA
        value = Negotiation(max_info_transmit=256)
        value.set_from_UA(b'')
        self.assertEqual(value.max_info_transmit, 128, "check set default tx")
        #


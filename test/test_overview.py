import unittest
from src.DLMS_SPODES.cosem_interface_classes import overview


class TestType(unittest.TestCase):
    def test_ClassID(self):
        value = overview.ClassID.DATA
        print(value)

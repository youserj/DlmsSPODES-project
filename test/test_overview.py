import unittest
from src.DLMS_SPODES.types import cosemClassID as classID


class TestType(unittest.TestCase):
    def test_ClassID(self):
        value = classID.DATA
        print(value)

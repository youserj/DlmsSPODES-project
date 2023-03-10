import unittest
from src.DLMS_SPODES.cosem_interface_classes.overview import ClassID
from src.DLMS_SPODES.types import ut


class TestType(unittest.TestCase):
    def test_CosemClassId(self):
        self.assertEqual(ClassID.DATA, ut.CosemClassId(1), "check ClassID enum")
        for i in filter(lambda it: isinstance(it, ut.CosemClassId), ClassID.__dict__.values()):
            print(i, i.__class__)

import unittest
from src.DLMS_SPODES.cosem_interface_classes.overview import ClassID, Version
from src.DLMS_SPODES.types import ut, cst
from src.DLMS_SPODES.cosem_interface_classes import collection


class TestType(unittest.TestCase):
    def test_CosemClassId(self):
        self.assertEqual(ClassID.DATA, ut.CosemClassId(1), "check ClassID enum")
        for i in filter(lambda it: isinstance(it, ut.CosemClassId), ClassID.__dict__.values()):
            print(i, i.__class__)

    def test_SecuritySuite(self):
        col = collection.Collection()
        print(col)
        ss = col.add(
            class_id=ClassID.SECURITY_SETUP,
            version=Version.V1,
            logical_name=cst.LogicalName("0.0.43.0.0.255")
        )
        print(ss)
        self.assertEqual(ss.security_suite.AES_GCM_128_AUT_ENCR_AND_AES_128_KEY_WRAP, 0, "check constant enum")

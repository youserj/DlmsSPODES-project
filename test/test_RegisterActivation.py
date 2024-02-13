import unittest
from src.DLMS_SPODES.cosem_interface_classes import collection, overview
from src.DLMS_SPODES.types import ut, cdt, cst


class TestType(unittest.TestCase):
    def test_init(self):
        col = collection.Collection()
        obj = col.add(
            class_id=overview.ClassID.REGISTER_ACTIVATION,
            version=overview.Version.V0,
            logical_name=cst.LogicalName("0.0.14.0.0.255"))
        print(obj)

import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection


class TestType(unittest.TestCase):

    def test_dummy_class(self):
        a = collection.ProfileGenericVer0("0.0.1.0.0.255")
        print(a)

    def test_get_type_from_class(self):
        ln = cst.LogicalName("0.0.1.0.0.255")
        value = collection.get_interface_class(ut.CosemClassId(7), cdt.Unsigned(0))
        v1 = value(ln)
        print(value, v1)

    def test_get_instance(self):
        col = collection.Collection()
        inst = col.get_instance(class_id=ut.CosemClassId(3),
                                version=cdt.Unsigned(0),
                                ln=cst.LogicalName("1.0.131.35.0.255"))
        self.assertRaises(ValueError, col.get_instance, class_id=ut.CosemClassId(1),
                          version=cdt.Unsigned(0),
                          ln=cst.LogicalName("1.0.1.7.0.255"))
        print(inst)

    def test_ClassMap(self):
        print(hash(collection.DataMap))

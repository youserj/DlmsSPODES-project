import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection
from src.DLMS_SPODES.version import AppVersion


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
        col.manufacturer = b"KPZ"
        col.server_ver = AppVersion(1, 4, 0)
        col.set_spec()
        ver_obj = col.add(class_id=ut.CosemClassId(1),
                          version=cdt.Unsigned(0),
                          logical_name=cst.LogicalName("0.0.96.1.6.255"))
        ver_obj.set_attr(2, "33 30")
        inst = col.get_instance(class_id=ut.CosemClassId(3),
                                version=cdt.Unsigned(0),
                                ln=cst.LogicalName("1.0.131.35.0.255"))
        self.assertRaises(ValueError, col.get_instance, class_id=ut.CosemClassId(1),
                          version=cdt.Unsigned(0),
                          ln=cst.LogicalName("1.0.1.7.0.255"))
        inst = col.get_instance(class_id=ut.CosemClassId(1),
                                version=cdt.Unsigned(0),
                                ln=cst.LogicalName("0.128.96.13.1.255"))
        print(inst)

    def test_ClassMap(self):
        print(hash(collection.DataMap))

    def test_xmlCodingDecoding(self):
        col = collection.Collection()
        col.from_xml("09054d324d5f33_0906312e342e3130.typ")
        print(col)
        col.to_xml("test.xml")
        col.save_type("test.typ")
        ver = col.get_object("0.0.0.2.1.255")
        col.clear_server_ver()
        ver.value.set("312e312e33")
        print(ver)

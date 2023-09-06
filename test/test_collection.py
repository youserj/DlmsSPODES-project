import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview
from src.DLMS_SPODES import cosem_interface_classes
from src.DLMS_SPODES.version import AppVersion
from src.DLMS_SPODES.ITE_exceptions import NeedUpdate, NoObject


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
        col.set_manufacturer(b"KPZ")
        col.set_server_ver(0, AppVersion(1, 4, 0))
        col.set_spec()
        ver_obj = col.add(class_id=ut.CosemClassId(1),
                          version=cdt.Unsigned(0),
                          logical_name=cst.LogicalName("0.0.96.1.6.255"))
        ver_obj.set_attr(2, "33 2e 30")
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
        col.set_server_ver(0, AppVersion(1, 5, 1))
        col.from_xml("09054d324d5f33_0906312e342e3130.typ")
        print(col)
        col.to_xml("test.xml")
        col.save_type("test.typ")
        ver = col.get_object("0.0.0.2.1.255")
        col.clear_server_ver()
        ver.value.set("312e312e33")
        print(ver.value)

    def test_get_object_list(self):
        col = collection.get_collection(
            manufacturer=b"KPZ",
            server_type=cdt.OctetString("4d324d5f33"),
            server_ver=AppVersion.from_str("1.4.15"))
        print(col)
        a = col.get_objects_list(collection.enums.ClientSAP(48))
        print(a)
        for i in range(10):
            col_new = collection.get_collection(
                manufacturer=b"KPZ",
                server_type=cdt.OctetString("4d324d5f33"),
                server_ver=AppVersion.from_str("1.4.16"))
            print(col_new)

    def test_to_xml3(self):
        """for template"""
        col = collection.get_collection(
            manufacturer=b"KPZ",
            server_type=cdt.OctetString("4d324d5f33"),
            server_ver=AppVersion.from_str("1.4.15"))
        clock_obj = col.get_object("0.0.1.0.0.255")
        clock_obj.set_attr(3, 120)
        act_cal = col.get_object("0.0.13.0.0.255")
        act_cal.day_profile_table_passive.append((1, [("11:00", "1.1.1.1.1.1", 1)]))
        used = {
            clock_obj.logical_name: {2, 3},
            act_cal.logical_name: {9}
        }
        col.to_xml3("test_to_xml3.xml",
                    used=used,
                    decode=True)

    def test_collection_from_xml(self):
        col, used = collection.Collection.from_xml3("test_to_xml3.xml")
        print(col, used)

    def test_get_collection(self):
        """for template"""
        for ver_txt in ("0.0.52", "1.1.9", "1.2.11", "1.3.25"):
            for manufacturer, type_ in ((b"101", "4d324d5f31"), (b"102", "4d324d5f33"), (b"103", "4d324d5f3153"), (b"104", "4d324d5f3353")):
                col = collection.get_collection(
                    manufacturer=manufacturer,
                    server_type=cdt.OctetString(type_),
                    server_ver=AppVersion.from_str(ver_txt))
            print(col)

    def test_to_xml4(self):
        """for template"""
        col = collection.get_collection(
            manufacturer=b"KPZ",
            server_type=cdt.OctetString("4d324d5f33"),
            server_ver=AppVersion.from_str("1.4.15"))
        col2 = collection.get_collection(
            manufacturer=b"102",
            server_type=cdt.OctetString("4d324d5f33"),
            server_ver=AppVersion.from_str("1.3.30"))
        clock_obj = col.get_object("0.0.1.0.0.255")
        clock_obj.set_attr(3, 120)
        act_cal = col.get_object("0.0.13.0.0.255")
        act_cal.day_profile_table_passive.append((1, [("11:00", "1.1.1.1.1.1", 1)]))
        used = {
            clock_obj.logical_name: {3},
            act_cal.logical_name: {9}
        }
        collection.to_xml4(
            collections=[col, col2],
            file_name="test_to_xml4.xml",
            used=used)

    def test_collection_from_xml4(self):
        cols, used = collection.from_xml4("test_to_xml4.xml")
        print(cols, used)

    def test_get_writable_dict(self):
        """use in template"""
        col = collection.get_collection(
            manufacturer=b"KPZ",
            server_type=cdt.OctetString("4d324d5f33"),
            server_ver=AppVersion.from_str("1.4.15"))
        ret = col.get_writable_attr()
        print(ret)

    def test_save_and_load(self):
        col = collection.get_collection(
            manufacturer=b"KPZ",
            server_type=cdt.OctetString("4d324d5f3354"),
            server_ver=AppVersion.from_str("1.4.15"))
        clock = col.get_object("0.0.1.0.0.255")
        clock.set_attr(3, 100)
        col.to_xml2("test_to_xml2.xml")
        col2 = collection.get_collection(
            manufacturer=b"KPZ",
            server_type=cdt.OctetString("4d324d5f3354"),
            server_ver=AppVersion.from_str("1.4.15"))
        col2.from_xml2("test_to_xml2.xml")

    def test_AssociationLN(self):
        col = collection.Collection()
        col.set_manufacturer(b"KPZ")
        col.set_server_ver(0, AppVersion(1, 4, 0))
        col.set_spec()
        ass_obj = col.add(class_id=overview.ClassID.ASSOCIATION_LN_CLASS,
                          version=overview.Version.V1,
                          logical_name=cst.LogicalName("0.0.40.0.3.255"))
        ver_obj = col.add(class_id=overview.ClassID.DATA,
                          version=overview.Version.V0,
                          logical_name=cst.LogicalName("0.0.0.2.1.255"))
        self.assertRaises(NeedUpdate,
                          ver_obj.set_attr,
                          2,
                          bytes.fromhex("0905312e352e30"))
        ass_obj.set_attr(6, bytes.fromhex("090760857405080202"))
        print(ass_obj)

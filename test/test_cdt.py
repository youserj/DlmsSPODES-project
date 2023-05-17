import datetime
import unittest
from src.DLMS_SPODES.types.common_data_types import encode_length
from src.DLMS_SPODES.cosem_interface_classes import ic, collection
from src.DLMS_SPODES.types import cdt, cst, ut, implementations as impl
from src.DLMS_SPODES import relation_to_OBIS, enums
from src.DLMS_SPODES.cosem_interface_classes.collection import Collection


class TestType(unittest.TestCase):
    def test_encode_length(self):
        self.assertEqual(encode_length(1), b'\x01')
        self.assertEqual(encode_length(0x7e), b'\x7e')
        self.assertEqual(encode_length(0x80), b'\x81\x80')
        self.assertEqual(encode_length(0xff), b'\x81\xff')
        self.assertEqual(encode_length(0x100), b'\x82\x01\x00')
        self.assertEqual(encode_length(0x1000), b'\x82\x10\x00')
        self.assertEqual(encode_length(0x10000), b'\x84\x00\x01\x00\x00')
        self.assertEqual(encode_length(0xffffffff), b'\x84\xff\xff\xff\xff')

    def test_exist_attr(self):
        """ Existing attribute 'class_name' in each DLMS class """
        # todo: rewrite, don't work in new API
        # for c_id in ic._COSEM_interface_class_ids:
        #     dlms_class = get_type_from_class(c_id, 0)
        #     self.assertTrue(hasattr(dlms_class, 'NAME'), F'{dlms_class}')

    def test_BitString(self):
        pattern = '101011'
        a = cdt.BitString()
        self.assertEqual(a.encoding, b'\x04\x00', 'default initiation')
        a.set(pattern)
        self.assertEqual(cdt.BitString(pattern), a, 'check set_contents_from')
        self.assertEqual(a.decode(), [1, 0, 1, 0, 1, 1], 'decode to list')

    def test_DateTime(self):
        pattern = datetime.datetime(2020, 1, 1, tzinfo=datetime.timezone.utc)
        self.assertEqual(cdt.DateTime(pattern).decode(), pattern, 'init from datetime and decoding')

    def test_Collection(self):
        collection = Collection()
        collection.add_major(collection.create(class_id=ut.CosemClassId(15), version=cdt.Unsigned(1), logical_name=cst.LogicalName('0.0.40.0.0.255')))
        collection.create(class_id=ut.CosemClassId(8), version=cdt.Unsigned(1), logical_name=cst.LogicalName('0.0.1.0.0.255'))
        collection.create(class_id=ut.CosemClassId(3), version=cdt.Unsigned(0), logical_name=cst.LogicalName('1.0.2.29.0.255'))
        self.assertTrue(len(collection) == 3)
        collection.clear()
        self.assertTrue(len(collection) == 1)
        collection.add_if_missing(class_id=ut.CosemClassId(15), version=cdt.Unsigned(1), logical_name=cst.LogicalName('0.0.40.0.0.255'))
        # self.collection.create(class_id=ut.CosemClassId(15), version=cdt.Unsigned(1), logical_name=cst.LogicalName('0.0.40.0.0.255'))
        self.assertTrue(len(collection) == 1, 'check for not added Association again')

    def test_UnitScaler(self):
        value = cdt.ScalUnitType()
        value.set((10, 10))
        print(value)

    def test_ProfileGeneric(self):
        from src.DLMS_SPODES.cosem_interface_classes.association_ln.ver1 import ObjectListElement
        from src.DLMS_SPODES.types.implementations import structs
        col = Collection()
        col.create(class_id=ut.CosemClassId(15), version=cdt.Unsigned(1), logical_name=cst.LogicalName('0.0.40.0.0.255'))
        col.create(class_id=ut.CosemClassId(8), version=cdt.Unsigned(1), logical_name=cst.LogicalName('0.0.1.0.0.255'))
        col.create(class_id=ut.CosemClassId(3), version=cdt.Unsigned(0), logical_name=cst.LogicalName('1.0.2.29.0.255'))
        col.create(class_id=ut.CosemClassId(3), version=cdt.Unsigned(0), logical_name=cst.LogicalName('1.0.1.29.0.255'))
        col.create(class_id=ut.CosemClassId(3), version=cdt.Unsigned(0), logical_name=cst.LogicalName('1.0.3.29.0.255'))
        col.create(class_id=ut.CosemClassId(3), version=cdt.Unsigned(0), logical_name=cst.LogicalName('1.0.4.29.0.255'))
        profile = collection.create(class_id=ut.CosemClassId(7), version=cdt.Unsigned(1), logical_name=cst.LogicalName('1.0.94.7.4.255'))
        profile.collection = collection
        profile.set_attr(6, structs.CaptureObjectDefinition().encoding)
        profile.set_attr(3, bytes.fromhex('01 05 02 04 12 00 08 09 06 00 00 01 00 00 ff 0f 02 12 00 00 02 04 12 00 03 09 06 01 00 02 1d 00 ff 0f 03 12 00 00 02 04 12 00 03 09 06 01 00 01 1d 00 ff 0f 03 12 00 00 02 04 12 00 03 09 06 01 00 03 1d 00 ff 0f 03 12 00 00 02 04 12 00 03 09 06 01 00 04 1d 00 ff 0f 03 12 00 00'))
        profile.object_list.selective_access.access_selector.set_contents_from(2)
        profile.set_attr(2, bytes.fromhex('01 01 02 05 09 0c 07 6e 08 1f 07 00 00 ff ff 80 00 00 02 02 0f fd 16 1e 02 02 0f fd 16 1e 02 02 0f fd 16 20 02 02 0f fd 16 20'))
        a = ObjectListElement((3, 0, '1.0.1.29.0.255', None))
        b = col.get_object(a)
        b1 = col.get_object(structs.CaptureObjectDefinition((3, '1.0.1.29.0.255', None, None)))
        # b2 = col.get_object(EntryDescriptor())
        desc1 = profile.get_attr_descriptor(2)
        self.assertEqual(desc1.contents, b'\x00\x07\x01\x00^\x07\x04\xff\x02\x01\x02\x02\x04\x06\x00\x00\x00\x01\x06\x00\x00\x00\x00\x12\x00\x01\x12\x00\x00')
        profile.get_attr(2).selective_access.access_selector.set_contents_from(1)
        desc2 = profile.get_attr_descriptor(2)
        self.assertEqual(desc2.contents, b'\x00\x07\x01\x00^\x07\x04\xff\x02\x01\x01\x02\x04\x02\x04\x12\x00\x01\t\x06\x00\x00\x01\x00\x00\xff\x0f\x02\x12\x00\x00\t\x0c\x07\xe4'
                                         b'\x01\x01\xff\xff\xff\xff\xff\x80\x00\xff\t\x0c\x07\xe4\x01\x02\xff\xff\xff\xff\xff\x80\x00\xff\x01\x00')
        # e = EntryDescriptor()
        # e.set_contents_from((1, 0, 1, 0))

    def test_Association(self):
        ass = collection.AssociationLNVer0('0.0.40.0.1.255')
        print(ass)

    def test_Conformance(self):
        from src.DLMS_SPODES.cosem_interface_classes.association_ln.ver0 import Conformance, XDLMSContextType
        c = Conformance()
        a = int('1011011101111', 2)
        c.set(a)
        self.assertEqual(c.decode(), [1, 1, 1, 1, 0, 1, 1, 1, 0, 1, 1, 0, 1, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        context = XDLMSContextType()
        print(context)

    def test_ImageTransfer(self):
        col = Collection()
        col.create(class_id=ut.CosemClassId(18), version=cdt.Unsigned(0), logical_name=cst.LogicalName('0.0.44.0.0.255'))
        print(col)

    def test_UTF8(self):
        value = cdt.Utf8String()
        value.set('ООО "Курганский приборостроительный завод"')
        print(value)

    def test_Duration(self):
        value = impl.double_long_usingneds.DoubleLongUnsignedSecond()
        value.set(1)
        self.assertEqual(value.report, "0 c")

    def test_ScalerUnitType(self):
        value = cdt.ScalUnitType((1, 4))
        value.unit.set(enums.Unit.CURRENT_AMPERE)
        print(value.unit == cdt.Unit(enums.Unit.CURRENT_AMPERE))

    def test_Array(self):
        obj = collection.Data("1.1.1.1.1.1")
        obj.set_attr(2, b'\x01\x00')
        # check Type setting in empty Array
        obj.set_attr(2, b'\x01\x01\x11\x02')
        a = obj.value.get_copy([1, 3])
        print(a)

    def test_get_copy(self):
        value = cdt.Unsigned(3)
        copy = value.get_copy(4)
        self.assertNotEqual(value, copy, "check different value")

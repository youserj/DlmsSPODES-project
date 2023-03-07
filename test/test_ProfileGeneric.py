import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection


class TestType(unittest.TestCase):

    def test_ProfileGeneric(self):
        col = collection.Collection()
        col.add_major(col.create(class_id=ut.CosemClassId(15), version=cdt.Unsigned(1), logical_name=cst.LogicalName('0.0.40.0.0.255')))
        col.create(class_id=ut.CosemClassId(8), version=cdt.Unsigned(0), logical_name=cst.LogicalName('0.0.1.0.0.255'))
        col.create(class_id=ut.CosemClassId(47), version=cdt.Unsigned(0), logical_name=cst.LogicalName("0.0.25.6.0.255"))
        new = col.create(class_id=ut.CosemClassId(1), version=cdt.Unsigned(0), logical_name=cst.LogicalName('0.0.96.11.0.255'))
        new.set_attr(2, b'\x09\x02hi')
        reg = col.create(class_id=ut.CosemClassId(3), version=cdt.Unsigned(0), logical_name=cst.LogicalName('1.0.12.7.0.255'))
        reg.set_attr(2, 6)
        col.create(class_id=ut.CosemClassId(3),
                   version=cdt.Unsigned(0),
                   logical_name=cst.LogicalName('1.0.12.7.4.255')
                   ).set_attr(2, 6)
        col.create(class_id=ut.CosemClassId(1),
                   version=cdt.Unsigned(0),
                   logical_name=cst.LogicalName('0.0.96.8.10.255')
                   ).set_attr(2, 6)
        col.create(class_id=ut.CosemClassId(1),
                   version=cdt.Unsigned(0),
                   logical_name=cst.LogicalName('0.0.96.8.0.255')
                   ).set_attr(2, 6)
        inst = col.create(class_id=ut.CosemClassId(7), version=cdt.Unsigned(1), logical_name=cst.LogicalName('0.0.99.13.0.255'))
        inst.set_attr(6, bytes.fromhex('020412000809060000010000ff0f02120000'))
        inst.set_attr(3, bytes.fromhex('01 02 02 04 12 00 2f 09 06 00 00 19 06 00 ff 0f 02 12 00 00 02 04 12 00 2f 09 06 00 00 19 06 00 ff 0f 06 12 00 03'))
        inst.set_attr(2, bytes.fromhex('01 03 02 02 0a 07 4d 65 67 61 46 6f 6e 11 1b 02 02 0a 0c 42 65 65 20 4c 69 6e 65 20 47 53 4d 11 3f 02 02 0a 03 4d 54 53 11 33'))
        # inst.set_attr(3, bytes.fromhex('0106020412000809060000010000ff0f02120000020412000109060000600b00ff0f021200000204120003090601000c0700ff0f021200000204120003090601000c0704ff0f0212000002041200010906000060080aff0f02120000020412000309060000600800ff0f02120000'))
        print(inst.get_capture_object_names())
        print(inst)

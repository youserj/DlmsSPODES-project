import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection
from src.DLMS_SPODES.relation_to_OBIS import get_name


class TestType(unittest.TestCase):

    def test_angles_objs(self):
        col = collection.Collection()
        col.add(class_id=ut.CosemClassId(3), version=cdt.Unsigned(0), logical_name=cst.LogicalName("1.0.81.7.4.255"))
        obj = col.get_object("1.0.81.7.4.255")
        self.assertEqual(get_name(obj.logical_name), "угол между Ia и Ua", "name matching")
        print(obj, get_name(obj.logical_name))

    def test_ExternalEventData(self):
        col = collection.Collection()
        col.add(class_id=ut.CosemClassId(1), version=cdt.Unsigned(0), logical_name=cst.LogicalName("0.0.96.11.4.255"))
        obj = col.get_object("0.0.96.11.4.255")
        obj.set_attr(2, 2)
        print(obj.value, obj.value.report)
        self.assertEqual(obj.value.report, "Магнитное поле - окончание(2)", "report match")
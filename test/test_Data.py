import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection
from src.DLMS_SPODES.cosem_interface_classes import implementations as impl


class TestType(unittest.TestCase):

    def test_Data(self):
        obj = collection.Data("0.0.0.1.0.255")
        obj.set_attr(2, cdt.Unsigned(8).encoding)
        a = obj.get_attr(2)
        a.set(3)
        print(obj.value)

    def test_eventsData(self):
        col = collection.Collection()
        col.add(class_id=ut.CosemClassId(7), version=cdt.Unsigned(1), logical_name=cst.LogicalName("0.0.99.98.4.255"))
        print(col)

    def test_ExternalEventData(self):
        col = collection.Collection()
        col.add(class_id=ut.CosemClassId(1), version=cdt.Unsigned(0), logical_name=cst.LogicalName("0.0.96.11.4.255"))
        obj = col.get_object("0.0.96.11.4.255")
        obj.set_attr(2, 2)
        print(obj.value, obj.value.report)
        self.assertEqual(obj.value.report, "Магнитное поле - окончание(2)", "report match")

import unittest
from src.DLMS_SPODES.types import cdt, cst, ut, cosemClassID as classID
from src.DLMS_SPODES.cosem_interface_classes import collection
from src.DLMS_SPODES.cosem_interface_classes import implementations as impl
from src.DLMS_SPODES.version import AppVersion


class TestType(unittest.TestCase):

    def test_Data(self):
        obj = collection.Data("0.0.0.1.0.255")
        obj.set_attr(2, cdt.Unsigned(8).encoding)
        a = obj.get_attr(2)
        a.set(3)
        print(obj.value)

    def test_eventsData(self):
        col = collection.Collection()
        col.add(class_id=classID.CosemClassId(7), version=cdt.Unsigned(1), logical_name=cst.LogicalName("0.0.99.98.4.255"))
        print(col)

    def test_ExternalEventData(self):
        col = collection.Collection()
        col.set_manufacturer(b'KPZ')
        col.set_country("3.0")
        col.server_ver = AppVersion(1, 3, 0)
        col.server_type = cdt.OctetString("4d324d5f33")
        col.set_spec()
        col.add(class_id=classID.CosemClassId(1), version=cdt.Unsigned(0), logical_name=cst.LogicalName("0.0.96.11.4.255"))
        obj = col.get_object("0.0.96.11.4.255")
        obj.set_attr(2, b'\x06\x00\x00\x00\x02')
        # obj.set_attr(2, 2)
        print(obj.value, obj.value.report)
        self.assertEqual(obj.value.report, "Магнитное поле - окончание(2)", "report match")
        print(col)

    def test_DeviceIdObjects(self):
        obj = impl.data.DLMSDeviceIDObject("0.0.96.1.4.255")
        datatime = cdt.DateTime("01.01.20 11:00")
        obj.set_attr(2, datatime.encoding)

    def test_SealStatus(self):
        obj = impl.data.SealStatus("0.0.96.51.5.255")
        obj.set_attr(2, 0)
        for i in range(255):
            obj.value.set(i)
            print(i, obj.value.get_report())

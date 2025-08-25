import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview
from src.DLMS_SPODES.cosem_interface_classes import implementations as impl


class TestType(unittest.TestCase):

    def test_Register(self):
        col = collection.Collection()
        reg = col.add(
            class_id=overview.ClassID.REGISTER,
            version=overview.VERSION_0,
            logical_name=cst.LogicalName("01 00 01 07 00 ff")
        )
        r_m = col.add(
            class_id=overview.ClassID.REGISTER_MONITOR,
            version=overview.VERSION_0,
            logical_name=cst.LogicalName("00 00 10 00 00 ff")
        )
        reg.set_attr(2, cdt.Integer(8).encoding)
        reg.set_attr(3, (1, 6))
        r_m.set_attr(3, (3, "01 00 01 07 00 ff", 2))
        r_m.set_attr(2, [4], cdt.Unsigned)
        rep = col.get_report(r_m, b'\x02\x00', 5)
        print(r_m)


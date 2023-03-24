import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection
from src.DLMS_SPODES.relation_to_OBIS import get_name
from src.DLMS_SPODES.configure import get_attr_index


class TestType(unittest.TestCase):

    def test_configure(self):
        ln = cst.LogicalName("1.0.94.7.4.255")
        obj = collection.ProfileGenericVer1(ln)
        print(get_attr_index(obj))

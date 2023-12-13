import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview
from src.DLMS_SPODES import cosem_interface_classes
from src.DLMS_SPODES.version import AppVersion
from src.DLMS_SPODES.exceptions import NeedUpdate, NoObject


class TestType(unittest.TestCase):

    def test_OutputState(self):
        from src.DLMS_SPODES.cosem_interface_classes.disconnect_control import OutputState
        value = OutputState(0)
        print(value)

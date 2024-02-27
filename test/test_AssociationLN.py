import os
import time
import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview
from src.DLMS_SPODES import cosem_interface_classes
from src.DLMS_SPODES.version import AppVersion
from src.DLMS_SPODES.exceptions import NeedUpdate, NoObject


class TestType(unittest.TestCase):

    def test_is_writable(self):
        ass = collection.AssociationLNVer1("0.0.40.0.0.255")
        ass.is_writable(
            ln=cst.LogicalName("0.0.1.0.0.255"),
            index=2)
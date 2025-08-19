import unittest
from src.DLMS_SPODES.cosem_interface_classes.parameter import Parameter
from src.DLMS_SPODES.cosem_interface_classes import parameters as prs


class TestType(unittest.TestCase):
    def test_one(self):
        class My(prs.Data):
            OBIS = Parameter.parse("0.0.0.1.0.255")

        print(My().LN)

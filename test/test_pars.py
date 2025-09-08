import unittest
from src.DLMS_SPODES.cosem_interface_classes.parameter import Parameter
from src.DLMS_SPODES.cosem_interface_classes import parameters as prs


class TestType(unittest.TestCase):
    def test_one(self):
        My = prs.Data.parse("0.0.0.1.0.255")
        My2 = prs.Data.parse("0.0.1.1.0.255")
        My3 = prs.Register.parse("0.2.1.1.0.255")

        print(My.logical_name, My2.logical_name, My3.scaler_unit)

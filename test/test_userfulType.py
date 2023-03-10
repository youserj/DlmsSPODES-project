import inspect
import unittest
from src.DLMS_SPODES.types import cdt, cst, useful_types as ut


class TestType(unittest.TestCase):
    def test_CHOICE(self):

        class TestChoice(ut.CHOICE):
            TYPE = cdt.CommonDataType
            ELEMENTS = {0: ut.SequenceElement('0 a', cdt.NullData),
                        15: ut.SequenceElement('1 d', cdt.Integer),
                        3: ut.SequenceElement('second', cdt.ScalUnitType),
                        4: ut.SequenceElement('3', cdt.Integer)}

        choice = TestChoice()
        a = choice.get_types()

    def test_Digital(self):
        value = ut.CosemClassId(1)
        self.assertEqual(value, 1, "compare with build-in <int>")

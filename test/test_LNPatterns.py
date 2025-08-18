import logging
import os
from itertools import count
import time
import unittest
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview, ln_pattern
from src.DLMS_SPODES import cosem_interface_classes
from src.DLMS_SPODES.obis import media_id
from src.DLMS_SPODES.exceptions import NeedUpdate, NoObject


class TestType(unittest.TestCase):
    def setUp(self):
        self.pattern = ln_pattern.LNPattern.parse("0.b.0.(1-5, 7-8).0.255")

    @staticmethod
    def get_pattern():
        return ln_pattern.LNPattern.parse("0.b.0.1.0.255")

    def test_create(self):
        print(self.pattern)

    def test_equal(self):
        self.assertEqual(self.pattern, cst.LogicalName.from_obis("0.2.0.1.0.255"))
        self.assertNotEqual(self.pattern, cst.LogicalName.from_obis("1.0.0.1.0.255"))

    def test_country(self):
        print(ln_pattern.COUNTRY_SPECIFIC_IDENTIFIERS)

    def test_1(self):
        reduce_ln = ln_pattern.LNPattern.parse("0.0.(40,42).0.0.255")
        print(reduce_ln == cst.LogicalName.from_obis("0.0.40.0.0.255"))

    def test_convert(self):
        clock_pat = ln_pattern.CLOCK
        print(clock_pat)

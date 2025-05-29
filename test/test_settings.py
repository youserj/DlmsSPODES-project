import unittest
from src.DLMS_SPODES.settings import settings, toml_data, Settings


class TestType(unittest.TestCase):
    def test_settings(self):
        self.assertIsInstance(settings, Settings)

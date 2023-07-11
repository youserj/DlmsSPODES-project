import unittest
from src.DLMS_SPODES.version import AppVersion


class TestType(unittest.TestCase):
    def test_encode_length(self):
        a = AppVersion.from_str("1.1.9")
        self.assertEqual(str(a), "1.1.9", "str conversion")
        b = AppVersion(1, 1, 9)
        self.assertEqual(a, b, "patch custom equal")
        self.assertNotEqual(AppVersion(1, 3), AppVersion(1, 3, 0), "different semver")
        variants = [AppVersion(1, 0, 13, "d1"), AppVersion(1, 0, 9)]
        self.assertEqual(b.select_nearest(variants), None, "select left")
        variants = [
            AppVersion(1, 0, 13, "d1"),
            AppVersion(1, 1, 8),
            AppVersion(1, 1, 6)]
        self.assertEqual(b.select_nearest(variants), variants[1], "select left")
        self.assertTrue(AppVersion(1, 3, 0) < AppVersion(1, 4, 0), "check1")
        print(b)

    def test_nearest(self):
        ver = AppVersion.from_str("1.1.3")
        ver2 = ver.select_nearest([AppVersion.from_str("1.1.2"), AppVersion.from_str("1.1.1"), AppVersion.from_str("1.0.1")])
        print(ver2)
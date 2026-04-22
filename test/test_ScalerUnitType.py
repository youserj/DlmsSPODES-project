import unittest
from COSEMpdu.byte_buffer import ByteBuffer
from src.DLMS_SPODES.cosem_interface_classes.register import ScalUnitType
from src.DLMS_SPODES.types import cdt, cst, ut
from src.DLMS_SPODES.cosem_interface_classes import collection, overview


class TestType(unittest.TestCase):

    def test_ScalerUnitType(self) -> None:
        su = ScalUnitType.parse((0, 27))
        su2 = ScalUnitType.create(0, 27)
        buf = ByteBuffer.allocate(10)
        res = su.put(buf)
        print(su)

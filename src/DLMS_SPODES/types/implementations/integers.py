"""all realisation cdt.Integer subclasses"""
from dataclasses import dataclass
from COSEMpdu.x680.constrained_type import ValueRange
from COSEMpdu.x680 import TaggingMode
from COSEMpdu.axdr import ConstrainedIntegerType, IntegerType, TaggedType


@dataclass
class Integer8Zero(ConstrainedIntegerType):
    """Integer8(0)"""
    constraint_spec = ValueRange(0, 0)
    value: IntegerType


@dataclass
class IntegerValue0(TaggedType[Integer8Zero]):
    """[15] IMPLICIT Integer(0)"""
    tag = 15
    mode = TaggingMode.IMPLICIT
    value: Integer8Zero


INTEGER_0 = IntegerValue0(Integer8Zero(IntegerType(0)))

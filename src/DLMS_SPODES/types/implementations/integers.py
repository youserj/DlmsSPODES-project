"""all realisation cdt.Integer subclasses"""
from typing import ClassVar
from COSEMpdu.x680 import ValueRange
from COSEMpdu.axdr import ConstrainedIntegerType, ImplicitTaggedType


class IntegerValue0(ImplicitTaggedType, ConstrainedIntegerType):
    """[15] IMPLICIT Integer(0)"""
    tag: ClassVar[int] = 15
    constraint_spec = ValueRange(0, 0)


INTEGER_0 = IntegerValue0(0)

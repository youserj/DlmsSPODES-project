"""all realisation cdt.Integer subclasses"""
from ...types import common_data_types as cdt
from typing_extensions import deprecated


@deprecated("use INTEGER_0")
class Only0(cdt.Integer, value=0):
    """ Limited Integer only 0 """


INTEGER_0 = cdt.Integer(0)

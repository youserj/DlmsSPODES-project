"""all realisation cdt.Integer subclasses"""
from ...types import common_data_types as cdt
from typing import Any


class Only0(cdt.Integer, value=0):
    """ Limited Integer only 0 """
    def __call__(self, *args: Any, **kwargs: Any) -> "Only0":
        return INTEGER_0


INTEGER_0 = Only0()

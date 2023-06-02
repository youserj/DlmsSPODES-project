"""all realisation cdt.Integer subclasses"""
from ...types import common_data_types as cdt


class Only0(cdt.Integer, value=0):
    """ Limited Integer only 0 """

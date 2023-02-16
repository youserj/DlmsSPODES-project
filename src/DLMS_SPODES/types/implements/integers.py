"""all realisation cdt.Integer subclasses"""
from ...types import common_data_types as cdt


class Only0(cdt.Integer):
    """ Limited Integer only 0 """
    NAME = F'{cdt.tn.INTEGER}(0)'

    def validate(self):
        if self.decode() != 0:
            raise ValueError(F'The integer(0) must only 0,  got {self.decode()}')

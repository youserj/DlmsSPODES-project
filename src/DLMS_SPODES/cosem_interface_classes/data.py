from __future__ import annotations
from .__class_init__ import *
from ..types import choices


class Data(ic.COSEMInterfaceClasses):
    """ Object stores data related to internal meter object(s). The meaning of the value is identified by the logical_name.
    The data type of the value is CHOICE. “Data” is typically used to store configuration data and parameters """
    NAME = cn.DATA
    CLASS_ID = ut.CosemClassId(class_id.DATA)
    VERSION = cdt.Unsigned(0)
    A_ELEMENTS = ic.ICAElement(an.VALUE, choices.common_dt, classifier=ic.Classifier.DYNAMIC),

    def characteristics_init(self):
        """nothing do it"""

    @property
    def value(self) -> cdt.CommonDataType:
        """Contains the data"""
        return self.get_attr(2)

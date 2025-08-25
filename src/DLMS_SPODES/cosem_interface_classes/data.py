from __future__ import annotations
from ..types import choices
from . import cosem_interface_class as ic
from .overview import ClassID
from .overview import VERSION_0


class Data(ic.COSEMInterfaceClasses):
    """ Object stores data related to internal meter object(s). The meaning of the value is identified by the logical_name.
    The data type of the value is CHOICE. “Data” is typically used to store configuration data and parameters """
    CLASS_ID = ClassID.DATA
    VERSION = VERSION_0
    A_ELEMENTS = ic.ICAElement("value", choices.common_dt, classifier=ic.Classifier.NOT_SPECIFIC),

    def characteristics_init(self):
        """nothing do it"""

    @property
    def value(self) -> cdt.CommonDataTypes:
        """Contains the data"""
        return self.get_attr(2)

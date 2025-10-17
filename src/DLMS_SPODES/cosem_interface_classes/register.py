from ..types.implementations import integers
from typing import Optional
from ..types import choices, cdt
from .cosem_interface_class import ICAuto, ICAElement, ICMElement, Classifier, Cardinality
from .Overview import class_id


class Register(ICAuto):
    """4.3.2 Register"""
    CLASS_ID = class_id.REGISTER
    VERSION = 0
    CARDINALITY = Cardinality()
    A_ELEMENTS = (
        ICAElement(2, "value", choices.register, classifier=Classifier.NOT_SPECIFIC),
        ICAElement(3, "scaler_unit", cdt.ScalUnitType))
    M_ELEMENTS = ICMElement(1, "reset", integers.Only0),
    value: Optional[choices.RegisterValues]
    scaler_unit: Optional[cdt.ScalUnitType]

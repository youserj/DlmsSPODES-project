from . import register
from typing import Optional
from ..types import choices, cdt, cst
from .cosem_interface_class import ICAElement, Classifier
from .Overview import class_id


class ExtendedRegister(register.Register):
    """4.3.3 Extended register"""
    CLASS_ID = class_id.EXT_REGISTER
    VERSION = 0
    A_ELEMENTS = (register.Register.getAElement(2).unwrap(),
                  register.Register.getAElement(3).unwrap(),
                  ICAElement(4, "status", choices.extended_register, classifier=Classifier.DYNAMIC),
                  ICAElement(5, "capture_time", cst.OctetStringDateTime, classifier=Classifier.DYNAMIC))
    M_ELEMENTS = register.Register.getMElement(1).unwrap(),
    status: Optional[choices.ExtendedRegisterValues]
    capture_time: Optional[cdt.DateTime]

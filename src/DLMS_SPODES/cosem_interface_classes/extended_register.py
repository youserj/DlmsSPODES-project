from typing import TypeAlias
from COSEMpdu.data import (
    NullData, BitString, DoubleLongUnsigned, OctetString, VisibleString, Utf8String,
    Unsigned, LongUnsigned, Long64Unsigned, Data, union2alternatives
)
from . import register
from ..types.type_alias import Attr
from ..types import cst
from .cosem_interface_class import ICAElement, Classifier


Value: TypeAlias = NullData | BitString | DoubleLongUnsigned | OctetString | VisibleString | Utf8String | Unsigned | LongUnsigned | Long64Unsigned


class StatusData(Data[Value]):
    """value"""
    alternatives = union2alternatives(Value)


class ExtendedRegister(register.Register):
    """4.3.3 Extended register"""
    CLASS_ID = 4
    VERSION = 0
    A_ELEMENTS = (
        register.Register.getAElement(2),
        register.Register.getAElement(3),
        ICAElement(4, "status", StatusData, classifier=Classifier.DYNAMIC),
        ICAElement(5, "capture_time", cst.OctetStringDateTime, classifier=Classifier.DYNAMIC))
    M_ELEMENTS = register.Register.getMElement(1),
    status: Attr
    capture_time: Attr

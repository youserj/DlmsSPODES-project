from COSEMpdu.data import DoubleLongUnsigned, LongUnsigned
from ...types import cst
from .. import register, extended_register
from ...types.implementations import integers
from ...types.type_alias import Attr
from ..cosem_interface_class import ICAuto, ICAElement, ICMElement, Classifier, Cardinality


class DemandRegister(ICAuto):
    """4.3.4.Demand register"""
    CLASS_ID = 5
    VERSION = 0
    CARDINALITY = Cardinality()
    A_ELEMENTS = (
        ICAElement(2, "current_average_value", register.ValueData, classifier=Classifier.DYNAMIC),
        ICAElement(3, "last_average_value", register.ValueData, classifier=Classifier.DYNAMIC),
        ICAElement(4, "scaler_unit", register.ScalUnitType),
        ICAElement(5, "status", extended_register.StatusData, classifier=Classifier.DYNAMIC),
        ICAElement(6, "capture_time", cst.OctetStringDateTime, classifier=Classifier.DYNAMIC),
        ICAElement(7, "start_time_current", cst.OctetStringDateTime, classifier=Classifier.DYNAMIC),
        ICAElement(8, "period", DoubleLongUnsigned, min=1),
        ICAElement(9, "number_of_periods", LongUnsigned, min=1, default=1))
    M_ELEMENTS = (
        ICMElement(1, "reset", integers.IntegerValue0),
        ICMElement(2, "next_period", integers.IntegerValue0))
    current_average_value: Attr
    last_average_value: Attr
    scaler_unit: Attr
    status: Attr
    capture_time: Attr
    start_time_current: Attr
    period: Attr
    number_of_periods: Attr

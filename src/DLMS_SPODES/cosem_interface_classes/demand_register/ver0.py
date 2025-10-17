from ...types import choices, cdt, cst
from ...types.implementations import integers
from ...types.type_alias import Attr
from ..cosem_interface_class import ICAuto, ICAElement, ICMElement, Classifier, Cardinality
from ..Overview import class_id


class DemandRegister(ICAuto):
    """4.3.4.Demand register"""
    CLASS_ID = class_id.DEMAND_REGISTER
    VERSION = 0
    CARDINALITY = Cardinality()
    A_ELEMENTS = (
        ICAElement(2, "current_average_value", choices.register, classifier=Classifier.DYNAMIC),
        ICAElement(3, "last_average_value", choices.register, classifier=Classifier.DYNAMIC),
        ICAElement(4, "scaler_unit", cdt.ScalUnitType),
        ICAElement(5, "status", choices.extended_register, classifier=Classifier.DYNAMIC),
        ICAElement(6, "capture_time", cst.OctetStringDateTime, classifier=Classifier.DYNAMIC),
        ICAElement(7, "start_time_current", cst.OctetStringDateTime, classifier=Classifier.DYNAMIC),
        ICAElement(8, "period", cdt.DoubleLongUnsigned, min=1),
        ICAElement(9, "number_of_periods", cdt.LongUnsigned, min=1, default=1))
    M_ELEMENTS = (
        ICMElement(1, "reset", integers.Only0),
        ICMElement(2, "next_period", integers.Only0))
    current_average_value: Attr
    last_average_value: Attr
    scaler_unit: Attr
    status: Attr
    capture_time: Attr
    start_time_current: Attr
    period: Attr
    number_of_periods: Attr

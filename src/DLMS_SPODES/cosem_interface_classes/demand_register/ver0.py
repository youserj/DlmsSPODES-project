from ..__class_init__ import *
from ...types import choices
from ...types.implementations import integers
from ..overview import VERSION_0


class DemandRegister(ic.COSEMInterfaceClasses):
    """DLMS UA 1000-1 Ed 14 4.3.4.Demand register"""
    CLASS_ID = ClassID.DEMAND_REGISTER
    VERSION = VERSION_0
    A_ELEMENTS = (
        ic.ICAElement(2, "current_average_value", choices.register, classifier=ic.Classifier.DYNAMIC),
        ic.ICAElement(3, "last_average_value", choices.register, classifier=ic.Classifier.DYNAMIC),
        ic.ICAElement(4, "scaler_unit", cdt.ScalUnitType),
        ic.ICAElement(5, "status", choices.extended_register, classifier=ic.Classifier.DYNAMIC),
        ic.ICAElement(6, "capture_time", cst.OctetStringDateTime, classifier=ic.Classifier.DYNAMIC),
        ic.ICAElement(7, "start_time_current", cst.OctetStringDateTime, classifier=ic.Classifier.DYNAMIC),
        ic.ICAElement(8, "period", cdt.DoubleLongUnsigned, min=1),
        ic.ICAElement(9, "number_of_periods", cdt.LongUnsigned, min=1, default=1))
    M_ELEMENTS = (
        ic.ICMElement(1, "reset", integers.INTEGER_0),
        ic.ICMElement(2, "next_period", integers.INTEGER_0))
    scaler_unit_not_settable: bool

    @property
    def current_average_value(self) -> choices.RegisterValues:
        return self.get_attr(2)

    @property
    def last_average_value(self) -> choices.RegisterValues:
        return self.get_attr(3)

    @property
    def scaler_unit(self) -> cdt.ScalUnitType:
        return self.get_attr(4)

    @property
    def status(self) -> choices.ExtendedRegisterValues:
        return self.get_attr(5)

    @property
    def capture_time(self) -> cst.OctetStringDateTime:
        return self.get_attr(6)

    @property
    def start_time_current(self) -> cst.OctetStringDateTime:
        return self.get_attr(7)

    @property
    def period(self) -> cdt.DoubleLongUnsigned:
        return self.get_attr(8)

    @property
    def number_of_periods(self) -> cdt.LongUnsigned:
        return self.get_attr(9)

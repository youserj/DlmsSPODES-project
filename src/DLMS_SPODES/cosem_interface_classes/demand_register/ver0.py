from ..__class_init__ import *
from ...types import choices
from ...types.implementations import integers


class DemandRegister(ic.COSEMInterfaceClasses):
    """DLMS UA 1000-1 Ed 14 4.3.4.Demand register"""
    CLASS_ID = ClassID.DEMAND_REGISTER
    VERSION = Version.V0
    A_ELEMENTS = (ic.ICAElement("current_average_value", choices.register, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("last_average_value", choices.register, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("scaler_unit", cdt.ScalUnitType),
                  ic.ICAElement("status", choices.extended_register, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("capture_time", cst.OctetStringDateTime, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("start_time_current", cst.OctetStringDateTime, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("period", cdt.DoubleLongUnsigned, min=1),
                  ic.ICAElement("number_of_periods", cdt.LongUnsigned, min=1, default=1))
    M_ELEMENTS = ic.ICMElement("reset", integers.Only0),
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

    def characteristics_init(self):
        self.scaler_unit_not_settable = False
        """ usability scaler unit flag. if True then it not used"""

from ..__class_init__ import *
from ...types import choices
from ...types.implementations import integers


class DemandRegister(ic.COSEMInterfaceClasses):
    """DLMS UA 1000-1 Ed 14 4.3.4.Demand register"""
    NAME = cn.DEMAND_REGISTER
    CLASS_ID = ClassID.DEMAND_REGISTER
    VERSION = Version.V0
    A_ELEMENTS = (ic.ICAElement(an.CURRENT_AVERAGE_VALUE, choices.register, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement(an.LAST_AVERAGE_VALUE, choices.register, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement(an.SCALER_UNIT, cdt.ScalUnitType),
                  ic.ICAElement(an.STATUS, choices.extended_register, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement(an.CAPTURE_TIME, cst.OctetStringDateTime, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement(an.START_TIME_CURRENT, cst.OctetStringDateTime, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement(an.PERIOD, cdt.DoubleLongUnsigned, min=1),
                  ic.ICAElement(an.NUMBER_OF_PERIODS, cdt.LongUnsigned, min=1, default=1))
    M_ELEMENTS = ic.ICMElement(mn.RESET, integers.Only0),
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
        self._cbs_attr_post_init.update({2: lambda: self.__set_value_data_type(2),
                                         3: lambda: self.__set_value_data_type(3),
                                         4: self.__set_value_scaler_unit})

        self.scaler_unit_not_settable = False
        """ usability scaler unit flag. if True then it not used"""

    def __set_value_data_type(self, attr_index: int):
        """ When instead of a “Data” object a “Register” object is used, (with the scaler_unit attribute not used or with scaler = 0, unit = 255) then the data types allowed for
        the value attribute of the “Data” interface class are allowed. """
        attr_value = self.get_attr(attr_index)
        if self.current_average_value is not None and self.last_average_value is not None and self.current_average_value.TAG != self.last_average_value.TAG:
            self.clear_attr(attr_index)
            raise ValueError(F"got {self.get_attr_element(attr_index).NAME} with: {attr_value=}, expected "
                             F"{cdt.get_common_data_type_from(self.current_average_value.TAG if attr_index == 3 else self.last_average_value.TAG).NAME}")
        match attr_value:
            case cdt.Array() | cdt.CompactArray() | cdt.Structure(): self.set_attr(4, cdt.ScalUnitType(b'\x02\x02\x0f\x00\x16\xff'))
            case cdt.Digital() | cdt.Float():                        attr_value.SCALER_UNIT = self.scaler_unit
            case _:                                                  """ nothing do it """
        match self.scaler_unit:
            case cdt.ScalUnitType(): self.__set_value_scaler_unit()
            case _:                  """ not necessary set Scaler Unit """

    def __set_value_scaler_unit(self):
        match self.current_average_value:
            case cdt.Digital() | cdt.Float() if self.current_average_value.SCALER_UNIT is None:  self.current_average_value.SCALER_UNIT = self.scaler_unit
            case cdt.Digital() | cdt.Float() if self.current_average_value.SCALER_UNIT == self.scaler_unit: """ already set """
            case cdt.Digital() | cdt.Float():                   raise ValueError(F'Got new scaler: {self.scaler_unit} not order with old {self.current_average_value.SCALER_UNIT}')
            case _:                                             """set only for digital"""
        match self.last_average_value:
            case cdt.Digital() | cdt.Float() if self.last_average_value.SCALER_UNIT is None:  self.last_average_value.SCALER_UNIT = self.scaler_unit
            case cdt.Digital() | cdt.Float() if self.last_average_value.SCALER_UNIT == self.scaler_unit: """ already set """
            case cdt.Digital() | cdt.Float():                   raise ValueError(F'Got new scaler: {self.scaler_unit} not order with old {self.last_average_value.SCALER_UNIT}')
            case _:                                             """set only for digital"""

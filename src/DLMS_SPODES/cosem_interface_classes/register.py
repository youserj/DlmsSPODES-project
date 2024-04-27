from .__class_init__ import *
from ..types import choices
from ..types.implementations import integers


class Register(ic.COSEMInterfaceClasses):
    """ A “Register” object stores a process value or a status value with its associated unit. The register object knows
    the nature of the process value or of the status value. The nature of the value is described by the attribute
    “logical name” using the OBIS identification system. """
    CLASS_ID = classID.REGISTER
    VERSION = Version.V0
    scaler_unit_not_settable: bool
    A_ELEMENTS = (ic.ICAElement("value", choices.register, classifier=ic.Classifier.NOT_SPECIFIC),
                  ic.ICAElement("scaler_unit", cdt.ScalUnitType))
    M_ELEMENTS = (
        ic.ICMElement("reset", integers.Only0),
        ic.ICMElement("next_period", integers.Only0))

    def characteristics_init(self):
        self._cbs_attr_post_init.update({2: self.__set_value_data_type,
                                         3: self.__set_value_scaler_unit})

        self.scaler_unit_not_settable = False
        """ usability scaler unit flag. if True then it not used"""

    @property
    def value(self) -> choices.RegisterValues:
        return self.get_attr(2)

    @property
    def scaler_unit(self) -> cdt.ScalUnitType:
        return self.get_attr(3)

    @property
    def reset(self) -> integers.Only0:
        return self.get_meth(1)

    def __set_value_data_type(self):
        """ When instead of a “Data” object a “Register” object is used, (with the scaler_unit attribute not used or with scaler = 0, unit = 255) then the data types allowed for
        the value attribute of the “Data” interface class are allowed. """
        match self.value:
            case cdt.Array() | cdt.CompactArray() | cdt.Structure(): self.set_attr(3, cdt.ScalUnitType(b'\x02\x02\x0f\x00\x16\xff'))
            case cdt.Digital() | cdt.Float():                        self.value.SCALER_UNIT = self.scaler_unit
            case _:                                                  """ nothing do it """
        match self.scaler_unit:
            case cdt.ScalUnitType(): self.__set_value_scaler_unit()
            case _:                  """ not necessary set Scaler Unit """

    def __set_value_scaler_unit(self):
        match self.value:
            case cdt.Digital() | cdt.Float() if self.value.SCALER_UNIT is None:  self.value.SCALER_UNIT = self.scaler_unit
            case cdt.Digital() | cdt.Float() if self.value.SCALER_UNIT == self.scaler_unit: """ already set """
            case cdt.Digital() | cdt.Float():                                    raise ValueError(F'Got new scaler: {self.scaler_unit} not order with old {self.value.SCALER_UNIT}')
            case _:                                                              """set only for digital"""

    def get_report(self):
        match self.value, self.scaler_unit:
            case None, None: rep = '? ?'
            case cdt.Digital(), _: rep = self.value.report
            case _: rep = F'{self.value} {self.scaler_unit}'
        return F'{self} {rep}'

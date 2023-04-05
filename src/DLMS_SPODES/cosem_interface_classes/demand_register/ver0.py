from ..__class_init__ import *
from ...types import choices
from ...types.implementations import integers


class Status(cdt.Enum):
    """ Indicates the registration status of the  modem. """
    ELEMENTS = {b'\x00': en.NOT_REGISTERED,
                b'\x01': en.REGISTERED_HOME_NETWORK,
                b'\x02': en.NOT_REGISTERED_BUT_MT,
                b'\x03': en.REGISTRATION_DENIED,
                b'\x04': en.UNKNOWN,
                b'\x05': en.REGISTERED_ROAMING}


class CSAttachment(cdt.Enum):
    """ Indicates the current circuit switched status."""
    ELEMENTS = {b'\x00': en.INACTIVE,
                b'\x01': en.INCOMING_CALL,
                b'\x02': en.ACTIVE}


class PSStatus(cdt.Enum):
    """ Indicates the packet switched status of the modem. """
    ELEMENTS = {b'\x00': en.INACTIVE,
                b'\x01': en.GPRS,
                b'\x02': en.EDGE,
                b'\x03': en.UMTS,
                b'\x04': en.HSDPA}


class SignalQuality(cdt.Unsigned):
    """for string report"""
    @property
    def report(self) -> str:
        value = int(self)
        if value == 0:
            return F"–113 dBm {en.OR_LESS}(0)"
        elif value == 1:
            return F"–111 dBm(1)"
        elif value < 31:
            return F"{-109+(value-2)*2} dBm({value})"
        elif value == 31:
            return F"–51 dBm {en.OR_GREATER}(31)"
        elif value == 99:
            return F"{en.NOT_KNOWN_OR_NOT_DETECTABLE}"
        else:
            return F"wrong {value=}"


class CellInfoType(cdt.Structure):
    """ Params of element """
    values: tuple[cdt.LongUnsigned, cdt.LongUnsigned, SignalQuality, cdt.Unsigned]
    ELEMENTS = (cdt.StructElement(cdt.se.CELL_ID, cdt.LongUnsigned),
                cdt.StructElement(cdt.se.LOCATION_ID, cdt.LongUnsigned),
                cdt.StructElement(cdt.se.SIGNAL_QUALITY, SignalQuality),
                cdt.StructElement(cdt.se.BER, cdt.Unsigned))

    @property
    def cell_ID(self) -> cdt.LongUnsigned:
        """Two-byte cell ID in hexadecimal format"""
        return self.values[0]

    @property
    def location_ID(self) -> cdt.LongUnsigned:
        """Two-byte location area code (LAC) in hexadecimal format"""
        return self.values[1]

    @property
    def signal_quality(self) -> SignalQuality:
        """represents the signal quality"""
        return self.values[2]

    @property
    def ber(self) -> cdt.Unsigned:
        """Bit error (BER) measurement in percent:
        (0...7) as RXQUAL_n values specified in ETSI GSM 05.08 8.2.4
        (99) not known or not detectable."""
        return self.values[3]


class AdjacentCellInfo(cdt.Structure):
    values: tuple[cdt.LongUnsigned, cdt.Unsigned]
    ELEMENTS = (cdt.StructElement(cdt.se.CELL_ID, cdt.LongUnsigned),
                cdt.StructElement(cdt.se.SIGNAL_QUALITY, cdt.Unsigned))

    @property
    def cell_ID(self) -> cdt.LongUnsigned:
        """Two-byte cell ID in hexadecimal format"""
        return self.values[0]

    @property
    def signal_quality(self) -> cdt.Unsigned:
        """represents the signal quality:
            0: -113 dBm or less,
            1: -11q dBm,
            2..30: -109...53 dBm,
            31: -51 or greater,
            99 not known or not detectable"""
        return self.values[1]


class AdjacentCells(cdt.Array):
    TYPE = AdjacentCellInfo


class DemandRegister(ic.COSEMInterfaceClasses):
    """DLMS UA 1000-1 Ed 14 4.3.4.Demand register"""
    NAME = cn.GSM_DIAGNOSTIC
    CLASS_ID = ClassID.GSM_DIAGNOSTIC
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

import logging
from ...config_parser import get_message
from COSEMpdu.data import Enum, Array, Structure, VisibleString, DateTime, EnumMixin, Unsigned, LongUnsigned
from ...types import cdt
from ..cosem_interface_class import ICAuto, ICAElement, Classifier
from ...types.type_alias import Attr


class Status(Enum):
    """status"""
    NOT_REGISTERED = 0
    REGISTERED_HOME = 1
    NOT_REGISTERED_SEARCHING = 2
    REGISTRATION_DENIED = 3
    UNKNOWN = 4
    REGISTERED_ROAMING = 5


class CSAttachment(Enum):
    """cs_attachment"""
    INACTIVE = 0
    INCOMING_CALL = 1
    ACTIVE = 2


class PSStatus(Enum):
    """ps_status"""
    INACTIVE = 0
    GPRS = 1
    EDGE = 2
    UMTS = 3
    HSPDA = 4


class SignalQuality(EnumMixin, Unsigned):
    """signal_quality"""
    _113_DBM_OR_LESS = 0
    _111_DBM = 1
    _109_DBM = 2
    _107_DBM = 3
    _105_DBM = 4
    _103_DBM = 5
    _101_DBM = 6
    _99_DBM = 7
    _97_DBM = 8
    _95_DBM = 9
    _93_DBM = 10
    _91_DBM = 11
    _89_DBM = 12
    _87_DBM = 13
    _85_DBM = 14
    _83_DBM = 15
    _81_DBM = 16
    _79_DBM = 17
    _77_DBM = 18
    _75_DBM = 19
    _73_DBM = 20
    _71_DBM = 21
    _69_DBM = 22
    _67_DBM = 23
    _65_DBM = 24
    _63_DBM = 25
    _61_DBM = 26
    _59_DBM = 27
    _57_DBM = 28
    _55_DBM = 29
    _53_DBM = 30
    _51_OR_GREATER = 31
    NOT_KNOWN_OR_NOT_DETECTABLE = 99

    def get_report(self) -> cdt.Report:
        val = int(self)
        if val == 0:
            return cdt.Report(get_message(F"({val}) –113 dBm $or$ $less$(0)"))
        if val == 1:
            return cdt.Report(F"({val}) –111 dBm")
        if val < 31:
            return cdt.Report(get_message(F"({val}) {-109 + (val - 2) * 2} dBm"))
        if val == 31:
            return cdt.Report(get_message(F"({val}) –51 dBm $or$ $greater$"))
        if val == 99:
            return cdt.Report(get_message(F"({val}) $not_known_or_not_detectable$"))
        return cdt.Report(
            msg=F"({val})",
            log=cdt.Log(logging.WARN, "unknown value"))


class CellInfoType(Structure):
    """cell_info_type"""
    cell_ID: LongUnsigned
    location_ID: LongUnsigned
    signal_quality: SignalQuality
    ber: Unsigned


class AdjacentCellInfo(Structure):
    """adjacent_cell_info"""
    cell_ID: LongUnsigned
    signal_quality: SignalQuality


class GSMDiagnostic(ICAuto):
    """4.7.8 GSM diagnostic"""
    CLASS_ID = 47
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "operator", VisibleString, classifier=Classifier.DYNAMIC),
        ICAElement(3, "status", Status, 0, 255, 0, classifier=Classifier.DYNAMIC),
        ICAElement(4, "cs_attachment", CSAttachment, 0, 255, 0, classifier=Classifier.DYNAMIC),
        ICAElement(5, "ps_status", PSStatus, 0, 255, 0, classifier=Classifier.DYNAMIC),
        ICAElement(6, "cell_info", CellInfoType, classifier=Classifier.DYNAMIC),
        ICAElement(7, "adjacent_cell", Array[AdjacentCellInfo], classifier=Classifier.DYNAMIC),
        ICAElement(8, "capture_time", DateTime, classifier=Classifier.DYNAMIC))
    operator: Attr
    status: Attr
    cs_attachment: Attr
    ps_status: Attr
    cell_info: Attr
    adjacent_cell: Attr
    capture_time: Attr

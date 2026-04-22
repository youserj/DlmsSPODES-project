from COSEMpdu.data import Enum, Array, Structure, Unsigned, LongUnsigned, DoubleLongUnsigned
from . import ver0
from ..cosem_interface_class import ICAElement, Classifier, update_collection
from ...types.type_alias import Attr


class PSStatus(Enum):
    """ps_status"""
    INACTIVE = 0
    GPRS = 1
    EDGE = 2
    UMTS = 3
    HSPDA = 4
    LTE = 5
    CDMA = 6


class CellInfoType(Structure):
    """cell_info_type"""
    cell_ID: DoubleLongUnsigned
    location_ID: LongUnsigned
    signal_quality: ver0.SignalQuality
    ber: Unsigned
    mcc: LongUnsigned
    mnc: LongUnsigned
    channel_number: DoubleLongUnsigned


class AdjacentCellInfo(Structure):
    """adjacent_cell_info"""
    cell_ID: DoubleLongUnsigned
    signal_quality: ver0.SignalQuality


class GSMDiagnostic(ver0.GSMDiagnostic):
    VERSION = 1
    A_ELEMENTS = update_collection(
        ver0.GSMDiagnostic.A_ELEMENTS,
        ICAElement(5, "ps_status", PSStatus, 0, 255, 0, classifier=Classifier.DYNAMIC),
        ICAElement(6, "cell_info", CellInfoType, classifier=Classifier.DYNAMIC),
        ICAElement(7, "adjacent_cell", Array[AdjacentCellInfo], classifier=Classifier.DYNAMIC))
    ps_status: Attr
    cell_info: Attr
    adjacent_cell: Attr

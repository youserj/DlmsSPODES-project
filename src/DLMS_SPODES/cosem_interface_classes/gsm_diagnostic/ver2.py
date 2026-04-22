from COSEMpdu.data import Enum
from . import ver0, ver1
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
    LTE_CAT_M1 = 7
    LTE_CAT_NB1 = 8
    LTE_CAT_NB2 = 9


class GSMDiagnostic(ver0.GSMDiagnostic):
    """4.7.8 GSM diagnostic"""
    VERSION = 2
    A_ELEMENTS = update_collection(
        ver1.GSMDiagnostic.A_ELEMENTS,
        ICAElement(5, "ps_status", PSStatus, 0, 255, 0, classifier=Classifier.DYNAMIC),
    )
    ps_status: Attr
    cell_info: Attr
    adjacent_cell: Attr

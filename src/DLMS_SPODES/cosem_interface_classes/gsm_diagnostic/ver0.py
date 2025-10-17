import logging
from ...config_parser import get_message
from typing import Optional
from ...types import cdt
from ..cosem_interface_class import ICAuto, ICAElement, Classifier
from ..Overview import class_id


class Status(cdt.Enum, elements=tuple(range(6))):
    """ Indicates the registration status of the  modem. """


class CSAttachment(cdt.Enum, elements=(0, 1, 2)):
    """ Indicates the current circuit switched status."""


class PSStatus(cdt.Enum, elements=tuple(range(5))):
    """ Indicates the packet switched status of the modem. """


class SignalQuality(cdt.IntegerEnum, cdt.Unsigned):
    """for string report"""
    def __init_subclass__(cls, **kwargs):
        """not need"""

    def get_report(self) -> cdt.Report:
        val = int(self)
        if val == 0:
            return cdt.Report(get_message(F"({val}) –113 dBm $or$ $less$(0)"))
        elif val == 1:
            return cdt.Report(F"({val}) –111 dBm")
        elif val < 31:
            return cdt.Report(get_message(F"({val}) {-109+(val-2)*2} dBm"))
        elif val == 31:
            return cdt.Report(get_message(F"({val}) –51 dBm $or$ $greater$"))
        elif val == 99:
            return cdt.Report(get_message(F"({val}) $not_known_or_not_detectable$"))
        else:
            return cdt.Report(
                msg=F"({val})",
                log=cdt.Log(logging.WARN, "unknown value"))


class CellInfoType(cdt.Structure):
    """ Params of element """
    cell_ID: cdt.LongUnsigned
    location_ID: cdt.LongUnsigned
    signal_quality: SignalQuality
    ber: cdt.Unsigned


class AdjacentCellInfo(cdt.Structure):
    cell_ID: cdt.LongUnsigned
    signal_quality: SignalQuality


class AdjacentCells(cdt.Array):
    TYPE = AdjacentCellInfo


class GSMDiagnostic(ICAuto):
    """4.7.8 GSM diagnostic"""
    CLASS_ID = class_id.GSM_DIAGNOSTIC
    VERSION = 0
    A_ELEMENTS = (ICAElement(2, "operator", cdt.VisibleString, classifier=Classifier.DYNAMIC),
                  ICAElement(3, "status", Status, 0, 255, 0, classifier=Classifier.DYNAMIC),
                  ICAElement(4, "cs_attachment", CSAttachment, 0, 255, 0, classifier=Classifier.DYNAMIC),
                  ICAElement(5, "ps_status", PSStatus, 0, 255, 0, classifier=Classifier.DYNAMIC),
                  ICAElement(6, "cell_info", CellInfoType, classifier=Classifier.DYNAMIC),
                  ICAElement(7, "adjacent_cell", AdjacentCells, classifier=Classifier.DYNAMIC),
                  ICAElement(8, "capture_time", cdt.DateTime, classifier=Classifier.DYNAMIC))
    operator: Optional[cdt.VisibleString]
    status: Optional[Status]
    cs_attachment: Optional[CSAttachment]
    ps_status: Optional[PSStatus]
    cell_info: Optional[CellInfoType]
    adjacent_cell: Optional[AdjacentCells]
    capture_time: Optional[cdt.DateTime]

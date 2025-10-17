from . import ver0
from typing import Optional
from ...types import cdt
from ..cosem_interface_class import ICAElement, Classifier


class PSStatus(cdt.Enum, elements=tuple(range(7))):
    """ Indicates the packet switched status of the modem. """


class CellInfoType(cdt.Structure):
    """ Params of element """
    cell_ID: cdt.DoubleLongUnsigned
    location_ID: cdt.LongUnsigned
    signal_quality: ver0.SignalQuality
    ber: cdt.Unsigned
    mcc: cdt.LongUnsigned
    mnc: cdt.LongUnsigned
    channel_number: cdt.DoubleLongUnsigned


class AdjacentCellInfo(cdt.Structure):
    cell_ID: cdt.DoubleLongUnsigned
    signal_quality: ver0.SignalQuality


class AdjacentCells(cdt.Array):
    TYPE = AdjacentCellInfo


class GSMDiagnostic(ver0.GSMDiagnostic):
    VERSION = 1
    A_ELEMENTS = (ver0.GSMDiagnostic.getAElement(2).unwrap(),
                  ver0.GSMDiagnostic.getAElement(3).unwrap(),
                  ver0.GSMDiagnostic.getAElement(4).unwrap(),
                  ICAElement(5, "ps_status", PSStatus, 0, 255, 0, classifier=Classifier.DYNAMIC),
                  ICAElement(6, "cell_info", CellInfoType, classifier=Classifier.DYNAMIC),
                  ICAElement(7, "adjacent_cell", AdjacentCells, classifier=Classifier.DYNAMIC),
                  ver0.GSMDiagnostic.getAElement(8).unwrap())
    ps_status: Optional[PSStatus]
    cell_info: Optional[CellInfoType]
    adjacent_cell: Optional[AdjacentCells]

from ..__class_init__ import *
from . import ver0


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
    A_ELEMENTS = (ver0.GSMDiagnostic.getAElement(2).unwrap(),
                  ver0.GSMDiagnostic.getAElement(3).unwrap(),
                  ver0.GSMDiagnostic.getAElement(4).unwrap(),
                  ic.ICAElement(5, "ps_status", PSStatus, 0, 255, 0, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement(6, "cell_info", CellInfoType, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement(7, "adjacent_cell", AdjacentCells, classifier=ic.Classifier.DYNAMIC),
                  ver0.GSMDiagnostic.getAElement(8).unwrap())

    # def __new__(cls, *args, **kwargs):
    #     raise ValueError(F"version: {__name__[-1]} of {cls.__class__.__name__} not support framework")


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
    A_ELEMENTS = (ver0.GSMDiagnostic.get_attr_element(2),
                  ver0.GSMDiagnostic.get_attr_element(3),
                  ver0.GSMDiagnostic.get_attr_element(4),
                  ic.ICAElement("ps_status", PSStatus, 0, 255, 0, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("cell_info", CellInfoType, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("adjacent_cell", AdjacentCells, classifier=ic.Classifier.DYNAMIC),
                  ver0.GSMDiagnostic.get_attr_element(8))

    # def __new__(cls, *args, **kwargs):
    #     raise ValueError(F"version: {__name__[-1]} of {cls.__class__.__name__} not support framework")


from ..__class_init__ import *
from ...config_parser import get_message


class Status(cdt.Enum, elements=tuple(range(6))):
    """ Indicates the registration status of the  modem. """


class CSAttachment(cdt.Enum, elements=(0, 1, 2)):
    """ Indicates the current circuit switched status."""


class PSStatus(cdt.Enum, elements=tuple(range(5))):
    """ Indicates the packet switched status of the modem. """


class SignalQuality(cdt.Unsigned):
    """for string report"""
    def get_report(self, with_unit: bool = True) -> str:
        value = int(self)
        if value == 0:
            return get_message("–113 dBm $or$ $less$(0)")
        elif value == 1:
            return F"–111 dBm(1)"
        elif value < 31:
            return F"{-109+(value-2)*2} dBm({value})"
        elif value == 31:
            return get_message("–51 dBm $or$ $greater$(31)")
        elif value == 99:
            return get_message("$not_known_or_not_detectable$")
        else:
            return F"wrong {value=}"


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


class GSMDiagnostic(ic.COSEMInterfaceClasses):
    """ The GSM/GPRS network is undergoing constant changes in terms of registration status, signal quality etc. It is necessary to monitor and log the relevant parameters in order
     to obtain diagnostic information that allows identifying communication problems in the network. An instance of the 'GSM diagnostic' class stores parameters of the GSM/GPRS
     network necessary for analysing the operation of the network."""
    CLASS_ID = ClassID.GSM_DIAGNOSTIC
    VERSION = Version.V0
    A_ELEMENTS = (ic.ICAElement("operator", cdt.VisibleString, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("status", Status, 0, 255, 0, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("cs_attachment", CSAttachment, 0, 255, 0, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("ps_status", PSStatus, 0, 255, 0, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("cell_info", CellInfoType, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("adjacent_cell", AdjacentCells, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("capture_time", cdt.DateTime, classifier=ic.Classifier.DYNAMIC))

    def characteristics_init(self):
        """nothing do it"""

    @property
    def operator(self) -> cdt.VisibleString:
        return self.get_attr(2)

    @property
    def status(self) -> Status:
        return self.get_attr(3)

    @property
    def cs_attachment(self) -> CSAttachment:
        return self.get_attr(4)

    @property
    def ps_status(self) -> PSStatus:
        return self.get_attr(5)

    @property
    def cell_info(self) -> CellInfoType:
        return self.get_attr(6)

    @property
    def adjacent_cell(self) -> AdjacentCells:
        return self.get_attr(7)

    @property
    def capture_time(self) -> cdt.DateTime:
        return self.get_attr(8)

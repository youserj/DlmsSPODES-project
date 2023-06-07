from ..__class_init__ import *


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
    cell_ID: cdt.LongUnsigned
    location_ID: cdt.LongUnsigned
    signal_quality: SignalQuality
    ber: cdt.Unsigned


class AdjacentCellInfo(cdt.Structure):
    cell_ID: cdt.LongUnsigned
    signal_quality: cdt.Unsigned


class AdjacentCells(cdt.Array):
    TYPE = AdjacentCellInfo


class GSMDiagnostic(ic.COSEMInterfaceClasses):
    """ The GSM/GPRS network is undergoing constant changes in terms of registration status, signal quality etc. It is necessary to monitor and log the relevant parameters in order
     to obtain diagnostic information that allows identifying communication problems in the network. An instance of the 'GSM diagnostic' class stores parameters of the GSM/GPRS
     network necessary for analysing the operation of the network."""
    NAME = cn.GSM_DIAGNOSTIC
    CLASS_ID = ClassID.GSM_DIAGNOSTIC
    VERSION = Version.V0
    A_ELEMENTS = (ic.ICAElement(an.OPERATOR, cdt.VisibleString),
                  ic.ICAElement(an.STATUS, Status, 0, 255, 0),
                  ic.ICAElement(an.CS_ATTACHMENT, CSAttachment, 0, 255, 0),
                  ic.ICAElement(an.PS_STATUS, PSStatus, 0, 255, 0),
                  ic.ICAElement(an.CELL_INFO, CellInfoType),
                  ic.ICAElement(an.ADJACENT_CELL, AdjacentCells),
                  ic.ICAElement(an.CAPTURE_TIME, cdt.DateTime))

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

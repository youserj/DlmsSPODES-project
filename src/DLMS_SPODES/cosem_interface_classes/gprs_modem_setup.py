from . __class_init__ import *


class QoSElement(cdt.Structure):
    """ Params of element """
    values: tuple[cdt.Unsigned, cdt.Unsigned, cdt.Unsigned, cdt.Unsigned, cdt.Unsigned]
    ELEMENTS = (cdt.StructElement(cdt.se.PRECEDENCE, cdt.Unsigned),
                cdt.StructElement(cdt.se.DELAY, cdt.Unsigned),
                cdt.StructElement(cdt.se.RELIABILITY, cdt.Unsigned),
                cdt.StructElement(cdt.se.PEAK_THROUGHPUT, cdt.Unsigned),
                cdt.StructElement(cdt.se.MEAN_THROUGHPUT, cdt.Unsigned))

    @property
    def precedence(self) -> cdt.Unsigned:
        return self.values[0]

    @property
    def delay(self) -> cdt.Unsigned:
        return self.values[1]

    @property
    def reliability(self) -> cdt.Unsigned:
        return self.values[2]

    @property
    def peak_throughput(self) -> cdt.Unsigned:
        return self.values[3]

    @property
    def mean_throughput(self) -> cdt.Unsigned:
        return self.values[4]


class QualityOfService(cdt.Structure):
    """ Specifies the quality of service parameters. It is a structure of 2 elements:
            1: defines the default or minimum characteristics of the network concerned. These parameters have to be set to best effort value;
            2: defines the requested parameters. """
    values: tuple[QoSElement, QoSElement]
    ELEMENTS = (cdt.StructElement(cdt.se.DEFAULT, QoSElement),
                cdt.StructElement(cdt.se.REQUESTED, QoSElement))

    @property
    def default(self) -> QoSElement:
        return self.values[0]

    @property
    def requested(self) -> QoSElement:
        return self.values[1]


class GPRSModemSetup(ic.COSEMInterfaceClasses):
    """ This IC allow setting up GPRS modems, by handling all data necessary data for modem management. """
    NAME = cn.GPRS_MODEM_SETUP
    CLASS_ID = ut.CosemClassId(class_id.GPRS_MODEM_SETUP)
    VERSION = cdt.Unsigned(0)
    A_ELEMENTS = (ic.ICAElement(an.APN, cdt.OctetString),
                  ic.ICAElement(an.PIN_CODE, cdt.LongUnsigned),
                  ic.ICAElement(an.QUALITY_OF_SERVICE, QualityOfService))

    def characteristics_init(self):
        """nothing do it"""

    @property
    def APN(self) -> cdt.OctetString:
        return self.get_attr(2)

    @property
    def PIN_code(self) -> cdt.LongUnsigned:
        return self.get_attr(3)

    @property
    def quality_of_service(self) -> QualityOfService:
        return self.get_attr(4)

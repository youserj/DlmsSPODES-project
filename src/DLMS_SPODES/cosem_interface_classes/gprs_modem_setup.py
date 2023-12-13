from . __class_init__ import *


class QoSElement(cdt.Structure):
    """ Params of element """
    precedence: cdt.Unsigned
    delay: cdt.Unsigned
    reliability: cdt.Unsigned
    peak_throughput: cdt.Unsigned
    mean_throughput: cdt.Unsigned


class QualityOfService(cdt.Structure):
    """ Specifies the quality of service parameters. It is a structure of 2 elements:
            1: defines the default or minimum characteristics of the network concerned. These parameters have to be set to best effort value;
            2: defines the requested parameters. """
    default: QoSElement
    requested: QoSElement


class GPRSModemSetup(ic.COSEMInterfaceClasses):
    """ This IC allow setting up GPRS modems, by handling all data necessary data for modem management. """
    CLASS_ID = ClassID.GPRS_MODEM_SETUP
    VERSION = Version.V0
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

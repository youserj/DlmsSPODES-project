from typing import Optional
from ..types import cdt
from .cosem_interface_class import ICAElement, ICAuto
from .Overview import class_id


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


class GPRSModemSetup(ICAuto):
    """ This IC allow setting up GPRS modems, by handling all data necessary data for modem management. """
    CLASS_ID = class_id.GPRS_MODEM_SETUP
    VERSION = 0
    A_ELEMENTS = (ICAElement(2, "APN", cdt.OctetString),
                  ICAElement(3, "PIN_code", cdt.LongUnsigned),
                  ICAElement(4, "quality_of_service", QualityOfService))
    APN: Optional[cdt.OctetString]
    PIN_code: Optional[cdt.LongUnsigned]
    quality_of_service: Optional[QualityOfService]

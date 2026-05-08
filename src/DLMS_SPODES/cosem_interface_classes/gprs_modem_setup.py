from COSEMpdu.data import Structure, OctetString, LongUnsigned, Unsigned
from .cosem_interface_class import ICAElement, ICAuto
from ..types.type_alias import Attr


class QoSElement(Structure):
    """qos_element"""
    precedence: Unsigned
    delay: Unsigned
    reliability: Unsigned
    peak_throughput: Unsigned
    mean_throughput: Unsigned


class QualityOfService(Structure):
    """quality_of_service"""
    default_: QoSElement
    requested: QoSElement


class GPRSModemSetup(ICAuto):
    """4.7.7 GPRS modem setup"""
    CLASS_ID = 45
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "APN", OctetString),
        ICAElement(3, "PIN_code", LongUnsigned),
        ICAElement(4, "quality_of_service", QualityOfService))
    APN: Attr
    PIN_code: Attr
    quality_of_service: Attr

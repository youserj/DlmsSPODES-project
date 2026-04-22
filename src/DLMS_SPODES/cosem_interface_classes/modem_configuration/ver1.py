from COSEMpdu.data import Array, Structure, OctetString, LongUnsigned
from . import ver0
from ..cosem_interface_class import ICAElement, update_collection
from ...types.type_alias import Attr


class InitializationStringElement(Structure):
    """initialization_string_element"""
    request: OctetString
    response: OctetString
    delay_after_response: LongUnsigned


InitializationString = Array[InitializationStringElement]
"""initialization_string"""


class ModemConfigurationVer1(ver0.PSTNModemConfiguration):
    """4.7.4 Modem configuration"""
    VERSION = 1
    A_ELEMENTS = update_collection(
        ver0.PSTNModemConfiguration.A_ELEMENTS,
        ICAElement(3, "initialization_string", InitializationString))
    initialization_string: Attr

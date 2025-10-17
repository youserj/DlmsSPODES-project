from . import ver0
from typing import Optional
from ...types import cdt
from ..cosem_interface_class import ICAElement
from ..Overview import class_id


class InitializationStringElement(cdt.Structure):
    """initialization_string_element"""
    request: cdt.OctetString
    response: cdt.OctetString
    delay_after_response: cdt.LongUnsigned


class InitializationString(cdt.Array):
    """initialization_string attribute"""
    TYPE = InitializationStringElement


class ModemConfigurationVer1(ver0.PSTNModemConfiguration):
    """4.7.4 Modem configuration"""
    ClassID = class_id.MODEM_CONFIGURATION
    VERSION = 1
    A_ELEMENTS = (ver0.PSTNModemConfiguration.getAElement(2).unwrap(),
                  ICAElement(3, "initialization_string", InitializationString),
                  ver0.PSTNModemConfiguration.getAElement(4).unwrap())
    initialization_string: Optional[InitializationString]

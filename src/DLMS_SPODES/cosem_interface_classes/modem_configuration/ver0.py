from ...types.implementations.enums import CommSpeed
from typing import Optional
from ...types import cdt
from ..cosem_interface_class import ICAElement, ICAuto
from ..Overview import class_id


class InitializationStringElement(cdt.Structure):
    """ initialization_string_element"""
    request: cdt.OctetString
    response: cdt.OctetString


class InitializationString(cdt.Array):
    """initialization_string attribute"""
    TYPE = InitializationStringElement


class ModemProfileElement(cdt.OctetString):
    """modem_profile_element"""

    def __init__(self, value: bytes = b'OK'.hex()):
        super(ModemProfileElement, self).__init__(value)
        if bytes(self) not in self.get_validate_values():  # todo: make ReportMixin
            raise ValueError(F'Got modem profile element {bytes(self)}, expected {b", ".join(self.get_validate_values())}')
        else:
            pass

    @staticmethod
    def get_validate_values() -> tuple[bytes, ...]:
        return b'OK', b'CONNECT', b'RING', b'NO CARRIER', b'ERROR', b'CONNECT 1 200', b'NO DIAL TONE', b'BUSY', b'NO ANSWER', b'CONNECT 600', b'CONNECT 2 400', b'CONNECT 4 800', \
               b'CONNECT 9 600', b'CONNECT 14 400', b'CONNECT 28 800', b'CONNECT 36 600', b'CONNECT 56 000'


class ModemProfile(cdt.Array):
    """modem_profile attribute"""
    TYPE = ModemProfileElement


class PSTNModemConfiguration(ICAuto):
    """5.7.4 PSTN modem configuration"""
    CLASS_ID = class_id.MODEM_CONFIGURATION
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "comm_speed", CommSpeed, 0, 9, 5),
        ICAElement(3, "initialization_string", InitializationString),
        ICAElement(4, "modem_profile", ModemProfile)
    )
    comm_speed: Optional[CommSpeed]
    initialization_string: Optional[InitializationString]
    modem_profile: Optional[ModemProfile]

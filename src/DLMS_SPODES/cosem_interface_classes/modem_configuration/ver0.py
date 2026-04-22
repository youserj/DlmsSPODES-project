from COSEMpdu.x680.type import OCTET_STRING
from COSEMpdu.data import Array, Structure, OctetString
from ..iec_hdlc_setup.ver0 import CommSpeed
from ..cosem_interface_class import ICAElement, ICAuto
from ...types.type_alias import Attr


class InitializationStringElement(Structure):
    """ initialization_string_element"""
    request: OctetString
    response: OctetString


InitializationString = Array[InitializationStringElement]
"""initialization_string"""


class ModemProfileElement(OctetString):
    """modem_profile_element"""
    containing_value: tuple[OCTET_STRING, ...] = (
        b"OK", b"CONNECT", b"RING", b"NO CARRIER", b"ERROR", b"CONNECT 1 200", b"NO DIAL TONE", b"BUSY", b"NO ANSWER", b"CONNECT 600", b"CONNECT 2 400", b"CONNECT 4 800",
        b"CONNECT 9 600", b"CONNECT 14 400", b"CONNECT 28 800", b"CONNECT 36 600", b"CONNECT 56 000"
    )


ModemProfile = Array[ModemProfileElement]
"""modem_profile attribute"""


class PSTNModemConfiguration(ICAuto):
    """5.7.4 PSTN modem configuration"""
    CLASS_ID = 27
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "comm_speed", CommSpeed, 0, 9, 5),
        ICAElement(3, "initialization_string", InitializationString),
        ICAElement(4, "modem_profile", ModemProfile)
    )
    comm_speed: Attr
    initialization_string: Attr
    modem_profile: Attr

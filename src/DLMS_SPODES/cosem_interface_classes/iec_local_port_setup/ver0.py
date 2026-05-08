from typing import Final
from COSEMpdu.data import OctetString, Enum
from ..cosem_interface_class import ICAElement, ICAuto


class DefaultMode(Enum):
    """attribute default_mode"""
    IEC_62056_21: Final = 0
    DLMS_UA_1000_2: Final = 1


class Baud(Enum):
    """?"""
    _300_BAUD: Final = 0
    _600_BAUD: Final = 1
    _1200_BAUD: Final = 2
    _2400_BAUD: Final = 3
    _4800_BAUD: Final = 4
    _9600_BAUD: Final = 5
    _19200_BAUD: Final = 6
    _38400_BAUD: Final = 7
    _57600_BAUD: Final = 8
    _115200_BAUD: Final = 9


class ResponseTime(Enum):
    """response_time"""
    _20MS: Final = 0
    _200MS: Final = 1


class IECLocalPortSetup(ICAuto):
    """ This IC allows modelling the configuration of communication ports using the protocols specified in IEC 62056-21:2002. Several ports can be configured. """
    CLASS_ID = 19
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "default_mode", DefaultMode),
        ICAElement(3, "default_baud", Baud),
        ICAElement(4, "prop_baud", Baud),
        ICAElement(5, "responseTime", ResponseTime),
        ICAElement(6, "device_addr", OctetString),
        ICAElement(7, "pass_p1", OctetString),
        ICAElement(8, "pass_p2", OctetString),
        ICAElement(9, "pass_w5", OctetString),
    )

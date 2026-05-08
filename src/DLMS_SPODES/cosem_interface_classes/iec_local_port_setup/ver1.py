from typing import Final
from COSEMpdu.data import Enum
from ..cosem_interface_class import update_collection, ICAElement
from . import ver0


class DefaultMode(Enum):
    """attribute default_mode"""
    IEC_62056_21: Final = 0
    DLMS_UA_1000_2: Final = 1
    NOT_SPECIFIED: Final = 2


class IECLocalPortSetup(ver0.IECLocalPortSetup):
    """ This IC allows modelling the configuration of communication ports using the protocols specified in IEC 62056-21:2002. Several ports can be configured. """
    VERSION = 1
    A_ELEMENTS = update_collection(
        ver0.IECLocalPortSetup.A_ELEMENTS,
        ICAElement(2, "default_mode", DefaultMode),
    )

from typing import Final
from COSEMpdu.data import Enum
from ..cosem_interface_class import ICAElement, Classifier, update_collection
from ...types.type_alias import Attr
from . import ver0


class TransmissionSpeed(Enum):
    """attribute transmission_speed"""
    BAUD_50: Final = 0
    BAUD_300: Final = 1
    BAUD_600: Final = 2
    BAUD_1200: Final = 3
    BAUD_2400: Final = 4
    BAUD_4800: Final = 5
    BAUD_7200: Final = 6


class SFSKPhyMACSetup(ver0.SFSKPhyMACSetup):
    """4.10.1 S-FSK Phy&MAC setup"""
    VERSION = 1
    A_ELEMENTS = update_collection(
        ver0.SFSKPhyMACSetup.A_ELEMENTS,
        ICAElement(15, "transmission_speed", TransmissionSpeed, classifier=Classifier.STATIC)
    )
    transmission_speed: Attr

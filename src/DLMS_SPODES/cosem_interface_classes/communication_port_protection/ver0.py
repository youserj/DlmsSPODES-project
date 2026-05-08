from typing import Final
from COSEMpdu.data import Enum, LongUnsigned, DoubleLongUnsigned, Unsigned, OctetString
from ...types.type_alias import Attr
from ..cosem_interface_class import ICAuto, ICAElement, Classifier, ICMElement
from ...types.implementations import integers


class ProtectionMode(Enum):
    """attribute protection_mode"""
    LOCKED: Final = 0
    LOCKED_ON_FAILED_ATTEMPTS: Final = 1
    UNLOCKED: Final = 2


class ProtectionStatus(Enum):
    """attribute protection_status"""
    UNLOCKED: Final = 0
    TEMPORARILY_LOCKED: Final = 1
    LOCKED: Final = 2


class CommunicationPortProtection(ICAuto):
    """4.4.12 Communication port protection"""
    CLASS_ID = 124
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "protection_mode", ProtectionMode, classifier=Classifier.STATIC),
        ICAElement(3, "allowed_failed_attempts", LongUnsigned, classifier=Classifier.STATIC),
        ICAElement(4, "initial_lockout_time", DoubleLongUnsigned, classifier=Classifier.STATIC),
        ICAElement(5, "steepness_factor", Unsigned, classifier=Classifier.STATIC),
        ICAElement(6, "max_lockout_time", DoubleLongUnsigned, classifier=Classifier.STATIC),
        ICAElement(7, "port_reference", OctetString, classifier=Classifier.STATIC),
        ICAElement(8, "protection_status", ProtectionStatus, classifier=Classifier.DYNAMIC),
        ICAElement(9, "failed_attempts", DoubleLongUnsigned, classifier=Classifier.DYNAMIC),
        ICAElement(10, "cumulative_failed_attempts", DoubleLongUnsigned, classifier=Classifier.DYNAMIC)
    )
    M_ELEMENTS = ICMElement(1, "reset", integers.IntegerValue0),
    value: Attr

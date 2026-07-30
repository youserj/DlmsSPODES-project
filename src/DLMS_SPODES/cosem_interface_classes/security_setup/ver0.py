from typing import Final
from dataclasses import dataclass
from COSEMpdu.data import Array, Structure, OctetString, Enum
from ..cosem_interface_class import ICAElement, ICMElement, Classifier, ICAuto
from ...types.type_alias import Attr


class SecurityPolicy(Enum):
    """security_policy"""
    NOTHING: Final = 0
    ALL_MESSAGES_TO_BE_AUTHENTICATED: Final = 1
    ALL_MESSAGES_TO_BE_ENCRYPTED: Final = 2
    ALL_MESSAGES_TO_BE_AUTHENTICATED_AND_ENCRYPTED: Final = 3


class SecuritySuite(Enum):
    """security_suite"""
    AES_GCM_128_WITH_AES128_WRAP: Final = 0


class KeyID(Enum):
    """key_id"""
    GLOBAL_UNICAST_ENCRYPTION_KEY: Final = 0
    GLOBAL_BROADCAST_ENCRYPTION_KEY: Final = 1
    AUTHENTICATION_KEY: Final = 2


@dataclass
class KeyData(Structure):
    """key_data"""
    key_id: KeyID
    key_wrapped: OctetString


GlobalKeyTransfer = Array[KeyData]
"""attribute global_key_transfer"""


class SecuritySetup(ICAuto):
    """4.4.7 Security setup"""
    CLASS_ID = 64
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "security_policy", SecurityPolicy, 0, 3, 0),
        ICAElement(3, "security_suite", SecuritySuite, 0, 0, 0),
        ICAElement(4, "client_system_title", OctetString, classifier=Classifier.DYNAMIC),
        ICAElement(5, "server_system_title", OctetString))
    M_ELEMENTS = (
        ICMElement(1, "security_activate", SecurityPolicy),
        ICMElement(2, "global_key_transfer", GlobalKeyTransfer))
    security_policy: Attr
    security_suite: Attr
    client_system_title: Attr
    server_system_title: Attr

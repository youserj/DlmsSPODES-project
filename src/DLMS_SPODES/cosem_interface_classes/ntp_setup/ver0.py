from dataclasses import dataclass
from typing import Final
from COSEMpdu.data import Array, Structure, OctetString, Boolean, LongUnsigned, Enum, DoubleLongUnsigned
from ...types.implementations import integers
from ..cosem_interface_class import ICAElement, ICAuto, ICMElement
from ...types.type_alias import Attr


class ServerAddress(OctetString):
    """server_address attribute"""


class AuthenticationMethod(Enum):
    """authentication_method"""
    NO_SECURITY: Final = 0
    SHARED_SECRETS: Final = 1
    AUTO_KEY_IFF: Final = 2


@dataclass
class AuthenticationKey(Structure):
    """authentication_key"""
    key_id: DoubleLongUnsigned
    key: OctetString


AuthenticationKeys = Array[AuthenticationKey]
"""authentication_keys"""


class NTPSetup(ICAuto):
    """4.9.7 NTP setup"""
    CLASS_ID = 100
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "activated", Boolean, default=False),
        ICAElement(3, "server_address", ServerAddress),
        ICAElement(4, "server_port", LongUnsigned, default=123),
        ICAElement(5, "authentication_method", AuthenticationMethod),
        ICAElement(6, "authentication_keys", AuthenticationKeys),
        ICAElement(7, "client_key", OctetString))
    M_ELEMENTS = (
        ICMElement(1, "synchronize", integers.IntegerValue0),
        ICMElement(2, "add_authentication_key", AuthenticationKey),
        ICMElement(3, "delete_authentication_key", DoubleLongUnsigned),
    )
    activated: Attr
    server_address: Attr
    server_port: Attr
    authentication_method: Attr
    authentication_keys: Attr
    client_key: Attr

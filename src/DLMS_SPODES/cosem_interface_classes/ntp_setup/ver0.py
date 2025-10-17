from ...types.implementations import integers
from typing import Optional
from ...types import cdt
from ..cosem_interface_class import ICAElement, ICAuto, ICMElement
from ..Overview import class_id


class ServerAddress(cdt.OctetString):
    """server_address attribute"""


class AuthenticationMethod(cdt.Enum, elements=(0, 1, 2)):
    """authentication_method attribute"""


class AuthenticationKey(cdt.Structure):
    """authentication_key"""
    key_id: cdt.DoubleLongUnsigned
    key: cdt.OctetString


class AuthenticationKeys(cdt.Array):
    """authentication_keys"""
    TYPE = AuthenticationKey


class NTPSetup(ICAuto):
    """4.9.7 NTP setup"""
    CLASS_ID = class_id.NTP_SETUP
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "activated", cdt.Boolean, default=False),
        ICAElement(3, "server_address", ServerAddress),
        ICAElement(4, "server_port", cdt.LongUnsigned, default=123),
        ICAElement(5, "authentication_method", AuthenticationMethod),
        ICAElement(6, "authentication_keys", AuthenticationKeys),
        ICAElement(7, "client_key", cdt.OctetString))
    M_ELEMENTS = (
        ICMElement(1, "synchronize", integers.Only0),
        ICMElement(2, "add_authentication_key", AuthenticationKey),
        ICMElement(3, "delete_authentication_key", cdt.DoubleLongUnsigned),
    )
    activated: Optional[cdt.Boolean]
    server_address: Optional[ServerAddress]
    server_port: Optional[cdt.LongUnsigned]
    authentication_method: Optional[AuthenticationMethod]
    authentication_keys: Optional[AuthenticationKeys]
    client_key: Optional[cdt.OctetString]

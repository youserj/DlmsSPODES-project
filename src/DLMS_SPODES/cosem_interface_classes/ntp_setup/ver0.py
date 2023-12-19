from ..__class_init__ import *
from ...types.implementations import integers


class ServerAddress(cdt.OctetString):
    """"""


class AuthenticationMethod(cdt.Enum, elements=(0, 1, 2)):
    """Defines the authentication mode used for NTP protocol"""


class AuthenticationKey(cdt.Structure):
    """"""
    key_id: cdt.DoubleLongUnsigned
    key: cdt.OctetString


class AuthenticationKeys(cdt.Array):
    """Contains the necessary symmetric keys if shared secrets mode of authentication is used"""
    TYPE = AuthenticationKey


class NTPSetup(ic.COSEMInterfaceClasses):
    """DLMS UA 1000-1 Ed 14, 4.9.7 NTP setup"""
    CLASS_ID = ClassID.NTP_SETUP
    VERSION = Version.V0
    A_ELEMENTS = (
        ic.ICAElement("activated", cdt.Boolean, default=False),
        ic.ICAElement("server_address", ServerAddress),
        ic.ICAElement("server_port", cdt.LongUnsigned, default=123),
        ic.ICAElement("authentication_method", AuthenticationMethod),
        ic.ICAElement("authentication_keys", AuthenticationKeys),
        ic.ICAElement("client_key", cdt.OctetString))
    M_ELEMENTS = (
        ic.ICMElement("synchronize", integers.Only0),
        ic.ICMElement("add_authentication_key", AuthenticationKey),
        ic.ICMElement("delete_authentication_key", cdt.DoubleLongUnsigned),
    )

    def characteristics_init(self):
        """nothing do it"""

    @property
    def activated(self) -> cdt.Boolean:
        return self.get_attr(2)

    @property
    def server_address(self) -> ServerAddress:
        return self.get_attr(3)

    @property
    def server_port(self) -> cdt.LongUnsigned:
        return self.get_attr(4)

    @property
    def authentication_method(self) -> AuthenticationMethod:
        return self.get_attr(5)

    @property
    def authentication_keys(self) -> AuthenticationKeys:
        return self.get_attr(6)

    @property
    def client_key(self) -> cdt.OctetString:
        return self.get_attr(7)

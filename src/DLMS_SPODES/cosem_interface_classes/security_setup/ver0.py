from __future__ import annotations
from ..__class_init__ import *


class SecurityPolicy(cdt.Enum):
    """ Enforces authentication and/or encrypting algorithm provided with security_suite """
    ELEMENTS = {b'\x00': en.NOTHING,
                b'\x01': en.ALL_MESSAGES_TO_BE_AUTHENTICATION,
                b'\x02': en.ALL_MESSAGES_TO_BE_ENCRYPTED,
                b'\x03': en.ALL_MESSAGES_TO_BE_AUTH_AND_ENC,
                b'\x04': en.RESERVED,
                b'\x05': en.RESERVED,
                b'\x06': en.RESERVED,
                b'\x07': en.RESERVED,
                b'\x08': en.RESERVED,
                b'\x09': en.RESERVED,
                b'\x0a': en.RESERVED,
                b'\x0b': en.RESERVED,
                b'\x0c': en.RESERVED,
                b'\x0d': en.RESERVED,
                b'\x0e': en.RESERVED,
                b'\x0f': en.RESERVED}


class SecuritySuite(cdt.Enum):
    """Specifies authentication, encryption and key transport algorithm"""
    ELEMENTS = {b'\x00': en.AES_GCM_128,
                b'\x01': en.RESERVED,
                b'\x02': en.RESERVED,
                b'\x03': en.RESERVED,
                b'\x04': en.RESERVED,
                b'\x05': en.RESERVED,
                b'\x06': en.RESERVED,
                b'\x07': en.RESERVED,
                b'\x08': en.RESERVED,
                b'\x09': en.RESERVED,
                b'\x0a': en.RESERVED,
                b'\x0b': en.RESERVED,
                b'\x0c': en.RESERVED,
                b'\x0d': en.RESERVED,
                b'\x0e': en.RESERVED,
                b'\x0f': en.RESERVED}


class SecurityActivate(cdt.Enum):
    """For Activates and strengthens the security policy"""
    ELEMENTS = {b'\x00': en.NOTHING,
                b'\x01': en.ALL_MESSAGES_TO_BE_AUTHENTICATION,
                b'\x02': en.ALL_MESSAGES_TO_BE_ENCRYPTED,
                b'\x03': en.ALL_MESSAGES_TO_BE_AUTH_AND_ENC}


class KeyID(cdt.Enum):
    """Use only in KeyData structure"""
    ELEMENTS = {b'\x00': en.GUEK,
                b'\x01': en.GBEK,
                b'\x02': en.GAK}


class KeyData(cdt.Structure):
    """ TODO: """
    values: tuple[KeyID, cdt.OctetString]
    ELEMENTS = (cdt.StructElement(cdt.se.KEY_ID, KeyID),
                cdt.StructElement(cdt.se.KEY_WRAPPED, cdt.OctetString))

    @property
    def key_id(self) -> KeyID:
        return self.values[0]

    @property
    def key_wrapped(self) -> cdt.OctetString:
        return self.values[1]


class GlobalKeyTransfer(cdt.Array):
    """ Array of key_data """
    TYPE = KeyData


class SecuritySetup(ic.COSEMInterfaceClasses):
    """ Instances of the “Security setup” IC contain the necessary information on the security suite in use and the security policy applicable between the server and a client
    and/or third party indentify by their respective system titles. They also provide methods to increase the level of security and to manage symmetric keys, asymmetric key pairs
     and certificates """
    NAME = cn.SECURITY_SETUP
    CLASS_ID = ut.CosemClassId(class_id.SECURITY_SETUP)
    VERSION = cdt.Unsigned(0)
    A_ELEMENTS = (ic.ICAElement(an.SECURITY_POLICY, SecurityPolicy, 0, 3, 0),
                  ic.ICAElement(an.SECURITY_SUITE, SecuritySuite, 0, 0, 0),
                  ic.ICAElement(an.CLIENT_SYSTEM_TITLE, cdt.OctetString),
                  ic.ICAElement(an.SERVER_SYSTEM_TITLE, cdt.OctetString))

    M_ELEMENTS = (ic.ICMElement(mn.SECURITY_ACTIVATE, SecurityActivate),
                  ic.ICMElement(mn.GLOBAL_KEY_TRANSFER, GlobalKeyTransfer))

    def characteristics_init(self):
        """nothing do it"""

    @property
    def security_policy(self) -> SecurityPolicy:
        return self.get_attr(2)

    @property
    def security_suite(self) -> SecuritySuite:
        return self.get_attr(3)

    @property
    def client_system_title(self) -> cdt.OctetString:
        return self .get_attr(4)

    @property
    def server_system_title(self) -> cdt.OctetString:
        return self .get_attr(5)

    @property
    def security_activate(self) -> SecurityActivate:
        return self .get_meth(1)

    @property
    def global_key_transfer(self) -> GlobalKeyTransfer:
        return self .get_meth(2)

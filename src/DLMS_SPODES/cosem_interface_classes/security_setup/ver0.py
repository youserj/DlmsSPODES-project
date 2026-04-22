from typing import Optional
from ...types import cdt
from ..cosem_interface_class import ICAElement, ICMElement, Classifier, ICAuto


class SecurityPolicy(cdt.Enum, elements=tuple(range(16))):
    """ Enforces authentication and/or encrypting algorithm provided with security_suite """


class SecuritySuite(cdt.Enum, elements=tuple(range(16))):
    """Specifies authentication, encryption and key transport algorithm"""
    AES_GCM_128_AUT_ENCR_AND_AES_128_KEY_WRAP = 0


class KeyID(cdt.Enum, elements=(0, 1, 2)):
    """Use only in KeyData structure"""


class KeyData(cdt.Structure):
    """ TODO: """
    key_id: KeyID
    key_wrapped: cdt.OctetString


class GlobalKeyTransfer(cdt.Array):
    """ Array of key_data """
    TYPE = KeyData


class SecuritySetup(ICAuto):
    """4.4.7 Security setup"""
    CLASS_ID = 64
    VERSION = 0
    A_ELEMENTS = (ICAElement(2, "security_policy", SecurityPolicy, 0, 3, 0),
                  ICAElement(3, "security_suite", SecuritySuite, 0, 0, 0),
                  ICAElement(4, "client_system_title", cdt.OctetString, classifier=Classifier.DYNAMIC),
                  ICAElement(5, "server_system_title", cdt.OctetString))

    M_ELEMENTS = (ICMElement(1, "security_activate", SecurityPolicy),
                  ICMElement(2, "global_key_transfer", GlobalKeyTransfer))
    security_policy: Optional[SecurityPolicy]
    security_suite: Optional[SecuritySuite]
    client_system_title: Optional[cdt.OctetString]
    server_system_title: Optional[cdt.OctetString]

from ..__class_init__ import *


class SecurityPolicy(cdt.Enum, elements=tuple(range(16))):
    """ Enforces authentication and/or encrypting algorithm provided with security_suite """


class SecuritySuite(cdt.Enum, elements=tuple(range(16))):
    """Specifies authentication, encryption and key transport algorithm"""


class KeyID(cdt.Enum, elements=(0, 1, 2)):
    """Use only in KeyData structure"""


class KeyData(cdt.Structure):
    """ TODO: """
    key_id: KeyID
    key_wrapped: cdt.OctetString


class GlobalKeyTransfer(cdt.Array):
    """ Array of key_data """
    TYPE = KeyData


class SecuritySetup(ic.COSEMInterfaceClasses):
    """ Instances of the “Security setup” IC contain the necessary information on the security suite in use and the security policy applicable between the server and a client
    and/or third party indentify by their respective system titles. They also provide methods to increase the level of security and to manage symmetric keys, asymmetric key pairs
     and certificates """
    NAME = cn.SECURITY_SETUP
    CLASS_ID = ClassID.SECURITY_SETUP
    VERSION = Version.V0
    A_ELEMENTS = (ic.ICAElement(an.SECURITY_POLICY, SecurityPolicy, 0, 3, 0),
                  ic.ICAElement(an.SECURITY_SUITE, SecuritySuite, 0, 0, 0),
                  ic.ICAElement(an.CLIENT_SYSTEM_TITLE, cdt.OctetString, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement(an.SERVER_SYSTEM_TITLE, cdt.OctetString))

    M_ELEMENTS = (ic.ICMElement(mn.SECURITY_ACTIVATE, SecurityPolicy),
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
    def security_activate(self) -> SecurityPolicy:
        return self .get_meth(1)

    @property
    def global_key_transfer(self) -> GlobalKeyTransfer:
        return self .get_meth(2)

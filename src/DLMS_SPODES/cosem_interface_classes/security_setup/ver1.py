from __future__ import annotations
from . import ver0
from ..__class_init__ import *


class SecurityPolicyVer1(cdt.FlagMixin, cdt.Enum, elements=tuple(range(8))):
    """ Enforces authentication and/or encryption and/or digital signature using the security algorithms available within security suite. It applies independently for requests and
     responses. When enum value is interpreted as an unsigned, the meaning of each bit is as shown below """


class CertificateEntity(cdt.Enum, elements=(0, 1, 2, 3)):
    """TODO:"""


class CertificateType(cdt.Enum, elements=(0, 1, 2, 3)):
    """TODO:"""


class SecuritySuite(cdt.Enum, elements=(0, 1, 2)):
    """Version 0 extension"""


class CertificateInfo(cdt.Structure):
    """ TODO: """
    values: tuple[CertificateEntity, CertificateType, cdt.OctetString, cdt.OctetString, cdt.OctetString, cdt.OctetString]
    ELEMENTS = (cdt.StructElement(cdt.se.CERTIFICATE_ENTITY, CertificateEntity),
                cdt.StructElement(cdt.se.CERTIFICATE_TYPE, CertificateType),
                cdt.StructElement(cdt.se.SERIAL_NUMBER, cdt.OctetString),
                cdt.StructElement(cdt.se.ISSUER, cdt.OctetString),
                cdt.StructElement(cdt.se.SUBJECT, cdt.OctetString),
                cdt.StructElement(cdt.se.SUBJECT_ALT_NAME, cdt.OctetString))

    @property
    def certificate_entity(self) -> CertificateEntity:
        return self.values[0]

    @property
    def certificate_type(self) -> CertificateType:
        return self.values[1]

    @property
    def serial_number(self) -> cdt.OctetString:
        return self.values[2]

    @property
    def issuer(self) -> cdt.OctetString:
        return self.values[3]

    @property
    def subject(self) -> cdt.OctetString:
        return self.values[4]

    @property
    def subject_alt_name(self) -> cdt.OctetString:
        return self.values[5]


class Certificates(cdt.Array):
    """Carries information on the X.509 v3 Certificates available and stored in the server"""
    TYPE = CertificateInfo


class KeyID(cdt.Enum, elements=(0, 1, 2, 3)):
    """Version 0 extension"""


class KeyTransferData(cdt.Structure):
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


class KeyTransfer(cdt.Array):
    """ Array of key_transfer_data """
    TYPE = KeyTransferData


class KeyAgreementData(cdt.Structure):
    """ TODO: """
    values: tuple[KeyID, cdt.OctetString]
    ELEMENTS = (cdt.StructElement(cdt.se.KEY_ID, KeyID),
                cdt.StructElement(cdt.se.KEY_DATA, cdt.OctetString))

    @property
    def key_id(self) -> KeyID:
        return self.values[0]

    @property
    def key_data(self) -> cdt.OctetString:
        return self.values[1]


class KeyAgreement(cdt.Array):
    """ Array of key_agreement_data """
    TYPE = KeyAgreementData


class KeyPair(cdt.Enum, elements=(0, 1, 2)):
    """TODO:"""


class CertificateIdentificationByEntity(cdt.Structure):
    """ TODO: """
    values: tuple[CertificateEntity, CertificateType, cdt.OctetString]
    ELEMENTS = (cdt.StructElement(cdt.se.CERTIFICATE_ENTITY, CertificateEntity),
                cdt.StructElement(cdt.se.CERTIFICATE_TYPE, CertificateType),
                cdt.StructElement(cdt.se.SYSTEM_TITLE, cdt.OctetString))

    @property
    def certificate_entity(self) -> CertificateEntity:
        return self.values[0]

    @property
    def certificate_type(self) -> CertificateType:
        return self.values[1]

    @property
    def system_title(self) -> cdt.OctetString:
        return self.values[2]


class CertificateIdentificationBySerial(cdt.Structure):
    """ TODO: """
    values: tuple[cdt.OctetString, cdt.OctetString]
    ELEMENTS = (cdt.StructElement(cdt.se.SERIAL_NUMBER, cdt.OctetString),
                cdt.StructElement(cdt.se.ISSUER, cdt.OctetString))

    @property
    def serial_number(self) -> cdt.OctetString:
        return self.values[0]

    @property
    def issuer(self) -> cdt.OctetString:
        return self.values[1]


class CertificateIdentificationType(cdt.Enum, elements=(0, 1)):
    """TODO:"""


class CertificateIdentificationOption(ut.CHOICE):
    TYPE = cdt.Structure
    ELEMENTS = {0: ut.SequenceElement('by entity', CertificateIdentificationByEntity),
                1: ut.SequenceElement('by serial', CertificateIdentificationBySerial)}


certificate_identification_option = CertificateIdentificationOption()


class CertificateIdentification(cdt.Structure):
    """Override several methods of cdt.Structure. It limited Structure."""
    values: tuple[CertificateIdentificationType, CertificateIdentificationByEntity | CertificateIdentificationBySerial]

    def __init__(self):
        self.__dict__["values"] = (CertificateIdentificationType(0), CertificateIdentificationByEntity())
        self.certificate_identification_type.register_cb_post_set(self.__set_certificate_identification_type)

    def __set_certificate_identification_type(self):
        self.__dict__["values"] = (self.certificate_identification_type, certificate_identification_option(int(self.certificate_identification_type)))

    @property
    def ELEMENTS(self) -> tuple[cdt.StructElement, cdt.StructElement]:
        return (cdt.StructElement(cdt.se.CERTIFICATE_IDENTIFICATION_TYPE, CertificateIdentificationType),
                cdt.StructElement(cdt.se.CERTIFICATION_IDENTIFICATION_OPTIONS,
                                  CertificateIdentificationByEntity if int(self.certificate_identification_type) == 0 else CertificateIdentificationBySerial))

    @property
    def certificate_identification_type(self) -> CertificateIdentificationType:
        return self.values[0]

    @property
    def certificate_identification_options(self) -> CertificateIdentificationByEntity | CertificateIdentificationBySerial:
        return self.values[1]


class SecuritySetup(ver0.SecuritySetup):
    VERSION = Version.V1
    A_ELEMENTS = (ic.ICAElement(an.SECURITY_POLICY, SecurityPolicyVer1),
                  ic.ICAElement(an.SECURITY_SUITE, SecuritySuite),
                  ver0.SecuritySetup.get_attr_element(4),
                  ver0.SecuritySetup.get_attr_element(5),
                  ic.ICAElement(an.CERTIFICATES, Certificates))

    M_ELEMENTS = (ic.ICMElement(mn.SECURITY_ACTIVATE, SecurityPolicyVer1),
                  ic.ICMElement(mn.KEY_TRANSFER, KeyTransfer),
                  ic.ICMElement(mn.KEY_AGREEMENT, KeyAgreement),
                  ic.ICMElement(mn.GENERATE_KEY_PAIR, KeyPair),
                  ic.ICMElement(mn.GENERATE_CERTIFICATE_REQUEST, KeyPair),
                  ic.ICMElement(mn.IMPORT_CERTIFICATE, cdt.OctetString),
                  ic.ICMElement(mn.EXPORT_CERTIFICATE, CertificateIdentification),
                  ic.ICMElement(mn.REMOVE_CERTIFICATE, CertificateIdentification))

    def characteristics_init(self):
        self.set_attr(2, None)
        self.set_attr(3, None)
        self.set_attr(6, None)

    @property
    def security_policy(self) -> SecurityPolicyVer1:
        return self.get_attr(2)

    @property
    def security_suite(self) -> SecuritySuite:
        return self.get_attr(3)

    @property
    def certificates(self) -> Certificates:
        return self.get_attr(6)

    @property
    def security_activate(self) -> SecurityPolicyVer1:
        return self.get_meth(1)

    @property
    def key_transfer(self) -> KeyTransferData:
        return self .get_meth(2)

    def key_agreement(self) -> KeyAgreement:
        return self .get_meth(3)

    def generate_certificate_request(self) -> KeyPair:
        return self .get_meth(4)

    def import_certificate(self) -> cdt.OctetString:
        return self .get_meth(5)

    def export_certificate(self) -> CertificateIdentification:
        return self .get_meth(6)

    def remove_certificate(self) -> CertificateIdentification:
        return self .get_meth(7)

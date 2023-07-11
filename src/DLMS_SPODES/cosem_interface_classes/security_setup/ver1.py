from . import ver0
from ..__class_init__ import *
from ...types import choices


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
    certificate_entity: CertificateEntity
    certificate_type: CertificateType
    serial_number: cdt.OctetString
    issuer: cdt.OctetString
    subject: cdt.OctetString
    subject_alt_name: cdt.OctetString


class Certificates(cdt.Array):
    """Carries information on the X.509 v3 Certificates available and stored in the server"""
    TYPE = CertificateInfo


class KeyID(cdt.Enum, elements=(0, 1, 2, 3)):
    """Version 0 extension"""


class KeyTransferData(cdt.Structure):
    """ TODO: """
    key_id: KeyID
    key_wrapped: cdt.OctetString


class KeyTransfer(cdt.Array):
    """ Array of key_transfer_data """
    TYPE = KeyTransferData


class KeyAgreementData(cdt.Structure):
    """ TODO: """
    key_id: KeyID
    key_data: cdt.OctetString


class KeyAgreement(cdt.Array):
    """ Array of key_agreement_data """
    TYPE = KeyAgreementData


class KeyPair(cdt.Enum, elements=(0, 1, 2)):
    """TODO:"""


class CertificateIdentificationByEntity(cdt.Structure):
    """ TODO: """
    certificate_entity: CertificateEntity
    certificate_type: CertificateType
    system_title: cdt.OctetString


class CertificateIdentificationBySerial(cdt.Structure):
    """ TODO: """
    serial_number: cdt.OctetString
    issuer: cdt.OctetString


class CertificateIdentificationType(cdt.Enum, elements=(0, 1)):
    """TODO:"""


class CertificationIdentificationOption(ut.CHOICE):
    TYPE = cdt.Structure
    ELEMENTS = {0: ut.SequenceElement('by entity', CertificateIdentificationByEntity),
                1: ut.SequenceElement('by serial', CertificateIdentificationBySerial)}


certification_identification_option = CertificationIdentificationOption()


class CertificateIdentification(choices.StructureMixin, cdt.Structure):
    """Override several methods of cdt.Structure. It limited Structure."""
    certificate_identification_type: CertificateIdentificationType
    certification_identification_options: certification_identification_option


class SecuritySetup(ver0.SecuritySetup):
    VERSION = Version.V1
    A_ELEMENTS = (ic.ICAElement(an.SECURITY_POLICY, SecurityPolicyVer1),
                  ic.ICAElement(an.SECURITY_SUITE, SecuritySuite),
                  ver0.SecuritySetup.get_attr_element(4),
                  ver0.SecuritySetup.get_attr_element(5),
                  ic.ICAElement(an.CERTIFICATES, Certificates, classifier=ic.Classifier.DYNAMIC))

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

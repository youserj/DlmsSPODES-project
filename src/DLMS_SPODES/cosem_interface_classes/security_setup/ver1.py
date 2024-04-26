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


class SecuritySuite(ver0.SecuritySuite, elements=(0, 1, 2)):
    """Version 0 extension"""
    AES_GCM_128_AUT_ENCR_ECDSA_P_256_DIG_SIGN_ECDH_P_256_KEY_AGR_SHA_256_HASH_V44_COMPR_AND_AES_128_KEY_WRAP = 1
    AES_GCM_256_AUT_ENCR_ECDSA_P_384_DIG_SIGN_ECDH_P_384_KEY_AGR_SHA_384_HASH_V44_COMPR_AND_AES_256_KEY_WRAP = 2


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
    ELEMENTS = {0: ut.SequenceElement('by entity', CertificateIdentificationByEntity),
                1: ut.SequenceElement('by serial', CertificateIdentificationBySerial)}


certification_identification_option = CertificationIdentificationOption()


class CertificateIdentification(choices.StructureMixin, cdt.Structure):
    """Override several methods of cdt.Structure. It limited Structure."""
    certificate_identification_type: CertificateIdentificationType
    certification_identification_options: certification_identification_option


class SecuritySetup(ver0.SecuritySetup):
    VERSION = Version.V1
    A_ELEMENTS = (ic.ICAElement("security_policy", SecurityPolicyVer1),
                  ic.ICAElement("security_suite", SecuritySuite),
                  ver0.SecuritySetup.get_attr_element(4),
                  ver0.SecuritySetup.get_attr_element(5),
                  ic.ICAElement("certificates", Certificates, classifier=ic.Classifier.DYNAMIC))

    M_ELEMENTS = (ic.ICMElement("security_activate", SecurityPolicyVer1),
                  ic.ICMElement("key_transfer", KeyTransfer),
                  ic.ICMElement("key_agreement", KeyAgreement),
                  ic.ICMElement("generate_key_pair", KeyPair),
                  ic.ICMElement("generate_certificate_request", KeyPair),
                  ic.ICMElement("import_certificate", cdt.OctetString),
                  ic.ICMElement("export_certificate", CertificateIdentification),
                  ic.ICMElement("remove_certificate", CertificateIdentification))

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

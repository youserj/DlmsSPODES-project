from . import ver0
from ...types import choices, cdt, ut
from typing import Optional
from ...types.type_alias import Attr
from ..cosem_interface_class import ICAElement, ICMElement, Classifier


class SecurityPolicy(cdt.Enum, cdt.IntegerFlag):
    """ security_policy"""


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
    TYPE = cdt.Structure
    ELEMENTS = {0: ut.SequenceElement('by entity', CertificateIdentificationByEntity),
                1: ut.SequenceElement('by serial', CertificateIdentificationBySerial)}


certification_identification_option = CertificationIdentificationOption()


class CertificateIdentification(choices.StructureMixin, cdt.Structure):
    """Override several methods of cdt.Structure. It limited Structure."""
    certificate_identification_type: CertificateIdentificationType
    certification_identification_options: certification_identification_option


class SecuritySetup(ver0.SecuritySetup):
    VERSION = 1
    A_ELEMENTS = (ICAElement(2, "security_policy", SecurityPolicy),
                  ver0.SecuritySetup.getAElement(3),
                  ver0.SecuritySetup.getAElement(4),
                  ver0.SecuritySetup.getAElement(5),
                  ICAElement(6, "certificates", Certificates, classifier=Classifier.DYNAMIC))

    M_ELEMENTS = (ICMElement(1, "security_activate", SecurityPolicy),
                  ICMElement(2, "key_transfer", KeyTransfer),
                  ICMElement(3, "key_agreement", KeyAgreement),
                  ICMElement(4, "generate_key_pair", KeyPair),
                  ICMElement(5, "generate_certificate_request", KeyPair),
                  ICMElement(6, "import_certificate", cdt.OctetString),
                  ICMElement(7, "export_certificate", CertificateIdentification),
                  ICMElement(8, "remove_certificate", CertificateIdentification))
    security_policy: Attr
    security_suite: Attr
    certificates: Attr

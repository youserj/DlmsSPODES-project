from typing import Final, TypeAlias
from COSEMpdu.data import Array, Structure, OctetString, Enum, BitMixin, DiscriminatedUnion, ExternallyData
from COSEMpdu.axdr import NamedType
from . import ver0
from ...types.type_alias import Attr
from ..cosem_interface_class import ICAElement, ICMElement, Classifier, update_collection


class SecurityPolicy(BitMixin, Enum):
    """security_policy"""
    AUTHENTICATED_REQUEST: Final = 0b100
    ENCRYPTED_REQUEST: Final = 0b1000
    DIGITALLY_SIGNED_REQUEST: Final = 0b1_0000
    AUTHENTICATED_RESPONSE: Final = 0b10_0000
    ENCRYPTED_RESPONSE: Final = 0b100_0000
    DIGITALLY_SIGNED_RESPONSE: Final = 0b1000_0000


class SecuritySuite(Enum):
    """security_suite"""
    AES_GCM_128_WITH_AES128_WRAP: Final = 0
    AES_GCM_128_WITH_ECDSA_P256_ECDH_P256_SHA256_V44_WRAP: Final = 1
    AES_GCM_256_WITH_ECDSA_P384_ECDH_P384_SHA384_V44_WRAP: Final = 2


class CertificateEntity(Enum):
    """certificate_entity"""
    SERVER: Final = 0
    CLIENT_OR_THIRD_PARTY: Final = 1
    CERTIFICATION_AUTHORITY: Final = 2
    OTHER: Final = 3


class CertificateType(Enum):
    """certificate_type"""
    DIGITAL_SIGNATURE: Final = 0
    KEY_AGREEMENT: Final = 1
    TLS: Final = 2
    OTHER: Final = 3


class CertificateInfo(Structure):
    """certificate_info"""
    certificate_entity: CertificateEntity
    certificate_type: CertificateType
    serial_number: OctetString
    issuer: OctetString
    subject: OctetString
    subject_alt_name: OctetString


Certificates = Array[CertificateInfo]
"""attribute certificates"""


class KeyID(Enum):
    """key_id"""
    GUEK: Final = 0  # global unicast encryption key
    GBEK: Final = 1  # global broadcast encryption key
    GAK: Final = 2   # authentication key
    KEK: Final = 3   # master key


class KeyTransferData(Structure):
    """key_transfer_data"""
    key_id: KeyID
    key_wrapped: OctetString


KeyTransfer = Array[KeyTransferData]
"""method key_transfer"""


class KeyAgreementData(Structure):
    """key_agreement_data"""
    key_id: KeyID
    key_data: OctetString


KeyAgreement = Array[KeyAgreementData]
"""method key_agreement"""


class KeyPair(Enum):
    """key_pair"""
    DIGITAL_SIGNATURE_KEY_PAIR: Final = 0
    KEY_AGREEMENT_KEY_PAIR: Final = 1
    TLS_KEY_PAIR: Final = 2


class CertificateIdentificationByEntity(Structure):
    """certificate_identification_by_entity"""
    certificate_entity: CertificateEntity
    certificate_type: CertificateType
    system_title: OctetString


class CertificateIdentificationBySerial(Structure):
    """certificate_identification_by_serial"""
    serial_number: OctetString
    issuer: OctetString


class CertificateIdentificationType(Enum):
    """certificate_identification_type"""
    CERTIFICATE_IDENTIFICATION_ENTITY: Final = 0
    CERTIFICATE_IDENTIFICATION_SERIAL: Final = 1


CertificateIdentificationT: TypeAlias = CertificateIdentificationByEntity | CertificateIdentificationBySerial


class CertificateIdentificationData(ExternallyData[CertificateIdentificationT]):
    """Controlled subset of alternatives to simplify testing"""
    alternatives = {
        0: NamedType("certificate_identification_entity", CertificateIdentificationByEntity),
        1: NamedType("certificate_identification_serial", CertificateIdentificationBySerial),
    }


class CertificateIdentification(DiscriminatedUnion):
    """certificate_identification"""
    type: CertificateIdentificationType
    option:  CertificateIdentificationData


class SecuritySetup(ver0.SecuritySetup):
    VERSION = 1
    A_ELEMENTS = update_collection(
        ver0.SecuritySetup.A_ELEMENTS,
        ICAElement(2, "security_policy", SecurityPolicy),
        ICAElement(3, "security_suite", SecuritySuite, 0, 0, 0),
        ICAElement(6, "certificates", Certificates, classifier=Classifier.DYNAMIC)
    )
    M_ELEMENTS = (
        ICMElement(1, "security_activate", SecurityPolicy),
        ICMElement(2, "key_transfer", KeyTransfer),
        ICMElement(3, "key_agreement", KeyAgreement),
        ICMElement(4, "generate_key_pair", KeyPair),
        ICMElement(5, "generate_certificate_request", KeyPair),
        ICMElement(6, "import_certificate", OctetString),
        ICMElement(7, "export_certificate", CertificateIdentification),
        ICMElement(8, "remove_certificate", CertificateIdentification))
    security_policy: Attr
    security_suite: Attr
    certificates: Attr

from dataclasses import dataclass
from typing import TypeAlias, Final
from COSEMpdu.data import Array, Integer, Structure, LongUnsigned, OctetString, Enum, DoubleLongUnsigned, NullData, ExternallyData, DiscriminatedUnion
from COSEMpdu.axdr import NamedType
from . import ver0
from ...types.type_alias import Attr
from ...types import cst
from ..cosem_interface_class import ICAElement, update_collection


@dataclass
class RestrictionByEntry(Structure):
    """restriction_by_entry"""
    from_entry: DoubleLongUnsigned
    to_entry: DoubleLongUnsigned


@dataclass
class RestrictionByDate(Structure):
    """restriction_by_date"""
    from_date: OctetString
    to_date: OctetString


RestrictionValueType: TypeAlias = NullData | RestrictionByDate | RestrictionByEntry


class RestrictionValue(ExternallyData[RestrictionValueType]):
    alternatives = {
        0: NamedType("NO RESTRICTION", NullData),
        1: NamedType("BY DATE", RestrictionByDate),
        2: NamedType("BY ENTRY", RestrictionByEntry)
    }


class RestrictionType(Enum):
    """restriction_type"""
    NONE = 0
    RANGE_BY_DATE = 1
    RANGE_BY_ENTRY = 2


class RestrictionElement(DiscriminatedUnion):
    """restriction_element"""
    restriction_type: RestrictionType
    restriction_value: RestrictionValue


@dataclass
class PushObjectDefinition(Structure):
    """push_object_definition"""
    class_id: LongUnsigned
    logical_name: cst.LogicalName
    attribute_index: Integer
    data_index: LongUnsigned
    restriction: RestrictionElement


PushObjectList = Array[PushObjectDefinition]
"""push_object_list attribute"""


class TransportServiceType(Enum):  # TODO: elements 200.. is manufacturer specific
    """transport_service_type"""
    TCP: Final = 0
    UDP: Final = 1
    FTP: Final = 2
    SMTP: Final = 3
    SMS: Final = 4
    HDLC: Final = 5
    M_BUS: Final = 6
    ZIG_BEE: Final = 7
    DLMS_GATEWAY: Final = 8


class MessageType(Enum):  # TODO: elements 128.. is manufacturer specific
    """message_type"""
    A_XDR_ENCODED_XDLMS_APDU: Final = 4
    XML_ENCODED_XDLMS_APDU: Final = 5


@dataclass
class SendDestinationAndMethod(Structure):
    """send_destination_and_method"""
    transport_service: TransportServiceType
    destination: OctetString
    message: MessageType


class IdentifiedKeyInfoOptions(Enum):
    """identified_key_info_options"""
    GLOBAL_UNICAST_ENCRYPTION_KEY = 0
    GLOBAL_BROADCAST_ENCRYPTION_KEY = 1


class KekId(Enum):
    """kek_id"""
    MASTER_KEY: Final = 0


@dataclass
class WrappedKeyInfoOptions(Structure):
    """wrapped_key_info_options"""
    kek_id: KekId
    key_ciphered_data: OctetString


@dataclass
class AgreedKeyInfoOptions(Structure):
    """agreed_key_info_options"""
    key_parameters: OctetString
    key_ciphered_data: OctetString


class KeyInfoType(Enum):
    """key_info_type"""
    IDENTIFIED_KEY = 0
    WRAPPED_KEY = 1
    AGREED_KEY = 2


KeyInfoOptionsType: TypeAlias = IdentifiedKeyInfoOptions | WrappedKeyInfoOptions | AgreedKeyInfoOptions


class KeyInfoOptions(ExternallyData[KeyInfoOptionsType]):
    """key_info_options"""
    alternatives = {
        0: NamedType("IdentifiedKeyInfoOptions", IdentifiedKeyInfoOptions),
        1: NamedType("WrappedKeyInfoOptions", WrappedKeyInfoOptions),
        2: NamedType("AgreedKeyInfoOptions", AgreedKeyInfoOptions)
    }


class KeyInfoElement(DiscriminatedUnion):
    """key_info_element"""
    key_info_type: KeyInfoType
    key_info_options: KeyInfoOptions


class ProtectionType(Enum):
    """protection_type"""
    AUTHENTICATION: Final = 0
    ENCRYPTION: Final = 1
    AUTHENTICATION_AND_ENCRYPTION: Final = 2
    DIGITAL_SIGNATURE: Final = 3


@dataclass
class ProtectionOptions(Structure):
    transaction_id: OctetString
    originator_system_title: OctetString
    recipient_system_title: OctetString
    other_information: OctetString
    key_info: KeyInfoElement


@dataclass
class ProtectionParametersElement(Structure):
    protection_type: ProtectionType
    protection_options: ProtectionOptions


PushProtectionParameters = Array[ProtectionParametersElement]


class PushSetup(ver0.PushSetup):
    """5.4.10 Push Setup"""
    VERSION = 1
    A_ELEMENTS = update_collection(
        ver0.PushSetup.A_ELEMENTS,
        ICAElement(2, "push_object_list", PushObjectList),
        ICAElement(3, "send_destination_and_method", SendDestinationAndMethod),
        ICAElement(8, "port_reference", cst.LogicalName),
        ICAElement(9, "push_client_sap", Integer),
        ICAElement(10, "push_protection_parameters", PushProtectionParameters),

    )
    port_reference: Attr
    push_client_sap: Attr
    push_protection_parameters: Attr

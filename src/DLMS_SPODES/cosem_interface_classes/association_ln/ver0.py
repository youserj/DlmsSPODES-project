from typing import Final, TypeAlias
from COSEMpdu.data import Data as Data_, Enum, Array, Integer, NullData, Structure, Boolean, Unsigned, LongUnsigned, OctetString, EnumMixin, union2alternatives
from COSEMpdu.user_information import Conformance
from COSEMpdu.axdr import ObjectIdentifierType, ImplicitTaggedType
from COSEMpdu import types_used
from ...types.type_alias import Attr
from ...types.implementations import long_unsigneds
from . import abstract
from ...types import cst
from ..cosem_interface_class import ICAuto, ICAElement, ICMElement, Classifier


class AccessMode(abstract.AccessModeProto, Enum):
    """access_mode"""
    NO_ACCESS = 0
    READ_ONLY = 1
    WRITE_ONLY = 2
    READ_AND_WRITE = 3

    def is_writable(self) -> bool:
        return int(self) >= self.WRITE_ONLY

    def is_readable(self) -> bool:
        return int(self) in (self.READ_ONLY, self.READ_AND_WRITE)


class ArrayInteger(Array[Integer]): ...


AccessSelectorsType: TypeAlias = NullData | ArrayInteger


class AccessSelectors(Data_[AccessSelectorsType]):
    alternatives = union2alternatives(AccessSelectorsType)


class AttributeAccessItem(Structure):
    """ Implemented attribute and it access . Use in Association LN """
    attribute_id: Integer
    access_mode: AccessMode
    access_selectors: AccessSelectors


AttributeAccessDescriptor = Array[AttributeAccessItem]


class MethodAccessItem(Structure):
    """method_access_item"""
    method_id: Integer
    access_mode: Boolean


MethodAccessDescriptor = Array[MethodAccessItem]


class AccessRight(Structure):
    attribute_access: AttributeAccessDescriptor
    method_access: MethodAccessDescriptor


class ObjectListElement(Structure):
    """object_list_element"""
    class_id: long_unsigneds.ClassId
    version: Unsigned
    logical_name: cst.LogicalName
    access_rights: AccessRight


class ObjectListType(Array[ObjectListElement]):
    """object_list_type"""


class ClientSAP(Enum):  # TODO: REWRITE elements here
    """ IEC 62056-46 2002 6.4.2.3 Reserved special HDLC addresses p.40. IS15952ver2 """
    NO_STATION: Final = 0
    MANAGEMENT_PROCESS: Final = 1
    PUBLIC: Final = 0x10
    READER: Final = 0x20
    CONFIGURATOR: Final = 0x30


class AssociatedPartnersType(Structure):
    """associated_partners_type"""
    client_SAP: ClientSAP
    server_SAP: long_unsigneds.ServerSAP


class ContextNameStructure(Structure):
    """context_name_structure"""
    joint_iso_ctt_element: Unsigned
    country_element: Unsigned
    country_name_element: LongUnsigned
    identified_organization_element: Unsigned
    DLMS_UA_element: Unsigned
    application_context_element: Unsigned
    context_id_element: Unsigned


class OctetStringObjectIdentifierType(ImplicitTaggedType[ObjectIdentifierType]):
    """OBJECT IDENTIFIER encoded as an octet-string TAG"""
    tag = 9


ContextNameTypeT: TypeAlias = ContextNameStructure | OctetStringObjectIdentifierType


class ContextNameType(Data_[ContextNameTypeT]):
    """context_name_type"""
    alternatives = union2alternatives(ContextNameTypeT)


class XDLMSContextType(Structure):
    """xDLMS-context-type"""
    conformance: Conformance
    max_receive_pdu_size: LongUnsigned
    max_send_pdu_size: LongUnsigned
    dlms_version_number: Unsigned
    quality_of_service: Integer
    cyphering_info: OctetString


class MechanismIdElement(EnumMixin, Unsigned):
    NONE: Final = 0
    LOW: Final = 1
    HIGH: Final = 2
    HIGH_MD5: Final = 3
    HIGH_SHA1: Final = 4
    HIGH_GMAC: Final = 5
    HIGH_SHA256: Final = 6
    HIGH_ECDSA: Final = 7


class MechanismNameStructure(Structure):
    """mechanism_name_structure"""
    joint_iso_ctt_element: Unsigned
    country_element: Unsigned
    country_name_element: LongUnsigned
    identified_organization_element: Unsigned
    DLMS_UA_element: Unsigned
    authentication_mechanism_name_element: Unsigned
    mechanism_id_element: MechanismIdElement


MechanismNameTypeT: TypeAlias = MechanismNameStructure | OctetStringObjectIdentifierType


class MechanismNameType(Data_[MechanismNameTypeT]):
    """mechanism_name_type"""
    alternatives = union2alternatives(MechanismNameTypeT)


class AssociationStatus(Enum):
    """association_status"""
    NON_ASSOCIATED: Final = 0
    ASSOCIATION_PENDING: Final = 1
    ASSOCIATED: Final = 2


class ObjectId(Structure):
    """object_id"""
    class_id: long_unsigneds.ClassId
    logical_name: cst.LogicalName


class ObjectIdList(Array[ObjectId]):
    """object_id_list"""


class ClassList(Array[long_unsigneds.ClassId]): ...


class SelectiveAccessDescriptor(types_used.SelectiveAccessDescriptor):
    selector_parameters = {
        1: NullData,        # All information
        2: ClassList,       # Access by class
        3: ObjectIdList,    # Access by object
        4: ObjectId         # Full object information
    }


class AssociationLN(ICAuto):
    """5.4.5 Association LN"""
    CLASS_ID = 15
    VERSION = 0
    A_ELEMENTS = (ICAElement(2, "object_list", ObjectListType, selective_access=SelectiveAccessDescriptor),
                  ICAElement(3, "associated_partners_id", AssociatedPartnersType),
                  ICAElement(4, "application_context_name", ContextNameType),
                  ICAElement(5, "xDLMS_context_info", XDLMSContextType),
                  ICAElement(6, "authentication_mechanism_name", MechanismNameType),
                  ICAElement(7, "LLS_secret", OctetString, classifier=Classifier.NOT_SPECIFIC),
                  ICAElement(8, "association_status", AssociationStatus, classifier=Classifier.DYNAMIC))
    M_ELEMENTS = (ICMElement(1, "reply_to_HLS_authentication", OctetString),
                  ICMElement(2, "change_HLS_secret", OctetString),
                  ICMElement(3, "add_object", ObjectListElement),
                  ICMElement(4, "remove_object", ObjectListElement))
    object_list: Attr
    associated_partners_id: Attr
    application_context_name: Attr
    xDLMS_context_info: Attr
    authentication_mechanism_name: Attr
    LLS_secret: Attr
    association_status: Attr

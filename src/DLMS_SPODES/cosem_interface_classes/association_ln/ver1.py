from dataclasses import dataclass
from COSEMpdu.data import Enum, Array, Integer, Structure, Unsigned, OctetString
from . import ver0
from ...types.implementations import long_unsigneds
from . import abstract
from ...types import cst
from ...types.type_alias import Attr
from ..cosem_interface_class import ICAElement, ICMElement, update_collection


class AccessMode(Enum, abstract.AccessModeProto):
    """access_mode"""
    NO_ACCESS = 0
    READ_ONLY = 1
    WRITE_ONLY = 2
    READ_AND_WRITE = 3
    AUTHENTICATED_READ_ONLY = 4
    AUTHENTICATED_WRITE_ONLY = 5
    AUTHENTICATED_READ_AND_WRITE = 6

    def is_writable(self) -> bool:
        return int(self) in (self.WRITE_ONLY, self.READ_AND_WRITE, self.AUTHENTICATED_WRITE_ONLY, self.AUTHENTICATED_READ_AND_WRITE)

    def is_readable(self) -> bool:
        return int(self) in (self.READ_ONLY, self.READ_AND_WRITE, self.AUTHENTICATED_READ_ONLY, self.AUTHENTICATED_READ_AND_WRITE)


@dataclass
class AttributeAccessItem(Structure):
    attribute_id: Integer
    access_mode: AccessMode
    access_selectors: ver0.AccessSelectors


AttributeAccessDescriptor = Array[AttributeAccessItem]


class AccessModeMeth(Enum):
    """access_mode"""
    NO_ACCESS = 0
    ACCESS = 1
    AUTHENTICATED_ACCESS = 2


@dataclass
class MethodAccessItem(Structure):
    """method_access_item"""
    method_id: Integer
    access_mode: AccessModeMeth


MethodAccessDescriptor = Array[MethodAccessItem]
"""method_access_descriptor"""


@dataclass
class AccessRight(Structure):
    """access_right"""
    attribute_access: AttributeAccessDescriptor
    method_access: MethodAccessDescriptor


@dataclass
class ObjectListElement(Structure):
    class_id: long_unsigneds.ClassId
    version: Unsigned
    logical_name: cst.LogicalName
    access_rights: AccessRight


class ObjectListType(Array[ObjectListElement]):
    """object_list_type"""


class AssociationLN(ver0.AssociationLN):
    """5.4.6 Association LN"""
    VERSION = 1
    A_ELEMENTS = update_collection(
        ver0.AssociationLN.A_ELEMENTS,
        ICAElement(2, "object_list", ObjectListType, selective_access=ver0.SelectiveAccessDescriptor),
        ICAElement(7, "secret", OctetString),
        ICAElement(9, "security_setup_reference", cst.LogicalName))
    M_ELEMENTS = update_collection(
        ver0.AssociationLN.M_ELEMENTS,
        ICMElement(3, "add_object", ObjectListElement),
        ICMElement(4, "remove_object", ObjectListElement))
    security_setup_reference: Attr

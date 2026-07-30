from dataclasses import dataclass
from COSEMpdu.data import Array, OctetString, Unsigned, LongUnsigned, Structure
from ...types.type_alias import Attr
from ..cosem_interface_class import ICAuto, ICAElement, ICMElement
from ...types import cst


@dataclass
class ObjectDefinition(Structure):
    """object_definition"""
    class_id: LongUnsigned
    logical_name: cst.LogicalName


RegisterAssignment = Array[ObjectDefinition]
IndexArray = Array[Unsigned]


@dataclass
class RegisterActMask(Structure):
    mask_name: OctetString
    index_list: IndexArray


MaskList = Array[RegisterActMask]


class RegisterActivation(ICAuto):
    """4.3.5 Register activation"""
    CLASS_ID = 6
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "register_assignment", RegisterAssignment),
        ICAElement(3, "mask_list", MaskList),
        ICAElement(4, "active_mask", OctetString))
    M_ELEMENTS = (
        ICMElement(1, "add_register", ObjectDefinition),
        ICMElement(2, "add_mask", RegisterActMask),
        ICMElement(3, "delete_mask", OctetString))
    register_assignment: Attr
    mask_list: Attr
    active_mask: Attr

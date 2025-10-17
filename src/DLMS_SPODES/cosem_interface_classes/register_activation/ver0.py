from ..cosem_interface_class import ICAuto, ICAElement, ICMElement
from ...types import cst
from ...types.implementations import long_unsigneds
from typing import Optional
from ...types import cdt
from ..Overview import class_id


class ObjectDefinition(cdt.Structure):
    class_id: long_unsigneds.ClassId
    logical_name: cst.LogicalName


class RegisterAssignment(cdt.Array):
    TYPE = ObjectDefinition


class IndexArray(cdt.Array):
    TYPE = cdt.Unsigned


class RegisterActMask(cdt.Structure):
    mask_name: cdt.OctetString
    index_list: IndexArray


class MaskList(cdt.Array):
    TYPE = RegisterActMask


class RegisterActivation(ICAuto):
    """4.3.5 Register activation"""
    CLASS_ID = class_id.REGISTER_ACTIVATION
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "register_assignment", RegisterAssignment),
        ICAElement(3, "mask_list", MaskList),
        ICAElement(4, "active_mask", cdt.OctetString))
    M_ELEMENTS = (
        ICMElement(1, "add_register", ObjectDefinition),
        ICMElement(2, "add_mask", RegisterActMask),
        ICMElement(3, "delete_mask", cdt.OctetString))
    register_assignment: Optional[RegisterAssignment]
    mask_list: Optional[MaskList]
    active_mask: Optional[cdt.OctetString]

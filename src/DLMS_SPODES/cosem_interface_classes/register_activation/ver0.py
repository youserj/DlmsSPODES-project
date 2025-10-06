from ..__class_init__ import *
from ...types import cst
from ...types.implementations import long_unsigneds
from ..overview import VERSION_0

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


class RegisterActivation(ic.COSEMInterfaceClasses):
    """ A “Register” object stores a process value or a status value with its associated unit. The register object knows
    the nature of the process value or of the status value. The nature of the value is described by the attribute
    “logical name” using the OBIS identification system. """
    CLASS_ID = ClassID.REGISTER_ACTIVATION
    VERSION = VERSION_0
    A_ELEMENTS = (
        ic.ICAElement(2, "register_assignment", RegisterAssignment),
        ic.ICAElement(3, "mask_list", MaskList),
        ic.ICAElement(4, "active_mask", cdt.OctetString))
    M_ELEMENTS = (
        ic.ICMElement(1, "add_register", ObjectDefinition),
        ic.ICMElement(2, "add_mask", RegisterActMask),
        ic.ICMElement(3, "delete_mask", cdt.OctetString))

    def characteristics_init(self):
        """nothing do"""

    @property
    def register_assignment(self) -> RegisterAssignment:
        return self.get_attr(2)

    @property
    def mask_list(self) -> MaskList:
        return self.get_attr(3)

    @property
    def active_mask(self) -> cdt.OctetString:
        return self.get_attr(4)

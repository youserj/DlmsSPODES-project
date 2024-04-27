from ..__class_init__ import *
from ...types import cst
from ...types.implementations import long_unsigneds


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
    CLASS_ID = classID.REGISTER_ACTIVATION
    VERSION = Version.V0
    A_ELEMENTS = (
        ic.ICAElement(
            NAME="register_assignment",
            DATA_TYPE=RegisterAssignment),
        ic.ICAElement(
            NAME="mask_list",
            DATA_TYPE=MaskList),
        ic.ICAElement(
            NAME="active_mask",
            DATA_TYPE=cdt.OctetString))
    M_ELEMENTS = (
        ic.ICMElement(
            NAME="add_register",
            DATA_TYPE=ObjectDefinition),
        ic.ICMElement(
            NAME="add_mask",
            DATA_TYPE=RegisterActMask),
        ic.ICMElement(
            NAME="delete_mask",
            DATA_TYPE=cdt.OctetString))

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

    @property
    def add_register(self) -> ObjectDefinition:
        return self.get_meth(1)

    @property
    def add_mask(self) -> RegisterActMask:
        return self.get_meth(2)

    @property
    def delete_mask(self) -> cdt.OctetString:
        return self.get_meth(3)

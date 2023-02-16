from __future__ import annotations
from . import ver0
from ...types import choices
from ... import ITE_exceptions as exc
from ..__class_init__ import *


class AccessMode(ver0.AccessMode,
                 elements={b'\x04': en.AUTHENTICATION_READ_ONLY,
                           b'\x05': en.AUTHENTICATION_WRITE_ONLY,
                           b'\x06': en.AUTHENTICATION_READ_AND_WRITE}):
    """Version 0 extension"""


class AccessModeMeth(cdt.Enum):
    """ Enum of access mode for methods """
    ELEMENTS = {b'\x00': en.NO_ACCESS,
                b'\x01': en.ACCESS,
                b'\x02': en.AUTHENTICATED_ACCESS}


# TODO: make as subclass of ver0
class AttributeAccessItem(cdt.Structure):
    """ Implemented attribute and it access . Use in Association LN """
    values: tuple[cdt.Integer, AccessMode, cdt.NullData | cdt.Array]
    ELEMENTS = (cdt.StructElement(cdt.se.ATTRIBUTE_ID, cdt.Integer),
                cdt.StructElement(cdt.se.ACCESS_MODE, AccessMode),
                cdt.StructElement(cdt.se.ACCESS_SELECTORS, choices.access_selectors))

    @property
    def attribute_id(self) -> cdt.Integer:
        return self.values[0]

    @property
    def access_mode(self) -> AccessMode:
        return self.values[1]

    @property
    def access_selectors(self) -> cdt.NullData | cdt.Array:
        return self.values[2]


class AttributeAccessDescriptor(cdt.Array):
    """ Array of attribute_access_item """
    TYPE = AttributeAccessItem


# TODO: make as subclass of ver0
class MethodAccessItem(cdt.Structure):
    """ Implemented method and it access . Use in Association LN """
    values: tuple[cdt.Integer, AccessModeMeth]
    ELEMENTS = (cdt.StructElement(cdt.se.METHOD_ID, cdt.Integer),
                cdt.StructElement(cdt.se.ACCESS_MODE, AccessModeMeth))

    @property
    def method_id(self) -> cdt.Integer:
        return self.values[0]

    @property
    def access_mode(self) -> AccessModeMeth:
        return self.values[1]


class MethodAccessDescriptor(cdt.Array):
    """ Contain all implemented methods """
    TYPE = MethodAccessItem


class AccessRight(cdt.Structure):
    """ TODO: """
    values: tuple[AttributeAccessDescriptor, MethodAccessDescriptor]
    attribute_access: AttributeAccessDescriptor
    method_access: MethodAccessDescriptor
    ELEMENTS = (cdt.StructElement(cdt.se.ATTRIBUTE_ACCESS, AttributeAccessDescriptor),
                cdt.StructElement(cdt.se.METHOD_ACCESS, MethodAccessDescriptor))

    @property
    def attribute_access(self) -> AttributeAccessDescriptor:
        return self.values[0]

    @property
    def method_access(self) -> MethodAccessDescriptor:
        return self.values[1]


class ObjectListElement(ver0.ObjectListElement):
    values: tuple[cdt.LongUnsigned, cdt.Unsigned, cst.LogicalName, AccessRight]
    ELEMENTS = (*ver0.ObjectListElement.ELEMENTS[:3],
                cdt.StructElement(cdt.se.ACCESS_RIGHTS, AccessRight))

    @property
    def access_rights(self) -> AccessRight:
        return self.values[3]


class ObjectListType(ver0.ObjectListType):
    TYPE = ObjectListElement

    def is_writable(self, ln: cst.LogicalName, indexes: set[int]) -> bool:
        """ index - DLMS object attribute index.
         True: AccessRight is WriteOnly or ReadAndWrite """
        el: ObjectListElement = next(filter(lambda it: it.logical_name == ln, self), None)
        if el is None:
            raise exc.NoObject(F"not find {ln} in object_list")
        item: AttributeAccessItem
        for index in indexes:
            for item in el.access_rights.attribute_access:
                if int(item.attribute_id) == index:
                    if int(item.access_mode) not in (2, 3, 5, 6):
                        return False
                    else:
                        break
                else:
                    continue
            else:
                raise ValueError(F"not find in {ln} attribute index: {index}")
        return True


class ContextNameType(cdt.AXDR, ver0.ApplicationContextName):
    """ In the COSEM environment, it is intended that an application context pre-exists and is referenced by its name during the establishment of an
    application association. This attribute contains the name of the application context for that association."""
    default = b'\x09\x07\x60\x85\x74\x05\x08\x01\x01'


class MechanismNameType(cdt.AXDR, ver0.AuthenticationMechanismName):
    """ In the COSEM environment, it is intended that an application context pre-exists and is referenced by its name during the establishment of an
    application association. This attribute contains the name of the application context for that association."""
    default = b'\x09\x07\x60\x85\x74\x05\x08\x02\x00'


class AssociationLN(ver0.AssociationLN):
    """ COSEM logical devices able to establish application associations within a COSEM context using logical name referencing, model the associations
    through instances of the “Association LN” class. A COSEM logical device has one instance of this IC for each association
    the device is able to support"""
    VERSION = cdt.Unsigned(1)
    A_ELEMENTS = (ic.ICAElement(an.OBJECT_LIST, ObjectListType, selective_access=ver0.SelectiveAccessDescriptor),
                  ver0.AssociationLN.get_attr_element(3),
                  ic.ICAElement(an.APPLICATION_CONTEXT_NAME, ContextNameType),
                  ver0.AssociationLN.get_attr_element(5),
                  ic.ICAElement(an.AUTHENTICATION_MECHANISM_NAME, MechanismNameType),
                  ver0.AssociationLN.get_attr_element(7),
                  ver0.AssociationLN.get_attr_element(8),
                  ic.ICAElement(an.SECURITY_SETUP_REFERENCE, cst.LogicalName))
    M_ELEMENTS = (ver0.AssociationLN.get_meth_element(1),
                  ver0.AssociationLN.get_meth_element(2),
                  ic.ICMElement(mn.ADD_OBJECT, ObjectListElement),
                  ic.ICMElement(mn.REMOVE_OBJECT, ObjectListElement))
    object_list: ObjectListType
    application_context_name: ContextNameType
    authentication_mechanism_name: MechanismNameType
    security_setup_reference: cst.LogicalName
    add_object: ObjectListElement
    remove_object: ObjectListElement

    def characteristics_init(self):
        super(AssociationLN, self).characteristics_init()
        # References a "Security setup" object by its logical name. The referenced object manages security for a given "Association LN" object
        # instance.
        self.set_attr(9, None)

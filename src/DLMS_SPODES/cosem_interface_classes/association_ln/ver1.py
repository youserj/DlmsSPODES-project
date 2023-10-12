from . import ver0
from ...types import choices
from ... import exceptions as exc
from ..__class_init__ import *


class AccessMode(cdt.Enum, elements=tuple(range(7))):
    """Version 0 extension"""
    def is_writable(self) -> bool:
        return True if int(self) in (2, 3, 5, 6) else False

    def is_readable(self) -> bool:
        return True if int(self) in (1, 3, 4, 6) else False


class AccessModeMeth(cdt.Enum, elements=(0, 1, 2)):
    """ Enum of access mode for methods """


# TODO: make as subclass of ver0
class AttributeAccessItem(cdt.Structure):
    """ Implemented attribute and it access . Use in Association LN """
    attribute_id: cdt.Integer
    access_mode: AccessMode
    access_selectors: choices.access_selectors


class AttributeAccessDescriptor(cdt.Array):
    """ Array of attribute_access_item """
    TYPE = AttributeAccessItem


# TODO: make as subclass of ver0
class MethodAccessItem(cdt.Structure):
    """ Implemented method and it access . Use in Association LN """
    method_id: cdt.Integer
    access_mode: AccessModeMeth


class MethodAccessDescriptor(cdt.Array):
    """ Contain all implemented methods """
    TYPE = MethodAccessItem


class AccessRight(cdt.Structure):
    """ TODO: """
    attribute_access: AttributeAccessDescriptor
    method_access: MethodAccessDescriptor


class ObjectListElement(cdt.Structure):
    class_id: ver0.long_unsigneds.ClassId
    version: cdt.Unsigned
    logical_name: cst.LogicalName
    access_rights: AccessRight


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
    DEFAULT = b'\x09\x07\x60\x85\x74\x05\x08\x01\x01'


class MechanismNameType(cdt.AXDR, ver0.AuthenticationMechanismName):
    """ In the COSEM environment, it is intended that an application context pre-exists and is referenced by its name during the establishment of an
    application association. This attribute contains the name of the application context for that association."""
    DEFAULT = b'\x09\x07\x60\x85\x74\x05\x08\x02\x00'


class AssociationLN(ver0.AssociationLN):
    """ COSEM logical devices able to establish application associations within a COSEM context using logical name referencing, model the associations
    through instances of the “Association LN” class. A COSEM logical device has one instance of this IC for each association
    the device is able to support"""
    VERSION = Version.V1
    A_ELEMENTS = (ic.ICAElement(an.OBJECT_LIST, ObjectListType, selective_access=ver0.SelectiveAccessDescriptor),
                  ver0.AssociationLN.get_attr_element(3),
                  ic.ICAElement(an.APPLICATION_CONTEXT_NAME, ContextNameType),
                  ver0.AssociationLN.get_attr_element(5),
                  ic.ICAElement(an.AUTHENTICATION_MECHANISM_NAME, MechanismNameType),
                  ver0.AssociationLN.get_attr_element(7),  # TODO: make new class Secret(LLC_Secret)
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

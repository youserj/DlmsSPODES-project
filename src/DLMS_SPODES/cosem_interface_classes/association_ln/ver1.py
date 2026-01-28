from . import ver0
from . import authentication_mechanism_name
from . import abstract
from ...types import choices, cdt, cst
from ...types.type_alias import Attr
from ..cosem_interface_class import ICAElement, ICMElement


class AccessMode(abstract.AccessMode, elements=tuple(range(7))):
    """Version 0 extension"""
    def is_writable(self) -> bool:
        return True if int(self) in (2, 3, 5, 6) else False

    def is_readable(self) -> bool:
        return True if int(self) in (1, 3, 4, 6) else False


class AccessModeMeth(cdt.Enum, elements=(0, 1, 2)):
    """ Enum of access mode for methods """


class AttributeAccessItem(abstract.AttributeAccessItem):
    access_mode: AccessMode


class AttributeAccessDescriptor(abstract.AttributeAccessDescriptor):
    """ Array of attribute_access_item """
    TYPE = AttributeAccessItem

    def set_read_access(self, attribute_id: cdt.Integer):
        it: AttributeAccessItem
        for it in self:
            if it.attribute_id == attribute_id:
                it.access_mode.set(1)
                break
        else:
            self.append(AttributeAccessItem((attribute_id, AccessMode.parse("1"), None)))


# TODO: make as subclass of ver0
class MethodAccessItem(abstract.MethodAccessItem):
    """ Implemented method and it access . Use in Association LN """
    access_mode: AccessModeMeth


class MethodAccessDescriptor(abstract.MethodAccessDescriptor):
    """ Contain all implemented methods """
    TYPE = MethodAccessItem


class AccessRight(abstract.AccessRight): 
    attribute_access: AttributeAccessDescriptor
    method_access: MethodAccessDescriptor


class ObjectListElement(abstract.ObjectListElement):
    access_rights: AccessRight


class ObjectListType(ver0.ObjectListType):
    TYPE = ObjectListElement

    # def is_writable(self, obisln: cst.LogicalName, indexes: set[int]) -> bool:
    #     """ index - DLMS object attribute index.
    #      True: AccessRight is WriteOnly or ReadAndWrite """
    #     el: ObjectListElement = next(filter(lambda it: it.logical_name == ln, self), None)
    #     if el is None:
    #         raise exc.NoObject(F"not find {ln} in object_list")
    #     item: AttributeAccessItem
    #     for index in indexes:
    #         for item in el.access_rights.attribute_access:
    #             if int(item.attribute_id) == index:
    #                 if int(item.access_mode) not in (2, 3, 5, 6):
    #                     return False
    #                 else:
    #                     break
    #             else:
    #                 continue
    #         else:
    #             raise ValueError(F"not find in {ln} attribute index: {index}")
    #     return True


class ContextNameType(cdt.AXDR, ver0.ApplicationContextName):
    """ In the COSEM environment, it is intended that an application context pre-exists and is referenced by its name during the establishment of an
    application association. This attribute contains the name of the application context for that association."""
    DEFAULT = b'\x09\x07\x60\x85\x74\x05\x08\x01\x01'


class MechanismNameType(cdt.AXDR, authentication_mechanism_name.AuthenticationMechanismName):
    """ In the COSEM environment, it is intended that an application context pre-exists and is referenced by its name during the establishment of an
    application association. This attribute contains the name of the application context for that association."""
    DEFAULT = b'\x09\x07\x60\x85\x74\x05\x08\x02\x00'


class AssociationLN(ver0.AssociationLN):
    """5.4.6 Association LN"""
    VERSION = 1
    A_ELEMENTS = (ICAElement(2, "object_list", ObjectListType, selective_access=ver0.SelectiveAccessDescriptor),
                  ver0.AssociationLN.getAElement(3).unwrap(),  # associated_partners_id
                  ICAElement(4, "application_context_name", ContextNameType),
                  ver0.AssociationLN.getAElement(5).unwrap(),  # xDLMS_context_info
                  ICAElement(6, "authentication_mechanism_name", MechanismNameType),
                  ICAElement(7, "secret", ver0.LLCSecret),  # TODO: make new class Secret(LLC_Secret)
                  ver0.AssociationLN.getAElement(8).unwrap(),  # association_status
                  ICAElement(9, "security_setup_reference", cst.LogicalName))
    M_ELEMENTS = (ver0.AssociationLN.getMElement(1).unwrap(),
                  ver0.AssociationLN.getMElement(2).unwrap(),
                  ICMElement(3, "add_object", ObjectListElement),
                  ICMElement(4, "remove_object", ObjectListElement))
    security_setup_reference: Attr
    add_object: ObjectListElement
    remove_object: ObjectListElement

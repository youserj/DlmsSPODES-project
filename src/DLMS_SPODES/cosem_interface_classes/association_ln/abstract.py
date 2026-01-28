from typing import Protocol, runtime_checkable
from ...types import cdt, cst, ut, choices
from ... import pdu_enums as pdu
from ...types.type_alias import Obis
from ...types.implementations import long_unsigneds
from ... import exceptions as exc


class AccessMode(cdt.Enum, Protocol):
    def is_writable(self) -> bool: ...
    def is_readable(self) -> bool: ...


class AttributeAccessItem(cdt.Structure, Protocol):
    """ Implemented attribute and it access . Use in Association LN """
    attribute_id: cdt.Integer
    access_mode: AccessMode
    access_selectors: choices.access_selectors


class AttributeAccessDescriptor(cdt.Array, Protocol):
    """ Array of attribute_access_item """
    TYPE = AttributeAccessItem
    """override this"""

    def set_read_access(self, attribute_id: cdt.Integer):
        """by attribute_id"""


class MethodAccessItem(cdt.Structure):
    """ Implemented method and it access . Use in Association LN """
    method_id: cdt.Integer
    access_mode: cdt.getCDT


class MethodAccessDescriptor(cdt.Array):
    """ Contain all implemented methods """
    TYPE = MethodAccessItem


class AccessRight(cdt.Structure):
    """ TODO: """
    attribute_access: AttributeAccessDescriptor
    method_access: MethodAccessDescriptor


class ObjectListElement(cdt.Structure):
    class_id: long_unsigneds.ClassId
    version: cdt.Unsigned
    logical_name: cst.LogicalName
    access_rights: AccessRight


@runtime_checkable
class ObjectListType(cdt._Array, Protocol):
    """ Array of object_list_element. The range for the client_SAP is 0…0x7F. The range for the server_SAP is 0x000…0x3FFF."""
    TYPE = ObjectListElement

    def is_readable(self, obis: Obis, i: int, security_policy: pdu.SecurityPolicy = 0) -> bool:
        """ index - DLMS object attribute index.
         True: AccessRight is WriteOnly or ReadAndWrite """

    def is_writable(self, obis: Obis, i: int, security_policy: pdu.SecurityPolicy = 0) -> bool:
        """ index - DLMS object attribute index.
         True: AccessRight is WriteOnly or ReadAndWrite """

    def get_attr_access(self, obis: Obis, i: int) -> pdu.AttributeAccess: ...

    def get_meth_access(self, obis: Obis, i: int) -> pdu.MethodAccess: ...

    def get_access_right(self, obis: Obis) -> AccessRight:
        """return object_list_element of object_list AssociationLN"""
        el: ObjectListElement = next(filter(lambda it: it.logical_name.contents == obis, self), None)
        if el is None:
            raise exc.NoObject(F"not find {obis=} in object_list")
        else:
            return el.access_rights

    def get_attr_access(self, obis: Obis, i: int) -> pdu.AttributeAccess:
        """ index - DLMS object attribute index """
        return pdu.AttributeAccess(int(self.get_access_mode))

    def get_access_mode(self, obis: Obis, i: int) -> AccessMode:
        """ index - DLMS object attribute index """
        for item in self.get_access_right(obis).attribute_access:  # item: AttributeAccessItem
            item: AttributeAccessItem
            if int(item.attribute_id) == i:
                return item.access_mode
            else:
                continue
        else:
            raise ValueError(F"access for {obis=}: {i} is absense")

    def get_meth_access(self, obis: Obis, i: int) -> pdu.MethodAccess:
        """ index - DLMS object method index """
        for item in self.get_access_right(obis).method_access:  # item: MethodAccessItem
            item: MethodAccessItem
            if int(item.method_id) == i:
                return pdu.MethodAccess(int(item.access_mode))
            else:
                continue
        else:
            raise exc.ITEApplication(F"not find method access rules in object_list for {obis=}:{i}")  # todo: make custom error


def is_attr_writable(
        mode: AccessMode,
        security_policy: pdu.SecurityPolicy = pdu.SecurityPolicyVer0.NOTHING) -> bool:
    match int(mode):
        case pdu.AttributeAccess.NO_ACCESS | pdu.AttributeAccess.READ_ONLY | pdu.AttributeAccess.AUTHENTICATED_READ_ONLY:
            return False
        case pdu.AttributeAccess.WRITE_ONLY | pdu.AttributeAccess.READ_AND_WRITE:
            return True
        case pdu.AttributeAccess.AUTHENTICATED_WRITE_ONLY | pdu.AttributeAccess.AUTHENTICATED_READ_AND_WRITE:
            if isinstance(security_policy, pdu.SecurityPolicyVer0):
                match security_policy:
                    case pdu.SecurityPolicyVer0.AUTHENTICATED | pdu.SecurityPolicyVer0.AUTHENTICATED_AND_ENCRYPTED:
                        return True
                    case _:
                        return False
            elif isinstance(security_policy, pdu.SecurityPolicyVer1):
                if bool(security_policy & (pdu.SecurityPolicyVer1.AUTHENTICATED_REQUEST | pdu.SecurityPolicyVer1.AUTHENTICATED_RESPONSE)):
                    return True
                else:
                    return False
            else:
                raise TypeError(F"unknown {security_policy.__class__}: {security_policy}")
        case err:
            raise exc.ITEApplication(F"unsupport access: {err}")

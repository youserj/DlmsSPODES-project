from typing import overload, Union
from COSEMpdu.data import Boolean
from .ver0 import (
    AttributeAccessItem as AttributeAccessItemVer0,
    ObjectListElement as ObjectListElementVer0,
    ObjectListType as ObjectListTypeVer0,
    AccessRight as AccessRight0,
    AccessMode as AccessMode0,
    MechanismIdElement,
    MechanismNameType,
    ClientSAP,
)
from .ver1 import (
    AttributeAccessItem as AttributeAccessItemVer1,
    ObjectListElement as ObjectListElementVer1,
    ObjectListType as ObjectListTypeVer1,
    AccessRight as AccessRight1,
    AccessMode as AccessMode1,
    AccessModeMeth as AccessModeMeth1
)
from ...types.type_alias import Obis
from ... import exceptions as exc
from ... import pdu_enums as pdu


AttributeAccessItem = Union[AttributeAccessItemVer0, AttributeAccessItemVer1]
ObjectListElement = Union[ObjectListElementVer0, ObjectListElementVer1]
ObjectListType = Union[ObjectListTypeVer0, ObjectListTypeVer1]
AccessRight = Union[AccessRight0, AccessRight1]
AccessMode = Union[AccessMode0, AccessMode1]
AccessModeMeth = Union[Boolean, AccessModeMeth1]


@overload
def get_access_right(instance: ObjectListTypeVer0, obis: Obis) -> AccessRight0: ...


@overload
def get_access_right(instance: ObjectListTypeVer1, obis: Obis) -> AccessRight1: ...


def get_access_right(instance: ObjectListType, obis: Obis) -> AccessRight:
    """return object_list_element of object_list AssociationLN"""
    for ole in instance:
        if ole.logical_name.normalize() == obis:
            break
    else:
        raise exc.NoObject(F"not find {obis=} in object_list")
    return ole.access_rights


@overload
def get_access_mode(instance: ObjectListTypeVer0, obis: Obis, i: int) -> AccessMode0: ...


@overload
def get_access_mode(instance: ObjectListTypeVer1, obis: Obis, i: int) -> AccessMode1: ...


def get_access_mode(instance: ObjectListType, obis: Obis, i: int) -> AccessMode:
    """ index - DLMS object attribute index """
    for item in get_access_right(instance, obis).attribute_access:
        if item.attribute_id.normalize() == i:
            return item.access_mode
    else:
        raise ValueError(F"access for {obis=}: {i} is absense")


def is_readable(instance: ObjectListType,
                obis: Obis,
                i: int,
                security_policy: pdu.SecurityPolicy = pdu.SecurityPolicyVer0.NOTHING
                ) -> bool:
    match get_access_mode(instance, obis, i).normalize():
        case AccessMode0.NO_ACCESS | AccessMode0.WRITE_ONLY | AccessMode1.AUTHENTICATED_WRITE_ONLY:
            return False
        case AccessMode0.READ_ONLY | AccessMode0.READ_AND_WRITE:
            return True
        case AccessMode1.AUTHENTICATED_READ_ONLY | AccessMode1.AUTHENTICATED_READ_AND_WRITE:
            if isinstance(security_policy, pdu.SecurityPolicyVer0):
                match security_policy:
                    case pdu.SecurityPolicyVer0.AUTHENTICATED | pdu.SecurityPolicyVer0.AUTHENTICATED_AND_ENCRYPTED:
                        return True
                    case _:
                        return False
            return bool(security_policy & (pdu.SecurityPolicyVer1.AUTHENTICATED_REQUEST | pdu.SecurityPolicyVer1.AUTHENTICATED_RESPONSE))
        case err:
            raise exc.ITEApplication(F"unsupport access: {err}")


def is_attr_writable(
        mode: AccessMode,
        security_policy: pdu.SecurityPolicy = pdu.SecurityPolicyVer0.NOTHING) -> bool:
    match int(mode):
        case AccessMode0.NO_ACCESS | AccessMode0.READ_ONLY | AccessMode1.AUTHENTICATED_READ_ONLY:
            return False
        case AccessMode0.WRITE_ONLY | AccessMode0.READ_AND_WRITE:
            return True
        case AccessMode1.AUTHENTICATED_WRITE_ONLY | AccessMode1.AUTHENTICATED_READ_AND_WRITE:
            if isinstance(security_policy, pdu.SecurityPolicyVer0):
                match security_policy:
                    case pdu.SecurityPolicyVer0.AUTHENTICATED | pdu.SecurityPolicyVer0.AUTHENTICATED_AND_ENCRYPTED:
                        return True
                    case _:
                        return False
            return bool(security_policy & (pdu.SecurityPolicyVer1.AUTHENTICATED_REQUEST | pdu.SecurityPolicyVer1.AUTHENTICATED_RESPONSE))
        case err:
            raise exc.ITEApplication(F"unsupport access: {err}")


def is_writable(instance: ObjectListType,
                obis: Obis,
                i: int,
                security_policy: pdu.SecurityPolicy = pdu.SecurityPolicyVer0.NOTHING
                ) -> bool:
    return is_attr_writable(
        mode=get_access_mode(instance, obis, i),
        security_policy=security_policy)


def get_meth_access(instance: ObjectListType, obis: Obis, i: int) -> AccessModeMeth:
    """ index - DLMS object method index """
    for item in get_access_right(instance, obis).method_access:  # item: MethodAccessItem
        if item.method_id.normalize() == i:
            return item.access_mode
    else:
        raise exc.ITEApplication(f"not find method access rules in object_list for {obis=}:{i}")  # todo: make custom error


def is_accessible(instance: ObjectListType, obis: Obis, i: int, m_id: int = MechanismIdElement.NONE) -> bool:
    """for ver 0 and 1 only"""
    match get_meth_access(instance, obis, i).normalize():
        case AccessModeMeth1.NO_ACCESS:
            return False
        case AccessModeMeth1.ACCESS:
            return True
        case AccessModeMeth1.AUTHENTICATED_ACCESS:
            return m_id != MechanismIdElement.NONE
        case err:
            raise exc.ITEApplication(F"unsupport access: {err}")


__all__ = [
    "AttributeAccessItem",
    "ObjectListType",
    "MechanismIdElement",
    "ClientSAP",
    "MechanismNameType"
]

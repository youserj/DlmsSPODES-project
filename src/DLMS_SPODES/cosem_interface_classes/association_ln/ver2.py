from . import ver1
from ...types.implementations import arrays, structs
from ...types.type_alias import Attr
from ..cosem_interface_class import ICAElement, ICMElement, update_collection


class AssociationLN(ver1.AssociationLN):
    """5.4.7 Association LN"""
    VERSION = 2
    A_ELEMENTS = update_collection(
        ver1.AssociationLN.A_ELEMENTS,
        ICAElement(10, "user_list", arrays.UserList),
        ICAElement(11, "current_user", structs.UserListEntry),
    )
    M_ELEMENTS = update_collection(
        ver1.AssociationLN.M_ELEMENTS,
        ICMElement(5, "add_user", structs.UserListEntry),
        ICMElement(6, "remove_user", structs.UserListEntry),
    )
    user_list: Attr
    current_user: Attr

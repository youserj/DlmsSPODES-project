from ..__class_init__ import *
from . import ver0, ver1
from ...types.implementations import structs, arrays
from ..overview import VERSION_2


class AssociationLN(ver1.AssociationLN):
    """5.4.7 Association LN"""
    VERSION = VERSION_2
    A_ELEMENTS = (
        ver1.AssociationLN.getAElement(2).unwrap(),  # <object_list>
        ver0.AssociationLN.getAElement(3).unwrap(),  # associated_partners_id
        ver0.AssociationLN.getAElement(4).unwrap(),  # application_context_name
        ver0.AssociationLN.getAElement(5).unwrap(),  # xDLMS_context_info
        ver0.AssociationLN.getAElement(6).unwrap(),  # authentication_mechanism_name
        ver1.AssociationLN.getAElement(7).unwrap(),  # secret
        ver0.AssociationLN.getAElement(8).unwrap(),  # association_status
        ver1.AssociationLN.getAElement(9).unwrap(),  # security_setup_reference
        ic.ICAElement(10, "user_list", arrays.UserList),
        ic.ICAElement(11, "current_user", structs.UserListEntry),
    )
    M_ELEMENTS = (
        ver0.AssociationLN.get_meth_element(1),
        ver0.AssociationLN.get_meth_element(2),
        ver1.AssociationLN.get_meth_element(3),  # add_object
        ver1.AssociationLN.get_meth_element(4),  # remove_object
        ic.ICMElement(5, "add_user", structs.UserListEntry),
        ic.ICMElement(6, "remove_user", structs.UserListEntry),
    )
    user_list: arrays.UserList
    current_user: structs.UserListEntry

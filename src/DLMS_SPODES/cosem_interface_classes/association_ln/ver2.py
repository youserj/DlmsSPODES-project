from ..__class_init__ import *
from . import ver0, ver1
from ...types.implementations import structs, arrays
from ..overview import VERSION_2


class AssociationLN(ver1.AssociationLN):
    """5.4.7 Association LN"""
    VERSION = VERSION_2
    A_ELEMENTS = (
        ver1.AssociationLN.get_attr_element(2),  # <object_list>
        ver0.AssociationLN.get_attr_element(3),  # associated_partners_id
        ver0.AssociationLN.get_attr_element(4),  # application_context_name
        ver0.AssociationLN.get_attr_element(5),  # xDLMS_context_info
        ver0.AssociationLN.get_attr_element(6),  # authentication_mechanism_name
        ver1.AssociationLN.get_attr_element(7),  # secret
        ver0.AssociationLN.get_attr_element(8),  # association_status
        ver1.AssociationLN.get_attr_element(9),  # security_setup_reference
        ic.ICAElement("user_list", arrays.UserList),
        ic.ICAElement("current_user", structs.UserListEntry),
    )
    M_ELEMENTS = (
        ver0.AssociationLN.get_meth_element(1),
        ver0.AssociationLN.get_meth_element(2),
        ver1.AssociationLN.get_meth_element(3),  # add_object
        ver1.AssociationLN.get_meth_element(4),  # remove_object
        ic.ICMElement("add_user", structs.UserListEntry),
        ic.ICMElement("remove_user", structs.UserListEntry),
    )
    user_list: arrays.UserList
    current_user: structs.UserListEntry

    def characteristics_init(self):
        super(AssociationLN, self).characteristics_init()
        # TODO: more 2 attribute
        # TODO: more 2 methods

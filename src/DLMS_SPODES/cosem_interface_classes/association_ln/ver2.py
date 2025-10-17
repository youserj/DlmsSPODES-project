from . import ver0, ver1
from ...types.implementations import arrays, structs
from ...types.type_alias import Attr
from ..cosem_interface_class import ICAElement, ICMElement

class AssociationLN(ver1.AssociationLN):
    """5.4.7 Association LN"""
    VERSION = 2
    A_ELEMENTS = (
        ver1.AssociationLN.getAElement(2).unwrap(),  # <object_list>
        ver0.AssociationLN.getAElement(3).unwrap(),  # associated_partners_id
        ver0.AssociationLN.getAElement(4).unwrap(),  # application_context_name
        ver0.AssociationLN.getAElement(5).unwrap(),  # xDLMS_context_info
        ver0.AssociationLN.getAElement(6).unwrap(),  # authentication_mechanism_name
        ver1.AssociationLN.getAElement(7).unwrap(),  # secret
        ver0.AssociationLN.getAElement(8).unwrap(),  # association_status
        ver1.AssociationLN.getAElement(9).unwrap(),  # security_setup_reference
        ICAElement(10, "user_list", arrays.UserList),
        ICAElement(11, "current_user", structs.UserListEntry),
    )
    M_ELEMENTS = (
        ver0.AssociationLN.getMElement(1).unwrap(),
        ver0.AssociationLN.getMElement(2).unwrap(),
        ver1.AssociationLN.getMElement(3).unwrap(),  # add_object
        ver1.AssociationLN.getMElement(4).unwrap(),  # remove_object
        ICMElement(5, "add_user", structs.UserListEntry),
        ICMElement(6, "remove_user", structs.UserListEntry),
    )
    user_list: Attr
    current_user: Attr

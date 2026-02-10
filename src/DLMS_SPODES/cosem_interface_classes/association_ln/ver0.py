from typing import Iterator, Optional
from enum import IntFlag, auto
from ..parameters import Parameter
from ... import exceptions as exc
from ...types.implementations import arrays, enums, bitstrings, long_unsigneds, structs
from ...types.type_alias import Attr
from ... import pdu_enums as pdu
from . import mechanism_id, authentication_mechanism_name, client_sap
from . import method
from . import abstract
from ...types import choices, cdt, cst, ut
from ..cosem_interface_class import ICAuto, ICAElement, ICMElement, Classifier
from ..Overview import class_id
from ...types.type_alias import Obis


class AccessMode(abstract.AccessMode, elements=(0, 1, 2, 3)):
    """ TODO: """
    def is_writable(self) -> bool:
        return True if int(self) >= 2 else False

    def is_readable(self) -> bool:
        return True if int(self) in (1, 3) else False


class AttributeAccessItem(abstract.AttributeAccessItem): 
    """ Implemented attribute and it access . Use in Association LN """
    access_mode: AccessMode


class AttributeAccessDescriptor(abstract.AttributeAccessDescriptor):
    """ Array of attribute_access_item """
    TYPE = AttributeAccessItem

    def set_read_access(self, attribute_id: cdt.Integer) -> None:
        it: AttributeAccessItem
        for it in self:
            if it.attribute_id == attribute_id:
                it.access_mode.set(1)
                break
        else:
            self.append(AttributeAccessItem((attribute_id, AccessMode.parse("1"), None)))


class MethodAccessItem(abstract.MethodAccessItem):
    """ Implemented method and it access . Use in Association LN """
    access_mode: cdt.Boolean


class MethodAccessDescriptor(abstract.MethodAccessDescriptor):
    """ Contain all implemented methods """
    TYPE = MethodAccessItem


class AccessRight(abstract.AccessRight): 
    attribute_access: AttributeAccessDescriptor
    method_access: MethodAccessDescriptor


class ObjectListElement(abstract.ObjectListElement):
    """ Visible COSEM objects with their class_id, version, logical name and the access rights to their attributes and methods within the given application association"""
    access_rights: AccessRight


class ObjectListType(arrays.SelectionAccess, abstract.ObjectListType):
    """ Array of object_list_element. The range for the client_SAP is 0…0x7F. The range for the server_SAP is 0x000…0x3FFF."""
    TYPE = ObjectListElement
    __getitem__: ObjectListElement

    def is_readable(self,
                    obis: Obis,
                    i: int,
                    security_policy: pdu.SecurityPolicy = pdu.SecurityPolicyVer0.NOTHING
                    ) -> bool:
        match self.get_attr_access(obis, i):
            case pdu.AttributeAccess.NO_ACCESS | pdu.AttributeAccess.WRITE_ONLY | pdu.AttributeAccess.AUTHENTICATED_WRITE_ONLY:
                return False
            case pdu.AttributeAccess.READ_ONLY | pdu.AttributeAccess.READ_AND_WRITE:
                return True
            case pdu.AttributeAccess.AUTHENTICATED_READ_ONLY | pdu.AttributeAccess.AUTHENTICATED_READ_AND_WRITE:
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

    def is_writable(self,
                    obis: Obis,
                    i: int,
                    security_policy: pdu.SecurityPolicy = pdu.SecurityPolicyVer0.NOTHING
                    ) -> bool:
        return abstract.is_attr_writable(
            mode=self.get_access_mode(obis, i),
            security_policy=security_policy)

    def is_accessible(self, obis: Obis, i: int, m_id: mechanism_id.MechanismIdElement = None) -> bool:
        """for ver 0 and 1 only"""
        match self.get_meth_access(obis, i):
            case pdu.MethodAccess.NO_ACCESS:
                return False
            case pdu.MethodAccess.ACCESS:
                return True
            case pdu.MethodAccess.AUTHENTICATED_ACCESS:
                if not m_id:
                    m_id = self.authentication_mechanism_name.mechanism_id_element
                if m_id > mechanism_id.NONE:
                    return True
                else:
                    return False
            case err:
                raise exc.ITEApplication(F"unsupport access: {err}")


class AssociatedPartnersType(cdt.Structure):
    """associated_partners_type"""
    DEFAULT = (0x10, 1)
    client_SAP: client_sap.ClientSAP
    server_SAP: long_unsigneds.ServerSAP


class ApplicationContextName(cdt.Structure):
    """ In the COSEM environment, it is intended that an application context pre-exists and is referenced by its name during the establishment of an
    application association. This attribute contains the name of the application context for that association."""
    DEFAULT = (2, 16, 116, 5, 8, 1, 1)
    joint_iso_ctt_element: cdt.Unsigned
    country_element: cdt.Unsigned
    country_name_element: cdt.LongUnsigned
    identified_organization_element: cdt.Unsigned
    DLMS_UA_element: cdt.Unsigned
    application_context_element: cdt.Unsigned
    context_id_element: cdt.Unsigned


class XDLMSContextType(cdt.Structure):
    """ Contains all the necessary information on the xDLMS context for the given association. """
    DEFAULT = (None, 1024, 1024, 6, 0, b'\x09\x07\x60\x85\x74\x05\x08\x02\x00')
    conformance: bitstrings.Conformance
    max_receive_pdu_size: cdt.LongUnsigned
    max_send_pdu_size: cdt.LongUnsigned
    dlms_version_number: cdt.Unsigned
    quality_of_service: cdt.Integer
    cyphering_info: cdt.OctetString


class AssociationStatus(cdt.Enum, elements=(0, 1, 2)):
    """ Enum of access mode for methods """


class ClassList(cdt.Array):
    """ Access by class. In this case, only those object_list_elements of the object_list shall be included in the response, which have a class_id
    equal to one of the class_id-s of the class-list. No access_right information is included """
    TYPE = long_unsigneds.ClassId


class ObjectId(cdt.Structure):
    DEFAULT = b'\x02\x02\x12\x00\x08\x09\x06\x00\x00\x01\x00\x00\xff'
    class_id: long_unsigneds.ClassId
    logical_name: cst.LogicalName


class ObjectIdList(cdt.Array):
    """ Access by object. The full information record of object instances on the object_Id_list shall be returned. """
    TYPE = ObjectId


class Representation(IntFlag):
    HEX = 0
    ASCII = auto()
    HIDDEN = auto()
    ASCII_HIDDEN = ASCII | HIDDEN


class LLCSecret(cdt.OctetString):
    """ representation for secret """
    __representation: Representation = Representation.HEX
    # used for set class property from instance

    def __init__(self, value: bytes | bytearray | str | int = None) -> None:

        super(LLCSecret, self).__init__(value)
        # self.representation = Representation(0)

    def __setattr__(self, key, value) -> None:
        match key:
            case 'representation' if not isinstance(value, Representation): raise ValueError(F"Error representation type")
            case 'representation' as rep:                                   LLCSecret.__representation = value
            case _:                                                         super().__setattr__(key, value)

    @property
    def representation(self) -> Representation:
        """used for set class property from instance"""
        return self.__representation

    def __getattr__(self, item):
        raise AttributeError(F'LLCSecret not has {item}')

    @staticmethod
    def __hide_all(value: str) -> str:
        for char_ in filter(lambda it: it != ' ', value):
            value = value.replace(char_, '*')
        return value

    def from_str(self, value: str) -> bytes:
        if self.__representation & Representation.ASCII:
            return cdt.VisibleString.from_str(self, value)
        else:
            return super(LLCSecret, self).from_str(value)

    def __str__(self) -> str:
        match self.__representation:
            case Representation.ASCII:                       return cdt.VisibleString.__str__(self)
            case Representation.HIDDEN:                      return self.__hide_all(super(LLCSecret, self).__str__())
            case Representation.ASCII_HIDDEN:                return self.__hide_all(cdt.VisibleString.__str__(self))
            case _:                                          return super(LLCSecret, self).__str__()


class LLCSecretHigh(LLCSecret):

    def validation(self):
        """ check for length equal 16 """
        if len(self) != 16:
            raise ValueError(F'Got length of High secret: {len(self)}, expected 16')


class AccessSelector(ut.Unsigned8):
    """ Unsigned8 1..4 """
    def __init__(self, value: int | str | ut.Unsigned8 = 1):
        super(AccessSelector, self).__init__(value)
        if int(self) > 4 or int(self) < 1:
            raise ValueError(F'The {self.__class__.__name__} got {self}, expected 1..4')


class Data(ut.Data):
    ELEMENTS = {1: ut.SequenceElement('All information', cdt.NullData),
                2: ut.SequenceElement('Access by class', ClassList),
                3: ut.SequenceElement('Access by object', ObjectIdList),
                4: ut.SequenceElement('Full object information', ObjectId)}


class SelectiveAccessDescriptor(ut.SelectiveAccessDescriptor):
    """ Selective access specification always starts with an access selector, followed by an access-specific access parameter list.
    Specified IS/IEC 62056-53 : 2006, 7.4.1.6 Selective access """
    access_selector: AccessSelector
    access_parameters: Data
    ELEMENTS = (ut.SequenceElement('access_selector', AccessSelector),
                ut.SequenceElement('access_parameters', Data))


class CosemAttributeDescriptorWithSelection(ut.CosemAttributeDescriptorWithSelection):
    access_selection: SelectiveAccessDescriptor
    ELEMENTS = (ut.SequenceElement('cosem_attribute_descriptor', ut.CosemAttributeDescriptor),
                ut.SequenceElement('access_selection', SelectiveAccessDescriptor))


class AssociationLN(ICAuto):
    """5.4.5 Association LN"""
    CLASS_ID = class_id.ASSOCIATION_LN
    VERSION = 0
    A_ELEMENTS = (ICAElement(2, "object_list", ObjectListType, selective_access=SelectiveAccessDescriptor),
                  ICAElement(3, "associated_partners_id", AssociatedPartnersType),
                  ICAElement(4, "application_context_name", ApplicationContextName),
                  ICAElement(5, "xDLMS_context_info", XDLMSContextType),
                  ICAElement(6, "authentication_mechanism_name", authentication_mechanism_name.AuthenticationMechanismName),
                  ICAElement(7, "LLS_secret", LLCSecret, classifier=Classifier.NOT_SPECIFIC),
                  ICAElement(8, "association_status", AssociationStatus, classifier=Classifier.DYNAMIC))
    M_ELEMENTS = (ICMElement(1, "reply_to_HLS_authentication", method.ReplyToHLSAuthentication),
                  ICMElement(2, "change_HLS_secret", LLCSecret),
                  ICMElement(3, "add_object", ObjectListElement),
                  ICMElement(4, "remove_object", ObjectListElement))
    object_list: Attr
    associated_partners_id: Attr
    application_context_name: Attr
    xDLMS_context_info: Attr
    authentication_mechanism_name: Attr
    LLS_secret: Attr
    association_status: Attr

    def __check_mechanism_id_existing(self):
        """check for existing mechanism ID else ERASE setting"""
        if self.authentication_mechanism_name is None:
            self.clear_attr(7)
            self._cbs_attr_post_init[7] = self.__check_mechanism_id_existing
        else:
            """nothing do it"""

    def __init_secret(self) -> None:
        """ before initiating secret need knowledge what kind of mechanism ID """
        match self.authentication_mechanism_name.mechanism_id_element, self.LLS_secret:
            case mechanism_id.NONE | mechanism_id.LOW, LLCSecret(): """keep secret value"""
            case mechanism_id.NONE | mechanism_id.LOW, _:           self.set_attr_link(7, LLCSecret())
            case mechanism_id.HIGH, LLCSecretHigh():                          """keep secret value"""
            case mechanism_id.HIGH, _:                                        self.set_attr_link(7, LLCSecretHigh())
            case unknown, _:                                                            raise ValueError(F'Not support Secret with {unknown}')

    # def get_attr_descriptor(self,
    #                         i: int,
    #                         with_selection: bool = False) -> ut.CosemAttributeDescriptor | CosemAttributeDescriptorWithSelection:
    #     """ with selection for object_list. TODO: Copypast ProfileGeneric"""
    #     descriptor: ut.CosemAttributeDescriptor = super(AssociationLN, self).get_attr_descriptor(i)
    #     if i == 2 and with_selection and self.object_list:
    #         return CosemAttributeDescriptorWithSelection((descriptor, self.object_list.selective_access))
    #     else:
    #         return descriptor
    #
    def get_lns(self) -> list[cst.LogicalName]:
        """return all LogicalNames"""
        el: ObjectListElement
        return [el.logical_name  for el in self.object_list]

    def iter_pars(self) -> Iterator[Parameter]:
        return (Parameter(el.logical_name.contents) for el in self.object_list)

    def __check_empty_object_list(self):
        if self.object_list is None:
            raise exc.ITEApplication(F"empty <{self.get_attr_element(2).NAME}> in {self}")

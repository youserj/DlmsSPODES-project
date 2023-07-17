from enum import IntFlag, auto
from ... import ITE_exceptions as exc
from ..__class_init__ import *
from ...types import choices
from ...types.implementations.long_unsigneds import ClassId
from ...types.implementations import arrays, enums
from ...pdu_enums import AttributeAccess, MethodAccess
from ...enums import MechanismId


class AccessMode(cdt.Enum, elements=(0, 1, 2, 3)):
    """ TODO: """


class AttributeAccessItem(cdt.Structure):
    """ Implemented attribute and it access . Use in Association LN """
    DEFAULT = b'\x02\x03\x0f\x01\x16\x00\x00'
    attribute_id: cdt.Integer
    access_mode: AccessMode
    access_selectors: choices.access_selectors


class AttributeAccessDescriptor(cdt.Array):
    """ Array of attribute_access_item """
    TYPE = AttributeAccessItem


class MethodAccessItem(cdt.Structure):
    """ Implemented method and it access . Use in Association LN """
    method_id: cdt.Integer
    access_mode: cdt.Boolean


class MethodAccessDescriptor(cdt.Array):
    """ Contain all implemented methods """
    TYPE = MethodAccessItem


class AccessRight(cdt.Structure):
    """ TODO: """
    attribute_access: AttributeAccessDescriptor
    method_access: MethodAccessDescriptor


class ObjectListElement(cdt.Structure):
    """ Visible COSEM objects with their class_id, version, logical name and the access rights to their attributes and methods within the given application association"""
    class_id: cdt.LongUnsigned
    version: cdt.Unsigned
    logical_name: cst.LogicalName
    access_rights: AccessRight


class ObjectListType(arrays.SelectionAccess):
    """ Array of object_list_element. The range for the client_SAP is 0…0x7F. The range for the server_SAP is 0x000…0x3FFF."""
    TYPE = ObjectListElement
    __getitem__: ObjectListElement

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
                    if int(item.access_mode) not in (2, 3):
                        return False
                    else:
                        break
                else:
                    continue
            else:
                raise ValueError(F"not find in {ln} attribute index: {index}")
        return True

    def __get_access_right(self, ln: cst.LogicalName | ut.CosemObjectInstanceId) -> AccessRight:
        """return object_list_element of object_list AssociationLN"""
        el: ObjectListElement = next(filter(lambda it: it.logical_name == ln, self), None)
        if el is None:
            raise exc.NoObject(F"not find {ln} in object_list")
        else:
            return el.access_rights

    def get_attr_access(self, ln: cst.LogicalName, index: int) -> AttributeAccess:
        """ index - DLMS object attribute index """
        for item in self.__get_access_right(ln).attribute_access:  # item: AttributeAccessItem
            item: AttributeAccessItem
            if int(item.attribute_id) == index:
                return AttributeAccess(int(item.access_mode))
            else:
                continue
        else:
            raise ValueError(F"not find in {ln} attribute index: {index}")

    def get_meth_access(self, ln: cst.LogicalName | ut.CosemObjectInstanceId, index: int) -> MethodAccess:
        """ index - DLMS object method index """
        for item in self.__get_access_right(ln).method_access:  # item: MethodAccessItem
            item: MethodAccessItem
            if int(item.method_id) == index:
                return MethodAccess(int(item.access_mode))
            else:
                continue
        else:
            raise ValueError(F"not find in {ln} attribute index: {index}")


class ServerSAP(cdt.LongUnsigned):

    def validate(self):
        if int.from_bytes(self.contents, 'big') > 0x3FFF:
            raise ValueError(F'The range for the server_SAP is 0x000…0x3FFF, but got {self.contents.hex()}')


class AssociatedPartnersType(cdt.Structure):
    """ Contains the identifiers of the COSEM client and the COSEM server (logical device) application processes within the physical devices
    hosting these processes, which belong to the application association modelled by the “Association LN” object. """
    DEFAULT = (0x10, 1)
    client_SAP: enums.ClientSAP
    server_SAP: ServerSAP


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


# TODO: join with cdt.FlagMixin
class Conformance(cdt.BitString):
    ELEMENTS = ({Language.ENGLISH: F'reserved-zero', Language.RUSSIAN: F'Зарезервированый-0'},
                {Language.ENGLISH: F'general-protection', Language.RUSSIAN: F'Основной защита'},
                {Language.ENGLISH: F'general-block-transfer', Language.RUSSIAN: F'Основная передача блока'},
                {Language.ENGLISH: F'read', Language.RUSSIAN: F'Чтение'},
                {Language.ENGLISH: F'write', Language.RUSSIAN: F'Запись'},
                {Language.ENGLISH: F'unconfirmed-write', Language.RUSSIAN: F'Неподтвержденная запись'},
                {Language.ENGLISH: F'reserved-six', Language.RUSSIAN: F'Зарезервированый-6'},
                {Language.ENGLISH: F'reserved-seven', Language.RUSSIAN: F'Зарезервированый-7'},
                {Language.ENGLISH: F'attribute0-supported-with-SET', Language.RUSSIAN: F'Поддерживается установка 0 атрибута'},
                {Language.ENGLISH: F'priority-mgmt-supported', Language.RUSSIAN: F'Поддерживается приоритет MGMT'},
                {Language.ENGLISH: F'attribute0-supported-with-GET', Language.RUSSIAN: F'Поддерживается чтение 0 атрибута'},
                {Language.ENGLISH: F'block-transfer-with-get-or-read', Language.RUSSIAN: F'Запрос или чтение через передачу блоков'},
                {Language.ENGLISH: F'block-transfer-with-set-or-write', Language.RUSSIAN: F'Установка или запись через передачу блоков'},
                {Language.ENGLISH: F'block-transfer-with-action', Language.RUSSIAN: F'Активация через передачу блоков'},
                {Language.ENGLISH: F'multiple-references', Language.RUSSIAN: F'Несколько ссылок'},
                {Language.ENGLISH: F'information-report', Language.RUSSIAN: F'Информационный отчет'},
                {Language.ENGLISH: F'data-notification', Language.RUSSIAN: F'Данные-уведомление'},
                {Language.ENGLISH: F'access', Language.RUSSIAN: F'Доступ'},
                {Language.ENGLISH: F'parameterized-access', Language.RUSSIAN: F'Параметризованный доступ'},
                {Language.ENGLISH: F'get', Language.RUSSIAN: F'Извлечение'},
                {Language.ENGLISH: F'set', Language.RUSSIAN: F'Установка'},
                {Language.ENGLISH: F'selective-access', Language.RUSSIAN: F'Выборочный доступ'},
                {Language.ENGLISH: F'event-notification', Language.RUSSIAN: F'Событие-уведомление'},
                {Language.ENGLISH: F'action', Language.RUSSIAN: F'Активация'})
    default = '011000001111111111111011'  # for LN only

    def __init__(self, value: bytes | bytearray | str | int | cdt.BitString = None):
        super(Conformance, self).__init__(value)
        if self.ELEMENTS is not None and len(self) != len(self.ELEMENTS):
            raise ValueError(F'For {self.__class__.__name__} get {len(self)} bits, expected {len(self.ELEMENTS)}')

    def __len__(self):
        return len(self.ELEMENTS)

    def from_bytes(self, value: bytes) -> bytes:
        length, pdu = cdt.get_length_and_pdu(value[1:])
        if length != len(self):
            raise ValueError(F'Got {length=}, expected {len(self)}')
        match value[:1]:
            case self.TAG if len(self) <= len(pdu) * 8: return pdu[:3]
            case self.TAG:                              raise ValueError(F'Got pdu length:{len(pdu)}, expected at least {len(self) >> 3}')
            case _ as error:                            raise TypeError(F'Expected {self.NAME} type, got {cdt.get_common_data_type_from(error).NAME}')

    def from_str(self, value: str) -> bytes:
        value = value + '0' * ((8 - len(self)) % 8)
        list_ = [value[count:(count + 8)] for count in range(0, len(self), 8)]
        value = b''
        for byte in list_:
            value += int(byte, base=2).to_bytes(1, byteorder='little')
        return value

    def from_int(self, value: int) -> bytes:
        if value < 0:
            raise ValueError
        res = 0
        start_bit = 2 ** (len(self) - 1)
        for i in range(len(self)):
            if value & (1 << i):
                res += start_bit >> i
        return res.to_bytes(len(self) // 8, byteorder='big')

    def from_bytearray(self, value: bytearray) -> bytes:
        return bytes(value)

    @classmethod
    def get_values(cls) -> list[str]:
        """ TODO: """
        return [values_dict[get_current_language()] for values_dict in cls.ELEMENTS]

    def validate_from(self, value: str, cursor_position: int) -> tuple[str, int]:
        """ return validated value and cursor position. TODO: copypast FlagMixin """
        type(self)(value=value.zfill(len(self)))
        return value, cursor_position

    @property
    def general_protection(self) -> int:
        return self.decode()[1]

    @property
    def general_block_transfer(self) -> int:
        return self.decode()[2]


class XDLMSContextType(cdt.Structure):
    """ Contains all the necessary information on the xDLMS context for the given association. """
    DEFAULT = (None, 1024, 1024, 6, 0, b'\x09\x07\x60\x85\x74\x05\x08\x02\x00')
    conformance: Conformance
    max_receive_pdu_size: cdt.LongUnsigned
    max_send_pdu_size: cdt.LongUnsigned
    dlms_version_number: cdt.Unsigned
    quality_of_service: cdt.Integer
    cyphering_info: cdt.OctetString


class MechanismIdElement(cdt.Enum, elements=tuple(range(8))):
    TAG = b'\x11'


class AuthenticationMechanismName(cdt.Structure):
    """ Contains the name of the authentication mechanism for the association (see IEC 62056-53). The authentication mechanism name is specified as an
    OBJECT IDENTIFIER in 7.3.7.2 of IEC 62056-53. The authentication_mechanism_name attribute includes the arc labels of the OBJECT IDENTIFIER. """
    DEFAULT = (2, 16, 756, 5, 8, 2, 0)
    joint_iso_ctt_element: cdt.Unsigned
    country_element: cdt.Unsigned
    country_name_element: cdt.LongUnsigned
    identified_organization_element: cdt.Unsigned
    DLMS_UA_element: cdt.Unsigned
    authentication_mechanism_name_element: cdt.Unsigned
    mechanism_id_element: MechanismIdElement

    def get_info(self) -> bytes:
        """ info for PDU from application_context_name. """
        return self.joint_iso_ctt_element.contents + \
               self.country_element.contents + \
               self.country_name_element.contents[1:] + \
               self.identified_organization_element.contents + \
               self.DLMS_UA_element.contents + \
               self.authentication_mechanism_name_element.contents + \
               self.mechanism_id_element.contents

    def get_mechanism_id_element(self) -> bytes:
        return self.mechanism_id_element.contents


class AssociationStatus(cdt.Enum, elements=(0, 1, 2)):
    """ Enum of access mode for methods """


class ClassList(cdt.Array):
    """ Access by class. In this case, only those object_list_elements of the object_list shall be included in the response, which have a class_id
    equal to one of the class_id-s of the class-list. No access_right information is included """
    TYPE = ClassId


class ObjectId(cdt.Structure):
    DEFAULT = b'\x02\x02\x12\x00\x08\x09\x06\x00\x00\x01\x00\x00\xff'
    class_id: ClassId
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

    def __init__(self, value: bytes | bytearray | str | int = None):

        super(LLCSecret, self).__init__(value)
        # self.representation = Representation(0)

    def __setattr__(self, key, value):
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

    def __str__(self):
        match self.__representation:
            case Representation.ASCII:                       return cdt.VisibleString.__str__(self)
            case Representation.HIDDEN:                      return self.__hide_all(super(LLCSecret, self).__str__())
            case Representation.ASCII_HIDDEN:                return self.__hide_all(cdt.VisibleString.__str__(self))
            case _:                                          return super(LLCSecret, self).__str__()


class LLCSecretHigh(LLCSecret):
    DEFAULT = b'0000000000000000'

    def validation(self):
        """ check for length equal 16 """
        if len(self) != 16:
            raise ValueError(F'Got length of High secret: {len(self)}, expected 16')

    def validate_from(self, value: str, cursor_position=None) -> tuple[str, int]:
        try:
            correct = type(self)(value)
            return str(correct), cursor_position + (len(str(correct))-len(value))
        except ValueError:
            match self.representation & 0b1:
                case Representation.HEX:
                    cursor_position: int = len(value)-1 if cursor_position is None else cursor_position
                    type(self)(F'{value[:cursor_position]}0{value[cursor_position:]}')  # check possible
                case Representation.ASCII:
                    type(self)(value.zfill(16))
            return value, cursor_position


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


class AssociationLN(ic.COSEMInterfaceClasses):
    """ COSEM logical devices able to establish application associations within a COSEM context using logical name referencing, model the associations
    through instances of the “Association LN” class. A COSEM logical device has one instance of this IC for each association
    the device is able to support"""
    NAME = cn.ASSOCIATION_LN
    CLASS_ID = ClassID.ASSOCIATION_LN_CLASS
    VERSION = Version.V0
    A_ELEMENTS = (ic.ICAElement(an.OBJECT_LIST, ObjectListType, selective_access=SelectiveAccessDescriptor),
                  ic.ICAElement(an.ASSOCIATED_PARTNERS_ID, AssociatedPartnersType),
                  ic.ICAElement(an.APPLICATION_CONTEXT_NAME, ApplicationContextName),
                  ic.ICAElement(an.XDLMS_CONTEXT_INFO, XDLMSContextType),
                  ic.ICAElement(an.AUTHENTICATION_MECHANISM_NAME, AuthenticationMechanismName),
                  ic.ICAElement(an.LLS_SECRET, LLCSecret),
                  ic.ICAElement(an.ASSOCIATION_STATUS, AssociationStatus))
    M_ELEMENTS = (ic.ICMElement(mn.REPLY_TO_HLS_AUTHENTICATION, cdt.OctetString),
                  ic.ICMElement(mn.CHANGE_HLS_SECRET, LLCSecret),
                  ic.ICMElement(mn.ADD_OBJECT, ObjectListElement),
                  ic.ICMElement(mn.REMOVE_OBJECT, ObjectListElement))

    def characteristics_init(self):
        self.set_attr(2, None)
        self.object_list.selective_access = SelectiveAccessDescriptor()
        self.set_attr(3, (0x10*self.logical_name.e, 1) if self.logical_name.e <= 4 else None)
        self.set_attr(4, None)
        self.set_attr(5, None)
        self.set_attr(8, None)
        # init secret after set authentication_mechanism_name(6)
        self._cbs_attr_post_init.update({5: self.__set_dlms_version_to_collection,
                                         6: self.__init_secret,
                                         7: self.__check_mechanism_id_existing})
        # set cb change client SAP
        match self.logical_name.e:
            case 0: self.associated_partners_id.client_SAP.register_cb_preset(self.__handle_preset_current_client_SAP)
            case _: self.associated_partners_id.client_SAP.register_cb_preset(self.__handle_preset_client_SAP)

    @property
    def object_list(self) -> ObjectListType:
        return self.get_attr(2)

    @property
    def associated_partners_id(self) -> AssociatedPartnersType:
        return self.get_attr(3)

    @property
    def application_context_name(self) -> ApplicationContextName:
        return self.get_attr(4)

    @property
    def xDLMS_context_info(self) -> XDLMSContextType:
        return self.get_attr(5)

    @property
    def authentication_mechanism_name(self) -> AuthenticationMechanismName:
        return self.get_attr(6)

    @property
    def LLS_secret(self) -> LLCSecret:
        return self.get_attr(7)

    @property
    def association_status(self) -> AssociationStatus:
        return self.get_attr(8)

    @property
    def reply_to_HLS_authentication(self) -> cdt.OctetString:
        return self.get_meth(1)

    @property
    def change_HLS_secret(self) -> LLS_secret:
        return self.get_meth(2)

    @property
    def add_object(self) -> ObjectListElement:
        return self.get_meth(3)

    @property
    def remove_object(self) -> ObjectListElement:
        return self.get_meth(4)

    def __check_mechanism_id_existing(self):
        """check for existing mechanism ID else ERASE setting"""
        if self.authentication_mechanism_name is None:
            self.clear_attr(7)
            self._cbs_attr_post_init[7] = self.__check_mechanism_id_existing
        else:
            """nothing do it"""

    def __init_secret(self):
        """ before initiating secret need knowledge what kind of mechanism ID """
        match int(self.authentication_mechanism_name.mechanism_id_element), self.LLS_secret:
            case MechanismId.NONE | MechanismId.LOW, LLCSecret(): """keep secret value"""
            case MechanismId.NONE | MechanismId.LOW, _:           self.set_attr_link(7, LLCSecret())
            case MechanismId.HIGH, LLCSecretHigh():                          """keep secret value"""
            case MechanismId.HIGH, _:                                        self.set_attr_link(7, LLCSecretHigh())
            case unknown, _:                                                            raise ValueError(F'Not support Secret with {unknown}')

    def __set_dlms_version_to_collection(self):
        self.collection.dlms_ver = int(self.xDLMS_context_info.dlms_version_number)

    @property
    def objects(self) -> list[ic.COSEMInterfaceClasses]:
        """ get all DLMS object in association"""
        try:
            return self.client_objects_list(self.associated_partners_id.client_SAP)
        except AttributeError as e:
            raise exc.NoObject('Objects list is empty')

    def client_objects_list(self, value: enums.ClientSAP) -> list[ic.COSEMInterfaceClasses]:
        """rudiment. use collection.get_object_list. TODO: remove in future"""
        for association in self.collection.get_objects_by_class_id(ut.CosemClassId(15)):
            if association.associated_partners_id.client_SAP == value and association.logical_name.e != 0:
                match association.object_list:
                    case ObjectListType():
                        ret = list()
                        for obj_list_type in association.object_list:
                            try:
                                obj = self.collection.get_object(obj_list_type)
                                if obj in ret:
                                    print(F'Double intersection {obj}')
                                else:
                                    ret.append(obj)
                            except exc.NoObject as e:
                                print(F'DLMS object not append to client object list. {e}')
                        return ret
                    case _:                raise exc.EmptyObj(F'{association} attr: 2')
        else:
            raise ValueError(F'Not found association with client SAP: {value}')

    def __handle_preset_current_client_SAP(self, value: enums.ClientSAP):
        """ Only for current association. Replacement attributes except logical_name and Client_SAP on attributes of association switching """
        for association in self.collection.get_objects_by_class_id(ut.CosemClassId(15)):
            if association.associated_partners_id.client_SAP == value and association is not self:
                # print('switch to: ', association)  # TODO: for debug
                for index, attr in association.get_index_with_attributes():
                    match index:
                        case 1: continue
                        case 3: self.associated_partners_id.server_SAP.set(attr.server_SAP)
                        case _: self.set_attr_link(index, attr)
                break
        else:
            raise exc.NoObject(F'Not found association with client SAP: {value}')

    def __handle_preset_client_SAP(self, value: cdt.LongUnsigned):
        """ ban change for all associations without current """
        if value != self.associated_partners_id.client_SAP:
            raise ValueError("Don't support change client SAP")

    @property
    def source_address(self) -> bytes:
        """ source address from client_SAP. ISO/IEC 13239:2002(E), Annex H, H.4 Frame format type 3 (page 128). """
        return (int(self.associated_partners_id.client_SAP) << 1 | 1).to_bytes(1, 'big')

    def get_attr_descriptor(self, value: int, SAP: enums.ClientSAP = enums.configurator_client) -> ut.CosemAttributeDescriptor | CosemAttributeDescriptorWithSelection:
        """ with selection for object_list. TODO: Copypast ProfileGeneric"""
        descriptor: ut.CosemAttributeDescriptor = super(AssociationLN, self).get_attr_descriptor(value, SAP)
        if value == 2 and bool(self.collection.getAssociationBySAP(SAP).xDLMS_context_info.conformance.decode()[21]):
            return CosemAttributeDescriptorWithSelection((descriptor, self.object_list.selective_access))
        else:
            return descriptor

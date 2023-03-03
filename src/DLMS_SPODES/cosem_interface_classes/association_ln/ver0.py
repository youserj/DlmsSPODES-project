from __future__ import annotations
from functools import cache
from typing import Callable
from enum import IntFlag, auto
from ... import ITE_exceptions as exc
from ..__class_init__ import *
from ...types import choices
from ...types.implementations.long_unsigneds import ClassId
from ...types.implementations import arrays
from ...pdu_enums import AttributeAccess, MethodAccess


class AccessMode(cdt.Enum):
    """ TODO: """
    ELEMENTS = {b'\x00': en.NO_ACCESS,
                b'\x01': en.READ_ONLY,
                b'\x02': en.WRITE_ONLY,
                b'\x03': en.READ_AND_WRITE}


class AttributeAccessItem(cdt.Structure):
    """ Implemented attribute and it access . Use in Association LN """
    values: tuple[cdt.Integer, AccessMode, cdt.NullData | cdt.Array]
    default = b'\x02\x03\x0f\x01\x16\x00\x00'
    ELEMENTS = (cdt.StructElement(cdt.se.ATTRIBUTE_ID, cdt.Integer),
                cdt.StructElement(cdt.se.ACCESS_MODE, AccessMode),
                cdt.StructElement(cdt.se.ACCESS_SELECTORS, choices.access_selectors))

    @property
    def attribute_id(self) -> cdt.Integer:
        return self.values[0]

    @property
    def access_mode(self) -> AccessMode:
        return self.values[1]

    @property
    def access_selectors(self) -> cdt.NullData | cdt.Array:
        return self.values[2]


class AttributeAccessDescriptor(cdt.Array):
    """ Array of attribute_access_item """
    TYPE = AttributeAccessItem


class MethodAccessItem(cdt.Structure):
    """ Implemented method and it access . Use in Association LN """
    values: tuple[cdt.Integer, cdt.Boolean]
    ELEMENTS = (cdt.StructElement(cdt.se.METHOD_ID, cdt.Integer),
                cdt.StructElement(cdt.se.ACCESS_MODE, cdt.Boolean))

    @property
    def method_id(self) -> cdt.Integer:
        return self.values[0]

    @property
    def access_mode(self) -> cdt.Boolean:
        return self.values[1]


class MethodAccessDescriptor(cdt.Array):
    """ Contain all implemented methods """
    TYPE = MethodAccessItem


class AccessRight(cdt.Structure):
    """ TODO: """
    values: tuple[AttributeAccessDescriptor, MethodAccessDescriptor]
    ELEMENTS = (cdt.StructElement(cdt.se.ATTRIBUTE_ACCESS, AttributeAccessDescriptor),
                cdt.StructElement(cdt.se.METHOD_ACCESS, MethodAccessDescriptor))

    @property
    def attribute_access(self) -> AttributeAccessDescriptor:
        return self.values[0]

    @property
    def method_access(self) -> MethodAccessDescriptor:
        return self.values[1]


class ObjectListElement(cdt.Structure):
    """ Visible COSEM objects with their class_id, version, logical name and the access rights to their attributes and methods within the given application association"""
    values: tuple[cdt.LongUnsigned, cdt.Unsigned, cst.LogicalName, AccessRight]
    ELEMENTS = (cdt.StructElement(cdt.se.CLASS_ID, cdt.LongUnsigned),
                cdt.StructElement(cdt.se.VERSION, cdt.Unsigned),
                cdt.StructElement(cdt.se.LOGICAL_NAME, cst.LogicalName),
                cdt.StructElement(cdt.se.ACCESS_RIGHTS, AccessRight))

    @property
    def class_id(self) -> cdt.LongUnsigned:
        return self.values[0]

    @property
    def version(self) -> cdt.Unsigned:
        return self.values[1]

    @property
    def logical_name(self) -> cst.LogicalName:
        return self.values[2]

    @property
    def access_rights(self) -> AccessRight:
        return self.values[3]


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


class ClientSAP(cdt.Enum):
    """ IEC 62056-46 2002 6.4.2.3 Reserved special HDLC addresses p.40. IS15952ver2 """
    TAG = b'\x0f'
    ELEMENTS = {b'\x00': en.NO_STATION,
                b'\x01': en.CLIENT_MANAGEMENT_PROCESS,
                b'\x10': en.PUBLIC_CLIENT,
                b'\x20': en.METER_READER,
                b'\x30': en.UTILITY_SETTING,
                b'\x40': en.PUSH,
                b'\x50': en.FIRMWARE_UPDATE,
                b'\x60': en.IHD}


class ServerSAP(cdt.LongUnsigned):

    def validate(self):
        if int.from_bytes(self.contents, 'big') > 0x3FFF:
            raise ValueError(F'The range for the server_SAP is 0x000…0x3FFF, but got {self.contents.hex()}')


class AssociatedPartnersType(cdt.Structure):
    """ Contains the identifiers of the COSEM client and the COSEM server (logical device) application processes within the physical devices
    hosting these processes, which belong to the application association modelled by the “Association LN” object. """
    values: tuple[ClientSAP, cdt.LongUnsigned]
    default = (0x10, 1)
    ELEMENTS = (cdt.StructElement(cdt.se.CLIENT_SAP, ClientSAP),
                cdt.StructElement(cdt.se.SERVER_SAP, ServerSAP))

    @property
    def client_SAP(self) -> ClientSAP:
        return self.values[0]

    @property
    def server_SAP(self) -> cdt.LongUnsigned:
        return self.values[1]


class ApplicationContextName(cdt.Structure):
    """ In the COSEM environment, it is intended that an application context pre-exists and is referenced by its name during the establishment of an
    application association. This attribute contains the name of the application context for that association."""
    values: tuple[cdt.Unsigned, cdt.Unsigned, cdt.LongUnsigned, cdt.Unsigned, cdt.Unsigned, cdt.Unsigned, cdt.Unsigned]
    default = (2, 16, 116, 5, 8, 1, 1)
    ELEMENTS = (cdt.StructElement(cdt.se.JOINT_ISO_CTT_ELEMENT, cdt.Unsigned),
                cdt.StructElement(cdt.se.COUNTRY_ELEMENT, cdt.Unsigned),
                cdt.StructElement(cdt.se.COUNTRY_NAME_ELEMENT, cdt.LongUnsigned),
                cdt.StructElement(cdt.se.IDENTIFIED_ORGANIZATION_ELEMENT, cdt.Unsigned),
                cdt.StructElement(cdt.se.DLMS_UA_ELEMENT, cdt.Unsigned),
                cdt.StructElement(cdt.se.APPLICATION_CONTEXT_ELEMENT, cdt.Unsigned),
                cdt.StructElement(cdt.se.CONTEXT_ID_ELEMENT, cdt.Unsigned))

    @property
    def joint_iso_ctt_element(self) -> cdt.Unsigned:
        return self.values[0]

    @property
    def country_element(self) -> cdt.Unsigned:
        return self.values[1]

    @property
    def country_name_element(self) -> cdt.LongUnsigned:
        return self.values[2]

    @property
    def identified_organization_element(self) -> cdt.Unsigned:
        return self.values[3]

    @property
    def DLMS_UA_element(self) -> cdt.Unsigned:
        return self.values[4]

    @property
    def application_context_element(self) -> cdt.Unsigned:
        return self.values[5]

    @property
    def context_id_element(self) -> cdt.Unsigned:
        return self.values[6]


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
    values: tuple[Conformance, cdt.LongUnsigned, cdt.LongUnsigned, cdt.Unsigned, cdt.Integer, cdt.OctetString]
    default = (None, 1024, 1024, 6, 0, b'\x09\x07\x60\x85\x74\x05\x08\x02\x00')
    ELEMENTS = (cdt.StructElement(cdt.se.CONFORMANCE, Conformance),
                cdt.StructElement(cdt.se.MAX_RECEIVE_PDU_SIZE, cdt.LongUnsigned),
                cdt.StructElement(cdt.se.MAX_SEND_PDU_SIZE, cdt.LongUnsigned),
                cdt.StructElement(cdt.se.DLMS_VERSION_NUMBER, cdt.Unsigned),
                cdt.StructElement(cdt.se.QUALITY_OF_SERVICE, cdt.Integer),
                cdt.StructElement(cdt.se.CYPHERING_INFO, cdt.OctetString))

    @property
    def conformance(self) -> Conformance:
        """the conformance element contains the xDLMS conformance block supported by the server"""
        return self.values[0]

    @property
    def max_receive_pdu_size(self) -> cdt.LongUnsigned:
        """the max_receive_pdu_size element contains the maximum  length for an xDLMS APDU, expressed in bytes that the client may send. This is the same
        as the server-max-receive-pdu-size parameter of the DLMS-Initiate.response pdu (see IEC 62056-53)"""
        return self.values[1]

    @property
    def max_send_pdu_size(self) -> cdt.LongUnsigned:
        """the max_send_pdu_size, in an active association contains the maximum length for an xDLMS APDU, expressed in bytes that the server may send.
        This is the same as the client-max-receive-pdu-size parameter of the DLMS-Initiate.request pdu (see IEC 62056-53)"""
        return self.values[2]

    @property
    def dlms_version_number(self) -> cdt.Unsigned:
        """the dlms_version_number element contains the DLMS version number supported by the server"""
        return self.values[3]

    @property
    def quality_of_service(self) -> cdt.Integer:
        """the quality_of _service element is not used"""
        return self.values[4]

    @property
    def cyphering_info(self) -> cdt.OctetString:
        """the cyphering_info, in an active association, contains the dedicated key parameter of the DLMS-Initiate.request pdu (See 62056-53)"""
        return self.values[5]


class MechanismIdElement(cdt.Enum):
    TAG = b'\x11'
    ELEMENTS = {b'\x00': en.NONE,
                b'\x01': en.LOW,
                b'\x02': en.HIGH,
                b'\x03': en.HIGH_MD5,
                b'\x04': en.HIGH_SHA1,
                b'\x05': en.HIGH_GMAC,
                b'\x06': en.HIGH_SHA256,
                b'\x07': en.HIGH_ECDSA}


class AuthenticationMechanismName(cdt.Structure):
    """ Contains the name of the authentication mechanism for the association (see IEC 62056-53). The authentication mechanism name is specified as an
    OBJECT IDENTIFIER in 7.3.7.2 of IEC 62056-53. The authentication_mechanism_name attribute includes the arc labels of the OBJECT IDENTIFIER. """
    values: tuple[cdt.Unsigned, cdt.Unsigned, cdt.LongUnsigned, cdt.Unsigned, cdt.Unsigned, cdt.Unsigned, MechanismIdElement]
    default = (2, 16, 756, 5, 8, 2, 0)
    ELEMENTS = (cdt.StructElement(cdt.se.JOINT_ISO_CTT_ELEMENT, cdt.Unsigned),
                cdt.StructElement(cdt.se.COUNTRY_ELEMENT, cdt.Unsigned),
                cdt.StructElement(cdt.se.COUNTRY_NAME_ELEMENT, cdt.LongUnsigned),
                cdt.StructElement(cdt.se.IDENTIFIED_ORGANIZATION_ELEMENT, cdt.Unsigned),
                cdt.StructElement(cdt.se.DLMS_UA_ELEMENT, cdt.Unsigned),
                cdt.StructElement(cdt.se.AUTHENTICATION_MECHANISM_NAME_ELEMENT, cdt.Unsigned),
                cdt.StructElement(cdt.se.MECHANISM_ID_ELEMENT, MechanismIdElement))

    @property
    def joint_iso_ctt_element(self) -> cdt.Unsigned:
        return self.values[0]

    @property
    def country_element(self) -> cdt.Unsigned:
        return self.values[1]

    @property
    def country_name_element(self) -> cdt.LongUnsigned:
        return self.values[2]

    @property
    def identified_organization_element(self) -> cdt.Unsigned:
        return self.values[3]

    @property
    def DLMS_UA_element(self) -> cdt.Unsigned:
        return self.values[4]

    @property
    def authentication_mechanism_name_element(self) -> cdt.Unsigned:
        return self.values[5]

    @property
    def mechanism_id_element(self) -> MechanismIdElement:
        return self.values[6]

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


class AssociationStatus(cdt.Enum):
    """ Enum of access mode for methods """
    ELEMENTS = {b'\x00': en.NON_ASSOCIATED,
                b'\x01': en.ASSOCIATION_PENDING,
                b'\x02': en.ASSOCIATED}


class ClassList(cdt.Array):
    """ Access by class. In this case, only those object_list_elements of the object_list shall be included in the response, which have a class_id
    equal to one of the class_id-s of the class-list. No access_right information is included """
    TYPE = ClassId


class ObjectId(cdt.Structure):
    values: tuple[ClassId, cst.LogicalName]
    default = b'\x02\x02\x12\x00\x08\x09\x06\x00\x00\x01\x00\x00\xff'
    ELEMENTS = (cdt.StructElement(cdt.se.CLASS_ID, ClassId),
                cdt.StructElement(cdt.se.LOGICAL_NAME, cst.LogicalName))

    @property
    def class_id(self) -> ClassId:
        return self.values[0]

    @property
    def logical_name(self) -> cst.LogicalName:
        return self.values[1]


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
    CLASS_ID = ut.CosemClassId(class_id.ASSOCIATION_LN_CLASS)
    VERSION = cdt.Unsigned(0)
    __cb_get_attr_descriptor: Callable[[int], ut.CosemAttributeDescriptor | ut.CosemAttributeDescriptorWithSelection]
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
        self._cbs_attr_post_init.update({6: self.__init_secret,
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
        match self.authentication_mechanism_name.mechanism_id_element:
            case MechanismIdElement(en.NONE) | MechanismIdElement(en.LOW): self.set_attr_link(7, LLCSecret())
            case MechanismIdElement(en.HIGH):                              self.set_attr_link(7, LLCSecretHigh())
            case unknown:                                                  raise ValueError(F'Not support Secret with {unknown}')
        print(F'set secret class {self}, REMOVE it message')

    @property
    def objects(self) -> list[ic.COSEMInterfaceClasses]:
        """ get all DLMS object in association"""
        try:
            return self.client_objects_list(self.associated_partners_id.client_SAP)
        except AttributeError as e:
            raise exc.NoObject('Objects list is empty')

    @cache
    def client_objects_list(self, value: ClientSAP) -> list[ic.COSEMInterfaceClasses]:
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

    def __handle_preset_current_client_SAP(self, value: ClientSAP):
        """ Only for current association. Replacement attributes except logical_name and Client_SAP on attributes of association switching """
        for association in self.collection.get_objects_by_class_id(ut.CosemClassId(15)):
            if association.associated_partners_id.client_SAP == value and association is not self:
                print('switch to: ', association)  # TODO: for debug
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

    def get_attr_descriptor(self, value: int) -> ut.CosemAttributeDescriptor | CosemAttributeDescriptorWithSelection:
        """ with selection for object_list. TODO: Copypast ProfileGeneric"""
        descriptor: ut.CosemAttributeDescriptor = super(AssociationLN, self).get_attr_descriptor(value)
        if value == 2 and bool(self.collection.current_association.xDLMS_context_info.conformance.decode()[21]):
            return CosemAttributeDescriptorWithSelection((descriptor, self.object_list.selective_access))
        else:
            return descriptor


if __name__ == '__main__':
    as1 = AssociationLN('0.0.40.0.1.255')
    # sela = SelectiveAccessDescriptor()
    # sela.set_selector(3, [(1,2,'1.2.3.4.5.6',None), (4,5,'1.2.3.4.5.4',None),])
    attr_des_with = CosemAttributeDescriptorWithSelection(((15, '0.0.40.0.0.255', 2), (2, [15])))
    a2 = CosemAttributeDescriptorWithSelection(((15, '0.0.40.0.0.255', 2), (4, (15, '0.0.40.0.1.255'))))
    attr_des_with.access_selection.set_selector(2)
    # a = max(map(lambda val: val[Language.RUSSIAN], ClientSAP.elements.values()), key=lambda value: len(value))
    a = Conformance('101010110010101011110101')
    a.set(b'\xb8\x18\x00')
    c = a[1]
    c = a.get_values()
    a = XDLMSContextType()
    a = LLCSecret('11 00 33 34')
    # a = AssociationLN(1)
    a.representation = Representation.ASCII | Representation.HIDDEN
    a1 = LLCSecret('11 55 55')
    print(str(a))
    a = MechanismIdElement(en.HIGH)
    d = MechanismIdElement(en.LOW)
    c = a > d
    a = SelectiveAccessDescriptor()
    b = bytes.fromhex('01 01 02 04 12 00 08 11 00 09 06 00 00 01 00 00 FF 02 02 01 09 02 03 0F 01 16 01 00 02 03 0F 02 16 03 00 02 03 0F 03 16 03 00 02 03 0F 04 16 03 00 02 03 0F 05 16 03 00 02 03 0F 06 16 03 00 02 03 0F 07 16 03 00 02 03 0F 08 16 03 00 02 03 0F 09 16 03 00 01 06 02 02 0F 01 16 01 02 02 0F 02 16 01 02 02 0F 03 16 01 02 02 0F 04 16 01 02 02 0F 05 16 01 02 02 0F 06 16 01')
    a = ObjectListType(b)
    print(a)

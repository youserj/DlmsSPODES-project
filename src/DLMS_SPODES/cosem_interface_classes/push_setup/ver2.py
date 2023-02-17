from ..__class_init__ import *
from ...types.implementations import structs, emuns, integers


class RestrictionValue(ut.CHOICE):
    TYPE = (cdt.Structure, cdt.NullData)
    ELEMENTS = {0: ut.SequenceElement("no restriction apply", cdt.NullData),
                1: ut.SequenceElement("restriction by date", structs.RestrictionByDate),
                2: ut.SequenceElement("restriction by entry", structs.RestrictionByEntry)}


restriction_value = RestrictionValue()


class RestrictionElement(cdt.Structure):
    """Override several methods of cdt.Structure. It limited Structure."""
    values: tuple[emuns.RestrictionType, cdt.NullData | structs.RestrictionByDate | structs.RestrictionByEntry]

    def __init__(self):
        self.__dict__["values"] = (emuns.RestrictionType(0), cdt.NullData())
        self.restriction_type.register_cb_post_set(self.__set_certificate_identification_type)

    def __set_certificate_identification_type(self):
        self.__dict__["values"] = (self.restriction_type, restriction_value(int(self.restriction_type)))

    @property
    def ELEMENTS(self) -> tuple[cdt.StructElement, cdt.StructElement]:
        match int(self.restriction_type):
            case 0: r_v = cdt.NullData
            case 1: r_v = structs.RestrictionByDate
            case 2: r_v = structs.RestrictionByEntry
            case err: raise ValueError(F"got {err} type of {self.__class__.__name__}, expect 0, 1, 2")
        return (cdt.StructElement(cdt.se.RESTRICTION_TYPE, emuns.RestrictionType),
                cdt.StructElement(cdt.se.RESTRICTION_VALUE, r_v))

    @property
    def restriction_type(self) -> emuns.RestrictionType:
        return self.values[0]

    @property
    def restriction_value(self) -> cdt.NullData | structs.RestrictionByDate | structs.RestrictionByEntry:
        return self.values[1]


class ColumnElement(cdt.Array):
    """ Specifies the list of capture objects """
    TYPE = structs.CaptureObjectDefinition


class PushObjectDefinition(cdt.Structure):
    values: tuple[cdt.LongUnsigned, cst.LogicalName, cdt.Integer, cdt.LongUnsigned, RestrictionElement, ColumnElement]
    ELEMENTS = (cdt.StructElement(cdt.se.CLASS_ID, cdt.LongUnsigned),
                cdt.StructElement(cdt.se.LOGICAL_NAME, cst.LogicalName),
                cdt.StructElement(cdt.se.ATTRIBUTE_INDEX, cdt.Integer),
                cdt.StructElement(cdt.se.DATA_INDEX, cdt.LongUnsigned),
                cdt.StructElement(cdt.se.RESTRICTION, RestrictionElement),
                cdt.StructElement(cdt.se.COLUMN, ColumnElement))

    @property
    def class_id(self) -> cdt.LongUnsigned:
        return self.values[0]

    @property
    def logical_name(self) -> cst.LogicalName:
        return self.values[1]

    @property
    def attribute_index(self) -> cdt.Integer:
        return self.values[2]

    @property
    def data_index(self) -> cdt.LongUnsigned:
        return self.values[3]

    @property
    def restriction(self) -> RestrictionElement:
        return self.values[4]

    @property
    def column(self) -> ColumnElement:
        return self.values[5]


class PushObjectList(cdt.Array):
    """ Defines the list of attributes to be pushed. """
    TYPE = PushObjectDefinition


class TransportServiceType(cdt.Enum):
    ELEMENTS = {b'\x00': en.TCP,
                b'\x01': en.UDP,
                b'\x02': en.FTP_RESERVED,
                b'\x03': en.SMTP_RESERVED,
                b'\x04': en.SMS,
                b'\x05': en.HDLC,
                b'\x06': en.M_BUS,
                b'\x07': en.ZIGBEE_RESERVED,
                b'\x08': en.DLMS_GATEWAY}
    ELEMENTS.update(((i.to_bytes(1, "big"), en.MANUFACTURER_SPECIFIC) for i in range(200, 256)))


class MessageType(cdt.Enum):
    ELEMENTS = {b'\x00': en.A_XDR,
                b'\x01': en.XML}
    ELEMENTS.update(((i.to_bytes(1, "big"), en.MANUFACTURER_SPECIFIC) for i in range(128, 256)))


class SendDestinationAndMethod(cdt.Structure):
    values: tuple[TransportServiceType, cdt.OctetString, MessageType]
    ELEMENTS = (cdt.StructElement(cdt.se.TRANSPORT_SERVICE, TransportServiceType),
                cdt.StructElement(cdt.se.DESTINATION, cdt.OctetString),
                cdt.StructElement(cdt.se.MESSAGE, MessageType))

    @property
    def transport_service(self) -> TransportServiceType:
        return self.values[0]

    @property
    def destination(self) -> cdt.OctetString:
        return self.values[1]

    @property
    def message(self) -> MessageType:
        return self.values[2]


class CommunicationWindow(cdt.Array):
    """ Defines the time points when the communication window(s) for the push become(s) active (start_time) and inactive (end_time). """
    TYPE = structs.WindowElement


class RepetitionDelay(cdt.Structure):
    values: tuple[cdt.LongUnsigned, cdt.LongUnsigned, cdt.LongUnsigned]
    ELEMENTS = (cdt.StructElement(cdt.se.REPETITION_DELAY_MIN, cdt.LongUnsigned),
                cdt.StructElement(cdt.se.REPETITION_DELAY_EXPONENT, cdt.LongUnsigned),
                cdt.StructElement(cdt.se.REPETITION_DELAY_MAX, cdt.LongUnsigned))

    @property
    def repetition_delay_min(self) -> cdt.LongUnsigned:
        return self.values[0]

    @property
    def repetition_delay_exponent(self) -> cdt.LongUnsigned:
        return self.values[1]

    @property
    def repetition_delay_max(self) -> cdt.LongUnsigned:
        return self.values[2]


class PushOperationMethod(cdt.Enum):
    ELEMENTS = {b'\x00': en.UNCONFIRMED_FAILURE,
                b'\x01': en.UNCONFIRMED_MISSING,
                b'\x02': en.CONFIRMED}


class ConfirmationParameters(cdt.Structure):
    values: tuple[cdt.DateTime, cdt.DoubleLongUnsigned]
    ELEMENTS = (cdt.StructElement(cdt.se.CONFIRMATION_START_DATE, cdt.DateTime),
                cdt.StructElement(cdt.se.CONFIRMATION_INTERVAL, cdt.DoubleLongUnsigned))

    @property
    def confirmation_start_date(self) -> cdt.DateTime:
        return self.values[0]

    @property
    def confirmation_interval(self) -> cdt.DoubleLongUnsigned:
        return self.values[1]


class IdentifiedKeyInfoOptions(cdt.Enum):
    ELEMENTS = {b'\x00': en.GLOB_UNI_ENCR_KEY,
                b'\x01': en.GLOB_BROAD_ENCR_KEY}


class KEKId(cdt.Enum):
    ELEMENTS = {b'\x00': en.MASTER_KEY}


class WrappedKeyInfoOptions(cdt.Structure):
    values: tuple[KEKId, cdt.OctetString]
    ELEMENTS = (cdt.StructElement(cdt.se.KEY_ID, KEKId),
                cdt.StructElement(cdt.se.KEY_CIPHERED_DATA, cdt.OctetString))

    @property
    def kek_id(self) -> KEKId:
        return self.values[0]

    @property
    def key_ciphered_data(self) -> cdt.OctetString:
        return self.values[1]


class AgreedKeyInfoOptions(cdt.Structure):
    values: tuple[cdt.OctetString, cdt.OctetString]
    ELEMENTS = (cdt.StructElement(cdt.se.KEY_PARAMETERS, cdt.OctetString),
                cdt.StructElement(cdt.se.KEY_CIPHERED_DATA, cdt.OctetString))

    @property
    def kek_id(self) -> cdt.OctetString:
        return self.values[0]

    @property
    def key_ciphered_data(self) -> cdt.OctetString:
        return self.values[1]


class KeyInfoOptions(ut.CHOICE):
    TYPE = (cdt.Enum, cdt.Structure)
    ELEMENTS = {0: ut.SequenceElement("identified_key", IdentifiedKeyInfoOptions),
                1: ut.SequenceElement("wrapped_key", WrappedKeyInfoOptions),
                2: ut.SequenceElement("agreed_key", AgreedKeyInfoOptions)}


key_info_options = KeyInfoOptions()


class KeyInfoElement(cdt.Structure):
    """Override several methods of cdt.Structure. It limited Structure."""
    values: tuple[emuns.KeyInfoType, IdentifiedKeyInfoOptions | WrappedKeyInfoOptions | AgreedKeyInfoOptions]

    def __init__(self):
        self.__dict__["values"] = (emuns.KeyInfoType(0), IdentifiedKeyInfoOptions())
        self.key_info_type.register_cb_post_set(self.__set_key_info_type)

    def __set_key_info_type(self):
        self.__dict__["values"] = (self.key_info_type, key_info_options(int(self.key_info_type)))

    @property
    def ELEMENTS(self) -> tuple[cdt.StructElement, cdt.StructElement]:
        match int(self.key_info_type):
            case 0: key_o = IdentifiedKeyInfoOptions
            case 1: key_o = WrappedKeyInfoOptions
            case 2: key_o = AgreedKeyInfoOptions
            case err: raise ValueError(F"got {err} type of {self.__class__.__name__}, expect 0, 1, 2")
        return (cdt.StructElement(cdt.se.KEY_INFO_TYPE, emuns.KeyInfoType),
                cdt.StructElement(cdt.se.KEY_INFO_OPTIONS, key_o))

    @property
    def key_info_type(self) -> emuns.KeyInfoType:
        return self.values[0]

    @property
    def key_info_options(self) -> IdentifiedKeyInfoOptions | WrappedKeyInfoOptions | AgreedKeyInfoOptions:
        return self.values[1]


class ProtectionOptions(cdt.Structure):
    values: tuple[cdt.OctetString, cdt.OctetString, cdt.OctetString, cdt.OctetString, KeyInfoElement]
    ELEMENTS = (cdt.StructElement(cdt.se.TRANSACTION_ID, cdt.OctetString),
                cdt.StructElement(cdt.se.ORIGINATOR_SYSTEM_TITLE, cdt.OctetString),
                cdt.StructElement(cdt.se.RECIPIENT_SYSTEM_TITLE, cdt.OctetString),
                cdt.StructElement(cdt.se.OTHER_INFORMATION, cdt.OctetString),
                cdt.StructElement(cdt.se.KEY_INFO, cdt.OctetString))

    @property
    def transaction_id(self) -> cdt.OctetString:
        return self.values[0]

    @property
    def originator_system_title(self) -> cdt.OctetString:
        return self.values[1]

    @property
    def recipient_system_title(self) -> cdt.OctetString:
        return self.values[2]

    @property
    def other_information(self) -> cdt.OctetString:
        return self.values[3]

    @property
    def key_info(self) -> KeyInfoElement:
        return self.values[4]


class ProtectionParametersElement(cdt.Structure):
    values: tuple[emuns.ProtectionType, ProtectionOptions]
    ELEMENTS = (cdt.StructElement(cdt.se.PROTECTION_TYPE, emuns.ProtectionType),
                cdt.StructElement(cdt.se.PROTECTION_OPTIONS, ProtectionOptions))

    @property
    def protection_type(self) -> emuns.ProtectionType:
        return self.values[0]

    @property
    def protection_options(self) -> ProtectionOptions:
        return self.values[1]


class PushProtectionParameters(cdt.Array):
    TYPE = ProtectionParametersElement


class PushSetup(ic.COSEMInterfaceClasses):
    """ DLMS UA 1000-1 Ed. 14 4.4.8.2 Push setup"""
    NAME = cn.PUSH_SETUP
    CLASS_ID = ut.CosemClassId(class_id.PUSH_SETUP)
    VERSION = cdt.Unsigned(2)
    A_ELEMENTS = (ic.ICAElement(an.PUSH_OBJECT_LIST, PushObjectList),
                  ic.ICAElement(an.SEND_DESTINATION_AND_METHOD, SendDestinationAndMethod),
                  ic.ICAElement(an.COMMUNICATION_WINDOW, CommunicationWindow),
                  ic.ICAElement(an.RANDOMISATION_START_INTERVAL, cdt.LongUnsigned),
                  ic.ICAElement(an.NUMBER_OF_RETRIES, cdt.Unsigned),
                  ic.ICAElement(an.REPETITION_DELAY, RepetitionDelay),
                  ic.ICAElement(an.PORT_REFERENCE, cst.LogicalName),
                  ic.ICAElement(an.PUSH_CLIENT_SAP, cdt.Integer),
                  ic.ICAElement(an.PUSH_PROTECTION_PARAMETERS, PushProtectionParameters),
                  ic.ICAElement(an.PUSH_OPERATION_METHOD, PushOperationMethod),
                  ic.ICAElement(an.CONFIRMATION_PARAMETERS, ConfirmationParameters),
                  ic.ICAElement(an.LAST_CONFIRMATION_DATE_TIME, cdt.DateTime))
    M_ELEMENTS = (ic.ICMElement(mn.PUSH, integers.Only0),
                  ic.ICMElement(mn.RESET, integers.Only0))

    def characteristics_init(self):
        """nothing do it"""

    @property
    def push_object_list(self) -> PushObjectList:
        return self.get_attr(2)

    @property
    def send_destination_and_method(self) -> SendDestinationAndMethod:
        return self.get_attr(3)

    @property
    def communication_window(self) -> CommunicationWindow:
        return self.get_attr(4)

    @property
    def randomisation_start_interval(self) -> cdt.LongUnsigned:
        return self.get_attr(5)

    @property
    def number_of_retries(self) -> cdt.Unsigned:
        return self.get_attr(6)

    @property
    def repetition_delay(self) -> RepetitionDelay:
        return self.get_attr(7)

    @property
    def port_reference(self) -> cst.LogicalName:
        return self.get_attr(8)

    @property
    def push_client_SAP(self) -> cdt.Integer:
        return self.get_attr(9)

    @property
    def push_protection_parameters(self) -> PushProtectionParameters:
        return self.get_attr(10)

    @property
    def push_operation_method(self) -> PushOperationMethod:
        return self.get_attr(11)

    @property
    def confirmation_parameters(self) -> ConfirmationParameters:
        return self.get_attr(12)

    @property
    def last_confirmation_date_time(self) -> cdt.DateTime:
        return self.get_attr(13)

    @property
    def push(self) -> integers.Only0:
        return self.get_meth(1)

    @property
    def reset(self) -> integers.Only0:
        return self.get_meth(2)

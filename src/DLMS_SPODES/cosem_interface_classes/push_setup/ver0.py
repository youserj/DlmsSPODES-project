from COSEMpdu.data import Array, Integer, Structure, LongUnsigned, OctetString, Unsigned, Enum, EnumMixin
from typing import Final
from ...types.type_alias import Attr
from ...types import cst
from ...types.implementations import structs, integers
from ..cosem_interface_class import ICAElement, ICMElement, ICAuto


class ObjectDefinition(Structure):
    """object_definition"""
    class_id: LongUnsigned
    logical_name: cst.LogicalName
    attribute_index: Integer
    data_index: LongUnsigned


PushObjectList = Array[ObjectDefinition]
"""push_object_list attribute"""


class TransportServiceType(Enum):  # TODO: elements 200.. is manufacturer specific
    """transport_service_type"""
    TCP: Final = 0
    UDP: Final = 1
    FTP: Final = 2
    SMTP: Final = 3
    SMS: Final = 4
    HDLC: Final = 5
    M_BUS: Final = 6
    ZIG_BEE: Final = 7


class MessageType(Enum):  # TODO: elements 128.. is manufacturer specific
    """message_type"""
    A_XDR_ENCODED_XDLMS_APDU = 2
    XML_ENCODED_XDLMS_APDU = 3


class SendDestinationAndMethod(Structure):
    """send_destination_and_method"""
    transport_service: TransportServiceType
    destination: OctetString
    message: MessageType


CommunicationWindow = Array[structs.WindowElement]
"""communication_window attribute"""


class PushSetup(ICAuto):
    """5.4.9 Push Setup"""
    CLASS_ID = 40
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "push_object_list", PushObjectList),
        ICAElement(3, "send_destination_and_method", SendDestinationAndMethod),
        ICAElement(4, "communication_window", CommunicationWindow),
        ICAElement(5, "randomisation_start_interval", LongUnsigned),
        ICAElement(6, "number_of_retries", Unsigned),
        ICAElement(7, "repetition_delay", LongUnsigned)
    )
    M_ELEMENTS = (ICMElement(1, "push", integers.IntegerValue0),)
    push_object_list: Attr
    send_destination_and_method: Attr
    communication_window: Attr
    randomisation_start_interval: Attr
    number_of_retries: Attr
    repetition_delay: Attr

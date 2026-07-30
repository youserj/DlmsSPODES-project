from typing import Final
from dataclasses import dataclass
from COSEMpdu.data import Array, Integer, Structure, LongUnsigned, OctetString, Enum, DoubleLongUnsigned, DateTime
from . import ver1
from ...types.type_alias import Attr
from ...types import cst
from ...types.implementations import integers, long_unsigneds
from ..cosem_interface_class import ICAElement, ICMElement, Classifier, update_collection


@dataclass
class PushObjectDefinition(Structure):
    """push_object_definition"""
    class_id: long_unsigneds.ClassId
    logical_name: cst.LogicalName
    attribute_index: Integer
    data_index: LongUnsigned
    restriction: ver1.RestrictionElement
    column: ver1.PushObjectDefinition


PushObjectList = Array[PushObjectDefinition]
"""push_object_list attribute"""


class MessageType(Enum):  # TODO: elements 128.. is manufacturer specific
    """message_type"""
    A_XDR_ENCODED_XDLMS_APDU: Final = 0
    XML_ENCODED_XDLMS_APDU: Final = 1


@dataclass
class SendDestinationAndMethod(Structure):
    """send_destination_and_method"""
    transport_service: ver1.TransportServiceType
    destination: OctetString
    message: MessageType


@dataclass
class RepetitionDelay(Structure):
    """repetition_delay"""
    repetition_delay_min: LongUnsigned
    repetition_delay_exponent: LongUnsigned
    repetition_delay_max: LongUnsigned


class PushOperationMethod(Enum):
    """push_operation_method enum"""
    UNCONFIRMED_RETRY_ON_SUPPORTING_PROTOCOL_LAYER_FAILURE = 0
    UNCONFIRMED_RETRY_ON_MISSING_SUPPORTING_PROTOCOL_LAYER_CONFIRMATION = 1
    CONFIRMED = 2


@dataclass
class ConfirmationParameters(Structure):
    confirmation_start_date: DateTime
    confirmation_interval: DoubleLongUnsigned


class PushSetup(ver1.PushSetup):
    """4.4.8.2 Push setup"""
    VERSION = 2
    A_ELEMENTS = update_collection(
        ver1.PushSetup.A_ELEMENTS,
        ICAElement(2, "push_object_list", PushObjectList),
        ICAElement(3, "send_destination_and_method", SendDestinationAndMethod),
        ICAElement(7, "repetition_delay", RepetitionDelay),
        ICAElement(11, "push_operation_method", PushOperationMethod),
        ICAElement(12, "confirmation_parameters", ConfirmationParameters),
        ICAElement(13, "last_confirmation_date_time", DateTime, classifier=Classifier.DYNAMIC))
    M_ELEMENTS = update_collection(
        ver1.PushSetup.M_ELEMENTS,
        ICMElement(2, "reset", integers.IntegerValue0))
    push_operation_method: Attr
    confirmation_parameters: Attr
    last_confirmation_date_time: Attr

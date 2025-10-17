from typing import Optional
from ...types import cdt, cst
from ...types.implementations import structs, enums, integers
from itertools import chain
from ...types import choices
from ..cosem_interface_class import ICAElement, ICMElement, Classifier, ICAuto
from ..Overview import class_id


class RestrictionElement(choices.StructureMixin, cdt.Structure):
    """restriction_element"""
    restriction_type: enums.RestrictionType
    restriction_value: choices.restriction_value


class ColumnElement(cdt.Array):
    """column_element"""
    TYPE = structs.CaptureObjectDefinition


class PushObjectDefinition(cdt.Structure):
    """push_object_definition"""
    class_id: cdt.LongUnsigned
    logical_name: cst.LogicalName
    attribute_index: cdt.Integer
    data_index: cdt.LongUnsigned
    restriction: RestrictionElement
    column: ColumnElement


class PushObjectList(cdt.Array):
    """push_object_list attribute"""
    TYPE = PushObjectDefinition


class TransportServiceType(cdt.Enum, elements=tuple(chain(range(9), range(200, 256)))):  # TODO: elements 200.. is manufacturer specific
    """transport_service_type"""


class MessageType(cdt.Enum, elements=tuple(chain((0, 1), range(128, 256)))):  # TODO: elements 128.. is manufacturer specific
    """message_type"""


class SendDestinationAndMethod(cdt.Structure):
    """send_destination_and_method"""
    transport_service: TransportServiceType
    destination: cdt.OctetString
    message: MessageType


class CommunicationWindow(cdt.Array):
    """communication_window attribute"""
    TYPE = structs.WindowElement


class RepetitionDelay(cdt.Structure):
    """repetition_delay"""
    repetition_delay_min: cdt.LongUnsigned
    repetition_delay_exponent: cdt.LongUnsigned
    repetition_delay_max: cdt.LongUnsigned


class PushOperationMethod(cdt.Enum, elements=(0, 1, 2)):
    """"""


class ConfirmationParameters(cdt.Structure):
    confirmation_start_date: cdt.DateTime
    confirmation_interval: cdt.DoubleLongUnsigned


class KeyInfoElement(choices.StructureMixin, cdt.Structure):
    """Override several methods of cdt.Structure. It limited Structure."""
    key_info_type: enums.KeyInfoType
    key_info_options: choices.KeyInfoOptions


class ProtectionOptions(cdt.Structure):
    transaction_id: cdt.OctetString
    originator_system_title: cdt.OctetString
    recipient_system_title: cdt.OctetString
    other_information: cdt.OctetString
    key_info: KeyInfoElement


class ProtectionParametersElement(cdt.Structure):
    protection_type: enums.ProtectionType
    protection_options: ProtectionOptions


class PushProtectionParameters(cdt.Array):
    TYPE = ProtectionParametersElement


class PushSetup(ICAuto):
    """4.4.8.2 Push setup"""
    CLASS_ID = class_id.PUSH_SETUP
    VERSION = 2
    A_ELEMENTS = (ICAElement(2, "push_object_list", PushObjectList),
                  ICAElement(3, "send_destination_and_method", SendDestinationAndMethod),
                  ICAElement(4, "communication_window", CommunicationWindow),
                  ICAElement(5, "randomisation_start_interval", cdt.LongUnsigned),
                  ICAElement(6, "number_of_retries", cdt.Unsigned),
                  ICAElement(7, "repetition_delay", RepetitionDelay),
                  ICAElement(8, "port_reference", cst.LogicalName),
                  ICAElement(9, "push_client_sap", cdt.Integer),
                  ICAElement(10, "push_protection_parameters", PushProtectionParameters),
                  ICAElement(11, "push_operation_method", PushOperationMethod),
                  ICAElement(12, "confirmation_parameters", ConfirmationParameters),
                  ICAElement(13, "last_confirmation_date_time", cdt.DateTime, classifier=Classifier.DYNAMIC))
    M_ELEMENTS = (ICMElement(1, "push", integers.Only0),
                  ICMElement(2, "reset", integers.Only0))
    push_object_list: Optional[PushObjectList]
    send_destination_and_method: Optional[SendDestinationAndMethod]
    communication_window: Optional[CommunicationWindow]
    randomisation_start_interval: Optional[cdt.LongUnsigned]
    number_of_retries: Optional[cdt.Unsigned]
    repetition_delay: Optional[RepetitionDelay]
    port_reference: Optional[cst.LogicalName]
    push_client_SAP: Optional[cdt.Integer]
    push_protection_parameters: Optional[PushProtectionParameters]
    push_operation_method: Optional[PushOperationMethod]
    confirmation_parameters: Optional[ConfirmationParameters]
    last_confirmation_date_time: Optional[cdt.DateTime]

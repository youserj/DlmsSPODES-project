from ..__class_init__ import *
from ...types.implementations import structs, enums, integers
from itertools import chain
from ...types import choices


class RestrictionElement(choices.StructureMixin, cdt.Structure):
    """Override several methods of cdt.Structure. It limited Structure."""
    restriction_type: enums.RestrictionType
    restriction_value: choices.restriction_value


class ColumnElement(cdt.Array):
    """ Specifies the list of capture objects """
    TYPE = structs.CaptureObjectDefinition


class PushObjectDefinition(cdt.Structure):
    class_id: cdt.LongUnsigned
    logical_name: cst.LogicalName
    attribute_index: cdt.Integer
    data_index: cdt.LongUnsigned
    restriction: RestrictionElement
    column: ColumnElement


class PushObjectList(cdt.Array):
    """ Defines the list of attributes to be pushed. """
    TYPE = PushObjectDefinition


class TransportServiceType(cdt.Enum, elements=tuple(chain(range(9), range(200, 256)))):  # TODO: elements 200.. is manufacturer specific
    """"""


class MessageType(cdt.Enum, elements=tuple(chain((0, 1), range(128, 256)))):  # TODO: elements 128.. is manufacturer specific
    """"""


class SendDestinationAndMethod(cdt.Structure):
    transport_service: TransportServiceType
    destination: cdt.OctetString
    message: MessageType


class CommunicationWindow(cdt.Array):
    """ Defines the time points when the communication window(s) for the push become(s) active (start_time) and inactive (end_time). """
    TYPE = structs.WindowElement


class RepetitionDelay(cdt.Structure):
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


class PushSetup(ic.COSEMInterfaceClasses):
    """ DLMS UA 1000-1 Ed. 14 4.4.8.2 Push setup"""
    CLASS_ID = ClassID.PUSH_SETUP
    VERSION = Version.V2
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
                  ic.ICAElement(an.LAST_CONFIRMATION_DATE_TIME, cdt.DateTime, classifier=ic.Classifier.DYNAMIC))
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

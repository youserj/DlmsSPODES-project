from typing import Final
from COSEMpdu.data import Array, Unsigned, LongUnsigned, Enum, Structure, Boolean
from ..cosem_interface_class import ICAuto, ICAElement, Classifier
from ...types.type_alias import Attr


class InitatorElectricalPhase(Enum):
    """attribute initiator_electrical_phase"""
    NOT_DEFINED: Final = 0
    PHASE_1: Final = 1
    PHASE_2: Final = 2
    PHASE_3: Final = 3


class DeltaElectricalPhase(Enum):
    """attribute delta_electrical_phase"""
    NOT_DEFINED: Final = 0
    SAME_PHASE: Final = 1
    DEGREE_60: Final = 2
    DEGREE_120: Final = 3
    DEGREE_180: Final = 4
    DEGREE_NEGATIVE_120: Final = 5
    DEGREE_NEGATIVE_60: Final = 6


class FrequenciesType(Structure):
    """frequencies_type"""
    mark_frequency: LongUnsigned
    space_frequency: LongUnsigned


class Repeater(Enum):
    """attribute repeater"""
    NEVER: Final = 0
    ALWAYS: Final = 1
    DYNAMIC: Final = 2


class SFSKPhyMACSetup(ICAuto):
    """5.10.1 S-FSK Phy&MAC setup"""
    CLASS_ID = 50
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "initiator_electrical_phase", InitatorElectricalPhase, classifier=Classifier.STATIC),
        ICAElement(3, "delta_electrical_phase", DeltaElectricalPhase, classifier=Classifier.DYNAMIC),
        ICAElement(4, "max_receiving_gain", Unsigned, classifier=Classifier.STATIC),
        ICAElement(5, "max_transmitting_gain", Unsigned, classifier=Classifier.STATIC),
        ICAElement(6, "search_initiator_gain", Unsigned, classifier=Classifier.STATIC),
        ICAElement(7, "frequencies", FrequenciesType, classifier=Classifier.STATIC),
        ICAElement(8, "mac_address", LongUnsigned, classifier=Classifier.DYNAMIC),
        ICAElement(9, "mac_group_addresses", Array[LongUnsigned], classifier=Classifier.STATIC),
        ICAElement(10, "repeater", Repeater, classifier=Classifier.STATIC),
        ICAElement(11, "repeater_status", Boolean, classifier=Classifier.DYNAMIC),
        ICAElement(12, "min_delta_credit", Unsigned, classifier=Classifier.DYNAMIC),
        ICAElement(13, "initiator_mac_address", LongUnsigned, classifier=Classifier.DYNAMIC),
        ICAElement(14, "synchronization_locked", Boolean, classifier=Classifier.DYNAMIC))
    initiator_electrical_phase: Attr
    delta_electrical_phase: Attr
    max_receiving_gain: Attr
    max_transmitting_gain: Attr
    search_initiator_gain: Attr
    frequencies: Attr
    mac_address: Attr
    mac_group_addresses: Attr
    repeater: Attr
    repeater_status: Attr
    min_delta_credit: Attr
    initiator_mac_address: Attr
    synchronization_locked: Attr

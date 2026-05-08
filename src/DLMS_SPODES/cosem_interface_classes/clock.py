from typing import Final
from COSEMpdu.data import Structure, Enum, Long, BitMixin, Integer, Boolean, DateTime
from ..types import cst
from ..types.implementations import integers
from ..types.type_alias import Attr
from .cosem_interface_class import ICAuto, ICAElement, ICMElement, Classifier


class ClockStatus(BitMixin, Enum):
    """clock_status"""
    INVALID_VALUE: Final = 0b1
    DOUBTFUL_VALUE: Final = 0b10
    DIFFERENT_CLOCK_BASE: Final = 0b100
    INVALID_CLOCK_STATUS: Final = 0b1000
    DAYLIGHT_SAVING_ACTIVE: Final = 0b100_0000


class ClockBase(Enum):
    """attribute clock_base"""
    NOT_DEFINED: Final = 0
    INTERNAL_CRYSTAL: Final = 1
    MAINS_FREQUENCY_50_HZ: Final = 2
    MAINS_FREQUENCY_60_HZ: Final = 3
    GPS_GLOBAL_POSITIONING_SYSTEM: Final = 4
    RADIO_CONTROLLED: Final = 5


class PresetAdjustingTime(Structure):
    """method preset_adjusting_time"""
    preset_time: DateTime
    validity_interval_start: DateTime
    validity_interval_end: DateTime


class ShiftTime(Long):
    """shift_time"""


class TimeZone(Long):
    """attribute time_zone"""


class Clock(ICAuto):
    """4.5.1 Clock"""
    CLASS_ID = 8
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "time", cst.OctetStringDateTime, classifier=Classifier.DYNAMIC),
        ICAElement(3, "time_zone", TimeZone, -720, 840),
        ICAElement(4, "status", ClockStatus, classifier=Classifier.DYNAMIC),
        ICAElement(5, "daylight_savings_begin", cst.OctetStringDateTime),
        ICAElement(6, "daylight_savings_end", cst.OctetStringDateTime),
        ICAElement(7, "daylight_savings_deviation", Integer, -120, 120),
        ICAElement(8, "daylight_savings_enabled", Boolean),
        ICAElement(9, "clock_base", ClockBase))
    M_ELEMENTS = (
        ICMElement(1, "adjust_to_quarter", integers.IntegerValue0),
        ICMElement(2, "adjust_to_measuring_period", integers.IntegerValue0),
        ICMElement(3, "adjust_to_minute", integers.IntegerValue0),
        ICMElement(4, "adjust_to_preset_time", integers.IntegerValue0),
        ICMElement(5, "preset_adjusting_time", PresetAdjustingTime),
        ICMElement(6, "shift_time", ShiftTime))
    time: Attr
    time_zone: Attr
    status: Attr
    daylight_savings_begin: Attr
    daylight_savings_end: Attr
    daylight_savings_deviation: Attr
    daylight_savings_enabled: Attr
    clock_base: Attr

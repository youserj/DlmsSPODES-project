from typing import Optional
from ..types import cdt, cst
from ..types.implementations import integers
from ..types.type_alias import Attr
from .Overview import class_id
from .cosem_interface_class import ICAuto, ICAElement, ICMElement, Classifier


class ClockStatus(cdt.Unsigned):
    """ interpreted as 8 bit string """

    # TODO: finish write as bit_string
    def __str__(self) -> str:
        value = int.from_bytes(self.contents, 'big')
        ret = ''
        if bool(value & 0b1):
            ret += ' invalid value'
        if bool(value & 0b10):
            ret += ' doubtful value'
        if bool(value & 0b100):
            ret += ' different clock base'
        if bool(value & 0b1000):
            ret += ' invalid clock status'
        if bool(value & 0b1000000):
            ret += ' daylight saving active'
        if ret == '':
            ret = 'empty'
        return ret


class DaylightSavingsDeviation(cdt.MaxDigital, cdt.MinDigital, cdt.Integer):
    """Contains the number of minutes by which the deviation in generalized time must be corrected at daylight savings begin.
    Deviation range of up to ± 120 min"""
    MIN = -120
    MAX = 120


class ClockBase(cdt.Enum, elements=(0, 1, 2, 3, 4, 5)):
    """ Defines where the basic timing information comes from. """


class PresetAdjustingTime(cdt.Structure):
    """ Presets the time to a new value (preset_time) and defines a validity_interval within which the new time can be activated """
    DEFAULT = b'\x02\x03\x19\x07\xe4\x01\x01\xff\xff\xff\xff\xff\x80\x00\xff' \
              b'\x19\x07\xe4\x01\x01\xff\xff\xff\xff\xff\x80\x00\xff\x19\x07\xe4\x01\x01\xff\xff\xff\xff\xff\x80\x00\xff'
    preset_time: cdt.DateTime
    validity_interval_start: cdt.DateTime
    validity_interval_end: cdt.DateTime


class ShiftTime(cdt.MinDigital, cdt.MaxDigital, cdt.Long):
    """ Limited Long -900..900 """
    MIN = -900
    MAX = 900


class TimeZone(cdt.Long):
    """"""


class Clock(ICAuto):
    """4.5.1 Clock"""
    CLASS_ID = class_id.CLOCK
    VERSION = 0
    A_ELEMENTS = (ICAElement(2, "time", cst.OctetStringDateTime, classifier=Classifier.DYNAMIC),
                  ICAElement(3, "time_zone", TimeZone, -720, 840),
                  ICAElement(4, "status", ClockStatus, classifier=Classifier.DYNAMIC),
                  ICAElement(5, "daylight_savings_begin", cst.OctetStringDateTime),
                  ICAElement(6, "daylight_savings_end", cst.OctetStringDateTime),
                  ICAElement(7, "daylight_savings_deviation", DaylightSavingsDeviation, -120, 120),
                  ICAElement(8, "daylight_savings_enabled", cdt.Boolean),
                  ICAElement(9, "clock_base", ClockBase))
    M_ELEMENTS = (ICMElement(1, "adjust_to_quarter", integers.Only0),
                  ICMElement(2, "adjust_to_measuring_period", integers.Only0),
                  ICMElement(3, "adjust_to_minute", integers.Only0),
                  ICMElement(4, "adjust_to_preset_time", integers.Only0),
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

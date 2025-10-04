import datetime
from .__class_init__ import *
from ..types.implementations import integers
from .overview import VERSION_0


class ClockStatus(cdt.Unsigned):
    """ interpreted as 8 bit string """

    # TODO: finish write as bit_string
    def __str__(self):
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


class DaylightSavingsDeviation(cdt.Integer, min=-120, max=120):
    """Contains the number of minutes by which the deviation in generalized time must be corrected at daylight savings begin.
    Deviation range of up to ± 120 min"""


class ClockBase(cdt.Enum, elements=(0, 1, 2, 3, 4, 5)):
    """ Defines where the basic timing information comes from. """


class PresetAdjustingTime(cdt.Structure):
    """ Presets the time to a new value (preset_time) and defines a validity_interval within which the new time can be activated """
    DEFAULT = b'\x02\x03\x19\x07\xe4\x01\x01\xff\xff\xff\xff\xff\x80\x00\xff' \
              b'\x19\x07\xe4\x01\x01\xff\xff\xff\xff\xff\x80\x00\xff\x19\x07\xe4\x01\x01\xff\xff\xff\xff\xff\x80\x00\xff'
    preset_time: cdt.DateTime
    validity_interval_start: cdt.DateTime
    validity_interval_end: cdt.DateTime


class ShiftTime(cdt.Long, min=-900, max=900):
    """ Limited Long -900..900 """


class TimeZone(cdt.Long):
    """"""


class Clock(ic.COSEMInterfaceClasses):
    """4.5.1 Clock"""
    CLASS_ID = ClassID.CLOCK
    VERSION = VERSION_0
    A_ELEMENTS = (ic.ICAElement("time", cst.OctetStringDateTime, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("time_zone", TimeZone, -720, 840),
                  ic.ICAElement("status", ClockStatus, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("daylight_savings_begin", cst.OctetStringDateTime),
                  ic.ICAElement("daylight_savings_end", cst.OctetStringDateTime),
                  ic.ICAElement("daylight_savings_deviation", DaylightSavingsDeviation, -120, 120),
                  ic.ICAElement("daylight_savings_enabled", cdt.Boolean),
                  ic.ICAElement("clock_base", ClockBase))
    M_ELEMENTS = (ic.ICMElement("adjust_to_quarter", integers.Only0),
                  ic.ICMElement("adjust_to_measuring_period", integers.Only0),
                  ic.ICMElement("adjust_to_minute", integers.Only0),
                  ic.ICMElement("adjust_to_preset_time", integers.Only0),
                  ic.ICMElement("preset_adjusting_time", PresetAdjustingTime),
                  ic.ICMElement("shift_time", ShiftTime))

    @property
    def time(self) -> cst.OctetStringDateTime:
        return self.get_attr(2)

    @property
    def time_zone(self) -> cdt.Long:
        return self.get_attr(3)

    @property
    def status(self) -> ClockStatus:
        return self.get_attr(4)

    @property
    def daylight_savings_begin(self) -> cst.OctetStringDateTime:
        return self.get_attr(5)

    @property
    def daylight_savings_end(self) -> cst.OctetStringDateTime:
        return self.get_attr(6)

    @property
    def daylight_savings_deviation(self) -> DaylightSavingsDeviation:
        return self.get_attr(7)

    @property
    def daylight_savings_enabled(self) -> cdt.Boolean:
        return self.get_attr(8)

    @property
    def clock_base(self) -> ClockBase:
        return self.get_attr(9)

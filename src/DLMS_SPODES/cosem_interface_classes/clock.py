from __future__ import annotations
import datetime
from .__class_init__ import *
from ..types.implementations import integers


class ClockStatus(cdt.Unsigned):
    """ interpreted as 8 bit string """
    NAME = F'{cdt.tn.UNSIGNED}(8bit string)'

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


class DaylightSavingsDeviation(cdt.Integer):
    """Contains the number of minutes by which the deviation in generalized time must be corrected at daylight savings begin.
    Deviation range of up to ± 120 min"""
    NAME = F'{cdt.tn.UNSIGNED}(-120..120)'

    def validate(self):
        if -120 > self.decode() or self.decode() > 120:
            raise ValueError(F'The deviation range out of range,  got {self.decode()} expected -120..120')


class ClockBase(cdt.Enum):
    """ Defines where the basic timing information comes from. """
    ELEMENTS = {b'\x00': en.NOT_DEFINED,
                b'\x01': en.INTERNAL_CRYSTAL,
                b'\x02': en.MAINS_FREQUENCY_50_HZ,
                b'\x03': en.MAINS_FREQUENCY_60_HZ,
                b'\x04': en.GPS_GLOBAL_POSITIONING_SYSTEM,
                b'\x05': en.RADIO_CONTROLLED}


class PresetAdjustingTime(cdt.Structure):
    """ Presets the time to a new value (preset_time) and defines a validity_interval within which the new time can be activated """
    values: tuple[cdt.DateTime, cdt.DateTime, cdt.DateTime]
    ELEMENTS: tuple[cdt.StructElement, cdt.StructElement, cdt.StructElement]
    default = b'\x02\x03\x19\x07\xe4\x01\x01\xff\xff\xff\xff\xff\x80\x00\xff' \
              b'\x19\x07\xe4\x01\x01\xff\xff\xff\xff\xff\x80\x00\xff\x19\x07\xe4\x01\x01\xff\xff\xff\xff\xff\x80\x00\xff'
    ELEMENTS = (cdt.StructElement(cdt.se.PRESET_TIME, cdt.DateTime),
                cdt.StructElement(cdt.se.VALIDITY_INTERVAL_START, cdt.DateTime),
                cdt.StructElement(cdt.se.VALIDITY_INTERVAL_END, cdt.DateTime))

    @property
    def preset_time(self) -> cdt.DateTime:
        return self.values[0]

    @property
    def validity_interval_start(self) -> cdt.DateTime:
        return self.values[1]

    @property
    def validity_interval_end(self) -> cdt.DateTime:
        return self.values[2]


class ShiftTime(cdt.Long):
    """ Limited Long -900..900 """
    NAME = F'{cdt.tn.UNSIGNED}(-900..900)'

    def validate(self):
        if self.decode() > 900 or self.decode() < -900:
            raise ValueError(F'The shift_time out of range, must be -900..900,  got {self.decode()}')


class Clock(ic.COSEMInterfaceClasses):
    """ An instance of the “Clock” interface class handles all information that is related to date and time, including leap years and the deviation of
    the local time to a generalized time reference (Greenwich Mean Time, GMT). The deviation from the local time to the generalized time reference can
    change depending on the season (e.g. summertime vs. wintertime). The interface to an external client is based on date information specified
    in day, month and year, time information given in hundredths of seconds, seconds, minutes and hours and the deviation from the local time to the
    generalized time reference.
    It also handles the daylight saving function in that way; i.e. it modifies the deviation of local time to GMT depending on the attributes.
    The start and end point of that function is normally set once. An internal algorithm calculates the real switch point depending on these settings. """
    NAME = cn.CLOCK
    CLASS_ID = ClassID.CLOCK
    VERSION = Version.V0
    A_ELEMENTS = (ic.ICAElement(an.TIME, cst.OctetStringDateTime),
                  ic.ICAElement(an.TIME_ZONE, cdt.Long, -720, 840),
                  ic.ICAElement(an.STATUS, ClockStatus),
                  ic.ICAElement(an.DAYLIGHT_SAVINGS_BEGIN, cst.OctetStringDateTime),
                  ic.ICAElement(an.DAYLIGHT_SAVINGS_END, cst.OctetStringDateTime),
                  ic.ICAElement(an.DAYLIGHT_SAVINGS_DEVIATION, DaylightSavingsDeviation, -120, 120),
                  ic.ICAElement(an.DAYLIGHT_SAVINGS_ENABLED, cdt.Boolean),
                  ic.ICAElement(an.CLOCK_BASE, ClockBase))
    M_ELEMENTS = (ic.ICMElement(mn.ADJUST_TO_QUARTER, integers.Only0),
                  ic.ICMElement(mn.ADJUST_TO_MEASURING_PERIOD, integers.Only0),
                  ic.ICMElement(mn.ADJUST_TO_MINUTE, integers.Only0),
                  ic.ICMElement(mn.ADJUST_TO_PRESET_TIME, integers.Only0),
                  ic.ICMElement(mn.PRESET_ADJUSTING_TIME, PresetAdjustingTime),
                  ic.ICMElement(mn.SHIFT_TIME, ShiftTime))

    def characteristics_init(self):
        self.cardinality = (0, 1)

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

    @property
    def adjust_to_quarter(self) -> integers.Only0:
        return self.get_meth(1)

    @property
    def adjust_to_measuring_period(self) -> integers.Only0:
        return self.get_meth(2)

    @property
    def adjust_to_minute(self) -> integers.Only0:
        return self.get_meth(3)

    @property
    def adjust_to_preset_time(self) -> integers.Only0:
        return self.get_meth(4)

    @property
    def preset_adjusting_time(self) -> PresetAdjustingTime:
        return self.get_meth(5)

    @property
    def shift_time(self) -> ShiftTime:
        return self.get_meth(6)

    def get_current_time(self) -> datetime.datetime:
        """ decided approximately server datetime without reading """
        try:
            record_time = self.get_record_time(2).decode()
        except AttributeError:
            raise AttributeError('Record time for Clock not found')
        TZ = datetime.timezone(datetime.datetime.now() - datetime.datetime.utcnow())
        delta = datetime.datetime.now(TZ) - record_time
        if self.time_zone is None:
            time_zone: datetime.timezone = self.time.time_zone
            if self.time.time_zone is None:
                raise ValueError('TimeZone not found in Clock object: time and timezone attributes')
        else:
            time_zone = datetime.timezone(datetime.timedelta(minutes=self.time_zone.decode()))
        return self.time.decode().replace(tzinfo=time_zone) + delta

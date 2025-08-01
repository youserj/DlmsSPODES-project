from dataclasses import dataclass
from typing import Self, Literal
from ..types import cst

SKIP = bytes(range(256))
RANGE64 = bytes(range(65))
type ObisGroup = int | set[int]
type GroupLiteral = Literal['a', 'b', 'c', 'd', 'e', 'f']


@dataclass
class LNPattern:
    """pattern for use in get_filtered.
    value "x.x.x.x.x.x" where x is:
    0..255 - simple value
    a,b,c,d,e,f - for skip value in each group
    (y, z, ...) - set of simple values(y or z)
    ((y-z), ...) - set of simple values with range(from y to z)
    !() - as () but, set of exclude values
    example: "a.0.(1,2,3).(0-64).0.f"
    """
    __values: tuple[bytes, ...]

    def __post_init__(self):
        if len(self.__values) != 6:
            raise ValueError(F"for {self.__class__.__name__} got values with length={len(self.__values)}, expected 6")

    @classmethod
    def parse(cls, value: str) -> Self:
        values: list[bytes] = [SKIP, SKIP, SKIP, SKIP, SKIP, SKIP]
        for i, val in enumerate(value.split('.', maxsplit=5)):
            if (
                len(val) == 1
                and (ord(val) == 97+i)
            ):
                if val == 'b':
                    values[i] = RANGE64
                else:
                    continue
            elif val.isdigit():
                values[i] = int(val)
                if not (0 <= values[i] <= 255):
                    raise ValueError(F"in {value=} got element {val=}, expected 0..255")
            elif val.startswith('(') and val.endswith(')'):
                el: set[int] = set()
                val = val.replace('(', "").replace(')', "")
                for j in val.split(","):
                    j = j.replace(" ", '')
                    match j.count('-'):
                        case 0:
                            el.add(cls.__simple_validate(j))
                        case 1:
                            start, end = j.split("-")
                            el.update(range(
                                cls.__simple_validate(start),
                                cls.__simple_validate(end)+1))
                        case err:
                            raise ValueError(F"got a lot of <-> in pattern: {value}, expected one")
                values[i] = bytes(el)
            elif val.startswith('!(') and val.endswith(')'):
                el: set[int] = set(range(256))
                val = val.replace('!(', "").replace(')', "")
                for j in val.split(","):
                    j = j.replace(" ", '')
                    match j.count('-'):
                        case 0:
                            el.discard(cls.__simple_validate(j))
                        case 1:
                            start, end = j.split("-")
                            el.difference_update(range(
                                cls.__simple_validate(start),
                                cls.__simple_validate(end)+1))
                        case err:
                            raise ValueError(F"got a lot of <-> in pattern: {value}, expected one")
                if len(el) == 0:
                    raise ValueError(F"no one element in group: {chr(97+i)}")
                values[i] = bytes(el)
            else:
                raise ValueError(F"got wrong symbol: {val} in pattern")
        return cls(tuple(values))

    @staticmethod
    def __simple_validate(value: str) -> int:
        if value.isdigit() and (0 <= (new := int(value)) <= 255):
            return new
        else:
            raise ValueError(F"got not valid element: {value} in pattern, expected 0..255")

    def get_update(self, group: GroupLiteral, value: str) -> Self:
        """get new instance with updated group value"""
        # todo: make this
        raise RuntimeError("no implement now")

    def __eq__(self, other: cst.LogicalName):
        for i, j in zip(self.__values, other):
            if i == j or (i == -1):
                continue
            elif isinstance(i, set) and j in i:
                continue
            else:
                return False
        return True

    def __repr__(self) -> str:
        return F"{self.__class__.__name__}(\"{".".join(map(lambda it: str(it) if isinstance(it, int) else str(tuple(it)), self.__values))}\")"

    def __hash__(self) -> int:
        return hash(self.__values)


@dataclass
class LNPatterns:
    value: tuple[LNPattern, ...]

    def __iter__(self):
        return iter(self.value)


ABSTRACT = LNPattern.parse("0")
ELECTRICITY = LNPattern.parse("1")
HCA = LNPattern.parse("4")
THERMAL = LNPattern.parse("(5,6)")
GAS = LNPattern.parse("7")
WATER = LNPattern.parse("(8,9)")
OTHER_MEDIA = LNPattern.parse("15")


BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES = LNPatterns((
    LNPattern.parse("0.b.0.1.(0,2,3,5).f"),
    LNPattern.parse("0.b.0.1.(1,4).255")))
PROGRAM_ENTRIES = LNPatterns((
    ACTIVE_FIRMWARE_IDENTIFIER := LNPattern.parse("0.b.0.2.0.255"),
    ACTIVE_FIRMWARE_VERSION := LNPattern.parse("0.b.0.2.1.255"),
    ACTIVE_FIRMWARE_SIGNATURE := LNPattern.parse("0.b.0.2.8.255")
))
TIME_ENTRIES = LNPattern.parse("0.b.0.9.(1,2).255")
CLOCK_OBJECTS = LNPatterns((
    CLOCK := LNPattern.parse("0.b.1.0.e.255"),
    UNIX_CLOCK := LNPattern.parse("0.b.1.1.e.255"),
    MICROSECONDS_CLOCK := LNPattern.parse("0.b.1.2.e.255"),
    MINUTES_CLOCK := LNPattern.parse("0.b.1.3.e.255"),
    HOURS_CLOCK := LNPattern.parse("0.b.1.4.e.255"),
    DAYS_CLOCK := LNPattern.parse("0.b.1.5.e.255"),
    WEEKS_CLOCK := LNPattern.parse("0.b.1.6.e.255")
))
TARIFFICATION_SCRIPT_TABLE = LNPattern.parse("0.b.10.0.100.255")
PUSH_SCRIPT_TABLE = LNPattern.parse("0.b.10.0.108.255")
SINGLE_ACTION_SCHEDULE = LNPatterns((
    END_OF_BILLING_PERIOD_SINGLE_ACTION_SCHEDULE := LNPattern.parse("0.b.15.0.0.255"),
    DISCONNECT_CONTROL_SINGLE_ACTION_SCHEDULE := LNPattern.parse("0.b.15.0.1.255"),
    IMAGE_ACTIVATION_SINGLE_ACTION_SCHEDULE := LNPattern.parse("0.b.15.0.2.255"),
    OUTPUT_CONTROL_SINGLE_ACTION_SCHEDULE := LNPattern.parse("0.b.15.0.3.255"),
    PUSH_SINGLE_ACTION_SCHEDULE := LNPattern.parse("0.b.15.0.4.255"),
    LOAD_PROFILE_CONTROL_SINGLE_ACTION_SCHEDULE := LNPattern.parse("0.b.15.0.5.255"),
    M_BUS_PROFILE_CONTROL_SINGLE_ACTION_SCHEDULE := LNPattern.parse("0.b.15.0.6.255"),
    FUNCTION_CONTROL_SINGLE_ACTION_SCHEDULE := LNPattern.parse("0.b.15.0.7.255")
))
ACTIVITY_CALENDAR = LNPattern.parse("0.b.13.0.e.255")
ASSOCIATION = LNPattern.parse("0.0.40.0.e.255")  # 6_2_33
NON_CURRENT_ASSOCIATION = LNPattern.parse("0.0.40.0.(1-255).255")  # MY
SAP_ASSIGNMENT = LNPattern.parse("0.0.41.0.0.255")  # 6.2.34
COSEM_logical_device_name = LNPattern.parse("0.0.42.0.0.255")  # 6.2.35
INFORMATION_SECURITY_RELATED = LNPatterns((
    LNPattern.parse("0.0.43.(0,2).e.255"),
    INVOCATION_COUNTER := LNPattern.parse("0.b.43.1.e.255")  # 6.2.36
))
IMAGE_TRANSFER = LNPattern.parse("0.b.44.0.e.255")  # 6.2.37
FUNCTION_CONTROL = LNPattern.parse("0.b.44.1.e.255")  # 6.2.38
COMMUNICATION_PORT_PROTECTION = LNPattern.parse("0.b.44.2.e.255")  # 6.2.39
UTILITY_TABLE = LNPattern.parse("0.b.65.(0-63).e.255")  # 6.2.40
COMPACT_DATA = LNPattern.parse("0.b.66.0.e.255")  # 6.2.41
DEVICE_ID = LNPattern.parse("0.b.96.1.(0,1,2,3,4,5,6,7,8,9,255).255")  # 6.2.42
METERING_POINT_ID = LNPattern.parse("0.b.96.1.10.255")  # 6.2.43
PARAMETER_CHANGES_CALIBRATION_AND_ACCESS = LNPattern.parse("0.b.96.2.e.f")  # 6.2.44
INPUT_OUTPUT_CONTROL_SIGNALS = LNPattern.parse("0.b.96.3.(0-4).f")  # 6.2.45
DISCONNECT_CONTROL = LNPattern.parse("0.b.96.3.10.f")  # 6.2.46
ARBITRATOR = LNPattern.parse("0.b.96.3.(20-29).f")  # 6.2.47
INTERNAL_CONTROL_SIGNALS = LNPattern.parse("0.b.96.4.(0-4).f")  # 6.2.48
INTERNAL_OPERATING_STATUS = LNPattern.parse("0.b.96.5.(0-4).f")  # 6.2.49
BATTERY_ENTRIES = LNPattern.parse("0.b.96.6.(0,1,2,3,4,5,6,10,11).f")  # 6.2.50
POWER_FAILURE_MONITORING = LNPattern.parse("0.b.96.7.(0-21).f")  # 6.2.51
OPERATING_TIME = LNPattern.parse("0.b.96.8.(0-63).f")
ENVIRONMENT_RELATED_PARAMETERS = LNPattern.parse("0.b.96.9.(0-2).f")
STATUS_REGISTER = LNPattern.parse("0.b.96.10.(1-10).f")
EVENT_CODE = LNPattern.parse("0.b.96.11.(0-99).f")
COMMUNICATION_PORT_LOG_PARAMETERS = LNPattern.parse("0.b.96.12.(0-6).f")
CONSUMER_MESSAGES = LNPattern.parse("0.b.96.13.(0,1).f")
CURRENTLY_ACTIVE_TARIFF = LNPattern.parse("0.b.96.14.(0-15).f")
EVENT_COUNTER = LNPattern.parse("0.b.96.15.(0-99).f")
PROFILE_ENTRY_DIGITAL_SIGNATURE = LNPattern.parse("0.b.96.16.(0-9).f")
PROFILE_ENTRY_COUNTER = LNPattern.parse("0.b.96.17.(0-127).f")
METER_TAMPER_EVENT_RELATED = LNPattern.parse("0.b.96.20.(0-34).f")
MANUFACTURER_SPECIFIC_ABSTRACT = LNPattern.parse("0.b.96.(50-99).e.f")

GENERAL_AND_SERVICE_ENTRY = LNPatterns((
    *BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES,
    *PROGRAM_ENTRIES,
    TIME_ENTRIES,
    DEVICE_ID,
    PARAMETER_CHANGES_CALIBRATION_AND_ACCESS,
    INPUT_OUTPUT_CONTROL_SIGNALS,
    INTERNAL_CONTROL_SIGNALS,
    INTERNAL_OPERATING_STATUS,
    BATTERY_ENTRIES,
    POWER_FAILURE_MONITORING,
    OPERATING_TIME,
    ENVIRONMENT_RELATED_PARAMETERS,
    STATUS_REGISTER,
    EVENT_CODE,
    COMMUNICATION_PORT_LOG_PARAMETERS,
    CONSUMER_MESSAGES,
    CURRENTLY_ACTIVE_TARIFF,
    EVENT_COUNTER,
    PROFILE_ENTRY_DIGITAL_SIGNATURE,
    PROFILE_ENTRY_COUNTER,
    METER_TAMPER_EVENT_RELATED,
    MANUFACTURER_SPECIFIC_ABSTRACT))
"""DLMS UA 1000-1 Ed. 14 7.4.1"""

LIMITER = LNPattern.parse("0.b.17.0.e.255")  # 6.2.15
ALARM_REGISTER = LNPattern.parse("0.b.97.98.(0-9).255")  # 6.2.64
COUNTRY_SPECIFIC_IDENTIFIERS = LNPattern.parse("0.b.94.d.e.f")  # 7.3.4.3
ALARM_REGISTER_FILTER = LNPattern.parse("0.b.97.98.(10-19).255")  # 6.2.64
ALARM_REGISTER_DESCRIPTOR = LNPattern.parse("0.b.97.98.(20-29).255")  # 6.2.64
ALARM_REGISTER_PROFILE = LNPattern.parse("0.b.97.98.255.255")  # 6.2.64
ALARM_REGISTER_TABLE = LNPattern.parse("0.b.97.98.255.255")  # 6.2.64
ALARM_REGISTER_FILTER_DESCRIPTOR = LNPatterns((ALARM_REGISTER, ALARM_REGISTER_FILTER, ALARM_REGISTER_DESCRIPTOR, ALARM_REGISTER_PROFILE))
# electricity
ID_NUMBERS_ELECTRICITY = LNPattern.parse("1.b.0.0.(0-9).255")
ELECTRIC_PROGRAM_ENTRIES = LNPattern.parse("1.b.0.2.e.255")
OUTPUT_PULSE_VALUES_OR_CONSTANTS = LNPattern.parse("1.0.0.3.(0-9).255")
RATIOS = LNPattern.parse("1.0.0.4.(0-7).255")
RECORDING_INTERVAL = LNPattern.parse("1.0.0.8.(4,5).255")
OTHER_ELECTRICITY_RELATED_GENERAL_PURPOSE = LNPattern.parse("1.b.0.(2,3,4,6,7,8,9,10).e.255")
# my special
COUNTRY_SPECIFIC = LNPattern.parse("a.b.94.d.e.f")  # 7.2.4 Table 54

# 7.5.2.1
INSTANTANEOUS_VALUE_EL_REL = LNPattern.parse("1.b.!(0,93,94,96,97,98,99).7.e.f")
ELECTRICITY_RELATED = LNPatterns((
    INSTANTANEOUS_VALUE_EL_REL,
    # todo: more other LNPatterns
))
"""7.5.2.1 Processing of measurement values Table 66"""

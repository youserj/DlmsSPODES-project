from dataclasses import dataclass
from ..types import common_data_types as cdt, cosem_service_types as cst, useful_types as ut


class LNPattern:
    """pattern for use in get_filtered.
    value "x.x.x.x.x.x" where x is:
    0..255 - simple value
    a,b,c,d,e,f - for skip value in each group
    (y, z, ...) - set of simple values(y or z)
    ((y-z), ...) - set of simple values with range(from y to z)
    example: "a.0.(1,2,3).(0-64).0.f"
    """
    __values: list[int, set[int]]

    def __init__(self, value: str):
        self.__values = [-1, -1, -1, -1, -1, -1]
        for i, val in enumerate(value.split('.', maxsplit=5)):
            if len(val) == 1 and (ord(val) == 97+i):
                continue
            elif val.isdigit():
                self.__values[i] = int(val)
                if not (0 <= self.__values[i] <= 255):
                    raise ValueError(F"in {value=} got element {val=}, expected 0..255")
            elif val.startswith('(') and val.endswith(')'):
                el: set[int] = set()
                val = val.replace('(', "").replace(')', "")
                for j in val.split(","):
                    j = j.replace(" ", '')
                    match j.count('-'):
                        case 0:
                            el.add(self.__simple_validate(j))
                        case 1:
                            start, end = j.split("-")
                            el.update(range(
                                self.__simple_validate(start),
                                self.__simple_validate(end)+1))
                        case err:
                            raise ValueError(F"got a lot of <-> in pattern: {value}, expected one")
                self.__values[i] = el
            else:
                raise ValueError(F"got wrong symbol: {val} in pattern")

    @staticmethod
    def __simple_validate(value: str) -> int:
        if value.isdigit() and (0 <= (new := int(value)) <= 255):
            return new
        else:
            raise ValueError(F"got not valid element: {value} in pattern, expected 0..255")

    def __eq__(self, other: cst.LogicalName):
        for i, j in zip(self.__values, other):
            if i == j or (i == -1):
                continue
            elif isinstance(i, set) and j in i:
                continue
            else:
                return False
        return True


@dataclass
class LNPatterns:
    value: tuple[LNPattern, ...]

    def __iter__(self):
        return iter(self.value)


ABSTRACT = LNPattern("0")
ELECTRICITY = LNPattern("1")
HCA = LNPattern("4")
THERMAL = LNPattern("(5,6)")
GAS = LNPattern("7")
WATER = LNPattern("(8,9)")
OTHER_MEDIA = LNPattern("15")


BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES = LNPatterns((
    LNPattern("0.b.0.1.(0,2,3,5).f"),
    LNPattern("0.b.0.1.(1,4).255")))
PROGRAM_ENTRIES = LNPattern("0.b.0.2.(0,1,8).255")
TIME_ENTRIES = LNPattern("0.b.0.9.(1,2).255")
ASSOCIATION_OBJECTS = LNPattern("0.0.40.0.e.255")  # 6_2_33
NON_CURRENT_ASSOCIATION = LNPattern("0.0.40.0.(1-255).255")  # MY
INVOCATION_COUNTER_OBJECTS = LNPattern("0.b.43.1.e.255")
DEVICE_IDS = LNPattern("0.b.96.1.(0-10).255")
PARAMETER_CHANGES_CALIBRATION_AND_ACCESS = LNPattern("0.b.96.2.(0,1,2,3,4,5,6,7,10,11,12,13).f")
INPUT_OUTPUT_CONTROL_SIGNALS = LNPattern("0.b.96.3.(0,1,2,3,4,10,20,21,22,23,24,25,26,27,28,29).f")
INTERNAL_CONTROL_SIGNALS = LNPattern("0.b.96.4.(0-4).f")
INTERNAL_OPERATING_STATUS = LNPattern("0.b.96.5.(0-4).f")
BATTERY_ENTRIES = LNPattern("0.b.96.6.(0,1,2,3,4,5,6,10,11).f")
POWER_FAILURE_MONITORING = LNPattern("0.b.96.7.(0-21).f")
OPERATING_TIME = LNPattern("0.b.96.8.(0-63).f")
ENVIRONMENT_RELATED_PARAMETERS = LNPattern("0.b.96.9.(0-2).f")
STATUS_REGISTER = LNPattern("0.b.96.10.(1-10).f")
EVENT_CODE = LNPattern("0.b.96.11.(0-99).f")
COMMUNICATION_PORT_LOG_PARAMETERS = LNPattern("0.b.96.12.(0-6).f")
CONSUMER_MESSAGES = LNPattern("0.b.96.13.(0,1).f")
CURRENTLY_ACTIVE_TARIFF = LNPattern("0.b.96.14.(0-15).f")
EVENT_COUNTER = LNPattern("0.b.96.15.(0-99).f")
PROFILE_ENTRY_DIGITAL_SIGNATURE_OBJECTS = LNPattern("0.b.96.16.(0-9).f")
PROFILE_ENTRY_COUNTER_OBJECTS = LNPattern("0.b.96.17.(0-127).f")
METER_TAMPER_EVENT_RELATED_OBJECTS = LNPattern("0.b.96.20.(0-34).f")
MANUFACTURER_SPECIFIC_ABSTRACT = LNPattern("0.b.96.(50-99).e.f")

GENERAL_AND_SERVICE_ENTRY_OBJECTS = LNPatterns((
    *BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES,
    PROGRAM_ENTRIES,
    TIME_ENTRIES,
    DEVICE_IDS,
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
    PROFILE_ENTRY_DIGITAL_SIGNATURE_OBJECTS,
    PROFILE_ENTRY_COUNTER_OBJECTS,
    METER_TAMPER_EVENT_RELATED_OBJECTS,
    MANUFACTURER_SPECIFIC_ABSTRACT))
"""DLMS UA 1000-1 Ed. 14 7.4.1"""

LIMITER_OBJECTS = LNPattern("0.b.17.0.e.255")  # 6.2.15
ALARM_REGISTER = LNPattern("0.b.97.98.(0-9).255")  # 6.2.64
ALARM_REGISTER_FILTER = LNPattern("0.b.97.98.(10-19).255")  # 6.2.64
ALARM_REGISTER_DESCRIPTOR = LNPattern("0.b.97.98.(20-29).255")  # 6.2.64
ALARM_REGISTER_PROFILE = LNPattern("0.b.97.98.255.255")  # 6.2.64
ALARM_REGISTER_TABLE = LNPattern("0.b.97.98.255.255")  # 6.2.64
ALARM_REGISTER_FILTER_DESCRIPTOR = LNPatterns((ALARM_REGISTER, ALARM_REGISTER_FILTER, ALARM_REGISTER_DESCRIPTOR, ALARM_REGISTER_PROFILE))
# electricity
ID_NUMBERS_ELECTRICITY = LNPattern("1.b.0.0.(0-9).255")
ELECTRIC_PROGRAM_ENTRIES = LNPattern("1.b.0.2.e.255")
OUTPUT_PULSE_VALUES_OR_CONSTANTS = LNPattern("1.0.0.3.(0-9).255")
RATIOS = LNPattern("1.0.0.4.(0-7).255")
RECORDING_INTERVAL = LNPattern("1.0.0.8.(4,5).255")
OTHER_ELECTRICITY_RELATED_GENERAL_PURPOSE_OBJECTS = LNPattern("1.b.0.(2,3,4,6,7,8,9,10).e.255")

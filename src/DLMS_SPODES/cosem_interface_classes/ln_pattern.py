from dataclasses import dataclass
from typing import Self, Literal
from ..types import cst
from copy import copy

SKIP: int = 0
RANGE256 = set(range(256))
RANGE64 = bytes(range(64))
RANGE64_WITH_LENGTH = b'\x40' + RANGE64


@dataclass(frozen=True, slots=True)
class LNPattern:
    """
    LNPattern ::= SEQUENCE (SIZE (6)) OF GroupPattern

    GroupPattern ::= CHOICE {
      skip        [0] NULL,               -- SKIP marker
      single      [1] INTEGER (0..255),   -- single value
      multiple   [2] SEQUENCE OF INTEGER (0..255)  -- set of values
    }
    LNPattern Binary Encoding Specification:
    ---------------------------------------
    A compact tag-less binary format for storing 6 OBIS-like groups.

    Structure:
      [L1][V1][L2][V2]...[L6][V6]
      where:
        - Ln: 1-byte length prefix for group n (0-255)
        - Vn: Value bytes (interpretation depends on Ln)

    Length Semantics:
      - L=0      : SKIP group (no value bytes follow)
      - L=1      : Single value (V is 1-byte integer 0-255)
      - L=2..255 : Value set (V contains L bytes as possible values)

    Special Cases:
      - Group 'b' (index 1) when marked SKIP uses predefined RANGE64 (0-64)
      - Empty exclusion sets "!()" are prohibited

    Example:
      Pattern "a.1.(2-5).!().0.f" encodes as:
      [00][01][01][04][02][03][04][05][00][01][00][00]
      (SKIP|1|{2,3,4,5}|SKIP|0|SKIP)

    Properties:
      - Fixed overhead: 6 bytes (1 length byte per group)
      - Max size: 6 + 255*6 = 1536 bytes
      - Order-preserving
      - Comparison-friendly memory layout
    """
    buffer: bytes

    @classmethod
    def parse(cls, value: str) -> Self:
        buffer = bytearray()
        parts = value.split('.', maxsplit=5)
        if len(parts) != 6:
            raise ValueError(f"got {len(parts)} elements, expected 6")
        for i, val in enumerate(parts):
            if val.isdigit():
                num = int(val)
                if 0 <= num <= 255:
                    buffer.extend((1, num))
                    continue
                raise ValueError(f"Value {val} out of range 0-255")
            if len(val) == 1:
                if val == "x":
                    buffer.append(SKIP)
                    continue
                elif (
                    i == 1
                    and val == "b"
                ):
                    buffer.extend(RANGE64_WITH_LENGTH)
                    continue
                elif ord(val) == i + 97:
                    buffer.append(SKIP)
                    continue
            if val == "":
                buffer.append(SKIP)
                continue
            if val[0]=='(' and val[-1]==')':
                el = set()
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
                                cls.__simple_validate(end) + 1))
                        case err:
                            raise ValueError(F"got a lot of <-> in pattern: {value}, expected one")
                # values = bytes(el)
                # buffer.extend([len(values)] + list(values))
                buffer.append(len(el))
                buffer.extend(el)
                continue
            if val.startswith('!(') and val.endswith(')'):
                el = copy(RANGE256)
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
                                cls.__simple_validate(end) + 1))
                        case err:
                            raise ValueError(F"got a lot of <-> in pattern: {value}, expected one")
                if len(el)==0:
                    raise ValueError(F"no one element in group: {chr(97 + i)}")
                # values = bytes(el)
                # buffer.extend([len(values)] + list(values))
                buffer.append(len(el))
                buffer.extend(el)
                continue
            raise ValueError(f"Invalid pattern: {val}")
        return cls(bytes(buffer))

    @staticmethod
    def __simple_validate(value: str) -> int:
        if value.isdigit() and (0 <= (new := int(value)) <= 255):
            return new
        else:
            raise ValueError(F"got not valid element: {value} in pattern, expected 0..255")

    def __eq__(self, other: "LNPattern") -> bool:
        ptr = 0
        for i in range(6):
            length = self.buffer[ptr]
            ptr += 1
            if length == 0:  # SKIP
                continue
            other_byte = other.contents[i]
            if length == 1:  # Single byte
                if self.buffer[ptr]!=other_byte:
                    return False
            else:  # Multiple bytes
                if other_byte not in self.buffer[ptr:ptr + length]:
                    return False
            ptr += length
        return True

    @staticmethod
    def _format_ranges(values: list[int]) -> str:
        if not values:
            return "!()"
        ranges = []
        start = end = values[0]
        for num in values[1:]:
            if num==end + 1:
                end = num
            else:
                ranges.append((start, end))
                start = end = num
        ranges.append((start, end))
        parts = []
        for start, end in ranges:
            if start==end:
                parts.append(str(start))
            elif end==start + 1:  # Диапазон из 2 чисел
                parts.extend([str(start), str(end)])
            else:
                parts.append(f"{start}-{end}")
        if len(parts) > 3 and len(values) > 128:  # Эмпирический порог
            all_values = set(range(256))
            excluded = sorted(all_values - set(values))
            if len(excluded) < len(values):
                return f"!({','.join(self._format_ranges(excluded))})"
        return f"({','.join(parts)})"

    def __str__(self) -> str:
        parts = []
        ptr = 0
        for _ in range(6):
            length = self.buffer[ptr]
            ptr += 1
            if length == 0:
                parts.append("x")
            elif length == 1:
                parts.append(str(self.buffer[ptr]))
            else:
                values = sorted(set(self.buffer[ptr:ptr + length]))
                parts.append(self._format_ranges(values))
            ptr += length
        return ".".join(parts)


@dataclass
class LNPatterns:
    value: tuple[LNPattern, ...]

    def __iter__(self):
        return iter(self.value)

    def __str__(self) -> str:
        return f"[{" | ".join(map(str, self.value))}]"


ABSTRACT = LNPattern.parse("0.....")
ELECTRICITY = LNPattern.parse("1.....")
HCA = LNPattern.parse("4.....")
THERMAL = LNPattern.parse("(5,6).....")
GAS = LNPattern.parse("7.....")
WATER = LNPattern.parse("(8,9).....")
OTHER_MEDIA = LNPattern.parse("15.....")


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

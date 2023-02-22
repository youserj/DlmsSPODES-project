""" The OBIS identification system serves as a basis for the COSEM logical names. The system of naming COSEM objects is defined in the basic
principles (see Clause 4 EN 62056-62:2007), the identification of real data items is specified in IEC 62056-61. The following clauses define the
usage of those definitions in the COSEM environment. All codes, which are not explicitly listed, but outside the manufacturer specific range are
reserved for future use."""
from __future__ import annotations
from functools import lru_cache
from . import settings
from .types import cosem_service_types as cst


match settings.get_current_language():
    case settings.Language.ENGLISH:     from .Values.EN import relation_to_obis_names as rn, class_names as cn
    case settings.Language.RUSSIAN:     from .Values.RU import relation_to_obis_names as rn, class_names as cn


def get_obj_names(electric_obj: int) -> str:
    """ corresponding with DLMS UA 1000-1 Ed. 14 7.5.1 Table 65. Value group C codes – Electricity. Range: 1..80, RU: 124..126 """
    match electric_obj:
        case 1 | 21 | 41 | 61:  return rn.ACTIVE_POWER_PLUS
        case 2 | 22 | 42 | 62:  return rn.ACTIVE_POWER_MINUS
        case 3 | 23 | 43 | 63:  return rn.REACTIVE_POWER_PLUS
        case 4 | 24 | 44 | 64:  return rn.REACTIVE_POWER_MINUS
        case 5 | 25 | 45 | 65:  return rn.REACTIVE_POWER_QI
        case 6 | 26 | 46 | 66:  return rn.REACTIVE_POWER_QII
        case 7 | 27 | 47 | 67:  return rn.REACTIVE_POWER_QIII
        case 8 | 28 | 48 | 68:  return rn.REACTIVE_POWER_QIV
        case 9 | 29 | 49 | 69:  return rn.APPARENT_POWER_PLUS
        case 10 | 30 | 50 | 70: return rn.APPARENT_POWER_MINUS
        case 11 | 31 | 51 | 71: return rn.CURRENT
        case 12 | 32 | 52 | 72: return rn.VOLTAGE
        case 13 | 33 | 53 | 73: return rn.POWER_FACTOR
        case 14 | 34 | 54 | 74: return rn.SUPPLY_FREQUENCY
        case 15 | 35 | 55 | 75: return rn.ACTIVE_POWER_ABS_PLUS
        case 16 | 36 | 56 | 76: return rn.ACTIVE_POWER_ABS_MINUS
        case 17 | 37 | 57 | 77: return rn.ACTIVE_POWER_QI
        case 18 | 38 | 58 | 78: return rn.ACTIVE_POWER_QII
        case 19 | 39 | 59 | 79: return rn.ACTIVE_POWER_QIII
        case 20 | 40 | 60 | 80:  return rn.ACTIVE_POWER_QIV
        case 88: return rn.CUMULATIVE_AMPERE_SQUARED_HOURS
        case 89: return rn.CUMULATIVE_VOLT_SQUARED_HOURS
        case 124: return F"{rn.RU_LINEAR_VOLTAGE} {rn.L1_L2}"
        case 125: return F"{rn.RU_LINEAR_VOLTAGE} {rn.L2_L3}"
        case 126: return F"{rn.RU_LINEAR_VOLTAGE} {rn.L3_L1}"
        case 128: return F"{rn.POWER_REACTIVE_FACTOR} {rn.L1}"
        case 129: return F"{rn.POWER_REACTIVE_FACTOR} {rn.L2}"
        case 130: return F"{rn.POWER_REACTIVE_FACTOR} {rn.L3}"
        case 131: return F"{rn.POWER_REACTIVE_FACTOR} {rn.ALL_PHASE}"
        case 133: return F"{rn.VOLTAGE_ASYMMETRY_COEFFICIENT}"
        case 147: return F"{rn.RU_TOTAL_DEVIATION_TIME} {rn.FOR} {rn.VOLTAGE}"
        case _:   raise ValueError(F"getting electrical name by C group with unknown: C={electric_obj}")


def get_harmonics_name(classification: int) -> str:
    """ See DLMS UA 1000-1 Ed.13 7.5.3.3 Harmonics """
    match classification:
        case 0:                               return rn.TOTAL_FUND_ALL
        case 124:                             return rn.THD
        case 125:                             return rn.TDD
        case 126:                             return rn.ALL_HARMONICS
        case 127:                             return rn.ALL_HARMONICS_TO_NOMINAL_VALUE_RATIO
        case _ if 120 >= classification >= 1: return F"{rn.HARMONIC} {classification}"
        case _: raise ValueError(F"for get harmonics unknown {classification=}")


def get_processing_names(d: int) -> str:
    match d:
        case 0: return rn.BILLING_PERIOD_AVERAGE_SINCE_LAST_RESET
        case 1: return rn.CUMULATIVE_MINIMUM_1
        case 2: return rn.CUMULATIVE_MAXIMUM_1
        case 3: return rn.MINIMUM_1
        case 4: return rn.CURRENT_AVERAGE_1
        case 5: return rn.LAST_AVERAGE_1
        case 6: return rn.MAXIMUM_1
        case 7: return rn.INSTANTANEOUS_VALUE
        case 8: return rn.TIME_INTEGRAL_1
        case 9: return rn.TIME_INTEGRAL_2
        case 10: return rn.TIME_INTEGRAL_3
        case 11: return rn.CUMULATIVE_MINIMUM_2
        case 12: return rn.CUMULATIVE_MAXIMUM_2
        case 13: return rn.MINIMUM_2
        case 14: return rn.CURRENT_AVERAGE_2
        case 15: return rn.LAST_AVERAGE_2
        case 16: return rn.MAXIMUM_2
        case 17: return rn.TIME_INTEGRAL_7
        case 18: return rn.TIME_INTEGRAL_8
        case 19: return rn.TIME_INTEGRAL_9
        case 20: return rn.TIME_INTEGRAL_10
        case 21: return rn.CUMULATIVE_MINIMUM_3
        case 22: return rn.CUMULATIVE_MAXIMUM_3
        case 23: return rn.MINIMUM_3
        case 24: return rn.CURRENT_AVERAGE_3
        case 25: return rn.LAST_AVERAGE_3
        case 26: return rn.MAXIMUM_3
        case 27: return rn.CURRENT_AVERAGE_5
        case 28: return rn.CURRENT_AVERAGE_6
        case 29: return rn.TIME_INTEGRAL_5
        case 30: return rn.TIME_INTEGRAL_6
        case 31: return rn.UNDER_LIMIT_THRESHOLD
        case 32: return rn.UNDER_LIMIT_OCCURRENCE_COUNTER
        case 33: return rn.UNDER_LIMIT_DURATION
        case 34: return rn.UNDER_LIMIT_MAGNITUDE
        case 35: return rn.OVER_LIMIT_THRESHOLD
        case 36: return rn.OVER_LIMIT_OCCURRENCE_COUNTER
        case 37: return rn.OVER_LIMIT_DURATION
        case 38: return rn.OVER_LIMIT_MAGNITUDE
        case 39: return rn.MISSING_THRESHOLD
        case 40: return rn.MISSING_OCCURRENCE_COUNTER
        case 41: return rn.MISSING_DURATION
        case 42: return rn.MISSING_MAGNITUDE
        case 43: return rn.TIME_THRESHOLD_FOR_UNDER_LIMIT
        case 44: return rn.TIME_THRESHOLD_FOR_OVER_LIMIT
        case 45: return rn.TIME_THRESHOLD_FOR_MISSING_MAGNITUDE
        case 46: return rn.CONTRACTED_VALUE
        case 49: return rn.AVERAGE_VALUE_FOR_RECORDING_INTERVAL_1
        case 50: return rn.AVERAGE_VALUE_FOR_RECORDING_INTERVAL_2
        case 51: return rn.MINIMUM_FOR_RECORDING_INTERVAL_1
        case 52: return rn.MINIMUM_FOR_RECORDING_INTERVAL_2
        case 53: return rn.MAXIMUM_FOR_RECORDING_INTERVAL_1
        case 54: return rn.MAXIMUM_FOR_RECORDING_INTERVAL_2
        case 55: return rn.TEST_AVERAGE
        case 56: return rn.CURRENT_AVERAGE_4_FOR_HARMONICS_MEASUREMENT
        case 58: return rn.TIME_INTEGRAL_4
        case 128: return rn.RU_POSITIVE_DEVIATION
        case 129: return rn.RU_NEGATIVE_DEVIATION
        case 133: return F"{rn.RU_TOTAL_DEVIATION_TIME} {rn.BILLING_PERIOD}"
        case 134: return rn.RU_CHANGE_LIMIT_LEVEL
        case _:  raise ValueError(F'Unknown Processing of measurement values {d}')


def get_rate(value: int) -> str:
    if value == 0:
        return rn.TOTAL
    elif value <= 63:
        return F", {rn.RATE} {value}"
    elif value <= 254:
        return F", {rn.MANUFACTURER_SPECIFIC} {value}"
    elif value == 255:
        return F", {rn.RESERVED}"
    else:
        raise ValueError(F"got group E: {value}, expect 0..255")


def handle_B(value: int) -> str:
    if value == 0:
        return ""
    elif value <= 64:
        return F", {rn.CHANNEL} {value}"
    elif value <= 127:
        return F", {rn.UTILITY_SPECIFIC} {value}"
    elif value <= 199:
        return F", {rn.MANUFACTURER_SPECIFIC} {value}"
    elif value <= 255:
        return F", {rn.RESERVED} {value}"
    else:
        raise ValueError(F"got group B: {value}, expect 0..255")


def handle_E(value: int) -> str:
    if value == 0:
        return ""
    elif value <= 127:
        return F", {rn.INSTANCE} {value}"
    elif value <= 255:
        return F", {rn.MANUFACTURER_SPECIFIC} {value}"
    else:
        raise ValueError(F"got group E: {value}, expect 0..255")


@lru_cache(maxsize=256)
def get_name(logical_name: cst.LogicalName) -> str:
    match logical_name:
        case cst.LogicalName(0, b, 0, 2, 0):    return F"{rn.ACTIVE_FIRMWARE_IDENTIFIER}{handle_B(b)}"
        case cst.LogicalName(0, b, 0, 2, 0):    return F"{rn.ACTIVE_FIRMWARE_IDENTIFIER}{handle_B(b)}"
        case cst.LogicalName(0, b, 0, 2, 1):    return F"{rn.ACTIVE_FIRMWARE_VERSION}{handle_B(b)}"
        case cst.LogicalName(0, b, 0, 2, 8):    return F"{rn.ACTIVE_FIRMWARE_SIGNATURE}{handle_B(b)}"
        case cst.LogicalName(0, b, 1, 0, e):    return F"{cn.CLOCK}{handle_B(b)}{handle_E(e)}"
        case cst.LogicalName(0, b, 2, 0, e):    return F"{cn.MODEM_CONFIGURATION}{handle_B(b)}{handle_E(e)}"
        case cst.LogicalName(0, b, 10, 0, 0):   return F"{rn.GLOBAL_METER_RESET_SCRIPT_TABLE}{handle_B(b)}"
        case cst.LogicalName(0, b, 10, 0, 1):   return F"{rn.MDI_RESET_END_OF_BILLING_PERIOD_SCRIPT_TABLE}{handle_B(b)}"
        case cst.LogicalName(0, b, 10, 0, 100): return F"{rn.TARIFFICATION_SCRIPT_TABLE}{handle_B(b)}"
        case cst.LogicalName(0, b, 10, 0, 103): return F"{rn.SET_OUTPUT_SIGNALS_SCRIPT_TABLE}{handle_B(b)}"
        case cst.LogicalName(0, b, 10, 0, 106): return F"{rn.DISCONNECT_CONTROL_SCRIPT_TABLE}{handle_B(b)}"
        case cst.LogicalName(0, b, 10, 0, 107): return F"{rn.IMAGE_ACTIVATION_SCRIPT_TABLE}{handle_B(b)}"
        case cst.LogicalName(0, b, 10, 0, 108): return F"{rn.PUSH_SCRIPT_TABLE}{handle_B(b)}"
        case cst.LogicalName(0, b, 10, 0, 128): return F"{rn.RU_STOP_FRAME_SCRIPT_TABLE}{handle_B(b)}"
        case cst.LogicalName(0, b, 11, 0, e):   return F"{cn.SPECIAL_DAYS_TABLE}{handle_B(b)}{handle_E(e)}"
        case cst.LogicalName(0, b, 12, 0, e):   return F"{cn.SCHEDULE}{handle_B(b)}{handle_E(e)}"
        case cst.LogicalName(0, b, 13, 0, e):   return F"{cn.ACTIVITY_CALENDAR}{handle_B(b)}{handle_E(e)}"
        case cst.LogicalName(0, b, 15, 0, 0):   return F"{rn.END_OF_BILLING_PERIOD_SINGLE_ACTION_SCHEDULE}{handle_B(b)}"
        case cst.LogicalName(0, b, 15, 0, 1):   return F"{rn.DISCONNECT_CONTROL_SINGLE_ACTION_SCHEDULE}{handle_B(b)}"
        case cst.LogicalName(0, b, 15, 0, 2):   return F"{rn.IMAGE_ACTIVATION_SINGLE_ACTION_SCHEDULE}{handle_B(b)}"
        case cst.LogicalName(0, b, 15, 0, 3):   return F"{rn.OUTPUT_CONTROL_SINGLE_ACTION_SCHEDULE}{handle_B(b)}"
        case cst.LogicalName(0, b, 15, 0, 4):   return F"{rn.PUSH_SINGLE_ACTION_SCHEDULE}{handle_B(b)}"
        case cst.LogicalName(0, b, 15, 0, 5):   return F"{rn.LOAD_PROFILE_CONTROL_SINGLE_ACTION_SCHEDULE}{handle_B(b)}"
        case cst.LogicalName(0, b, 15, 0, 6):   return F"{rn.M_BUS_PROFILE_CONTROL_SINGLE_ACTION_SCHEDULE}{handle_B(b)}"
        case cst.LogicalName(0, b, 15, 0, 7):   return F"{rn.FUNCTION_CONTROL_SINGLE_ACTION_SCHEDULE}{handle_B(b)}"
        case cst.LogicalName(0, b, 16, 1, 1):   return F"{rn.RU_ALARM_MONITOR_1}{handle_B(b)}"
        case cst.LogicalName(0, b, 17, 0, 0):   return F"{rn.RU_LIMITER_BY_POWER}{handle_B(b)}"
        case cst.LogicalName(0, b, 17, 0, 1):   return F"{rn.RU_LIMITER_BY_CURRENT}{handle_B(b)}"
        case cst.LogicalName(0, b, 17, 0, 2):   return F"{rn.RU_LIMITER_BY_VOLTAGE}{handle_B(b)}"
        case cst.LogicalName(0, b, 17, 0, 3):   return F"{rn.RU_LIMITER_BY_MAGNETIC}{handle_B(b)}"
        case cst.LogicalName(0, b, 17, 0, 4):   return F"{rn.RU_LIMITER_BY_DIFFERENCE_CURRENT}{handle_B(b)}"
        case cst.LogicalName(0, b, 17, 0, 5):   return F"{rn.RU_LIMITER_BY_TEMPERATURE}{handle_B(b)}"
        case cst.LogicalName(0, b, 17, 0, e):   return F"{cn.LIMITER}{handle_B(b)}{handle_E(e)}"
        case cst.LogicalName(0, 0, 21, 0, 1):   return rn.GENERAL_DISPLAY_READOUT
        case cst.LogicalName(0, 0, 21, 0, 2):   return rn.ALTERNATE_DISPLAY_READOUT
        case cst.LogicalName(0, 0, 22, 0, 0):   return rn.RU_IEC_HDLC_SETUP_OPTO
        case cst.LogicalName(0, 1, 22, 0, 0):   return rn.RU_IEC_HDLC_SETUP_RS_485
        case cst.LogicalName(0, 2, 22, 0, 0):   return rn.RU_IEC_HDLC_SETUP_GSM
        case cst.LogicalName(0, b, 22, 0, 0):   return F"{cn.IEC_HDLC_SETUP}{handle_B(b)}"
        case cst.LogicalName(0, b, 25, 0, 0):   return F"{cn.TCP_UDP_SETUP}{handle_B(b)}"
        case cst.LogicalName(0, b, 25, 1, 0):   return F"{cn.IPV4_SETUP}{handle_B(b)}"
        case cst.LogicalName(0, b, 25, 4, 0):   return F"{cn.GPRS_MODEM_SETUP}{handle_B(b)}"
        case cst.LogicalName(0, b, 25, 6, 0):   return F"{cn.GSM_DIAGNOSTIC}{handle_B(b)}"
        case cst.LogicalName(0, b, 25, 9, 0):   return F"{cn.PUSH_SETUP}{handle_B(b)}"
        case cst.LogicalName(0, 0, 40, 0, 0):   return rn.CURRENT_ASSOCIATION
        case cst.LogicalName(0, 0, 40, 0, 1):   return rn.RU_PUBLIC_CLIENT_ASSOCIATION
        case cst.LogicalName(0, 0, 40, 0, 2):   return rn.RU_METER_READER_ASSOCIATION
        case cst.LogicalName(0, 0, 40, 0, 3):   return rn.RU_UTILITY_SETTING_ASSOCIATION
        case cst.LogicalName(0, 0, 40, 0, 4):   return rn.RU_PUBLIC_CLIENT_ASSOCIATION
        case cst.LogicalName(0, 0, 40, 0, e):   return F"{cn.ASSOCIATION_LN}{handle_E(e)}"
        case cst.LogicalName(0, 0, 42, 0, 0):   return rn.COSEM_LOGICAL_DEVICE_NAME
        case cst.LogicalName(0, 0, 43, 0, e):   return F"{cn.SECURITY_SETUP}{handle_E(e)}"
        case cst.LogicalName(0, b, 43, 1, e):   return F"{rn.INVOCATION_COUNTER}{handle_B(b)}{handle_E(e)}"
        case cst.LogicalName(0, 0, 44, 0, e):   return F"{cn.IMAGE_TRANSFER}{handle_E(e)}"
        case cst.LogicalName(0, 0, 94, 7, 1):   return rn.RU_SPECIFIC_PASSPORT_DATA_PROFILE
        case cst.LogicalName(0, b, 96, 1, 0):   return F"{rn.RU_DEVICE_FACTORY_NUMBER}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 1, 1):   return F"{rn.RU_DEVICE_TYPE}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 1, 2):   return F"{rn.RU_DEVICE_METROLOGICAL_VERSION}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 1, 3):   return F"{rn.RU_PRODUCER_NAME}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 1, 4):   return F"{rn.RU_DEVICE_RELEASE_DATE}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 1, 5):   return F"{rn.RU_REMOTE_CONSOLE_SERIAL_NUMBER}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 1, 6):   return F"{rn.RU_SPODES_VERSION}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 1, 7):   return F"{rn.RU_DEVICE_CONNECTION_SCHEME}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 1, 8):   return F"{rn.RU_DEVICE_NOT_METROLOGICAL_VERSION}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 1, 9):   return F"{rn.RU_DEVICE_ID}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 1, 10):  return F"{rn.RU_COUNTER_POINT_DATA}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 2, 0):   return F"{rn.NUMBER_OF_CONFIGURATION_PROGRAM_CHANGES}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 2, 1):   return F"{rn.DATE_A_OF_LAST_CONFIGURATION_PROGRAM_CHANGE}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 2, 2):   return F"{rn.DATE_A_OF_LAST_TIME_SWITCH_PROGRAM_CHANGE}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 2, 3):   return F"{rn.DATE_A_OF_LAST_RIPPLE_CONTROL_RECEIVER_PROGRAM_CHANGE}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 2, 4):   return F"{rn.STATUS_OF_SECURITY_SWITCHES}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 2, 5):   return F"{rn.DATE_A_OF_LAST_CALIBRATION}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 2, 6):   return F"{rn.DATE_A_OF_NEXT_CONFIGURATION_PROGRAM_CHANGE}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 2, 7):   return F"{rn.DATE_A_OF_ACTIVATION_OF_THE_PASSIVE_CALENDAR}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 2, 10):   return F"{rn.NUMBER_OF_PROTECTED_CONFIGURATION_PROGRAM_CHANGES}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 2, 11):   return F"{rn.DATE_A_OF_LAST_PROTECTED_CONFIGURATION_PROGRAM_CHANGE}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 2, 12):   return F"{rn.DATE_A_CORRECTED_OF_LAST_CLOCK_SYNCHRONIZATION_SETTING}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 2, 13):   return F"{rn.DATE_OF_LAST_FIRMWARE_ACTIVATION}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 3, 0):   return F"{rn.I_O_CONTROL_SIGNAL_OBJECTS_GLOBAL}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 3, 10):  return F"{cn.DISCONNECT_CONTROL}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 3, 20):  return F"{rn.RU_RELAY_LOAD_ARBITRATOR}{handle_B(b)}"
        case cst.LogicalName(0, 0, 96, 4, 1):   return rn.RU_LCD_BACKLIGHT_MODE
        case cst.LogicalName(0, 0, 96, 4, 3):   return rn.RU_LOAD_LOCK_STATUS
        case cst.LogicalName(0, 0, 96, 5, 0):   return rn.INTERNAL_OPERATING_STATUS_GLOBAL
        case cst.LogicalName(0, 0, 96, 5, 1):   return rn.INTERNAL_OPERATING_STATUS_1
        case cst.LogicalName(0, 0, 96, 5, 2):   return rn.INTERNAL_OPERATING_STATUS_2
        case cst.LogicalName(0, 0, 96, 5, 3):   return rn.INTERNAL_OPERATING_STATUS_3
        case cst.LogicalName(0, 0, 96, 5, 4):   return rn.INTERNAL_OPERATING_STATUS_4
        case cst.LogicalName(0, b, 96, 8, 0):   return F"{rn.TIME_OF_OPERATION}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 8, 10):  return F"{rn.RU_DURATION_OF_FAILURE_OVERSTRAIN}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 9, 0):   return F"{rn.RU_AMBIENT_TEMPERATURE}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 11, 0):  return F"{rn.EVENTS_RELATED_TO_VOLTAGE}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 11, 1):  return F"{rn.RU_EVENTS_RELATED_TO_CURRENT}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 11, 2):  return F"{rn.RU_EVENTS_RELATED_TO_LOAD_RELAY}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 11, 3):  return F"{rn.RU_EVENTS_FOR_PROGRAMMING_DEVICE_PARAMETERS}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 11, 4):  return F"{rn.RU_EXTERNAL_IMPACT_EVENTS}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 11, 5):  return F"{rn.RU_COMMUNICATION_EVENTS}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 11, 6):  return F"{rn.RU_ACCESS_CONTROL_EVENTS}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 11, 7):  return F"{rn.RU_EVENT_CODES_FOR_THE_SELF_DIAGNOSIS_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 11, 8):  return F"{rn.RU_EVENTS_FOR_EXCEEDING_THE_REACTIVE_POWER}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 12, 4):  return F"{rn.RU_CHANNEL_NUMBER_INTERFACE}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 12, 6):  return F"{rn.COMMUNICATION_ADDRESS}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 13, 0):  return F"{rn.LOCAL_CONSUMER_MESSAGE}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 13, 1):  return F"{rn.DISPLAY_CONSUMER_MESSAGE}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 15, 0):  return F"{rn.RU_RELAY_TRIGGERING_METER_FOR_OPENING}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 0):  return F"{rn.METER_OPEN_EVENT_COUNTER}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 1):  return F"{rn.METER_OPEN_EVENT_TIME_STAMP}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 2):  return F"{rn.METER_OPEN_EVENT_DURATION}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 3):  return F"{rn.METER_OPEN_EVENT_CUMULATIVE_DURATION}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 5):  return F"{rn.TERMINAL_COVER_OPEN_EVENT_COUNTER}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 6):  return F"{rn.TERMINAL_COVER_OPEN_EVENT_TIME_STAMP}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 7):  return F"{rn.TERMINAL_COVER_OPEN_EVENT_DURATION}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 8):  return F"{rn.TERMINAL_COVER_OPEN_EVENT_CUMULATIVE}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 10):  return F"{rn.TILT_EVENT_COUNTER}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 11):  return F"{rn.TILT_EVENT_TIME_STAMP}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 12):  return F"{rn.TILT_EVENT_DURATION}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 13):  return F"{rn.TILT_EVENT_CUMULATIVE_DURATION}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 15):  return F"{rn.STRONG_DC_MAGNETIC_FIELD_EVENT_COUNTER}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 16):  return F"{rn.STRONG_DC_MAGNETIC_FIELD_EVENT_TIME_STAMP}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 17):  return F"{rn.STRONG_DC_MAGNETIC_FIELD_EVENT_DURATION}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 18):  return F"{rn.STRONG_DC_MAGNETIC_FIELD_EVENT_CUMULATIVE_DURATION}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 20):  return F"{rn.SUPPLY_CONTROL_SWITCH_VALVE_TAMPER_EVENT_COUNTER}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 21):  return F"{rn.SUPPLY_CONTROL_SWITCH_VALVE_TAMPER_EVENT_TIME_STAMP}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 22):  return F"{rn.SUPPLY_CONTROL_SWITCH_VALVE_TAMPER_EVENT_DURATION}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 23):  return F"{rn.SUPPLY_CONTROL_SWITCH_VALVE_TAMPER_EVENT_CUMULATIVE_DURATION}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 25):  return F"{rn.METROLOGY_TAMPER_EVENT_COUNTER}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 26):  return F"{rn.METROLOGY_TAMPER_EVENT_TIME_STAMP}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 27):  return F"{rn.METROLOGY_TAMPER_EVENT_DURATION}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 28):  return F"{rn.METROLOGY_TAMPER_EVENT_CUMULATIVE_DURATION}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 30):  return F"{rn.COMMUNICATION_TAMPER_EVENT_COUNTER}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 31):  return F"{rn.COMMUNICATION_TAMPER_EVENT_TIME_STAMP}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 32):  return F"{rn.COMMUNICATION_TAMPER_EVENT_DURATION}{handle_B(b)}"
        case cst.LogicalName(0, b, 96, 20, 33):  return F"{rn.COMMUNICATION_TAMPER_EVENT_CUMULATIVE_DURATION}{handle_B(b)}"
        case cst.LogicalName(0, 0, 96, 51, 0):  return rn.RU_BODY_OPENING_STATE
        case cst.LogicalName(0, 0, 96, 51, 1):  return rn.RU_TERMINALS_COVER_OPENING_STATE
        case cst.LogicalName(0, 0, 96, 51, 3):  return rn.RU_MAGNETIC_FIELD_STATE
        case cst.LogicalName(0, 0, 96, 51, 4):  return rn.RU_HF_FIELD_STATE
        case cst.LogicalName(0, 0, 96, 51, 5):  return rn.RU_ELECTRONIC_SEALS_FIXED_STATE_OF_EVENTS
        case cst.LogicalName(0, 0, 96, 51, 6):  return rn.RU_PRESSING_ELECTRONIC_SEALS
        case cst.LogicalName(0, 0, 96, 51, 7):  return rn.RU_CLEAR_OF_ELECTRONIC_SEALS_FIXED_STATE
        case cst.LogicalName(0, 0, 96, 51, 8):  return rn.RU_FIRST_OPENING_TIME_OF_BODY
        case cst.LogicalName(0, 0, 96, 51, 9):  return rn.RU_FIRST_OPENING_TIME_OF_TERMINALS_COVER
        case cst.LogicalName(0, 0, 97, 98, 0):  return rn.RU_ALARM_REGISTER_1
        case cst.LogicalName(0, 0, 97, 98, 1):  return rn.RU_ALARM_REGISTER_2
        case cst.LogicalName(0, 0, 97, 98, 10):  return rn.RU_ALARM_FILTER_1
        case cst.LogicalName(0, 0, 97, 98, 11):  return rn.RU_ALARM_FILTER_2
        case cst.LogicalName(0, b, 99, 1, e):   return F"{rn.LOAD_PARAMETERS_PROFILE}{handle_B(b)}{handle_E(e)}"
        case cst.LogicalName(0, b, 99, 13, e):  return F"{rn.GSM_DIAGNOSTIC_PROFILE}{handle_B(b)}{handle_E(e)}"
        case cst.LogicalName(0, b, 99, 98, 0):  return F"{rn.RU_VOLTAGE_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 1):  return F"{rn.RU_CURRENT_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 2):  return F"{rn.RU_COMMUTATION_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 3):  return F"{rn.RU_DATA_CORRECTION_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 4):  return F"{rn.RU_EXTERNAL_IMPACT_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 5):  return F"{rn.RU_COMMUNICATION_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 6):  return F"{rn.RU_ACCESS_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 7):  return F"{rn.RU_SELF_DIAGNOSTIC_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 8):  return F"{rn.RU_REACTIVE_POWER_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 9):  return F"{rn.RU_QUALITY_POWER_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 10): return F"{rn.RU_STATUS_I_O_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 12): return F"{rn.RU_REACTIVE_POWER_LIMIT_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 13): return F"{rn.RU_TIME_CORRECTION_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 14): return F"{rn.RU_START_YEAR_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 15): return F"{rn.RU_QUALITY_FOR_CALCULATION_PERIOD_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 16): return F"{rn.RU_CONTROL_POWER_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 17): return F"{rn.RU_BATTERY_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 18): return F"{rn.RU_CONTROL_OF_LOAD_RELAY_BLOCKER_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 19): return F"{rn.RU_TEMPERATURE_CONTROL_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 20): return F"{rn.RU_VOLTAGE_DEVIATION_LOG} {rn.L1}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 21): return F"{rn.RU_VOLTAGE_DEVIATION_LOG} {rn.L2}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 22): return F"{rn.RU_VOLTAGE_DEVIATION_LOG} {rn.L3}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 23): return F"{rn.RU_LINEAR_VOLTAGE_DEVIATION_LOG} {rn.L1_L2}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 24): return F"{rn.RU_LINEAR_VOLTAGE_DEVIATION_LOG} {rn.L2_L3}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 25): return F"{rn.RU_LINEAR_VOLTAGE_DEVIATION_LOG} {rn.L3_L1}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 26): return F"{rn.RU_OVER_VOLTAGE_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 27): return F"{rn.RU_VOLTAGE_INTERRUPTION_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, 28): return F"{rn.RU_ABNORMAL_NETWORK_SITUATION_LOG}{handle_B(b)}"
        case cst.LogicalName(0, b, 99, 98, e):  return F"{cn.PROFILE_GENERIC}{handle_B(b)}{handle_E(e)}"
        case cst.LogicalName(0, 0, 128, 100, 0):   return rn.ITE_FIRMWARE_DESCRIPTOR
        case cst.LogicalName(0, 0, 128, 101, 0):   return rn.ITE_MAGNETIC_SENSOR_STATUS
        case cst.LogicalName(0, 0, 128, 102, 0):   return rn.ITE_DISCRETE_OUTPUTS
        case cst.LogicalName(0, 0, 128, 103, 0):   return rn.ITE_SETTING_OF_RELAY_INCLUSION_PER_DAY
        case cst.LogicalName(0, 0, 128, 150, 0):   return rn.ITE_SETTINGS_MESSAGES
        case cst.LogicalName(0, 0, 128, 151, 0):   return rn.ITE_CORE_REGISTERS
        case cst.LogicalName(0, 0, 128, 152, 0):   return rn.ITE_BLE_ID
        case cst.LogicalName(0, 0, 128, 170, 0):   return rn.ITE_ICCID
        case cst.LogicalName(0, 0, 199, 255, 255): return cn.CLIENT_SETUP
        case cst.LogicalName(1, b, 0, 0, e):    return F"{F'{rn.COMPLETE_COMBINED_ELECTRICITY_ID} {e+1}'}{handle_B(b)}"
        case cst.LogicalName(1, b, 0, 2, 0):    return F"{rn.ACTIVE_FIRMWARE_IDENTIFIER}{handle_B(b)}"
        case cst.LogicalName(1, b, 0, 2, 8):    return F"{rn.ACTIVE_FIRMWARE_SIGNATURE}{handle_B(b)}"
        case cst.LogicalName(1, b, 0, 3, 3):    return F"{rn.ACTIVE_ENERGY_OUTPUT_PULSE}{handle_B(b)}"
        case cst.LogicalName(1, b, 0, 3, 4):    return F"{rn.REACTIVE_ENERGY_OUTPUT_PULSE}{handle_B(b)}"
        case cst.LogicalName(1, b, 0, 4, 2):    return F"{rn.TRANSFORMER_RATIO_CURRENT}{handle_B(b)}"
        case cst.LogicalName(1, b, 0, 4, 3):    return F"{rn.TRANSFORMER_RATIO_VOLTAGE}{handle_B(b)}"
        # Nominal values
        case cst.LogicalName(1, b, 0, 6, 0):    return F"{rn.NOMINAL_VOLTAGE}{handle_B(b)}"
        case cst.LogicalName(1, b, 0, 6, 1):    return F"{rn.NOMINAL_CURRENT}{handle_B(b)}"
        case cst.LogicalName(1, b, 0, 6, 2):    return F"{rn.NOMINAL_FREQUENCY}{handle_B(b)}"
        case cst.LogicalName(1, b, 0, 6, 3):    return F"{rn.MAXIMUM_CURRENT}{handle_B(b)}"
        case cst.LogicalName(1, b, 0, 6, 4):    return rn.REFERENCE_VOLTAGE_FOR_POWER_QUALITY_MEASUREMENT
        case cst.LogicalName(1, b, 0, 6, 5):    return F"{rn.REFERENCED_VOLTAGE_FOR_AUX_POWER_SUPPLY}{handle_B(b)}"
        case cst.LogicalName(1, b, 0, 8, 4):    return F"{rn.RECORDING_INTERVAL_1_FOR_LOAD_PROFILE}{handle_B(b)}"
        case cst.LogicalName(1, b, 0, 8, 5):    return F"{rn.RECORDING_INTERVAL_2_FOR_LOAD_PROFILE}{handle_B(b)}"
        # Coefficients
        case cst.LogicalName(1, b, 0, 10, 0):    return F"{rn.TRANSFORMER_MAGNETIC_LOSSES}{handle_B(b)}"
        case cst.LogicalName(1, b, 0, 10, 1):    return F"{rn.TRANSFORMER_IRON_LOSSES}{handle_B(b)}"
        case cst.LogicalName(1, b, 0, 10, 2):    return F"{rn.LINE_RESISTANCE_LOSSES}{handle_B(b)}"
        case cst.LogicalName(1, b, 0, 10, 3):    return F"{rn.LINE_REACTANCE_LOSSES}{handle_B(b)}"
        case cst.LogicalName(1, b, 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 13 | 14 | 15 | 16 | 17 | 18 | 19 | 20 as c, d, e):
            return F"{handle_B(b)}{rn.CUMULATIVE} {get_obj_names(c)} {get_processing_names(d)} {get_rate(e)}"
        case cst.LogicalName(1, b, 11 | 12 as c, 7, e):
            return F"{handle_B(b)}{get_obj_names(c)} {get_harmonics_name(e)}"
        case cst.LogicalName(1, b, 11 | 12 as c, 134, 0):
            return F"{handle_B(b)}{get_obj_names(c)} {rn.RU_CHANGE_LIMIT_LEVEL}"
        case cst.LogicalName(1, b, 11 | 12 as c, d, e):
            return F"{handle_B(b)}{rn.ANY_PHASE} {get_obj_names(c)} {get_processing_names(d)} {get_harmonics_name(e)}"
        case cst.LogicalName(1, b, c, d, e) if c in range(21, 41):
            return F"{handle_B(b)}{rn.L1} {get_obj_names(c)} {get_processing_names(d)} {get_rate(e)}"
        case cst.LogicalName(1, b, c, d, e) if c in range(41, 61):
            return F"{handle_B(b)}{rn.L2} {get_obj_names(c)} {get_processing_names(d)} {get_rate(e)}"
        case cst.LogicalName(1, b, c, d, e) if c in range(61, 81):
            return F"{handle_B(b)}{rn.L3} {get_obj_names(c)} {get_processing_names(d)} {get_rate(e)}"
        case cst.LogicalName(1, b, 88 | 89 | 124 | 125 | 126 | 128 | 129 | 130 | 131 as c, d, e):
            return F"{handle_B(b)}{get_obj_names(c)} {get_processing_names(d)} {get_rate(e)}"
        case cst.LogicalName(1, b, 91, 7, 131):   return F"{rn.RU_DIFFERENTIAL_CURRENT}. {rn.INSTANTANEOUS_VALUE}{handle_B(b)}"
        case cst.LogicalName(1, b, 91, 7, 132):   return F"{rn.RU_DIFFERENTIAL_CURRENT}. {rn.PERCENT}. {rn.INSTANTANEOUS_VALUE}{handle_B(b)}"
        case cst.LogicalName(1, b, 91, d, e) if d <= 127:
            return F"{handle_B(b)}{rn.L0_CURRENT_NEUTRAL} {get_processing_names(d)} {get_harmonics_name(e)}"
        case cst.LogicalName(1, b, 137, d, 128):
            return F"{handle_B(b)}{rn.REACTIVE_FACTOR} {get_processing_names(d)}"
        case cst.LogicalName(1, 0, 147 as c, 133, 0): return F"{get_obj_names(c)} {rn.BILLING_PERIOD}"
        case cst.LogicalName(1, 0, 148, 36, 0): return F"{rn.OVER_VOLTAGE_COUNTER} {rn.BILLING_PERIOD}"
        case cst.LogicalName(1, b, 81, 7, e) if e < 78:
            angel_values = (rn.U_L1, rn.U_L2, rn.U_L3, rn.ERROR, rn.I_L1, rn.I_L2, rn.I_L3, rn.I_L0)
            to_, from_ = divmod(logical_name.e, 10)
            return F"{F'{rn.ANGLE_FROM} {angel_values[from_]} {rn.TO} {angel_values[to_]}'}{handle_B(b)}"
        case cst.LogicalName(1, b, 94, 7, 0):   return F"{rn.RU_PROFILE_OF_CURRENT_VALUES}{handle_B(b)}"
        case cst.LogicalName(1, b, 94, 7, 1):   return F"{rn.RU_SCALE_PROFILE_FOR_THE_MAGAZINE_OF_MONTHLY_INDICATIONS}{handle_B(b)}"
        case cst.LogicalName(1, b, 94, 7, 2):   return F"{rn.RU_SCALE_PROFILE_FOR_A_JOURNAL_OF_DAILY_INDICATION}{handle_B(b)}"
        case cst.LogicalName(1, b, 94, 7, 3):   return F"{rn.RU_SCALE_PROFILE_FOR_CURRENT_FRAMES_OF_CURRENT_VALUES}{handle_B(b)}"
        case cst.LogicalName(1, b, 94, 7, 4):   return F"{rn.RU_SCALE_PROFILE_FOR_LOAD_PROFILES}{handle_B(b)}"
        case cst.LogicalName(1, b, 94, 7, 5):   return F"{rn.RU_TELEMECHANICS_PROFILE_FOR_TELEVISION_MEASUREMENTS}{handle_B(b)}"
        case cst.LogicalName(1, b, 94, 7, 6):   return F"{rn.RU_TELEMECHANICS_PROFILE_OF_TELEVISION_SIGNALING}{handle_B(b)}"
        case cst.LogicalName(1, b, 94, 7, e):      return F"{F'{rn.COUNTRY_SPECIFIC_IDENTIFIER} #{e+1}'}{handle_B(b)}"
        case cst.LogicalName(1, b, 98, 1, e):      return F"{rn.RU_MONTHLY_PROFILE}{handle_B(b)}{handle_E(e)}"
        case cst.LogicalName(1, b, 98, 2, e):      return F"{rn.RU_DAILY_PROFILE}{handle_B(b)}{handle_E(e)}"
        case cst.LogicalName(1, b, 99, 1, e):      return F"{rn.RU_LOAD_PROFILE}{handle_B(b)}{handle_E(e)}"
        case cst.LogicalName(1, b, 99, 2, e):      return F"{rn.RU_LOAD_PROFILE} #2{handle_B(b)}{handle_E(e)}"
        case cst.LogicalName(128, 0, 0, 0, 0):     return rn.ITE_CALIBRATION_STATUS
        case cst.LogicalName(128, 0, 1, 0, 0):     return rn.ITE_CALIBRATION_APPARENT_POWER
        case cst.LogicalName(128, 0, 2, 0, 0):     return rn.ITE_CALIBRATION_ACTIVE_POWER
        case cst.LogicalName(128, 0, 3, 0, 0):     return rn.ITE_CALIBRATION_REACTIVE_POWER
        case cst.LogicalName(128, 0, 4, 0, 0):     return rn.ITE_CALIBRATION_VOLTAGE
        case cst.LogicalName(128, 0, 5, 0, 0):     return rn.ITE_CALIBRATION_CURRENT
        case cst.LogicalName(128, 0, 6, 0, 0):     return rn.ITE_CALIBRATION_ANGLE
        case cst.LogicalName(128, 0, 7, 0, 0):     return rn.ITE_DISPLAY_SETTING_1
        case cst.LogicalName(128, 0, 8, 0, 0):     return rn.ITE_DISPLAY_SETTING_2
        case cst.LogicalName(128, 0, 9, 0, 0):     return rn.ITE_CLOCK_OFFSET_SETTING
        case cst.LogicalName(128, 0, 10, 0, 0):     return rn.ITE_FACTORY_SETTING_10
        case cst.LogicalName(128, 0, 11, 0, 0):     return rn.ITE_FACTORY_SETTING_11
        case cst.LogicalName(128, 0, 12, 0, 0):     return rn.ITE_FACTORY_SETTING_12
        case cst.LogicalName(128, 0, 13, 0, 0):     return rn.ITE_FACTORY_SETTING_13
        case cst.LogicalName(128, 0, 14, 0, 0):     return rn.ITE_FACTORY_SETTING_14
        case cst.LogicalName(128, 0, 15, 0, 0):     return rn.ITE_FACTORY_SETTING_15
        case cst.LogicalName(128, 0, 16, 0, 0):     return rn.ITE_FACTORY_SETTING_16
        case cst.LogicalName(128, 0, 17, 0, 0):     return rn.ITE_FACTORY_SETTING_17
        case cst.LogicalName(128, 0, 18, 0, 0):     return rn.ITE_FACTORY_SETTING_18
        case cst.LogicalName(128, 0, 19, 0, 0):     return rn.ITE_FACTORY_SETTING_19
        case _:                                    return rn.UNKNOWN
    """ return name by according logical name """

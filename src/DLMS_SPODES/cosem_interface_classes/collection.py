""" The OBIS identification system serves as a basis for the COSEM logical names. The system of naming COSEM objects is defined in the basic
principles (see Clause 4 EN 62056-62:2007), the identification of real data items is specified in IEC 62056-61. The following clauses define the
usage of those definitions in the COSEM environment. All codes, which are not explicitly listed, but outside the manufacturer specific range are
reserved for future use."""
from __future__ import annotations
import os
import copy
from struct import pack
import datetime
from dataclasses import dataclass
from itertools import count, chain
from functools import reduce, cached_property, lru_cache
from typing import TypeAlias, Iterator, Type, Self, Callable, Literal, Iterable
import logging
from ..version import AppVersion
from ..types import common_data_types as cdt, cosem_service_types as cst, useful_types as ut
from ..types.implementations import structs, enums, octet_string
from . import cosem_interface_class as ic
from .ln_pattern import LNPattern, LNPatterns
from .activity_calendar import ActivityCalendar
from .arbitrator import Arbitrator
from .association_ln import mechanism_id
from .association_sn.ver0 import AssociationSN as AssociationSNVer0
from .association_ln.ver0 import AssociationLN as AssociationLNVer0, ObjectListElement
from .association_ln.ver1 import AssociationLN as AssociationLNVer1
from .association_ln.ver2 import AssociationLN as AssociationLNVer2
from .push_setup.ver0 import PushSetup as PushSetupVer0
from .push_setup.ver1 import PushSetup as PushSetupVer1
from .push_setup.ver2 import PushSetup as PushSetupVer2
from .clock import Clock
from .data import Data
from .disconnect_control import DisconnectControl
from .gprs_modem_setup import GPRSModemSetup
from .gsm_diagnostic.ver0 import GSMDiagnostic as GSMDiagnosticVer0
from .gsm_diagnostic.ver1 import GSMDiagnostic as GSMDiagnosticVer1
from .gsm_diagnostic.ver2 import GSMDiagnostic as GSMDiagnosticVer2
from .iec_hdlc_setup.ver0 import IECHDLCSetup as IECHDLCSetupVer0
from .iec_hdlc_setup.ver1 import IECHDLCSetup as IECHDLCSetupVer1
from .image_transfer.ver0 import ImageTransfer
from .ipv4_setup import IPv4Setup
from .modem_configuration.ver0 import PSTNModemConfiguration
from .modem_configuration.ver1 import ModemConfigurationVer1
from .limiter import Limiter
from .ntp_setup.ver0 import NTPSetup
from .profile_generic.ver0 import ProfileGeneric as ProfileGenericVer0
from .profile_generic.ver1 import ProfileGeneric as ProfileGenericVer1
from .register import Register
from .extended_register import ExtendedRegister
from .demand_register.ver0 import DemandRegister as DemandRegisterVer0
from .register_activation.ver0 import RegisterActivation
from .register_monitor import RegisterMonitor
from .schedule import Schedule
from .security_setup.ver0 import SecuritySetup as SecuritySetupVer0
from .security_setup.ver1 import SecuritySetup as SecuritySetupVer1
from .script_table import ScriptTable
from .single_action_schedule import SingleActionSchedule
from .special_days_table import SpecialDaysTable
from .tcp_udp_setup import TCPUDPSetup
from .. import exceptions as exc
import xml.etree.ElementTree as ET
from xml.dom import minidom
from ..relation_to_OBIS import get_name
from ..cosem_interface_classes import implementations as impl
from ..cosem_interface_classes.overview import ClassID, Version, CountrySpecificIdentifiers
from ..enums import TagsName
from . import obis as o, ln_pattern
from .. import pdu_enums as pdu
from ..config_parser import config, get_values
from ..obis import media_id


_report = {
    "empty": "--",
    "empty_unit": "??",
}
if toml_val := get_values("DLMS", "report"):
    _report.update(toml_val)


LNContaining: TypeAlias = bytes | str | cst.LogicalName | cdt.Structure | ut.CosemObjectInstanceId | ut.CosemAttributeDescriptor | ut.CosemAttributeDescriptorWithSelection \
                          | ut.CosemMethodDescriptor

AssociationSN: TypeAlias = AssociationSNVer0
AssociationLN: TypeAlias = AssociationLNVer0 | AssociationLNVer1 | AssociationLNVer2
ModemConfiguration: TypeAlias = PSTNModemConfiguration | ModemConfigurationVer1
SecuritySetup: TypeAlias = SecuritySetupVer0 | SecuritySetupVer1
PushSetup: TypeAlias = PushSetupVer0 | PushSetupVer1 | PushSetupVer2
ProfileGeneric: TypeAlias = ProfileGenericVer1
DemandRegister: TypeAlias = DemandRegisterVer0
IECHDLCSetup: TypeAlias = IECHDLCSetupVer0 | IECHDLCSetupVer1
GSMDiagnostic: TypeAlias = GSMDiagnosticVer0 | GSMDiagnosticVer1 | GSMDiagnosticVer2
InterfaceClass: TypeAlias = Data | Register | ExtendedRegister | DemandRegister | ProfileGeneric | Clock | ScriptTable | Schedule | SpecialDaysTable | ActivityCalendar | \
                            SingleActionSchedule | AssociationLN | IECHDLCSetup | DisconnectControl | Limiter | ModemConfiguration | PSTNModemConfiguration | ImageTransfer | \
                            GPRSModemSetup | GSMDiagnostic | SecuritySetup | TCPUDPSetup | IPv4Setup | Arbitrator | RegisterMonitor | PushSetup | AssociationSN | \
                            NTPSetup


UsedAttributes: TypeAlias = dict[cst.LogicalName, set[int]]


ObjectTreeMode: TypeAlias = Literal["", "m", "g", "c", "mc", "cm", "gm", "gc", "cg", "gmc"]
SortMode: TypeAlias = Literal["l", "n", "c", "cl", "cn"]


class ClassMap(dict):
    def __hash__(self):
        return hash(tuple(it.hash_ for it in self.values()))


DataMap = ClassMap({
    0: Data})
DataStaticMap = ClassMap({
    0: impl.data.DataStatic})
DataDynamicMap = ClassMap({
    0: impl.data.DataDynamic})
RegisterMap = ClassMap({
    0: Register})
ExtendedRegisterMap = ClassMap({
    0: ExtendedRegister})
DemandRegisterMap = ClassMap({
    0: DemandRegisterVer0})
RegisterActivationMap = ClassMap({
    0: RegisterActivation})
ProfileGenericMap = ClassMap({
    0: ProfileGenericVer0,
    1: ProfileGenericVer1})
ClockMap = ClassMap({
    0: Clock})
ScriptTableMap = ClassMap({
    0: ScriptTable})
ScheduleMap = ClassMap({
    0: Schedule})
SpecialDaysTableMap = ClassMap({
    0: SpecialDaysTable
})
AssociationSNMap = ClassMap({
    0: AssociationSNVer0,
})
AssociationLNMap = ClassMap({
    0: AssociationLNVer0,
    1: AssociationLNVer1,
    2: AssociationLNVer2,
})
ImageTransferMap = ClassMap({
    0: ImageTransfer
})
ActivityCalendarMap = ClassMap({
    0: ActivityCalendar
})
RegisterMonitorMap = ClassMap({
    0: RegisterMonitor
})
SingleActionScheduleMap = ClassMap({
    0: SingleActionSchedule
})
IECHDLCSetupMap = ClassMap({
    0: IECHDLCSetupVer0,
    1: IECHDLCSetupVer1
})
ModemConfigurationMap = ClassMap({
    0: PSTNModemConfiguration,
    1: ModemConfigurationVer1
})
TCPUDPSetupMap = ClassMap({
    0: TCPUDPSetup
})
IPv4SetupMap = ClassMap({
    0: IPv4Setup
})
GPRSModemSetupMap = ClassMap({
    0: GPRSModemSetup
})
GSMDiagnosticMap = ClassMap({
    0: GSMDiagnosticVer0,
    1: GSMDiagnosticVer1,
    2: GSMDiagnosticVer2
})
PushSetupMap = ClassMap({
    0: PushSetupVer0,
    1: PushSetupVer1,
    2: PushSetupVer2,
})
SecuritySetupMap = ClassMap({
    0: SecuritySetupVer0,
    1: SecuritySetupVer1
})
ArbitratorMap = ClassMap({
    0: Arbitrator
})
DisconnectControlMap = ClassMap({
    0: DisconnectControl
})
LimiterMap = ClassMap({
    0: Limiter
})
NTPSetupMap = ClassMap({
    0: NTPSetup
})

# implementation ClassMap
UnsignedDataMap = ClassMap({
    0: impl.data.Unsigned
})

CosemClassMap: TypeAlias = DataMap | RegisterMap | ExtendedRegisterMap | DemandRegisterMap | ProfileGenericMap | ClockMap | ScriptTableMap | ScheduleMap | SpecialDaysTableMap | \
                           AssociationLNMap | ImageTransferMap | ActivityCalendarMap | RegisterMonitorMap | SingleActionScheduleMap | IECHDLCSetupMap | ModemConfigurationMap | \
                           TCPUDPSetupMap | IPv4SetupMap | GPRSModemSetupMap | GSMDiagnosticMap | SecuritySetupMap | ArbitratorMap | DisconnectControlMap | LimiterMap | \
                           NTPSetupMap


LN_C: TypeAlias = int
LN_D: TypeAlias = int


common_interface_class_map: dict[int, dict[[int, None], Type[InterfaceClass]]] = {
    1: DataMap,
    3: RegisterMap,
    4: ExtendedRegisterMap,
    5: DemandRegisterMap,
    6: RegisterActivationMap,
    7: ProfileGenericMap,
    8: ClockMap,
    9: ScriptTableMap,
    10: ScheduleMap,
    11: SpecialDaysTableMap,
    15: AssociationLNMap,
    18: ImageTransferMap,
    20: ActivityCalendarMap,
    21: RegisterMonitorMap,
    22: SingleActionScheduleMap,
    23: IECHDLCSetupMap,
    27: ModemConfigurationMap,
    41: TCPUDPSetupMap,
    42: IPv4SetupMap,
    45: GPRSModemSetupMap,
    47: GSMDiagnosticMap,
    64: SecuritySetupMap,
    68: ArbitratorMap,
    70: DisconnectControlMap,
    71: LimiterMap,
    100: NTPSetupMap,
}


def get_interface_class(class_map: dict[int, CosemClassMap], c_id: ut.CosemClassId, ver: cdt.Unsigned) -> Type[InterfaceClass]:
    """new version <get_type_from_class>"""
    ret = class_map.get(int(c_id), None)
    if ret:
        ret2 = ret.get(int(ver), None)
        """interface class type"""
        if ret2:
            return ret2
        else:
            raise ValueError(F"not valid {ver=} for {c_id=}")
    else:
        if int(c_id) not in common_interface_class_map.keys():
            raise ValueError(F"unknown {c_id=}")
        else:
            raise ValueError(F"got {c_id=}, expected {', '.join(map(str, class_map.keys()))}")


_CUMULATIVE = (1, 2, 11, 12, 21, 22)
_MAX_MIN_VALUES = (3, 6, 13, 16, 26, 51, 52, 53, 54)
_CURRENT_AND_LAST_AVERAGE_VALUES = (0, 4, 5, 14, 15, 24, 25, 27, 28, 49, 50, 55, 56)
_INSTANTANEOUS_VALUES = (7, 39, 41, 42)
_TIME_INTEGRAL_VALUES = (8, 9, 10, 17, 18, 19, 20, 29, 30, 58)
_OCCURRENCE_COUNTER = 40
_CONTRACTED_VALUES = (46,)
_UNDER_OVER_LIMIT_THRESHOLDS = (31, 35, 43, 44)
_UNDER_OVER_LIMIT_OCCURRENCE_COUNTERS = (32, 36)
_UNDER_OVER_LIMIT_DURATIONS = (33, 37)
_UNDER_OVER_LIMIT_MAGNITUDES = (34, 38)
_NOT_PROCESSING_OF_MEASUREMENT_VALUES = tuple(set(range(256)).difference((0, 93, 94, 96, 97, 98, 99)))  # BlueBook DLMS UA 1000-1 Ed.14 7.5.2.1 Table 66
_RU_CHANGE_LIMIT_LEVEL = 134

logger = logging.getLogger(__name__)
logger.level = logging.INFO


@dataclass(frozen=True)
class ObjectRelation:
    IC: int | tuple[int, ...] | ic.COSEMInterfaceClasses
    Additional: bytes | dict | bool = None


@lru_cache()
def _create_map(maps: CosemClassMap | tuple[CosemClassMap]) -> dict[int, CosemClassMap]:
    if isinstance(maps, tuple):
        return {int(map_[0].CLASS_ID): map_ for map_ in maps}
    else:
        return {int((tuple(maps.values())[0]).CLASS_ID): maps}


A: TypeAlias = int
B: TypeAlias = int
C: TypeAlias = int
D: TypeAlias = int
E: TypeAlias = int

FOR_C: TypeAlias = tuple[A, C]
FOR_CD: TypeAlias = tuple[A, C | tuple[C, ...], D] | tuple[A, tuple[C, ...], tuple[D, ...]]
FOR_CDE: TypeAlias = tuple[A, C, D | tuple[D, ...], E | tuple[E, ...]]
FOR_BCDE: TypeAlias = tuple[A, B, C, D, E | tuple[E, ...]]
FUNC_MAP: TypeAlias = dict[bytes, dict[int, CosemClassMap]]
"""ln.BCDE | ln.CDE | ln.CD | ln.C: {class_id: {version: CosemInterfaceClass}}"""


func_maps: dict[str, FUNC_MAP] = dict()


def get_func_map(for_create_map: dict) -> FUNC_MAP:
    ret: FUNC_MAP = dict()
    for it in for_create_map:
        keys: list[bytes] = list()
        match len(it):
            case 4:
                match it[2], it[3]:
                    case int(), tuple() as e_g:
                        for e in e_g:
                            keys.append(pack(">BBBB", it[0], it[1], it[2], e))
                    case tuple() as d_g, int():
                        for d in d_g:
                            keys.append(pack(">BBBB", it[0], it[1], d, it[3]))
                    case tuple() as d_g, tuple() as e_g:
                        for d in d_g:
                            for e in e_g:
                                keys.append(pack(">BBBB", it[0], it[1], d, e))
                    case int(), int():
                        keys.append(bytes(it))
                    case _:
                        raise ValueError(F"unknown {it[2]=} and {it[3]=} in dict values: {it}")
            case 3:
                match it[1], it[2]:
                    case int(), int():
                        keys.append(bytes(it))
                    case tuple() as c_g, int():
                        for c in c_g:
                            keys.append(pack(">BBB", it[0], c, it[2]))
                    case int(), tuple() as d_g:
                        for d in d_g:
                            keys.append(pack(">BBB", it[0], it[1], d))
                    case tuple() as c_g, tuple() as d_g:
                        for c in c_g:
                            for d in d_g:
                                keys.append(pack(">BBB", it[0], c, d))
                    case err:
                        raise ValueError(F"unknown {it[1]=} in dict values: {err}")
            case 5:
                match it[2], it[4]:
                    case int(), int():
                        keys.append(bytes(it))
                    case int(), tuple() as e_g:
                        for e in e_g:
                            keys.append(pack(">BBBBB", it[0], it[1], it[2], it[3], e))
                    case tuple() as c_g, int():
                        for c in c_g:
                            keys.append(pack(">BBBBB", it[0], it[1], c, it[3], it[4]))
                    case _:
                        raise ValueError(F"unknown dict values: {it}")
            case 2:
                keys.append(bytes(it))
            case err_len:
                raise ValueError(F"got {err_len=} map_for_create, expect 2..5")
        for k in keys:
            ret[k] = _create_map(for_create_map[it])
    return ret


__func_map_for_create: dict[FOR_C | FOR_CD | FOR_CDE | FOR_BCDE, tuple[CosemClassMap, ...] | CosemClassMap] = {
    # abstract
    (0, 0, 1): DataMap,
    (0, 0, 2): DataMap,
    (0, 0, 2, 1): ClassMap({0: impl.data.ActiveFirmwareId}),
    (0, 0, 9): DataMap,
    (0, 1, 0): ClockMap,
    (0, 1, 1): DataMap,
    (0, 1, 2): DataMap,
    (0, 1, 3): DataMap,
    (0, 1, 4): DataMap,
    (0, 1, 5): DataMap,
    (0, 1, 6): DataMap,
    (0, 2, 0, 0): ModemConfigurationMap,
    #
    (0, 10, 0, (0, 1, 125)+tuple(range(100, 112))): ScriptTableMap,
    (0, 11, 0): SpecialDaysTableMap,
    (0, 12, 0): ScheduleMap,
    (0, 13, 0): ActivityCalendarMap,
    (0, 14, 0): RegisterActivationMap,
    (0, 15, 0, tuple(range(0, 8))): SingleActionScheduleMap,
    (0, 16, 0): RegisterMonitorMap,
    (0, 16, 1, tuple(range(0, 10))): RegisterMonitorMap,
    #
    (0, 17, 0): LimiterMap,
    #
    (0, 19, tuple(range(50, 60)), (1, 2)): DataMap,
    #
    (0, 21, 0): (DataMap, ProfileGenericMap),
    (0, 22, 0, 0): IECHDLCSetupMap,
    #
    (0, 23, 2, 0): DataMap,
    (0, 23, 3, tuple(range(0, 10))): (DataMap, ProfileGenericMap),
    (0, 23, 3, tuple(range(10, 256))): DataMap,
    #
    (0, 24, 2): ExtendedRegisterMap,
    (0, 24, 3): ProfileGenericMap,
    (0, 24, 4, 0): DisconnectControlMap,
    (0, 24, 5, 0): ProfileGenericMap,
    #
    (0, 25, 0, 0): TCPUDPSetupMap,
    (0, 25, 1, 0): IPv4SetupMap,
    #
    (0, 25, 4, 0): GPRSModemSetupMap,
    #
    (0, 25, 6, 0): GSMDiagnosticMap,
    #
    (0, 25, 9, 0): PushSetupMap,
    (0, 25, 10, 0): NTPSetupMap,
    #
    (0, 0, 40, 0, tuple(range(8))): (AssociationSNMap, AssociationLNMap),  # todo: now limit by 8 association, solve it
    #
    (0, 0, 42, 0, 0): ClassMap({0: impl.data.LDN}),
    (0, 0, 43, 0, tuple(range(256))): SecuritySetupMap,
    (0, 43, 1): DataMap,
    #
    (0, 0, 44, 0, tuple(range(256))): ImageTransferMap,
    #
    (0, 96, 1, tuple(range(0, 11))): ClassMap({0: impl.data.DLMSDeviceIDObject}),
    (0, 96, 1, 255): ProfileGenericMap,  # todo: add RegisterTable
    (0, 96, 2): DataDynamicMap,
    (0, 96, 3, tuple(range(0, 4))): DataMap,  # todo: add StatusMapping
    (0, 96, 3, 10): DisconnectControlMap,
    (0, 96, 3, tuple(range(20, 29))): ArbitratorMap,
    (0, 96, (4, 5), 0): (DataMap, ProfileGenericMap),  # todo: add RegisterTable, StatusMapping
    (0, 96, (4, 5), (1, 2, 3, 4)): DataMap,  # todo: add StatusMapping
    (0, 96, 6, tuple(range(0, 7))): (DataMap, RegisterMap,  ExtendedRegisterMap),
    (0, 96, 7, tuple(range(0, 22))): (DataMap, RegisterMap,  ExtendedRegisterMap),
    (0, 96, 8, tuple(range(0, 64))): (DataMap, RegisterMap,  ExtendedRegisterMap),
    (0, 96, 9, (0, 1, 2)): (RegisterMap,  ExtendedRegisterMap),
    (0, 96, 10, tuple(range(1, 10))): DataMap,  # todo: add StatusMapping
    (0, 96, 11, tuple(range(100))): (DataDynamicMap, RegisterMap,  ExtendedRegisterMap),
    (0, 96, 12, (0, 1, 2, 3, 5, 6)): (DataMap, RegisterMap,  ExtendedRegisterMap),
    (0, 96, 12, 4): ClassMap({0: impl.data.CommunicationPortParameter}),
    (0, 96, 13, (0, 1)): (DataMap, RegisterMap,  ExtendedRegisterMap),
    (0, 96, 14, tuple(range(16))): (DataMap, RegisterMap,  ExtendedRegisterMap),
    (0, 96, 15, tuple(range(100))): (DataMap, RegisterMap,  ExtendedRegisterMap),
    (0, 96, 16, tuple(range(10))): (DataMap, RegisterMap,  ExtendedRegisterMap),
    (0, 96, 17, tuple(range(128))): (DataMap, RegisterMap,  ExtendedRegisterMap),
    (0, 96, 20): (DataMap, RegisterMap,  ExtendedRegisterMap),
    (0, 97, 97, tuple(range(10))): DataMap,
    (0, 97, (97, 98), 255): ProfileGenericMap,  # todo: add RegisterTable
    (0, 97, 98, tuple(range(10))+tuple(range(10, 30))): DataMap,
    (0, 98,): ProfileGenericMap,
    (0, 99, 98): ProfileGenericMap,
    # electricity
    (1, 0, 0, tuple(range(10))): DataMap,
    (1, 0, 0, 255): ProfileGenericMap,  # todo: add RegisterTable
    (1, 0, 1): DataMap,
    (1, 0, 2): DataStaticMap,
    (1, 0, (3, 4, 7, 8, 9)): (DataStaticMap, RegisterMap, ExtendedRegisterMap),
    (1, 0, (6, 10)): (RegisterMap, ExtendedRegisterMap),
    (1, 0, 11, tuple(range(1, 8))): DataMap,
    (1, 96, 1, tuple(range(10))): DataMap,
    (1, 96, 1, 255): ProfileGenericMap,  # todo: add RegisterTable
    (1, 96, 5, (0, 1, 2, 3, 4, 5)): DataMap,  # todo: add StatusMapping
    (1, 96, 10, (0, 1, 2, 3)): DataMap,  # todo: add StatusMapping
    (1, 98,): ProfileGenericMap,
    (1, 99, (1, 2, 11, 12, 97, 98, 99)): ProfileGenericMap,
    (1, 99, (3, 13, 14), 0): ProfileGenericMap,
    (1, 99, 10, (1, 2, 3)): ProfileGenericMap,
    (1, _CUMULATIVE, _RU_CHANGE_LIMIT_LEVEL): RegisterMap,
    (1, _NOT_PROCESSING_OF_MEASUREMENT_VALUES, tuple(chain(_CUMULATIVE, _TIME_INTEGRAL_VALUES, _CONTRACTED_VALUES,
                                                           _UNDER_OVER_LIMIT_THRESHOLDS, _UNDER_OVER_LIMIT_OCCURRENCE_COUNTERS,
                                                           _UNDER_OVER_LIMIT_DURATIONS, _UNDER_OVER_LIMIT_MAGNITUDES))): (RegisterMap, ExtendedRegisterMap),
    (1, _NOT_PROCESSING_OF_MEASUREMENT_VALUES, _INSTANTANEOUS_VALUES): RegisterMap,
    (1, _NOT_PROCESSING_OF_MEASUREMENT_VALUES, _MAX_MIN_VALUES): (RegisterMap, ExtendedRegisterMap, ProfileGenericMap),
    (1, _NOT_PROCESSING_OF_MEASUREMENT_VALUES, _CURRENT_AND_LAST_AVERAGE_VALUES): (RegisterMap, DemandRegisterMap),
    (1, _NOT_PROCESSING_OF_MEASUREMENT_VALUES, 40): (DataMap, RegisterMap),
}

func_maps["DLMS_6"] = get_func_map(__func_map_for_create)


# SPODES3 Update
__func_map_for_create.update({
    (0, 21, 0): ClassMap({1: impl.profile_generic.SPODES3DisplayReadout}),
    (0, 96, 1, (0, 2, 4, 5, 8, 9, 10)): ClassMap({0: impl.data.SPODES3IDNotSpecific}),
    (0, 96, 1, 6): ClassMap({0: impl.data.SPODES3SPODESVersion}),
    (0, 96, 2, (1, 2, 3, 5, 6, 7, 11, 12)): ClassMap({0: impl.data.AnyDateTime}),
    (0, 96, 3, 20): ClassMap({0: impl.arbitrator.SPODES3Arbitrator}),
    (0, 96, 5, 1): ClassMap({0: impl.data.SPODES3PowerQuality1Event}),
    (0, 96, 5, 4): ClassMap({0: impl.data.SPODES3PowerQuality2Event}),
    (0, 96, 5, 132): ClassMap({0: impl.data.Unsigned}),  # TODO: make according with СПОДЭС3 13.9. Контроль чередования фаз
    (0, 96, 11, 0): ClassMap({0: impl.data.SPODES3VoltageEvent}),
    (0, 96, 11, 1): ClassMap({0: impl.data.SPODES3CurrentEvent}),
    (0, 96, 11, 2): ClassMap({0: impl.data.SPODES3CommutationEvent}),
    (0, 96, 11, 3): ClassMap({0: impl.data.SPODES3ProgrammingEvent}),
    (0, 96, 11, 4): ClassMap({0: impl.data.SPODES3ExternalEvent}),
    (0, 96, 11, 5): ClassMap({0: impl.data.SPODES3CommunicationEvent}),
    (0, 96, 11, 6): ClassMap({0: impl.data.SPODES3AccessEvent}),
    (0, 96, 11, 7): ClassMap({0: impl.data.SPODES3SelfDiagnosticEvent}),
    (0, 96, 11, 8): ClassMap({0: impl.data.SPODES3ReactivePowerEvent}),
    (0, 0, 96, 51, 0): ClassMap({0: impl.data.OpeningBody}),
    (0, 0, 96, 51, 1): ClassMap({0: impl.data.OpeningCover}),
    (0, 0, 96, 51, 3): ClassMap({0: impl.data.ExposureToMagnet}),
    (0, 0, 96, 51, 4): ClassMap({0: impl.data.ExposureToHSField}),
    (0, 0, 96, 51, 5): ClassMap({0: impl.data.SealStatus}),
    (0, 0, 96, 51, (6, 7)): UnsignedDataMap,
    (0, 0, 96, 51, (8, 9)): ClassMap({0: impl.data.OctetStringDateTime}),
    # electricity
    (1, 0, 8, (4, 5)): ClassMap({0: impl.data.SPODES3MeasurementPeriod}),
    (1, 98, 1): ClassMap({1: impl.profile_generic.SPODES3MonthProfile}),
    (1, 98, 2): ClassMap({1: impl.profile_generic.SPODES3DailyProfile}),
    (1, 99, (1, 2)): ClassMap({1: impl.profile_generic.SPODES3LoadProfile}),
    (1, 0, 131, 35, 0): RegisterMap,
    (1, 0, 133, 35, 0): RegisterMap,
    (1, 0, 147, 133, 0): RegisterMap,
    (1, 0, 148, 136, 0): RegisterMap,
    (1, 94, 7, 0): ClassMap({1: impl.profile_generic.SPODES3CurrentProfile}),
    (1, 94, 7, (1, 2, 3, 4, 5, 6)): ClassMap({1: impl.profile_generic.SPODES3ScalesProfile}),  # Todo: RU. Scaler-profile With 1 entry and more
    # KPZ
    (128, 0, tuple(range(20)), 0, 0): RegisterMap
})

func_maps["SPODES_3"] = get_func_map(__func_map_for_create)

# KPZ Update
__func_map_for_create.update({
    (0, 128, 96, 13, 1): ClassMap({0: impl.data.ITEBitMap}),
    (0, 128, 154, 0, 0): ClassMap({0: impl.data.KPZGSMPingIP}),
    (0, 0, 128, (100, 101, 102, 103, 150, 151, 152, 170)): DataMap,
})
func_maps["KPZ"]: FUNC_MAP = get_func_map(__func_map_for_create)
# KPZ1 with bag in log event profiles
__func_map_for_create.update({
    (0, 96, 11, 0): ClassMap({0: impl.data.KPZ1SPODES3VoltageEvent}),
    (0, 96, 11, 1): ClassMap({0: impl.data.KPZ1SPODES3CurrentEvent}),
    (0, 96, 11, 2): ClassMap({0: impl.data.KPZ1SPODES3CommutationEvent}),
    (0, 96, 11, 3): ClassMap({0: impl.data.KPZ1SPODES3ProgrammingEvent}),
    (0, 96, 11, 4): ClassMap({0: impl.data.KPZ1SPODES3ExternalEvent}),
    (0, 96, 11, 5): ClassMap({0: impl.data.KPZ1SPODES3CommunicationEvent}),
    (0, 96, 11, 6): ClassMap({0: impl.data.KPZ1SPODES3AccessEvent}),
    (0, 96, 11, 7): ClassMap({0: impl.data.KPZ1SPODES3SelfDiagnosticEvent}),
    (0, 96, 11, 8): ClassMap({0: impl.data.KPZ1SPODES3ReactivePowerEvent}),
})
func_maps["KPZ1"]: FUNC_MAP = get_func_map(__func_map_for_create)


def get_type(class_id: ut.CosemClassId,
             version: cdt.Unsigned | None,
             ln: cst.LogicalName,
             func_map: FUNC_MAP) -> Type[InterfaceClass]:
    """use DLMS UA 1000-1 Ed. 14 Table 54"""
    if (128 <= ln.b <= 199) or (128 <= ln.c <= 199) or ln.c == 240 or (128 <= ln.d <= 254) or (128 <= ln.e <= 254) or (128 <= ln.f <= 254):
        # try search in BCDE group for manufacture object before in CDE
        c_m = func_map.get((ln.contents[:5]), common_interface_class_map)
    else:
        # try search in CDE group
        c_m = func_map.get((ln.contents[:1]+ln.contents[2:5]), None)
        if not c_m:
            # try search in CD group
            c_m = func_map.get((ln.contents[:1]+ln.contents[2:4]), None)
            if not c_m:
                # try search in BCDE group
                c_m = func_map.get((ln.contents[:5]), None)
                if not c_m:
                    # try search in C group
                    c_m = func_map.get((ln.contents[:1]+ln.contents[3:4]), common_interface_class_map)
    return get_interface_class(class_map=c_m,
                               c_id=class_id,
                               ver=version)


@lru_cache(20000)
def get_unit(class_id: ClassID, par: bytes) -> int | None:
    match class_id, *par:
        case (ClassID.CLOCK, 3 | 7):
            return 6  # min
        case (ClassID.IEC_HDLC_SETUP, 7) | (ClassID.MODEM_CONFIGURATION, 3, 2):
            return 7  # millisecond
        case ClassID.S_FSK_PHY_MAC_SET_UP, 7, _:
            return 44  # HZ
        case (ClassID.S_FSK_PHY_MAC_SET_UP, 4 | 5):
            return 72  # Db
        case ClassID.S_FSK_PHY_MAC_SET_UP, 6:
            return 71  # DbmicroV
        case _:
            return None


class Collection:
    __dlms_ver: int
    __manufacturer: bytes | None
    __country: CountrySpecificIdentifiers
    __country_ver: AppVersion | None
    __server_type: cdt.CommonDataType | None
    __server_ver: dict[int, AppVersion]
    __container: dict[bytes, InterfaceClass]
    __const_objs: int
    __spec: str
    __collection_ver: AppVersion | None

    def __init__(self,
                 country: CountrySpecificIdentifiers = CountrySpecificIdentifiers.RUSSIA,
                 ldn: octet_string.LDN = None):
        self.__collection_ver = None
        self.__dlms_ver = 6
        self.__manufacturer = None
        self.__country = country
        self.__country_ver = None
        """country version specification"""
        self.__server_type = None
        self.__server_ver = dict()
        """key: instance of 0.b.2.0.1.255, value AppVersion"""
        self.__spec = "DLMS_6"
        self.__container = dict()
        """ all DLMS objects container with obis key """
        ldn_obj = self.add(
            class_id=ClassID.DATA,
            version=Version.V0,
            logical_name=cst.LogicalName("0.0.42.0.0.255"))
        if ldn:
            ldn_obj.set_attr(2, ldn)

    def __eq__(self, other: Self):
        return hash(self) == hash(other)

    def __hash__(self):
        return hash((self.__manufacturer, self.__server_type, self.__collection_ver))

    def copy(self, ldn: octet_string.LDN = None) -> Self:
        new_collection = Collection(self.__country, ldn=ldn)
        new_collection.set_dlms_ver(self.__dlms_ver)
        new_collection.set_manufacturer(self.__manufacturer)
        new_collection.set_country_ver(self.__country_ver)
        new_collection.set_collection_ver(self.__collection_ver)
        new_collection.set_spec()
        max_ass: AssociationLN | None = None
        """more full association"""  # todo: move to collection(from_xml)
        for obj in self.__container.values():
            new_obj: InterfaceClass = obj.__class__(obj.logical_name)
            new_collection.__container[obj.logical_name.contents] = new_obj
            new_obj.collection = new_collection
            if obj.CLASS_ID == ClassID.ASSOCIATION_LN:
                if max_ass is None or (obj.object_list and len(max_ass.object_list) < len(obj.object_list)):
                    max_ass = obj
        obj_for_set = max_ass.get_objects()
        ass_id: int = max_ass.logical_name.e
        last_length = len(obj_for_set)
        raise_count = None
        while len(obj_for_set) != 0:
            obj = obj_for_set.pop(0)
            try:
                new_collection.__container.get(obj.logical_name.contents).copy(obj, ass_id)
                raise_count = None
            except Exception as e:
                if last_length == len(obj_for_set):
                    if not raise_count:
                        raise_count = count(last_length, -1)
                        continue
                    else:
                        next(raise_count)
                        raise e
                else:
                    last_length = len(obj_for_set)
                    logger.warning(F"can't set value. {e}. leftover {len(obj_for_set)} objects")
                    obj_for_set.append(obj)
        return new_collection

    @property
    def dlms_ver(self):
        return self.__dlms_ver

    def set_dlms_ver(self, value: int):
        if not self.__dlms_ver:
            self.__dlms_ver = value
        else:
            if value != self.__dlms_ver:
                raise ValueError(F"got dlms_version: {value}, expected {self.__dlms_ver}")
            else:
                """success validation"""

    @property
    def manufacturer(self):
        return self.__manufacturer

    def set_manufacturer(self, value: bytes):
        if not self.__manufacturer:
            self.__manufacturer = value
        else:
            if value != self.__manufacturer:
                raise ValueError(F"got manufacturer: {value}, expected {self.__manufacturer}")
            else:
                """success validation"""

    @property
    def country(self):
        return self.__country

    def set_country(self, value: CountrySpecificIdentifiers):
        if not self.__country:
            self.__country = value
        else:
            if value != self.__country:
                raise ValueError(F"got country: {value}, expected {self.__country}")
            else:
                """success validation"""

    @property
    def country_ver(self):
        return self.__country_ver

    def set_country_ver(self, value: AppVersion):
        """country version specification"""
        if not self.__country_ver:
            self.__country_ver = value
        else:
            if value != self.__country_ver:
                raise ValueError(F"got country version: {value}, expected {self.__country_ver}")
            else:
                """success validation"""

    @property
    def server_type(self) -> cdt.CommonDataTypes | None:
        return self.__server_type

    def set_server_type(self, value: cdt.CommonDataTypes, force: bool = False):
        if not self.__server_type or force:
            self.__server_type = value
        else:
            if value != self.__server_type:
                raise ValueError(F"got server type: {value}, expected {self.__server_type}")
            else:
                """success validation"""

    @property
    def server_ver(self) -> dict[int, AppVersion]:
        return self.__server_ver

    def clear_server_ver(self):
        self.__server_ver.clear()

    def set_server_ver(self, instance: int, value: AppVersion, force: bool = False):
        if self.__server_ver.get(instance) is None or force:
            self.__server_ver[instance] = value
        else:
            if value.major != self.__server_ver[instance].major or value.minor != self.__server_ver[instance].minor:
                raise ValueError(F"attempt set server version[{instance}]: {value}, existed {self.__server_ver[instance]}. Execute search of type")
            elif value.patch <= self.__server_ver[instance].patch:
                """success validation"""
            else:
                raise ValueError(F"got more hi patch: {value} expected before {self.__server_ver[instance].patch}")

    @property
    def collection_ver(self) -> AppVersion:
        return self.__collection_ver

    def set_collection_ver(self, value: AppVersion):
        """once setting collection version from file"""
        if not self.__collection_ver:
            self.__collection_ver = value
        else:
            raise ValueError(F"set collection version: {value} failure, already exist")

    def __str__(self):
        return F"[{len(self.__container)}] DLMS version: {self.__dlms_ver}, country: {self.__country.name}, country specific version: {self.__country_ver}, " \
               F"manufacturer: {self.__manufacturer}, server type: {repr(self.__server_type)}, collection/server version: {self.__server_ver}/{self.__collection_ver}, " \
               F"uses specification: {self.__spec}"

    def __iter__(self) -> Iterator[ic.COSEMInterfaceClasses]:
        return iter(self.__container.values())

    @classmethod
    def from_xml3(cls, filename: str) -> tuple[Self, UsedAttributes]:
        """ create collection from xml for template and UsedAttributes """
        used: UsedAttributes = dict()
        tree = ET.parse(filename)
        objects = tree.getroot()
        decode: bool = bool(int(objects.attrib.get("decode", "0")))
        if objects.tag != TagsName.TEMPLATE_ROOT.value:
            raise ValueError(F"ERROR: Root tag got {objects.tag}, expected {TagsName.TEMPLATE_ROOT.value}")
        root_version: AppVersion = AppVersion.from_str(objects.attrib.get('version', '1.0.0'))
        logger.info(F'Версия: {root_version}, file: {filename.split("/")[-1]}')
        new = get_collection(
            manufacturer=objects.findtext("manufacturer").encode("utf-8"),
            server_type=cdt.get_instance_and_pdu_from_value(bytes.fromhex(objects.findtext("server_type")))[0],
            server_ver=AppVersion.from_str(objects.findtext("server_ver")))
        match root_version:
            case AppVersion(4, 0):
                for obj in objects.findall('object'):
                    ln: str = obj.attrib.get("ln", 'is absence')
                    logical_name: cst.LogicalName = cst.LogicalName(ln)
                    if not new.is_in_collection(logical_name):
                        raise ValueError(F"got object with {ln=} not find in collection. Abort attribute setting")
                    else:
                        new_object = new.get_object(logical_name)
                        used[logical_name] = set()
                    for attr in obj.findall("attr"):
                        index: int = int(attr.attrib.get("index"))
                        used[logical_name].add(index)
                        try:
                            if decode:
                                match attr.attrib.get("type", "simple"):
                                    case "simple":
                                        new_object.set_attr(index, attr.text)
                                    case "array" | "struct":
                                        stack = [(list(), iter(attr))]
                                        while stack:
                                            v1, v2 = stack[-1]
                                            v = next(v2, None)
                                            if v is None:
                                                stack.pop()
                                            elif v.tag == "simple":
                                                v1.append(v.text)
                                            else:
                                                v1.append(list())
                                                stack.append((v1[-1], iter(v)))
                                        new_object.set_attr(index, v1)
                            else:
                                new_object.set_attr(index, bytes.fromhex(attr.text))
                        except exc.NoObject as e:
                            logger.error(F"Can't fill {new_object} attr: {index}. Skip. {e}.")
                            break
                        except exc.ITEApplication as e:
                            logger.error(F"Can't fill {new_object} attr: {index}. {e}")
                        except IndexError:
                            logger.error(F'Object "{new_object}" not has attr: {index}')
                        except TypeError as e:
                            logger.error(F'Object {new_object} attr:{index} do not write, encoding wrong : {e}')
                        except ValueError as e:
                            logger.error(F'Object {new_object} attr:{index} do not fill: {e}')
                        except AttributeError as e:
                            logger.error(F'Object {new_object} attr:{index} do not fill: {e}')
            case _ as error:
                raise exc.VersionError(error, additional='Xml')
        return new, used

    @classmethod
    def from_xml(cls, filename: os.DirEntry | str) -> Self:
        """ append objects from xml file """
        tree = ET.parse(filename)
        objects = tree.getroot()
        new = cls()
        if objects.tag != TagsName.DEVICE_ROOT.value:
            raise ValueError(F"ERROR: Root tag got {objects.tag}, expected {TagsName.DEVICE_ROOT.value}")
        root_version: AppVersion = AppVersion.from_str(objects.attrib.get('version', '1.0.0'))
        if (dlms_ver := objects.findtext("dlms_ver")) is not None:
            new.set_dlms_ver(int(dlms_ver))
        if (country := objects.findtext("country")) is not None:
            new.set_country(CountrySpecificIdentifiers(int(country)))
        if (country_ver := objects.findtext("country_ver")) is not None:
            new.set_country_ver(AppVersion.from_str(country_ver))
        if (manufacturer := objects.findtext("manufacturer")) is not None:
            new.set_manufacturer(manufacturer.encode("utf-8"))
        if (server_type := objects.findtext("server_type")) is not None:
            tmp, _ = cdt.get_instance_and_pdu_from_value(bytes.fromhex(server_type))
            new.set_server_type(tmp)
        for server_ver in objects.findall("server_ver"):
            new.set_collection_ver(value=AppVersion.from_str(server_ver.text))
            break
        new.set_spec()
        logger.info(F'Версия: {root_version}, file: {filename}')
        match root_version:
            case AppVersion(3, 0 | 1 | 2):
                attempts: iter = count(3, -1)
                """ attempts counter """
                while len(objects) != 0 and next(attempts):
                    logger.info(F'{attempts=}')
                    for obj in objects.findall('object'):
                        ln: str = obj.attrib.get('ln', 'is absence')
                        class_id: str = obj.findtext('class_id')
                        if not class_id:
                            logger.warning(F"skip create DLMS {ln} from Xml. Class ID is absence")
                            continue
                        version: str | None = obj.findtext('version')
                        try:
                            logical_name: cst.LogicalName = cst.LogicalName(ln)
                            if not new.is_in_collection(logical_name):
                                new_object = new.add(class_id=ut.CosemClassId(class_id),
                                                     version=None if version is None else cdt.Unsigned(version),
                                                     logical_name=logical_name)
                            else:
                                new_object = new.__get_object(logical_name.contents)
                        except TypeError as e:
                            logger.error(F'Object {obj.attrib["name"]} not created : {e}')
                            continue
                        except ValueError as e:
                            logger.error(F'Object {obj.attrib["name"]} not created. {class_id=} {version=} {ln=}: {e}')
                            continue
                        indexes: list[int] = list()
                        """ got attributes indexes for current object """
                        for attr in obj.findall('attribute'):
                            index: str = attr.attrib.get('index')
                            if index.isdigit():
                                indexes.append(int(index))
                            else:
                                raise ValueError(F'ERROR: for {new_object.logical_name if new_object is not None else ""} got index {index} and it is not digital')
                            try:
                                match len(attr.text), new_object.get_attr_element(indexes[-1]).DATA_TYPE:
                                    case 1 | 2, ut.CHOICE():
                                        if new_object.get_attr(indexes[-1]) is None:
                                            new_object.set_attr(indexes[-1], int(attr.text))
                                        else:
                                            """not need set"""
                                    case 1 | 2, data_type if data_type.TAG[0] == int(attr.text): """ ordering by old"""
                                    case 1 | 2, data_type:                                       raise ValueError(F'Got {attr.text} attribute Tag, expected {data_type}')
                                    case _:
                                        record_time: str = attr.attrib.get('record_time')
                                        if record_time is not None:
                                            new_object.set_record_time(indexes[-1], bytes.fromhex(record_time))
                                        new_object.set_attr(indexes[-1], bytes.fromhex(attr.text))
                                obj.remove(attr)
                            except ut.UserfulTypesException as e:
                                if attr.attrib.get("forced", None):
                                    new_object.set_attr_force(indexes[-1], cdt.get_common_data_type_from(int(attr.text).to_bytes(1, "big"))())
                                logger.warning(F"set to {new_object} attr: {indexes[-1]} forced value after. {e}.")
                            except exc.NoObject as e:
                                logger.error(F"Can't fill {new_object} attr: {indexes[-1]}. Skip. {e}.")
                                break
                            except exc.ITEApplication as e:
                                logger.error(F"Can't fill {new_object} attr: {indexes[-1]}. {e}")
                            except IndexError:
                                logger.error(F'Object "{new_object}" not has attr: {index}')
                            except TypeError as e:
                                logger.error(F'Object {new_object} attr:{index} do not write, encoding wrong : {e}')
                            except ValueError as e:
                                logger.error(F'Object {new_object} attr:{index} do not fill: {e}')
                            except AttributeError as e:
                                logger.error(F'Object {new_object} attr:{index} do not fill: {e}')
                        if len(obj.findall('attribute')) == 0:
                            objects.remove(obj)
                    logger.info(F'Not parsed DLMS objects: {len(objects)}')
            case AppVersion(4, 0):
                attempts: iter = count(3, -1)
                """ attempts counter """
                while len(objects) != 0 and next(attempts):
                    logger.info(F'{attempts=}')
                    for obj in objects.findall("obj"):
                        ln: str = obj.attrib.get('ln', 'is absence')
                        version: str | None = obj.findtext("ver")
                        try:
                            logical_name: cst.LogicalName = cst.LogicalName(ln)
                            if version:  # only for AssociationLN
                                new_object: AssociationLN = new.add_if_missing(
                                    class_id=ClassID.ASSOCIATION_LN,
                                    version=cdt.Unsigned(version),
                                    logical_name=logical_name)
                                new.add_if_missing(  # current association with know version
                                    class_id=ClassID.ASSOCIATION_LN,
                                    version=cdt.Unsigned(version),
                                    logical_name=cst.LogicalName("0.0.40.0.0.255"))
                            else:
                                new_object = new.__get_object(logical_name.contents)
                        except TypeError as e:
                            logger.error(F'Object {obj.attrib["ln"]} not created : {e}')
                            continue
                        except ValueError as e:
                            logger.error(F'Object {obj.attrib["ln"]} not created. {version=} {ln=}: {e}')
                            continue
                        for attr in obj.findall("attr"):
                            i: int = int(attr.attrib.get("i"))
                            try:
                                if len(attr.text) <= 2:  # set only type with default value
                                    data_type = new_object.get_attr_element(i).DATA_TYPE
                                    if isinstance(data_type, ut.CHOICE):
                                        new_object.set_attr(i, int(attr.text))
                                    elif data_type.TAG[0] == int(attr.text):
                                        """ ordering by old"""
                                    else:
                                        raise ValueError(F'Got {attr.text} attribute Tag, expected {data_type}')
                                else:  # set common value
                                    new_object.set_attr(i, bytes.fromhex(attr.text))
                                    if new_object.CLASS_ID == ClassID.ASSOCIATION_LN and i == 2:  # setup new objects from AssociationLN.object_list
                                        for obj_el in new_object.object_list:
                                            obj_el: ObjectListElement
                                            new.add_if_missing(
                                                class_id=obj_el.class_id,
                                                version=obj_el.version,
                                                logical_name=obj_el.logical_name)
                                obj.remove(attr)
                            except ut.UserfulTypesException as e:
                                if attr.attrib.get("forced", None):
                                    new_object.set_attr_force(i, cdt.get_common_data_type_from(int(attr.text).to_bytes(1, "big"))())
                                logger.warning(F"set to {new_object} attr: {i} forced value after. {e}.")
                            except exc.NoObject as e:
                                logger.error(F"Can't fill {new_object} attr: {i}. Skip. {e}.")
                                break
                            except exc.ITEApplication as e:
                                logger.error(F"Can't fill {new_object} attr: {i}. {e}")
                            except IndexError:
                                logger.error(F'Object "{new_object}" not has attr: {i}')
                            except TypeError as e:
                                logger.error(F'Object {new_object} attr:{i} do not write, encoding wrong : {e}')
                            except ValueError as e:
                                logger.error(F'Object {new_object} attr:{i} do not fill: {e}')
                            except AttributeError as e:
                                logger.error(F'Object {new_object} attr:{i} do not fill: {e}')
                        if len(obj.findall("attr")) == 0:
                            objects.remove(obj)
                    logger.info(F'Not parsed DLMS objects: {len(objects)}')
            case _ as error:
                raise exc.VersionError(error, additional='Xml')
        return new

    def from_xml2(self, filename: str) -> Self:
        """ set attribute values from xml. validation ID's """
        tree = ET.parse(filename)
        objects = tree.getroot()
        if objects.tag != TagsName.DEVICE_ROOT.value:
            raise ValueError(F"ERROR: Root tag got {objects.tag}, expected {TagsName.DEVICE_ROOT.value}")
        root_version: AppVersion = AppVersion.from_str(objects.attrib.get('version', '1.0.0'))
        if (dlms_ver := objects.findtext("dlms_ver")) is not None:
            self.set_dlms_ver(int(dlms_ver))
        if (country := objects.findtext("country")) is not None:
            self.set_country(CountrySpecificIdentifiers(int(country)))
        if (country_ver := objects.findtext("country_ver")) is not None:
            self.set_country_ver(AppVersion.from_str(country_ver))
        if (manufacturer := objects.findtext("manufacturer")) is not None:
            self.set_manufacturer(manufacturer.encode("utf-8"))
        if (server_type := objects.findtext("server_type")) is not None:
            tmp, _ = cdt.get_instance_and_pdu_from_value(bytes.fromhex(server_type))
            self.set_server_type(tmp)
        for server_ver in objects.findall("server_ver"):
            self.set_server_ver(instance=int(server_ver.attrib.get("instance", "0")),
                                value=AppVersion.from_str(server_ver.text))
        logger.info(F'Версия: {root_version}, file: {filename.split("/")[-1]}')
        match root_version:
            case AppVersion(2, 0 | 1 | 2):
                attempts: iter = count(3, -1)
                """ attempts counter """
                while len(objects) != 0 and next(attempts):
                    logger.info(F'{attempts=}')
                    for obj in objects.findall('object'):
                        ln: str = obj.attrib.get('ln', 'is absence')
                        class_id: str = obj.findtext('class_id')
                        if not class_id:
                            logger.warning(F"skip create DLMS {ln} from Xml. Class ID is absence")
                            continue
                        version: str | None = obj.findtext('version')
                        try:
                            logical_name: cst.LogicalName = cst.LogicalName(ln)
                            if not self.is_in_collection(logical_name):
                                new_object = self.add(
                                    class_id=ut.CosemClassId(class_id),
                                    version=None if version is None else cdt.Unsigned(version),
                                    logical_name=cst.LogicalName(ln))
                            else:
                                new_object = self.get_object(logical_name.contents)
                        except TypeError as e:
                            logger.error(F'Object {obj.attrib["name"]} not created : {e}')
                            continue
                        except ValueError as e:
                            logger.error(F'Object {obj.attrib["name"]} not created. {class_id=} {version=} {ln=}: {e}')
                            continue
                        indexes: list[int] = list()
                        """ got attributes indexes for current object """
                        for attr in obj.findall('attribute'):
                            index: str = attr.attrib.get('index')
                            if index.isdigit():
                                indexes.append(int(index))
                            else:
                                raise ValueError(F'ERROR: for {new_object.logical_name if new_object is not None else ""} got index {index} and it is not digital')
                            try:
                                match len(attr.text), new_object.get_attr_element(indexes[-1]).DATA_TYPE:
                                    case 1 | 2, ut.CHOICE():
                                        if new_object.get_attr(indexes[-1]) is None:
                                            new_object.set_attr(indexes[-1], int(attr.text))
                                        else:
                                            """not need set"""
                                    case 1 | 2, data_type if data_type.TAG[0] == int(attr.text):
                                        """ ordering by old"""
                                    case 1 | 2, data_type:
                                        raise ValueError(F'Got {attr.text} attribute Tag, expected {data_type}')
                                    case _:
                                        record_time: str = attr.attrib.get('record_time')
                                        if record_time is not None:
                                            new_object.set_record_time(indexes[-1], bytes.fromhex(record_time))
                                        new_object.set_attr(indexes[-1], bytes.fromhex(attr.text))
                                obj.remove(attr)
                            except exc.NoObject as e:
                                logger.error(F"Can't fill {new_object} attr: {indexes[-1]}. Skip. {e}.")
                                break
                            except exc.ITEApplication as e:
                                logger.error(F"Can't fill {new_object} attr: {indexes[-1]}. {e}")
                            except IndexError:
                                logger.error(F'Object "{new_object}" not has attr: {index}')
                            except TypeError as e:
                                logger.error(F'Object {new_object} attr:{index} do not write, encoding wrong : {e}')
                            except ValueError as e:
                                logger.error(F'Object {new_object} attr:{index} do not fill: {e}')
                            except AttributeError as e:
                                logger.error(F'Object {new_object} attr:{index} do not fill: {e}')
                        if len(obj.findall('attribute')) == 0:
                            objects.remove(obj)
                    logger.info(F'Not parsed DLMS objects: {len(objects)}')
            case AppVersion(3, 1 | 2):
                for obj in objects.findall('object'):
                    ln: str = obj.attrib.get('ln', 'is absence')
                    logical_name: cst.LogicalName = cst.LogicalName(ln)
                    if not self.is_in_collection(logical_name):
                        logger.error(F"got object with {ln=} not find in collection. Skip it attribute values")
                        continue
                    else:
                        new_object = self.get_object(logical_name)
                    indexes: list[int] = list()
                    """ got attributes indexes for current object """
                    for attr in obj.findall('attribute'):
                        index: str = attr.attrib.get('index')
                        if index.isdigit():
                            indexes.append(int(index))
                        else:
                            raise ValueError(F'ERROR: for obj with {ln=} got index {index} and it is not digital')
                        try:
                            new_object.set_attr(indexes[-1], bytes.fromhex(attr.text))
                        except exc.NoObject as e:
                            logger.error(F"Can't fill {new_object} attr: {indexes[-1]}. Skip. {e}.")
                            break
                        except exc.ITEApplication as e:
                            logger.error(F"Can't fill {new_object} attr: {indexes[-1]}. {e}")
                        except IndexError:
                            logger.error(F'Object "{new_object}" not has attr: {index}')
                        except TypeError as e:
                            logger.error(F'Object {new_object} attr:{index} do not write, encoding wrong : {e}')
                        except ValueError as e:
                            logger.error(F'Object {new_object} attr:{index} do not fill: {e}')
                        except AttributeError as e:
                            logger.error(F'Object {new_object} attr:{index} do not fill: {e}')
            case AppVersion(4, 0):
                for obj in objects.findall('object'):
                    ln: str = obj.attrib.get("ln", 'is absence')
                    logical_name: cst.LogicalName = cst.LogicalName(ln)
                    if not self.is_in_collection(logical_name):
                        raise ValueError(F"got object with {ln=} not find in collection. Abort attribute setting")
                    else:
                        new_object = self.get_object(logical_name)
                        for attr in obj.findall("attr"):
                            index: int = int(attr.attrib.get("index"))
                            try:
                                new_object.set_attr(index, bytes.fromhex(attr.text))
                            except exc.NoObject as e:
                                logger.error(F"Can't fill {new_object} attr: {index}. Skip. {e}.")
                                break
                            except exc.ITEApplication as e:
                                logger.error(F"Can't fill {new_object} attr: {index}. {e}")
                            except IndexError:
                                logger.error(F'Object "{new_object}" not has attr: {index}')
                            except TypeError as e:
                                logger.error(F'Object {new_object} attr:{index} do not write, encoding wrong : {e}')
                            except ValueError as e:
                                logger.error(F'Object {new_object} attr:{index} do not fill: {e}')
                            except AttributeError as e:
                                logger.error(F'Object {new_object} attr:{index} do not fill: {e}')
            case _ as error:
                raise exc.VersionError(error, additional='Xml')

    def __get_base_xml_element(self, root_tag: str = TagsName.DEVICE_ROOT.value) -> ET.Element:
        objects = ET.Element(root_tag, attrib={'version': '4.0.0'})
        ET.SubElement(objects, 'dlms_ver').text = str(self.dlms_ver)
        ET.SubElement(objects, 'country').text = str(self.country.value)
        if self.country_ver:
            ET.SubElement(objects, 'country_ver').text = str(self.country_ver)
        if self.manufacturer is not None:
            ET.SubElement(objects, 'manufacturer').text = self.manufacturer.decode("utf-8")
        if self.server_type is not None:
            ET.SubElement(objects, 'server_type').text = self.server_type.encoding.hex()
        for ver in self.server_ver:
            server_ver_node = ET.SubElement(objects, 'server_ver', attrib={"instance": str(ver)})
            server_ver_node.text = str(self.server_ver[ver])
        return objects

    def to_xml(self, file_name: str,
               root_tag: str = TagsName.DEVICE_ROOT.value,
               with_comment: bool = False,
               is_decode: bool = False):
        """Save attributes of client. For types only STATIC save """
        classes: set[ut.CosemClassId] = set()
        objects = self.__get_base_xml_element(root_tag)
        for obj in self.values():
            object_node = ET.SubElement(objects, 'object', attrib={'name': F'{get_name(obj.logical_name)}', 'ln': str(obj.logical_name)})
            if obj.CLASS_ID == ClassID.ASSOCIATION_LN:
                ET.SubElement(object_node, "ver").text = str(obj.VERSION)
            classes.add(obj.CLASS_ID)
            for index, attr in obj.get_index_with_attributes():
                if index == 1:  # don't keep ln
                    continue
                else:
                    el = obj.get_attr_element(index)
                    match attr, el.DATA_TYPE:
                        case None, ut.CHOICE:
                            logger.warning(F'PASS choice {obj} {index}')
                        case None, cdt.CommonDataType():
                            if with_comment:
                                object_node.append(ET.Comment(F'{el.NAME}. Type: {el.DATA_TYPE}'))
                            ET.SubElement(object_node, 'attribute', attrib={'index': str(index)}).text = str(el.DATA_TYPE.TAG[0])
                        case cdt.CommonDataType(), _:
                            if is_decode:
                                attr_el = ET.SubElement(
                                    object_node,
                                    "attr",
                                    {"name": str(obj.get_attr_element(index)),
                                     "index": str(index)})
                                if isinstance(attr, cdt.SimpleDataType):
                                    attr_el.text = str(attr)
                                elif isinstance(attr, cdt.ComplexDataType):
                                    attr_el.attrib["type"] = "array" if attr.TAG == b'\x01' else "struct"  # todo: make better
                                    stack: list = [(attr_el, "attr_el_name", iter(attr))]
                                    while stack:
                                        node, name, value_it = stack[-1]
                                        value = next(value_it, None)
                                        if value:
                                            if not isinstance(name, str):
                                                name = next(name).NAME
                                            if isinstance(value, cdt.Array):
                                                stack.append((ET.SubElement(node,
                                                                            "array",
                                                                            attrib={"name": name}), "ar_name", iter(value)))
                                            elif isinstance(value, cdt.Structure):
                                                stack.append((ET.SubElement(node, "struct"), iter(value.ELEMENTS), iter(value)))
                                            else:
                                                ET.SubElement(node,
                                                              "simple",
                                                              attrib={"name": name}).text = str(value)
                                        else:
                                            stack.pop()
                            else:
                                el_attrib: dict = {'index': str(index)}
                                if with_comment:
                                    object_node.append(ET.Comment(F'{el.NAME}: {attr}'))
                                ET.SubElement(object_node, 'attribute', attrib=el_attrib).text = attr.encoding.hex()
                        case _:
                            logger.warning('PASS')
            print("child =", len(object_node))

        # TODO: '<!DOCTYPE ITE_util_tree SYSTEM "setting.dtd"> or xsd
        xml_string = ET.tostring(objects, encoding='cp1251', method='xml')
        dom_xml = minidom.parseString(xml_string)
        str_ = dom_xml.toprettyxml(indent="  ", encoding='cp1251')
        with open(file_name, "wb") as f:
            f.write(str_)

    def to_xml2(self, file_name: str,
                root_tag: str = TagsName.DEVICE_ROOT.value,
                association_id: int = 3) -> bool:
        """Save attributes WRITABLE and STATIC of client"""
        objects = self.__get_base_xml_element(root_tag)
        col = get(
            m=self.manufacturer,
            t=self.server_type,
            ver=self.server_ver[0])
        is_empty: bool = True
        for desc in col.getASSOCIATION(association_id).object_list:
            obj = self.get_object(desc)
            object_node = None
            for i, attr in obj.get_index_with_attributes():
                if i == 1:
                    """skip ln"""
                elif obj.get_attr_element(i).classifier == ic.Classifier.DYNAMIC:
                    """skip DYNAMIC attributes"""
                elif not col.is_writable(obj.logical_name, i, 3):
                    """skip not writable"""
                elif col.get_object(obj.logical_name).get_attr(i) == attr:
                    """skip not changed attr value"""
                elif isinstance(attr, cdt.Array) and len(attr) == 0:
                    """skip empty arrays"""
                else:
                    is_empty = False
                    if not object_node:
                        object_node = ET.SubElement(objects, 'object', attrib={'ln': str(obj.logical_name)})
                    ET.SubElement(object_node, 'attribute', attrib={'index': str(i)}).text = attr.encoding.hex()
        if not is_empty:
            # TODO: '<!DOCTYPE ITE_util_tree SYSTEM "setting.dtd"> or xsd
            xml_string = ET.tostring(objects, encoding='cp1251', method='xml')
            dom_xml = minidom.parseString(xml_string)
            str_ = dom_xml.toprettyxml(indent="  ", encoding='cp1251')
            with open(file_name, "wb") as f:
                f.write(str_)
        else:
            logger.warning("nothing save. all attributes according with origin collection")
        return not is_empty

    def save_type(self,
                  file_name: str,
                  root_tag: str = TagsName.DEVICE_ROOT.value):
        """ For concrete device save all attributes. For types only STATIC save """
        objects = self.__get_base_xml_element(root_tag)
        objs: dict[ln, set[int]] = dict()
        """key: LN, value: not writable and readable container"""
        for ass in filter(lambda it: it.logical_name.e != 0, self.get_objects_by_class_id(ClassID.ASSOCIATION_LN)):
            for obj_el in ass.object_list:
                if str(obj_el.logical_name) in ("0.0.40.0.0.255", "0.0.42.0.0.255"):
                    """skip LDN and current_association"""
                    continue
                elif obj_el.logical_name in objs:
                    """"""
                else:
                    objs[obj_el.logical_name] = set()
                for access in obj_el.access_rights.attribute_access[1:]:  # without ln
                    if not access.access_mode.is_writable() and access.access_mode.is_readable():
                        objs[obj_el.logical_name].add(int(access.attribute_id))
        o2 = list()
        """container sort by AssociationLN first"""
        for ln in objs.keys():
            obj = self.get_object(ln)
            if obj.CLASS_ID == ClassID.ASSOCIATION_LN:
                o2.insert(0, obj)
            else:
                o2.append(obj)
        for obj in o2:
            object_node = ET.SubElement(objects, "obj", attrib={'ln': str(obj.logical_name)})
            if obj.CLASS_ID == ClassID.ASSOCIATION_LN:
                ET.SubElement(object_node, "ver").text = str(obj.VERSION)
            v = objs[obj.logical_name]
            for i, attr in filter(lambda it: it[0] != 1, obj.get_index_with_attributes()):
                el: ic.ICAElement = obj.get_attr_element(i)
                if el.classifier == ic.Classifier.STATIC and ((i in v) or el.DATA_TYPE == impl.profile_generic.CaptureObjectsDisplayReadout):
                    if attr is None:
                        logger.error(F"for {obj} attr: {i} not set, value is absense")
                    else:
                        ET.SubElement(object_node, "attr", attrib={"i": str(i)}).text = attr.encoding.hex()
                elif isinstance(el.DATA_TYPE, ut.CHOICE):  # need keep all CHOICES types if possible
                    if attr is None:
                        logger.error(F"for {obj} attr: {i} type not set, value is absense")
                    else:
                        ET.SubElement(object_node, "attr", attrib={"i": str(i)}).text = str(attr.TAG[0])
                else:
                    logger.info(F"for {obj} attr: {i} value not need. skipped")
            if len(object_node) == 0:
                objects.remove(object_node)
        # TODO: '<!DOCTYPE ITE_util_tree SYSTEM "setting.dtd"> or xsd
        xml_string = ET.tostring(objects, encoding='cp1251', method='xml')
        dom_xml = minidom.parseString(xml_string)
        str_ = dom_xml.toprettyxml(indent="  ", encoding='cp1251')
        with open(file_name, "wb") as f:
            f.write(xml_string)

    def set_spec(self):
        """set functional map to specification by identification fields"""
        match self.dlms_ver:
            case 6: self.__spec = "DLMS_6"
            case _: raise ValueError(F"unsupport {self.dlms_ver=}")
        if self.country == CountrySpecificIdentifiers.RUSSIA:
            if self.country_ver == AppVersion(3, 0):
                self.__spec = "SPODES_3"
            if self.manufacturer == b"KPZ":
                if self.server_ver and self.server_ver.get(0) < AppVersion(1, 3, 30):
                    self.__spec = "KPZ1"
                else:
                    self.__spec = "KPZ"
            pass
        else:
            """not support other country"""

    def add_if_missing(self, class_id: ut.CosemClassId,
                       version: cdt.Unsigned | None,
                       logical_name: cst.LogicalName) -> InterfaceClass:
        """ like as add method with check for missing """
        if not self.__container.get(logical_name.contents):
            return self.add(
                class_id=class_id,
                version=version,
                logical_name=logical_name)
        else:
            return self.__get_object(logical_name.contents)

    def get(self, obis: bytes) -> InterfaceClass | None:
        """ get object, return None if it absence """
        return self.__container.get(obis, None)

    def values(self) -> tuple[InterfaceClass]:
        return tuple(self.__container.values())

    def __len__(self):
        return len(self.__container)

    def add(self, class_id: ut.CosemClassId,
            version: cdt.Unsigned | None,
            logical_name: cst.LogicalName) -> InterfaceClass:
        """ append new DLMS object to collection with return it"""
        try:
            new_object = get_type(
                class_id=class_id,
                version=self.find_version(class_id) if version is None else version,
                ln=logical_name,
                func_map=func_maps[self.__spec])(logical_name)
            new_object.collection = self
            self.__container[logical_name.contents] = new_object
            logger.info(F'Create {new_object}')
            return new_object
        except ValueError as e:
            raise ValueError(F"error getting DLMS object instance with {class_id=} {version=} {logical_name=}: {e}")
        except StopIteration as e:
            raise ValueError(F"not find class version for {class_id=} {logical_name=}: {e}")

    def get_class_version(self) -> dict[ut.CosemClassId, cdt.Unsigned]:
        """use for check all class version by unique"""
        ret: dict[ut.CosemClassId, cdt.Unsigned] = dict()
        for obj in self.__container.values():
            if ver := ret.get(obj.CLASS_ID):
                if obj.VERSION != ver:
                    raise ValueError(F"for {obj.CLASS_ID=} exist several versions: {obj.VERSION}, {ver} in one collection")
            else:
                ret[obj.CLASS_ID] = obj.VERSION
        return ret

    def get_n_phases(self) -> int:
        """search objects with L2 phase"""
        ret: int | None = None
        for obj in filter(lambda obj: obj.logical_name.a == 1, self):
            if 41 <= obj.logical_name.c <= 60:
                return 3
            ret = 1
        if ret is None:
            raise exc.NoObject("no one electricity object was find")
        else:
            return ret

    @lru_cache(maxsize=100)  # amount of all ClassID
    def find_version(self, class_id: ut.CosemClassId) -> cdt.Unsigned:
        """use for add new object from profile_generic if absence in object list"""
        return next(filter(lambda obj: obj.CLASS_ID == class_id, self.__container.values())).VERSION

    def is_in_collection(self, value: LNContaining) -> bool:
        obis: bytes = get_ln_contents(value)
        return False if self.__container.get(obis) is None else True

    def get_object(self, value: LNContaining) -> InterfaceClass:
        """ return object from obis<string> or raise exception if it absence """
        return self.__get_object(get_ln_contents(value))

    def get_object2(self, value: LNContaining) -> InterfaceClass | None:
        """ return object from obis<string> or None"""
        # todo: refactoring with one get_ln_contents
        if self.is_in_collection(value):
            return self.__get_object(get_ln_contents(value))
        else:
            return None

    def get_report(self,
                   obj: ic.COSEMInterfaceClasses,
                   par: bytes,
                   a_val: cdt.CommonDataType = None
                   ) -> cdt.Report:
        """par: attribute_index, par1, par2, ..."""
        if a_val is None:  # for recursion
            a_val = obj.get_attr(par[0])
        if a_val is None:
            return cdt.Report(
                mess=_report["empty"],
                lev=logging.WARN)
        else:
            if unit := get_unit(obj.CLASS_ID, par):
                return cdt.Report(
                    mess=str(a_val),
                    unit=str(cdt.Unit(unit))
                )
            else:
                if s_u := self.get_scaler_unit(obj, par, a_val):
                    return cdt.Report(
                        mess=str(int(a_val) * 10 ** int(s_u.scaler)),
                        unit=str(s_u.unit))
                else:
                    match obj.CLASS_ID, *par:
                        case (ClassID.PROFILE_GENERIC, 3, _) | (ClassID.PROFILE_GENERIC, 6):
                            a_val: structs.CaptureObjectDefinition
                            obj = self.get_object(a_val.logical_name)
                            return cdt.Report(
                                mess=F"{get_name(a_val.logical_name)}.{obj.get_attr_element(int(a_val.attribute_index))}"
                            )
                        case _:
                            return cdt.Report(str(a_val))

    @lru_cache(20000)
    def get_scaler_unit(self,
                        obj: ic.COSEMInterfaceClasses,
                        par: bytes,
                        a_val: cdt.CommonDataType
                        ) -> cdt.ScalUnitType | None:
        match obj.CLASS_ID, *par:
            case (ClassID.REGISTER, 2) | (ClassID.DEMAND_REGISTER, 2 | 3):
                if (s_u := obj.scaler_unit) is None:
                    raise ic.EmptyAttribute(obj.logical_name, 3)
                else:
                    if (s := cdt.get_unit_scaler(s_u.unit.contents)) != 0:
                        s_u = s_u.copy()
                        s_u.scaler.set(int(s_u.scaler)-s)
                    return s_u
            case ClassID.LIMITER, 3 | 4 | 5:
                obj: Limiter
                if m_v := obj.monitored_value:
                    return self.get_scaler_unit(
                        obj=self.get_object(m_v.logical_name),
                        par=m_v.contents,
                        a_val=a_val)  # recursion 1 level
                else:
                    raise ic.EmptyAttribute(obj.logical_name, 2)
            case _:
                return None

    def filter_by_ass(self, ass_id: int) -> list[InterfaceClass]:
        """return only association objects"""
        ret = list()
        for olt in self.getASSOCIATION(ass_id).object_list:
            ret.append(self.__get_object(olt.logical_name.contents))
        return ret

    def get_objects_list(self, value: enums.ClientSAP) -> list[ic.COSEMInterfaceClasses]:
        for association in self.get_objects_by_class_id(ut.CosemClassId(15)):
            if association.associated_partners_id.client_SAP == value and association.logical_name.e != 0:
                if association.object_list is None:
                    raise exc.EmptyObj(F'{association} attr: 2')
                else:
                    ret = list()
                    for el in association.object_list:
                        ret.append(self.__get_object(el.logical_name.contents))
                    return ret
        else:
            raise ValueError(F'Not found association with client SAP: {value}')

    def get_attr(self, value: ut.CosemAttributeDescriptor) -> cdt.CommonDataTypes:
        """attribute value from descriptor"""
        return self.__get_object(value.instance_id.contents).get_attr(int(value.attribute_id))

    def get_first(self, values: list[str | bytes | cst.LogicalName]) -> InterfaceClass:
        """ return first object from it exist in collection from value"""
        for val in values:
            if self.is_in_collection(val):
                return self.get_object(val)
            else:
                """search next"""
        else:
            raise exc.NoObject(F"not found at least one DLMS Objects from collection with {values=}")

    def get_objects_by_class_id(self, value: ut.CosemClassId) -> list[InterfaceClass]:
        return list(filter(lambda obj: obj.CLASS_ID == value, self.__container.values()))

    def get_objects_descriptions(self) -> list[tuple[cst.LogicalName, cdt.LongUnsigned, cdt.Unsigned]]:
        """ return container of objects for get device clone """
        return list(map(lambda obj: (obj.logical_name, obj.CLASS_ID, obj.VERSION), self.__container.values()))

    def get_writable_attr(self) -> UsedAttributes:
        """return all writable {obj.ln: {attribute_index}}"""
        ret: UsedAttributes = dict()
        for ass in filter(lambda it: it.logical_name.e != 0, self.get_objects_by_class_id(ClassID.ASSOCIATION_LN)):
            for list_type in ass.object_list:
                for attr_access in list_type.access_rights.attribute_access:
                    if attr_access.access_mode.is_writable():
                        if ret.get(list_type.logical_name, None) is None:
                            ret[list_type.logical_name] = set()
                        ret[list_type.logical_name].add(int(attr_access.attribute_id))
        return ret

    def copy_obj_attr_values_from(self, other: InterfaceClass) -> bool:
        """ copy all attributes value from other and return bool result """
        try:
            obj: InterfaceClass = self.__get_object(other.get_obis())
            for i, attr in other.get_index_with_attributes(in_init_order=True):
                if i == 1:
                    continue
                else:
                    if attr is not None:
                        obj.set_attr(i, attr.encoding)
            return True
        except exc.NoObject as e:
            return False

    def copy_objects_attr_values_from(self, other: Collection) -> bool:
        """ Copy collections values and return True if all was writen """
        if len(other) != 0:
            return bool(reduce(lambda a, b: a or b, map(self.copy_obj_attr_values_from, other.values())))
        else:
            return False

    @property
    def current_time(self) -> datetime.datetime | None:
        return self.clock.get_current_time()

    def change_association_version(self, version: cdt.Unsigned):
        """ change Association version with clear attributes """
        logger.warning(F'Attention. ALL Association attributes will to default')
        for ass in self.get_objects_by_class_id(ut.CosemClassId(15)):
            self.__container.pop(ass.logical_name.contents)
            self.add(
                class_id=ut.CosemClassId(15),
                version=version,
                logical_name=ass.logical_name)

    def __get_object(self, obis: bytes) -> InterfaceClass:
        if (obj := self.__container.get(obis)) is None:
            logical_name = cst.LogicalName(bytearray(obis))
            raise exc.NoObject(F"{get_name(logical_name)}:{logical_name} is absence")
        else:
            return obj

    @cached_property
    def LDN(self) -> impl.data.LDN:
        return self.__get_object(o.LDN)

    @cached_property
    def current_association(self) -> AssociationLN:
        return self.__get_object(o.CURRENT_ASSOCIATION)

    def getASSOCIATION(self, instance: int) -> AssociationLN:
        return self.__get_object(bytes((0, 0, 40, 0, instance, 255)))

    def getAssociationBySAP(self, SAP: enums.ClientSAP) -> AssociationLN:
        return self.__get_object(bytes((0, 0, 40, 0, self.get_association_id(SAP), 255)))

    @cached_property
    def PUBLIC_ASSOCIATION(self) -> AssociationLN:
        return self.__get_object(bytes((0, 0, 40, 0, 1, 255)))

    @property
    def COMMUNICATION_PORT_PARAMETER(self) -> impl.data.CommunicationPortParameter:
        return self.__get_object(bytes((0, 0, 96, 12, 4, 255)))

    @property
    def clock(self) -> Clock:
        return self.__get_object(bytes((0, 0, 1, 0, 0, 255)))

    @property
    def activity_calendar(self) -> ActivityCalendar:
        return self.__get_object(bytes((0, 0, 13, 0, 0, 255)))

    @property
    def special_day_table(self) -> SpecialDaysTable:
        return self.__get_object(bytes((0, 0, 11, 0, 0, 255)))

    def getIECHDLCSetup(self, ch: int = 0) -> IECHDLCSetup:
        return self.__get_object(bytes((0, ch, 22, 0, 0, 255)))

    @cached_property
    def TCP_UDP_setup(self) -> TCPUDPSetup:
        return self.__get_object(bytes((0, 0, 25, 0, 0, 255)))

    def getIPv4Setup(self, ch: int = 0) -> IPv4Setup:
        return self.__get_object(bytes((0, ch, 25, 1, 0, 255)))

    @property
    def IPv4_setup(self) -> IPv4Setup:
        return self.__get_object(bytes((0, 0, 25, 1, 0, 255)))

    @property
    def boot_image_transfer(self) -> ImageTransfer:
        return self.__get_object(bytes((0, 0, 44, 0, 128, 255)))

    @property
    def firmware_image_transfer(self) -> ImageTransfer:
        return self.__get_object(bytes((0, 0, 44, 0, 0, 255)))

    @property
    def RU_EXTENDED_PASSPORT_DATA(self) -> ProfileGeneric:
        return self.__get_object(bytes((0, 0, 94, 7, 1, 255)))

    @property
    def firmware_version(self) -> Data:
        return self.__get_object(bytes((0, 0, 96, 1, 2, 255)))

    @cached_property
    def device_type(self) -> Data:
        return self.__get_object(bytes((0, 0, 96, 1, 1, 255)))

    @property
    def manufacturing_date(self) -> Data:
        return self.__get_object(bytes((0, 0, 96, 1, 4, 255)))

    @property
    def RU_LOAD_LOCK_STATUS(self) -> Data:
        return self.__get_object(bytes((0, 0, 96, 4, 3, 255)))

    @property
    def firmwares_description(self) -> Data:
        """ Consist from boot_version, descriptor, ex.: 0005PWRM_M2M_3_F1_5ppm_Spvq. 0.0.128.100.0.255 """
        return self.__get_object(bytes((0, 0, 128, 100, 0, 255)))

    @property
    def serial_number(self) -> Data:
        """ Ex.: 0101000434322 """
        return self.__get_object(bytes((0, 0, 96, 1, 0, 255)))

    @property
    def RU_MAGNETIC_EFFECT(self) -> Data:
        """ Russian. СПОДЕСv3 E.12.3 """
        return self.__get_object(bytes((0, 0, 96, 51, 3, 255)))

    @property
    def RU_HF_FIELD_EFFECT(self) -> Data:
        """ Russian. СПОДЕСv3 E.12.4 """
        return self.__get_object(bytes((0, 0, 96, 51, 4, 255)))

    @property
    def RU_ELECTRIC_SEAL_STATUS(self) -> impl.data.SealStatus:
        """ Russian. СПОДЕС Г.2 """
        return self.__get_object(bytes((0, 0, 96, 51, 5, 255)))

    @property
    def RU_CLOSE_ELECTRIC_SEAL(self) -> Data:
        """ Russian. СПОДЕС Г.2 """
        return self.__get_object(bytes((0, 0, 96, 51, 6, 255)))

    @property
    def RU_ERASE_MAGNETIC_EVENTS(self) -> Data:
        """ Russian. СПОДЕС Г.2 """
        return self.__get_object(bytes((0, 0, 96, 51, 7, 255)))

    @property
    def RU_ALARM_REGISTER_2(self) -> Data:
        """ Russian. Alarm register relay"""
        return self.__get_object(bytes((0, 0, 97, 98, 1, 255)))

    @property
    def RU_FILTER_ALARM_2(self) -> Data:
        """ Russian. Filter of Alarm register relay"""
        return self.__get_object(bytes((0, 0, 97, 98, 11, 255)))

    @property
    def RU_DAILY_PROFILE(self) -> ProfileGeneric:
        """ Russian. Profile of daily values """
        return self.__get_object(bytes((1, 0, 98, 2, 0, 255)))

    @property
    def RU_MAXIMUM_CURRENT_EXCESS_LIMIT(self) -> Register:
        """ RU. СТО 34.01-5.1-006-2021 ver3, 11.1. Maximum current excess limit before the subscriber is disconnected, % of IMAX """
        return self.__get_object(bytes((1, 0, 11, 134, 0, 255)))

    @property
    def RU_MAXIMUM_VOLTAGE_EXCESS_LIMIT(self) -> Register:
        """ RU. СТО 34.01-5.1-006-2021 ver3, 11.1. Maximum voltage excess limit before the subscriber is disconnected, % of Unominal """
        return self.__get_object(bytes((1, 0, 12, 134, 0, 255)))

    def getDISCONNECT_CONTROL(self, ch: int = 0) -> DisconnectControl:
        """DLMS UA 1000-1 Ed 14 6.2.46 Disconnect control objects by channel"""
        return self.__get_object(bytes((0, ch, 96, 3, 10, 255)))

    def getARBITRATOR(self, ch: int = 0) -> Arbitrator:
        """DLMS UA 1000-1 Ed 14 6.2.47 Arbitrator objects objects by channel"""
        return self.__get_object(bytes((0, ch, 96, 3, 20, 255)))

    @property
    def boot_version(self) -> str:
        try:
            return self.firmwares_description.value.to_str()[:4]
        except Exception as e:
            print(e)
            return 'unknown'

    def get_script_names(self, ln: cst.LogicalName, selector: cdt.LongUnsigned) -> str:
        """return name from script by selector"""
        obj = self.__get_object(bytes(ln))
        if isinstance(obj, ScriptTable):
            for script in obj.scripts:
                script: ScriptTable.scripts
                if script.script_identifier == selector:
                    names: list[str] = list()
                    for action in script.actions:
                        action_obj = self.__get_object(bytes(action.logical_name))
                        if int(action_obj.CLASS_ID) != int(action.class_id):
                            raise ValueError(F"got {action_obj.CLASS_ID}, expected {action.class_id}")
                        match int(action.service_id):
                            case 1:  # for write
                                if isinstance(action.parameter, cdt.NullData):
                                    names.append(str(action_obj.get_attr_element(int(action.index))))
                                else:
                                    raise TypeError(F"not support by framework")  # TODO: make it
                            case 2:  # for execute
                                if isinstance(action.parameter, cdt.NullData):
                                    names.append(str(action_obj.get_meth_element(int(action.index))))
                                else:
                                    raise TypeError(F"not support by framework")  # TODO: make it
                    return ", ".join(names)
            else:
                raise ValueError(F"not find {selector} in {obj}")
        else:
            raise ValueError(F"object with {ln} is not {ScriptTable.CLASS_ID}")

    @lru_cache(4)
    def get_association_id(self, client_sap: enums.ClientSAP) -> int:
        """return id(association instance) from it client address without current"""
        for ass in get_filtered(iter(self), (ln_pattern.NON_CURRENT_ASSOCIATION,)):
            if ass.associated_partners_id.client_SAP == client_sap:
                return ass.logical_name.e
            else:
                continue
        else:
            raise ValueError(F"absent association with {client_sap}")

    @lru_cache(maxsize=1000)
    def is_readable(self, ln: cst.LogicalName,
                    index: int,
                    association_id: int,
                    security_policy: pdu.SecurityPolicy = pdu.SecurityPolicyVer0.NOTHING
                    ) -> bool:
        return self.getASSOCIATION(association_id).is_readable(
            ln=ln,
            index=index,
            security_policy=security_policy
        )

    @lru_cache(maxsize=1000)
    def is_writable(self, ln: cst.LogicalName,
                    index: int,
                    association_id: int,
                    security_policy: pdu.SecurityPolicy = pdu.SecurityPolicyVer0.NOTHING
                    ) -> bool:
        return self.getASSOCIATION(association_id).is_writable(
            ln=ln,
            index=index,
            security_policy=security_policy
        )

    @lru_cache(maxsize=1000)
    def is_accessible(self, ln: cst.LogicalName,
                      index: int,
                      association_id: int,
                      m_id: mechanism_id.MechanismIdElement = None
                      ) -> bool:
        """for ver 0 and 1 only"""

        return self.getASSOCIATION(association_id).is_accessible(
            ln=ln,
            index=index,
            m_id=m_id
        )

    @lru_cache(maxsize=100)
    def get_name_and_type(self, value: structs.CaptureObjectDefinition) -> tuple[list[str], Type[cdt.CommonDataType]]:
        """ return names and type of element from collection"""
        names: list[str] = list()
        obj = self.__get_object(value.logical_name.contents)
        names.append(get_name(obj.logical_name))
        attr_index = int(value.attribute_index)
        data_index = int(value.data_index)
        data_type: Type[cdt.CommonDataType] = obj.get_attr_data_type(attr_index)
        names.append(str(obj.get_attr_element(attr_index)))
        if data_index == 0:
            pass
        elif issubclass(data_type, cdt.Structure):
            if len(data_type.ELEMENTS) < data_index:
                raise ValueError(F"can't create buffer_struct_type for {self}, got {data_index=} in struct {data_type.__name__}, expected 1..{len(data_type.ELEMENTS)}")
            else:
                el: cdt.StructElement = data_type.ELEMENTS[data_index - 1]
                names.append(el.NAME)
                data_type = el.TYPE
        elif isinstance(obj, ProfileGeneric) and attr_index == 2:
            """according to DLMS UA 1000-1 Ed 14. ProfileGeneric.capture_object.data_index annex"""
            return self.get_name_and_type(obj.capture_objects[data_index - 1])  # todo: is recurse need rewrite here
        else:
            pass
        return names, data_type

    def get_attr_tree(self,
                      ass_id: int,
                      obj_mode: ObjectTreeMode = "c",
                      obj_filter: tuple[ClassID | media_id.MediaId | LNPattern, ...] = None,
                      sort_mode: SortMode = "",
                      af_mode: Literal["l", "r", "w", "lr", "lw", "wr", "lrw"] = "l",
                      ai_filter: tuple[tuple[ClassID, tuple[int, ...]], ...] = None    # todo: maybe ai_filter with LNPattern, indexes need?
                      ) -> dict[ClassID | media_id.MediaId, dict[ic.COSEMInterfaceClasses, list[int]]] | dict[ic.COSEMInterfaceClasses, list[int]]:  # todo: not all ret annotation
        """af_mode(attribute filter mode): l-reduce logical_name, r-show only readable, w-show only writeable,
        attr_filter(attribute index filter), example: ((ClassID.REGISTER, (2,))) - is restricted for Register only Value attribute without logical_name and scaler_unit
        """
        without_ln = True if "l" in af_mode else False
        only_read = True if "r" in af_mode else False
        only_write = True if "w" in af_mode else False
        ai_f = dict(ai_filter) if ai_filter else dict()
        filtered = self.filter_by_ass(ass_id)
        if obj_filter:
            filtered = get_filtered(filtered, obj_filter)
        ret = get_object_tree(
            objects=get_sorted(
                objects=filtered,
                mode=sort_mode),
            mode=obj_mode)
        stack = [(None, None, ret)]
        while len(stack) != 0:
            d, k, v = stack.pop()
            if isinstance(d, dict):
                for k_, v_ in tuple(d.items()):
                    if len(v_) == 0:
                        d.pop(k_)
            if isinstance(v, list):
                objects = dict()
                for obj in v:
                    obj: ic.COSEMInterfaceClasses
                    indexes = list()
                    for i, attr in obj.get_index_with_attributes():
                        if without_ln and i == 1:
                            continue
                        elif only_read and not self.is_readable(obj.logical_name, i, ass_id):
                            continue
                        elif only_write and not self.is_writable(obj.logical_name, i, ass_id):
                            continue
                        elif (attrs := ai_f.get(obj.CLASS_ID)) and i not in attrs:
                            continue
                        else:
                            indexes.append(i)
                    if len(indexes) != 0:
                        objects[obj] = indexes
                if d is None:
                    return objects
                if len(objects) != 0:
                    d[k] = objects
                else:
                    d.pop(k)
            elif isinstance(v, dict):
                for k_, v_ in v.items():
                    stack.append((v, k_, v_))
            else:
                raise ValueError('not support')
        return ret

    # def decode(self, file_name: str,
    #            root_tag: str = TagsName.DEVICE_ROOT.value):
    #     objects = self.__get_base_xml_element(root_tag)
    #     objects.attrib["decode"] = "1"
    #     for obj in self:
    #         try:
    #             object_node = ET.SubElement(
    #                 objects,
    #                 "object",
    #                 attrib={
    #                     "ln": str(obj.logical_name),
    #                     "name": obj.NAME
    #                 })
    #             for i in tuple(indexes):
    #                 attr = obj.get_attr(i)
    #                 if isinstance(attr, cdt.CommonDataType):
    #                     attr_el = ET.SubElement(
    #                         object_node,
    #                         "attr",
    #                         {"name": obj.get_attr_element(i).NAME,
    #                          "index": str(i)})
    #                     if isinstance(attr, cdt.SimpleDataType):
    #                         attr_el.text = str(attr)
    #                     elif isinstance(attr, cdt.ComplexDataType):
    #                         attr_el.attrib["type"] = "array" if attr.TAG == b'\x01' else "struct"  # todo: make better
    #                         stack: list = [(attr_el, "attr_el_name", iter(attr))]
    #                         while stack:
    #                             node, name, value_it = stack[-1]
    #                             value = next(value_it, None)
    #                             if value:
    #                                 if not isinstance(name, str):
    #                                     name = next(name).NAME
    #                                 if isinstance(value, cdt.Array):
    #                                     stack.append((ET.SubElement(node,
    #                                                                 "array",
    #                                                                 attrib={"name": name}), "ar_name", iter(value)))
    #                                 elif isinstance(value, cdt.Structure):
    #                                     stack.append((ET.SubElement(node, "struct"), iter(value.ELEMENTS), iter(value)))
    #                                 else:
    #                                     ET.SubElement(node,
    #                                                   "simple",
    #                                                   attrib={"name": name}).text = str(value)
    #                             else:
    #                                 stack.pop()
    #                     indexes.remove(i)
    #                 else:
    #                     logger.error(F"skip record {obj}:attr={i} with value={attr}")
    #             if len(used[ln]) == 0:
    #                 used.pop(ln)
    #         except exc.NoObject as e:
    #             logger.warning(F"skip obj with {ln=} in {collections.index(col)} collection: {e}")
    #             continue
    #     with open(
    #             file_name,
    #             mode="wb") as f:
    #         f.write(ET.tostring(
    #             element=objects,
    #             encoding="utf-8",
    #             method="xml",
    #             xml_declaration=True))


def get_base_template_xml_element(collections: list[Collection], root_tag: str = TagsName.DEVICE_ROOT.value) -> ET.Element:
    objects = ET.Element(root_tag, attrib={'version': '4.1.0'})
    ET.SubElement(objects, 'dlms_ver').text = str(collections[0].dlms_ver)
    ET.SubElement(objects, 'country').text = str(collections[0].country.value)
    ET.SubElement(objects, 'country_ver').text = str(collections[0].country_ver)
    for col in collections:
        manufacture_node = ET.SubElement(objects, 'manufacturer')
        manufacture_node.text = col.manufacturer.decode("utf-8")
        server_type_node = ET.SubElement(manufacture_node, 'server_type')
        server_type_node.text = col.server_type.encoding.hex()
        for ver in col.server_ver:
            server_ver_node = ET.SubElement(server_type_node, 'server_ver', attrib={"instance": str(ver)})
            server_ver_node.text = str(col.server_ver[ver])
    return objects


def to_xml4(collections: list[Collection],
            file_name: str,
            used: UsedAttributes,
            verified: bool = False):
    """For template only"""
    used_copy = copy.deepcopy(used)
    objects = get_base_template_xml_element(
        collections=collections,
        root_tag=TagsName.TEMPLATE_ROOT.value)
    objects.attrib["decode"] = "1"
    if verified:
        objects.attrib["verified"] = "1"
    for col in collections:
        for ln, indexes in copy.copy(used_copy).items():
            try:
                obj = col.get_object(ln)
                object_node = ET.SubElement(
                    objects,
                    "object",
                    attrib={"ln": str(obj.logical_name)})
                for i in tuple(indexes):
                    attr = obj.get_attr(i)
                    if isinstance(attr, cdt.CommonDataType):
                        attr_el = ET.SubElement(
                            object_node,
                            "attr",
                            {"name": obj.get_attr_element(i).NAME,
                             "index": str(i)})
                        if isinstance(attr, cdt.SimpleDataType):
                            attr_el.text = str(attr)
                        elif isinstance(attr, cdt.ComplexDataType):
                            attr_el.attrib["type"] = "array" if attr.TAG == b'\x01' else "struct"  # todo: make better
                            stack: list = [(attr_el, "attr_el_name", iter(attr))]
                            while stack:
                                node, name, value_it = stack[-1]
                                value = next(value_it, None)
                                if value:
                                    if not isinstance(name, str):
                                        name = next(name).NAME
                                    if isinstance(value, cdt.Array):
                                        stack.append((ET.SubElement(node,
                                                                    "array",
                                                                    attrib={"name": name}), "ar_name", iter(value)))
                                    elif isinstance(value, cdt.Structure):
                                        stack.append((ET.SubElement(node, "struct"), iter(value.ELEMENTS), iter(value)))
                                    else:
                                        ET.SubElement(node,
                                                      "simple",
                                                      attrib={"name": name}).text = str(value)
                                else:
                                    stack.pop()
                        indexes.remove(i)
                    else:
                        logger.error(F"skip record {obj}:attr={i} with value={attr}")
                if len(indexes) == 0:
                    used_copy.pop(ln)
            except exc.NoObject as e:
                logger.warning(F"skip obj with {ln=} in {collections.index(col)} collection: {e}")
                continue
        if len(used_copy) == 0:
            logger.info(F"success decoding: used {collections.index(col)+1} from {len(collections)} collections")
            break
    if len(used_copy) != 0:
        raise ValueError(F"failed decoding: {used_copy}")
    with open(
            file_name,
            mode="wb") as f:
        f.write(ET.tostring(
            element=objects,
            encoding="utf-8",
            method="xml",
            xml_declaration=True))


def from_xml4(filename: str) -> tuple[list[Collection], UsedAttributes, bool]:
    """ create collection from xml for template and UsedAttributes """
    used: UsedAttributes = dict()
    cols = list()
    tree = ET.parse(filename)
    objects = tree.getroot()
    if objects.tag != TagsName.TEMPLATE_ROOT.value:
        raise ValueError(F"ERROR: Root tag got {objects.tag}, expected {TagsName.TEMPLATE_ROOT.value}")
    root_version: AppVersion = AppVersion.from_str(objects.attrib.get('version', '1.0.0'))
    logger.info(F'Версия: {root_version}, file: {filename.split("/")[-1]}')
    for manufacturer_node in objects.findall("manufacturer"):
        for server_type_node in manufacturer_node.findall("server_type"):
            for server_ver_node in server_type_node.findall("server_ver"):
                cols.append(get_collection(
                    manufacturer=manufacturer_node.text.encode("utf-8"),
                    server_type=cdt.get_instance_and_pdu_from_value(bytes.fromhex(server_type_node.text))[0],
                    server_ver=AppVersion.from_str(server_ver_node.text)))
    match root_version:
        case AppVersion(4, 0 | 1):
            for obj in objects.findall('object'):
                ln: str = obj.attrib.get("ln", 'is absence')
                logical_name: cst.LogicalName = cst.LogicalName(ln)
                objs: list[ic.COSEMInterfaceClasses] = list()
                for col in cols:
                    if not col.is_in_collection(logical_name):
                        logger.warning(F"got object with {ln=} not find in collection: {col}")
                    else:
                        objs.append(col.get_object(logical_name))
                used[logical_name] = set()
                for attr in obj.findall("attr"):
                    index: int = int(attr.attrib.get("index"))
                    used[logical_name].add(index)
                    try:
                        match attr.attrib.get("type", "simple"):
                            case "simple":
                                for new_object in objs:
                                    new_object.set_attr(index, attr.text)
                            case "array" | "struct":
                                stack = [(list(), iter(attr))]
                                while stack:
                                    v1, v2 = stack[-1]
                                    v = next(v2, None)
                                    if v is None:
                                        stack.pop()
                                    elif v.tag == "simple":
                                        v1.append(v.text)
                                    else:
                                        v1.append(list())
                                        stack.append((v1[-1], iter(v)))
                                for new_object in objs:
                                    new_object.set_attr(index, v1)
                    except exc.ITEApplication as e:
                        logger.error(F"Can't fill {new_object} attr: {index}. {e}")
                    except IndexError:
                        logger.error(F'Object "{new_object}" not has attr: {index}')
                    except TypeError as e:
                        logger.error(F'Object {new_object} attr:{index} do not write, encoding wrong : {e}')
                    except ValueError as e:
                        logger.error(F'Object {new_object} attr:{index} do not fill: {e}')
                    except AttributeError as e:
                        logger.error(F'Object {new_object} attr:{index} do not fill: {e}')
        case _ as error:
            raise exc.VersionError(error, additional='Xml')
    return cols, used, bool(int(objects.findtext("verified", default="0")))


if config is not None:
    try:
        __collection_path = config['DLMS']['collection']['path']
    except KeyError as e:
        raise exc.TomlKeyError(F"not find {e} in [DLMS.collection]<path>")


@lru_cache(1)
def get_manufactures_container() -> dict[bytes, dict[bytes, dict[AppVersion, os.DirEntry]]]:
    ret: dict[bytes, dict[bytes, dict[AppVersion, os.DirEntry]]] = dict()
    with os.scandir(__collection_path) as ms:
        for m in ms:
            if len(m.name) == 3 and m.is_dir():
                ret[man := m.name.encode("ascii")] = dict()
                with os.scandir(m) as ts:
                    for t in ts:
                        if t.is_dir():
                            ret[man][server_type := bytes.fromhex(t.name)] = dict()
                            with os.scandir(t) as vs:
                                for ver in vs:
                                    if ver.is_file() and (v := ver.name.partition(".typ"))[1] == ".typ":
                                        ret[man][server_type][AppVersion.from_str(v[0])] = ver
    return ret


@lru_cache(maxsize=100)
def get_dir_entry(m: bytes, t: cdt.CommonDataType, ver: AppVersion) -> os.DirEntry:
    """one recursion collection get way. ret: file, is_searched"""  # todo: make <ver> handle non SemVer from CDT
    if (man := get_manufactures_container().get(m)) is None:
        raise exc.NoConfig(F"no support manufacturer: {m.decode('utf-8', errors='strict')}")
    elif (type_ := man.get(t.encoding)) is None:
        raise exc.NoConfig(F"no support type {t.to_str()}, with manufacturer: {m.decode('utf-8', errors='strict')}")
    elif (f := type_.get(ver)) is None:
        if searched_version := ver.select_nearest(type_.keys()):
            return type_.get(searched_version)
        else:
            raise exc.NoConfig(F"no support version {ver} with manufacturer: {m.decode('utf-8', errors='strict')}, type: {t.to_str()}")
    logger.info(F"got collection from library by path: {f.path}")
    return f


@lru_cache(maxsize=100)
def get(m: bytes, t: cdt.CommonDataType, ver: AppVersion) -> Collection:
    """caching collection"""
    return Collection.from_xml(get_dir_entry(m, t, ver))


def get_collection(
        manufacturer: bytes,
        server_type: cdt.CommonDataType,
        server_ver: AppVersion,
) -> Collection:
    """get copy of collection with caching"""
    ret = get(manufacturer, server_type, server_ver).copy()
    ret.set_server_type(server_type)  # if xml file not contains the type
    return ret


def get_ln_contents(value: LNContaining) -> bytes:
    """return LN as bytes[6] for use in any searching"""
    match value:
        case bytes():                                                    return value
        case cst.LogicalName() | ut.CosemObjectInstanceId():             return value.contents
        case ut.CosemAttributeDescriptor() | ut.CosemMethodDescriptor(): return value.instance_id.contents
        case ut.CosemAttributeDescriptorWithSelection():                 return value.cosem_attribute_descriptor.instance_id.contents
        case cdt.Structure(logical_name=value.logical_name):             return value.logical_name.contents
        case cdt.Structure() as s:
            s: cdt.Structure
            for it in s:
                if isinstance(it, cst.LogicalName):
                    return it.contents
            raise ValueError(F"can't convert {value=} to Logical Name contents. Struct {s} not content the Logical Name")
        case str():                                                      return cst.LogicalName(value).contents
        case _:                                                          raise ValueError(F"can't convert {value=} to Logical Name contents")


class AttrDesc:
    """keep constant descriptors"""
    OBJECT_LIST = ut.CosemAttributeDescriptor((ClassID.ASSOCIATION_LN, ut.CosemObjectInstanceId("0.0.40.0.0.255"), ut.CosemObjectAttributeId(2)))
    LDN_VALUE = ut.CosemAttributeDescriptor((ClassID.DATA, ut.CosemObjectInstanceId("0.0.42.0.0.255"), ut.CosemObjectAttributeId(2)))


__range10_and_255: tuple = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 255
__range63: tuple = tuple(range(0, 64))
__range120_and_124_127: tuple = tuple(chain(range(0, 121), range(124, 128)))
__range100_and_255: tuple = tuple(chain(range(0, 100), (255,)))
__range100_and_101_125_and_255: tuple = tuple(chain(__range100_and_255, range(101, 126)))
__c1: tuple = tuple(chain(range(1, 10), (13, 14, 33, 34, 53, 54, 73, 74, 82), range(16, 31), range(36, 51), range(56, 70), range(76, 81), range(84, 90)))
"""DLMS UA 1000-1 Ed 14. Table 45 c1"""
__table44: tuple = (11, 12, 15, 31, 32, 35, 51, 52, 55, 71, 72, 75, 90, 91, 92)
"""DLMS UA 1000-1 Ed 14. Table 44 for active power"""
__c2: tuple = tuple(chain(__table44, range(100, 108)))
"""DLMS UA 1000-1 Ed 14. Table 45 c2"""


def get_media_id(ln: cst.LogicalName) -> media_id.MediaId:
    return media_id.MediaId.from_int(ln.a)


def get_class_id(obj: InterfaceClass) -> ClassID:
    return obj.CLASS_ID


def get_map_by_obj(objects: list[InterfaceClass] | tuple[InterfaceClass], key: Callable[[InterfaceClass], ...]) -> dict[media_id.MediaId, list[InterfaceClass]]:
    ret = dict()
    for obj in objects:
        if ret.get(new_key := key(obj)):
            ret[new_key].append(obj)
        else:
            ret[new_key] = [obj]
    return ret


def get_object_tree(objects: list[InterfaceClass] | tuple[InterfaceClass],
                    mode: ObjectTreeMode) -> dict[media_id.MediaId | ClassID, list[InterfaceClass]]:
    """mode: m-media_id, g-relation_group, c-class_id"""
    mode = list(mode)
    ret = objects
    while mode:
        match mode.pop():
            case "m":
                key = lambda obj: get_media_id(obj.logical_name)
            case "g":
                key = lambda obj: get_relation_group(obj.logical_name)
            case "c":
                key = get_class_id
            case _:
                raise KeyError(F"got unknown {mode=} for get_map")
        stack = [(None, None, ret)]
        while len(stack) != 0:
            d, k, v = stack.pop()
            if isinstance(v, list):
                res = get_map_by_obj(v, key)
                if d is None:
                    ret = res
                else:
                    d[k] = res
            elif isinstance(v, dict):
                stack.extend(((v, k_, v_) for k_, v_ in v.items()))
            else:
                raise ValueError('not support')
    return ret


def get_sorted(objects: list[InterfaceClass],
               mode: SortMode) -> list[InterfaceClass]:
    """mode: l-logical_name, n-name, c-class_id
    """
    mode = list(mode)
    while mode:
        match mode.pop():
            case "l":
                key = None
            case "n":
                key = lambda obj: get_name(obj.logical_name)
            case "c":
                key = lambda obj: obj.CLASS_ID
            case _:
                raise KeyError(F"got unknown {mode=} for get_map")
        objects = sorted(objects, key=key)
    return objects


def get_filtered(objects: Iterable[InterfaceClass],
                 keys: tuple[ClassID | LNPattern | LNPatterns, ...]) -> list[InterfaceClass]:
    c_ids: list[ut.CosemClassId] = list()
    patterns: list[LNPattern] = list()
    for k in keys:
        if isinstance(k, ut.CosemClassId):
            c_ids.append(k)
        elif isinstance(k, LNPattern):
            patterns.append(k)
        elif isinstance(k, LNPatterns):
            patterns.extend(k)
    new_list = list()
    for obj in objects:
        if c_ids and (obj.CLASS_ID not in c_ids):
            continue
        if patterns and (obj.logical_name not in patterns):
            continue
        new_list.append(obj)
    return new_list


RelationGroup: TypeAlias = media_id.Abstract | media_id.Electricity | media_id.Hca | media_id.Gas | media_id.Thermal | media_id.Water | media_id.Other
RelationGroups: tuple[media_id.MediaId, ...] = (media_id.ABSTRACT, media_id.ELECTRICITY, media_id.HCA, media_id.GAS, media_id.THERMAL, media_id.WATER)


@lru_cache(maxsize=1000)
def get_relation_group(ln: cst.LogicalName) -> RelationGroup:
    if ln.a == media_id.ABSTRACT:
        if ln.c == 0:
            if ln.d == 1:
                return media_id.BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES
            elif ln.d in (2, 9):
                return media_id.OTHER_ABSTRACT_GENERAL_PURPOSE_OBIS_CODES
        elif ln.c == 1:
            if ln.d in (0, 1, 2, 3, 4, 5, 6):
                return media_id.CLOCK_OBJECTS
        elif ln.c == 2:
            if ln.d in (0, 1, 2):
                return media_id.MODEM_CONFIGURATION_AND_RELATED_OBJECTS
        elif ln.c == 10 and ln.d == 0 and ln.e in (0, 1, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 125):
            return media_id.SCRIPT_TABLE_OBJECTS
        elif ln.c == 11 and ln.d == 0:
            return media_id.SPECIAL_DAYS_TABLE_OBJECTS
        elif ln.c == 12 and ln.d == 0:
            return media_id.SCHEDULE_OBJECTS
        elif ln.c == 13 and ln.d == 0:
            return media_id.ACTIVITY_CALENDAR_OBJECTS
        elif ln.c == 14 and ln.d == 0:
            return media_id.REGISTER_ACTIVATION_OBJECTS
        elif ln.c == 15 and ln.d == 0 and ln.e in (0, 1, 2, 3, 4, 5, 6, 7):
            return media_id.SINGLE_ACTION_SCHEDULE_OBJECTS
        elif ln.c == 16:
            if ln.d == 0 or (ln.d == 1 and ln.e in range(0, 10)):
                return media_id.REGISTER_OBJECTS_MONITOR
            elif ln.d == 2:
                return media_id.PARAMETER_MONITOR_OBJECTS
        elif ln.c == 17 and ln.d == 0:
            return media_id.LIMITER_OBJECTS
        elif ln.c == 18 and ln.d == 0:
            return media_id.ARRAY_MANAGER_OBJECT
        elif ln.c == 19:
            if (ln.d in range(0, 10) and ln.e == 0) or ln.d in range(10, 50) or ln.d in (range(50, 60) and ln.e in (1, 2)):
                return media_id.PAYMENT_METERING_RELATED_OBJECTS
        elif ln.c == 20 and ln.d == 0 and ln.e in (0, 1):
            return media_id.IEC_LOCAL_PORT_SETUP_OBJECTS
        elif ln.c == 21 and ln.d == 0:
            return media_id.STANDARD_READOUT_PROFILE_OBJECTS
        elif ln.c == 22 and ln.d == 0 and ln.e == 0:
            return media_id.IEC_HDLC_SETUP_OBJECTS
        elif ln.c == 23:
            if (ln.d in 0, 1, 2 and ln.e == 0) or ln.d == 3:
                return media_id.IEC_TWISTED_PAIR_1_SETUP_OBJECTS
        elif ln.c == 24:
            if (ln.d in (0, 1, 4, 5, 6) and ln.e == 0) or (ln.d in (2, 8, 9)):
                return media_id.OBJECTS_RELATED_TO_DATA_EXCHANGE_OVER_M_BUS
        elif ln.c == 31 and ln.d == 0 and ln.e == 0:
            return media_id.OBJECTS_RELATED_TO_DATA_EXCHANGE_OVER_M_BUS
        elif ln.c == 25:
            if ln.d in (0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15) and ln.e == 0:
                return media_id.OBJECTS_TO_SET_UP_DATA_EXCHANGE_OVER_THE_INTERNET
            elif ln.d == 9 and ln.e == 0:
                return media_id.OBJECTS_TO_SET_UP_PUSH_SETUP
        elif ln.c == 26 and ln.d in (0, 1, 2, 3, 5, 6) and ln.e == 0:
            return media_id.OBJECTS_FOR_SETTING_UP_DATA_EXCHANGE_USING_S_FSK_PLC
        elif ln.c == 27 and ln.d in (0, 1, 2) and ln.e == 0:
            return media_id.OBJECTS_FOR_SETTING_UP_THE_ISO_IEC_8802_2_LLC_LAYER
        elif ln.c == 28 and ln.d in (0, 1, 2, 3, 4, 5, 6, 7) and ln.e == 0:
            return media_id.OBJECTS_FOR_DATA_EXCHANGE_USING_NARROWBAND_OFDM_PLC_FOR_PRIME_NETWORKS
        elif ln.c == 29 and ln.d in (0, 1, 2) and ln.e == 0:
            return media_id.OBJECTS_FOR_DATA_EXCHANGE_USING_NARROW_BAND_OFDM_PLC_FOR_G3_PLC_NETWORKS
        elif ln.c == 30 and ln.d in (0, 1, 2, 3, 4):
            return media_id.ZIGBEE_SETUP_OBJECTS
        elif ln.c == 32 and ln.d in (0, 1, 2, 3) and ln.e == 0:
            return media_id.OBJECTS_FOR_SETTING_UP_AND_MANAGING_DATA_EXCHANGE_USING_ISO_IEC_14908_PLC_NETWORKS
        elif ln.c == 33 and ln.d in (0, 1, 2, 3) and ln.e == 0:
            return media_id.OBJECTS_FOR_DATA_EXCHANGE_USING_HS_PLC_ISO_IEC_12139_1_ISO_EC_12139_1_NETWORKS
        elif ln.c == 34 and ln.d in (0, 1, 2, 3) and ln.e == 0:
            return media_id.OBJECTS_FOR_DATA_EXCHANGE_USING_WI_SUN_NETWORKS
        elif ln.c == 40 and ln.b == 0 and ln.d == 0:
            return media_id.ASSOCIATION_OBJECTS
        elif ln.c == 41 and ln.b == 0 and ln.d == 0 and ln.e == 0:
            return media_id.SAP_ASSIGNMENT_OBJECT
        elif ln.c == 42 and ln.b == 0 and ln.d == 0 and ln.e == 0:
            return media_id.COSEM_LOGICAL_DEVICE_NAME_OBJECT
        elif ln.c == 43:
            if (ln.b == 0 and ln.d == 0) or ln.d in (1, 2):
                return media_id.INFORMATION_SECURITY_RELATED_OBJECTS
        elif ln.c == 44:
            if ln.b == 0:
                if ln.d == 0:
                    return media_id.IMAGE_TRANSFER_OBJECTS
                elif ln.d == 1:
                    return media_id.FUNCTION_CONTROL_OBJECTS
                elif ln.d == 2:
                    return media_id.COMMUNICATION_PORT_PROTECTION_OBJECTS
        elif ln.c == 65 and ln.d in __range63:
            return media_id.UTILITY_TABLE_OBJECTS
        elif ln.c == 66 and ln.d == 0:
            return media_id.COMPACT_DATA_OBJECTS
        elif ln.c == 96:
            if ln.d == 1:
                if ln.e in __range10_and_255:
                    return media_id.DEVICE_ID_OBJECTS
                elif ln.e == 10:
                    return media_id.METERING_POINT_ID_OBJECTS
            elif ln.d == 2:
                return media_id.PARAMETER_CHANGES_AND_CALIBRATION_OBJECTS
            elif ln.d == 3:
                if ln.e in (0, 1, 2, 3, 4):
                    return media_id.I_O_CONTROL_SIGNAL_OBJECTS
                elif ln.e == 10:
                    return media_id.DISCONNECT_CONTROL_OBJECTS
                elif ln.e in range(20, 30):
                    return media_id.ARBITRATOR_OBJECTS
            elif ln.d == 4 and ln.e in (0, 1, 2, 3, 4):
                return media_id.STATUS_OF_INTERNAL_CONTROL_SIGNALS_OBJECTS
            elif ln.d == 5 and ln.e in (0, 1, 2, 3, 4):
                return media_id.INTERNAL_OPERATING_STATUS_OBJECTS
            elif ln.d == 6 and ln.e in (0, 1, 2, 3, 4, 5, 6):
                return media_id.BATTERY_ENTRIES_OBJECTS
            elif ln.d == 7 and ln.e in range(0, 22):
                return media_id.POWER_FAILURE_MONITORING_OBJECTS
            elif ln.d == 8 and ln.e in __range63:
                return media_id.OPERATING_TIME_OBJECTS
            elif ln.d == 9 and ln.e in (0, 1, 2):
                return media_id.ENVIRONMENT_RELATED_PARAMETERS_OBJECTS
            elif ln.d == 10 and ln.e in range(1, 11):
                return media_id.STATUS_REGISTER_OBJECTS
            elif ln.d == 11 and ln.e in range(0, 100):
                return media_id.EVENT_CODE_OBJECTS
            elif ln.d == 12 and ln.e in range(0, 7):
                return media_id.COMMUNICATION_PORT_LOG_PARAMETER_OBJECTS
            elif ln.d == 13 and ln.e in (0, 1):
                return media_id.CONSUMER_MESSAGE_OBJECTS
            elif ln.d == 14 and ln.e in range(0, 16):
                return media_id.CURRENTLY_ACTIVE_TARIFF_OBJECTS
            elif ln.d == 15 and ln.e in range(0, 100):
                return media_id.EVENT_COUNTER_OBJECTS
            elif ln.d == 16 and ln.e in range(0, 10):
                return media_id.PROFILE_ENTRY_DIGITAL_SIGNATURE_OBJECTS
            elif ln.d == 17 and ln.e in range(0, 128):
                return media_id.PROFILE_ENTRY_COUNTER_OBJECTS
            elif ln.d == 20:
                return media_id.METER_TAMPER_EVENT_RELATED_OBJECTS
            elif ln.d in range(50, 100):
                return media_id.ABSTRACT_MANUFACTURER_SPECIFIC
        elif ln.c == 97:
            if ln.d == 97 and ln.e in __range10_and_255:
                return media_id.ERROR_REGISTER_OBJECTS
            elif ln.d == 98 and (ln.e in chain(range(0, 30), (255,))):
                return media_id.ALARM_REGISTER_FILTER_DESCRIPTOR_OBJECTS
        elif ln.c == 98:
            return media_id.GENERAL_LIST_OBJECTS
        elif ln.c == 99:
            if ln.d in (1, 2, 12, 13, 14, 15, 16, 17, 18) or (ln.d == 3 and ln.e == 0):
                return media_id.ABSTRACT_DATA_PROFILE_OBJECTS
            if ln.d == 98:
                return media_id.EVENT_LOG_OBJECTS
        elif ln.c == 127 and ln.d == 0:
            return media_id.INACTIVE_OBJECTS
        else:
            return media_id.ABSTRACT
    elif ln.a == media_id.ELECTRICITY:
        if ln.c == 0:
            if ln.d == 0 and ln.e in __range10_and_255:
                return media_id.ID_NUMBERS_ELECTRICITY
            elif ln.d == 1:
                return media_id.BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES_EL
            elif ln.d in (2, 3, 4, 6, 7, 8, 9, 10):
                return media_id.OTHER_ELECTRICITY_RELATED_GENERAL_PURPOSE_OBJECTS
            elif ln.d == 11 and ln.e in (1, 2, 3, 4, 5, 6, 7):
                return media_id.MEASUREMENT_ALGORITHM
        elif ln.c in (1, 21, 41, 61):
            return media_id.ACTIVE_POWER_PLUS
        elif ln.c in (2, 22, 42, 62):
            return media_id.ACTIVE_POWER_MINUS
        elif ln.c in (3, 23, 43, 63):
            return media_id.REACTIVE_POWER_PLUS
        elif ln.c in (4, 24, 44, 64):
            return media_id.REACTIVE_POWER_MINUS
        elif ln.c in (5, 25, 45, 65):
            return media_id.REACTIVE_POWER_QI
        elif ln.c in (6, 26, 46, 66):
            return media_id.REACTIVE_POWER_QII
        elif ln.c in (7, 27, 47, 67):
            return media_id.REACTIVE_POWER_QIII
        elif ln.c in (8, 28, 48, 68):
            return media_id.REACTIVE_POWER_QIV
        elif ln.c in (9, 29, 49, 69):
            return media_id.APPARENT_POWER_PLUS
        elif ln.c in (10, 30, 50, 70):
            return media_id.APPARENT_POWER_MINUS
        elif ln.c in (11, 31, 51, 71):
            return media_id.CURRENT
        elif ln.c in (12, 32, 52, 72):
            return media_id.VOLTAGE
        elif ln.c in (13, 33, 53, 73):
            return media_id.POWER_FACTOR
        elif ln.c in (14, 34, 54, 74):
            return media_id.SUPPLY_FREQUENCY
        elif ln.c in (15, 35, 55, 75):
            return media_id.ACTIVE_POWER_SUM
        elif ln.c in (16, 36, 56, 76):
            return media_id.ACTIVE_POWER_DIFF
        elif ln.c in (17, 37, 57, 77):
            return media_id.ACTIVE_POWER_QI
        elif ln.c in (18, 38, 58, 78):
            return media_id.ACTIVE_POWER_QII
        elif ln.c in (19, 39, 59, 79):
            return media_id.ACTIVE_POWER_QIII
        elif ln.c in (20, 40, 60, 80):
            return media_id.ACTIVE_POWER_QIV
        elif ln.c == 96:
            if ln.d == 1 and ln.e in __range10_and_255:
                return media_id.ELECTRICITY_METERING_POINT_ID_OBJECTS
            elif ln.d == 5 and ln.e in (0, 1, 2, 3, 4, 5):
                return media_id.ELECTRICITY_RELATED_STATUS_OBJECTS
            elif ln.d == 10 and ln.e in (0, 1, 2, 3):
                return media_id.ELECTRICITY_RELATED_STATUS_OBJECTS
        elif ln.c == 98:
            return media_id.LIST_OBJECTS_ELECTRICITY
        elif ln.d in range(31, 46) and ln.f in __range100_and_255:
            if ln.c in __c1 and ln.e in __range63:
                return media_id.THRESHOLD_VALUES
            elif ln.c in __table44 and ln.e in __range120_and_124_127:
                return media_id.THRESHOLD_VALUES
        elif ln.f in __range100_and_255:
            if ln.d in (31, 35, 39, 4, 5, 14, 15, 24, 25):
                if ln.c in __c1 and ln.e in __range63:
                    return media_id.REGISTER_MONITOR_OBJECTS
                elif ln.c in __c2 and ln.e in __range120_and_124_127:
                    return media_id.REGISTER_MONITOR_OBJECTS
        else:
            return media_id.ELECTRICITY
    elif ln.a == media_id.HCA:
        if ln.c == 0:
            if ln.d == 0 and ln.e in __range10_and_255:
                return media_id.ID_NUMBERS_HCA
            elif ln.d == 1 and ln.e in (1, 2, 10, 11):
                return media_id.BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES_HCA
            elif ln.d == 2 and ln.e in (0, 1, 2, 3):
                return media_id.GENERAL_PURPOSE_OBJECTS_HCA
            elif ln.d == 4 and ln.e in (0, 1, 2, 3, 4, 5, 6):
                return media_id.GENERAL_PURPOSE_OBJECTS_HCA
            elif ln.d == 5 and ln.e in (10, 11):
                return media_id.GENERAL_PURPOSE_OBJECTS_HCA
            elif ln.d == 8 and ln.e in (0, 4, 6):
                return media_id.GENERAL_PURPOSE_OBJECTS_HCA
            elif ln.d == 9 and ln.e in (1, 2, 3):
                return media_id.GENERAL_PURPOSE_OBJECTS_HCA
        elif ln.c in (1, 2) and ln.e == 0:
            if ln.d in (0, 6) and ln.f == 255:
                return media_id.MEASURED_VALUES_HCA_CONSUMPTION
            elif ln.d in (1, 2, 3, 4, 5) and ln.f in __range100_and_101_125_and_255:
                return media_id.MEASURED_VALUES_HCA_CONSUMPTION
        elif ln.c in range(3, 8) and ln.d in (0, 4, 5, 6) and ln.e == 255 and ln.f == 255:
            return media_id.MEASURED_VALUES_HCA_TEMPERATURE
        elif ln.c == 97 and ln.d == 97:
            return media_id.ERROR_REGISTER_OBJECTS_HCA
        elif ln.c == 98:
            return media_id.LIST_OBJECTS_HCA
        elif ln.c == 99 and ln.d == 1:
            return media_id.DATA_PROFILE_OBJECTS_HCA
        else:
            return media_id.HCA
    elif ln.a == media_id.THERMAL:
        if ln.c == 0:
            if ln.d == 0 and ln.e in __range10_and_255:
                return media_id.ID_NUMBERS_THERMAL
            elif ln.d == 1 and ln.e in (1, 2, 10, 11):
                return media_id.BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES_THERMAL
            elif ln.d == 2 and ln.e in chain(range(0, 5), range(10, 14)):
                return media_id.GENERAL_PURPOSE_OBJECTS_THERMAL
            elif ln.d == 4 and ln.e in (1, 2, 3):
                return media_id.GENERAL_PURPOSE_OBJECTS_THERMAL
            elif ln.d == 5 and ln.e in chain(range(1, 10), range(21, 25)):
                return media_id.GENERAL_PURPOSE_OBJECTS_THERMAL
            elif ln.d == 8 and ln.e in chain(range(0, 8), range(11, 15), range(21, 26), range(31, 35)):
                return media_id.GENERAL_PURPOSE_OBJECTS_THERMAL
            elif ln.d == 9 and ln.e in (1, 2, 3):
                return media_id.GENERAL_PURPOSE_OBJECTS_THERMAL
        elif ln.c in range(1, 8):
            if ln.e in range(10):
                if ln.d in (0, 1, 2, 3, 7) and ln.f == 255:
                    return media_id.MEASURED_VALUES_THERMAL_CONSUMPTION
                elif ln.d in (3, 8, 9) and ln.f in __range100_and_101_125_and_255:
                    return media_id.MEASURED_VALUES_THERMAL_CONSUMPTION
                elif ln.d in (1, 2, 4, 5, 12, 13, 14, 15) and ln.f in chain(range(100), range(100, 126)):
                    return media_id.MEASURED_VALUES_THERMAL_CONSUMPTION
            elif ln.d == 6 and ln.e == 255 and ln.f == 255:
                return media_id.MEASURED_VALUES_THERMAL_CONSUMPTION
        elif ln.e in range(10):
            if ln.f in __range100_and_101_125_and_255:
                if ln.c in range(1, 8) and ln.d in (5, 15):
                    return media_id.MEASURED_VALUES_THERMAL_ENERGY
                elif ln.c in (8, 9) and ln.d in (1, 4, 5, 12, 13, 14, 15):
                    return media_id.MEASURED_VALUES_THERMAL_ENERGY
            elif ln.c in range(10, 14):
                if ln.d == 0 and ln.f == 255:
                    return media_id.MEASURED_VALUES_THERMAL_ENERGY
                elif ln.d in (4, 5, 14, 15) and ln.f in chain(range(100), range(101, 126)):
                    return media_id.MEASURED_VALUES_THERMAL_ENERGY
                elif ln.d in (6, 7, 10, 11) and ln.f == 255:
                    return media_id.MEASURED_VALUES_THERMAL_ENERGY
            elif ln.c in range(1, 14) and (ln.d in range(20, 26)) and ln.f == 255:
                return media_id.MEASURED_VALUES_THERMAL_ENERGY
        elif ln.c == 97 and ln.d == 97 and ln.e in (0, 1, 2):
            return media_id.ERROR_REGISTER_OBJECTS_THERMAL
        elif ln.c == 98:
            return media_id.LIST_OBJECTS_THERMAL
        elif ln.c == 99 and ln.f == 255:
            if ln.d in (1, 2) and ln.e in (1, 2, 3):
                return media_id.DATA_PROFILE_OBJECTS_THERMAL
            elif ln.d == 3 and ln.e == 1:
                return media_id.DATA_PROFILE_OBJECTS_THERMAL
            elif ln.d == 99:
                return media_id.DATA_PROFILE_OBJECTS_THERMAL
        else:
            return media_id.THERMAL
    elif media_id.GAS == ln.a:
        if ln.c == 0:
            if ln.d == 0 and ln.e in __range10_and_255:
                return media_id.ID_NUMBERS_GAS
            elif ln.d == 1:
                return media_id.BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES_GAS
            elif ln.d in (2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15):
                return media_id.GENERAL_PURPOSE_OBJECTS_GAS
        elif ln.c == 96 and ln.d == 5 and (ln.e in range(10)):
            return media_id.INTERNAL_OPERATING_STATUS_OBJECTS_GAS
        elif ln.c in chain(range(1, 9), range(11, 17), range(21, 27), range(31, 36), range(61, 66)) and ln.e in __range63:
            if ln.d in (24, 25, 26, 42, 43, 44, 63, 64, 65, 81, 82, 83) and ln.f in chain(range(100), range(101, 127)):
                return media_id.MEASURED_VALUES_GAS_INDEXES_AND_INDEX_DIFFERENCES
            elif ln.d in chain(range(6, 24), range(27, 33), range(45, 51), range(66, 72), range(84, 90)) and ln.f == 255:
                return media_id.MEASURED_VALUES_GAS_INDEXES_AND_INDEX_DIFFERENCES
            elif ln.d in chain(range(33, 42), range(52, 63), range(72, 81), range(90, 99)) and ln.f in chain(__range100_and_101_125_and_255, (126,)):
                return media_id.MEASURED_VALUES_GAS_INDEXES_AND_INDEX_DIFFERENCES
        elif ln.c == 42 and ln.e == 0:
            if ln.d in chain(0, 1, 2, 13, range(15, 19), range(19, 31), range(35, 51), range(55, 71)) and ln.f == 255:
                return media_id.MEASURED_VALUES_GAS_FLOW_RATE
            elif ln.d in chain(range(31, 35), range(51, 55)) and ln.f in chain(__range100_and_101_125_and_255, (126,)):
                return media_id.MEASURED_VALUES_GAS_FLOW_RATE
        elif ln.c in chain((41, 42), range(44, 50)) and ln.d in (0, 2, 3, 10, 11, 13, range(15, 92)) and ln.e == 0 and ln.f == 255:
            return media_id.MEASURED_VALUES_GAS_PROCESS_VALUES
        elif ln.c in range(51, 56):
            if ln.d in (0, 2, 3, 10, 11) and ln.e in chain((0, 1), range(11, 29)) and ln.f == 255:
                return media_id.CONVERSION_RELATED_FACTORS_AND_COEFFICIENTS_GAS
            elif ln.d == 12 and ln.e in range(20) and ln.f == 255:
                return media_id.CALCULATION_METHODS_GAS
        elif ln.c == 70 and ln.f == 255:
            if ln.d in (8, 9) and ln.e == 0:
                return media_id.NATURAL_GAS_ANALYSIS
            elif ln.d in chain(range(10, 21), range(60, 85)) and ln.e in chain((0, 1), range(11, 29)):
                return media_id.NATURAL_GAS_ANALYSIS
        elif ln.c == 98:
            return media_id.LIST_OBJECTS_GAS
        else:
            return media_id.GAS
    elif ln.a == media_id.WATER:
        if ln.c == 0:
            if ln.d == 0 and ln.e in __range10_and_255:
                return media_id.ID_NUMBERS_WATER
            elif ln.d == 1 and ln.e in (1, 2, 10, 11, 12):
                return media_id.BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES_WATER
            elif ln.d == 2 and ln.e in (0, 3):
                return media_id.GENERAL_PURPOSE_OBJECTS_WATER
            elif ln.d in (5, 7) and ln.e == 1:
                return media_id.GENERAL_PURPOSE_OBJECTS_WATER
            elif ln.d == 8 and ln.e in (1, 6):
                return media_id.GENERAL_PURPOSE_OBJECTS_WATER
            elif ln.d == 9 and ln.e in (1, 2, 3):
                return media_id.GENERAL_PURPOSE_OBJECTS_WATER
        elif ln.c == 1 and ln.e in range(0, 13):
            if ln.d in (0, 1, 2, 3, 6) and ln.f == 255:
                return media_id.MEASURED_VALUES_WATER_CONSUMPTION
            elif ln.d in range(1, 6) and ln.f in chain(range(100), range(101, 126)):
                return media_id.MEASURED_VALUES_WATER_CONSUMPTION
        elif ln.c in (2, 3) and ln.e in range(0, 13):
            if ln.d in (0, 1, 2, 3, 6) and ln.f == 255:
                return media_id.MEASURED_VALUES_WATER_MONITORING_VALUES
            elif ln.d in range(1, 6) and ln.f in chain(range(100), range(101, 126)):
                return media_id.MEASURED_VALUES_WATER_MONITORING_VALUES
        elif ln.c == 97 and ln.d == 97:
            return media_id.ERROR_REGISTER_OBJECTS_WATER
        elif ln.c == 98:
            return media_id.LIST_OBJECTS_WATER
        elif ln.c == 99 and ln.d == 1:
            return media_id.DATA_PROFILE_OBJECTS_WATER
        else:
            return media_id.WATER
    return media_id.OTHER_MEDIA


DLMSObjectContainer: TypeAlias = Collection | list[InterfaceClass] | filter


def class_id_filter(container: DLMSObjectContainer, class_id: ClassID) -> filter[InterfaceClass]:
    """return filter by class_id"""
    return filter(lambda obj: obj.CLASS_ID == class_id, container)


def media_id_filter(container: DLMSObjectContainer, media_id: media_id.MediaId) -> filter[InterfaceClass]:
    return filter(lambda obj: obj.logical_name.a == media_id, container)

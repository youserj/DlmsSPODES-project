""" The OBIS identification system serves as a basis for the COSEM logical names. The system of naming COSEM objects is defined in the basic
principles (see Clause 4 EN 62056-62:2007), the identification of real data items is specified in IEC 62056-61. The following clauses define the
usage of those definitions in the COSEM environment. All codes, which are not explicitly listed, but outside the manufacturer specific range are
reserved for future use."""
from __future__ import annotations
import os
import copy
from struct import pack
import datetime
import dataclasses
from itertools import count, chain
from collections import deque
from functools import reduce, cached_property, lru_cache
from typing import TypeAlias, Iterator, Type, Callable, Self
import logging
from ..version import AppVersion
from ..types import common_data_types as cdt, cosem_service_types as cst, useful_types as ut
from ..types.implementations import structs, enums
from . import cosem_interface_class as ic
from .activity_calendar import ActivityCalendar
from .arbitrator import Arbitrator
from .association_sn.ver0 import AssociationSN as AssociationSNVer0
from .association_ln.ver0 import AssociationLN as AssociationLNVer0
from .association_ln.ver1 import AssociationLN as AssociationLNVer1
from .association_ln.ver2 import AssociationLN as AssociationLNVer2
from .push_setup.ver0 import PushSetup as PushSetupVer0
from .push_setup.ver1 import PushSetup as PushSetupVer1
from .push_setup.ver2 import PushSetup as PushSetupVer2
from .client_setup import ClientSetup
from .clock import Clock
from .data import Data
from .disconnect_control import DisconnectControl
from .gprs_modem_setup import GPRSModemSetup
from .gsm_diagnostic.ver0 import GSMDiagnostic as GSMDiagnosticVer0
from .gsm_diagnostic.ver1 import GSMDiagnostic as GSMDiagnosticVer1
from .gsm_diagnostic.ver2 import GSMDiagnostic as GSMDiagnosticVer2
from .iec_hdlc_setup.ver0 import IECHDLCSetup as IECHDLCSetupVer0
from .iec_hdlc_setup.ver1 import IECHDLCSetup as IECHDLCSetupVer1
from .image_transfer import ImageTransfer
from .ipv4_setup import IPv4Setup
from .modem_configuration.ver0 import PSTNModemConfiguration
from .modem_configuration.ver1 import ModemConfigurationVer1
from .limiter import Limiter
from .profile_generic.ver0 import ProfileGeneric as ProfileGenericVer0
from .profile_generic.ver1 import ProfileGeneric as ProfileGenericVer1
from .register import Register
from .extended_register import ExtendedRegister
from .demand_register.ver0 import DemandRegister as DemandRegisterVer0
from .register_monitor import RegisterMonitor
from .schedule import Schedule
from .security_setup.ver0 import SecuritySetup as SecuritySetupVer0
from .security_setup.ver1 import SecuritySetup as SecuritySetupVer1
from .script_table import ScriptTable
from .single_action_schedule import SingleActionSchedule
from .special_days_table import SpecialDaysTable
from .tcp_udp_setup import TCPUDPSetup
from .. import ITE_exceptions as exc
import xml.etree.ElementTree as ET
from xml.dom import minidom
from ..relation_to_OBIS import get_name
from ..cosem_interface_classes import implementations as impl
from ..cosem_interface_classes.overview import ClassID, Version, CountrySpecificIdentifiers
from ..enums import TagsName, MechanismId
from . import obis as o
from .. import pdu_enums as pdu
from ..configure import get_saved_parameters
from ..config_parser import config


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
                            GPRSModemSetup | GSMDiagnostic | ClientSetup | SecuritySetup | TCPUDPSetup | IPv4Setup | Arbitrator | RegisterMonitor | PushSetup | AssociationSN


UsedAttributes: TypeAlias = dict[cst.LogicalName, set[int]]


class ClassMap(dict):
    def __hash__(self):
        return hash(tuple(it.hash_ for it in self.values()))


DataMap = ClassMap({
    0: Data})
RegisterMap = ClassMap({
    0: Register})
ExtendedRegisterMap = ClassMap({
    0: ExtendedRegister})
DemandRegisterMap = ClassMap({
    0: DemandRegisterVer0})
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
ClientSetupMap = ClassMap({
    0: ClientSetup
})

# implementation ClassMap
UnsignedDataMap = ClassMap({
    0: impl.data.Unsigned
})

CosemClassMap: TypeAlias = DataMap | RegisterMap | ExtendedRegisterMap | DemandRegisterMap | ProfileGenericMap | ClockMap | ScriptTableMap | ScheduleMap | SpecialDaysTableMap | \
                           AssociationLNMap | ImageTransferMap | ActivityCalendarMap | RegisterMonitorMap | SingleActionScheduleMap | IECHDLCSetupMap | ModemConfigurationMap | \
                           TCPUDPSetupMap | IPv4SetupMap | GPRSModemSetupMap | GSMDiagnosticMap | SecuritySetupMap | ArbitratorMap | DisconnectControlMap | LimiterMap | \
                           ClientSetupMap


LN_C: TypeAlias = int
LN_D: TypeAlias = int


common_interface_class_map: dict[int, dict[[int, None], Type[InterfaceClass]]] = {
    1: DataMap,
    3: RegisterMap,
    4: ExtendedRegisterMap,
    5: DemandRegisterMap,
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
    32767: ClientSetupMap
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


@dataclasses.dataclass(frozen=True)
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
    #
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
    #
    (0, 0, 40, 0, tuple(range(8))): (AssociationSNMap, AssociationLNMap),  # todo: now limit by 8 association, solve it
    #
    (0, 0, 42, 0, 0): ClassMap({0: impl.data.LDN}),
    (0, 0, 43, 0, tuple(range(256))): SecuritySetupMap,
    (0, 43, 1): DataMap,
    #
    (0, 0, 44, 0, tuple(range(256))): ImageTransferMap,
    #
    (0, 96, 1, tuple(range(0, 11))): DataMap,
    (0, 96, 1, 255): ProfileGenericMap,  # todo: add RegisterTable
    (0, 96, 2): DataMap,
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
    (0, 96, 11, tuple(range(100))): (DataMap, RegisterMap,  ExtendedRegisterMap),
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
    (1, 0, 2): DataMap,
    (1, 0, (3, 4, 7, 8, 9)): (DataMap, RegisterMap, ExtendedRegisterMap),
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

# Utility Update
__func_map_for_create.update({
    (0, 0, 199, 255, 255): ClientSetupMap,
})

# SPODES3 Update
__func_map_for_create.update({
    (0, 21, 0): ClassMap({1: impl.profile_generic.SPODES3DisplayReadout}),
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
    (0, 0, 96, 51, 5): ClassMap({0: impl.data.SealStatus}),
    (0, 0, 96, 51, (1, 3, 4, 6, 7)): UnsignedDataMap,
    (0, 0, 96, 51, (8, 9)): ClassMap({0: impl.data.OctetStringDateTime}),
    # electricity
    (1, 0, 8, (4, 5)): UnsignedDataMap,
    (1, 98, 1): ClassMap({1: impl.profile_generic.SPODES3MonthProfile}),
    (1, 98, 2): ClassMap({1: impl.profile_generic.SPODES3DailyProfile}),
    (1, 99, (1, 2)): ClassMap({1: impl.profile_generic.SPODES3LoadProfile}),
    (1, 0, 131, 35, 0): RegisterMap,
    (1, 0, 133, 35, 0): RegisterMap,
    (1, 0, 147, 133, 0): RegisterMap,
    (1, 0, 148, 136, 0): RegisterMap,
    (1, 94, 7, 0): ClassMap({1: impl.profile_generic.SPODES3CurrentProfile}),
    (1, 94, 7, (1, 2, 3, 4, 5, 6)): ProfileGenericMap,  # Todo: RU. Scaler-profile With 1 entry and more
    # KPZ
    (128, 0, tuple(range(20)), 0, 0): RegisterMap
})

func_maps["SPODES_3"] = get_func_map(__func_map_for_create)

# KPZ Update
__func_map_for_create.update({
    (0, 128, 96, 13, 1): ClassMap({0: impl.data.ITEBitMap}),
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
    c_m = None
    if ln.b >= 128:
        # try search in BCDE group for manufacture object before in CDE
        c_m = func_map.get((ln.contents[:5]), None)
    if not c_m:
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


class Collection:
    __dlms_ver: int
    __manufacturer: bytes | None
    __country: CountrySpecificIdentifiers
    __country_ver: AppVersion | None
    __server_type: cdt.CommonDataType | None
    __server_ver: dict[int, AppVersion]
    __container: deque[InterfaceClass]
    __const_objs: list[ic.COSEMInterfaceClasses]
    __spec: str

    def __init__(self, country: CountrySpecificIdentifiers = CountrySpecificIdentifiers.RUSSIA):
        self.__container = deque()
        """ all DLMS objects container with obis key """
        self.__const_objs = list()
        """ container for major(constant) DLMS objects LN. They don't deletable """
        self.init_ids(country)

    def copy(self, association_id: int = 3) -> Self:
        new_collection = Collection(self.__country)
        new_collection.set_dlms_ver(self.__dlms_ver)
        new_collection.set_manufacturer(self.__manufacturer)
        new_collection.set_country_ver(self.__country_ver)
        new_collection.set_server_type(self.__server_type)
        for inst, ver in self.__server_ver.items():
            new_collection.set_server_ver(inst, ver)
        new_collection.set_spec()
        # for obj in self.getASSOCIATION(association_id).get_objects():
        for obj in self.__container:
            new_obj: InterfaceClass = obj.__class__(obj.logical_name)
            new_collection.__container.append(new_obj)
            new_obj.collection = new_collection
        for obj in self.getASSOCIATION(association_id).get_objects():
            new_collection.get_object(obj.logical_name).copy(obj, association_id)
        return new_collection

    def init_ids(self, country):
        """initiate of identificators"""
        self.__dlms_ver = 6
        self.__manufacturer = None
        self.__country = country
        self.__country_ver = None
        """country version specification"""
        self.__server_type = None
        self.__server_ver = dict()
        """key: instance of 0.b.2.0.1.255, value AppVersion"""
        self.__spec = "DLMS_6"

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

    def pop(self, class_id: ClassID) -> list[InterfaceClass]:
        """pop from collection by Class_ID"""
        ret: list[InterfaceClass] = list()
        for obj in self.__container:
            if obj.CLASS_ID == class_id:
                ret.append(obj)
        for obj in ret:
            self.__container.remove(obj)
        return ret

    @property
    def server_ver(self):
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

    def __str__(self):
        return F"[{len(self.__container)}] DLMS version: {self.__dlms_ver}, country: {self.__country.name}, country specific version: {self.__country_ver}, " \
               F"manufacturer: {self.__manufacturer}, server type: {repr(self.__server_type)}, server version: {self.__server_ver}, uses specification: {self.__spec}"

    def __iter__(self) -> Iterator[ic.COSEMInterfaceClasses]:
        return iter(self.__container)

    @classmethod
    def from_description(cls, descriptions: list[tuple[cst.LogicalName, cdt.LongUnsigned, cdt.Unsigned]] = None):
        """ get instance with objects from descriptions """
        new_instance = cls()
        if isinstance(descriptions, list):
            deque(map(lambda description: new_instance.create(description[1], description[2], description[0]), descriptions))
        return new_instance

    def create_objects_from_collection(self, container: Collection):
        """ create objects from other collection """
        for obj in container:
            self.add_if_missing(class_id=obj.CLASS_ID,
                                version=obj.VERSION,
                                logical_name=obj.logical_name)

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
    def from_xml(cls, filename: str, use: dict[cst.LogicalName, set[int]] = None) -> Self:
        """ append objects from xml file """
        tree = ET.parse(filename)
        objects = tree.getroot()
        new = cls()
        if use is None and objects.tag != TagsName.DEVICE_ROOT.value:
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
            new.set_server_ver(instance=int(server_ver.attrib.get("instance", "0")),
                               value=AppVersion.from_str(server_ver.text))
        new.set_spec()
        logger.info(F'Версия: {root_version}, file: {filename.split("/")[-1]}')
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
                                                     logical_name=cst.LogicalName(ln))
                                if use is not None:
                                    use[new_object.logical_name] = set()
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
                                        if use is not None:
                                            use[new_object.logical_name].add(indexes[-1])
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
               with_comment: bool = False):
        """Save attributes of client. For types only STATIC save """
        classes: set[ut.CosemClassId] = set()
        objects = self.__get_base_xml_element(root_tag)
        for obj in self.values():
            object_node = ET.SubElement(objects, 'object', attrib={'name': F'{get_name(obj.logical_name)}', 'ln': str(obj.logical_name)})
            ET.SubElement(object_node, 'class_id').text = str(obj.CLASS_ID)
            if obj.CLASS_ID not in classes:
                ET.SubElement(object_node, 'version').text = str(obj.VERSION)
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
                            record_time = obj.get_record_time(index)
                            el_attrib: dict = {'index': str(index)}
                            if record_time is not None:
                                el_attrib.update({'rec_time': record_time.encoding.hex()})
                            if with_comment:
                                object_node.append(ET.Comment(F'{el.NAME}: {attr}'))
                            ET.SubElement(object_node, 'attribute', attrib=el_attrib).text = attr.encoding.hex()
                        case _:
                            logger.warning('PASS')

        # TODO: '<!DOCTYPE ITE_util_tree SYSTEM "setting.dtd"> or xsd
        xml_string = ET.tostring(objects, encoding='cp1251', method='xml')
        dom_xml = minidom.parseString(xml_string)
        str_ = dom_xml.toprettyxml(indent="  ", encoding='cp1251')
        with open(file_name, "wb") as f:
            f.write(str_)

    def to_xml2(self, file_name: str,
                root_tag: str = TagsName.DEVICE_ROOT.value) -> bool:
        """Save attributes WRITABLE and STATIC of client"""
        objects = self.__get_base_xml_element(root_tag)
        col = get(
            m=self.manufacturer,
            t=self.server_type,
            ver=self.server_ver[0])
        is_empty: bool = True
        for desc in col.getASSOCIATION(3).object_list:
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

    def to_xml3(self, file_name: str,
                used: dict[cst.LogicalName, set[int]],
                decode: bool = False):
        """For template only"""
        objects = self.__get_base_xml_element(TagsName.TEMPLATE_ROOT.value)
        objects.attrib["decode"] = str(int(decode))
        for obj in self.values():
            if not used.get(obj.logical_name):
                continue
            object_node = ET.SubElement(
                objects,
                "object",
                attrib={
                    "ln": str(obj.logical_name),
                    "name": obj.NAME
                })
            for i, attr in obj.get_index_with_attributes():
                if i == 1:  # don't keep ln
                    continue
                elif i not in used[obj.logical_name]:
                    """skip not used attribute"""
                else:
                    if isinstance(attr, cdt.CommonDataType):
                        if decode:
                            attr_el = ET.SubElement(
                                object_node,
                                "attr",
                                {
                                    "name": obj.get_attr_element(i).NAME,
                                    "index": str(i)})
                            if isinstance(attr, cdt.SimpleDataType):
                                attr_el.text = str(attr)
                            else:
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
                            ET.SubElement(
                                object_node,
                                "attr",
                                {"index": str(i)}
                            ).text = attr.encoding.hex()
                    else:
                        logger.error(F"skip record {obj}:attr={i} with value={attr}")
        with open(
                file_name,
                mode="wb") as f:
            f.write(ET.tostring(
                element=objects,
                encoding="utf-8",
                method="xml",
                xml_declaration=True))

    def save_type(self, file_name: str, root_tag: str = TagsName.DEVICE_ROOT.value):
        """ For concrete device save all attributes. For types only STATIC save """
        objects = self.__get_base_xml_element(root_tag)
        classes: set[ut.CosemClassId] = set()
        for obj in self.values():
            object_node = ET.SubElement(objects, 'object', attrib={'name': F'{get_name(obj.logical_name)}', 'ln': str(obj.logical_name)})
            ET.SubElement(object_node, 'class_id').text = str(obj.CLASS_ID)
            if obj.CLASS_ID not in classes:
                ET.SubElement(object_node, 'version').text = str(obj.VERSION)
            classes.add(obj.CLASS_ID)
            for index, method in get_saved_parameters(obj).items():
                attr = obj.get_attr(index)
                match method, attr:
                    case 1, None if isinstance(obj.get_attr_element(index).DATA_TYPE, ut.CHOICE):
                        logger.warning(F'For {obj} {attr} not selected type from: {obj.get_attr_element(index).DATA_TYPE}')
                    case 1, None:
                        logger.warning(F'REMOVE {obj} {attr} for saving in type')
                    case 1, _:
                        object_node.append(ET.Comment(F'{obj.get_attr_element(index).NAME}. Type: {attr.NAME}'))
                        ET.SubElement(object_node, 'attribute', attrib={'index': str(index)}).text = str(attr.TAG[0])
                    case 0, cdt.CommonDataType():
                        object_node.append(ET.Comment(F'{obj.get_attr_element(index).NAME}: {attr}'))
                        ET.SubElement(object_node, 'attribute', attrib={'index': str(index)}).text = attr.encoding.hex()
                    case 0, None:
                        logger.warning(F'For {obj} attr: {index} value not set')
                    case _ as unknown:
                        logger.warning(F'Unknown pattern for select keep attribute: {unknown}')

        # TODO: '<!DOCTYPE ITE_util_tree SYSTEM "setting.dtd"> or xsd
        xml_string = ET.tostring(objects, encoding='cp1251', method='xml')
        dom_xml = minidom.parseString(xml_string)
        str_ = dom_xml.toprettyxml(indent="  ", encoding='cp1251')
        with open(file_name, "wb") as f:
            f.write(str_)

    def add_major(self, obj: InterfaceClass):
        self.__const_objs.append(obj)

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

    def get_instance(self, class_id: ut.CosemClassId,
                     version: cdt.Unsigned | None,
                     ln: cst.LogicalName) -> InterfaceClass:
        """ TODO: naming"""
        if version is None:
            version = self.set_version(class_id, version)
        try:
            return get_type(class_id, version, ln, func_maps[self.__spec])(ln)
        except ValueError as e:
            raise ValueError(F"error getting DLMS object instance with {class_id=} {version=} {ln=}: {e}")
        # ret: Type[InterfaceClass] = _func_map_A.get(ln.a, None)
        # if ret:
        #     return ret(class_id, version, ln)(ln)
        # else:
        #     raise ValueError(F"unknown {ln.a} in {ln} with: {class_id=}, {version=}")

    def add_if_missing(self, class_id: ut.CosemClassId,
                       version: cdt.Unsigned | None,
                       logical_name: cst.LogicalName) -> InterfaceClass:
        """ like as add method with check for missing """
        if not self.is_in_collection(logical_name):
            return self.create(class_id=class_id,
                               version=version,
                               logical_name=logical_name)
        else:
            return self.__get_object(logical_name.contents)

    def get(self, obis: bytes) -> InterfaceClass | None:
        """ get object, return None if it absence """
        return next(filter(lambda obj: obj.logical_name.contents == obis, self.__container), None)

    def values(self) -> tuple[InterfaceClass]:
        return tuple(self.__container)

    def __len__(self):
        return len(self.__container)

    def create(self, class_id: ut.CosemClassId,
               version: cdt.Unsigned | None,
               logical_name: cst.LogicalName,
               is_major: bool = False) -> InterfaceClass:
        """ append new DLMS object in collection. <is_major>=True is not erased object """
        if self.is_in_collection(logical_name):
            raise exc.ITEApplication(F'ERROR created DLMS object with {logical_name=}. Already exist')
        new_object = self.get_instance(class_id, version, logical_name)
        new_object.collection = self
        self.__container.append(new_object)
        if is_major:
            self.__const_objs.append(new_object)
            logger.info(F'Create Major {new_object}')
        else:
            logger.info(F'Create {new_object}')
        return new_object

    def add(self, class_id: ut.CosemClassId,
            version: cdt.Unsigned | None,
            logical_name: cst.LogicalName) -> InterfaceClass:
        """ Use only in template. TODO: move to template """
        new_object = self.get_instance(class_id, version, logical_name)
        new_object.collection = self
        self.__container.append(new_object)
        logger.info(F'Create {new_object}')
        return new_object

    def raise_before(self, obj: InterfaceClass, other: InterfaceClass):
        """ Insert <obj> above <other> """
        other_index: int = self.__container.index(other)
        a = self.__container.index(obj)
        if other_index < self.__container.index(obj):
            self.__container.remove(obj)
            self.__container.insert(other_index, obj)

    def try_remove(self, logical_name: cst.LogicalName, indexes: list[int] = None) -> bool:
        """ If indexes is None when remove object else:
        Use in template. Remove attributes by indexes and remove object from collection if it has only logic attribute """
        match self.get(logical_name.contents), indexes:
            case None, _:
                return False
            case ic.COSEMInterfaceClasses() as obj, None if obj not in self.__const_objs:
                self.__container.remove(obj)
                return True
            case ic.COSEMInterfaceClasses() as obj, list():
                obj: InterfaceClass
                for i in indexes:
                    obj.clear_attr(i)
                for i in range(2, obj.get_attr_length()):
                    if obj.get_attr(i) is not None:
                        break
                else:
                    self.__container.remove(obj)  # TODO: Rewrite with new list attr API
                return True
            case _:
                logger.warning(F'Dont remove with: {logical_name}: {indexes=}')
                return False

    @lru_cache(maxsize=100)  # amount of all ClassID
    def set_version(self, class_id: ut.CosemClassId, version: cdt.Unsigned | None = None) -> cdt.Unsigned:
        """ Set DLMS Class version for all Class ID. Return Class Version according by Class ID """
        for obj in filter(lambda it: it.CLASS_ID == class_id, self.__container):
            if version is None or version == obj.VERSION:
                return obj.VERSION
            else:
                raise ValueError(F'Not match Class Version. Expected: {obj.VERSION}, got {version}')
        if version is not None:
            return version
        else:
            raise ValueError(F'Not find version for {class_id=}')

    def is_in_collection(self, value: str | bytes | cst.LogicalName) -> bool:
        match value:
            case bytes():           obis = value
            case str():             obis = cst.LogicalName(value).contents
            case cst.LogicalName(): obis = value.contents
            case _ as error:        raise TypeError(F'Unknown type {error}')
        return obis in (obj.logical_name.contents for obj in self.__container)

    def get_object(self, value: LNContaining) -> InterfaceClass:
        """ return object from obis<string> or raise exception if it absence """
        match value:
            case bytes():                                                    return self.__get_object(value)
            case cst.LogicalName() | ut.CosemObjectInstanceId():             return self.__get_object(value.contents)
            case ut.CosemAttributeDescriptor() | ut.CosemMethodDescriptor(): return self.__get_object(value.instance_id.contents)
            case ut.CosemAttributeDescriptorWithSelection():                 return self.__get_object(value.cosem_attribute_descriptor.instance_id.contents)
            case str():                                                      return self.__get_object(cst.LogicalName(value).contents)
            case cdt.Structure(logical_name=value.logical_name):             return self.__get_object(value.logical_name.contents)
            case _:                                                          raise exc.NoObject(F"Can't find DLMS Object from collection with {value=}")

    @lru_cache(4)
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

    def get_objects_by_class_id(self, value: int | ut.CosemClassId) -> list[InterfaceClass]:
        class_id = ut.CosemClassId(value)
        return list(filter(lambda obj: obj.CLASS_ID == class_id, self.__container))

    def get_objects_descriptions(self) -> list[tuple[cst.LogicalName, cdt.LongUnsigned, cdt.Unsigned]]:
        """ return container of objects for get device clone """
        return list(map(lambda obj: (obj.logical_name, obj.CLASS_ID, obj.VERSION), self.__container))

    def get_writable_attr(self) -> UsedAttributes:
        """return all writable {obj.ln: {attribute_index}}"""
        ret: UsedAttributes = dict()
        for ass in filter(lambda it: it.logical_name.e != 0, self.get_objects_by_class_id(ClassID.ASSOCIATION_LN_CLASS)):
            for list_type in ass.object_list:
                for attr_access in list_type.access_rights.attribute_access:
                    if attr_access.access_mode.is_writable():
                        if ret.get(list_type.logical_name, None) is None:
                            ret[list_type.logical_name] = set()
                        ret[list_type.logical_name].add(int(attr_access.attribute_id))
        return ret

    def clear(self):
        """ clear to default objects amount """
        for obj in self.__container.copy():
            if obj not in self.__const_objs and obj.CLASS_ID != ClassID.ASSOCIATION_LN_CLASS:  # keep all AssociationLN for keep it secret
                self.__container.remove(obj)
        # clear cached parameters
        self.__get_object.cache_clear()
        self.get_objects_list.cache_clear()
        self.is_writable.cache_clear()
        self.is_readable.cache_clear()
        self.is_accessable.cache_clear()
        self.get_name_and_type.cache_clear()
        # end clear cached
        self.init_ids(CountrySpecificIdentifiers.RUSSIA)

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
        del self.current_association
        logger.warning(F'Attention. ALL Association attributes will to default')
        for ass in self.get_objects_by_class_id(ut.CosemClassId(15)):
            self.__container.remove(ass)
            self.__container.append(self.get_instance(class_id=ut.CosemClassId(15),
                                                      version=version,
                                                      ln=ass.logical_name))

    @lru_cache(maxsize=256)
    def __get_object(self, obis: bytes) -> InterfaceClass:
        obj: InterfaceClass = next(filter(lambda it: it.logical_name.contents == obis, self.__container), None)
        if obj is None:
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

    @lru_cache(4)
    def getASSOCIATION(self, instance: int) -> AssociationLN:
        return self.__get_object(bytes((0, 0, 40, 0, instance, 255)))

    @lru_cache(4)
    def getAssociationBySAP(self, SAP: enums.ClientSAP) -> AssociationLN:
        return self.__get_object(bytes((0, 0, 40, 0, self.get_association_id(SAP), 255)))

    @cached_property
    def PUBLIC_ASSOCIATION(self) -> AssociationLN:
        return self.__get_object(bytes((0, 0, 40, 0, 1, 255)))

    @property
    def COMMUNICATION_PORT_PARAMETER(self) -> impl.data.CommunicationPortParameter:
        return self.__get_object(bytes((0, 0, 96, 12, 4, 255)))

    @cached_property
    def client_setup(self) -> ClientSetup:
        return self.__get_object(bytes((0, 0, 199, 255, 255, 255)))

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
                                    names.append(action_obj.get_attr_element(int(action.index)).NAME)
                                else:
                                    raise TypeError(F"not support by framework")  # TODO: make it
                            case 2:  # for execute
                                if isinstance(action.parameter, cdt.NullData):
                                    names.append(action_obj.get_meth_element(int(action.index)).NAME)
                                else:
                                    raise TypeError(F"not support by framework")  # TODO: make it
                    return ", ".join(names)
            else:
                raise ValueError(F"not find {selector} in {obj}")
        else:
            raise ValueError(F"object with {ln} is not {ScriptTable.NAME}")

    @lru_cache(4)
    def get_association_id(self, client_sap: enums.ClientSAP) -> int:
        """return id(association instance) from it client address without current"""
        for ass in self.get_objects_by_class_id(AssociationLNVer0.CLASS_ID):
            if ass.associated_partners_id.client_SAP == client_sap and ass.logical_name.e != 0:
                return ass.logical_name.e
            else:
                continue
        else:
            raise ValueError(F"absent association with {client_sap}")

    @lru_cache(maxsize=1000)
    def is_writable(self, ln: cst.LogicalName,
                    index: int,
                    association_id: int,
                    security_policy: pdu.SecurityPolicy = pdu.SecurityPolicyVer0.NOTHING
                    ) -> bool:
        match self.getASSOCIATION(association_id).object_list.get_attr_access(ln, index):
            case pdu.AttributeAccess.NO_ACCESS | pdu.AttributeAccess.READ_ONLY | pdu.AttributeAccess.AUTHENTICATED_READ_ONLY:
                return False
            case pdu.AttributeAccess.WRITE_ONLY | pdu.AttributeAccess.READ_AND_WRITE:
                return True
            case pdu.AttributeAccess.AUTHENTICATED_WRITE_ONLY | pdu.AttributeAccess.AUTHENTICATED_READ_AND_WRITE:
                if isinstance(security_policy, pdu.SecurityPolicyVer0):
                    match security_policy:
                        case pdu.SecurityPolicyVer0.AUTHENTICATED | pdu.SecurityPolicyVer0.AUTHENTICATED_AND_ENCRYPTED:
                            return True
                        case _:
                            return False
                elif isinstance(security_policy, pdu.SecurityPolicyVer1):
                    if bool(security_policy & (pdu.SecurityPolicyVer1.AUTHENTICATED_REQUEST | pdu.SecurityPolicyVer1.AUTHENTICATED_RESPONSE)):
                        return True
                    else:
                        return False
                else:
                    raise TypeError(F"unknown {security_policy.__class__}: {security_policy}")
            case err:
                raise exc.ITEApplication(F"unsupport access: {err}")

    @lru_cache(maxsize=1000)
    def is_readable(self, ln: cst.LogicalName,
                    index: int,
                    association_id: int,
                    security_policy: pdu.SecurityPolicy = pdu.SecurityPolicyVer0.NOTHING
                    ) -> bool:
        match self.getASSOCIATION(association_id).object_list.get_attr_access(ln, index):
            case pdu.AttributeAccess.NO_ACCESS | pdu.AttributeAccess.WRITE_ONLY | pdu.AttributeAccess.AUTHENTICATED_WRITE_ONLY:
                return False
            case pdu.AttributeAccess.READ_ONLY | pdu.AttributeAccess.READ_AND_WRITE:
                return True
            case pdu.AttributeAccess.AUTHENTICATED_READ_ONLY | pdu.AttributeAccess.AUTHENTICATED_READ_AND_WRITE:
                if isinstance(security_policy, pdu.SecurityPolicyVer0):
                    match security_policy:
                        case pdu.SecurityPolicyVer0.AUTHENTICATED | pdu.SecurityPolicyVer0.AUTHENTICATED_AND_ENCRYPTED:
                            return True
                        case _:
                            return False
                elif isinstance(security_policy, pdu.SecurityPolicyVer1):
                    if bool(security_policy & (pdu.SecurityPolicyVer1.AUTHENTICATED_REQUEST | pdu.SecurityPolicyVer1.AUTHENTICATED_RESPONSE)):
                        return True
                    else:
                        return False
                else:
                    raise TypeError(F"unknown {security_policy.__class__}: {security_policy}")
            case err:
                raise exc.ITEApplication(F"unsupport access: {err}")

    @lru_cache(maxsize=1000)
    def is_accessable(self, ln: cst.LogicalName,
                      index: int,
                      association_id: int,
                      mechanism_id: MechanismId = None
                      ) -> bool:
        """for ver 0 and 1 only"""
        ass: AssociationLN = self.getASSOCIATION(association_id)
        match ass.object_list.get_meth_access(ln, index):
            case pdu.MethodAccess.NO_ACCESS:
                return False
            case pdu.MethodAccess.ACCESS:
                return True
            case pdu.MethodAccess.AUTHENTICATED_ACCESS:
                if not mechanism_id:
                    mechanism_id = int(ass.authentication_mechanism_name.mechanism_id_element)
                if mechanism_id >= MechanismId.LOW:
                    return True
                else:
                    return False
            case err:
                raise exc.ITEApplication(F"unsupport access: {err}")

    @lru_cache(maxsize=100)
    def get_name_and_type(self, value: structs.CaptureObjectDefinition) -> tuple[list[str], Type[cdt.CommonDataType]]:
        """ return names and type of element from collection"""
        names: list[str] = list()
        obj = self.__get_object(value.logical_name.contents)
        names.append(get_name(obj.logical_name))
        attr_index = int(value.attribute_index)
        data_index = int(value.data_index)
        data_type: Type[cdt.CommonDataType] = obj.get_attr_data_type(attr_index)
        names.append(obj.get_attr_element(attr_index).NAME)
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


def get_base_template_xml_element(collections: list[Collection], root_tag: str = TagsName.DEVICE_ROOT.value) -> ET.Element:
    objects = ET.Element(root_tag, attrib={'version': '4.1.0'})
    ET.SubElement(objects, 'dlms_ver').text = str(collections[0].dlms_ver)
    ET.SubElement(objects, 'country').text = str(collections[0].country.value)
    ET.SubElement(objects, 'country_ver').text = str(collections[0].country_ver)
    manufacture_node = ET.SubElement(objects, 'manufacturer')
    manufacture_node.text = collections[0].manufacturer.decode("utf-8")
    for col in collections:
        server_type_node = ET.SubElement(manufacture_node, 'server_type')
        server_type_node.text = col.server_type.encoding.hex()
        for ver in col.server_ver:
            server_ver_node = ET.SubElement(server_type_node, 'server_ver', attrib={"instance": str(ver)})
            server_ver_node.text = str(col.server_ver[ver])
    return objects


def to_xml4(collections: list[Collection],
            file_name: str,
            used: UsedAttributes):
    """For template only"""
    objects = get_base_template_xml_element(
        collections=collections,
        root_tag=TagsName.TEMPLATE_ROOT.value)
    objects.attrib["decode"] = "1"
    for col in collections:
        for ln, indexes in copy.copy(used).items():
            try:
                obj = col.get_object(ln)
                object_node = ET.SubElement(
                    objects,
                    "object",
                    attrib={
                        "ln": str(obj.logical_name),
                        "name": obj.NAME
                    })
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
                if len(used[ln]) == 0:
                    used.pop(ln)
            except exc.NoObject as e:
                logger.warning(F"skip obj with {ln=} in {collections.index(col)} collection: {e}")
                continue
        if len(used) == 0:
            logger.info(F"success decoding: used {collections.index(col)+1} from {len(collections)} collections")
            break
    if len(used) != 0:
        raise ValueError(F"failed decoding: {used}")
    with open(
            file_name,
            mode="wb") as f:
        f.write(ET.tostring(
            element=objects,
            encoding="utf-8",
            method="xml",
            xml_declaration=True))


def from_xml4(filename: str) -> tuple[list[Collection], UsedAttributes]:
    """ create collection from xml for template and UsedAttributes """
    used: UsedAttributes = dict()
    cols = list()
    tree = ET.parse(filename)
    objects = tree.getroot()
    if objects.tag != TagsName.TEMPLATE_ROOT.value:
        raise ValueError(F"ERROR: Root tag got {objects.tag}, expected {TagsName.TEMPLATE_ROOT.value}")
    root_version: AppVersion = AppVersion.from_str(objects.attrib.get('version', '1.0.0'))
    logger.info(F'Версия: {root_version}, file: {filename.split("/")[-1]}')
    manufacturer_node = objects.find("manufacturer")
    manufacturer = manufacturer_node.text.encode("utf-8")
    for server_type_node in manufacturer_node.findall("server_type"):
        server_type = cdt.get_instance_and_pdu_from_value(bytes.fromhex(server_type_node.text))[0]
        for server_ver_node in server_type_node.findall("server_ver"):
            cols.append(get_collection(
                manufacturer=manufacturer,
                server_type=server_type,
                server_ver=AppVersion.from_str(server_ver_node.text)))
    match root_version:
        case AppVersion(4, 0):
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
    return cols, used


if config is not None:
    try:
        __collection_path = config['DLMS']['collection']['path']
    except KeyError as e:
        raise exc.TomlKeyError(F"not find {e} in [DLMS.collection]<path>")


@lru_cache(maxsize=100)
def get(m: bytes, t: cdt.CommonDataType, ver: AppVersion) -> Collection:
    context: str = F"{m.decode('utf-8')}/{t.to_str()}/{ver}"
    logger.info(F"start search in Type library: {context}")
    path: str = F"{__collection_path}{m.decode('utf-8')}/{t.encoding.hex()}/"
    if not os.path.isfile(file_name := F"{path}{ver}.typ"):
        logging.info(F"For {t.decode()}: version {ver} not type in Types")
        if searched_version := ver.select_nearest([AppVersion.from_str(f_n.removesuffix(".typ")) for f_n in os.listdir(path)]):
            return get(m, t, searched_version)
        else:
            raise exc.NoConfig(F"no support {context}")
    return Collection.from_xml(file_name)


def get_collection(manufacturer: bytes, server_type: cdt.CommonDataType, server_ver: AppVersion) -> Collection:
    """get copy of collection with caching"""
    return get(manufacturer, server_type, server_ver).copy()

""" The OBIS identification system serves as a basis for the COSEM logical names. The system of naming COSEM objects is defined in the basic
principles (see Clause 4 EN 62056-62:2007), the identification of real data items is specified in IEC 62056-61. The following clauses define the
usage of those definitions in the COSEM environment. All codes, which are not explicitly listed, but outside the manufacturer specific range are
reserved for future use."""
import logging
from struct import pack
from dataclasses import dataclass
from itertools import count, chain
from functools import reduce, cached_property, lru_cache
from typing import TypeAlias, Iterator, Self, Callable, Literal, Iterable, Optional, Hashable, Protocol, cast, Annotated
from DLMS_SPODES.types.type_alias import attr2d
from semver import Version as SemVer
from StructResult import result
from ..types import common_data_types as cdt, cosem_service_types as cst, useful_types as ut
from ..types.implementations import structs, enums, octet_string
from .ln_pattern import LNPattern, LNPatterns
from .activity_calendar import ActivityCalendar, DayProfileAction
from .arbitrator import Arbitrator
from .association_ln import ObjectListType, is_readable, is_writable, is_accessible, MechanismIdElement
from .association_sn.ver0 import AssociationSN as AssociationSNVer0
from .association_ln.ver0 import AssociationLN as AssociationLNVer0, AssociatedPartnersType, ClientSAP
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
from ..relation_to_OBIS import obis2name
from ..cosem_interface_classes import implementations as impl
from ..cosem_interface_classes.overview import ClassID, CountrySpecificIdentifiers
from . import obis as o, ln_pattern
from .. import pdu_enums as pdu
from ..config_parser import config, get_message
from ..obis import media_id
from .parameter import Parameter
from typing_extensions import deprecated, override
from .cosem_interface_class import IC, Classifier, _LN_ELEMENT, ICAElement, DataType
from ..settings import settings
from ..types.type_alias import Obis, Encoding, Attr, Tag, attr2i, attr2obis, attr2a, attr2b, attr2c, attr2e, attr2f, attr2d, Index, unpack_attr, Attr2report



class CollectionMapError(exc.DLMSException):
    """"""


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


type AttributeIndex = int
UsedAttributes: TypeAlias = dict[cst.LogicalName, set[AttributeIndex]]


ObjectTreeMode: TypeAlias = Literal["", "m", "g", "c", "mc", "cm", "gm", "gc", "cg", "gmc"]
SortMode: TypeAlias = Literal["l", "n", "c", "cl", "cn"]


# todo: make new class ClassMap(for field Collection.spec_map). fields: name, version, dict(current version ClassMap)
class ClassMap:

    def __init__(self, *values: type[IC]) -> None:
        self._values = values

    def __hash__(self) -> int:
        return hash(id(it) for it in self._values)

    def get(self, ver: int) -> type[IC]:
        if (ver := int(ver)) < len(self._values):
            return self._values[ver]
        raise RuntimeError(f"got {ver=}, expected maximal={len(self._values)}")

    def renew(self, ver: int, cls_: type[IC]) -> Self:
        """return with one change"""
        if ver < (l := len(self._values)):
            tmp = list(self._values)
            tmp.insert(ver, cls_)
            return self.__class__(*tmp)
        if ver == l:
            return self.__class__(*(self._values + (cls_,)))
        raise RuntimeError(f"got {ver=}, expected maximal={len(self._values)}")

    def __str__(self) -> str:
        return f"{self._values[0].CLASS_ID}[{len(self._values)}]"


DataMap = ClassMap(Data)
DataStaticMap = ClassMap(impl.data.DataStatic)
DataDynamicMap = ClassMap(impl.data.DataDynamic)
RegisterMap = ClassMap(Register)
ExtendedRegisterMap = ClassMap(ExtendedRegister)
DemandRegisterMap = ClassMap(DemandRegisterVer0)
RegisterActivationMap = ClassMap(RegisterActivation)
ProfileGenericMap = ClassMap(ProfileGenericVer0, ProfileGenericVer1)
ClockMap = ClassMap(Clock)
ScriptTableMap = ClassMap(ScriptTable)
ScheduleMap = ClassMap(Schedule)
SpecialDaysTableMap = ClassMap(SpecialDaysTable)
AssociationSNMap = ClassMap(AssociationSNVer0)
AssociationLNMap = ClassMap(AssociationLNVer0, AssociationLNVer1, AssociationLNVer2)
ImageTransferMap = ClassMap(ImageTransfer)
ActivityCalendarMap = ClassMap(ActivityCalendar)
RegisterMonitorMap = ClassMap(RegisterMonitor)
SingleActionScheduleMap = ClassMap(SingleActionSchedule)
IECHDLCSetupMap = ClassMap(IECHDLCSetupVer0, IECHDLCSetupVer1)
ModemConfigurationMap = ClassMap(PSTNModemConfiguration, ModemConfigurationVer1)
TCPUDPSetupMap = ClassMap(TCPUDPSetup)
IPv4SetupMap = ClassMap(IPv4Setup)
GPRSModemSetupMap = ClassMap(GPRSModemSetup)
GSMDiagnosticMap = ClassMap(GSMDiagnosticVer0, GSMDiagnosticVer1, GSMDiagnosticVer2)
PushSetupMap = ClassMap(PushSetupVer0, PushSetupVer1, PushSetupVer2)
SecuritySetupMap = ClassMap(SecuritySetupVer0, SecuritySetupVer1)
ArbitratorMap = ClassMap(Arbitrator)
DisconnectControlMap = ClassMap(DisconnectControl)
LimiterMap = ClassMap(Limiter)
NTPSetupMap = ClassMap(NTPSetup)

# implementation ClassMap
UnsignedDataMap = ClassMap(impl.data.Unsigned)

LN_C: TypeAlias = int
LN_D: TypeAlias = int


common_interface_class_map: dict[int, ClassMap] = {
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


def get_interface_class(class_map: dict[int, ClassMap], c_id: int, ver: int) -> result.SimpleOrError[type[IC]]:
    """new version <get_type_from_class>"""
    if isinstance(ret := class_map.get(c_id), ClassMap):
        return result.Simple(ret.get(ver))
    if c_id not in common_interface_class_map:
        return result.Error.from_e(ValueError(f"unknown {c_id=}"), "get interface class")
    return result.Error.from_e(ValueError((f"got {c_id=}, expected {', '.join(map(str, class_map.keys()))}")))


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


@lru_cache()
def _create_map(maps: ClassMap | tuple[ClassMap]) -> dict[int, ClassMap]:
    if isinstance(maps, tuple):
        return {int(map_.get(0).CLASS_ID): map_ for map_ in maps}
    else:
        return {int(maps.get(0).CLASS_ID): maps}


A: TypeAlias = int
B: TypeAlias = int
C: TypeAlias = int
D: TypeAlias = int
E: TypeAlias = int


class Xgroup(Protocol):
    fmt: str

    def get_key(self) -> Iterator[bytes]:
        ...


class SimpleGroup(Xgroup, Protocol):
    def get_key(self) -> Iterator[bytes]:
        yield pack(self.fmt, *self)  # type: ignore[misc]


class ACgroup(SimpleGroup, tuple[A, C]):
    """Grouping of OBIS codes by group A (media) and group C (attribute).
    Creates a composite key for objects sharing the same media type and attribute.
    """
    fmt = ">BB"


class ACDgroup_(Xgroup, Protocol):
    """Grouping of OBIS codes by groups A (media), C (attribute), and D (data) with mask support.
    Supports exact values or masks for attribute (C) and data (D) groups.
    Allows flexible grouping by media type with variable attribute and data patterns.
    """
    fmt: str = ">BBB"


class ACDgroup(SimpleGroup, ACDgroup_, tuple[A, C, D]):
    ...


class ACCDgroup(ACDgroup_, tuple[A, tuple[C, ...], D]):
    def get_key(self) -> Iterator[bytes]:
        a, _, d = self
        return (pack(self.fmt, a, c, d) for c in self[1])


class ACDDgroup(ACDgroup_, tuple[A, C, tuple[D, ...]]):
    def get_key(self) -> Iterator[bytes]:
        a, c, _ = self
        return (pack(self.fmt, a, c, d) for d in self[2])


class ACCDDgroup(ACDgroup_, tuple[A, tuple[C, ...], tuple[D, ...]]):
    """Grouping of OBIS codes by groups A (media), C (attribute), and D (data) with mask support.
    Supports exact values or masks for attribute (C) and data (D) groups.
    Allows flexible grouping by media type with variable attribute and data patterns.
    """
    def get_key(self) -> Iterator[bytes]:
        a = self[0]
        return (pack(self.fmt, a, c, d) for c in self[1] for d in self[2])


class ACDEgroup_(Xgroup, Protocol):
    """Grouping of OBIS codes by groups A (media), C (attribute), D (data), and E (data version) with mask support.
    Groups by fixed media and attribute with support for data and data version masks.
    Enables precise control over data grouping with optional version filtering.
    """
    fmt: str = ">BBBB"


class ACDEgroup(SimpleGroup, ACDEgroup_, tuple[A, C, D, E]):
    ...


class ACDDEgroup(ACDEgroup_, tuple[A, C, tuple[D, ...], E]):
    def get_key(self) -> Iterator[bytes]:
        a, c, _, e = self
        return (pack(self.fmt, a, c, d, e) for d in self[2])



class ACDEEgroup(ACDEgroup_, tuple[A, C, D, tuple[E, ...]]):
    def get_key(self) -> Iterator[bytes]:
        a, c, d, _ = self
        return (pack(self.fmt, a, c, d, e) for e in self[3])


class ACDDEEgroup(ACDEgroup_, tuple[A, C, tuple[D, ...], tuple[E, ...]]):
    def get_key(self) -> Iterator[bytes]:
        a, c, _, _ = self
        return (pack(self.fmt, a, c, d, e) for d in self[2] for e in self[3])


class ABCDEgroup_(Xgroup, Protocol):
    """Grouping of OBIS codes by all OBIS groups A-E with data version mask support.

    Comprehensive grouping by:
    - A: media
    - B: channel/interface
    - C: attribute
    - D: data
    - E: data version (with mask support)

    Provides complete OBIS code grouping with flexible version matching.
    """
    fmt: str = ">BBBBB"


class ABCDEgroup(SimpleGroup, ABCDEgroup_, tuple[A, B, C, D, E]):
    ...


class ABCCDEgroup(ABCDEgroup_, tuple[A, B, tuple[C, ...], D, E]):
    def get_key(self) -> Iterator[bytes]:
        a, b, _, d, e = self
        return (pack(self.fmt, a, b, c, d, e) for c in self[2])


class ABCDEEgroup(ABCDEgroup_, tuple[A, B, C, D, tuple[E, ...]]):
    def get_key(self) -> Iterator[bytes]:
        a, b, c, d, _ = self
        return (pack(self.fmt, a, b, c, d, e) for e in self[4])


type PossibleGroup = ACgroup | ACDgroup_ | ACDEgroup | ABCDEgroup
FUNC_MAP: TypeAlias = dict[bytes, dict[int, ClassMap]]
"""ln.BCDE | ln.CDE | ln.CD | ln.C: {class_id: {version: CosemInterfaceClass}}"""


func_maps: dict[str, FUNC_MAP] = {}
type PossibleClassMap = tuple[ClassMap, ...] | ClassMap


def get_func_map(for_create_map: dict[PossibleGroup, PossibleClassMap]) -> FUNC_MAP:
    ret: FUNC_MAP = {}
    for g in for_create_map:
        for k in g.get_key():
            ret[k] = _create_map(for_create_map[g])
    return ret


__func_map_for_create: dict[PossibleGroup, PossibleClassMap] = {
    # abstract
    ACDgroup((0, 0, 1)): DataMap,
    ACDgroup((0, 0, 2)): DataMap,
    ACDEgroup((0, 0, 2, 1)): ClassMap(impl.data.ActiveFirmwareId),
    ACDgroup((0, 0, 9)): DataMap,
    ACDgroup((0, 1, 0)): ClockMap,
    ACDgroup((0, 1, 1)): DataMap,
    ACDgroup((0, 1, 2)): DataMap,
    ACDgroup((0, 1, 3)): DataMap,
    ACDgroup((0, 1, 4)): DataMap,
    ACDgroup((0, 1, 5)): DataMap,
    ACDgroup((0, 1, 6)): DataMap,
    ACDEgroup((0, 2, 0, 0)): ModemConfigurationMap,
    #
    ACDEEgroup((0, 10, 0, (0, 1, 125)+tuple(range(100, 112)))): ScriptTableMap,
    ACDgroup((0, 11, 0)): SpecialDaysTableMap,
    ACDgroup((0, 12, 0)): ScheduleMap,
    ACDgroup((0, 13, 0)): ActivityCalendarMap,
    ACDgroup((0, 14, 0)): RegisterActivationMap,
    ACDEEgroup((0, 15, 0, tuple(range(0, 8)))): SingleActionScheduleMap,
    ACDgroup((0, 16, 0)): RegisterMonitorMap,
    ACDEEgroup((0, 16, 1, tuple(range(0, 10)))): RegisterMonitorMap,
    #
    ACDgroup((0, 17, 0)): LimiterMap,
    #
    ACDDEEgroup((0, 19, tuple(range(50, 60)), (1, 2))): DataMap,
    #
    ACDgroup((0, 21, 0)): (DataMap, ProfileGenericMap),
    ACDEgroup((0, 22, 0, 0)): IECHDLCSetupMap,
    #
    ACDEgroup((0, 23, 2, 0)): DataMap,
    ACDEEgroup((0, 23, 3, tuple(range(0, 10)))): (DataMap, ProfileGenericMap),
    ACDEEgroup((0, 23, 3, tuple(range(10, 256)))): DataMap,
    #
    ACDgroup((0, 24, 2)): ExtendedRegisterMap,
    ACDgroup((0, 24, 3)): ProfileGenericMap,
    ACDEgroup((0, 24, 4, 0)): DisconnectControlMap,
    ACDEgroup((0, 24, 5, 0)): ProfileGenericMap,
    #
    ACDEgroup((0, 25, 0, 0)): TCPUDPSetupMap,
    ACDEgroup((0, 25, 1, 0)): IPv4SetupMap,
    #
    ACDEgroup((0, 25, 4, 0)): GPRSModemSetupMap,
    #
    ACDEgroup((0, 25, 6, 0)): GSMDiagnosticMap,
    #
    ACDEgroup((0, 25, 9, 0)): PushSetupMap,
    ACDEgroup((0, 25, 10, 0)): NTPSetupMap,
    #
    ABCDEEgroup((0, 0, 40, 0, tuple(range(8)))): (AssociationSNMap, AssociationLNMap),  # todo: now limit by 8 association, solve it
    #
    ABCDEgroup((0, 0, 42, 0, 0)): ClassMap(impl.data.LDN),
    ABCDEEgroup((0, 0, 43, 0, tuple(range(256)))): SecuritySetupMap,
    ACDgroup((0, 43, 1)): DataMap,
    #
    ABCDEEgroup((0, 0, 44, 0, tuple(range(256)))): ImageTransferMap,
    #
    ACDEEgroup((0, 96, 1, tuple(range(0, 11)))): ClassMap(impl.data.DLMSDeviceIDObject),
    ACDEgroup((0, 96, 1, 255)): ProfileGenericMap,  # todo: add RegisterTable
    ACDgroup((0, 96, 2)): DataDynamicMap,
    ACDEEgroup((0, 96, 3, tuple(range(0, 4)))): DataMap,  # todo: add StatusMapping
    ACDEgroup((0, 96, 3, 10)): DisconnectControlMap,
    ACDEEgroup((0, 96, 3, tuple(range(20, 29)))): ArbitratorMap,
    ACDDEgroup((0, 96, (4, 5), 0)): (DataMap, ProfileGenericMap),  # todo: add RegisterTable, StatusMapping
    ACDDEEgroup((0, 96, (4, 5), (1, 2, 3, 4))): DataMap,  # todo: add StatusMapping
    ACDEEgroup((0, 96, 6, tuple(range(0, 7)))): (DataMap, RegisterMap,  ExtendedRegisterMap),
    ACDEEgroup((0, 96, 7, tuple(range(0, 22)))): (DataMap, RegisterMap,  ExtendedRegisterMap),
    ACDEEgroup((0, 96, 8, tuple(range(0, 64)))): (DataMap, RegisterMap,  ExtendedRegisterMap),
    ACDEEgroup((0, 96, 9, (0, 1, 2))): (RegisterMap,  ExtendedRegisterMap),
    ACDEEgroup((0, 96, 10, tuple(range(1, 10)))): DataMap,  # todo: add StatusMapping
    ACDEEgroup((0, 96, 11, tuple(range(100)))): (DataDynamicMap, RegisterMap,  ExtendedRegisterMap),
    ACDEEgroup((0, 96, 12, (0, 1, 2, 3, 5, 6))): (DataMap, RegisterMap,  ExtendedRegisterMap),
    ACDEgroup((0, 96, 12, 4)): ClassMap(impl.data.CommunicationPortParameter),
    ACDEEgroup((0, 96, 13, (0, 1))): (DataMap, RegisterMap,  ExtendedRegisterMap),
    ACDEEgroup((0, 96, 14, tuple(range(16)))): (DataMap, RegisterMap,  ExtendedRegisterMap),
    ACDEEgroup((0, 96, 15, tuple(range(100)))): (DataMap, RegisterMap,  ExtendedRegisterMap),
    ACDEEgroup((0, 96, 16, tuple(range(10)))): (DataMap, RegisterMap,  ExtendedRegisterMap),
    ACDEEgroup((0, 96, 17, tuple(range(128)))): (DataMap, RegisterMap,  ExtendedRegisterMap),
    ACDgroup((0, 96, 20)): (DataMap, RegisterMap,  ExtendedRegisterMap),
    ACDEEgroup((0, 97, 97, tuple(range(10)))): DataMap,
    ACDDEgroup((0, 97, (97, 98), 255)): ProfileGenericMap,  # todo: add RegisterTable
    ACDEEgroup((0, 97, 98, tuple(range(10))+tuple(range(10, 30)))): DataMap,
    ACgroup((0, 98)): ProfileGenericMap,
    ACDgroup((0, 99, 98)): ProfileGenericMap,
    # electricity
    ACDEEgroup((1, 0, 0, tuple(range(10)))): DataMap,
    ACDEgroup((1, 0, 0, 255)): ProfileGenericMap,  # todo: add RegisterTable
    ACDgroup((1, 0, 1)): DataMap,
    ACDgroup((1, 0, 2)): DataStaticMap,
    ACDDgroup((1, 0, (3, 4, 7, 8, 9))): (DataStaticMap, RegisterMap, ExtendedRegisterMap),
    ACDDgroup((1, 0, (6, 10))): (RegisterMap, ExtendedRegisterMap),
    ACDEEgroup((1, 0, 11, tuple(range(1, 8)))): DataMap,
    ACDEEgroup((1, 96, 1, tuple(range(10)))): DataMap,
    ACDEgroup((1, 96, 1, 255)): ProfileGenericMap,  # todo: add RegisterTable
    ACDEEgroup((1, 96, 5, (0, 1, 2, 3, 4, 5))): DataMap,  # todo: add StatusMapping
    ACDEEgroup((1, 96, 10, (0, 1, 2, 3))): DataMap,  # todo: add StatusMapping
    ACgroup((1, 98)): ProfileGenericMap,
    ACDDgroup((1, 99, (1, 2, 11, 12, 97, 98, 99))): ProfileGenericMap,
    ACDDEgroup((1, 99, (3, 13, 14), 0)): ProfileGenericMap,
    ACDEEgroup((1, 99, 10, (1, 2, 3))): ProfileGenericMap,
    ACCDgroup((1, _CUMULATIVE, _RU_CHANGE_LIMIT_LEVEL)): RegisterMap,
    ACCDDgroup((
        1,
        _NOT_PROCESSING_OF_MEASUREMENT_VALUES,
        tuple(chain(
            _CUMULATIVE,
            _TIME_INTEGRAL_VALUES,
            _CONTRACTED_VALUES,
            _UNDER_OVER_LIMIT_THRESHOLDS,
            _UNDER_OVER_LIMIT_OCCURRENCE_COUNTERS,
            _UNDER_OVER_LIMIT_DURATIONS,
            _UNDER_OVER_LIMIT_MAGNITUDES
        )))): (RegisterMap, ExtendedRegisterMap),
    ACCDDgroup((1, _NOT_PROCESSING_OF_MEASUREMENT_VALUES, _INSTANTANEOUS_VALUES)): RegisterMap,
    ACCDDgroup((1, _NOT_PROCESSING_OF_MEASUREMENT_VALUES, _MAX_MIN_VALUES)): (RegisterMap, ExtendedRegisterMap, ProfileGenericMap),
    ACCDDgroup((1, _NOT_PROCESSING_OF_MEASUREMENT_VALUES, _CURRENT_AND_LAST_AVERAGE_VALUES)): (RegisterMap, DemandRegisterMap),
    ACCDgroup((1, _NOT_PROCESSING_OF_MEASUREMENT_VALUES, 40)): (DataMap, RegisterMap),
}

func_maps["DLMS_6"] = get_func_map(__func_map_for_create)


# SPODES3 Update
__func_map_for_create.update({
    ACDgroup((0, 21, 0)): ProfileGenericMap.renew(1, impl.profile_generic.SPODES3DisplayReadout),
    ACDEEgroup((0, 96, 1, (0, 2, 4, 5, 8, 9, 10))): ClassMap(impl.data.SPODES3IDNotSpecific),
    ACDEgroup((0, 96, 1, 6)): ClassMap(impl.data.SPODES3SPODESVersion),
    ACDEEgroup((0, 96, 2, (1, 2, 3, 5, 6, 7, 11, 12))): ClassMap(impl.data.AnyDateTime),
    ACDEgroup((0, 96, 3, 20)): ClassMap(impl.arbitrator.SPODES3Arbitrator),
    ACDEgroup((0, 96, 4, 3)): ClassMap(impl.data.SPODES3LoadLocker),
    ACDEgroup((0, 96, 5, 1)): ClassMap(impl.data.SPODES3PowerQuality2Event),
    ACDEgroup((0, 96, 5, 4)): ClassMap(impl.data.SPODES3PowerQuality1Event),
    ACDEgroup((0, 96, 5, 132)): ClassMap(impl.data.Unsigned),  # TODO: make according with СПОДЭС3 13.9. Контроль чередования фаз
    ACDEgroup((0, 96, 11, 0)): ClassMap(impl.data.SPODES3VoltageEvent),
    ACDEgroup((0, 96, 11, 1)): ClassMap(impl.data.SPODES3CurrentEvent),
    ACDEgroup((0, 96, 11, 2)): ClassMap(impl.data.SPODES3CommutationEvent),
    ACDEgroup((0, 96, 11, 3)): ClassMap(impl.data.SPODES3ProgrammingEvent),
    ACDEgroup((0, 96, 11, 4)): ClassMap(impl.data.SPODES3ExternalEvent),
    ACDEgroup((0, 96, 11, 5)): ClassMap(impl.data.SPODES3CommunicationEvent),
    ACDEgroup((0, 96, 11, 6)): ClassMap(impl.data.SPODES3AccessEvent),
    ACDEgroup((0, 96, 11, 7)): ClassMap(impl.data.SPODES3SelfDiagnosticEvent),
    ACDEgroup((0, 96, 11, 8)): ClassMap(impl.data.SPODES3ReactivePowerEvent),
    ABCDEgroup((0, 0, 96, 51, 0)): ClassMap(impl.data.OpeningBody),
    ABCDEgroup((0, 0, 96, 51, 1)): ClassMap(impl.data.OpeningCover),
    ABCDEgroup((0, 0, 96, 51, 3)): ClassMap(impl.data.ExposureToMagnet),
    ABCDEgroup((0, 0, 96, 51, 4)): ClassMap(impl.data.ExposureToHSField),
    ABCDEgroup((0, 0, 96, 51, 5)): ClassMap(impl.data.SealStatus),
    ABCDEEgroup((0, 0, 96, 51, (6, 7))): UnsignedDataMap,
    ABCDEEgroup((0, 0, 96, 51, (8, 9))): ClassMap(impl.data.OctetStringDateTime),
    ABCDEEgroup((0, 0, 97, 98, (0, 10, 20))): ClassMap(impl.data.SPODES3Alarm1),
    ABCDEEgroup((0, 0, 97, 98, (1, 11))): ClassMap(impl.data.SPODES3ControlAlarm1),
    # electricity
    ACDEEgroup((1, 0, 8, (4, 5))): ClassMap(impl.data.SPODES3MeasurementPeriod),
    ACDgroup((1, 98, 1)): ProfileGenericMap.renew(1, impl.profile_generic.SPODES3MonthProfile),
    ACDgroup((1, 98, 2)): ProfileGenericMap.renew(1, impl.profile_generic.SPODES3DailyProfile),
    ACDDgroup((1, 99, (1, 2))): ProfileGenericMap.renew(1, impl.profile_generic.SPODES3LoadProfile),
    ABCDEgroup((1, 0, 131, 35, 0)): RegisterMap,
    ABCDEgroup((1, 0, 133, 35, 0)): RegisterMap,
    ABCDEgroup((1, 0, 147, 133, 0)): RegisterMap,
    ABCDEgroup((1, 0, 148, 136, 0)): RegisterMap,
    ACDEgroup((1, 94, 7, 0)): ProfileGenericMap.renew(1, impl.profile_generic.SPODES3CurrentProfile),
    ACDEEgroup((1, 94, 7, (1, 2, 3, 4, 5, 6))): ProfileGenericMap.renew(1, impl.profile_generic.SPODES3ScalesProfile),  # Todo: RU. Scaler-profile With 1 entry and more
})

func_maps["SPODES_3"] = get_func_map(__func_map_for_create)

# KPZ Update
__func_map_for_create.update({
    ACDEgroup((0, 96, 11, 4)): ClassMap(impl.data.KPZSPODES3ExternalEvent),
    ABCDEEgroup((0, 0, 97, 98, (0, 10, 20))): ClassMap(impl.data.KPZAlarm1),
    ABCDEgroup((0, 128, 25, 6, 0)): ClassMap(impl.data.DataStatic),
    ABCDEEgroup((0, 128, 96, 2, (0, 1, 2))): ClassMap(impl.data.KPZAFEOffsets),
    ABCDEgroup((0, 128, 96, 13, 1)): ClassMap(impl.data.ITEBitMap),
    ABCDEgroup((0, 128, 154, 0, 0)): ClassMap(impl.data.KPZGSMPingIP),
    ACDEEgroup((0, 0, 128, (100, 101, 102, 103, 150, 151, 152, 170))): DataMap,
    ABCCDEgroup((128, 0, tuple(range(20)), 0, 0)): RegisterMap
})
func_maps["KPZ"] = get_func_map(__func_map_for_create)
# KPZ1 with bag in log event profiles
__func_map_for_create.update({
    ACDEgroup((0, 96, 11, 0)): ClassMap(impl.data.KPZ1SPODES3VoltageEvent),
    ACDEgroup((0, 96, 11, 1)): ClassMap(impl.data.KPZ1SPODES3CurrentEvent),
    ACDEgroup((0, 96, 11, 2)): ClassMap(impl.data.KPZ1SPODES3CommutationEvent),
    ACDEgroup((0, 96, 11, 3)): ClassMap(impl.data.KPZ1SPODES3ProgrammingEvent),
    ACDEgroup((0, 96, 11, 4)): ClassMap(impl.data.KPZ1SPODES3ExternalEvent),
    ACDEgroup((0, 96, 11, 5)): ClassMap(impl.data.KPZ1SPODES3CommunicationEvent),
    ACDEgroup((0, 96, 11, 6)): ClassMap(impl.data.KPZ1SPODES3AccessEvent),
    ACDEgroup((0, 96, 11, 7)): ClassMap(impl.data.KPZ1SPODES3SelfDiagnosticEvent),
    ACDEgroup((0, 96, 11, 8)): ClassMap(impl.data.KPZ1SPODES3ReactivePowerEvent),
})
func_maps["KPZ1"] = get_func_map(__func_map_for_create)


def get_type(c_id: int,
             ver: int,
             obis: Obis,
             func_map: FUNC_MAP) -> result.SimpleOrError[type[IC]]:
    """use DLMS UA 1000-1 Ed. 14 Table 54"""
    c_m: Optional[dict[int, ClassMap]]
    if (
        (128 <= attr2b(obis) <= 199)
        or (128 <= attr2c(obis) <= 199)
        or obis[2] == 240
        or (128 <= attr2d(obis) <= 254)
        or (128 <= attr2e(obis) <= 254)
        or (128 <= attr2f(obis) <= 254)
    ):
        # try search in ABCDE group for manufacture object before in CDE
        c_m = func_map.get(obis[:5], common_interface_class_map)
    else:
        # try search in ABCDE group
        c_m = func_map.get(obis[:5], None)
        if c_m is None:
            # try search in A-CDE group
            c_m = func_map.get(obis[:1] + obis[2:5], None)
            if c_m is None:
                # try search in A-CD group
                c_m = func_map.get(obis[:1] + obis[2:4], None)
                if c_m is None:
                    # try search in A-C group
                    c_m = func_map.get(obis[:1] + obis[3:4], common_interface_class_map)
    return get_interface_class(class_map=c_m,
                               c_id=c_id,
                               ver=ver)


@lru_cache(20000)
def get_unit(class_id: ClassID, elements: Iterable[int]) -> Optional[int]:
    match class_id, *elements:
        case (ClassID.LIMITER, 6 | 7) | (ClassID.LIMITER, 8, 2) | (ClassID.DEMAND_REGISTER, 8) | (ClassID.PROFILE_GENERIC, 4) | (ClassID.PUSH_SETUP, 5) |\
             (ClassID.PUSH_SETUP, 7, _) | (ClassID.PUSH_SETUP, 12, 1) | (ClassID.COMMUNICATION_PORT_PROTECTION, 4 | 6) | (ClassID.CHARGE, 8) | (ClassID.IEC_HDLC_SETUP, 8) \
             | (ClassID.AUTO_CONNECT, 4):
            return 7  # second
        case ClassID.CLOCK, 3 | 7:
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


type ObjFilteredKey = tuple[ClassID | LNPattern | LNPatterns | Channel, ...]


def get_filtered(objects: Iterable[IC],
                 keys: ObjFilteredKey) -> list[IC]:
    c_ids: list[ut.CosemClassId] = []
    patterns: list[LNPattern] = []
    ch: Optional[Channel] = None
    for k in keys:
        if isinstance(k, ut.CosemClassId):
            c_ids.append(k)
        elif isinstance(k, LNPattern):
            patterns.append(k)
        elif isinstance(k, LNPatterns):
            patterns.extend(k)
        elif isinstance(k, Channel):
            ch = k
    new_list = []
    for obj in objects:
        if obj.CLASS_ID in c_ids:
            pass
        elif obj.obis in patterns:
            pass
        else:
            continue
        if ch and not ch.is_approve(obj.obis[1]):
            continue
        new_list.append(obj)
    return new_list


@deprecated("use <AttrData>")
@dataclass(unsafe_hash=True, frozen=True)
class ParameterValue:
    par: bytes
    value: bytes

    def __str__(self) -> str:
        return F"{'.'.join(map(str, self.par[:6]))}:{self.par[6]} - {cdt.get_instance_and_pdu_from_value(self.value)[0].__repr__()}"

    def __bytes__(self) -> bytes:
        """par + 0x00 + value"""  # todo: 00 in future other parameters
        return self.par + b'\x00' + self.value

    @classmethod
    def parse(cls, value: bytes) -> Self:
        if value[7] != 0:
            raise exc.ITEApplication(F"wrong {value!r} for {cls.__name__}")
        return cls(
            par=value[:7],
            value=value[8:]
        )


@dataclass(unsafe_hash=True, frozen=True)
class AttrData:
    attr: Attr
    data: Encoding

    def __str__(self) -> str:
        return f"{".".join(map(str, attr2obis(self.attr)))}:{attr2i(self.attr)} - {cdt.get_instance_and_pdu_from_value(self.data)[0].__repr__()}"

    def __bytes__(self) -> bytes:
        return self.attr + self.data

    @classmethod
    def parse(cls, value: bytes) -> Self:
        return cls(value[:7], value[7:])


@dataclass(frozen=True, unsafe_hash=True)
class ID:
    man: bytes
    f_id: AttrData
    f_ver: AttrData
    sap: ClientSAP

    def __bytes__(self) -> bytes:
        return self.man + self.sap.contents + bytes(self.f_id) + bytes(self.f_ver)


class EmptyAttribute(exc.DLMSException):
    """need read attribute"""
    def __init__(self,
                 ln: cst.LogicalName,
                 i: int):
        Exception.__init__(self, F"empty {ln}: {i}")
        self.ln = ln
        self.i = i


class Collection:
    __id: ID
    __dlms_ver: int
    __country: Optional[CountrySpecificIdentifiers]
    __country_ver: Optional[AttrData]
    __objs: dict[Obis, IC]
    _data: dict[Attr, DataType]
    _t: dict[Attr, Tag]
    spec_map: str

    def __init__(self,
                 id_: ID,
                 dlms_ver: int = 6,
                 country: Optional[CountrySpecificIdentifiers] = None,
                 cntr_ver: Optional[AttrData] = None):
        self.__id = id_
        self.__dlms_ver = dlms_ver
        self.__country = country
        self.__country_ver = cntr_ver
        """country version specification"""
        self.spec_map = "DLMS_6"
        self.__objs = {}
        """all DLMS objects container with obis key"""
        self._data = {}
        """data of collection"""
        self._t = {}
        """expected Tags of Attributes"""

    def getCDT(self, attr: Attr) -> result.SimpleOrError[DataType]:
        if (data := self._data.get(attr)) is None:
            return result.Error.from_e(ValueError(f"not find data in collection with {attr=}"))
        return result.Simple(data)

    def get[T: DataType](self, attr: Attr, e_type: type[T]) -> result.SimpleOrError[T]:
        if (data := self._data.get(attr)) is None:
            return result.Error.from_e(ValueError(f"not find data in collection with {attr=}"))
        if isinstance(data, e_type):
            return result.Simple(data)
        return result.Error.from_e(TypeError(f"got {data.__class__}, expected {e_type}"))

    @property
    def id(self) -> ID:
        return self.__id

    def validate_id(self, value: ID) -> result.Ok | result.Error:
        if value != self.__id:
            return result.Error.from_e(ValueError(F"can't set ID: {value}, find {self.__id}"))
        return result.OK

    def add_from_object_list(self, obj_list: ObjectListType) -> result.StrictOk | result.Error:
        res = result.StrictOk()
        for o_l_el in obj_list:
            if isinstance(res_new := self.addIC(
                    c_id=o_l_el.class_id.normalize(),
                    version=o_l_el.version.normalize(),
                    obis=o_l_el.logical_name.contents
            ), result.Error):
                res.append_err(res_new.err)
        return res

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Collection):
            return hash(self) == hash(other)
        raise NotImplementedError

    def __hash__(self) -> int:
        return hash(self.id)

    @property
    def dlms_ver(self) -> int:
        return self.__dlms_ver

    def set_dlms_ver(self, value: int) -> result.Ok | result.Error:
        if not self.__dlms_ver:
            self.__dlms_ver = value
        elif value != self.__dlms_ver:
            return result.Error.from_e(ValueError(F"got dlms_version: {value}, expected {self.__dlms_ver}"))
        return result.OK

    @property
    def country(self) -> Optional[CountrySpecificIdentifiers]:
        return self.__country

    def set_country(self, value: CountrySpecificIdentifiers) -> result.Ok | result.Error:
        if not self.__country:
            self.__country = value
        elif value != self.__country:
            return result.Error.from_e(ValueError(F"got country: {value}, expected {self.__country}"))
        return result.OK

    @property
    def country_ver(self) -> Optional[AttrData]:
        return self.__country_ver

    def set_country_ver(self, value: AttrData) -> result.Ok | result.Error:
        """country version specification"""
        if not self.__country_ver:
            self.__country_ver = value
        elif value != self.__country_ver:
            return result.Error.from_e(ValueError(F"got country version: {value}, expected {self.__country_ver}"))
        return result.OK

    def __str__(self) -> str:
        return F"[{len(self.__objs)}] DLMS version: {self.__dlms_ver}, country: {self.__country}, country specific version: {self.__country_ver}, " \
               F"id: {self.id}, uses specification: {self.spec_map}"

    def __iter__(self) -> Iterator[IC]:
        return iter(self.__objs.values())

    def get_spec(self) -> str:
        """return functional map to specification by identification fields"""
        match self.id.man:
            case b"KPZ":
                return "KPZ"
            case b"101" | b"102" | b"103" | b"104":
                return "KPZ1"
            case _:
                if self.country_ver:
                    if self.country == CountrySpecificIdentifiers.RUSSIA:
                        if (
                            self.country_ver.attr == b'\x00\x00`\x01\x06\xff\x02'
                            and SemVer.parse(bytes(cdt.OctetString(self.country_ver.data)), True) == SemVer(3, 0)
                        ):
                            return "SPODES_3"
                if self.dlms_ver == 6:
                    return "DLMS_6"
                else:
                    raise exc.DLMSException("unknown specification")

    def __getitem__(self, item: Obis) -> IC:
        return self.__objs[item]

    def attr2ICAElement(self, obis: Obis, i: Index) -> result.SimpleOrError[ICAElement]:
        if isinstance(r_ic := self.obis2ic(obis), result.Error):
            return r_ic
        return r_ic.value.getAElement(i)

    @deprecated("use <obis2ic> or <obis2obj>")
    def par2obj(self, par: Parameter) -> result.SimpleOrError[IC]:
        """return: DLMSObject"""
        return self.obis2ic(par.obis)

    def par2data(self, par: Parameter) -> result.Option[cdt.CommonDataType] | result.Error:
        """:return CDT by Parameter, return None if data wasn't setting"""
        if isinstance((r_obj := self.obis2ic(par.obis)), result.Error):
            return r_obj
        res = result.Option(r_obj.value.get_attr(par.i))
        if res.value is None:
            return res
        for i, el in enumerate(par.elements()):
            if isinstance(res.value, cdt.ComplexDataType):
                res.value = res.value[el]
            else:
                return result.Error.from_e(ValueError(f"object with {par} not has element {i}"))
        return res

    def values(self) -> tuple[IC, ...]:
        return tuple(self.__objs.values())

    def __len__(self) -> int:
        return len(self.__objs)

    def setupCDT(self, attr: Attr, encoding: Encoding) -> result.Simple[cdt.CommonDataType] | result.Error:
        if isinstance(res_obj := self.obis2ic(attr2obis(attr)), result.Error):
            return res_obj
        if isinstance(res_data := res_obj.value.getCDT(attr2i(attr), encoding), result.Error):
            return res_data.with_msg(f"{res_obj.value}:{attr2i(attr)}")
        return self.setup_data(attr, res_data.value)

    def setup[T: cdt.CommonDataType](self, attr: Attr, encoding: Encoding, e_type: type[T]) -> result.Simple[T] | result.Error:
        if isinstance(res_obj := self.obis2ic(attr2obis(attr)), result.Error):
            return res_obj
        if isinstance(res_data := res_obj.value.get(attr2i(attr), encoding, e_type), result.Error):
            return res_data
        return self.setup_data(attr, res_data.value)

    def setup_data[T: cdt.CommonDataType](self, attr: Attr, data: T) -> result.Simple[T] | result.Error:
        if data != self._data.setdefault(attr, data):
            return result.Error.from_e(ValueError(f"collection already exist other <Encoding> for {attr=}"))
        return result.Simple(data)

    def setupTag(self, attr: Attr, encoding: Tag | Encoding) -> result.Simple[Tag] | result.Error:
        tag = encoding[:1]  # use only 1 byte
        obis, i = unpack_attr(attr)
        if isinstance(res_obj := self.obis2ic(obis), result.Error):
            return res_obj
        if isinstance(res_el := res_obj.value.getAElement(i), result.Error):
            return res_el
        if not isinstance(d_t := res_el.value.DATA_TYPE, ut.CHOICE):
            return result.Error.from_e(TypeError(f"{res_obj.value}:{attr2i(attr)} can't setup TAG to not CHOICE element"))
        expected = d_t.get_types()
        if not any((t_.TAG == tag for t_ in expected)):
            return result.Error.from_e(TypeError(f"{res_obj.value}:{attr2i(attr)} got tag: {tag[0]}, expected {",".join(map(str, (t_.TAG for t_ in expected)))}"))
        if tag != self._t.setdefault(attr, tag):
            return result.Error.from_e(ValueError(f"collection already exist oter <Tag> for {attr=}"))
        return result.Simple(tag)

    def addIC(self, c_id: int,
              version: Optional[int],
              obis: Obis) -> result.SimpleOrError[IC]:
        """ append new DLMS object to collection with return it"""
        if isinstance(r_ic_type := get_type(
            c_id=c_id,
            ver=self.find_version(c_id) if version is None else version,
            obis=obis,
            func_map=func_maps[self.spec_map]), result.Error):
            return r_ic_type
        new = r_ic_type.value(obis)
        return result.Simple(self.__objs.setdefault(obis, new))

    def get_class_version(self) -> dict[ut.CosemClassId, cdt.Unsigned]:
        """use for check all class version by unique"""
        ret: dict[ut.CosemClassId, cdt.Unsigned] = {}
        for obj in self.__objs.values():
            if ver := ret.get(obj.CLASS_ID):
                if obj.VERSION != ver:
                    raise ValueError(F"for {obj.CLASS_ID=} exist several versions: {obj.VERSION}, {ver} in one collection")
            else:
                ret[obj.CLASS_ID] = obj.VERSION
        return ret

    def get_n_phases(self) -> int:
        """search objects with L2 phase"""
        ret: int | None = None
        for obj in filter(lambda obj: attr2a(obj.obis) == 1, self):
            if 41 <= attr2c(obj.obis) <= 60:
                return 3
            ret = 1
        if ret is None:
            raise exc.NoObject("no one electricity object was find")
        else:
            return ret

    @lru_cache(maxsize=100)  # amount of all ClassID
    def find_version(self, class_id: ut.CosemClassId) -> int:
        """use for add new object from profile_generic if absence in object list"""
        return next(filter(lambda obj: obj.CLASS_ID == class_id, self.__objs.values())).VERSION

    def is_in_collection(self, value: LNContaining) -> bool:
        obis = lnContents2obis(value)
        return False if self.__objs.get(obis) is None else True

    def get_object(self, value: LNContaining) -> IC:
        """ return object from obis<string> or raise exception if it absence """
        return self.obis2ic(lnContents2obis(value)).unwrap()

    @deprecated("use <par2rep>")
    def get_report(self,
                   obj: IC,
                   par: bytes,
                   a_val: Optional[cdt.CommonDataType]
                   ) -> cdt.Report:
        """par: attribute_index, par1, par2, ..."""
        rep = cdt.Report(str(a_val))
        try:
            if a_val is None:
                rep.msg = settings.report.empty
                rep.log = cdt.EMPTY_VAL
            elif isinstance(a_val, cdt.ReportMixin):
                rep = a_val.get_report()
            elif isinstance(a_val, DayProfileAction):
                rep.msg = F"{get_message("$rate$")}-{a_val.script_selector}: {a_val.start_time}"
                if isinstance(script_obj := self.get_object(a_val.script_logical_name), ScriptTable):
                    for script in script_obj.scripts:
                        if script.script_identifier == a_val.script_selector:
                            break
                    else:
                        rep.log = cdt.Log(logging.ERROR, F"absent script with ID: {a_val.script_selector}")
                else:
                    rep.log = cdt.Log(logging.ERROR, f"wrong script object with {a_val.script_logical_name}")
            else:
                if unit := get_unit(obj.CLASS_ID, par):
                    rep.unit = cdt.Unit(unit).get_name()
                else:
                    if s_u := self.get_scaler_unit(obj, par):
                        rep.msg = (settings.report.scaler_format).format(int(a_val) * 10 ** int(s_u.scaler))
                        rep.unit = s_u.unit.get_name()
                    else:
                        match obj.CLASS_ID, *par:
                            case (ClassID.PROFILE_GENERIC, 3, _) | (ClassID.PROFILE_GENERIC, 6):
                                a_val: structs.CaptureObjectDefinition
                                obj = self.get_object(a_val.logical_name)
                                rep.msg = F"{obis2name(obj.obis)}.{obj.get_attr_element(int(a_val.attribute_index))}"
                            case _:
                                pass
                rep.log = cdt.Log(logging.INFO)
        except Exception as e:
            rep.log = cdt.Log(logging.ERROR, e)
        finally:
            return rep

    def par2rep(self, par: Parameter, data: Optional[cdt.CommonDataType]) -> cdt.Report:
        rep = cdt.Report(str(data))
        try:
            if data is None:
                rep.msg = settings.report.empty
                rep.log = cdt.EMPTY_VAL
            elif isinstance(data, cdt.ReportMixin):
                rep = data.get_report()
            elif isinstance(data, DayProfileAction):
                rep.msg = F"{get_message("$rate$")}-{data.script_selector}: {data.start_time}"
                if isinstance(script_obj := self.get_object(data.script_logical_name), ScriptTable):
                    for script in script_obj.scripts:
                        if script.script_identifier == data.script_selector:
                            break
                    else:
                        rep.log = cdt.Log(logging.ERROR, F"absent script with ID: {data.script_selector}")
                else:
                    rep.log = cdt.Log(logging.ERROR, f"wrong script object with {data.script_logical_name}")
            else:
                obj = self.par2obj(par).unwrap()
                elements = tuple(par.elements())
                if unit := get_unit(obj.CLASS_ID, elements):
                    rep.unit = cdt.Unit(unit).get_name()
                else:
                    if s_u := self.par2su(par):
                        rep.msg = (settings.report.scaler_format).format(int(data) * 10 ** int(s_u.scaler))
                        rep.unit = s_u.unit.get_name()
                    else:
                        match obj.CLASS_ID, *elements:
                            case (ClassID.PROFILE_GENERIC, 3, _) | (ClassID.PROFILE_GENERIC, 6):
                                data_: structs.CaptureObjectDefinition
                                obj = self.get_object(data_.logical_name)
                                rep.msg = F"{obis2name(obj.obis)}.{obj.get_attr_element(int(data_.attribute_index))}"
                            case _:
                                pass
                rep.log = cdt.Log(logging.INFO)
        except Exception as e:
            rep.log = cdt.Log(logging.ERROR, e)
        finally:
            return rep

    @deprecated("use par2su")
    def get_scaler_unit(self,
                        obj: IC,
                        par: bytes
                        ) -> cdt.ScalUnitType | None:
        match obj.CLASS_ID, *par:
            case (ClassID.REGISTER | ClassID.EXT_REGISTER, 2) | (ClassID.DEMAND_REGISTER, 2 | 3):
                obj: Register | DemandRegister
                if (s_u := obj.scaler_unit) is None:
                    raise EmptyAttribute(obj.logical_name, 3)
                else:
                    if (s := cdt.get_unit_scaler(s_u.unit.contents)) != 0:
                        s_u = copy(s_u)
                        s_u.scaler.set(int(s_u.scaler)-s)
                    return s_u
            case ClassID.LIMITER, 3 | 4 | 5:
                obj: Limiter
                if m_v := obj.monitored_value:
                    return self.get_scaler_unit(  # recursion 1 level
                        obj=self.get_object(m_v.logical_name),
                        par=m_v.attribute_index.contents)
                else:
                    raise EmptyAttribute(obj.logical_name, 2)
            case ClassID.REGISTER_MONITOR, 2, _:
                obj: RegisterMonitor
                if (m_v := obj.monitored_value) is None:
                    raise EmptyAttribute(obj.logical_name, 3)
                else:
                    return self.get_scaler_unit(  # recursion 1 level
                        obj=self.get_object(m_v.logical_name),
                        par=m_v.attribute_index.contents
                    )
            case _:
                return None

    @lru_cache(20000)
    def par2su(self, par: Parameter) -> Optional[cdt.ScalUnitType]:
        """convert Parameter -> Optional[ScalerUnit],
        raise: NoObject, EmptyAttribute"""
        match (obj := self.obis2ic(par.obis).unwrap()), par.i:
            case (exc.NoObject, _):
                raise obj
            case (ClassID.REGISTER | ClassID.EXT_REGISTER, 2) | (ClassID.DEMAND_REGISTER, 2 | 3):
                obj: Register | DemandRegister
                if (s_u := obj.scaler_unit) is None:
                    raise EmptyAttribute(obj.logical_name, 3)
                else:
                    if (s := cdt.get_unit_scaler(s_u.unit.contents)) != 0:
                        s_u = copy(s_u)
                        s_u.scaler.set(int(s_u.scaler)-s)
                    return s_u
            case ClassID.LIMITER, 3 | 4 | 5:
                obj: Limiter
                if m_v := obj.monitored_value:
                    return self.par2su(Parameter(m_v.logical_name.contents).set_i(int(m_v.attribute_index)))  # recursion 1 level
                else:
                    raise EmptyAttribute(obj.logical_name, 2)
            case ClassID.REGISTER_MONITOR, 2, _:
                obj: RegisterMonitor
                if (m_v := obj.monitored_value) is None:
                    raise EmptyAttribute(obj.logical_name, 3)
                else:
                    return self.par2su(Parameter(m_v.logical_name.contents).set_i(int(m_v.attribute_index)))  # recursion 1 level
            case _:
                return None

    def par2float(self, par: Parameter) -> float:
        """try convert CDT value according with Parameter to build-in float"""
        data = self.par2data(par).unwrap()
        if isinstance(data, cdt.Digital):
            value = float(int(data))
        elif isinstance(data, cdt.Float):
            value = float(data)
        else:
            raise TypeError("can't convert Parameter data to int or float")
        if (su := self.par2su(par)):
            value *= 10 ** int(su.scaler)
        return value


    def filter_by_ass(self, ass_id: int) -> list[IC]:
        """return only association objects"""
        ret = []
        for olt in self.get(self.getASSOCIATION(ass_id).object_list, ObjectListType).unwrap():
            ret.append(self.obis2ic(olt.logical_name.contents).unwrap())
        return ret

    def sap2objects(self, sap: ClientSAP) -> result.List[IC]:
        res = result.List()
        for par in self.sap2association(sap).iter_pars():
            if isinstance(res1 := self.par2obj(par), result.Error):
                res1.append_err(res.err)
            else:
                res.append(res1)
        return res

    def iter_classID_objects(self,
                        class_id: ut.CosemClassId) -> Iterator[IC]:
        return (obj for obj in self.__objs.values() if obj.CLASS_ID == class_id)

    def iter_objects[T: IC](self, e_type: type[T]) -> Iterator[T]:
        return (obj for obj in self.__objs.values() if isinstance(obj, e_type))

    def LNPattern2objects(self,
                          pat: LNPattern) -> list[InterfaceClass]:
        ret = []
        for obj in self.__objs.values():
            if obj.obis in pat:
                ret.append(obj)
        return ret

    def get_first(self, values: list[str | bytes | cst.LogicalName]) -> InterfaceClass:
        """ return first object from it exist in collection from value"""
        for val in values:
            if self.is_in_collection(val):
                return self.get_object(val)
            else:
                """search next"""
        else:
            raise exc.NoObject(F"not found at least one DLMS Objects from collection with {values=}")

    @deprecated("use <iter_classID_objects>")
    def get_objects_by_class_id(self, value: ut.CosemClassId) -> list[InterfaceClass]:
        return list(filter(lambda obj: obj.CLASS_ID == value, self.__objs.values()))

    def get_writable_attr(self) -> result.SimpleOrError[UsedAttributes]:
        """return all writable {obj.ln: {attribute_index}}"""
        ret = {}
        res = result.Simple(ret)
        for ass in self.iter_classID_objects(ClassID.ASSOCIATION_LN):
            if attr2e(ass.obis) == 0:
                """skip current association"""
            elif isinstance(res_obj_list := self.get(AssociationLNVer0.object_list, ObjectListType, result.Error)):
                res.append_e(TypeError(f"got {type(res_obj_list.value)} expected {ObjectListType.__name__}"))
            else:
                for list_type in res.value:
                    for attr_access in list_type.access_rights.attribute_access:
                        if attr_access.access_mode.is_writable():
                            if ret.get(list_type.logical_name, None) is None:
                                ret[list_type.logical_name] = set()
                            ret[list_type.logical_name].add(int(attr_access.attribute_id))
        if (
            len(ret) == 0
            and res.err is not None
        ):
            return res.result
        return res

    def get_profile_s_u(self,
                        obj: ProfileGeneric,
                        mask: Optional[set[int]] = None
                        ) -> list[Optional[cdt.ScalUnitType]]:
        """return container of scaler_units if possible, mask: position number in capture_objects"""
        res: list[cdt.ScalUnitType | None] = []
        for i, obj_def in enumerate(obj.capture_objects):
            obj_def: structs.CaptureObjectDefinition
            if (
                mask
                and i not in mask
            ):
                continue
            s_u = None
            try:
                s_u = self.get_scaler_unit(
                    obj=self.get_object(obj_def.logical_name),
                    par=bytes([int(obj_def.attribute_index)]))
            except EmptyAttribute as e:
                print(F"Can't fill Scaler and Unit for {obis2name(obj_def.logical_name.contents)}: {e}")
            finally:
                res.append(s_u)
        return res

    def obis2ic(self, obis: Obis) -> result.SimpleOrError[IC]:
        if obj := self.__objs.get(obis, None):
            return result.Simple(obj)
        return result.Error.from_e(ValueError(f"not exist DLMSObject with {obis=}"))

    def obis2obj[T: IC](self, obis: Obis, e_type: type[T]) -> result.SimpleOrError[T]:
        if (obj := self.__objs.get(obis)) is None:
            return result.Error.from_e(ValueError(f"not exist DLMSObject with {obis=}"))
        if isinstance(obj, e_type):
            return result.Simple(obj)
        return result.Error.from_e(TypeError(f"got {obj} expected {e_type}"))

    def logicalName2obj(self, ln: cst.LogicalName) -> result.SimpleOrError[InterfaceClass]:
        return self.obis2ic(ln.contents)

    @cached_property
    @deprecated("use <c.ldn>")
    def LDN(self) -> impl.data.LDN:
        return self.obis2ic(b"\x00\x00\x2A\x00\x00\xff").unwrap()

    @cached_property
    def current_association(self) -> AssociationLN:
        return self.obis2ic(o.CURRENT_ASSOCIATION).unwrap()

    def getASSOCIATION(self, instance: int) -> AssociationLN:
        return self.obis2obj(bytes((0, 0, 40, 0, instance, 255)), AssociationLN).unwrap()

    def getObjectList(self, instance: int) -> ObjectListType:
        return self.get(self.getASSOCIATION(instance).object_list, ObjectListType).unwrap()

    @cached_property
    def PUBLIC_ASSOCIATION(self) -> AssociationLN:
        return self.obis2obj(bytes(0, 0, 40, 0, 1, 255), AssociationLN).unwrap()

    @property
    def COMMUNICATION_PORT_PARAMETER(self) -> impl.data.CommunicationPortParameter:
        return self.obis2ic(bytes((0, 0, 96, 12, 4, 255))).unwrap()

    @property
    def clock(self) -> Clock:
        return self.obis2ic(bytes((0, 0, 1, 0, 0, 255))).unwrap()

    @property
    def boot_image_transfer(self) -> ImageTransfer:
        return self.obis2ic(bytes((0, 0, 44, 0, 128, 255))).unwrap()

    @property
    def firmware_image_transfer(self) -> ImageTransfer:
        return self.obis2ic(bytes((0, 0, 44, 0, 0, 255))).unwrap()

    @property
    def firmwares_description(self) -> Data:
        """ Consist from boot_version, descriptor, ex.: 0005PWRM_M2M_3_F1_5ppm_Spvq. 0.0.128.100.0.255 """
        return self.obis2ic(bytes((0, 0, 128, 100, 0, 255))).unwrap()

    @property
    def RU_CLOSE_ELECTRIC_SEAL(self) -> Data:
        """ Russian. СПОДЕС Г.2 """
        return self.obis2ic(bytes((0, 0, 96, 51, 6, 255))).unwrap()

    @property
    def RU_ERASE_MAGNETIC_EVENTS(self) -> Data:
        """ Russian. СПОДЕС Г.2 """
        return self.obis2ic(bytes((0, 0, 96, 51, 7, 255))).unwrap()

    @property
    def RU_FILTER_ALARM_2(self) -> Data:
        """ Russian. Filter of Alarm register relay"""
        return self.obis2ic(bytes((0, 0, 97, 98, 11, 255))).unwrap()

    @property
    def RU_DAILY_PROFILE(self) -> ProfileGeneric:
        """ Russian. Profile of daily values """
        return self.obis2ic(bytes((1, 0, 98, 2, 0, 255))).unwrap()

    @property
    def RU_MAXIMUM_CURRENT_EXCESS_LIMIT(self) -> Register:
        """ RU. СТО 34.01-5.1-006-2021 ver3, 11.1. Maximum current excess limit before the subscriber is disconnected, % of IMAX """
        return self.obis2ic(bytes((1, 0, 11, 134, 0, 255))).unwrap()

    @property
    def RU_MAXIMUM_VOLTAGE_EXCESS_LIMIT(self) -> Register:
        """ RU. СТО 34.01-5.1-006-2021 ver3, 11.1. Maximum voltage excess limit before the subscriber is disconnected, % of Unominal """
        return self.obis2ic(bytes((1, 0, 12, 134, 0, 255))).unwrap()

    def getDISCONNECT_CONTROL(self, ch: int = 0) -> DisconnectControl:
        """DLMS UA 1000-1 Ed 14 6.2.46 Disconnect control objects by channel"""
        return self.obis2ic(bytes((0, ch, 96, 3, 10, 255))).unwrap()

    def getARBITRATOR(self, ch: int = 0) -> Arbitrator:
        """DLMS UA 1000-1 Ed 14 6.2.47 Arbitrator objects objects by channel"""
        return self.obis2obj(bytes((0, ch, 96, 3, 20, 255)), Arbitrator).unwrap()

    @property
    def boot_version(self) -> str:
        try:
            return self.firmwares_description.value.to_str()[:4]
        except Exception as e:
            print(e)
            return 'unknown'

    def get_script_names(self, ln: cst.LogicalName, selector: cdt.LongUnsigned) -> str:
        """return name from script by selector"""
        obj = self.obis2obj(ln.contents, ScriptTable).unwrap()
        for script in obj.scripts:
            script: ScriptTable.scripts
            if script.script_identifier == selector:
                names: list[str] = []
                for action in script.actions:
                    action_obj = self.obis2ic(action.logical_name.contents).unwrap()
                    if int(action_obj.CLASS_ID) != int(action.class_id):
                        raise ValueError(F"got {action_obj.CLASS_ID}, expected {action.class_id}")
                    match int(action.service_id):
                        case 1:  # for write
                            if isinstance(action.parameter, cdt.NullData):
                                names.append(str(action_obj.getAElement(int(action.index)).unwrap()))
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

    @lru_cache(4)
    def get_association_id(self, client_sap: ClientSAP) -> int:
        """return id(association instance) from it client address without current"""
        for ass in get_filtered(iter(self), (ln_pattern.NON_CURRENT_ASSOCIATION,)):
            if ass.associated_partners_id.client_SAP == client_sap:
                return attr2e(ass.logical_name)
            else:
                continue
        else:
            raise ValueError(F"absent association with {client_sap}")

    def sap2association(self, sap: ClientSAP) -> result.SimpleOrError[AssociationLN]:
        acc = result.ErrorAccumulator()
        for ass in self.iter_classID_objects(15):
            if isinstance(r_par_type := acc.merge_err(self.get(ass.associated_partners_id, AssociatedPartnersType)), result.Error):
                continue
            if r_par_type.value.client_SAP == sap:
                return result.Simple(ass)
        else:
            return acc.as_error(msg=F"hasn't association with {sap}")

    @lru_cache(maxsize=1000)
    def is_readable(self, obis: Obis,
                    i: int,
                    ass_id: int,
                    security_policy: pdu.SecurityPolicy = pdu.SecurityPolicyVer0.NOTHING
                    ) -> bool:
        return is_readable(self.getObjectList(ass_id), obis, i, security_policy)

    @lru_cache(maxsize=1000)
    def is_writable(self, obis: Obis,
                    i: int,
                    ass_id: int,
                    security_policy: pdu.SecurityPolicy = pdu.SecurityPolicyVer0.NOTHING
                    ) -> bool:
        return is_writable(self.getObjectList(ass_id), obis, i, security_policy)

    @lru_cache(maxsize=1000)
    def isnt_mutable(self,
                   par: Parameter,
                   association_id: int,
                   security_policy: pdu.SecurityPolicy = pdu.SecurityPolicyVer0.NOTHING
                   ) -> bool:
        """is not writable and STATIC data"""
        if (
            not self.is_writable(par.ln, par.i, association_id, security_policy, security_policy)
            and self.par2obj(par
                             ).unwrap().getAElement(par.i
                                                    ).unwrap().classifier == Classifier.STATIC
        ):
            return True
        return False

    @lru_cache(maxsize=1000)
    def is_accessible(self,
                      obis: Obis,
                      i: int,
                      ass_id: int,
                      m_id: int = MechanismIdElement.NONE
                      ) -> bool:
        """for ver 0 and 1 only"""
        return is_accessible(self.getObjectList(ass_id), obis, i, m_id)

    @lru_cache(maxsize=100)
    def get_name_and_type(self, value: structs.CaptureObjectDefinition) -> tuple[list[str], type[cdt.CommonDataType]]:
        """ return names and type of element from collection"""
        names: list[str] = []
        obj = self.obis2ic(value.logical_name.contents).unwrap()
        names.append(obis2name(obj.obis))
        attr_index = int(value.attribute_index)
        data_index = int(value.data_index)
        data_type: type[cdt.CommonDataType] = obj.get_attr_data_type(attr_index)
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
                      obj_filter: Optional[ObjFilteredKey] = None,
                      sort_mode: SortMode = "",
                      af_mode: Literal["l", "r", "w", "lr", "lw", "wr", "lrw", "m", "mlrw", "mlr"] = "l",
                      oi_filter: Optional[tuple[tuple[ut.CosemClassId, tuple[int, ...]], ...]] = None  # todo: maybe ai_filter with LNPattern, indexes need?
                      ) -> dict[ut.CosemClassId | media_id.MediaId, dict[IC, list[int]]] | dict[IC, list[int]]:  # todo: not all ret annotation
        """af_mode(attribute filter mode): l-reduce logical_name, r-show only readable, w-show only writeable,
        oi_filter(object attribute index filter), example: ((ClassID.REGISTER, (2,))) - is restricted for Register only Value attribute without logical_name and scaler_unit
        """
        objects: dict[IC, list[int]]
        without_ln = True if "l" in af_mode else False
        only_read = True if "r" in af_mode else False
        only_write = True if "w" in af_mode else False
        with_methods = True if "m" in af_mode else False
        oi_f = dict(oi_filter) if oi_filter else {}
        """objects indexes filter"""
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
                objects = {}
                for obj in v:
                    obj: IC
                    f_i = oi_f.get(obj.CLASS_ID)
                    """filter indexes"""
                    indexes = []
                    elements = obj.A_ELEMENTS
                    if not without_ln:
                        elements = _LN_ELEMENT + elements
                    for el in elements:
                        i = el.i
                        if only_read and not self.is_readable(obj.obis, i, ass_id):
                            continue
                        if only_write and not self.is_writable(obj.obis, i, ass_id):
                            continue
                        if f_i and i not in f_i:
                            continue
                        indexes.append(i)
                    if with_methods:
                        i_meth = count(1)
                        for i, m_el in zip(i_meth, obj.M_ELEMENTS):
                            try:
                                if (
                                    not self.is_accessible(obj.obis, i, ass_id, MechanismIdElement.LOW)
                                    or f_i and -i not in f_i
                                ):
                                    continue
                                indexes.append(-i)
                            except exc.ITEApplication as e:
                                print(F"skip {i}... methods for {obj}: {e}")
                                break
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


if config is not None:
    try:
        __collection_path = settings.collection.path
    except KeyError as e:
        raise exc.TomlKeyError(F"not find {e} in [DLMS.collection]<path>")


def lnContents2obis(value: LNContaining) -> Obis:
    """return LN as OBIS for use in any searching"""
    match value:
        case bytes():
            return value
        case cst.LogicalName() | ut.CosemObjectInstanceId():
            return value.contents
        case ut.CosemAttributeDescriptor() | ut.CosemMethodDescriptor():
            return value.instance_id.contents
        case ut.CosemAttributeDescriptorWithSelection():
            return value.cosem_attribute_descriptor.instance_id.contents
        case cdt.Structure(logical_name=value.logical_name):
            return value.logical_name.contents
        case cdt.Structure() as s:
            for it in s:
                if isinstance(it, cst.LogicalName):
                    return o.OBIS(it.contents)
            raise ValueError(F"can't convert {value=} to Logical Name contents. Struct {s} not content the Logical Name")
        case str() if value.find('.') != -1:
            return cst.LogicalName.from_obis(value).contents
        case str():
            return cst.LogicalName(value).contents
        case _:                                                          raise ValueError(F"can't convert {value=} to Logical Name contents")


class AttrDesc:
    """keep constant descriptors # todo: make better"""
    OBJECT_LIST = ut.CosemAttributeDescriptor((ClassID.ASSOCIATION_LN, ut.CosemObjectInstanceId("0.0.40.0.0.255"), ut.CosemObjectAttributeId(2)))
    LDN_VALUE = ut.CosemAttributeDescriptor((ClassID.DATA, ut.CosemObjectInstanceId("0.0.42.0.0.255"), ut.CosemObjectAttributeId(2)))
    SPODES_VERSION = ut.CosemAttributeDescriptor((ClassID.DATA, ut.CosemObjectInstanceId("0.0.96.1.6.255"), ut.CosemObjectAttributeId(2)))


__range10_and_255: tuple[int, ...] = 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 255
__range63: tuple[int, ...] = tuple(range(0, 64))
__range120_and_124_127: tuple[int, ...] = tuple(chain(range(0, 121), range(124, 128)))
__range100_and_255: tuple[int, ...] = tuple(chain(range(0, 100), (255,)))
__range100_and_101_125_and_255: tuple[int, ...] = tuple(chain(__range100_and_255, range(101, 126)))
__c1: tuple[int, ...] = tuple(chain(range(1, 10), (13, 14, 33, 34, 53, 54, 73, 74, 82), range(16, 31), range(36, 51), range(56, 70), range(76, 81), range(84, 90)))
"""DLMS UA 1000-1 Ed 14. Table 45 c1"""
__table44: tuple[int, ...] = (11, 12, 15, 31, 32, 35, 51, 52, 55, 71, 72, 75, 90, 91, 92)
"""DLMS UA 1000-1 Ed 14. Table 44 for active power"""
__c2: tuple[int, ...] = tuple(chain(__table44, range(100, 108)))
"""DLMS UA 1000-1 Ed 14. Table 45 c2"""


def obis2mediaId(obis: Obis) -> media_id.MediaId:
    return media_id.MediaId.from_int(attr2a(obis))


def get_class_id(obj: InterfaceClass) -> ut.CosemClassId:
    return obj.CLASS_ID


def get_map_by_obj(objects: list[InterfaceClass] | tuple[InterfaceClass, ...], key: Callable[[InterfaceClass], None]) -> dict[media_id.MediaId, list[InterfaceClass]]:
    ret = {}
    for obj in objects:
        if ret.get(new_key := key(obj)):
            ret[new_key].append(obj)
        else:
            ret[new_key] = [obj]
    return ret


def get_object_tree(objects: list[IC] | tuple[IC],
                    mode: ObjectTreeMode) -> dict[media_id.MediaId | ClassID, list[IC]]:
    """mode: m-media_id, g-relation_group, c-class_id"""
    mode = list(mode)
    ret = objects
    while mode:
        match mode.pop():
            case "m":
                key = lambda obj: obis2mediaId(obj.obis)
            case "g":
                key = lambda obj: obis2relationGroup(obj.obis)
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


def get_sorted(objects: list[IC],
               mode: SortMode) -> list[IC]:
    """mode: l-logical_name, n-name, c-class_id
    """
    mode: list[str] = list(mode)
    while mode:
        match mode.pop():
            case "l":
                key = None
            case "n":
                key = lambda obj: get_name(obj.obis)
            case "c":
                key = lambda obj: obj.CLASS_ID
            case _:
                raise KeyError(F"got unknown {mode=} for get_map")
        objects = sorted(objects, key=key)
    return objects

@dataclass
class Channel:
    """for object filter approve"""
    n: int

    def __post_init__(self) -> None:
        if not self.is_channel(self.n):
            raise ValueError(F"got value={self.n}, expected (0..64)")

    @staticmethod
    def is_channel(b: int) -> bool:
        return True if 0 <= b <= 64 else False

    def is_approve(self, b: int) -> bool:
        if self.is_channel(b):
            return True if b == self.n else False
        else:
            return True


RelationGroup: TypeAlias = media_id.Abstract | media_id.Electricity | media_id.Hca | media_id.Gas | media_id.Thermal | media_id.Water | media_id.Other
RelationGroups: tuple[media_id.MediaId, ...] = (media_id.ABSTRACT, media_id.ELECTRICITY, media_id.HCA, media_id.GAS, media_id.THERMAL, media_id.WATER)


@lru_cache(maxsize=1000)
def obis2relationGroup(obis: Obis) -> RelationGroup:
    a, b, c, d, e, f = obis
    if a == media_id.ABSTRACT:
        if c == 0:
            if d == 1:
                return media_id.BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES
            if d in (2, 9):
                return media_id.OTHER_ABSTRACT_GENERAL_PURPOSE_OBIS_CODES
        if c == 1:
            if d in (0, 1, 2, 3, 4, 5, 6):
                return media_id.CLOCK_OBJECTS
        if c == 2:
            if d in (0, 1, 2):
                return media_id.MODEM_CONFIGURATION_AND_RELATED_OBJECTS
        if c == 10 and d == 0 and e in (0, 1, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 125):
            return media_id.SCRIPT_TABLE_OBJECTS
        if c == 11 and d == 0:
            return media_id.SPECIAL_DAYS_TABLE_OBJECTS
        if c == 12 and d == 0:
            return media_id.SCHEDULE_OBJECTS
        if c == 13 and d == 0:
            return media_id.ACTIVITY_CALENDAR_OBJECTS
        if c == 14 and d == 0:
            return media_id.REGISTER_ACTIVATION_OBJECTS
        if c == 15 and d == 0 and e in (0, 1, 2, 3, 4, 5, 6, 7):
            return media_id.SINGLE_ACTION_SCHEDULE_OBJECTS
        if c == 16:
            if d == 0 or (d == 1 and e in range(0, 10)):
                return media_id.REGISTER_OBJECTS_MONITOR
            if d == 2:
                return media_id.PARAMETER_MONITOR_OBJECTS
        if c == 17 and d == 0:
            return media_id.LIMITER_OBJECTS
        if c == 18 and d == 0:
            return media_id.ARRAY_MANAGER_OBJECT
        if c == 19:
            if (d in range(0, 10) and e == 0) or d in range(10, 50) or d in (range(50, 60) and e in (1, 2)):
                return media_id.PAYMENT_METERING_RELATED_OBJECTS
        if c == 20 and d == 0 and e in (0, 1):
            return media_id.IEC_LOCAL_PORT_SETUP_OBJECTS
        if c == 21 and d == 0:
            return media_id.STANDARD_READOUT_PROFILE_OBJECTS
        if c == 22 and d == 0 and e == 0:
            return media_id.IEC_HDLC_SETUP_OBJECTS
        if c == 23:
            if (d in 0, 1, 2 and e == 0) or d == 3:
                return media_id.IEC_TWISTED_PAIR_1_SETUP_OBJECTS
        if c == 24:
            if (d in (0, 1, 4, 5, 6) and e == 0) or (d in (2, 8, 9)):
                return media_id.OBJECTS_RELATED_TO_DATA_EXCHANGE_OVER_M_BUS
        if c == 31 and d == 0 and e == 0:
            return media_id.OBJECTS_RELATED_TO_DATA_EXCHANGE_OVER_M_BUS
        if c == 25:
            if d in (0, 1, 2, 3, 4, 5, 6, 7, 10, 11, 12, 13, 14, 15) and e == 0:
                return media_id.OBJECTS_TO_SET_UP_DATA_EXCHANGE_OVER_THE_INTERNET
            if d == 9 and e == 0:
                return media_id.OBJECTS_TO_SET_UP_PUSH_SETUP
        if c == 26 and d in (0, 1, 2, 3, 5, 6) and e == 0:
            return media_id.OBJECTS_FOR_SETTING_UP_DATA_EXCHANGE_USING_S_FSK_PLC
        if c == 27 and d in (0, 1, 2) and e == 0:
            return media_id.OBJECTS_FOR_SETTING_UP_THE_ISO_IEC_8802_2_LLC_LAYER
        if c == 28 and d in (0, 1, 2, 3, 4, 5, 6, 7) and e == 0:
            return media_id.OBJECTS_FOR_DATA_EXCHANGE_USING_NARROWBAND_OFDM_PLC_FOR_PRIME_NETWORKS
        if c == 29 and d in (0, 1, 2) and e == 0:
            return media_id.OBJECTS_FOR_DATA_EXCHANGE_USING_NARROW_BAND_OFDM_PLC_FOR_G3_PLC_NETWORKS
        if c == 30 and d in (0, 1, 2, 3, 4):
            return media_id.ZIGBEE_SETUP_OBJECTS
        if c == 32 and d in (0, 1, 2, 3) and e == 0:
            return media_id.OBJECTS_FOR_SETTING_UP_AND_MANAGING_DATA_EXCHANGE_USING_ISO_IEC_14908_PLC_NETWORKS
        if c == 33 and d in (0, 1, 2, 3) and e == 0:
            return media_id.OBJECTS_FOR_DATA_EXCHANGE_USING_HS_PLC_ISO_IEC_12139_1_ISO_EC_12139_1_NETWORKS
        if c == 34 and d in (0, 1, 2, 3) and e == 0:
            return media_id.OBJECTS_FOR_DATA_EXCHANGE_USING_WI_SUN_NETWORKS
        if c == 40 and b == 0 and d == 0:
            return media_id.ASSOCIATION_OBJECTS
        if c == 41 and b == 0 and d == 0 and e == 0:
            return media_id.SAP_ASSIGNMENT_OBJECT
        if c == 42 and b == 0 and d == 0 and e == 0:
            return media_id.COSEM_LOGICAL_DEVICE_NAME_OBJECT
        if c == 43:
            if (b == 0 and d == 0) or d in (1, 2):
                return media_id.INFORMATION_SECURITY_RELATED_OBJECTS
        if c == 44:
            if b == 0:
                if d == 0:
                    return media_id.IMAGE_TRANSFER_OBJECTS
                if d == 1:
                    return media_id.FUNCTION_CONTROL_OBJECTS
                if d == 2:
                    return media_id.COMMUNICATION_PORT_PROTECTION_OBJECTS
        if c == 65 and d in __range63:
            return media_id.UTILITY_TABLE_OBJECTS
        if c == 66 and d == 0:
            return media_id.COMPACT_DATA_OBJECTS
        if c == 96:
            if d == 1:
                if e in __range10_and_255:
                    return media_id.DEVICE_ID_OBJECTS
                if e == 10:
                    return media_id.METERING_POINT_ID_OBJECTS
            if d == 2:
                return media_id.PARAMETER_CHANGES_AND_CALIBRATION_OBJECTS
            if d == 3:
                if e in (0, 1, 2, 3, 4):
                    return media_id.I_O_CONTROL_SIGNAL_OBJECTS
                if e == 10:
                    return media_id.DISCONNECT_CONTROL_OBJECTS
                if e in range(20, 30):
                    return media_id.ARBITRATOR_OBJECTS
            if d == 4 and e in (0, 1, 2, 3, 4):
                return media_id.STATUS_OF_INTERNAL_CONTROL_SIGNALS_OBJECTS
            if d == 5 and e in (0, 1, 2, 3, 4):
                return media_id.INTERNAL_OPERATING_STATUS_OBJECTS
            if d == 6 and e in (0, 1, 2, 3, 4, 5, 6):
                return media_id.BATTERY_ENTRIES_OBJECTS
            if d == 7 and e in range(0, 22):
                return media_id.POWER_FAILURE_MONITORING_OBJECTS
            if d == 8 and e in __range63:
                return media_id.OPERATING_TIME_OBJECTS
            if d == 9 and e in (0, 1, 2):
                return media_id.ENVIRONMENT_RELATED_PARAMETERS_OBJECTS
            if d == 10 and e in range(1, 11):
                return media_id.STATUS_REGISTER_OBJECTS
            if d == 11 and e in range(0, 100):
                return media_id.EVENT_CODE_OBJECTS
            if d == 12 and e in range(0, 7):
                return media_id.COMMUNICATION_PORT_LOG_PARAMETER_OBJECTS
            if d == 13 and e in (0, 1):
                return media_id.CONSUMER_MESSAGE_OBJECTS
            if d == 14 and e in range(0, 16):
                return media_id.CURRENTLY_ACTIVE_TARIFF_OBJECTS
            if d == 15 and e in range(0, 100):
                return media_id.EVENT_COUNTER_OBJECTS
            if d == 16 and e in range(0, 10):
                return media_id.PROFILE_ENTRY_DIGITAL_SIGNATURE_OBJECTS
            if d == 17 and e in range(0, 128):
                return media_id.PROFILE_ENTRY_COUNTER_OBJECTS
            if d == 20:
                return media_id.METER_TAMPER_EVENT_RELATED_OBJECTS
            if d in range(50, 100):
                return media_id.ABSTRACT_MANUFACTURER_SPECIFIC
        if c == 97:
            if d == 97 and e in __range10_and_255:
                return media_id.ERROR_REGISTER_OBJECTS
            if d == 98 and (e in chain(range(0, 30), (255,))):
                return media_id.ALARM_REGISTER_FILTER_DESCRIPTOR_OBJECTS
        if c == 98:
            return media_id.GENERAL_LIST_OBJECTS
        if c == 99:
            if d in (1, 2, 12, 13, 14, 15, 16, 17, 18) or (d == 3 and e == 0):
                return media_id.ABSTRACT_DATA_PROFILE_OBJECTS
            if d == 98:
                return media_id.EVENT_LOG_OBJECTS
        if c == 127 and d == 0:
            return media_id.INACTIVE_OBJECTS
        else:
            return media_id.ABSTRACT
    if a == media_id.ELECTRICITY:
        if c == 0:
            if d == 0 and e in __range10_and_255:
                return media_id.ID_NUMBERS_ELECTRICITY
            if d == 1:
                return media_id.BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES_EL
            if d in (2, 3, 4, 6, 7, 8, 9, 10):
                return media_id.OTHER_ELECTRICITY_RELATED_GENERAL_PURPOSE_OBJECTS
            if d == 11 and e in (1, 2, 3, 4, 5, 6, 7):
                return media_id.MEASUREMENT_ALGORITHM
        if c in (1, 21, 41, 61):
            return media_id.ACTIVE_POWER_PLUS
        if c in (2, 22, 42, 62):
            return media_id.ACTIVE_POWER_MINUS
        if c in (3, 23, 43, 63):
            return media_id.REACTIVE_POWER_PLUS
        if c in (4, 24, 44, 64):
            return media_id.REACTIVE_POWER_MINUS
        if c in (5, 25, 45, 65):
            return media_id.REACTIVE_POWER_QI
        if c in (6, 26, 46, 66):
            return media_id.REACTIVE_POWER_QII
        if c in (7, 27, 47, 67):
            return media_id.REACTIVE_POWER_QIII
        if c in (8, 28, 48, 68):
            return media_id.REACTIVE_POWER_QIV
        if c in (9, 29, 49, 69):
            return media_id.APPARENT_POWER_PLUS
        if c in (10, 30, 50, 70):
            return media_id.APPARENT_POWER_MINUS
        if c in (11, 31, 51, 71):
            return media_id.CURRENT
        if c in (12, 32, 52, 72):
            return media_id.VOLTAGE
        if c in (13, 33, 53, 73):
            return media_id.POWER_FACTOR
        if c in (14, 34, 54, 74):
            return media_id.SUPPLY_FREQUENCY
        if c in (15, 35, 55, 75):
            return media_id.ACTIVE_POWER_SUM
        if c in (16, 36, 56, 76):
            return media_id.ACTIVE_POWER_DIFF
        if c in (17, 37, 57, 77):
            return media_id.ACTIVE_POWER_QI
        if c in (18, 38, 58, 78):
            return media_id.ACTIVE_POWER_QII
        if c in (19, 39, 59, 79):
            return media_id.ACTIVE_POWER_QIII
        if c in (20, 40, 60, 80):
            return media_id.ACTIVE_POWER_QIV
        if c == 96:
            if d == 1 and e in __range10_and_255:
                return media_id.ELECTRICITY_METERING_POINT_ID_OBJECTS
            if d == 5 and e in (0, 1, 2, 3, 4, 5):
                return media_id.ELECTRICITY_RELATED_STATUS_OBJECTS
            if d == 10 and e in (0, 1, 2, 3):
                return media_id.ELECTRICITY_RELATED_STATUS_OBJECTS
        if c == 98:
            return media_id.LIST_OBJECTS_ELECTRICITY
        if d in range(31, 46) and f in __range100_and_255:
            if c in __c1 and e in __range63:
                return media_id.THRESHOLD_VALUES
            if c in __table44 and e in __range120_and_124_127:
                return media_id.THRESHOLD_VALUES
        if f in __range100_and_255:
            if d in (31, 35, 39, 4, 5, 14, 15, 24, 25):
                if c in __c1 and e in __range63:
                    return media_id.REGISTER_MONITOR_OBJECTS
                if c in __c2 and e in __range120_and_124_127:
                    return media_id.REGISTER_MONITOR_OBJECTS
        else:
            return media_id.ELECTRICITY
    if a == media_id.HCA:
        if c == 0:
            if d == 0 and e in __range10_and_255:
                return media_id.ID_NUMBERS_HCA
            if d == 1 and e in (1, 2, 10, 11):
                return media_id.BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES_HCA
            if d == 2 and e in (0, 1, 2, 3):
                return media_id.GENERAL_PURPOSE_OBJECTS_HCA
            if d == 4 and e in (0, 1, 2, 3, 4, 5, 6):
                return media_id.GENERAL_PURPOSE_OBJECTS_HCA
            if d == 5 and e in (10, 11):
                return media_id.GENERAL_PURPOSE_OBJECTS_HCA
            if d == 8 and e in (0, 4, 6):
                return media_id.GENERAL_PURPOSE_OBJECTS_HCA
            if d == 9 and e in (1, 2, 3):
                return media_id.GENERAL_PURPOSE_OBJECTS_HCA
        if c in (1, 2) and e == 0:
            if d in (0, 6) and f == 255:
                return media_id.MEASURED_VALUES_HCA_CONSUMPTION
            if d in (1, 2, 3, 4, 5) and f in __range100_and_101_125_and_255:
                return media_id.MEASURED_VALUES_HCA_CONSUMPTION
        if c in range(3, 8) and d in (0, 4, 5, 6) and e == 255 and f == 255:
            return media_id.MEASURED_VALUES_HCA_TEMPERATURE
        if c == 97 and d == 97:
            return media_id.ERROR_REGISTER_OBJECTS_HCA
        if c == 98:
            return media_id.LIST_OBJECTS_HCA
        if c == 99 and d == 1:
            return media_id.DATA_PROFILE_OBJECTS_HCA
        else:
            return media_id.HCA
    if a == media_id.THERMAL:
        if c == 0:
            if d == 0 and e in __range10_and_255:
                return media_id.ID_NUMBERS_THERMAL
            if d == 1 and e in (1, 2, 10, 11):
                return media_id.BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES_THERMAL
            if d == 2 and e in chain(range(0, 5), range(10, 14)):
                return media_id.GENERAL_PURPOSE_OBJECTS_THERMAL
            if d == 4 and e in (1, 2, 3):
                return media_id.GENERAL_PURPOSE_OBJECTS_THERMAL
            if d == 5 and e in chain(range(1, 10), range(21, 25)):
                return media_id.GENERAL_PURPOSE_OBJECTS_THERMAL
            if d == 8 and e in chain(range(0, 8), range(11, 15), range(21, 26), range(31, 35)):
                return media_id.GENERAL_PURPOSE_OBJECTS_THERMAL
            if d == 9 and e in (1, 2, 3):
                return media_id.GENERAL_PURPOSE_OBJECTS_THERMAL
        if c in range(1, 8):
            if e in range(10):
                if d in (0, 1, 2, 3, 7) and f == 255:
                    return media_id.MEASURED_VALUES_THERMAL_CONSUMPTION
                if d in (3, 8, 9) and f in __range100_and_101_125_and_255:
                    return media_id.MEASURED_VALUES_THERMAL_CONSUMPTION
                if d in (1, 2, 4, 5, 12, 13, 14, 15) and f in chain(range(100), range(100, 126)):
                    return media_id.MEASURED_VALUES_THERMAL_CONSUMPTION
            if d == 6 and e == 255 and f == 255:
                return media_id.MEASURED_VALUES_THERMAL_CONSUMPTION
        if e in range(10):
            if f in __range100_and_101_125_and_255:
                if c in range(1, 8) and d in (5, 15):
                    return media_id.MEASURED_VALUES_THERMAL_ENERGY
                if c in (8, 9) and d in (1, 4, 5, 12, 13, 14, 15):
                    return media_id.MEASURED_VALUES_THERMAL_ENERGY
            if c in range(10, 14):
                if d == 0 and f == 255:
                    return media_id.MEASURED_VALUES_THERMAL_ENERGY
                if d in (4, 5, 14, 15) and f in chain(range(100), range(101, 126)):
                    return media_id.MEASURED_VALUES_THERMAL_ENERGY
                if d in (6, 7, 10, 11) and f == 255:
                    return media_id.MEASURED_VALUES_THERMAL_ENERGY
            if c in range(1, 14) and (d in range(20, 26)) and f == 255:
                return media_id.MEASURED_VALUES_THERMAL_ENERGY
        if c == 97 and d == 97 and e in (0, 1, 2):
            return media_id.ERROR_REGISTER_OBJECTS_THERMAL
        if c == 98:
            return media_id.LIST_OBJECTS_THERMAL
        if c == 99 and f == 255:
            if d in (1, 2) and e in (1, 2, 3):
                return media_id.DATA_PROFILE_OBJECTS_THERMAL
            if d == 3 and e == 1:
                return media_id.DATA_PROFILE_OBJECTS_THERMAL
            if d == 99:
                return media_id.DATA_PROFILE_OBJECTS_THERMAL
        else:
            return media_id.THERMAL
    if media_id.GAS == a:
        if c == 0:
            if d == 0 and e in __range10_and_255:
                return media_id.ID_NUMBERS_GAS
            if d == 1:
                return media_id.BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES_GAS
            if d in (2, 3, 4, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15):
                return media_id.GENERAL_PURPOSE_OBJECTS_GAS
        if c == 96 and d == 5 and (e in range(10)):
            return media_id.INTERNAL_OPERATING_STATUS_OBJECTS_GAS
        if c in chain(range(1, 9), range(11, 17), range(21, 27), range(31, 36), range(61, 66)) and e in __range63:
            if d in (24, 25, 26, 42, 43, 44, 63, 64, 65, 81, 82, 83) and f in chain(range(100), range(101, 127)):
                return media_id.MEASURED_VALUES_GAS_INDEXES_AND_INDEX_DIFFERENCES
            if d in chain(range(6, 24), range(27, 33), range(45, 51), range(66, 72), range(84, 90)) and f == 255:
                return media_id.MEASURED_VALUES_GAS_INDEXES_AND_INDEX_DIFFERENCES
            if d in chain(range(33, 42), range(52, 63), range(72, 81), range(90, 99)) and f in chain(__range100_and_101_125_and_255, (126,)):
                return media_id.MEASURED_VALUES_GAS_INDEXES_AND_INDEX_DIFFERENCES
        if c == 42 and e == 0:
            if d in chain((0, 1, 2, 13), range(15, 19), range(19, 31), range(35, 51), range(55, 71)) and f == 255:
                return media_id.MEASURED_VALUES_GAS_FLOW_RATE
            if d in chain(range(31, 35), range(51, 55)) and f in chain(__range100_and_101_125_and_255, (126,)):
                return media_id.MEASURED_VALUES_GAS_FLOW_RATE
        if c in chain((41, 42), range(44, 50)) and d in (0, 2, 3, 10, 11, 13, range(15, 92)) and e == 0 and f == 255:
            return media_id.MEASURED_VALUES_GAS_PROCESS_VALUES
        if c in range(51, 56):
            if d in (0, 2, 3, 10, 11) and e in chain((0, 1), range(11, 29)) and f == 255:
                return media_id.CONVERSION_RELATED_FACTORS_AND_COEFFICIENTS_GAS
            if d == 12 and e in range(20) and f == 255:
                return media_id.CALCULATION_METHODS_GAS
        if c == 70 and f == 255:
            if d in (8, 9) and e == 0:
                return media_id.NATURAL_GAS_ANALYSIS
            if d in chain(range(10, 21), range(60, 85)) and e in chain((0, 1), range(11, 29)):
                return media_id.NATURAL_GAS_ANALYSIS
        if c == 98:
            return media_id.LIST_OBJECTS_GAS
        else:
            return media_id.GAS
    if a == media_id.WATER:
        if c == 0:
            if d == 0 and e in __range10_and_255:
                return media_id.ID_NUMBERS_WATER
            if d == 1 and e in (1, 2, 10, 11, 12):
                return media_id.BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES_WATER
            if d == 2 and e in (0, 3):
                return media_id.GENERAL_PURPOSE_OBJECTS_WATER
            if d in (5, 7) and e == 1:
                return media_id.GENERAL_PURPOSE_OBJECTS_WATER
            if d == 8 and e in (1, 6):
                return media_id.GENERAL_PURPOSE_OBJECTS_WATER
            if d == 9 and e in (1, 2, 3):
                return media_id.GENERAL_PURPOSE_OBJECTS_WATER
        if c == 1 and e in range(0, 13):
            if d in (0, 1, 2, 3, 6) and f == 255:
                return media_id.MEASURED_VALUES_WATER_CONSUMPTION
            if d in range(1, 6) and f in chain(range(100), range(101, 126)):
                return media_id.MEASURED_VALUES_WATER_CONSUMPTION
        if c in (2, 3) and e in range(0, 13):
            if d in (0, 1, 2, 3, 6) and f == 255:
                return media_id.MEASURED_VALUES_WATER_MONITORING_VALUES
            if d in range(1, 6) and f in chain(range(100), range(101, 126)):
                return media_id.MEASURED_VALUES_WATER_MONITORING_VALUES
        if c == 97 and d == 97:
            return media_id.ERROR_REGISTER_OBJECTS_WATER
        if c == 98:
            return media_id.LIST_OBJECTS_WATER
        if c == 99 and d == 1:
            return media_id.DATA_PROFILE_OBJECTS_WATER
        else:
            return media_id.WATER
    return media_id.OTHER_MEDIA


DLMSObjectContainer: TypeAlias = Collection | list[InterfaceClass] | filter


@dataclass
class Template:
    name:        str
    collections: list[Collection]
    used:        UsedAttributes
    description: str = ""
    verified:    bool = False

    def get_not_contains(self, cols: Iterable[Collection]) -> list[Collection]:
        """return of collections not contains in template"""
        ret = []
        for i, col in enumerate(cols):
            if col not in self.collections:
                ret.append(col)
        return ret

    def get_not_valid(self, col: Collection) -> list[Exception]:
        """with update col"""
        attr: cdt.CommonDataType
        ret: list[Exception] = []
        use_col = self.collections[0]
        """temporary used first collection"""
        for ln, indexes in self.used.items():
            try:
                obj = use_col.get_object(ln)
                obj_col = col.get_object(ln)
            except exc.NoObject as e:
                ret.append(e)
                print(F"<add_collection> skip obj{self}: {e}")
                continue
            for i in indexes:
                if (attr := obj.get_attr(i)) is not None:
                    try:
                        attr.validate()
                    except ValueError as e:
                        ret.append(ValueError(F"can't decode value {attr} for {ln}:{i}"))
                else:
                    ret.append(exc.NoObject(F"has't attribute {i} for {ln}"))
        return ret

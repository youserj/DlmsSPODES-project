""" The OBIS identification system serves as a basis for the COSEM logical names. The system of naming COSEM objects is defined in the basic
principles (see Clause 4 EN 62056-62:2007), the identification of real data items is specified in IEC 62056-61. The following clauses define the
usage of those definitions in the COSEM environment. All codes, which are not explicitly listed, but outside the manufacturer specific range are
reserved for future use."""
from __future__ import annotations
import datetime
import dataclasses
from itertools import count, chain
from collections import deque
from functools import reduce, cached_property, lru_cache
from typing import TypeAlias, Iterator, Type
import logging
from ..version import AppVersion
from ..types import common_data_types as cdt, cosem_service_types as cst, useful_types as ut
from . import cosem_interface_class as ic
from . import events as e_
from .activity_calendar import ActivityCalendar
from .arbitrator import Arbitrator
from .association_ln.ver0 import AssociationLN as AssociationLNVer0
from .association_ln.ver1 import AssociationLN as AssociationLNVer1
from .association_ln.ver2 import AssociationLN as AssociationLNVer2
from .push_setup.ver2 import PushSetup as PushSetupVer2
from .client_setup import ClientSetup
from .clock import Clock
from .data import Data
from .disconnect_control import DisconnectControl
from .extended_register import ExtendedRegister
from .gprs_modem_setup import GPRSModemSetup
from .gsm_diagnostic import GSMDiagnostic
from .iec_hdlc_setup import IECHDLCSetup
from .image_transfer import ImageTransfer
from .ipv4_setup import IPv4Setup
from .modem_configuration.ver0 import PSTNModemConfiguration
from .modem_configuration.ver1 import ModemConfigurationVer1
from .limiter import Limiter
from .profile_generic import ProfileGeneric
from .register import Register
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
from ..relation_to_OBIS import get_name
from ..cosem_interface_classes import implementations as impl, class_id as c_id
from .. import settings
from ..enums import TagsName
from . import obis as o
from .. import pdu_enums as pdu

match settings.get_current_language():
    case settings.Language.ENGLISH:        from ..Values.EN import actors
    case settings.Language.RUSSIAN:        from ..Values.RU import actors

AssociationLN: TypeAlias = AssociationLNVer0 | AssociationLNVer1 | AssociationLNVer2
AssociationLN_c: tuple[Type[AssociationLN], ...] = (AssociationLNVer0, AssociationLNVer1, AssociationLNVer2)
"""container with Association types. Use in get_instance"""
ModemConfiguration: TypeAlias = PSTNModemConfiguration | ModemConfigurationVer1
ModemConfiguration_c: tuple[Type[ModemConfiguration], ...] = (PSTNModemConfiguration, ModemConfigurationVer1)
"""container with ModemConfiguration types. Use in get_instance"""
SecuritySetup: TypeAlias = SecuritySetupVer0 | SecuritySetupVer1
SecuritySetup_c: tuple[Type[SecuritySetup], ...] = (SecuritySetupVer0, SecuritySetupVer1)
"""container with SecuritySetup types. Use in get_instance"""
PushSetup: TypeAlias = PushSetupVer2

InterfaceClass: TypeAlias = Data | Register | ProfileGeneric | Clock | ScriptTable | Schedule | SpecialDaysTable | ActivityCalendar | SingleActionSchedule | AssociationLN | \
                            IECHDLCSetup | ExtendedRegister | DisconnectControl | Limiter | ModemConfiguration | PSTNModemConfiguration | ImageTransfer | GPRSModemSetup | \
                            GSMDiagnostic | ClientSetup | SecuritySetup | TCPUDPSetup | IPv4Setup | Arbitrator | RegisterMonitor | PushSetup


def get_type_from_class(c_id: int, ver: int) -> Type[InterfaceClass]:
    match c_id:
        case 1:  return Data
        case 3:  return Register
        case 4:  return ExtendedRegister
        case 7:  return ProfileGeneric
        case 8:  return Clock
        case 9:  return ScriptTable
        case 10: return Schedule
        case 11: return SpecialDaysTable
        case 15: return AssociationLN_c[ver]
        case 18: return ImageTransfer
        case 20: return ActivityCalendar
        case 21: return RegisterMonitor
        case 22: return SingleActionSchedule
        case 23: return IECHDLCSetup
        case 27: return ModemConfiguration_c[ver]
        case 41: return TCPUDPSetup
        case 42: return IPv4Setup
        case 45: return GPRSModemSetup
        case 47: return GSMDiagnostic
        case 64: return SecuritySetup_c[ver]
        case 68: return Arbitrator
        case 70: return DisconnectControl
        case 71: return Limiter
        case 32767: return ClientSetup
        case _: raise ValueError(F"unknown DLMS class with ID {c_id}")


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

_NOT_PROCESSING_OF_MEASUREMENT_VALUES = (0, 93, 94, 96, 97, 98, 99)  # BlueBook DLMS UA 1000-1 Ed.14 7.5.2.1 Table 66
_RU_CHANGE_LIMIT_LEVEL = 134

logger = logging.getLogger(__name__)
logger.level = logging.INFO


@dataclasses.dataclass(frozen=True)
class ObjectRelation:
    IC: int | tuple[int, ...] | ic.COSEMInterfaceClasses
    Additional: bytes | dict | bool = None


class Collection:
    __container: deque[InterfaceClass]
    __const_objs: list[ic.COSEMInterfaceClasses]

    def __init__(self):
        self.__container = deque()
        """ all DLMS objects container with obis key """

        self.__const_objs = list()
        """ container for major(constant) DLMS objects LN. They don't deletable """

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

    def from_xml(self, filename: str, use: dict[cst.LogicalName, set[int]] = None):
        """ append objects from xml file """
        tree = ET.parse(filename)
        objects = tree.getroot()
        if use is None and objects.tag != TagsName.DEVICE_ROOT.value:
            raise ValueError(F"ERROR: Root tag got {objects.tag}, expected {TagsName.DEVICE_ROOT.value}")
        root_version: AppVersion = AppVersion.from_str(objects.attrib.get('version', '1.0.0'))
        logger.info(F'Версия: {root_version}, file: {filename.split("/")[-1]}')
        match root_version:
            case AppVersion(1):
                attempts: iter = count(3, -1)
                """ attempts counter """
                while len(objects) != 0 and next(attempts):
                    logger.info(F'{attempts=}')
                    for obj in objects.findall('object'):
                        new_object: ic.COSEMInterfaceClasses | None = None
                        indexes: list[int] = list()
                        """ got attributes indexes for current object """
                        for attr in obj.findall('attribute'):
                            index: ET.Element = attr.find('index')
                            if index.text.isdigit():
                                indexes.append(int(index.text))
                            else:
                                raise ValueError(F'ERROR: for {new_object.logical_name if new_object is not None else ""} got index {index.text} and it is not digital')
                            if isinstance(index, ET.Element):
                                if indexes[-1] == 1:
                                    try:
                                        ln_encoding: str = attr.findtext('encoding')
                                        if ln_encoding is None:
                                            raise ValueError('logical_name not found')
                                        class_id: str = obj.findtext('class_id')
                                        if class_id is None:
                                            raise ValueError('class_id not found')
                                        version: str = obj.findtext('version')
                                        if version is None:
                                            raise ValueError('version not found')
                                        new_object = self.add_if_missing(class_id=ut.CosemClassId(class_id),
                                                                         version=cdt.Unsigned(version),
                                                                         logical_name=cst.LogicalName(bytes.fromhex(ln_encoding)))
                                        if use is not None:
                                            use[new_object.logical_name] = set()
                                    except TypeError as e:
                                        logger.error(F'Object {obj.attrib["name"]} not created : {e}')
                                    except ValueError as e:
                                        logger.error(F'Object {obj.attrib["name"]} not created : {e}')
                                else:
                                    if new_object is None:
                                        logger.info(F'ERROR. Object "{obj.attrib["name"]}" not created : Attribute with index <1> not found')
                                        break
                                    else:
                                        try:
                                            match attr.find('encoding'), attr.find('tag'):
                                                case ET.Element() as encoding, _:
                                                    record_time: ET.Element = attr.find('record_time')
                                                    if record_time is not None:
                                                        new_object.set_record_time(indexes[-1], bytes.fromhex(record_time.text))
                                                    if new_object.logical_name == cst.LogicalName('1.0.94.7.2.255') and indexes[-1] == 2:
                                                        print('stop')
                                                    new_object.set_attr(indexes[-1], bytes.fromhex(encoding.text))
                                                    if use is not None:
                                                        use[new_object.logical_name].add(indexes[-1])
                                                case None, ET.Element() as tag:
                                                    choice = new_object.get_attr_element(indexes[-1])
                                                    if new_object.get_attr(indexes[-1]) is None and isinstance(choice, ut.CHOICE):
                                                        new_object.set_attr(indexes[-1], int(tag.text))
                                                case _ as error:
                                                    raise ValueError(F'encoding and tag not found: {error}')
                                            obj.remove(attr)
                                        except exc.NoObject as e:
                                            logger.error(F"Can't fill {new_object} attr: {indexes[-1]}. Skip. {e}.")
                                            break
                                        except exc.ITEApplication as e:
                                            logger.error(F"Can't fill {new_object} attr: {indexes[-1]}. {e}")
                                        except IndexError:
                                            logger.error(F'Object "{new_object}" not has attribute with index {index.text}')
                                        except TypeError as e:
                                            logger.error(F'Object {new_object} attr:{index.text} do not write, encoding wrong : {e}')
                                        except ValueError as e:
                                            logger.error(F'Object {new_object} attr:{index.text} do not fill: {e}')
                                        except AttributeError as e:
                                            logger.error(F'Object {new_object} attr:{index.text} do not fill: {e}')
                        if len(obj.findall('attribute')) == 1:  # only logical name
                            objects.remove(obj)
                    logger.info(F'Not parsed DLMS objects: {len(objects)}')
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
                                new_object = self.add(class_id=ut.CosemClassId(class_id),
                                                      version=None if version is None else cdt.Unsigned(version),
                                                      logical_name=cst.LogicalName(ln))
                                if use is not None:
                                    use[new_object.logical_name] = set()
                            else:
                                new_object = self.__get_object(logical_name.contents)
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

    def add_major(self, obj: InterfaceClass):
        self.__const_objs.append(obj)

    def get_instance(self, class_id: ut.CosemClassId,
                     version: cdt.Unsigned | None,
                     ln: cst.LogicalName) -> InterfaceClass:
        """ TODO: naming"""
        if version is None:
            version = self.set_version(class_id, version)
        match int(class_id), int(version), ln:
            case c_id.PROFILE_GENERIC,                                   1, cst.LogicalName(a, b, 99, 98, e):
                return ProfileGeneric(ln)
            case c_id.DATA,                                              0, cst.LogicalName(0 | 1, b, 0, 2, e):
                return Data(ln)
            case c_id.CLOCK,                                             0, cst.LogicalName(0, b, 1, 0, e):
                return Clock(ln)
            case c_id.MODEM_CONFIGURATION,                               v, cst.LogicalName(0, b, 2, 0, e) if v < len(ModemConfiguration_c):
                return ModemConfiguration_c[v](ln)
            case c_id.SCRIPT_TABLE,                                      0, cst.LogicalName(0, b, 10, 0, e) if e in (0, 1, 125) or 100 <= e <= 111:
                return ScriptTable(ln)
            case c_id.SPECIAL_DAYS_TABLE,                                0, cst.LogicalName(0, b, 11, 0, e):
                return SpecialDaysTable(ln)
            case c_id.SCHEDULE,                                          0, cst.LogicalName(0, b, 12, 0, e):
                return Schedule(ln)
            case c_id.ACTIVITY_CALENDAR,                                 0, cst.LogicalName(0, b, 13, 0, e):
                return ActivityCalendar(ln)
            case c_id.SINGLE_ACTION_SCHEDULE,                            0, cst.LogicalName(0, b, 15, 0, e) if 0 <= e <= 7:
                return SingleActionSchedule(ln)
            case c_id.REGISTER_MONITOR,                                  0, cst.LogicalName(0, b, 16, 0, e) | cst.LogicalName(0, b, 16, 1, e) if 0 <= e <= 9:
                return RegisterMonitor(ln)
            case c_id.LIMITER,                                           0, cst.LogicalName(0, b, 17, 0, e):
                return Limiter(ln)
            case c_id.PROFILE_GENERIC,                                   1, cst.LogicalName(0, b, 21, 0, e):
                return ProfileGeneric(ln)
            case c_id.IEC_HDLC_SETUP,                                    1, cst.LogicalName(0, b, 22, 0, 0):
                return IECHDLCSetup(ln)
            case c_id.TCP_UDP_SETUP,                                     0, cst.LogicalName(0, b, 25, 0, 0):
                return TCPUDPSetup(ln)
            case c_id.IPV4_SETUP,                                        0, cst.LogicalName(0, b, 25, 1, 0):
                return IPv4Setup(ln)
            case c_id.GPRS_MODEM_SETUP,                                  0, cst.LogicalName(0, b, 25, 4, 0):
                return GPRSModemSetup(ln)
            case c_id.GSM_DIAGNOSTIC,                                    0, cst.LogicalName(0, b, 25, 6, 0):
                return GSMDiagnostic(ln)
            case c_id.PUSH_SETUP,                                        2, cst.LogicalName(0, b, 25, 9, 0):
                return PushSetup(ln)
            case c_id.ASSOCIATION_LN_CLASS,                              v, cst.LogicalName(0, 0, 40, 0, e) if v < len(AssociationLN_c):
                return AssociationLN_c[v](ln)
            case c_id.DATA,                                              0, cst.LogicalName(0, 0, 42, 0, 0) | cst.LogicalName(0, _, 43, 1, _):
                return Data(ln)
            case c_id.SECURITY_SETUP,                                    v, cst.LogicalName(0, 0, 43, 0, e) if v < len(SecuritySetup_c):
                return SecuritySetup_c[v](ln)
            case c_id.IMAGE_TRANSFER,                                    0, cst.LogicalName(0, 0, 44, 0, e):
                return ImageTransfer(ln)
            case c_id.PROFILE_GENERIC,                                   1, cst.LogicalName(0, 0, 94, 7, 1):
                return ProfileGeneric(ln)
            case c_id.DATA,                                              0, cst.LogicalName(0, b, 96, 1, e) if 0 <= e <= 10:
                return Data(ln)
            # 6.2.44 Parameter changes and calibration objects
            case c_id.DATA,                                              0, cst.LogicalName(0, b, 96, 2, 0 | 4 | 10 | 13):
                return Data(ln)
            case c_id.DATA,                                              0, cst.LogicalName(0, b, 96, 2, 1 | 2 | 3 | 5 | 6 | 7 | 11 | 12):
                return impl.data.AnyDateTime(ln)
            case c_id.DATA,                                              0, cst.LogicalName(0, b, 96, 3, e) if 0 <= e <= 4:
                return Data(ln)
            case c_id.DISCONNECT_CONTROL,                                0, cst.LogicalName(0, b, 96, 3, 10):
                return DisconnectControl(ln)
            case c_id.ARBITRATOR,                                        0, cst.LogicalName(0, b, 96, 3, 20):
                ret = Arbitrator(ln)
                ret.actors = (actors.MANUAL,
                              actors.LOCAL_1,
                              actors.LOCAL_2,
                              actors.LOCAL_3,
                              actors.LOCAL_4,
                              actors.LOCAL_5,
                              actors.LOCAL_6,
                              actors.LOCAL_7)
                return ret
            case c_id.ARBITRATOR,                                        0, cst.LogicalName(0, b, 96, 3, e) if 21 <= e <= 29:
                return Arbitrator(ln)
            case c_id.DATA,                                              0, cst.LogicalName(0, b, 96, 4, e) if 0 <= e <= 4:
                return Data(ln)
            case c_id.DATA | c_id.PROFILE_GENERIC as i,                  v, cst.LogicalName(0, b, 96, 5, 0):  # TODO: add RegisterTable
                return get_type_from_class(i, v)(ln)
            case c_id.DATA,                                              0, cst.LogicalName(0, b, 96, 5, e) if 1 <= e <= 4:  # TODO: add StatusMaping
                return Data(ln)
            case c_id.DATA,                                              0, cst.LogicalName(0, 0, 96, 5, 132):
                return impl.data.Unsigned(ln)  # TODO: make according with СПОДЭС3 13.9. Контроль чередования фаз
            case c_id.DATA | c_id.REGISTER | c_id.EXT_REGISTER as i,     0, cst.LogicalName(0, b, 96, 8, e) if 0 <= e <= 63:
                return get_type_from_class(i, 0)(ln)
            case c_id.REGISTER | c_id.EXT_REGISTER as i,                 0, cst.LogicalName(0, b, 96, 9, e) if 0 <= e <= 2:
                return get_type_from_class(i, 0)(ln)
            case c_id.EXT_REGISTER,                                      0, cst.LogicalName(0, b, 96, 9, e) if 0 <= e <= 2:
                return ExtendedRegister(ln)
            case c_id.DATA | c_id.REGISTER | c_id.EXT_REGISTER as i,     0, cst.LogicalName(0, b, 96, 11, 0):
                ret = get_type_from_class(i, 0)(ln)
                ret.events = e_.voltage_events
                return ret
            case c_id.DATA | c_id.REGISTER | c_id.EXT_REGISTER as i,     0, cst.LogicalName(0, b, 96, 11, 1):
                ret = get_type_from_class(i, 0)(ln)
                ret.events = e_.current_events
                return ret
            case c_id.DATA | c_id.REGISTER | c_id.EXT_REGISTER as i,     0, cst.LogicalName(0, b, 96, 11, 2):
                ret = get_type_from_class(i, 0)(ln)
                ret.events = e_.commutation_events
                return ret
            case c_id.DATA | c_id.REGISTER | c_id.EXT_REGISTER as i,     0, cst.LogicalName(0, b, 96, 11, 3):
                ret = get_type_from_class(i, 0)(ln)
                ret.events = e_.programming_events
                return ret
            case c_id.DATA | c_id.REGISTER | c_id.EXT_REGISTER as i,     0, cst.LogicalName(0, b, 96, 11, 4):
                ret = get_type_from_class(i, 0)(ln)
                ret.events = e_.external_impact_events
                return ret
            case c_id.DATA | c_id.REGISTER | c_id.EXT_REGISTER as i,     0, cst.LogicalName(0, b, 96, 11, 5):
                ret = get_type_from_class(i, 0)(ln)
                ret.events = e_.communication_events
                return ret
            case c_id.DATA | c_id.REGISTER | c_id.EXT_REGISTER as i,     0, cst.LogicalName(0, b, 96, 11, 6):
                ret = get_type_from_class(i, 0)(ln)
                ret.events = e_.access_events
                return ret
            case c_id.DATA | c_id.REGISTER | c_id.EXT_REGISTER as i,     0, cst.LogicalName(0, b, 96, 11, 7):
                ret = get_type_from_class(i, 0)(ln)
                ret.events = e_.self_diagnostics_events
                return ret
            case c_id.DATA | c_id.REGISTER | c_id.EXT_REGISTER as i,     0, cst.LogicalName(0, b, 96, 11, 8):
                ret = get_type_from_class(i, 0)(ln)
                ret.events = e_.reactive_power_events
                return ret
            case c_id.DATA,                                              0, cst.LogicalName(0, b, 96, 12, 4):
                return impl.data.CommunicationPortParameter(ln)
            case c_id.DATA | c_id.REGISTER | c_id.EXT_REGISTER as i,     0, cst.LogicalName(0, b, 96, 12, e) if e in (0, 1, 2, 3, 5, 6):
                return get_type_from_class(i, 0)(ln)
            case c_id.DATA,                                              0, cst.LogicalName(0, b, 96, 12, 128):
                return Data(ln)
            # 6.2.57 Consumer message objects
            case c_id.DATA,                                              0, cst.LogicalName(0, 128, 96, 13, 1):
                return impl.data.ITEBitMap(ln)
            case c_id.DATA | c_id.REGISTER | c_id.EXT_REGISTER as i,     0, cst.LogicalName(0, b, 96, 13, 0 | 1):
                return get_type_from_class(i, 0)(ln)
            case c_id.DATA | c_id.REGISTER | c_id.EXT_REGISTER as i,     0, cst.LogicalName(0, b, 96, 15, e) if 0 <= e <= 99:
                return get_type_from_class(i, 0)(ln)
            case c_id.DATA | c_id.REGISTER | c_id.EXT_REGISTER as i,     0, cst.LogicalName(0, b, 96, 20, e):
                return get_type_from_class(i, 0)(ln)
            case c_id.DATA,                                              0, cst.LogicalName(0, 0, 96, 51, 0):
                return impl.data.OpeningBody(ln)
            case c_id.DATA,                                              0, cst.LogicalName(0, 0, 96, 51, 5):
                return impl.data.SealStatus(ln)
            case c_id.DATA,                                              0, cst.LogicalName(0, 0, 96, 51, e) if e in (1, 3, 4, 5, 6, 7):
                return impl.data.Unsigned(ln)
            case c_id.DATA,                                              0, cst.LogicalName(0, 0, 96, 51, e) if e == 8 or e == 9:
                return impl.data.OctetStringDateTime(ln)
            case c_id.DATA,                                              0, cst.LogicalName(0, b, 97, 98, e) if 0 <= e <= 9 or 10 <= e <= 29:
                return Data(ln)
            # 7.4.5 Data profile objects – Abstract
            case c_id.PROFILE_GENERIC,                                   1, cst.LogicalName(0, b, 99, 3, 0):
                return ProfileGeneric(ln)
            case c_id.PROFILE_GENERIC,                                   1, cst.LogicalName(0, b, 99, 1 | 2 | 12 | 13 | 14 | 15 | 16 | 17 | 18, e):
                return ProfileGeneric(ln)
            # ITE manufacture specific
            case c_id.DATA,                                              0, cst.LogicalName(0, 0, 128, 100 | 101 | 102 | 103 | 150 | 151 | 152 | 170, 0):
                return Data(ln)
            case c_id.DATA,                                              0, cst.LogicalName(0, 0, 128, 160, 0):
                return impl.data.ITEBitMap(ln)
            case c_id.CLIENT_SETUP,                                      0, cst.LogicalName(0, 0, 199, 255, 255):
                return ClientSetup(ln)
            case c_id.DATA,                                              0, cst.LogicalName(1, b, 0, 0, e) if e <= 9:
                return Data(ln)
            case c_id.DATA | c_id.REGISTER | c_id.EXT_REGISTER as i,     0, cst.LogicalName(1, b, 0, 3 | 4 | 7 | 9, e):
                return get_type_from_class(i, 0)(ln)
            # Nominal values
            case c_id.REGISTER | c_id.EXT_REGISTER as i,                 0, cst.LogicalName(1, b, 0, 6, e) if e <= 5:
                return get_type_from_class(i, 0)(ln)
            # Measurement period- / recording interval- / billing period duration
            case c_id.DATA,                 0, cst.LogicalName(1, b, 0, 8, 4 | 5):
                return impl.data.Unsigned(ln)
            # Coefficients
            case c_id.REGISTER | c_id.EXT_REGISTER as i,                 0, cst.LogicalName(1, b, 0, 10, e) if e <= 3:
                return get_type_from_class(i, 0)(ln)
            case c_id.DATA,                                              0, cst.LogicalName(1, b, 0, 11, e) if 1 <= e <= 7:
                return Data(ln)
            # RU. СТО 34.01-5.1-006-2021. 11.1 Рекомендуемые коды обозначения электрических величин
            case c_id.REGISTER,                                          0, cst.LogicalName(1, 0, 131, 35, 0):
                return Register(ln)
            case c_id.REGISTER,                                          0, cst.LogicalName(1, 0, 133, 35, 0):
                return Register(ln)
            #
            case c_id.REGISTER | c_id.EXT_REGISTER as i,                 0, cst.LogicalName(1, b, c, d, e) if c not in _NOT_PROCESSING_OF_MEASUREMENT_VALUES and \
                d in chain(_CUMULATIVE, _TIME_INTEGRAL_VALUES, _CONTRACTED_VALUES, _UNDER_OVER_LIMIT_THRESHOLDS, _UNDER_OVER_LIMIT_OCCURRENCE_COUNTERS,
                           _UNDER_OVER_LIMIT_DURATIONS, _UNDER_OVER_LIMIT_MAGNITUDES):
                return get_type_from_class(i, 0)(ln)
            case c_id.REGISTER,                                          0, cst.LogicalName(1, b, c, d, e) if c not in _NOT_PROCESSING_OF_MEASUREMENT_VALUES and \
                                                                                                              d in _INSTANTANEOUS_VALUES:
                return Register(ln)
            case c_id.REGISTER,                                          0, cst.LogicalName(1, 0, c, d, 0) if c in _CUMULATIVE and \
                                                                                                              d == _RU_CHANGE_LIMIT_LEVEL:
                return Register(ln)
            case c_id.REGISTER | c_id.EXT_REGISTER | c_id.PROFILE_GENERIC as i, 0, cst.LogicalName(1, b, c, d, e) if c not in _NOT_PROCESSING_OF_MEASUREMENT_VALUES and \
                                                                                                              d in _MAX_MIN_VALUES:
                return get_type_from_class(i, 0)(ln)
            # TODO: add DemandRegister below
            case c_id.REGISTER | c_id.EXT_REGISTER as i,                 0, cst.LogicalName(1, b, c, d, e) if c not in _NOT_PROCESSING_OF_MEASUREMENT_VALUES and \
                                                                                                              d in _CURRENT_AND_LAST_AVERAGE_VALUES:
                return get_type_from_class(i, 0)(ln)
            case c_id.DATA | c_id.REGISTER as i,                         0, cst.LogicalName(1, b, c, 40, e) if c not in _NOT_PROCESSING_OF_MEASUREMENT_VALUES:
                return get_type_from_class(i, 0)(ln)
            # RU. СТО 34.01-5.1-006-2021. 11.1 Рекомендуемые коды обозначения электрических величин
            case c_id.REGISTER,                                          0, cst.LogicalName(1, 0, 147, 133, 0):
                return Register(ln)
            case c_id.REGISTER,                                          0, cst.LogicalName(1, 0, 148, 36, 0):
                return Register(ln)
            #
            case c_id.PROFILE_GENERIC,                                1, cst.LogicalName(1, b, 94, 7, 0):
                ret = ProfileGeneric(ln)
                ret.scaler_profile_key = bytes((1, 0, 94, 7, 3, 255))
                return ret
            case c_id.PROFILE_GENERIC,                                1, cst.LogicalName(1, b, 94, 7, 1 | 2 | 3 | 4):
                return ProfileGeneric(ln)                           # Todo: RU. Scaler-profile With 1 entry
            case c_id.PROFILE_GENERIC,                                1, cst.LogicalName(1, b, 94, 7, 5 | 6):
                return ProfileGeneric(ln)                           # RU. Profile
            case c_id.PROFILE_GENERIC,                                1, cst.LogicalName(1, b, 98, 1, e):
                ret = ProfileGeneric(ln)
                ret.scaler_profile_key = bytes((1, 0, 94, 7, 1, 255))
                return ret
            case c_id.PROFILE_GENERIC,                                1, cst.LogicalName(1, b, 98, 2, e):
                ret = ProfileGeneric(ln)
                ret.scaler_profile_key = bytes((1, 0, 94, 7, 2, 255))
                return ret
            case c_id.PROFILE_GENERIC,                                1, cst.LogicalName(1, b, 99, 1 | 2, e):
                ret = ProfileGeneric(ln)
                ret.scaler_profile_key = bytes((1, 0, 94, 7, 4, 255))
                return ret
            case c_id.REGISTER,                                      0, cst.LogicalName(128, 0, c, 0, 0) if c <= 19:
                return Register(ln)
            case _:
                raise exc.NoObject(F'DLMS Object: {class_id=} {version=} {ln=} not searched in relation library')

    def add_if_missing(self, class_id: ut.CosemClassId = None,
                       version: cdt.Unsigned | None = cdt.Unsigned(),
                       logical_name: cst.LogicalName = cst.LogicalName()) -> InterfaceClass | None:
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
               version: cdt.Unsigned | None = cdt.Unsigned(0),
               logical_name: cst.LogicalName = cst.LogicalName(),
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

    def add(self, class_id: ut.CosemClassId = None,
            version: cdt.Unsigned | None = cdt.Unsigned(0),
            logical_name: cst.LogicalName = cst.LogicalName()) -> InterfaceClass:
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

    @lru_cache(maxsize=ic.get_COSEM_class_amount())
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

    def get_object(self, value: bytes | str | cst.LogicalName | cdt.Structure | ut.CosemObjectInstanceId | ut.CosemAttributeDescriptor
                   | ut.CosemAttributeDescriptorWithSelection | ut.CosemMethodDescriptor) -> InterfaceClass:
        """ return object from obis<string> or raise exception if it absence """
        match value:
            case bytes():                                                    return self.__get_object(value)
            case cst.LogicalName() | ut.CosemObjectInstanceId():             return self.__get_object(value.contents)
            case ut.CosemAttributeDescriptor() | ut.CosemMethodDescriptor(): return self.__get_object(value.instance_id.contents)
            case ut.CosemAttributeDescriptorWithSelection():                 return self.__get_object(value.cosem_attribute_descriptor.instance_id.contents)
            case str():                                                      return self.__get_object(cst.LogicalName(value).contents)
            case cdt.Structure(logical_name=value.logical_name):             return self.__get_object(value.logical_name.contents)
            case _:                                                          raise exc.NoObject(F"Can't find DLMS Object from collection with {value=}")

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

    def clear(self):
        """ clear to default objects amount """
        for obj in self.__container.copy():
            if obj not in self.__const_objs:
                self.__container.remove(obj)
        self.__get_object.cache_clear()

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
    def LDN(self) -> Data:
        return self.__get_object(o.LDN)

    @cached_property
    def current_association(self) -> AssociationLN:
        return self.__get_object(o.CURRENT_ASSOCIATION)

    lru_cache(4)
    def getASSOCIATION(self, instance: int) -> AssociationLN:
        return self.__get_object(bytes((0, 0, 40, 0, instance, 255)))

    @cached_property
    def PUBLIC_ASSOCIATION(self) -> AssociationLN:
        return self.__get_object(bytes((0, 0, 40, 0, 1, 255)))

    @cached_property
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

    @property
    def IEC_HDLS_setup(self) -> IECHDLCSetup:
        return self.__get_object(bytes((0, int(self.client_setup.channel_communication), 22, 0, 0, 255)))

    @cached_property
    def TCP_UDP_setup(self) -> TCPUDPSetup:
        return self.__get_object(bytes((0, 0, 25, 0, 0, 255)))

    @lru_cache(3)
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

    @cached_property
    def RU_EXTENDED_PASSPORT_DATA(self) -> ProfileGeneric:
        return self.__get_object(bytes((0, 0, 94, 7, 1, 255)))

    @cached_property
    def firmware_version(self) -> Data:
        return self.__get_object(bytes((0, 0, 96, 1, 2, 255)))

    @cached_property
    def device_type(self) -> Data:
        return self.__get_object(bytes((0, 0, 96, 1, 1, 255)))

    @cached_property
    def manufacturing_date(self) -> Data:
        return self.__get_object(bytes((0, 0, 96, 1, 4, 255)))

    @cached_property
    def RU_LOAD_LOCK_STATUS(self) -> Data:
        return self.__get_object(bytes((0, 0, 96, 4, 3, 255)))

    @property
    def firmwares_description(self) -> Data:
        """ Consist from boot_version, descriptor, ex.: 0005PWRM_M2M_3_F1_5ppm_Spvq. 0.0.128.100.0.255 """
        return self.__get_object(bytes((0, 0, 128, 100, 0, 255)))

    @cached_property
    def serial_number(self) -> Data:
        """ Ex.: 0101000434322 """
        return self.__get_object(bytes((0, 0, 96, 1, 0, 255)))

    def SECURITY_SETUP(self) -> SecuritySetup:
        """SecuritySetup by order of CurrentAssociation"""
        return self.__get_object(bytes(self.current_association.security_setup_reference))

    @property
    def IC(self) -> Data:
        """ invocation counter """
        return self.__get_object(bytes((0, int(self.client_setup.channel_communication), 43, 1, self.current_association.security_setup_reference.e, 255)))

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

    @cached_property
    def RU_MAXIMUM_CURRENT_EXCESS_LIMIT(self) -> Register:
        """ RU. СТО 34.01-5.1-006-2021 ver3, 11.1. Maximum current excess limit before the subscriber is disconnected, % of IMAX """
        return self.__get_object(bytes((1, 0, 11, 134, 0, 255)))

    @cached_property
    def RU_MAXIMUM_VOLTAGE_EXCESS_LIMIT(self) -> Register:
        """ RU. СТО 34.01-5.1-006-2021 ver3, 11.1. Maximum voltage excess limit before the subscriber is disconnected, % of Unominal """
        return self.__get_object(bytes((1, 0, 12, 134, 0, 255)))

    @lru_cache(5)
    def getDISCONNECT_CONTROL(self, ch: int = 0) -> DisconnectControl:
        """DLMS UA 1000-1 Ed 14 6.2.46 Disconnect control objects by channel"""
        return self.__get_object(bytes((0, ch, 96, 3, 10, 255)))

    @lru_cache(5)
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

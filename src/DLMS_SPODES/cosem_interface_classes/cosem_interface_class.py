"""
DLMS UA 1000-1 Ed 14
"""
import dataclasses
from functools import lru_cache

from typing_extensions import deprecated
from abc import ABC, abstractmethod
from typing import Iterator, Type, TypeAlias, Callable, Any, Self, Literal
from ..types import cdt, ut, cst
from ..relation_to_OBIS import get_name
import logging
from enum import IntEnum
from itertools import count
from .. import exceptions as exc
from .overview import ClassID, Version

from ..config_parser import get_values


_am_names = get_values("DLMS", "am_names")


logger = logging.getLogger(__name__)
logger.level = logging.INFO

logger.info(F'Register start')

_n_class = count(0)


class Classifier(IntEnum):
    """ (dyn.) Classifies an attribute that carries a process value, which is updated by the meter itself.
    (static) Classifies an attribute, which is not updated by the meter itself (e.g. configuration data). """
    NOT_SPECIFIC = 0
    STATIC = 1
    DYNAMIC = 2

    def __str__(self):
        return self.name


SelectiveAccessDescriptor: TypeAlias = ut.SelectiveAccessDescriptor  # TODO: make with subclass


@dataclasses.dataclass(frozen=True)
class ICElement:
    NAME: str

    def __str__(self):
        if _am_names and (t := _am_names.get(self.NAME)):
            return t
        else:
            return self.NAME


@dataclasses.dataclass(frozen=True)
class ICAElement(ICElement):
    DATA_TYPE: Type[cdt.CommonDataType] | ut.CHOICE
    min: int = None
    max: int = None
    default: int = None
    classifier: Classifier = Classifier.STATIC
    selective_access: Type[SelectiveAccessDescriptor] | None = None

    def get_change(self,
                   data_type: Type[cdt.CommonDataType] | ut.CHOICE = None,
                   classifier: Classifier = None) -> Self:
        return ICAElement(
            NAME=self.NAME,
            DATA_TYPE=self.DATA_TYPE if data_type is None else data_type,
            min=self.min,
            max=self.max,
            default=self.default,
            classifier=self.classifier if classifier is None else classifier,
            selective_access=self.selective_access)


@dataclasses.dataclass(frozen=True)
class ICMElement(ICElement):
    DATA_TYPE: Type[cdt.CommonDataType]


_LN_ELEMENT = ICAElement(
    NAME="logical_name",
    DATA_TYPE=cst.LogicalName)
"""" first element for each COSEM Interface Class"""


class ObjectValidationError(exc.DLMSException):
    """use in validation method of COSEMInterfaceClasses"""
    def __init__(self,
                 ln: cst.LogicalName,
                 i: int,
                 message: str):
        Exception.__init__(self, F"for {ln}: {i}. {message}")
        self.ln = ln
        self.i = i


class EmptyAttribute(exc.DLMSException):
    """need read attribute"""
    def __init__(self,
                 ln: cst.LogicalName,
                 i: int):
        Exception.__init__(self, F"empty {ln}: {i}")
        self.ln = ln
        self.i = i


Name = Literal[
    "Data",
    "Register",
    "Extended register",
    "Demand register",
    "Register activation",
    "Profile generic",
    "Clock",
    "Script table",
    "Schedule",
    "Special days table",
    "Association SN",
    "Association LN",
    "SAP Assignment",
    "Image transfer",
    "IEC local port setup",
    "Activity calendar",
    "Register monitor",
    "Single action schedule",
    "IEC HDLC setup",
    "IEC twisted pair (1) setup",
    "M-BUS slave port setup",
    "Utility tables",
    "Modem configuration",
    "PSTN modem configuration",
    "Auto answer",
    "Auto connect",
    "PSTN Auto dial",
    "Data protection",
    "Push setup",
    "TCP-UDP setup",
    "IPv4 setup",
    "MAC address setup",
    "PPP setup",
    "GPRS modem setup",
    "SMTP setup",
    "GSM diagnostic",
    "IPv6 setup",
    "S-FSK Phy&MAC setup",
    "S-FSK Active initiator",
    "S-FSK MAC synchronization timeouts",
    "S-FSK MAC counters",
    "IEC 61334-4-32 LLC setup",
    "S-FSK IEC 61334-4-32 LLC setup",
    "S-FSK Reporting system list",
    "ISO/IEC 8802-2 LLC Type 1 setup",
    "ISO/IEC 8802-2 LLC Type 2 setup",
    "ISO/IEC 8802-2 LLC Type 3 setup",
    "Register table",
    "Compact data",
    "Status mapping",
    "Security setup",
    "Parameter monitor",
    "Sensor manager",
    "Arbitrator",
    "Disconnect control",
    "Limiter",
    "M-Bus client",
    "Wireless Mode Q channel",
    "M-Bus master port setup",
    "DLMS/COSEM server M-Bus port setup",
    "M-Bus diagnostic",
    "61334-4-32 LLC SSCS setup",
    "PRIME NB OFDM PLC Physical layer counters",
    "PRIME NB OFDM PLC MAC setup",
    "PRIME NB OFDM PLC MAC functional parameters",
    "PRIME NB OFDM PLC MAC counters",
    "PRIME NB OFDM PLC MAC network administration data",
    "PRIME NB OFDM PLC Application identification",
    "G3-PLC MAC layer counters",
    "G3 NB OFDM PLC MAC layer counters",
    "G3-PLC MAC setup",
    "G3 NB OFDM PLC MAC setup",
    "G3-PLC 6LoWPAN adaptation layer setup",
    "G3 NB OFDM PLC 6LoWPAN adaptation layer setup",
    "Wi-SUN setup",
    "Wi-SUN diagnostic",
    "RPL diagnostic",
    "MPL diagnostic",
    "NTP Setup",
    "ZigBee® SAS startup",
    "ZigBee® SAS join",
    "ZigBee® SAS APS fragmentation",
    "ZigBee® network control",
    "ZigBee® tunnel setup",
    "Account",
    "Credit",
    "Charge",
    "Token gateway",
    "Function control",
    "Array manager",
    "Communication port protection",
    "SCHC-LPWAN setup",
    "SCHC-LPWAN diagnostic",
    "LoRaWAN setup",
    "LoRaWAN diagnostic",
    "ISO/IEC14908 Identification",
    "ISO/IEC 14908 Protocol setup",
    "ISO/IEC 14908 protocol status",
    "ISO/IEC 14908 diagnostic",
    "HS-PLC ISO/IEC 12139-1 MAC setup",
    "HS-PLC ISO/IEC 12139-1 CPAS setup",
    "HS-PLC ISO/IEC 12139-1 IP SSAS setup",
    "HS-PLC ISO/IEC 12139-1 HDLC SSAS setup",
    "LTE monitoring"]
"""Interface class name row from Table 3 – List of interface classes by class_id"""


@lru_cache(150)
def ClassIDVer2Name(class_id: ClassID, ver: Version) -> Name:
    """Table 3 – List of interface classes by class_id"""
    match int(class_id), int(ver):
        case 1, 0: return "Data"
        case 3, 0: return "Register"
        case 4, 0: return "Extended register"
        case 5, 0: return "Demand register"
        case 6, 0: return "Register activation"
        case 7, 0 | 1: return "Profile generic"
        case 8, 0: return "Clock"
        case 9, 0: return "Script table"
        case 10, 0: return "Schedule"
        case 11, 0: return "Special days table"
        case 12, 0 | 1 | 2 | 3 | 4: return "Association SN"
        case 15, 0 | 1 | 2 | 3: return "Association LN"
        case 17, 0: return "SAP Assignment"
        case 18, 0: return "Image transfer"
        case 19, 0 | 1: return "IEC local port setup"
        case 20, 0: return "Activity calendar"
        case 21, 0: return "Register monitor"
        case 22, 0: return "Single action schedule"
        case 23, 0 | 1: return "IEC HDLC setup"
        case 24, 0 | 1: return "IEC twisted pair (1) setup"
        case 25, 0: return "M-BUS slave port setup"
        case 26, 0: return "Utility tables"
        case 27, 1: return "Modem configuration"
        case 27, 0: return "PSTN modem configuration"
        case 28, 0 | 2: return "Auto answer"
        case 29, 1 | 2: return "Auto connect"
        case 29, 0: return "PSTN Auto dial"
        case 30, 0: return "Data protection"
        case 40, 0 | 1 | 2: return "Push setup"
        case 41, 0: return "TCP-UDP setup"
        case 42, 0: return "IPv4 setup"
        case 43, 0: return "MAC address setup"
        case 44, 0: return "PPP setup"
        case 45, 0: return "GPRS modem setup"
        case 46, 0: return "SMTP setup"
        case 47, 0 | 1 | 2: return "GSM diagnostic"
        case 48, 0: return "IPv6 setup"
        case 50, 0 | 1: return "S-FSK Phy&MAC setup"
        case 51, 0: return "S-FSK Active initiator"
        case 52, 0: return "S-FSK MAC synchronization timeouts"
        case 53, 0: return "S-FSK MAC counters"
        case 55, 1: return "IEC 61334-4-32 LLC setup"
        case 55, 0: return "S-FSK IEC 61334-4-32 LLC setup"
        case 56, 0: return "S-FSK Reporting system list"
        case 57, 0: return "ISO/IEC 8802-2 LLC Type 1 setup"
        case 58, 0: return "ISO/IEC 8802-2 LLC Type 2 setup"
        case 59, 0: return "ISO/IEC 8802-2 LLC Type 3 setup"
        case 61, 0: return "Register table"
        case 62, 0 | 1: return "Compact data"
        case 63, 0: return "Status mapping"
        case 64, 0 | 1: return "Security setup"
        case 65, 0 | 1: return "Parameter monitor"
        case 67, 0: return "Sensor manager"
        case 68, 0: return "Arbitrator"
        case 70, 0: return "Disconnect control"
        case 71, 0: return "Limiter"
        case 72, 0 | 1: return "M-Bus client"
        case 73, 0: return "Wireless Mode Q channel"
        case 74, 0: return "M-Bus master port setup"
        case 76, 0: return "DLMS/COSEM server M-Bus port setup"
        case 77, 0: return "M-Bus diagnostic"
        case 80, 0: return "61334-4-32 LLC SSCS setup"
        case 81, 0: return "PRIME NB OFDM PLC Physical layer counters"
        case 82, 0: return "PRIME NB OFDM PLC MAC setup"
        case 83, 0: return "PRIME NB OFDM PLC MAC functional parameters"
        case 84, 0: return "PRIME NB OFDM PLC MAC counters"
        case 85, 0: return "PRIME NB OFDM PLC MAC network administration data"
        case 86, 0: return "PRIME NB OFDM PLC Application identification"
        case 90, 1: return "G3-PLC MAC layer counters"
        case 90, 0: return "G3 NB OFDM PLC MAC layer counters"
        case 91, 1 | 2: return "G3-PLC MAC setup"
        case 91, 0: return "G3 NB OFDM PLC MAC setup"
        case 92, 1 | 2: return "G3-PLC 6LoWPAN adaptation layer setup"
        case 92, 0: return "G3 NB OFDM PLC 6LoWPAN adaptation layer setup"
        case 95, 0: return "Wi-SUN setup"
        case 96, 0: return "Wi-SUN diagnostic"
        case 97, 0: return "RPL diagnostic"
        case 98, 0: return "MPL diagnostic"
        case 100, 0: return "NTP Setup"
        case 101, 0: return "ZigBee® SAS startup"
        case 102, 0: return "ZigBee® SAS join"
        case 103, 0: return "ZigBee® SAS APS fragmentation"
        case 104, 0: return "ZigBee® network control"
        case 104, 0: return "ZigBee® tunnel setup"
        case 111, 0: return "Account"
        case 112, 0: return "Credit"
        case 113, 0: return "Charge"
        case 115, 0: return "Token gateway"
        case 122, 0: return "Function control"
        case 123, 0: return "Array manager"
        case 124, 0: return "Communication port protection"
        case 126, 0: return "SCHC-LPWAN setup"
        case 127, 0: return "SCHC-LPWAN diagnostic"
        case 128, 0: return "LoRaWAN setup"
        case 129, 0: return "LoRaWAN diagnostic"
        case 130, 0: return "ISO/IEC14908 Identification"
        case 131, 0: return "ISO/IEC 14908 Protocol setup"
        case 132, 1: return "ISO/IEC 14908 protocol status"
        case 133, 1: return "ISO/IEC 14908 diagnostic"
        case 140, 0: return "HS-PLC ISO/IEC 12139-1 MAC setup"
        case 141, 0: return "HS-PLC ISO/IEC 12139-1 CPAS setup"
        case 142, 0: return "HS-PLC ISO/IEC 12139-1 IP SSAS setup"
        case 143, 0: return "HS-PLC ISO/IEC 12139-1 HDLC SSAS setup"
        case 151, 0 | 1: return "LTE monitoring"
        case _: raise exc.ITEApplication(F"not find <Interface class name> with: {class_id=}, {ver=}")


class COSEMInterfaceClasses(ABC):
    CLASS_ID: ClassID
    VERSION: Version | None = None
    """ Identification code of the version of the class. The version of each object is retrieved together with the logical name and the class_id by reading the object_list 
    attribute of an “Association LN” / ”Association SN” object. Within one logical device, all instances of a certain class must be of the same version."""
    A_ELEMENTS: tuple[ICAElement, ...]
    M_ELEMENTS: tuple[ICMElement, ...] = tuple()  # empty if class not has the methods
    cardinality: tuple[int, int | None]
    __attributes: list[cdt.CommonDataType | None]
    __specific_methods: tuple[cdt.CommonDataType, ...] = None
    _cbs_attr_post_init: dict[int, Callable]
    collection: Any | None  # Collection. todo: remove in future

    def __init__(self, logical_name: cst.LogicalName | bytes | str):
        self.collection = None
        # """ TODO: """
        self.cardinality = (0, None)
        """ (min, max). default is (0, None) from 0 to infinity. If min == max then they are value.   
        Specifies the number of instances of the class within a logical device. value The class shall be 
        instantiated exactly “value” times. min...max. The class shall be instantiated at least “min.” times 
        and at most “max.” times. If min. is zero (0) then the class is optional, otherwise (min. > 0) "min." 
        instantiations of the class are mandatory. """

        self.__attributes = [_LN_ELEMENT.DATA_TYPE(logical_name), *[None] * len(self.A_ELEMENTS)]
        """ Attributes container """

        if self.M_ELEMENTS is not None:
            self.__specific_methods = tuple(el.DATA_TYPE() for el in self.M_ELEMENTS)
            """Specific methods container"""

        self._cbs_attr_post_init = dict()
        """container with callbacks for post initial attribute by index"""

        self._cbs_attr_before_init = dict()
        """container with callbacks for before initial attribute by index"""

        # init all attributes with default value
        for i in range(2, len(self.A_ELEMENTS)+2):
            default = self.get_attr_element(i).default
            if default is not None:
                self.set_attr(i, default)

        self.characteristics_init()

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        cls.hash_ = next(_n_class)
        # print(cls.__name__)

    @classmethod
    def get_attr_element(cls, i: int) -> ICAElement:
        """return element by order index. Override in each new class"""
        if i == 1:
            return _LN_ELEMENT
        elif i > len(cls.A_ELEMENTS) + 1:
            raise exc.DLMSException(F"got attribute index: {i}, expected 1..{len(cls.A_ELEMENTS) + 1}")
        else:
            return cls.A_ELEMENTS[i - 2]

    @classmethod
    def get_meth_element(cls, i: int) -> ICMElement:
        """ implement in subclasses with methods """
        return cls.M_ELEMENTS[i - 1]

    @abstractmethod
    def characteristics_init(self):
        """ initiate all attributes and methods of class """

    def get_attr(self, index: int) -> Any | None:
        if index > (max_l := self.get_attr_length()):
            raise IndexError(F"for {self} got attribute index: {index}, expected 0..{max_l}")
        elif index >= 1:
            return self.__attributes[index-1]
        else:
            raise IndexError(F"not support {index=} as attribute")

    def set_attr_force(self,
                       index: int,
                       value: cdt.CommonDataType):
        self.__attributes[index-1] = value
        """use for change official types to custom(not valid)"""

    def encode(self,
               index: int,
               value: str | int) -> cdt.CommonDataType | None:
        """encode attribute value from string if possible, else return None(for CHOICE variant)"""
        if (attr := self.get_attr(index)) is None:
            data_type = self.get_attr_element(index).DATA_TYPE
            if isinstance(data_type, ut.CHOICE):
                return None
            else:
                return self.get_attr_element(index).DATA_TYPE(value)
        else:
            ret = attr.copy()
            ret.set(value)
            return ret

    def set_attr(self,
                 index: int,
                 value=None,
                 data_type: cdt.CommonDataType = None):
        value = self.get_attr_element(index).default if value is None else value
        data_type = self.get_attr_element(index).DATA_TYPE if data_type is None else data_type
        if self.__attributes[index-1] is None:
            new_value = data_type(value)
            if cb_func := self._cbs_attr_before_init.get(index, None):
                cb_func(new_value)
                self._cbs_attr_before_init.pop(index)
            self.__attributes[index-1] = new_value
            if cb_func := self._cbs_attr_post_init.get(index, None):
                cb_func()
                self._cbs_attr_post_init.pop(index)
            else:
                """without callback post init"""
        else:
            self.__attributes[index-1].set(value)

    def parse_attr(self, index: int, value: cdt.Transcript, data_type: cdt.CommonDataType = None):
        """set attribute value by Transcript"""
        dt = self.get_attr_element(index).DATA_TYPE if data_type is None else data_type
        if hasattr(dt, "TAG"):
            self.__attributes[index - 1] = dt.parse(value)
        else:  # maybe CHOICE
            self.__attributes[index - 1] = self.get_attr(index).parse(value)

    def set_attr_link(self, index: int, link: cdt.CommonDataType):
        # self.__attributes[index - 1] = link  # TODO: without validate now for pass load_objects
        if isinstance(link, self.get_attr_element(index).DATA_TYPE):
            self.__attributes[index-1] = link
        else:
            raise ValueError(F'get wrong link: {link} for {self} attr: {index}')

    def get_attr_data_type(self, index: int) -> Type[cdt.CommonDataType] | ut.CHOICE:
        """search data_type attribute value"""
        value: cdt.CommonDataType = self.get_attr(index)
        if value is not None:
            return value.__class__
        else:
            return self.get_attr_element(index).DATA_TYPE

    def clear_attr(self, i: int):
        """use in template"""
        if i > 1:
            self.__attributes[i-1] = None
        else:
            raise ValueError(F'not support clear {self} attr: {i}')

    @deprecated("use get_meth_element")
    def get_meth(self, index: int) -> Any:
        if index >= 1:
            return self.__specific_methods[index-1]
        else:
            raise IndexError(F'not support {index=} as attribute')

    def get_index_with_attributes(self) -> Iterator[tuple[int, cdt.CommonDataType | None]]:
        """ if by initiation order is True then need override method for concrete class"""
        return iter(zip(range(1, self.get_attr_length()+1), self.__attributes))

    def get_attr_length(self) -> int:
        """common attributes amount"""
        return len(self.A_ELEMENTS)+1

    @property
    def it_index_with_meth(self) -> Iterator[tuple[int, cdt.CommonDataType]]:
        return iter(zip(range(1, 20), self.__specific_methods))

    @property
    def logical_name(self) -> cst.LogicalName:
        """ The logical name is always the first attribute of a class. It identifies the instantiation (COSEM object) of this class.
        The value of the logical_name conforms to OBIS (see IEC 62056-61)"""
        return self.get_attr(1)

    def __lt__(self, other: Self):
        return self.logical_name < other.logical_name

    def __setattr__(self, key, value):
        match key:
            case 'VERSION' | 'CLASS_ID' | 'A_ELEMENTS' | 'M_ELEMENTS' as prop: raise ValueError(F"Don't support set {prop}")
            case _:                                                            super().__setattr__(key, value)

    def __getitem__(self, item) -> cdt.CommonDataType:
        """ get attribute value by index, start with 1 """
        if isinstance(item, str):
            return super(COSEMInterfaceClasses, self).__getattr__(item)
        return self.get_attr(item)

    def __iter__(self) -> Iterator[cdt.CommonDataType]:
        """ return attributes iterator"""
        return iter(self.__attributes)

    def __str__(self):
        return F'{self.logical_name.get_report()} {get_name(self.logical_name)}'

    def get_obis(self) -> bytes:
        """ return obis as bytes[6] """
        return self.logical_name.contents

    @property
    def instance_id(self) -> cdt.OctetString:
        return self.logical_name

    # TODO: rewrite this
    def get_attribute_descriptor(self, index: int) -> bytes:
        """ Cosem-Attribute-Descriptor IS/IEC 62056-53 : 2006, 8.3 Useful types """
        return self.CLASS_ID.contents + self.instance_id.contents + ut.CosemObjectAttributeId(index).contents

    @property
    def string_type_cardinality(self) -> str:
        min_cardinality, max_cardinality = self.cardinality
        if min_cardinality == max_cardinality:
            return str(min_cardinality)
        else:
            max_cardinality = str(max_cardinality) if max_cardinality else 'n'
            return F'{str(min_cardinality)}...{max_cardinality}'

    def reset_attribute(self, index: int):
        """ try set default to value """
        self.set_attr(index, self.get_attr_element(index).default)

    def get_attr_descriptor(self,
                            value: int,
                            with_selection: bool = False) -> ut.CosemAttributeDescriptor:
        """ return AttributeDescriptor without selection """
        return ut.CosemAttributeDescriptor((
            self.CLASS_ID,
            ut.CosemObjectInstanceId(self.logical_name.contents),
            ut.CosemObjectAttributeId(value)))

    def get_meth_descriptor(self, value: str | int) -> ut.CosemMethodDescriptor:
        """ TODO """
        match value:
            case int() as index:
                return ut.CosemMethodDescriptor((ut.CosemClassId(self.CLASS_ID.contents),
                                                 ut.CosemObjectInstanceId(self.logical_name.contents),
                                                 ut.CosemObjectMethodId(index)))

    def __hash__(self):
        return hash(self.logical_name)

    def validate(self):
        """procedure for validate class values"""

    def get_value(self, par: bytes) -> cdt.CommonDataType:
        ret = self.get_attr(par[0])
        for i in par[1:]:
            ret = ret[i]
        return ret

    def get_values(self, par: bytes) -> list[cdt.CommonDataType]:
        ret = [self.get_attr(par[0])]
        for i in par[1:]:
            ret.append(ret[-1][i])
        return ret

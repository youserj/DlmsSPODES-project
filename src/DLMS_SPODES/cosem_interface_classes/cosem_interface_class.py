"""
DLMS UA 1000-1 Ed 14
"""
from dataclasses import dataclass
from struct import Struct
from functools import lru_cache
from typing_extensions import deprecated
from typing import TypeAlias, Self, Literal, Optional, Protocol, ClassVar, Any, overload
from ..types.type_alias import Attr, Obis, Index, Encoding, attr2i, attr2obis, AttrDesc, pack_attr, Meth
from ..types import cdt, ut, cst
from StructResult import result
from StructResult.result import ValueOrError, Error
from COSEMpdu.byte_buffer import ByteBuffer
from COSEMpdu import axdr
from COSEMpdu.apdu import CosemClassId, SelectiveAccessDescriptor
from enum import IntEnum
from .. import exceptions as exc
from .overview import ClassID
from ..settings import settings
from .. import literals


obis2attr_pat = Struct(">6sH")
"""concatenate Obis and Index pattern"""


class Classifier(IntEnum):
    """ (dyn.) Classifies an attribute that carries a process value, which is updated by the meter itself.
    (static) Classifies an attribute, which is not updated by the meter itself (e.g. configuration data). """
    NOT_SPECIFIC = 0
    STATIC = 1
    DYNAMIC = 2

    def __str__(self) -> str:
        return self.name


@dataclass(frozen=True)
class ICElement:
    i: int
    NAME: str

    def __str__(self) -> str:
        try:
            return str(getattr(settings.am_names, self.NAME))
        except AttributeError:
            return self.NAME

    def __lt__(self, value: object) -> bool:
        if isinstance(value, ICElement):
            return self.i < value.i
        raise NotImplementedError


type DataType = axdr.ChoiceType | axdr.TaggedType[Any]


@dataclass(frozen=True)
class ICAElement(ICElement):
    DATA_TYPE: type[DataType]
    min: Optional[int] = None
    max: Optional[int] = None
    default: Optional[int] = None
    classifier: Classifier = Classifier.STATIC
    selective_access: Optional[type[SelectiveAccessDescriptor]] = None

    def get_change(self,
                   data_type: Optional[type[DataType]] = None,
                   classifier: Optional[Classifier] = None) -> "ICAElement":
        return ICAElement(
            i=self.i,
            NAME=self.NAME,
            DATA_TYPE=self.DATA_TYPE if data_type is None else data_type,
            min=self.min,
            max=self.max,
            default=self.default,
            classifier=self.classifier if classifier is None else classifier,
            selective_access=self.selective_access)


@dataclass(frozen=True)
class ICMElement(ICElement):
    DATA_TYPE: type[DataType]


@overload
def update_collection(container: tuple[ICAElement, ...], *elements: ICAElement) -> tuple[ICAElement, ...]: ...


@overload
def update_collection(container: tuple[ICMElement, ...], *elements: ICMElement) -> tuple[ICMElement, ...]: ...


def update_collection[T: ICElement](container: tuple[T, ...], *elements: T) -> tuple[T, ...]:
    new = list(container)
    for el in elements:
        for c_el in container:
            if el.i == c_el.i:
                new.remove(c_el)
                break
        new.append(el)
    new.sort()
    return tuple(new)


_LN_ELEMENT: ICAElement = ICAElement(1, "logical_name", cst.LogicalName)
"""" first element for each COSEM Interface Class"""


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
    "LTE monitoring"
]
"""Interface class name row from Table 3 – List of interface classes by class_id"""


@lru_cache(150)
def ClassIDVer2Name(class_id: ClassID, ver: cdt.Unsigned) -> Name:
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


@dataclass
class Cardinality:
    """4.1.4 Class description notation"""
    min: int = 0
    max: int = -1
    """default -1 as infinity"""


class IC(Protocol):
    """4 The COSEM interface classes"""
    obis: Obis
    CLASS_ID: ClassVar[int]
    "class_id"
    VERSION: ClassVar[int]
    "version"
    A_ELEMENTS: ClassVar[tuple[ICAElement, ...]]
    "Attributes"
    M_ELEMENTS: ClassVar[tuple[ICMElement, ...]] = ()  # empty if class not has the methods
    "Specific methods"
    CARDINALITY: ClassVar[Cardinality] = Cardinality()
    "Cardinality"

    def __init__(self, obis: Obis) -> None:
        self.obis = obis

    @classmethod
    def getAElement(cls, i: int) -> ValueOrError[ICAElement]:
        """return element by order index. Override in each new class"""
        if i == 1:
            return _LN_ELEMENT
        if i > len(cls.A_ELEMENTS) + 1:
            return result.Error.from_e(exc.DLMSException(F"got attribute index: {i}, expected 1..{len(cls.A_ELEMENTS) + 1}"))
        return cls.A_ELEMENTS[i - 2]

    @classmethod
    def getMElement(cls, i: int) -> ValueOrError[ICMElement]:
        """return method element by order index. Override in each new class"""
        if i > len(cls.M_ELEMENTS):
            return result.Error.from_e(exc.DLMSException(F"got method index: {i}, expected 1..{len(cls.M_ELEMENTS)}"))
        return cls.M_ELEMENTS[i - 1]

    def get[T: DataType](self, i: Index, buf: ByteBuffer, e_type: type[T]) -> ValueOrError[T]:
        """get CDT with type checking"""
        if isinstance(r_el := self.getAElement(i), result.Error):
            return r_el
        if isinstance(r_data := r_el.DATA_TYPE.get(buf), result.Error):
            return r_data
        if isinstance(r_data, e_type):
            return r_data
        return result.Error.from_e(TypeError(f"got {r_data.__class__}, expected {e_type}"))

    def getCDT(self, i: Index, buf: ByteBuffer) -> ValueOrError[DataType]:
        """get CDT without type checking"""
        if isinstance(res_el := self.getAElement(i), result.Error):
            return res_el
        return res_el.DATA_TYPE.get(buf)

    @property
    def logical_name(self) -> Attr:
        """logical name"""
        return pack_attr(self.obis, 1)

    # def get_attr(self, i: int) -> Optional[cdt.CommonDataType]:
    #     aelement = self.getAElement(i).unwrap()
    #     if len(self._encodings[i - 1]) < 2:
    #         if (data := self._data[i - 1]) is None:
    #             return None
    #         return data
    #     data = aelement.DATA_TYPE(self._encodings[i - 1])  # todo: make from_encoding
    #     self._data[i - 1] = data
    #     self._encodings[i - 1] = b""
    #     return data
    #
    # def get_encoding(self, i: int) -> result.SimpleOrError[bytes]:
    #     if isinstance(res_ae := self.getAElement(i), result.Error):
    #         return res_ae
    #     if len(enc := self._encodings[i - 1]) > 1:
    #         return result.Simple(enc)
    #     if (data := self._data[i - 1]) is not None:
    #         return result.Simple(data.encoding)
    #     return result.Error(f"not find encoding for index={i}")
    #
    # def get_tag(self, i: int) -> result.SimpleOrError[cdt.TAG]:
    #     if isinstance(res_ae := self.getAElement(i), result.Error):
    #         return res_ae
    #     if (data := self._data[i - 1]) is not None:
    #         return result.Simple(data.TAG)
    #     if len(enc := self._encodings[i - 1]) > 0:
    #         return result.Simple(cdt.TAG(enc[0:]))
    #     return result.Error(f"not find TAG for index={i}")
    #
    # @deprecated("not used now")
    # def set_attr_force(self,
    #                    index: int,
    #                    value: cdt.CommonDataType):
    #     raise RuntimeError("set_attr_force")
    #
    # @deprecated("use <parse_attr>")
    # def encode(self,
    #            index: int,
    #            value: str | int) -> cdt.CommonDataType | None:
    #     """encode attribute value from string if possible, else return None(for CHOICE variant)"""
    #     raise RuntimeError("encode")
    #
    # def set(self, i: int, data: Encoding):
    #     self._encodings[i - 1] = data
    #
    # def set_attr(self, i: int, value: cdt.CommonDataType):
    #     aelement = self.getAElement(i).unwrap()
    #     if self._data[i - 1] is None:
    #         new_value = aelement.DATA_TYPE(value)
    #         self._data[i - 1] = new_value
    #     else:
    #         self._data[i - 1].set(value)

    def parse[T: cdt.CommonDataType](self, i: int, value: cdt.Transcript, e_type: type[T]) -> result.SimpleOrError[T]:
        """get CDT value by Transcript"""
        if isinstance(res_el := self.getAElement(i), result.Error):
            return res_el
        if isinstance(data := res_el.value.DATA_TYPE.parse(value), e_type):
            return result.Simple(data)
        return result.Error.from_e(TypeError(f"got {data.__class__}, expected {e_type}"))

    # @deprecated("not used now")
    # def set_attr_link(self, index: int, link: cdt.CommonDataType):
    #     # self.__attributes[index - 1] = link  # TODO: without validate now for pass load_objects
    #     if isinstance(link, self.get_attr_element(index).DATA_TYPE):
    #         self._encodings[index - 1] = link
    #     else:
    #         raise ValueError(F'get wrong link: {link} for {self} attr: {index}')
    #
    # def get_attr_data_type(self, index: int) -> Type[cdt.CommonDataType] | ut.CHOICE:
    #     """search data_type attribute value"""
    #     value: cdt.CommonDataType = self.get_attr(index)
    #     if value is not None:
    #         return value.__class__
    #     else:
    #         return self.get_attr_element(index).DATA_TYPE
    #
    # def clear_attr(self, i: int):
    #     """use in template"""
    #     self.getAElement(i).unwrap()  # check
    #     self.set(i, b"")
    #
    # def get_index_with_attributes(self) -> Iterator[tuple[int, cdt.CommonDataType | None]]:
    #     """ if by initiation order is True then need override method for concrete class"""
    #     return iter(zip(range(1, self.get_attr_length()+1), self._encodings))
    #
    # def iter_ael_with_encoding(self) -> Iterator[tuple[ICAElement, Encoding]]:
    #     """iterator of Attribute element with it encodings"""
    #     return iter(zip(self.A_ELEMENTS, self._encodings[1:]))
    #
    # def get_attr_length(self) -> int:
    #     """common attributes amount"""
    #     return len(self.A_ELEMENTS)+1
    #
    def __lt__(self, other: Self) -> bool:
        return self.obis < other.obis

    def __str__(self) -> str:
        return f"{self.__class__.__name__} v{self.VERSION} {".".join(map(str, self.obis))}"

    def get_attr_descriptor(self,
                            i: int,
                            with_selection: bool = False) -> ut.CosemAttributeDescriptor:
        """ return AttributeDescriptor without selection """
        return ut.CosemAttributeDescriptor((
            self.CLASS_ID,
            ut.CosemObjectInstanceId(self.obis),
            ut.CosemObjectAttributeId(i)))

    def get_meth_descriptor(self, i: int) -> ut.CosemMethodDescriptor:
        """ TODO """
        return ut.CosemMethodDescriptor((
            self.CLASS_ID,
            ut.CosemObjectInstanceId(self.obis),
            ut.CosemObjectMethodId(i)))

    def __hash__(self):
        return hash(self.obis)

    @deprecated("use <Collection.get> or <Client.get>")
    def get_value(self, par: bytes) -> cdt.CommonDataType:
        ret = self.get_attr(par[0])
        for i in par[1:]:
            ret = ret[i]
        return ret

    @deprecated("use <Collection.get> or <Client.get>")
    def get_values(self, par: bytes) -> list[cdt.CommonDataType]:
        ret = [self.get_attr(par[0])]
        for i in par[1:]:
            ret.append(ret[-1][i])
        return ret


class ICAuto(IC):
    """IC Automatic attribute Property"""
    __slots__ = ("obis", )

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        for element in cls.A_ELEMENTS:
            cls._create_property_for_element(element)
        for element in cls.M_ELEMENTS:
            cls._create_property_for_element(element)

    @classmethod
    def _create_property_for_element[T: Attr | Meth](cls, element: ICElement) -> None:
        def getter(self) -> T:
            return pack_attr(self.obis, attr_index)

        attr_index = element.i
        prop = property(getter)
        setattr(cls, element.NAME, prop)


__all__ = (
    "DataType",
)

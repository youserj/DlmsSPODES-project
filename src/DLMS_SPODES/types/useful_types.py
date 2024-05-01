from functools import lru_cache
from abc import ABC, abstractmethod
from typing import Type, Any, Callable, Self, TypeAlias
from struct import pack
from dataclasses import dataclass, astuple, asdict, field, fields
from math import log
from ..types import common_data_types as cdt
from ..exceptions import DLMSException
from ..config_parser import get_values


class UserfulTypesException(DLMSException):
    """override DLMSException"""


BuildIn: TypeAlias = int | bytes


def encode_length(length: int) -> bytes:
    """ convert int to ASN.1 format """
    if length < 0x80:
        return length.to_bytes(1, "big")
    elif length < 0x1_00:
        return pack("BB", 0x81, length)
    elif length < 0x1_00_00:
        return pack(">BH", 0x82, length)
    elif length < 0x1_00_00_00_00:
        return pack(">BL", 0x84, length)
    else:
        amount = int(log(length, 256)) + 1
        return pack('B', 0x80 + amount) + length.to_bytes(amount, byteorder='big')


def get_length_and_pdu(input_pdu: bytes) -> tuple[int, bytes]:
    """ return Tuple[length, pdu] from value by decoding according to 8.1.3 Length octets ITU-T Rec. X.690 (07/2002) """
    content_start: int = 1
    """ start contents index without length """
    try:
        define_length = input_pdu[0]
    except IndexError:
        raise ValueError('in try getting length, got empty value')
    if bool(define_length & 0b10000000):
        content_start += define_length - 0x80
        length = int.from_bytes(input_pdu[1:content_start], 'big')
    else:
        length = define_length
    pdu = input_pdu[content_start:]
    return length, pdu


class UT(ABC):
    value: Any

    @abstractmethod
    def __init__(self, value: Any):
        """constructor from PYTHON builtin"""

    @property
    @abstractmethod
    def contents(self) -> bytes:
        """return contents"""

    @classmethod
    @abstractmethod
    def from_str(cls, value: str) -> Self:
        """constructor from python string"""

    @abstractmethod
    def __str__(self):
        """string representation"""


def get_instance_and_context(meta: Type[UT], value: bytes) -> tuple[UT, bytes]:
    instance = meta(value)
    return instance, value[len(instance.contents):]


@dataclass
class Sequence(UT, ABC):
    """ TODO: """

    def __init__(self, *args):
        raise ValueError("not implement")

    @property
    def contents(self):
        data = bytearray()
        for it in astuple(self, tuple_factory=iter):
            data.extend(it.contents)
        return bytes(data)

    @classmethod
    def from_contents(cls, value: bytes | bytearray) -> Self:
        values = list()
        for f in fields(cls):
            new, value = get_instance_and_context(f.type, value)
            values.append(new)
            if not len(value):
                break
        return cls(*values)

    def __str__(self):
        return str(asdict(self))

    @classmethod
    def from_str(cls, value: str) -> Self:
        raise ValueError("not implementation")

    # def __repr__(self):
    #     return F'{self.__class__.__name__}(({(", ".join(map(str, self.values)))}))'

    def __len__(self):
        return len(astuple(self))

    @property
    def NAME(self) -> str:
        return F'{self.__class__.__name__}[{len(self)}]'


class ConstSizeMixin(ABC):
    value: bytes

    def __init__(self, value: bytes):
        if len(value) == self.SIZE():
            super().__init__(value)
        else:
            raise ValueError(F"for init {self.__class__.__name__} got length value: {len(value)}, expected {self.SIZE()}")

    @property
    def contents(self) -> bytes:
        return self.value

    @classmethod
    def from_contents(cls, value: bytes) -> Self:
        return cls(value[:cls.SIZE()])

    @classmethod
    @abstractmethod
    def SIZE(cls) -> int:
        """length value constant"""


class OctetString(UT):
    """ An ordered sequence of octets (8 bit bytes) """
    value: bytes

    def __init__(self, value: bytes):
        length, pdu = get_length_and_pdu(value)
        if length <= len(pdu):
            self.value = pdu[:length]
        else:
            raise ValueError(F"for {self.__class__.__name__} got {length=}, but content length only: {len(pdu)}")

    @classmethod
    def from_contents(cls, value: bytes) -> Self:
        length, pdu = get_length_and_pdu(value)
        if length <= len(pdu):
            return cls(pdu[:length])
        else:
            raise ValueError(F"for {cls.__name__} got {length=}, but content length only: {len(pdu)}")

    @property
    def contents(self) -> bytes:
        return encode_length(len(self)) + self.value

    @classmethod
    def from_str(cls, value: str) -> Self:
        """ input as hex code """
        return cls(value.encode("utf-8"))

    def __str__(self):
        return self.value.hex(' ')

    def __repr__(self):
        return F"{self.__class__.__name__}({self.value})"

    def __len__(self):
        return len(self.value)

    def __getitem__(self, item):
        return self.value[item]

    # TODO: maybe remove as redundante?
    def to_str(self, encoding: str = 'utf-8') -> str:
        """ decode to cp1251 by default, replace to '?' if unsupported """
        temp = list()
        for i in self.value:
            temp.append(i if i > 32 else 63)
        return bytes(temp).decode(encoding)

    def __bytes__(self):
        return self.value


class OctetString4(ConstSizeMixin, OctetString):
    @classmethod
    def SIZE(cls) -> int:
        return 4


class OctetString5(ConstSizeMixin, OctetString):
    @classmethod
    def SIZE(cls) -> int:
        return 5


class OctetString6(ConstSizeMixin, OctetString):
    @classmethod
    def SIZE(cls) -> int:
        return 5


class OctetString8(ConstSizeMixin, OctetString):
    @classmethod
    def SIZE(cls) -> int:
        return 8


class OctetString12(ConstSizeMixin, OctetString):
    @classmethod
    def SIZE(cls) -> int:
        return 12


class VisibleString(UT):
    """ An ordered sequence of octets (7 bit bytes) """
    value: str

    def __init__(self, value: str = ""):
        self.value = value
        self.value.encode("ascii")  # validator

    @classmethod
    def from_contents(cls, value: bytes) -> Self:
        length, pdu = cdt.get_length_and_pdu(value)
        if length <= len(pdu):
            return cls(pdu[:length].decode("ascii"))
        else:
            raise ValueError(F"for {cls.__name__} got {length=}, but content length only: {len(pdu)}")

    @property
    def contents(self) -> bytes:
        return encode_length(len(self)) + self.value.encode("ascii")

    @classmethod
    def from_str(cls, value: str) -> Self:
        """ input as hex code """
        return cls(value)

    def __str__(self):
        return self.value

    def __repr__(self):
        return F"{self.__class__.__name__}({self.value})"

    def __len__(self):
        return len(self.value)

    def __getitem__(self, item):
        return self.value[item]


class UTF8String(UT):
    """UTF8String"""
    value: str

    def __init__(self, value: str = ""):
        self.value = value
        self.value.encode("utf-8")  # validator

    @classmethod
    def from_contents(cls, value: bytes) -> Self:
        length, pdu = cdt.get_length_and_pdu(value)
        if length <= len(pdu):
            return cls(pdu[:length].decode("utf-8"))
        else:
            raise ValueError(F"for {cls.__name__} got {length=}, but content length only: {len(pdu)}")

    @property
    def contents(self) -> bytes:
        encoding = self.value.encode("utf-8")
        return encode_length(len(encoding)) + encoding

    @classmethod
    def from_str(cls, value: str) -> Self:
        """ input as hex code """
        return cls(value)

    def __str__(self):
        return self.value

    def __repr__(self):
        return F"{self.__class__.__name__}({self.value})"

    def __len__(self):
        return len(self.value)

    def __getitem__(self, item):
        return self.value[item]


@dataclass(frozen=True)
class SequenceElement:
    NAME: str
    TYPE: Type[UT | Sequence | cdt.CommonDataType]

    def __str__(self):
        return F'{self.NAME}: {self.TYPE.__name__}'


@dataclass
class ChoiceElement:
    name: str
    tag: int
    type: Type[UT]


class Choice(UT):
    """CHOICE"""
    value: UT
    ELEMENTS: tuple[ChoiceElement, ...]

    def __init__(self, value: UT):
        self.value = value
        self._get_element_by_type(value.__class__)  # validation

    @classmethod
    def from_contents(cls, value: bytes) -> Self:
        if len(value) == 0:
            raise ValueError(F"for {cls.__name__} got contents length = 0, expected 1")  # todo: a lot of copypast this expression
        el = cls._get_element_by_tag(value[0])
        return cls(el.type.from_contents(value[1:]))

    @property
    def contents(self) -> bytes:
        return pack(F"B{len(self.value.contents)}s",
                    self._get_element_by_type(self.value.__class__).tag,
                    self.value.contents)

    def __str__(self):
        el = self._get_element_by_type(self.value.__class__)
        return F'{self.__class__.__name__}: {el.name} [{el.tag}] {self.value}'

    @classmethod
    def from_str(cls, value: str) -> Self:
        tag, value2 = value.split(sep=" ")
        tag: str
        if not tag.isdigit():
            raise ValueError(F"in {value}, got {tag=}, expected is digit")
        return cls(cls._get_element_by_tag(int(tag)).type.from_str(value2))

    @classmethod
    def _get_element_by_type(cls, value: Type[UT]) -> ChoiceElement:
        for el in cls.ELEMENTS:
            if issubclass(value, el.type):
                return el
        else:
            raise ValueError(F"not find type: {value} in {cls.__name__}")

    @classmethod
    def _get_element_by_tag(cls, value: int) -> ChoiceElement:
        for el in cls.ELEMENTS:
            if value == el.tag:
                return el
        else:
            raise ValueError(F"not find tag: {value} in {cls.__name__}")

    def __eq__(self, other: Self):
        if self._get_element_by_type(self.value.__class__) == other._get_element_by_type(other.value.__class__) and self.value.contents == other.value.contents:
            return True
        else:
            return False


class CHOICE(ABC):
    """ TODO: with cdt.CHOICE """
    ELEMENTS: dict[int, SequenceElement | dict[int, SequenceElement]]

    def __getitem__(self, item: int) -> SequenceElement:
        return self.ELEMENTS[item]

    @property
    def NAME(self) -> str:
        return F'CHOICE[{len(self)}]'

    def __len__(self):
        return len(self.ELEMENTS)

    def is_key(self, value: int) -> bool:
        return value in self.ELEMENTS.keys()

    def __call__(self,
                 value: bytes | int = None,
                 force: bool = False) -> cdt.CommonDataType:
        """ get instance from encoding or tag(with default value). For CommonDataType only """
        try:
            match value:
                case bytes() as encoding:
                    match self.ELEMENTS[encoding[0]]:
                        case SequenceElement() as el: return el.TYPE(encoding)
                        case dict() as ch:
                            if encoding[1] in ch.keys():
                                return ch[encoding[1]].TYPE(encoding)  # use for choice cst.Time | DateTime | Date as OctetString
                            else:
                                raise ValueError(F"got type with tag: {encoding[0]} and length: {encoding[1]}, expected length {tuple(ch.keys())}")
                        case err:                     raise ValueError(F"got {err.__name__}, expected {SequenceElement.__name__} or {dict.__name__}")
                case int() if force:                  return cdt.get_common_data_type_from(value.to_bytes(1, "big"))()
                case int() as tag:                    return self.ELEMENTS[tag].TYPE()
                case None:                            return tuple(self.ELEMENTS.values())[0].TYPE()
                case error:                           raise ValueError(F'Unknown value type {error}')
        except KeyError as e:
            raise UserfulTypesException(F"for {self.__class__.__name__} got {cdt.CommonDataType.__name__}: {cdt.TAG(e.args[0].to_bytes(1))}; expected: {', '.join(map(lambda el: el.NAME, self.ELEMENTS.values()))}")

    def __get_elements(self) -> list[SequenceElement]:
        """all elements with nested values"""
        elements = list()
        for el in self.ELEMENTS.values():
            match el:
                case SequenceElement():
                    elements.append(el)
                case dict() as dict_el:
                    elements.extend(dict_el.values())
                case err:
                    raise ValueError(F"unknown CHOICE element type {err}")
        return elements

    def get_types(self) -> tuple[Type[cdt.CommonDataType]]:
        """ Use in setter attribute.value for validate """
        return tuple((seq_el.TYPE for seq_el in self.__get_elements()))

    def __str__(self):
        return F'{CHOICE}: {", ".join((el.NAME for el in self.__get_elements()))}'


class SEQUENCE_OF(ABC):
    type: None
    values: list


class Null(UT):
    __slots__ = tuple()

    def __init__(self):
        pass

    @classmethod
    def from_contents(cls, value: bytes) -> Self:
        return NULL

    @property
    def contents(self):
        return b''

    @classmethod
    def from_str(cls, value: str):
        return NULL

    def __str__(self):
        return self.__class__.__name__


NULL = Null()


class BOOLEAN(UT):
    value: bool
    __slots__ = ("value",)

    def __init__(self, value: bool = True):
        self.value = value

    @classmethod
    def from_contents(cls, value: bytes) -> Self:
        if len(value) == 0:
            raise ValueError(F"for {cls.__name__} got contents length = 0, expected 1")
        elif value[0] == 0:
            return FALSE
        else:
            return TRUE

    @property
    def contents(self):
        return b'\x01' if self.value else b'\x00'

    @classmethod
    def from_str(cls, value: str):
        match value:
            case "0", "False":
                return FALSE
            case "1", "True":
                return TRUE
            case _:
                raise ValueError(F"for {cls.__name__}.from_str got unknown {value=}")

    def __str__(self):
        return str(self.value)

    @classmethod
    def from_int(cls, value: int):
        return FALSE if value == 0 else TRUE

    def __bool__(self):
        return self.value

    def __int__(self):
        return 1 if self.value else 0

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.contents == other.contents:
            return True
        else:
            return False


FALSE = BOOLEAN(False)
TRUE = BOOLEAN(True)


class BitString(UT):
    """ An ordered sequence of boolean values """
    value: list[int]
    SIZE: int = -1

    def __init__(self, value: list[int]):
        self.value = value

    @property
    def contents(self) -> bytes:
        a = "".join(map(str, self.value))
        value = a + '0' * ((8 - len(self.value)) % 8)
        x = bytes((int(value[count:(count + 8)], base=2) for count in range(0, len(self.value), 8)))
        return encode_length(len(self)) + x

    @classmethod
    def from_contents(cls, value: bytes) -> Self:
        length, pdu = get_length_and_pdu(value)
        if len(pdu)*8 < length:
            raise ValueError(F"in {cls.__name__} for decode: {value=} not enough value")
        ret = list()
        for char in pdu[:int(length/8)+1]:
            ret.extend([(char >> it) & 0b00000001 for it in range(7, -1, -1)])
        return cls(ret[:length])

    @classmethod
    def from_str(cls, value: str) -> Self:
        return cls(list(map(int, value)))

    def __str__(self):
        return ''.join(map(str, self.value))

    def __setitem__(self, key: int, value: int | bool):
        self.value[key] = value

    def inverse(self, index: int):
        """ inverse one bit by index"""
        self.value[index] = not self.value[index]

    # def __lshift__(self, other):
    #     for i in range(other):
    #         tmp: list[int] = self.decode()
    #         tmp.append(tmp.pop(0))
    #         self.set(''.join(map(str, tmp)))
    #
    # def __rshift__(self, other):
    #     for i in range(other):
    #         tmp: list[int] = self.decode()
    #         tmp.insert(0, tmp.pop())
    #         self.set(''.join(map(str, tmp)))

    def __len__(self):
        return len(self.value)

    def clear(self):
        """set all bits as 0"""
        for i in range(len(self)):
            self.value[i] = 0


class SequenceOptional(UT, ABC):
    """for used in SEQUENCE now"""
    TYPE: Type[UT]
    value: UT
    __slots__ = ("value",)

    def __init__(self, value: UT = None):
        if isinstance(value, self.TYPE):
            self.value = value
        else:
            self.value = NULL

    @classmethod
    def from_contents(cls, value: bytes):
        if len(value) == 0:
            raise ValueError(F"for {cls.__name__} got contents length = 0, expected at least 1")
        elif value[0] == 0:
            return cls(None)
        else:
            return cls(cls.TYPE.from_contents(value[1:]))

    @property
    def contents(self):
        if self.value is NULL:
            return FALSE.contents
        else:
            return TRUE.contents + self.value.contents

    def __str__(self):
        return str(self.value)

    @classmethod
    def from_str(cls, value: str) -> Self:
        raise RuntimeError(F"Not implementation for {cls.__name__}")


def OPTIONAL(value: Type[UT]) -> Type[SequenceOptional]:
    class Optional(SequenceOptional):
        TYPE = value

    return Optional


class INTEGER(ABC):
    """ Default value is 0 """
    SIGNED: bool
    LENGTH: int
    value: int

    def __init__(self, value: int):
        self.value = value
        assert self.contents  # simple validator

    @classmethod
    def from_contents(cls, value: bytes):
        return cls(int.from_bytes(value[0:1], "big", signed=cls.SIGNED))

    @property
    def contents(self) -> bytes:
        return self.value.to_bytes(self.LENGTH, "big", signed=self.SIGNED)

    @classmethod
    def from_str(cls, value: str):
        return cls(int(value))

    def __str__(self):
        return str(self.value)

    def __int__(self):
        return self.value

    def __repr__(self):
        return F'{self.__class__.__name__}({self.value})'

    def __gt__(self, other: Self):
        match other:
            case INTEGER(): return self.value > other.value
            case _:          raise TypeError(F'Compare type is {other.__class__}, expected Digital')

    def __len__(self) -> int:
        return self.LENGTH

    def __hash__(self):
        return self.value

    def __eq__(self, other: Self):
        return self.contents == other.contents


class Integer8(INTEGER, UT):
    """ INTEGER(-127…128) """
    LENGTH = 1
    SIGNED = True


class Integer16(INTEGER, UT):
    """ INTEGER(-32 768...32 767) """
    LENGTH = 2
    SIGNED = True


class Integer32(INTEGER, UT):
    """ INTEGER(-2 147 483 648...2 147 483 647) """
    LENGTH = 4
    SIGNED = True


class Integer64(INTEGER, UT):
    """ INTEGER(-2^63...2^63-1) """
    LENGTH = 8
    SIGNED = True


class Unsigned8(INTEGER, UT):
    """ INTEGER(0...255) """
    LENGTH = 1
    SIGNED = False
    # __match_args__ = ('contents',)


class Unsigned16(INTEGER, UT):
    """ INTEGER(0...65 535) """
    LENGTH = 2
    SIGNED = False


class Unsigned32(INTEGER, UT):
    """ INTEGER(0...4 294 967 295) """
    LENGTH = 4
    SIGNED = False


class Unsigned64(INTEGER, UT):
    """ INTEGER(0...264-1) """
    LENGTH = 8
    SIGNED = False


class AccessSelectionParameters(Unsigned8):
    """ Unsigned8(0..1) """

    def __init__(self, value: int | str | Unsigned8 = 1):
        super(AccessSelectionParameters, self).__init__(value)
        if int(self) > 1 or int(self) < 0:
            raise ValueError(F'The {self.__class__.__name__} got {self}, expected 0..1')


class Data(CHOICE, ABC):
    ELEMENTS = {
        0: SequenceElement('null-data', Null),
        1: SequenceElement('array', Sequence),
        15: SequenceElement('integer', Integer8),
    }


class SelectiveAccessDescriptor(Sequence, ABC):
    """ Selective access specification always starts with an access selector, followed by an access-specific access parameter list.
    Specified IS/IEC 62056-53 : 2006, 7.4.1.6 Selective access """
    access_selector: Unsigned8
    access_parameters: cdt.CommonDataType
    ELEMENTS: tuple[SequenceElement, SequenceElement]

    def __init__(self, value: tuple | bytes | None = None):
        super(SelectiveAccessDescriptor, self).__init__(value)
        self.access_selector.cb_post_set = self.__validate_selector

    @property
    @abstractmethod
    def ELEMENTS(self) -> tuple[SequenceElement, SequenceElement]:
        """ return elements """

    def from_default(self):
        self.values[0] = self.ELEMENTS[0].TYPE()
        self.values[1] = self.ELEMENTS[1].TYPE.ELEMENTS[int(self.access_selector)].TYPE()

    def from_bytes(self, value: bytes | bytearray):
        self.values[0], value = get_instance_and_context(self.ELEMENTS[0].TYPE, value)
        self.values[1] = self.ELEMENTS[1].TYPE.ELEMENTS[int(self.access_selector)].TYPE(value)

    def from_tuple(self, value: tuple | list):
        self.values[0] = self.ELEMENTS[0].TYPE(value[0])
        self.values[1] = self.ELEMENTS[1].TYPE.ELEMENTS[int(self.access_selector)].TYPE(value[1])

    @property
    def contents(self) -> bytes:
        return self.access_selector.contents+self.access_parameters.encoding

    def __validate_selector(self):
        self.values[1] = self.ELEMENTS[1].TYPE.ELEMENTS[int(self.access_selector)].TYPE()
        print('change sel')

    def set_selector(self, index: int, value=None):
        """ set selector value from int type """
        self.access_selector.set_contents_from(index)
        if value:
            self.access_parameters.set(value)


# class CosemAttributeDescriptorWithSelection(Sequence):
#     cosem_attribute_descriptor: CosemAttributeDescriptor
#     access_selection: SelectiveAccessDescriptor
#     ELEMENTS: tuple[CosemAttributeDescriptor, SequenceElement]
#
#     def __init__(self, value: bytes | tuple | list = None):
#         super(CosemAttributeDescriptorWithSelection, self).__init__(value)
#         self.cosem_attribute_descriptor.access_selection_parameters.set_contents_from(1)
#
#     @property
#     @abstractmethod
#     def ELEMENTS(self) -> tuple[SequenceElement, SequenceElement]:
#         """ return elements. Need initiate in subclass """


####
@dataclass
class ServiceClass:
    value: bool

    def __str__(self):
        return "Confirmed" if self.value else "Unconfirmed"

    def __int__(self):
        return 0b0100_0000 if self.value else 0


@dataclass
class Priority:
    value: bool

    def __str__(self):
        return "High" if self.value else "Normal"

    def __int__(self):
        return 0b1000_0000 if self.value else 0


@dataclass
class InvokeIdAndPriority(Unsigned8):
    invoke_id: int
    service_class: ServiceClass
    priority: Priority

    @classmethod
    def from_contents(cls, value: bytes) -> Self:
        if cls.LENGTH > len(value):  # todo: copypast from DigitalMixin
            raise ValueError(F"for {cls.__name__} got content length={len(value)}, expected at least {cls.LENGTH}")
        else:
            return cls(
                invoke_id=value[0] & 0b0000_1111,
                service_class=ServiceClass(bool(value[0] & 0b0100_0000)),
                priority=Priority(bool(value[0] & 0b0100_0000)))

    @property
    def contents(self) -> bytes:
        return int(self).to_bytes(1, "big")

    def __str__(self):
        return F"{self.priority} | {self.service_class} | {self.invoke_id}"

    @classmethod
    def from_str(cls, value: str):
        raise RuntimeError(F"for {cls.__name__} not implemented method <from_str>")

    def __int__(self):
        return self.invoke_id + int(self.service_class) + int(self.priority)


class CosemClassId(Unsigned16):
    """COSEMpdu-Gb83.asn"""

    def __str__(self):
        if _class_names:
            return _class_names.get(self, repr(self))
        else:
            return repr(self)

    def __repr__(self):
        return F"{self.__class__.__name__}({int(self)})"


_class_names = {CosemClassId(value=int(k)): v for k, v in class_names.items()} if (class_names := get_values("DLMS", "class_name")) else None
"""use for string representation CosemClassId"""


class CosemObjectInstanceId(ConstSizeMixin, OctetString):
    """Cosem-Object-Instance-Id"""
    @classmethod
    def SIZE(cls) -> int:
        return 6

    def __str__(self):
        return '.'.join(map(str, self.value))

    @classmethod
    def from_str(cls, value: str) -> Self:
        """ create logical_name: octet_string from string type ddd.ddd.ddd.ddd.ddd.ddd, ex.: 0.0.1.0.0.255 """
        raw_value = bytes()
        for typecast, separator in zip((cls.__from_group_A, )*5+(cls.__from_group_F, ), ('.', '.', '.', '.', '.', ' ')):
            try:
                element, value = value.split(separator, 1)
            except ValueError:
                element, value = value, ''
            raw_value += typecast(element)
        return cls(raw_value)

    @staticmethod
    def __from_group_A(value: str) -> bytes:
        if isinstance(value, str):
            if value == '':
                return b'\x00'
            try:
                return int(value).to_bytes(1, 'big')
            except OverflowError:
                raise ValueError(F'Int too big to convert {value}')
        else:
            raise TypeError(F'Unsupported type validation from string, got {value.__class__}')

    @staticmethod
    def __from_group_F(value: str) -> bytes:
        if isinstance(value, str):
            if value == '':
                return b'\xff'
            try:
                return int(value).to_bytes(1, 'big')
            except OverflowError:
                raise ValueError(F'Int too big to convert {value}')
        else:
            raise TypeError(F'Unsupported type validation from string, got {value.__class__}')


class CosemObjectAttributeId(Integer8):
    """Cosem-Object-Attribute-Id"""


class CosemObjectMethodId(Integer8):
    """Cosem-Object-Method-Id"""


@dataclass
class SelectiveAccessDescriptor(Sequence):
    """COSEMpdu_GB83 Selective-Access-Descriptor"""
    access_selector: Unsigned8
    access_parameters: Data


@dataclass
class CosemAttributeDescriptor(Sequence):
    """COSEMpdu_GB83 Cosem-Attribute-Descriptor"""
    class_id: CosemClassId
    instance_id: CosemObjectInstanceId
    attribute_id: CosemObjectAttributeId


@dataclass
class CosemMethodDescriptor(Sequence):
    class_id: CosemClassId
    instance_id: CosemObjectInstanceId
    method_id: CosemObjectMethodId


class Data(Choice):
    ELEMENTS = (
        ChoiceElement(name="null-data",             tag=0,  type=Null),
        # ChoiceElement(name="array",               tag=1, type=...),
        # ChoiceElement(name="structure",           tag=2, type=...),
        ChoiceElement(name="boolean",               tag=3,  type=BOOLEAN),
        ChoiceElement(name="bit-string",            tag=4,  type=BitString),
        ChoiceElement(name="double-long",           tag=5,  type=Integer32),
        ChoiceElement(name="double-long-unsigned",  tag=6,  type=Unsigned32),
        ChoiceElement(name="octet-string", tag=9, type=OctetString),
        ChoiceElement(name="visible-string",        tag=10, type=VisibleString),
        ChoiceElement(name="utf8-string",           tag=12, type=UTF8String),
        ChoiceElement(name="bcd",                   tag=13, type=Integer8),
        ChoiceElement(name="integer",               tag=15, type=Integer8),
        ChoiceElement(name="long",                  tag=16, type=Integer16),
        ChoiceElement(name="unsigned",              tag=17, type=Unsigned8),
        ChoiceElement(name="long-unsigned",         tag=18, type=Unsigned16),
        # ChoiceElement(name="compact-array",         tag=19, type=...),
        ChoiceElement(name="long64",                tag=20, type=Integer64),
        ChoiceElement(name="long64-unsigned",       tag=21, type=Unsigned64),
        ChoiceElement(name="enum",                  tag=22, type=Unsigned8),
        # ChoiceElement(name="float32",               tag=23, IMPLICIT   OCTET STRING (SIZE(4)),
        # ChoiceElement(name="float64",               tag=24,  IMPLICIT   OCTET STRING (SIZE(8)),
        # ChoiceElement(name="date-time",             tag=25,  IMPLICIT   OCTET STRING (SIZE(12)),
        # ChoiceElement(name="date",                  tag=26,  IMPLICIT   OCTET STRING (SIZE(5)),
        # ChoiceElement(name="time",                  tag=27,  type=OCTET_STRING(4)),
        ChoiceElement(name="dont-care",             tag=255, type=Null)
    )

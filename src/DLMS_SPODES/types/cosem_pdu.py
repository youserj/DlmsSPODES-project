from abc import ABC, abstractmethod
from typing import Self, Type, Iterable
from dataclasses import dataclass
from struct import pack, pack_into, Struct
from math import log
from .byte_buffer import ByteBuffer


_length1 = Struct("> B B")
_length2 = Struct("> B H")
_length4 = Struct("> B L")


class Buffer(ByteBuffer):
    """Cosem pdu buffer implementation"""
    def get_length(self) -> int:
        """ return common element length from buffer, with increasing by decoding according to 8.1.3 Length octets ITU-T Rec. X.690 (07/2002) """
        define_length = self.get_uint8()
        if define_length & 0b10000000:
            return self.get_uint(define_length >> 1)
        else:
            return define_length

    def read_by_length(self, length: int = None) -> memoryview:
        """with check length"""
        return self.read(self.get_length())

    def put_length(self, length: int) -> int:
        """ put length to buffer, increase position"""
        if length < 0x80:
            return self.put_int(length)
        elif length < 0x1_00:
            _length1.pack_into(self.buf, 0,
                               0x81, length)
            return 2
        elif length < 0x1_00_00:
            _length2.pack_into(self.buf, 0,
                               0x82, length)
            return 3
        elif length < 0x1_00_00_00_00:
            _length4.pack_into(self.buf, 0,
                               0x84, length)
            return 5
        else:
            amount = int(log(length, 256)) + 1
            ret: int = self.put_int(0x80 + amount)
            length: bytes = length.to_bytes(amount, byteorder='big')
            return ret + self.write(length)

    def write_with_length(self, value: memoryview) -> int:
        """ write to buffer, increase position"""
        ret: int = self.put_length(len(value))
        return ret + self.write(value)


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


class UT(ABC):

    @abstractmethod
    def __init__(self, value):
        """self.contents = contents"""

    # def validate(self):
    #     if not (len(self) == -1 or len(self) == len(self.contents)):
    #         raise ValueError(F"for create {self.__class__.__name__} has contents with length {len(self.contents)}, expected {len(self)}")

    @classmethod
    @abstractmethod
    def __len__(cls) -> int:
        """return size in bytes"""

    @classmethod
    @abstractmethod
    def get(cls, buf: Buffer) -> Self:
        """"""

    @abstractmethod
    def put(self, buf: Buffer) -> int:
        """"""

    @classmethod
    @abstractmethod
    def from_str(cls, value: str) -> Self:
        """constructor from python string"""

    @classmethod
    @abstractmethod
    def default(cls) -> Self:
        """return cls(memoryview(bytes(cls.__len__())))"""

    @abstractmethod
    def __str__(self):
        """string representation"""

    @abstractmethod
    def __bytes__(self):
        """"""

    @abstractmethod
    def __getitem__(self, item):
        """"""


class Simple(UT, ABC):
    contents: memoryview

    def __init__(self, value: memoryview):
        self.contents = value

    def validate(self):
        if not (len(self) == -1 or len(self) == len(self.contents)):
            raise ValueError(F"for create {self.__class__.__name__} has contents with length {len(self.contents)}, expected {len(self)}")

    @classmethod
    @abstractmethod
    def __len__(cls) -> int:
        """return necessary size"""

    @classmethod
    def get(cls, buf: Buffer) -> Self:
        return cls(buf.read(cls.__len__()))

    def put(self, buf: Buffer) -> int:
        return buf.write(self.contents)

    @classmethod
    @abstractmethod
    def from_str(cls, value: str) -> Self:
        """constructor from python string"""

    @classmethod
    def default(cls) -> Self:
        return cls(memoryview(bytes(cls.__len__())))

    @abstractmethod
    def __str__(self):
        """string representation"""

    def __bytes__(self):
        return bytes(self.contents)

    def __getitem__(self, item):
        return self.contents[item]


class VarSizeMixin(Simple, ABC):
    def __len__(self) -> int:
        return len(self.contents)

    @classmethod
    def get(cls, buf: Buffer) -> Self:
        return cls(buf.read_by_length())

    def put(self, buf: Buffer) -> int:
        return buf.write_with_length(self.contents)

    @classmethod
    def default(cls) -> Self:
        return cls(memoryview(bytearray()))


class NULL(Simple):
    @classmethod
    def __len__(cls) -> int:
        return 0

    @classmethod
    def from_str(cls, value: str):
        return NULL_

    def __str__(self):
        return self.__class__.__name__


NULL_ = NULL(memoryview(b''))
"""static object for NULL"""


class BOOLEAN(Simple):
    @classmethod
    def __len__(cls) -> int:
        return 1

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
        return str(bool(self))

    @classmethod
    def from_int(cls, value: int):
        return FALSE if value == 0 else TRUE

    def __bool__(self):
        return bool(int(self))

    def __int__(self):
        return self.contents[0]

    def __eq__(self, other):
        if isinstance(other, self.__class__) and self.contents == other.contents:
            return True
        else:
            return False


FALSE = BOOLEAN(memoryview(b'\x00'))
"""allocated FALSE"""
TRUE = BOOLEAN(memoryview(b'\x01'))
"""allocated TRUE"""


class INTEGER(Simple, ABC):
    """ Default value is 0 """

    @classmethod
    @abstractmethod
    def SIGNED(cls) -> bool:
        """return signed flag"""

    @classmethod
    def from_int(cls, value: int) -> Self:
        return cls(memoryview(value.to_bytes(cls.__len__(), "big", signed=cls.SIGNED())))

    @classmethod
    def from_str(cls, value: str):
        return cls.from_int(int(value))

    def __str__(self):
        return str(int(self))

    def __int__(self):
        return int.from_bytes(self.contents, signed=self.SIGNED())

    def __gt__(self, other: Self):
        match other:
            case INTEGER(): return self.contents > other.value
            case _:          raise TypeError(F'Compare type is {other.__class__}, expected Digital')

    def __hash__(self):
        return int(self)

    def __eq__(self, other: Self):
        return self.contents == other.contents


class Integer8(INTEGER, Simple):
    """ INTEGER(-127…128) """

    @classmethod
    def __len__(cls) -> int:
        return 1

    @classmethod
    def SIGNED(cls) -> bool:
        return True


class Integer16(INTEGER, Simple):
    """ INTEGER(-32 768...32 767) """
    @classmethod
    def __len__(cls) -> int:
        return 2

    @classmethod
    def SIGNED(cls) -> bool:
        return True


class Integer32(INTEGER, Simple):
    """ INTEGER(-2 147 483 648...2 147 483 647) """
    @classmethod
    def __len__(cls) -> int:
        return 4

    @classmethod
    def SIGNED(cls) -> bool:
        return True


class Integer64(INTEGER, Simple):
    """ INTEGER(-2^63...2^63-1) """
    @classmethod
    def __len__(cls) -> int:
        return 8

    @classmethod
    def SIGNED(cls) -> bool:
        return True


class Unsigned8(INTEGER, Simple):
    """ INTEGER(0...255) """
    @classmethod
    def __len__(cls) -> int:
        return 1

    @classmethod
    def SIGNED(cls) -> bool:
        return False


class Unsigned16(INTEGER, Simple):
    """ INTEGER(0...65 535) """
    @classmethod
    def __len__(cls) -> int:
        return 2

    @classmethod
    def SIGNED(cls) -> bool:
        return False


class Unsigned32(INTEGER, Simple):
    """ INTEGER(0...4 294 967 295) """
    @classmethod
    def __len__(cls) -> int:
        return 4

    @classmethod
    def SIGNED(cls) -> bool:
        return False


class Unsigned64(INTEGER, Simple):
    """ INTEGER(0...264-1) """
    @classmethod
    def __len__(cls) -> int:
        return 8

    @classmethod
    def SIGNED(cls) -> bool:
        return False


class StringMixin(Simple, ABC):
    """ An ordered sequence of octets (8 bit bytes) """
    @classmethod
    def from_str(cls, value: str) -> Self:
        """ input as hex code """
        return cls(memoryview(value.encode("utf-8")))

    def __str__(self):
        return self.contents.hex(' ')


class OctetString(StringMixin, VarSizeMixin, Simple):
    """ An ordered sequence of octets (8 bit bytes) """


class OctetString4(StringMixin, Simple):
    @classmethod
    def __len__(cls) -> int:
        return 4


class OctetString5(StringMixin, Simple):
    @classmethod
    def __len__(cls) -> int:
        return 5


class OctetString6(StringMixin, Simple):
    @classmethod
    def __len__(cls) -> int:
        return 6


class OctetString8(StringMixin, Simple):
    @classmethod
    def __len__(cls) -> int:
        return 8


class OctetString12(StringMixin, Simple):
    @classmethod
    def __len__(cls) -> int:
        return 12


class Sequence(UT):
    """ TODO: """
    values: tuple[UT, ...]

    def __init__(self, value: tuple[UT, ...]):
        self.values = value

    def __len__(self) -> int:
        return sum((len(it) for it in self.values))

    @property
    def _get0(self):
        return self.values[0]

    @property
    def _get1(self):
        return self.values[1]

    @property
    def _get2(self):
        return self.values[2]

    @property
    def _get3(self):
        return self.values[3]

    @property
    def _get4(self):
        return self.values[4]

    @property
    def _get5(self):
        return self.values[5]

    @property
    def _get6(self):
        return self.values[6]

    @property
    def _get7(self):
        return self.values[7]

    @property
    def _get8(self):
        return self.values[8]

    @property
    def _get9(self):
        return self.values[9]

    def __init_subclass__(cls, **kwargs):
        """link attributes with functions"""
        for (name, type_), f in zip(cls.__annotations__.items(), (cls._get0, cls._get1, cls._get2, cls._get3, cls._get4, cls._get5, cls._get6, cls._get7, cls._get8, cls._get9)):
            setattr(cls, name, f)

    @classmethod
    def get(cls, buf: Buffer) -> Self:
        ret = list()
        for el in cls.__annotations__.values():
            el: Simple
            ret.append(el.get(buf))
        return cls(tuple(ret))

    def put(self, buf: Buffer) -> int:
        """put to buffer"""
        return sum(val.put(buf) for val in self.values)

    @classmethod
    def default(cls) -> Self:
        return cls(tuple(el.default() for el in cls.__annotations__.values()))

    @classmethod
    def from_str(cls, value: str) -> Self:
        values = value.split(" ")
        return cls(tuple(el.from_str(val) for el, val in zip(cls.__annotations__.values(), values)))

    def __str__(self):
        return F"{self.__class__.__name__} {Sequence.__name__}[{len(self.__annotations__)}]"

    def __bytes__(self):
        raise ValueError("not impl")

    def __getitem__(self, item):
        return self.values[item]


class SequenceOptional(UT):
    """for used in SEQUENCE now"""
    TYPE: Type[UT]
    value: UT
    __slots__ = ("value",)

    def __init__(self, value: UT):
        self.value = value

    @classmethod
    def get(cls, buf: Buffer) -> Self:
        if buf.get_uint8() == 0:
            return cls(NULL_)
        else:
            return cls(cls.TYPE.get(buf))

    def put(self, buf: Buffer) -> int:
        if self.value is NULL_:
            return buf.put_int(0)
        else:
            buf.put_int(1)
            return self.value.put(buf) + 1

    def __str__(self):
        return str(self.value)

    @classmethod
    def from_str(cls, value: str) -> Self:
        if value == "":
            return cls(NULL_)
        else:
            return cls(cls.TYPE.from_str(value))

    @classmethod
    def default(cls) -> Self:
        return cls(NULL_)

    def __bytes__(self):
        raise ValueError("not impl")

    def __len__(self):
        return len(self.value) + 1

    def __getitem__(self, item):
        raise ValueError("not impl")


def OPTIONAL(value: Type[UT]) -> Type[SequenceOptional]:
    class Optional(SequenceOptional):
        TYPE = value

    return Optional


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

    def validation(self):
        self._get_element_by_type(self.value.__class__)

    @classmethod
    def get(cls, buf: Buffer) -> Self:
        el = cls._get_element_by_tag(buf.get_uint8())
        return cls(el.type.get(buf))

    def put(self, buf: Buffer) -> int:
        buf.put_int(self._get_element_by_type(self.value.__class__).tag)
        return 1 + self.value.put(buf)

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
        if self._get_element_by_type(self.value.__class__) == other._get_element_by_type(other.value.__class__) and self.value == other.value:
            return True
        else:
            return False

    @classmethod
    def default(cls) -> Self:
        """choice 0 tag parameter"""
        return cls(cls._get_element_by_tag(0).type.default())

    def __bytes__(self):
        buf = Buffer.allocate(len(self))
        self.put(buf)
        return bytes(buf)

    def __len__(self):
        return len(self.value) + 1

    def __getitem__(self, item):
        raise self.value[item]


class Data(Choice):
    ELEMENTS = (
        ChoiceElement("null-data",             0, NULL),
        # ChoiceElement(name="array",               tag=1, type=...),
        # ChoiceElement(name="structure",           tag=2, type=...),
        ChoiceElement("boolean",               3,  BOOLEAN),
        # ChoiceElement(name="bit-string",            4,  BitString),
        ChoiceElement("double-long",           5,  Integer32),
        ChoiceElement("double-long-unsigned",  6,  Unsigned32),
        ChoiceElement("octet-string",          9, OctetString),
        # ChoiceElement(name="visible-string",        10, VisibleString),
        # ChoiceElement(name="utf8-string",           12, UTF8String),
        ChoiceElement("bcd",                   13, Integer8),
        ChoiceElement("integer",               15, Integer8),
        ChoiceElement("long",                  16, Integer16),
        ChoiceElement("unsigned",              17, Unsigned8),
        ChoiceElement("long-unsigned",         18, Unsigned16),
        # ChoiceElement("compact-array",         19, ...),
        ChoiceElement("long64",                20, Integer64),
        ChoiceElement("long64-unsigned",       21, Unsigned64),
        ChoiceElement("enum",                  22, Unsigned8),
        ChoiceElement("float32",               23, OctetString4),
        ChoiceElement("float64",               24, OctetString8),
        ChoiceElement("date-time",             25, OctetString12),
        ChoiceElement("date",                  26, OctetString5),
        ChoiceElement("time",                  27, OctetString4),
        ChoiceElement("dont-care",             255, NULL)
    )

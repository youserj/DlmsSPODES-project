from __future__ import annotations
from functools import lru_cache
from abc import ABC, abstractmethod
from typing import Type, Any, Callable, Self
from dataclasses import dataclass, astuple, asdict, field, fields
from ..types import common_data_types as cdt
from ..exceptions import DLMSException
from ..config_parser import get_values


class UserfulTypesException(DLMSException):
    """override DLMSException"""


class UT(ABC):
    @abstractmethod
    def __init__(self, value: Any):
        """constructor from PYTHON build-in"""

    @classmethod
    @abstractmethod
    def from_contents(cls, value: bytes) -> Self:
        """constructor from bytes"""

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


class StringMixin(ABC):
    LENGTH: int | None

    def __init__(self, value: bytes | bytearray | str | int | tuple | UsefulType = None):
        match value:
            case None:                                                        self.__dict__["contents"] = bytes(self.LENGTH)
            case bytes() if self.LENGTH is None or self.LENGTH <= len(value): self.__dict__["contents"] = value[:self.LENGTH]
            # case bytes() if self.LENGTH <= len(value):                       self.contents = value[:self.LENGTH]
            case bytes():            raise ValueError(F'Length of contents for {self.__class__.__name__} must be at least {self.LENGTH}, but got {len(value)}')
            case tuple():
                if len(value) == self.LENGTH:
                    self.__dict__["contents"] = bytes(value)
                else:
                    raise ValueError(F"in {self.__class__.__name__} with {value=} got length: {len(value)}, expect {self.LENGTH}")
            case bytearray():                                                 self.__dict__["contents"] = bytes(value)  # Attention!!! changed method content getting from bytearray
            case str():                                                       self.__dict__["contents"] = self.from_str(value)
            case int():                                                       self.__dict__["contents"] = self.from_int(value)
            case UsefulType():                                                self.__dict__["contents"] = value.contents  # TODO: make right type
            case _:                                                           raise ValueError(F'Error create {self.__class__.__name__} with value {value}')

    @abstractmethod
    def __len__(self):
        """ define in subclasses """


class OctetString(UT):
    """ An ordered sequence of octets (8 bit bytes) """
    value: bytes

    def __init__(self, value: bytes = None):
        self.value = value

    @classmethod
    def from_contents(cls, value: bytes) -> Self:
        length, pdu = cdt.get_length_and_pdu(value)
        if length <= len(pdu):
            return cls(pdu[:length])
        else:
            raise ValueError(F"for {cls.__name__} got {length=}, but content length only: {len(pdu)}")

    @property
    def contents(self) -> bytes:
        return cdt.encode_length(len(self)) + self.value

    @classmethod
    def from_str(cls, value: str) -> Self:
        """ input as hex code """
        return cls(value.encode("utf-8"))

    def __str__(self):
        return self.value.hex(' ')

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


def get_instance_and_context(meta: Type[UsefulType], value: bytes) -> tuple[UsefulType, bytes]:
    instance = meta(value)
    return instance, value[len(instance.contents):]


class SEQUENCE_OF(ABC):
    type: None
    values: list


@dataclass(frozen=True)
class SequenceElement:
    NAME: str
    TYPE: Type[UsefulType | SEQUENCE | CHOICE | cdt.CommonDataType]

    def __str__(self):
        return F'{self.NAME}: {self.TYPE.__name__}'


class UT(ABC):
    @abstractmethod
    def __init__(self, value: Any):
        """constructor from PYTHON build-in"""

    @classmethod
    @abstractmethod
    def from_contents(cls, value: bytes) -> Self:
        """constructor from bytes"""

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

    def decode(self) -> None:
        return None

    @classmethod
    def from_str(cls, value: str):
        return NULL

    def __str__(self):
        return self.__class__.__name__


NULL = Null()


class Boolean(UT):
    __contents: bytes
    __slots__ = ("__contents",)

    def __init__(self, value: bool = True):
        self.__contents = b'\x01' if value else b'\x00'

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
        return self.__contents

    @classmethod
    def from_int(cls, value: int):
        return FALSE if value == 0 else TRUE

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
        return str(self.decode())

    def decode(self) -> bool:
        """ decode to bool """
        return False if self.contents == b'\x00' else True

    def __bool__(self):
        return self.decode()

    def __int__(self):
        return 0 if self.contents == b'\x00' else 1


FALSE = Boolean(False)
TRUE = Boolean(True)


class OPTIONAL(UT, ABC):
    TYPE: Type[UT]
    __slots__ = ("value",)

    def __init__(self, value: UT = None):
        if value is None:
            self.value = None
        elif isinstance(value, self.TYPE):
            self.value = value
        else:
            raise ValueError(F"for {self.__class__.__name__} got type{value.__class__.__name__}, expected {self.TYPE}")

    @classmethod
    def from_contents(cls, value: bytes):
        if len(value) == 0:
            raise ValueError(F"for {cls.__name__} got contents length = 0, expected at least 1")
        elif value[0] == 0:
            return cls(None)
        else:
            return cls(cls.TYPE(value[1:]))

    @property
    def contents(self):
        if self.value is None:
            return FALSE.contents
        else:
            return TRUE.contents + self.value.contents

    def __str__(self):
        return str(NULL) if self.value is None else self.value

    @classmethod
    def from_str(cls, value: str) -> Self:
        raise RuntimeError(F"Not implementation for {cls.__name__}")


@dataclass
class SEQUENCE(UT):
    """ TODO: """

    @property
    def contents(self):
        data = bytearray()
        for it in astuple(self, tuple_factory=iter):
            data.extend(it.contents)
        return bytes(data)

    # def __init__(self, value: bytes | tuple | list):
    #     self.__dict__['values'] = [None] * len(self.ELEMENTS)
    #     match value:
    #         case bytes():
    #             for i, element in enumerate(self.ELEMENTS):
    #                 self.values[i], value = get_instance_and_context(element.TYPE, value)
    #         case tuple() | list():
    #             if len(value) != len(self):
    #                 raise ValueError(F'Struct {self.__class__.__name__} got length:{len(value)}, expected length:{len(self)}')
    #             self.from_tuple(value)
    #         case bytes():           self.from_bytes(value)
    #         case None:              self.from_default()
    #         case self.__class__():  self.from_bytes(value.contents)
    #         case _:                 raise TypeError(F'Value: "{value}" not supported')

    # def from_default(self):
    #     for i in range(len(self)):
    #         self.values[i] = self.ELEMENTS[i].TYPE()

    @classmethod
    def from_contents(cls, value: bytes | bytearray) -> Self:
        for f in fields(cls):
            print(f)

    def from_tuple(self, value: tuple | list):
        for i, val in enumerate(value):
            self.values[i] = self.ELEMENTS[i].TYPE(val)

    def __str__(self):
        return str(asdict(self))

    @classmethod
    def from_str(cls, value: str) -> Self:
        raise ValueError("not implementation")

    # def __repr__(self):
    #     return F'{self.__class__.__name__}(({(", ".join(map(str, self.values)))}))'

    def __get_index(self, name: str) -> int | None:
        """ get index by name. Return None if not found """
        for i, element in enumerate(self.ELEMENTS):
            if element.NAME == name:
                return i
        else:
            return None

    def __getitem__(self, item: str | int) -> UsefulType:
        """ get element by index or name """
        match item:
            case str() as name:  return self.values[self.__get_index(name)]
            case int() as index: return self.values[index]
            case _:              raise ValueError(F'Unsupported type {item.__class__}')

    def __setitem__(self, key: int, value: UsefulType):
        """ set data to element by index """
        if isinstance(value, self.ELEMENTS[key].TYPE):
            self.values[key] = value
        else:
            raise ValueError(F'Type got {value.__class__.__name__}, expected {self.ELEMENTS[key].TYPE}')

    def __len__(self):
        return len(astuple(self))

    @property
    def NAME(self) -> str:
        return F'{self.__class__.__name__}[{len(self)}]'


class UsefulType(ABC):
    """"""
    contents: bytes
    __match_args__ = ('contents',)
    cb_post_set: Callable
    cb_preset: Callable

    @abstractmethod
    def __init__(self, value):
        """ constructor """

    def __eq__(self, other: UsefulType):
        match other:
            case self.__class__(self.contents): return True
            case _:                             return False

    def set_contents_from(self, value: UsefulType | bytes | bytearray | str | int | bool | None):
        new_value = self.__class__(value)
        if hasattr(self, 'cb_preset'):
            self.cb_preset(new_value)
        self.__dict__['contents'] = new_value.contents
        if hasattr(self, 'cb_post_set'):
            self.cb_post_set()

    def __setattr__(self, key, value):
        match key:
            case 'contents' as prop if hasattr(self, 'contents'): raise ValueError(F"Don't support set {prop}")
            case _: super().__setattr__(key, value)


class DigitalMixin(ABC):
    """ Default value is 0 """
    SIGNED: bool
    LENGTH: int
    value: int

    def __init__(self, value: int):
        self.value = value
        assert self.contents  # simple validator

    @classmethod
    def from_contents(cls, value: bytes):
        return cls(int.from_bytes(value, "big", signed=cls.SIGNED))

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

    def __gt__(self, other: DigitalMixin):
        match other:
            case DigitalMixin(): return self.value > other.value
            case _:          raise TypeError(F'Compare type is {other.__class__}, expected Digital')

    def __len__(self) -> int:
        return self.LENGTH

    def __hash__(self):
        return self.value

    def __eq__(self, other: DigitalMixin):
        return self.contents == other.contents


class Integer8(DigitalMixin, UT):
    """ INTEGER(-127…128) """
    LENGTH = 1
    SIGNED = True


class Integer16(DigitalMixin, UT):
    """ INTEGER(-32 768...32 767) """
    LENGTH = 2
    SIGNED = True


class Integer32(DigitalMixin, UT):
    """ INTEGER(-2 147 483 648...2 147 483 647) """
    LENGTH = 4
    SIGNED = True


class Integer64(DigitalMixin, UT):
    """ INTEGER(-2^63...2^63-1) """
    LENGTH = 8
    SIGNED = True


class Unsigned8(DigitalMixin, UT):
    """ INTEGER(0...255) """
    LENGTH = 1
    SIGNED = False
    # __match_args__ = ('contents',)


class Unsigned16(DigitalMixin, UT):
    """ INTEGER(0...65 535) """
    LENGTH = 2
    SIGNED = False


class Unsigned32(DigitalMixin, UT):
    """ INTEGER(0...4 294 967 295) """
    LENGTH = 4
    SIGNED = False


class Unsigned64(DigitalMixin, UT):
    """ INTEGER(0...264-1) """
    LENGTH = 8
    SIGNED = False


class CosemClassId(Unsigned16):
    """COSEMpdu-Gb83"""

    def __str__(self):
        if _class_names:
            return _class_names.get(self, repr(self))
        else:
            return repr(self)

    def __repr__(self):
        return F"{self.__class__.__name__}({int(self)})"


_class_names = {CosemClassId(value=int(k)): v for k, v in class_names.items()} if (class_names := get_values("DLMS", "class_name")) else None
"""use for string representation CosemClassId"""


class CosemObjectInstanceId(OctetString):
    LENGTH = 6

    def __init__(self, value: bytes):
        if len(value) == self.LENGTH:
            super(CosemObjectInstanceId, self).__init__(value)
        else:
            raise ValueError(F"for init {self.__class__.__name__} got length value: {len(value)}, expected {self.LENGTH}")

    def __str__(self):
        return F"\"{'.'.join(map(str, self.contents))}\""

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
    """ TODO """

    @lru_cache(14)  # for test
    def __new__(cls, *args, **kwargs):
        return super().__new__(cls)


class CosemObjectMethodId(Integer8):
    """ TODO """


class AccessSelectionParameters(Unsigned8):
    """ Unsigned8(0..1) """

    def __init__(self, value: int | str | Unsigned8 = 1):
        super(AccessSelectionParameters, self).__init__(value)
        if int(self) > 1 or int(self) < 0:
            raise ValueError(F'The {self.__class__.__name__} got {self}, expected 0..1')


class CosemAttributeDescriptor(SEQUENCE):
    class_id: CosemClassId
    instance_id: CosemObjectInstanceId
    attribute_id: CosemObjectAttributeId
    access_selection_parameters: AccessSelectionParameters
    ELEMENTS = (SequenceElement('class_id', CosemClassId),
                SequenceElement('instance_id', CosemObjectInstanceId),
                SequenceElement('attribute_id', CosemObjectAttributeId))

    def __init__(self, value: bytes | tuple | list = None):
        super(CosemAttributeDescriptor, self).__init__(value)
        self.__dict__['access_selection_parameters'] = AccessSelectionParameters(0)

    @property
    def contents(self) -> bytes:
        """ Always contain Access_Selection_Parameters. DLMS UA 1000-2 Ed.9 Excerpt 9.3.9.1.3 """
        return super(CosemAttributeDescriptor, self).contents + self.access_selection_parameters.contents


class CosemMethodDescriptor(SEQUENCE):
    class_id: CosemClassId
    instance_id: CosemObjectInstanceId
    method_id: CosemObjectMethodId
    ELEMENTS = (SequenceElement('class_id', CosemClassId),
                SequenceElement('instance_id', CosemObjectInstanceId),
                SequenceElement('method_id', CosemObjectMethodId))

    def __init__(self, value: tuple[CosemClassId, CosemObjectInstanceId, CosemObjectMethodId]):
        super(CosemMethodDescriptor, self).__init__(value)


class Data(CHOICE, ABC):
    ELEMENTS = {
        0: SequenceElement('null-data', Null),
        1: SequenceElement('array', SEQUENCE),
        15: SequenceElement('integer', Integer8),
    }


class SelectiveAccessDescriptor(SEQUENCE, ABC):
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


class CosemAttributeDescriptorWithSelection(SEQUENCE):
    cosem_attribute_descriptor: CosemAttributeDescriptor
    access_selection: SelectiveAccessDescriptor
    ELEMENTS: tuple[CosemAttributeDescriptor, SequenceElement]

    def __init__(self, value: bytes | tuple | list = None):
        super(CosemAttributeDescriptorWithSelection, self).__init__(value)
        self.cosem_attribute_descriptor.access_selection_parameters.set_contents_from(1)

    @property
    @abstractmethod
    def ELEMENTS(self) -> tuple[SequenceElement, SequenceElement]:
        """ return elements. Need initiate in subclass """

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Type, Any, Callable
from dataclasses import dataclass
from ..types import common_data_types as cdt


class _String(ABC):
    LENGTH: int | None

    def __init__(self, value: bytes | bytearray | str | int | UsefulType = None):
        match value:
            case None:                                                        self.contents = bytes(self.LENGTH)
            case bytes() if self.LENGTH is None or self.LENGTH <= len(value): self.contents = value[:self.LENGTH]
            # case bytes() if self.LENGTH <= len(value):                       self.contents = value[:self.LENGTH]
            case bytes():            raise ValueError(F'Length of contents for {self.__class__.__name__} must be at least {self.LENGTH}, but got {len(value)}')
            case bytearray():                                                 self.contents = bytes(value)  # Attention!!! changed method content getting from bytearray
            case str():                                                       self.contents = self.from_str(value)
            case int():                                                       self.contents = self.from_int(value)
            case UsefulType():                                                self.contents = value.contents  # TODO: make right type
            case _:                                                           raise ValueError(F'Error create {self.__class__.__name__} with value {value}')

    @abstractmethod
    def __len__(self):
        """ define in subclasses """


class OCTET_STRING(_String):
    """ An ordered sequence of octets (8 bit bytes) """

    def from_str(self, value: str) -> bytes:
        """ input as hex code """
        return bytes.fromhex(value)

    def from_int(self, value: int) -> bytes:
        """ Convert with recursion. Maximum convert length is 32 """
        def to_bytes_with(length_):
            try:
                return int.to_bytes(value, length_, 'big')
            except OverflowError:
                if length_ > 31:
                    raise ValueError(F'Value {value} is big to convert to bytes')
                return to_bytes_with(length_+1)
        length = 1
        return to_bytes_with(length)

    def __str__(self):
        return self.contents.hex(' ')

    def __len__(self):
        return len(self.contents)

    def __getitem__(self, item):
        return self.contents[item]

    # TODO: maybe remove as redundante?
    def decode(self) -> bytes:
        """ decode to build in bytes type """
        return self.contents

    # TODO: maybe remove as redundante?
    def to_str(self, encoding: str = 'cp1251') -> str:
        """ decode to cp1251 by default, replace to '?' if unsupported """
        temp = list()
        for i in self.contents:
            temp.append(i if i > 32 else 63)
        return bytes(temp).decode(encoding)


class CHOICE(ABC):
    """ TODO: with cdt.CHOICE """
    ELEMENTS: dict[int, SequenceElement | dict[int, SequenceElement]]

    @property
    @abstractmethod
    def TYPE(self) -> Any:
        """ return valid types """

    def __init_subclass__(cls, **kwargs):
        if hasattr(cls, 'ELEMENTS'):
            for el in cls.ELEMENTS.values():
                if isinstance(el, dict):
                    """pass, maybe it is for cst.AnyTime"""
                elif issubclass(el.TYPE, cls.TYPE):
                    """ type in order """
                else:
                    raise ValueError(F'For {cls.__name__} got type {el.TYPE.__name__} with {el.NAME=}, expected {cls.TYPE.__name__}')
        else:
            """ subclass with type carry initiate """

    def __getitem__(self, item: int) -> SequenceElement:
        return self.ELEMENTS[item]

    @property
    def NAME(self) -> str:
        return F'CHOICE[{len(self)}]'

    def __len__(self):
        return len(self.ELEMENTS)

    def is_key(self, value: int) -> bool:
        return value in self.ELEMENTS.keys()

    def __call__(self, value: bytes | int) -> cdt.CommonDataType:
        """ get instance from encoding or tag(with default value). For CommonDataType only """
        try:
            match value:
                case bytes() as encoding:
                    match self.ELEMENTS[encoding[0]]:
                        case SequenceElement() as el: return el.TYPE(encoding)
                        case dict() as ch:            return ch[encoding[1]].TYPE(encoding)  # use for choice cst.Time | DateTime | Date as OctetString
                        case err:                     raise ValueError(F"got {err.__name__}, expected {SequenceElement.__name__} or {dict.__name__}")
                case int() as tag:                    return self.ELEMENTS[tag].TYPE()
                case error:                           raise ValueError(F'Unknown value type {error}')
        except KeyError as e:
            raise KeyError(F'For {self.__class__.__name__} got key: {e.args[0]}, expected {tuple(self.ELEMENTS.keys())}')

    def get_types(self) -> tuple[Type[cdt.CommonDataType]]:
        """ Use in setter attribute.value for validate """
        return tuple((seq_el.TYPE for seq_el in self.ELEMENTS.values()))

    def __str__(self):
        return F'{CHOICE}: {", ".join((el.NAME for el in self.ELEMENTS.values()))}'


def get_instance_and_context(meta: Type[UsefulType], value: bytes) -> tuple[UsefulType, bytes]:
    instance = meta(value)
    return instance, value[len(instance.contents):]


@dataclass(frozen=True)
class SequenceElement:
    NAME: str
    TYPE: Type[UsefulType | SEQUENCE | CHOICE | cdt.CommonDataType]

    def __str__(self):
        return F'{self.NAME}: {self.TYPE.__name__}'


class SEQUENCE(ABC):
    """ TODO: """
    ELEMENTS: tuple[SequenceElement | SEQUENCE, ...]
    values: list[UsefulType]

    def __init__(self, value: bytes | tuple | list | None | SEQUENCE = None):
        self.__dict__['values'] = [None] * len(self.ELEMENTS)
        match value:
            case tuple() | list():
                if len(value) != len(self):
                    raise ValueError(F'Struct {self.__class__.__name__} got length:{len(value)}, expected length:{len(self)}')
                self.from_tuple(value)
            case bytes():           self.from_bytes(value)
            case None:              self.from_default()
            case self.__class__():  self.from_bytes(value.contents)
            case _:                 raise TypeError(F'Value: "{value}" not supported')

    def from_default(self):
        for i in range(len(self)):
            self.values[i] = self.ELEMENTS[i].TYPE()

    def from_bytes(self, value: bytes | bytearray):
        for i, element in enumerate(self.ELEMENTS):
            self.values[i], value = get_instance_and_context(element.TYPE, value)

    def from_tuple(self, value: tuple | list):
        for i, val in enumerate(value):
            self.values[i] = self.ELEMENTS[i].TYPE(val)

    def __str__(self):
        return F'{{{", ".join(map(lambda val: F"{val[0].NAME}: {val[1]}", zip(self.ELEMENTS, self.values)))}}}'

    def __get_index(self, name: str) -> int | None:
        """ get index by name. Return None if not found """
        for i, element in enumerate(self.ELEMENTS):
            if element.NAME == name:
                return i
        else:
            return None

    def __setattr__(self, key, value: UsefulType):
        match self.__get_index(key):
            case int() as i if isinstance(value, self.ELEMENTS[i]):                self.values[i] = value
            case int() as i:                raise ValueError(F'Try assign {key} Type got {value.__class__.__name__}, expected {self.ELEMENTS[i].NAME}')
            case _:                raise ValueError(F'Unsupported change: {key}')

    def __getattr__(self, item: str) -> UsefulType:
        match self.__get_index(item):
            case int() as i: return self.values[i]
            case _:          return self.__dict__[item]

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
        return len(self.ELEMENTS)

    @property
    def contents(self) -> bytes:
        return b''.join(el.contents for el in self.values)

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
    contents: bytes

    def __init__(self, value: bytes | bytearray | str | int | DigitalMixin = None):
        match value:
            case bytes() if self.LENGTH <= len(value): self.contents = value[:self.LENGTH]
            case bytes():            raise ValueError(F'Length of contents for {self.__class__.__name__} must be at least {self.LENGTH}, but got {len(value)}')
            case bytearray():                          self.contents = bytes(value)  # Attention!!! changed method content getting from bytearray
            case str('-') if self.SIGNED:              self.contents = bytes(self.LENGTH)
            case int():                                self.contents = self.from_int(value)
            case str():                                self.contents = self.from_str(value)
            case None:                                 self.contents = bytes(self.LENGTH)
            case self.__class__():                     self.contents = value.contents
            case _:                                    raise ValueError(F'Error create {self.__class__.__name__} with value: {value}')

    def from_int(self, value: int | float) -> bytes:
        try:
            return int(value).to_bytes(self.LENGTH, 'big', signed=self.SIGNED)
        except OverflowError:
            raise ValueError(F'value {value} out of range')

    def from_str(self, value: str) -> bytes:
        return self.from_int(float(value))

    def __int__(self):
        """ return the build in integer type """
        return int.from_bytes(self.contents, 'big', signed=self.SIGNED)

    def __str__(self):
        return str(int(self))

    def __repr__(self):
        return F'{self.__class__.__name__}({self})'

    def __gt__(self, other: DigitalMixin):
        match other:
            case DigitalMixin(): return int(self) > int(other)
            case _:          raise TypeError(F'Compare type is {other.__class__}, expected Digital')

    def __len__(self) -> int:
        return self.LENGTH

    def __hash__(self):
        return int(self)

    def validate_from(self, value: str, cursor_position: int) -> tuple[str, int]:
        """ return validated value and cursor position. Use in Entry. TODO: remove it, make better """
        type(self)(value=value)
        return value, cursor_position


class Integer8(DigitalMixin, UsefulType):
    """ INTEGER(-127…128) """
    LENGTH = 1
    SIGNED = True


class Integer16(DigitalMixin, UsefulType):
    """ INTEGER(-32 768...32 767) """
    LENGTH = 2
    SIGNED = True


class Integer32(DigitalMixin, UsefulType):
    """ INTEGER(-2 147 483 648...2 147 483 647) """
    LENGTH = 4
    SIGNED = True


class Integer64(DigitalMixin, UsefulType):
    """ INTEGER(-2^63...2^63-1) """
    LENGTH = 8
    SIGNED = True


class Unsigned8(DigitalMixin, UsefulType):
    """ INTEGER(0...255) """
    LENGTH = 1
    SIGNED = False
    # __match_args__ = ('contents',)


class Unsigned16(DigitalMixin, UsefulType):
    """ INTEGER(0...65 535) """
    LENGTH = 2
    SIGNED = False


class Unsigned32(DigitalMixin, UsefulType):
    """ INTEGER(0...4 294 967 295) """
    LENGTH = 4
    SIGNED = False


class Unsigned64(DigitalMixin, UsefulType):
    """ INTEGER(0...264-1) """
    LENGTH = 8
    SIGNED = False


class CosemClassId(Unsigned16):
    """ Identification code of the IC (range 0 to 65 535). The class_id of each object is retrieved together with the logical name by reading the object_list attribute of an
    “Association LN” / ”Association SN” object.
        - class_id-s from 0 to 8 191 are reserved to be specified by the DLMS UA.
        - class_id-s from 8 192 to 32 767 are reserved for manufacturer specific ICs.
        - class_id-s from 32 768 to 65 535 are reserved for user group specific ICs.
    The DLMS UA reserves the right to assign ranges to individual manufacturers or user groups. """


class CosemObjectInstanceId(OCTET_STRING, UsefulType):
    LENGTH = 6

    def __str__(self):
        return '.'.join(map(str, self.contents))

    def from_str(self, value: str) -> bytes:
        """ create logical_name: octet_string from string type ddd.ddd.ddd.ddd.ddd.ddd, ex.: 0.0.1.0.0.255 """
        raw_value = bytes()
        for typecast, separator in zip((self.__from_group_A, )*5+(self.__from_group_F, ), ('.', '.', '.', '.', '.', ' ')):
            try:
                element, value = value.split(separator, 1)
            except ValueError:
                element, value = value, ''
            raw_value += typecast(element)
        return raw_value

    def __from_group_A(self, value: str) -> bytes:
        if isinstance(value, str):
            if value == '':
                return b'\x00'
            try:
                return int(value).to_bytes(1, 'big')
            except OverflowError:
                raise ValueError(F'Int too big to convert {value}')
        else:
            raise TypeError(F'Unsupported type validation from string, got {value.__class__}')

    def __from_group_F(self, value: str) -> bytes:
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
    TYPE = cdt.CommonDataType


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


class InvokeIdAndPriority(Unsigned8):

    def __init__(self, value: bytes | bytearray | str | int | DigitalMixin = 0b1100_0000):
        super(InvokeIdAndPriority, self).__init__(value)
        if self.contents[0] & 0b00110000:
            raise ValueError(F'For {self.__class__.__name__} set reserved bits')

    @classmethod
    def from_parameters(cls, invoke_id: int = 0,
                        service_class: int = 0,
                        priority: int = 0):
        instance = cls()
        instance.invoke_id = invoke_id
        instance.service_class = service_class
        instance.priority = priority
        return instance

    @property
    def invoke_id(self) -> int:
        return self.contents[0] & 0b0000_1111

    @invoke_id.setter
    def invoke_id(self, value: int):
        if value & 0b00001111:
            self.__dict__['contents'] = int((self.contents[0] & 0b1111_0000) | value).to_bytes(1, 'big')
        else:
            raise ValueError(F'Got {value} for invoke-id, expected 0..15')

    @property
    def service_class(self) -> int:
        """ 0: Unconfirmed or 1: Confirmed bit return """
        return (self.contents[0] >> 6) & 0b1

    @service_class.setter
    def service_class(self, value: int):
        match value:
            case 0 | 1: self.__dict__['contents'] = int((self.contents[0] & 0b1011_1111) | (value << 6)).to_bytes(1, 'big')
            case _:     raise ValueError(F'Got {value} for service_class, expected 0..1')

    @property
    def priority(self) -> int:
        """ 0: Normal or 1: High bit return """
        return (self.contents[0] >> 7) & 0b1

    @priority.setter
    def priority(self, value: int):
        match value:
            case 0 | 1: self.__dict__['contents'] = int((self.contents[0] & 0b0111_1111) | (value << 7)).to_bytes(1, 'big')
            case _:     raise ValueError(F'Got {value} for service_class, expected 0..1')

    def __str__(self):
        return F'priority: {"High" if self.contents[0] & 0b1000_0000 else "Normal"}, ' \
               F'service-class: {"Confirmed" if self.contents[0] & 0b0100_0000 else "Unconfirmed"}, ' \
               F'invoke-id: {self.invoke_id},'


if __name__ == '__main__':
    a = CosemObjectAttributeId(1)
    b = CosemObjectAttributeId(2)
    print(a > b)

    a = CosemClassId(cdt.LongUnsigned(1).contents)
    a = InvokeIdAndPriority()
    c = a.invoke_id
    d = a.service_class
    f = a.priority
    a.service_class = 1
    a.invoke_id = 14
    e = InvokeIdAndPriority.from_parameters(1, 1, 1)
    class AccessSelector(Unsigned8):
        """ Unsigned8 1..4 """
        def __init__(self, value: int | str | Unsigned8 = 1):
            super(AccessSelector, self).__init__(value)
            if int(self) > 4 or int(self) < 1:
                raise ValueError(F'The {self.__class__.__name__} got {self}, expected 1..4')


    class MyData(Data):
        ELEMENTS = {1: SequenceElement('0 a', cdt.NullData),
                    2: SequenceElement('1 d', cdt.Integer),
                    3: SequenceElement('second', cdt.ScalUnitType),
                    4: SequenceElement('3', cdt.Integer)}

    class My(SelectiveAccessDescriptor):
        access_selector: AccessSelector
        access_parameters: MyData
        ELEMENTS = (SequenceElement('access_selector', AccessSelector),
                    SequenceElement('access_parameters', MyData))

    ba = My()
    b = My((3, (10, 10)))
    b2 = b.access_selector
    b3 = b.access_parameters
    b4 = b.access_parameters.unit
    b_repr = My(b'\x03\x0f"')
    b.set_selector(3, 34)
    a = CosemAttributeDescriptor((1, '1.1.1.1.1.1', 1))
    a_repr = CosemAttributeDescriptor(b'\x00\x01\x01\x01\x01\x01\x01\x01\x01\x00')

    class MyWith(CosemAttributeDescriptorWithSelection):
        access_selection: My
        ELEMENTS = (SequenceElement('cosem_attribute_descriptor', CosemAttributeDescriptor),
                    SequenceElement('access_selection', My))

    c = MyWith()
    c_from = MyWith((a, b))
    c_repr = MyWith(b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x01\x01\x00')
    print(a)
    c = CosemAttributeDescriptor(b'\x00\x01\x01\x01\x01\x01\x01\x01\x01\x00')
    print(c)

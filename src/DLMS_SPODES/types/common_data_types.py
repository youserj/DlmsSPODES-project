from __future__ import annotations
from itertools import chain
from dataclasses import dataclass
from struct import pack, unpack
from abc import ABC, abstractmethod
from typing import Optional, Type, Tuple, Dict, List, Any, Callable, TypeAlias
from collections import deque
from math import log, ceil
import datetime
import logging
from .. import settings


match settings.get_current_language():
    case settings.Language.ENGLISH: from ..Values.EN import cdt as tn, se, enum_names as en
    case settings.Language.RUSSIAN: from ..Values.RU import cdt as tn, se, enum_names as en
    case _ as lang:                        raise ImportError(F'{lang} is absence')


logger = logging.getLogger(__name__)
logger.level = logging.INFO


# TODO: rewrite with Cython
def separate(value: str, pattern: str, max_sep: int) -> tuple[str, list[str]]:
    """ separating string to container by pattern. Use in Date and Time """
    paths = list()
    separators = path = ''
    while len(value) != 0:
        if value[0] in pattern:
            paths.append(path)
            separators += value[0]
            if len(separators) == max_sep:
                paths.append(value[1:])
                break
            else:
                path = ''
        elif value[0] == ' ':
            paths.append(path)
            separators += value[0]
            paths.append(value[1:])
            break
        else:
            path += value[0]
        value = value[1:]
    else:
        paths.append(path)
    return separators, paths


def get_common_data_type_from(tag: bytes) -> Type[CommonDataType]:
    """ search and get class from tag if existed """
    try:
        return __types[tag[:1]]
    except KeyError:
        raise ValueError(F'type with tag:{tag[:1]} is absence in Common Data Type')


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
        raise ValueError('Value is empty')
    if bool(define_length & 0b10000000):
        content_start += define_length - 0x80
        length = int.from_bytes(input_pdu[1:content_start], 'big')
    else:
        length = define_length
    pdu = input_pdu[content_start:]
    return length, pdu


def get_instance_and_pdu(meta: Type[CommonDataType], value: bytes) -> tuple[CommonDataType, bytes]:
    instance = meta(value)
    return instance, value[len(instance.encoding):]


def get_instance_and_pdu_from_value(value: bytes | bytearray) -> Tuple[CommonDataType, bytes]:
    instance = get_common_data_type_from(value[:1])(value)
    try:    # TODO: remove it in future
        return instance, value[len(instance.encoding):]
    except Exception as e:
        print(F'{e.args}')


class CommonDataType(ABC):
    """ DLMS BlueBook(IEC 62056-6-2) 13.0 4.1.5 Common data types . X.690: OSI networking and system aspects – Abstract
    Syntax Notation One (ASN.1) """
    cb_post_set: Callable
    cb_preset: Callable
    contents: bytes

    @abstractmethod
    def __init__(self, value=None):
        """ constructor """

    @abstractmethod
    def clear(self):
        """set value to default"""

    @property
    def complex_data(self) -> bytes:
        """ Provides an alternative, compact encoding of complex data. For CompactArray
        TODO: remove it after all types value will be bytes"""
        return self.contents

    @property
    @abstractmethod
    def TAG(self) -> bytes:
        """ 62056-53 8.3 TypeDescription ::= CHOICE. Set at once, no supported change """

    @property
    @abstractmethod
    def NAME(self) -> str:
        """ return the type name which depends from language"""

    @property
    @abstractmethod
    def encoding(self) -> bytes:
        """ The complete sequence of octets used to represent the data value. """

    def __setattr__(self, key, value):
        match key:
            case 'TAG' | 'NAME' as prop: raise ValueError(F"Don't support set {prop}")
            case _:                      super().__setattr__(key, value)

    def __eq__(self, other) -> bool:
        match other:
            case bytes() if self.encoding == other:                   return True
            case CommonDataType() if self.encoding == other.encoding: return True
            case bytes() | CommonDataType() | None:                   return False
            case _:                                                   raise ValueError(F'Unknown equal type <{other}>{other.__class__}')

    @abstractmethod
    def set(self, value: SimpleDataType | bytes | bytearray | str | int | bool | float | datetime.date | None):
        """ get new instance from value and set to content with validation """

    def validate_from(self, value: str, cursor_position: int) -> tuple[str, int]:
        """ not allowed change of string in common class """
        raise ValueError(F'Not supported in {self.NAME}')

    @classmethod
    def get_types(cls):
        """ return DLMS type """
        return cls

    @abstractmethod
    def copy(self) -> CommonDataType:
        """ return copy of object """

    @abstractmethod
    def decode(self) -> str | int | list | bytes | None | float:
        """ to build in python type """

    def register_cb_post_set(self, func: Callable):
        """ register callback function for calling after <set>"""
        self.__dict__['cb_post_set'] = func

    def register_cb_preset(self, func: Callable):
        """ register callback function for calling before <set>"""
        self.__dict__['cb_preset'] = func

    def to_str(self) -> str:
        """ represent value as string """
        raise ValueError(F'to_str method not support for {self.NAME}')

    def __int__(self):
        """ represent value as build-in integer """
        raise ValueError(F'to_int method not support for {self.NAME}')

    def __bytes__(self):
        """ represent value as string """
        raise ValueError(F'to_bytes method not support for {self.NAME}')

    # TODO: work not in all types. Solve it
    def __repr__(self):
        return F'{self.__class__.__name__}({self})'


class SimpleDataType(CommonDataType, ABC):

    def __setattr__(self, key, value):
        match key:
            case 'contents' as prop if hasattr(self, 'contents'): raise ValueError(F"Don't support set {prop}")
            case _: super().__setattr__(key, value)

    def validate_from(self, value: str, cursor_position: int) -> tuple[str, int]:
        """ return validated value and cursor position """
        type(self)(value=value)
        return value, cursor_position

    def copy(self) -> SimpleDataType:
        return self.__class__(self.encoding)

    def _new_instance(self, value) -> SimpleDataType:
        return self.__class__(value)

    def set(self, value: SimpleDataType | bytes | bytearray | str | int | bool | float | datetime.date | None):
        new_value = self._new_instance(value)
        if hasattr(self, 'cb_preset'):
            self.cb_preset(new_value)
        self.__dict__['contents'] = new_value.contents
        if hasattr(self, 'cb_post_set'):
            self.cb_post_set()


class ComplexDataType(CommonDataType, ABC):
    values: list[CommonDataType, ...]

    @property
    def contents(self) -> bytes:
        """ ITU-T Rec. X.690 8.1.1 Structure of an encoding """
        return b''.join(map(lambda el: el.encoding, self.values))

    @abstractmethod
    def __len__(self):
        """ elements amount """

    def copy(self) -> ComplexDataType:
        return self.__class__(self.encoding)

    @property
    def encoding(self) -> bytes:
        """ The complete sequence of octets used to represent the data value. """
        return self.TAG + encode_length(len(self.values)) + self.contents


class __Array(ABC):
    TYPE: Type[SimpleDataType | Structure]
    values: list[SimpleDataType | Structure]

    def remove(self, element: SimpleDataType | Structure):
        if isinstance(element, self.TYPE):
            self.values.remove(element)

    def pop(self, index: int | None = None):
        self.values.pop(index)

    def __len__(self):
        return len(self.values)

    def clear(self):
        self.values.clear()


class _String(ABC):
    TAG: bytes
    DEFAULT: bytes = b''

    def __init__(self, value: bytes | bytearray | str | int | SimpleDataType = None):
        match value:
            case None:                                                       self.contents = self.DEFAULT
            case bytes() as encoding:
                length, pdu = get_length_and_pdu(encoding[1:])
                match encoding[:1]:
                    case self.TAG if length <= len(pdu):                     self.contents = pdu[:length]
                    case self.TAG:                                           raise ValueError(F'Length is {length}, but contents got only {len(pdu)}')
                    case _:                                                  raise TypeError(F'Expected {self.NAME} type, got {get_common_data_type_from(encoding[:1]).NAME}')
            case bytearray():                                                self.contents = bytes(value)  # Attention!!! changed method content getting from bytearray
            case str():                                                      self.contents = self.from_str(value)
            case int():                                                      self.contents = self.from_int(value)
            case SimpleDataType():                                           self.contents = value.contents
            case _:                                                          raise ValueError(F'Error create {self.NAME} with value {value}')
        self.validation()

    def validation(self):
        """ do any thing """

    @abstractmethod
    def __len__(self):
        """ define in subclasses """

    @property
    def encoding(self) -> bytes:
        return self.TAG + encode_length(len(self)) + self.contents

    def clear(self):
        self.__dict__['contents'] = self.DEFAULT


class FlagMixin(ABC):
    """ Used for override Common Data Type as Flag data """
    ELEMENTS: dict[int, str]
    contents: bytes

    def validation(self):
        """ call exception if bit is absence in elements"""
        mask = int('1'*len(self.contents)*8, base=2)
        for el in self.ELEMENTS.keys():
            mask ^= 1 << el
        match mask & int.from_bytes(self.contents, 'big'):
            case 0:              """ validation OK. Not using bit is not set """
            case _ as bit_error: raise ValueError(F'Unused bit set: {bin(bit_error)}')

    def from_str(self, value: str) -> bytes:
        value = value + '0' * ((8 - len(self)) % 8)
        list_ = [value[count:(count + 8)] for count in range(0, len(self), 8)]
        value = b''
        for byte in list_:
            value += int(byte, base=2).to_bytes(1, byteorder='little')
        return value

    def from_none(self) -> bytes:
        """because differ from Enum ELEMENT keys"""
        return next(iter(self.ELEMENTS)).to_bytes(1, 'little')

    def decode(self) -> list[int]:
        """ TODO: copypast BitString """
        ret = list()
        for byte_ in self.contents:
            ret.extend([(byte_ >> it) & 0b00000001 for it in range(7, -1, -1)])
        return ret[:len(self)]

    def __len__(self):
        """ return bits amount """
        return max(self.ELEMENTS.keys()) + 1

    def __str__(self):
        """ TODO: copypast BitString """
        return ''.join(map(str, self.decode()))

    def validate_from(self, value: str, cursor_position=None):
        """ return 'Ok' if string is valid else return valid Str. TODO: copypast BitString """
        if self.ELEMENTS:
            type(self)(value=value.zfill(len(self.ELEMENTS)))
        else:
            type(self)(value=value)
        return value, cursor_position


class Digital(ABC):
    """ Default value is 0 """
    contents: bytes
    TAG: bytes
    SCALER_UNIT: ScalUnitType | None
    DEFAULT = None

    def __init__(self, value: bytes | bytearray | str | int | float | Digital = None, scaler_unit: ScalUnitType = None):
        if value is None:
            value = self.DEFAULT
        self.__dict__['SCALER_UNIT'] = scaler_unit
        match value:
            case bytes():
                length_and_contents = value[1:]
                match value[:1]:
                    case self.TAG if self.LENGTH <= len(length_and_contents): self.contents = length_and_contents[:self.LENGTH]
                    case self.TAG:                                                     raise ValueError(F'Length of contents for {self.NAME} must be at least '
                                                                                                        F'{self.LENGTH}, but got {len(length_and_contents)}')
                    case _ as wrong_tag:                                               raise TypeError(F'Expected {self.NAME} type, got {get_common_data_type_from(wrong_tag).NAME}')
            case bytearray():                                                          self.contents = bytes(value)  # Attention!!! changed method content getting from bytearray
            case str('-') if self.SIGNED:                                              self.contents = bytes(self.LENGTH)
            case int() | float():                                                      self.contents = self.from_int(value)
            case str():                                                                self.contents = self.from_str(value)
            case None:                                                                 self.contents = bytes(self.LENGTH)
            case self.__class__():                                                     self.contents = value.contents
            case _:                                                                    raise ValueError(F'Error create {self.NAME} with value: {value}')
        self.validate()

    def validate(self):
        """ receiving contents validate. override it if need """

    def _new_instance(self, value) -> Digital:
        """ override SimpleDataType for send scaler_unit . use only for check and send contents """
        return self.__class__(value, self.SCALER_UNIT)

    def from_int(self, value: int | float) -> bytes:
        try:
            match self.SCALER_UNIT:
                case ScalUnitType(): value *= 10**(-self.SCALER_UNIT.scaler.decode())
                case None:           """ no scaler """
                case _ as error:     raise TypeError(F'Unknown scaler_unit: {error}')
            return int(value).to_bytes(self.LENGTH, 'big', signed=self.SIGNED)
        except OverflowError:
            raise ValueError(F'value {value} out of range')

    def from_str(self, value: str) -> bytes:
        return self.from_int(float(value))

    def clear(self):
        if self.DEFAULT:
            self.__dict__['contents'] = self.__class__(self.DEFAULT).contents
        else:
            self.__dict__['contents'] = bytes(self.LENGTH)

    @property
    def encoding(self) -> bytes:
        return self.TAG + self.contents

    def decode(self) -> int | float:
        """ return the build in integer type or float type """
        match self.SCALER_UNIT:
            case None:           return int.from_bytes(self.contents, 'big', signed=self.SIGNED)
            case ScalUnitType(): return int.from_bytes(self.contents, 'big', signed=self.SIGNED) * 10 ** self.SCALER_UNIT.scaler.decode()
            case _ as error:     raise TypeError(F'Unknown scaler_unit type {error}')

    def __int__(self):
        if self.SCALER_UNIT is None:
            return int.from_bytes(self.contents, 'big', signed=self.SIGNED)
        else:
            raise ValueError(F"not support to_int for {self} with ScalerUnit")

    def __lshift__(self, other: int):
        for i in range(other):
            tmp = int.from_bytes(self.contents, "big")
            tmp <<= 1
            tmp &= 0x100**self.LENGTH - 1
            self.__dict__["contents"] = tmp.to_bytes(self.LENGTH, "big")

    def __rshift__(self, other):
        for i in range(other):
            tmp = int.from_bytes(self.contents, "big")
            tmp >>= 1
            self.__dict__["contents"] = tmp.to_bytes(self.LENGTH, "big")

    @property
    @abstractmethod
    def SIGNED(self) -> bool:
        """ True for signed digital, False for unsigned. Default is unsigned"""

    @property
    @abstractmethod
    def LENGTH(self) -> int:
        """ Content length of type"""

    def __str__(self):
        match self.decode():
            case int() as value:   return str(value)
            case float() as value: return F'{self.decode():.{-min(self.SCALER_UNIT.scaler.decode(), 0)}f}'
            case _ as error:       return F'Error decoding type: {error}'

    @property
    def report(self) -> str:
        """ report value with unit """
        match self.SCALER_UNIT:
            case None: return str(self)
            case _:    return F'{self} {self.SCALER_UNIT.unit}'

    def __gt__(self, other: Digital | int):
        match other:
            case int():     return self.decode() > other
            case Digital(): return self.decode() > other.decode()
            case _:         raise TypeError(F'Compare type is {other.__class__}, expected Digital')

    def __len__(self) -> int:
        return self.LENGTH

    def __setattr__(self, key, value):
        match key, value:
            case 'SCALER_UNIT', ScalUnitType() if self.SCALER_UNIT is None:  self.__dict__['SCALER_UNIT'] = value
            case 'SCALER_UNIT', None:                                        self.__dict__['SCALER_UNIT'] = None
            case 'SCALER_UNIT', ScalUnitType() if self.SCALER_UNIT == value: """ double set Scaler Unit """
            case 'SCALER_UNIT', ScalUnitType():                              raise ValueError('Scaler Unit already set')
            case 'SCALER_UNIT', _ as error:                                  raise TypeError(F'Unknown type {error} for Scaler Unit')
            case 'SIGNED' as prop:                                           raise ValueError(F"Don't support set {prop}")
            case _:                                                          super().__setattr__(key, value)

    def validate_from(self, value: str, cursor_position: int) -> tuple[str, int]:
        """ return validated value and cursor position """
        if self.SCALER_UNIT:
            class WithScaler(self.__class__):
                SCALER_UNIT = self.SCALER_UNIT

            WithScaler(value=value)
        else:
            type(self)(value=value)
        return value, cursor_position

    def __hash__(self):
        return self.decode()


class Float(ABC):
    contents: bytes
    TAG: bytes

    @abstractmethod
    def __len__(self):
        """constant for contents length"""

    @property
    @abstractmethod
    def fraction_wide(self) -> int:
        """ constant for fraction wide """

    @property
    @abstractmethod
    def exponent_wide(self) -> int:
        """ constant for exponent wide """

    def __init__(self, value: bytes | bytearray | str | int | float | SimpleDataType = None):
        match value:
            case None:                                                             self.clear()
            case bytes() as encoding:
                length_and_contents = encoding[1:]
                match encoding[:1], len(self):
                    case self.TAG, int() if len(self) <= len(length_and_contents): self.contents = length_and_contents[:len(self)]
                    case self.TAG, _:                                              raise ValueError(F'Length of contents for {self.NAME} must be at least '
                                                                                                    F'{len(self)}, but got {len(length_and_contents)}')
                    case _ as wrong_tag, _:                                        raise TypeError(F'Expected {self.NAME} type, got {get_common_data_type_from(wrong_tag).NAME}')
            case bytearray():                                                      self.contents = bytes(value)  # Attention!!! changed method content getting from bytearray
            case str():                                                            self.contents = self.from_str(value)
            case int():                                                            self.contents = self.from_float(float(value))
            case float():                                                          self.contents = self.from_float(value)
            case Float():                                                          self.contents = value.contents
            case _:                                                                raise ValueError(F'Error create {self.NAME} with value {value}')

    def from_str(self, value: str) -> bytes:
        """ Input 1. float: <sign><integer>.<fraction>[e[-+]power] example: 1.0, -0.003, 1e+12, 4.5e-7
         2. hex_float:  <sign>0x<integer>.<fraction>p[+-]<power> example 0x1.e4d00p+15 (62056.0) """
        try:
            return self.from_float(float(value))
        except ValueError:
            return self.from_float(float.fromhex(value))
        except OverflowError:
            raise ValueError

    @property
    def encoding(self) -> bytes:
        """ The complete sequence of octets used to represent the data value. """
        return self.TAG + self.contents

    def from_float(self, value: float) -> bytes:
        """ Input float: <sign><integer>.<fraction>[e[-+]power] example: 1.0, -0.003, 1e+12, 4.5e-7 """
        if 'inf' in str(value):
            raise OverflowError(F'Float overflow error')
        hex_string = value.hex()
        sign, mantissa_and_exponent = hex_string.split('0x')
        sign = 1 << (len(self) * 8 - 1) if sign else 0
        mantissa, exponent = mantissa_and_exponent.split('p')
        integer, fraction = mantissa.split('.')
        integer = int(integer, base=16)
        exponent = (int(exponent) + 2 ** (len(self) - 1) - 1)
        if exponent >= 2 ** self.exponent_wide:
            raise OverflowError(F'Exponent overflow error')
        exponent <<= self.fraction_wide if integer else 0
        fraction_quartet_amount = ceil(self.fraction_wide / 4)
        offset = fraction_quartet_amount*4 - self.fraction_wide
        fraction = int(fraction[:fraction_quartet_amount], base=16) >> offset
        return (sign + exponent + fraction).to_bytes(len(self), 'big')

    def decode(self) -> float:
        """  return the build in float type IEEE 60559"""
        sign = self.contents[0] >> 7
        exponent = (int.from_bytes(self.contents[:2], 'big') & 0x7fff) >> (15 - self.exponent_wide)
        fraction = int.from_bytes(self.contents[1:], 'big') & (1 << self.fraction_wide)-1
        ret = 2 ** (exponent - 2**(self.exponent_wide-1)+1) * (1 + fraction/(1 << self.fraction_wide))
        if sign:
            ret *= -1
        return ret

    def validate_from(self, value: str, cursor_position=None) -> tuple[str, int]:
        # adding '0' for available set service symbols
        if value[-1] in '.-+exp':
            value += '0'
        return SimpleDataType(self).validate_from(value, cursor_position)

    def __str__(self):
        return str(self.decode())

    def clear(self):
        self.contents = bytes(len(self))


class LIST(ABC):
    """ Special class flag for enumeration any type """


class __DateTime(ABC):
    __len__: int
    _separators: tuple[str]
    contents: bytes
    TAG: bytes
    NAME: str

    def __init__(self, value: bytes | bytearray | str | int | bool | float | datetime.datetime | datetime.time | SimpleDataType):
        match value:  # TODO: replace priority case
            case bytes():
                length_and_contents = value[1:]
                match value[:1]:
                    case self.TAG if len(self) <= len(length_and_contents): self.contents = length_and_contents[:len(self)]
                    case self.TAG:                                                     raise ValueError(F'Length of contents for {self.NAME} must be at least '
                                                                                                        F'{len(self)}, but got {len(length_and_contents)}')
                    case _ as wrong_tag:                                               raise TypeError(F'Expected {self.NAME} type, got {get_common_data_type_from(wrong_tag).NAME}')
            case None:                                                                 self.clear()
            case bytearray():                                                          self.contents = bytes(value)  # Attention!!! changed method content getting from bytearray
            case str():                                                                self.contents = self.from_str(value)
            case datetime.datetime():                                                  self.contents = self.from_datetime(value)
            case datetime.date():                                                      self.contents = self.from_date(value)
            case datetime.time():                                                      self.contents = self.from_time(value)
            case self.__class__():                                                     self.contents = value.contents
            case _:                                                                    raise ValueError(F'Error create {self.NAME} with value {value}')

    @property
    def encoding(self) -> bytes:
        return self.TAG + self.contents

    @abstractmethod
    def from_str(self, value: str) -> bytes:
        """ typecast from string to bytes """

    def from_datetime(self, value: datetime.datetime) -> bytes:
        """ typecast from datetime to bytes """
        raise ValueError('"Date_time" type not supported')

    def from_date(self, value: datetime.date) -> bytes:
        """ typecast from date to bytes """
        raise ValueError('"Date" type not supported')

    def from_time(self, value: datetime.time) -> bytes:
        """ typecast from time to bytes """
        raise ValueError('"Time" type not supported')

    def separator_amount(self, string: str, amount: int = 0) -> int:
        """ returning sum of '.', ':', ' ' in string """
        for separator in set(self._separators):
            amount += string.count(separator)
        return amount

    def validate_from(self, value: str, cursor_position: int) -> tuple[str, int]:
        while len(value) > cursor_position and value[cursor_position] == '_':
            value = value[:cursor_position] + value[cursor_position+1:]
        while value[cursor_position-2] == '_':
            value = value[:cursor_position-2] + value[cursor_position-1:]
            cursor_position -= 1
        try:
            type(self)(value)
            return value, cursor_position
        except ValueError as e:
            try:
                with_separator = F'{value[:cursor_position-1]}{self._separators[self.separator_amount(value[:cursor_position])]}{value[cursor_position-1:]}'
                type(self)(with_separator)  # check possible
                return with_separator, cursor_position + (len(with_separator)-len(value))
            except IndexError:
                raise ValueError

    @abstractmethod
    def DEFAULT(self):
        """"""

    def clear(self):
        self.contents = self.DEFAULT


class __Date(ABC):
    """ years, month, day setters/getters for Date and DateTime """

    @property
    def year(self) -> int | None:
        """ return year if specific or None """
        match self.contents[0] * 256 + self.contents[1]:
            case 0xffff:    return None
            case _ as year: return year

    # TODO: add 0xfe, 0xfd code
    @property
    def month(self) -> Optional[int]:
        """ return month if specific or None """
        match self.contents[2]:
            case 0xff:                           return None
            case _ as month if 1 <= month <= 12: return month
            case _ as wrong_value:               raise ValueError(F'Got month={wrong_value} from {self.NAME} contents, must be: 1..12, fe, fd, ff')

    # TODO: add 0xfe, 0xfd code
    @property
    def day(self) -> Optional[int]:
        """ return day if specific or None """
        match self.contents[3]:
            case 0xff:                       return None
            case _ as day if 1 <= day <= 31: return day
            case _ as wrong_value:           raise ValueError(F'Got day={wrong_value} from {self.NAME} contents, must be: 1..31, fe, fd, ff')

    @property
    def weekday(self) -> Optional[int]:
        """ return weekday if specific or None """
        match self.contents[4]:
            case 0xff:                              return None
            case _ as weekday if 1 <= weekday <= 7: return weekday
            case _ as wrong_value:                  raise ValueError(F'Got weekday={wrong_value} from {self.NAME} contents, must be: 1..7, ff')

    def set_year(self, value: int):
        """ set day """
        if (9999 >= value > 1) or value == 0xffff:
            contents = bytearray(self.contents)
            contents[:2] = value.to_bytes(2, 'big')
            self.set(contents)
        else:
            raise ValueError(F'Year out of range, got {value}, expected 1..9999, 65535')

    def set_month(self, value: int):
        """ set month """
        if (12 >= value >= 1) or value == 0xff:
            contents = bytearray(self.contents)
            contents[2] = value
            self.set(contents)
        else:
            raise ValueError(F'Month out of range, got {value}, expected 1..12, 255')

    def set_day(self, value: int):
        """ set day """
        if (31 >= value >= 1) or value == 0xff:
            contents = bytearray(self.contents)
            contents[3] = value
            self.set(contents)
        else:
            raise ValueError(F'Day out of range, got {value}, expected 1..31, 255')

    def set_weekday(self, value: int):
        """ set weekday """
        if (7 >= value >= 1) or value == 0xff:
            contents = bytearray(self.contents)
            contents[4] = value
            self.set(contents)

    @abstractmethod
    def decode(self) -> datetime.datetime:
        """ return python time. Used 00 instead 'NOT SPECIFIED'  """

    @staticmethod
    def check_date(value: bytes):
        if len(value) != 5:
            raise ValueError(F'In the Date type expected length 5, but got {len(value)}')
        year_highbyte, year_lowbyte, month, day_of_month, day_of_week = \
            value[0:2].replace(b'\xff\xff', b'\x01\x00') + \
            value[2:4].replace(b'\xff', b'\x01').replace(b'\xfe', b'\x01').replace(b'\xfd', b'\x01') + \
            value[4:5].replace(b'\xff', b'\x01')
        if datetime.date(year_highbyte * 256 + year_lowbyte, month, day_of_month).weekday() != \
                day_of_week - 1 and value[4:] != b'\xff' and value[0:2] != b'\xff\xff' and \
                value[2:3] not in b'\xfd\xfe\xff' and value[2:3] not in b'\xfd\xfe\xff':
            raise ValueError('Error init Data: week day wrong')

    @property
    def strfdate(self):
        """ get date in format d.m.Y-A or d.m.Y or d.m """
        match self.contents[2]:
            case 0xff:  month = '__'
            case 0xfe:  month = 'begin'
            case 0xfd:  month = 'end'
            case value: month = str(value).zfill(2)
        match self.contents[3]:
            case 0xff:     month_day = '__'
            case 0xfe:     month_day = 'last'
            case 0xfd:     month_day = 'penult'
            case value:    month_day = str(value).zfill(2)
        match self.contents[4]:
            case 1:    weekday = '-пон'
            case 2:    weekday = '-вто'
            case 3:    weekday = '-сре'
            case 4:    weekday = '-чет'
            case 5:    weekday = '-пят'
            case 6:    weekday = '-суб'
            case 7:    weekday = '-вос'
            case 0xff: weekday = ''
            case value: raise ValueError(F'Got weekday={value}, expected 1..7, ff')
        match unpack('>h', self.contents[:2])[0]:
            case -1 if weekday == '': year = ''
            case -1:                  year = '.____'
            case value:               year = F'.{str(value).zfill(4)}'
        return F'{month_day}.{month}{year}{weekday}'

    @staticmethod
    def strpdate(value: str) -> bytes | tuple[bytes, str]:
        """ typecasting string to DLMS Date. Where: Y - year, m - month, d - month day, w - weekday """
        def from_year() -> tuple[int, int]:
            nonlocal Y
            match Y:
                case '' | '_' | '__' | '___' | '____':      return 0xff, 0xff
                case _ as y if y.isdigit() and len(y) <= 2: return divmod(int(y) + 2000, 0x100)
                case _ if Y.isdigit() and len(Y) <= 4:      return divmod(int(Y), 0x100)
                case _:                                     raise ValueError(F'Got wrong year={Y}')

        def from_month() -> int:
            nonlocal m
            match m:
                case '' | '_' | '__':                        return 0xff
                case _ if m.isdigit() and 1 <= int(m) <= 12: return int(m)
                case 'begin':                                return 0xfe
                case 'end':                                  return 0xfd
                case _:                                      raise ValueError(F'Got wrong month={m}')

        def from_monthday() -> int:
            nonlocal d
            match d:
                case '' | '_' | '__':                        return 0xff
                case _ if d.isdigit() and 1 <= int(d) <= 31: return int(d)
                case 'last':                                 return 0xfe
                case 'penult':                               return 0xfd
                case _:                                      raise ValueError(F'Got wrong monthday={d}')

        def from_weekday() -> int:
            nonlocal w
            match w.lower():
                case '' | '_' | '__':                                                                          return 0xff
                case _ if w.isdigit() and 1 <= int(w) <= 7:                                                    return int(w)
                case '1' | 'по' | 'пон' | 'понедельник' | 'mo' | 'mon' | 'monday':                             return 1
                case '2' | 'вт' | 'вто' | 'вторник' | 'tu' | 'tue' | 'tuesday':                                return 2
                case '3' | 'ср' | 'сре' | 'среда' | 'we' | 'wed' | 'wednesday':                                return 3
                case '4' | 'чт' | 'чет' | 'четверг' | 'th' | 'thu' | 'thursday':                               return 4
                case '5' | 'пт' | 'пят' | 'пятница' | 'fr' | 'fri' | 'friday':                                 return 5
                case '6' | 'сб' | 'суб' | 'суббота' | 'sa' | 'sat' | 'saturday':                               return 6
                case '7' | 'вс' | 'вос' | 'воскресенье' | 'su' | 'sun' | 'sunday' | '':                        return 7
                case _ if any(map(lambda pat: pat.startswith(w),
                                  ('понедельни', 'вторни', 'сред', 'четвер', 'пятниц', 'суббот', 'воскресень',
                                   'monda', 'tuesda', 'wednesda', 'thursda','frida','saturda', 'sunda'))):     return 0xff
                case _:                                                                                        raise ValueError(F'Got wrong weekday={w}')

        match separate(value, '.-', 3):
            case _,      (d,) if d.isdigit(): return bytes((0xff, 0xff,   0xff,         from_monthday(), 0xff))
            case _,      (w,):                return bytes((0xff, 0xff,   0xff,         0xff,            from_weekday()))
            case '.',    (d, m):              return bytes((0xff, 0xff,   from_month(), from_monthday(), 0xff))
            case '..',   (d, m, Y):           return bytes((*from_year(), from_month(), from_monthday(), 0xff))
            case '.-',   (d, m, w):           return bytes((0xff, 0xff,   from_month(), from_monthday(), from_weekday()))
            case '-.',   (w, d, m):           return bytes((0xff, 0xff,   from_month(), from_monthday(), from_weekday()))
            case '..-',  (d, m, Y, w):        return bytes((*from_year(), from_month(), from_monthday(), from_weekday()))
            case '-..',  (w, d, m, Y):        return bytes((*from_year(), from_month(), from_monthday(), from_weekday()))
            case _ as separate_result:        raise ValueError(F'Unknown date format: separators=<{separate_result[0]}>, values={", ".join(separate_result[1])}')


class __Time(ABC):
    """ hour, minute, second, hundredths setters/getters for Time and DateTime """
    contents: bytes

    @property
    def __contents_offset(self) -> int:
        """ return offset if type is DateTime """
        return 0 if len(self) == 4 else 5

    def set_hour(self, value: int):
        """ set hour """
        if (0 <= value <= 23) or value == 0xff:
            contents = bytearray(self.contents)
            contents[0+self.__contents_offset] = value
            self.set(contents)
        else:
            raise ValueError(F'Hour out of range, got {value}, expected 0..23, 255')

    def set_minute(self, value: int):
        """ set minute """
        if (0 <= value <= 59) or value == 0xff:
            contents = bytearray(self.contents)
            contents[1+self.__contents_offset] = value
            self.set(contents)
        else:
            raise ValueError(F'Minute out of range, got {value}, expected 0..59, 255')

    def set_hundredths(self, value: int):
        """ set hun """
        if (0 <= value <= 99) or value == 0xff:
            contents = bytearray(self.contents)
            contents[3+self.__contents_offset] = value
            self.set(contents)
        else:
            raise ValueError(F'Minute out of range, got {value}, expected 0..99, 255')

    @property
    def hour(self) -> int | None:
        """ return hour if specific or None """
        match self.contents[0+self.__contents_offset]:
            case 0xff:                    return None
            case _ as hour if hour <= 23: return hour
            case _ as wrong_value:        raise ValueError(F'Got hour={wrong_value} from {self.NAME} contents, must be: 0..23, ff')

    @property
    def minute(self) -> int | None:
        """ return minutes if specific or None """
        match self.contents[1+self.__contents_offset]:
            case 0xff:                        return None
            case _ as minute if minute <= 59: return minute
            case _ as wrong_value:            raise ValueError(F'Got minute={wrong_value} from {self.NAME} contents, must be: 0..59, ff')

    @property
    def second(self) -> int | None:
        """ return second if specific or None """
        match self.contents[2+self.__contents_offset]:
            case 0xff:                        return None
            case _ as second if second <= 59: return second
            case _ as wrong_value:            raise ValueError(F'Got second={wrong_value} from {self.NAME} contents, must be: 0..59, ff')

    @property
    def hundredths(self) -> int | None:
        """ return hundredths if specific or None """
        match self.contents[3+self.__contents_offset]:
            case 0xff:                                return None
            case _ as hundredths if hundredths <= 99: return hundredths
            case _ as wrong_value:                    raise ValueError(F'Got hundredths={wrong_value} from {self.NAME} contents, must be: 0..99, ff')

    def check_time(self):
        datetime.time(*tuple(self.contents[0+self.__contents_offset: 4+self.__contents_offset].replace(b'\xff', b'\x00')))

    @property
    def strftime(self) -> str:
        """ get time in format H:M:S.f or H:M:S or H:M """
        match self.contents[3+self.__contents_offset]:
            case 0xff:       hundredths = ''
            case _ as value: hundredths = F'.{str(value).zfill(2)}'
        match self.contents[2+self.__contents_offset]:
            case 0xff if hundredths == '': second = ''
            case 0xff:                     second = ':__'
            case _ as value:               second = F':{str(value).zfill(2)}'
        match self.contents[1+self.__contents_offset]:
            case 0xff:       minute = '__'
            case _ as value: minute = str(value).zfill(2)
        match self.contents[0+self.__contents_offset]:
            case 0xff:       hour = '__'
            case _ as value: hour = str(value).zfill(2)
        return F'{hour}:{minute}{second}{hundredths}'

    @staticmethod
    def strptime(value: str) -> bytes:
        """ typecasting string to DLMS Time. Where: H - hour, M - minute, S - second, f - hundredths """
        def from_hour() -> int:
            nonlocal H
            match H:
                case '' | '_' | '__':                        return 0xff
                case _ if H.isdigit() and 0 <= int(H) <= 23: return int(H)
                case _:                                      raise ValueError(F'Got wrong hour={H}')

        def from_minute() -> int:
            nonlocal M
            match M:
                case '' | '_' | '__':                        return 0xff
                case _ if M.isdigit() and 0 <= int(M) <= 59: return int(M)
                case _:                                      raise ValueError(F'Got wrong minute={M}')

        def from_second() -> int:
            nonlocal S
            match S:
                case '' | '_' | '__':                        return 0xff
                case _ if S.isdigit() and 0 <= int(S) <= 59: return int(S)
                case _:                                      raise ValueError(F'Got wrong second={S}')

        def from_hundredths() -> int:
            nonlocal f
            match f:
                case '' | '_' | '__':                    return 0xff
                case _ if f.isdigit() and len(f) <= 2: return int(f)
                case _:                                  raise ValueError(F'Got wrong hundredths={f}')

        match separate(value, ':.', 3):
            case _,     (H,):         return bytes((from_hour(), 0xff,          0xff,          0xff))
            case ':',   (H, M):       return bytes((from_hour(), from_minute(), 0xff,          0xff))
            case '.',   (S, f):       return bytes((0xff,        0xff,          from_second(), from_hundredths()))
            case '::',  (H, M, S):    return bytes((from_hour(), from_minute(), from_second(), 0xff))
            case ':.',  (M, S, f):    return bytes((0xff,        from_minute(), from_second(), from_hundredths()))
            case '::.', (H, M, S, f): return bytes((from_hour(), from_minute(), from_second(), from_hundredths()))
            case _ as separate_result: raise ValueError(F'Unknown time format: separators={separate_result[0]}, values={", ".join(separate_result[1])}')


class NullData(SimpleDataType):
    """ An ordered sequence of octets (8 bit bytes) """
    TAG = b'\x00'
    NAME = tn.NULL_DATA

    def __init__(self, value: bytes | str | NullData = None):
        match value:
            case bytes() if value[:1] == self.TAG: pass
            case bytes():                          raise TypeError(F'Expected {self.NAME} type, got {get_common_data_type_from(value[:1]).NAME}')
            case None | str() | NullData():        pass
            case _:                                raise ValueError(F'Error create {self.NAME} with value {value}')

    @property
    def contents(self) -> bytes: return b''

    def __str__(self): return 'null-data'

    def decode(self): return None

    @property
    def encoding(self) -> bytes: return b'\x00'

    def clear(self):
        """ nothing do it"""


class Array(__Array, ComplexDataType):
    """ The elements of the array are defined in the Attribute or Method description section of a COSEM IC
    specification """
    TYPE: Type[CommonDataType] = None
    values: list[CommonDataTypes]
    TAG: bytes = b'\x01'
    NAME = tn.ARRAY
    unique: bool = False
    """ True for arrays with unique elements """

    def __init__(self, value: bytes | list | None | Array = None):
        self.__dict__['values'] = list()
        match value:
            case bytes():
                match value[:1], value[1:]:
                    case self.TAG, length_and_contents:
                        length, pdu = get_length_and_pdu(length_and_contents)
                        if length and self.TYPE is None:
                            self.__dict__['TYPE'] = get_common_data_type_from(pdu[:1])
                        for number in range(length):
                            if pdu == b'':
                                raise ValueError(F'{self.NAME} Error of input data length: {number} instead {length}')
                            new_element, pdu = get_instance_and_pdu(self.TYPE, pdu)
                            self.append(new_element)
                    case b'', _:   raise ValueError(F'Wrong Value. Value not consist the tag. Empty Value.')
                    case _:        raise TypeError(F'Expected {self.NAME} type, got {get_common_data_type_from(value[:1]).NAME}')
            case list():           deque(map(self.append, value))
            case None:             """create empty array"""
            case Array():          self.__init__(value.encoding)  # TODO: make with bytearray
            case _:                raise TypeError(F'Init {self.__class__} with Value: "{value}" not supported')

    def __str__(self):
        return F'{self.NAME if self.TYPE is None else self.TYPE.NAME}[{len(self.values)}]'

    def append(self, element: CommonDataType | None | Any = None):
        """ append element to end """
        match element:
            case self.TYPE(): pass
            case None:        element = self.new_element()
            case _:           element = self.TYPE(element)
            # case _:           raise ValueError(F'Types not equal. Must be {self.type.NAME} got {type(element).__name__}')
        if self.unique and element in self.values:  # TODO: remove after full implement append_validate (see below)
            raise ValueError(F'Element {element.NAME} already exist in {self.NAME}')
        self.append_validate(element)
        self.values.append(element)

    def new_element(self) -> CommonDataType:
        """for override elements validator if it consist ID's. """
        return self.TYPE()

    def append_validate(self, element: CommonDataType):
        """validate before append last value. In override here need insert <raise> in some events and register callbacks"""

    def __setattr__(self, key, value: CommonDataType):
        match key:
            case 'TYPE' | 'values' as prop:                                         raise ValueError(F"Don't support set {prop}")
            case _:                                                                 super().__setattr__(key, value)

    def __getitem__(self, item: int) -> CommonDataTypes:
        """ get element by index """
        return self.values[item]

    def get_type(self) -> Type[CommonDataType]:
        return self.TYPE

    def set_type(self, value: Type[Structure] | Type[SimpleDataType]):
        """ set new type with clear array"""
        self.clear()
        self.__dict__['TYPE'] = value

    def decode(self) -> list:
        return [el.decode() for el in self.values]

    def set(self, value: bytes | bytearray | list | None):
        self.clear()
        if hasattr(self, 'cb_preset'):
            self.cb_preset(value)
        for el in Array(value):
            self.append(self.TYPE(el))
        if hasattr(self, 'cb_post_set'):
            self.cb_post_set()


@dataclass(frozen=True)
class StructElement:
    NAME: str
    TYPE: Type[CommonDataType]

    def __str__(self):
        return F'{self.NAME}: {self.TYPE.NAME}'


class AXDR(ABC):
    """ Use in structures for association LN objects """
    is_xdr: bool
    NAME = F'{tn.STRUCTURE} A-XDR'
    ELEMENTS: tuple[StructElement, ...]
    values: tuple[CommonDataType, None]

    def __init__(self, value: bytes = None):
        match value:
            case bytes() as encoding:
                tag, length_and_contents = encoding[:1], encoding[1:]
                match tag:
                    case b'\x09':
                        values = [None] * len(self.ELEMENTS)
                        self.__dict__['is_xdr'] = True
                        self.__dict__['TAG'] = b'\x09'
                        length, pdu = get_length_and_pdu(length_and_contents)
                        if length <= len(pdu):
                            xdr = pdu[:length]
                            values_in: deque[int] = deque(xdr)
                            values_index = iter(range(len(self.ELEMENTS)))
                            # ger first two values
                            two_values = divmod(values_in.popleft(), 40)
                            # self._set_value(next(values_index), two_values[0])
                            # self._set_value(next(values_index), two_values[1])
                            i = next(values_index)
                            values[i] = self.ELEMENTS[i].TYPE(two_values[0])
                            i = next(values_index)
                            values[i] = self.ELEMENTS[i].TYPE(two_values[1])
                            tmp = 0
                            while values_in:
                                tmp = (tmp & 0b0111_1111) << 7
                                if values_in[0] >= 0b1000_0000:
                                    tmp += values_in.popleft() & 0b0111_1111
                                else:
                                    tmp += values_in.popleft()
                                    # self._set_value(next(values_index), tmp)
                                    i = next(values_index)
                                    values[i] = self.ELEMENTS[i].TYPE(tmp)
                                    tmp = 0
                            self.__dict__['values'] = tuple(values)
                        else:
                            raise TypeError(F'Expected {self.NAME} type, got {get_common_data_type_from(encoding[:1]).NAME}')
                    case _:
                        self.__dict__['is_xdr'] = False
                        super(AXDR, self).__init__(value)
            case None:                                              self.__init__(self.default)

    @property
    def contents(self) -> bytes:
        if self.is_xdr:
            return self.get_a_xdr()
        else:
            return super(AXDR, self).contents


class Structure(ComplexDataType):
    """ The elements of the structure are defined in the Attribute or Method description section of a COSEM IC specification """
    TAG = b'\x02'
    NAME = tn.STRUCTURE
    ELEMENTS: tuple[StructElement, ...] = None
    values: tuple[CommonDataTypes, ...]
    default: bytes = None

    def __init__(self, value: bytes | tuple | list | None | bytearray | Structure = None):
        if value is None:
            value = self.default
        match value:
            case bytes():                  self.__from_bytes(value)
            case tuple() | list():         self.__from_sequence(value)
            case None:                     self.__dict__['values'] = tuple((el.TYPE() for el in self.ELEMENTS))
            case bytearray():              self.__from_bytearray(value)
            case Structure():              self.__from_bytearray(bytearray(value.contents))
            # case Structure():              self.__from_sequence(value)
            case _:                        raise TypeError(F'For {self.NAME} "{value=}" not supported')

    def __from_bytes(self, encoding: bytes):
        values = list()
        tag, length_and_contents = encoding[:1], encoding[1:]
        if tag != self.TAG:
            raise TypeError(F'Expected {self.NAME} type, got {get_common_data_type_from(tag).NAME}')
        length, pdu = get_length_and_pdu(length_and_contents)
        if self.ELEMENTS is None:
            el: list[StructElement] = list()
            for i in range(length):
                el.append(StructElement(F'#{i}', get_common_data_type_from(pdu[:1])))
                el_value, pdu = get_instance_and_pdu(el[i].TYPE, pdu)
                values.append(el_value)
            self.__dict__['ELEMENTS'] = tuple(el)
        else:
            if len(self) != length:
                raise ValueError(F'Struct {self.NAME} got length:{length}, expected length:{len(self)}')
            for el in self.ELEMENTS:
                el_value, pdu = get_instance_and_pdu(el.TYPE, pdu)
                values.append(el_value)
        self.__dict__['values'] = tuple(values)

    def __from_sequence(self, sequence: tuple):
        if len(sequence) != len(self):
            raise ValueError(F'Struct {self.__class__.__name__} got length:{len(sequence)}, expected length:{len(self)}')
        self.__dict__['values'] = tuple((el.TYPE(val) for val, el in zip(sequence, self.ELEMENTS)))

    def __from_bytearray(self, value: bytearray):
        values = list()
        pdu = bytes(value)
        for el in self.ELEMENTS:
            el_value, pdu = get_instance_and_pdu(el.TYPE, pdu)
            values.append(el_value)
        self.__dict__['values'] = tuple(values)

    def __len__(self):
        return len(self.ELEMENTS)

    def clear(self):
        for value in self.values:
            value.clear()

    def __str__(self):
        """ names with values elements """
        return F'{{{", ".join(map(str, self.values))}}}'

    def __setattr__(self, key, value: CommonDataType):
        """ don't support """
        raise ValueError(F'Unsupported change: {key}')

    def set_name(self, value: str):
        """use in ProfileGeneric for new CaptureObject"""
        self.__dict__["NAME"] = value

    def set(self, value: bytes | bytearray | tuple | list | None):
        for index, el_value in enumerate(self.get_types()(value)):
            self[index].set(el_value)

    @property
    def contents(self) -> bytes:
        """ ITU-T Rec. X.690 8.1.1 Structure of an encoding """
        return b''.join((value.encoding for value in self.values))

    @property
    def complex_data(self) -> bytes:
        return b''.join((value.contents for value in self.values))

    def __getitem__(self, item: int) -> CommonDataType:
        """ get element value by index """
        return self.values[item]

    def __setitem__(self, key: int, value: CommonDataType):
        """ set data to element by index. """
        if isinstance(value, self.ELEMENTS[key].TYPE):
            self.values[key] = value
        else:
            raise ValueError(F'Type got {value.NAME}, expected {self.ELEMENTS[key].TYPE.NAME}')

    def decode(self) -> tuple:
        return tuple(el.decode() for el in self.values)

    def get_a_xdr(self) -> bytes:
        """ use in AssociationLN """
        res = bytearray()
        res.append(40 * self.values[0].decode() + self.values[1].decode())
        for i in range(2, len(self.ELEMENTS)):
            value = self.values[i].decode()
            tmp = list()
            while value != 0 or not tmp:
                value, tmp1 = divmod(value, 128)
                tmp.append(tmp1)
                if len(tmp) != 1:
                    tmp[-1] |= 0b1000_0000
            while tmp:
                res.append(tmp.pop())
        return bytes(res)


class Boolean(SimpleDataType):
    """ boolean """
    TAG = b'\x03'
    NAME = tn.BOOLEAN

    def __init__(self, value: bytes | bytearray | str | int | bool | float | datetime.datetime | datetime.time | Boolean = None):
        match value:
            case None:                                                       self.clear()
            case bytes():                                                    self.contents = self.from_bytes(value)
            case bytearray():                                                self.contents = bytes(value)  # Attention!!! changed method content getting from bytearray
            case str():                                                      self.contents = self.from_str(value)
            case int():                                                      self.contents = self.from_int(value)
            case bool():                                                     self.contents = self.from_bool(value)
            case Boolean():                                                  self.contents = value.contents
            case _:                                                          raise ValueError(F'Error create {self.NAME} with value {value}')

    @property
    def encoding(self) -> bytes:
        return self.TAG + self.contents

    def from_bytes(self, encoding: bytes) -> bytes:
        """ return 0x00 from 0x00, 0x01 from 0x01..0xFF """
        tag, contents = encoding[:1], encoding[1:]
        if tag != self.TAG:
            raise TypeError(F'Expected {self.NAME} type, got {get_common_data_type_from(tag).NAME}')
        return b'\x00' if contents[:1] == b'\x00' else b'\x01'

    def from_str(self, value) -> bytes:
        if value == '0' or 'False'.startswith(value.title()) or 'Ложь'.startswith(value.title()) or \
                'No'.startswith(value.title()) or 'Нет'.startswith(value.title()):
            return b'\x00'
        elif value == '1' or 'True'.startswith(value.title()) or 'Правда'.startswith(value.title()) or \
                'Yes'.startswith(value.title()) or 'Да'.startswith(value.title()):
            return b'\x01'

    def from_bool(self, value: bool) -> bytes:
        return b'\x01' if value else b'\x00'

    def __str__(self):
        return str(self.decode())

    def decode(self) -> bool:
        """ decode to bool """
        return False if self.contents == b'\x00' else True

    def clear(self):
        self.contents = b'\x00'


class BitString(SimpleDataType):
    """ An ordered sequence of boolean values """
    TAG = b'\x04'
    NAME = tn.BIT_STRING
    __length: int
    default: bytes | bytearray | str | int = b'\x04\x00'

    def __init__(self, value: bytearray | bytes | str | int | BitString = None):
        match value:
            case None:
                new_instance = self.__class__(self.default)
                self.contents = new_instance.contents
                self.__length = len(new_instance)
            case bytes():                               self.contents = self.from_bytes(value)
            case bytearray():                           self.from_bytearray(value)
            case str():                                 self.contents = self.from_str(value)
            case int():                                 self.contents = self.from_int(value)
            case BitString():
                self.contents = value.contents
                self.__length = len(value)
            case _:                                     raise ValueError(F'Error create {self.NAME} with value {value}')

    def from_bytes(self, value: bytes) -> bytes:
        self.__length, pdu = get_length_and_pdu(value[1:])
        match value[:1]:
            case self.TAG if self.__length == 0:            return b''
            case self.TAG if self.__length <= len(pdu) * 8: return pdu[:ceil(self.__length / 8)]
            case self.TAG:                                  raise ValueError(F'Length is {self.__length}, but contents got only {len(pdu) * 8}')
            case _ as error:                                raise TypeError(F'Expected {self.NAME} type, got {get_common_data_type_from(error).NAME}')

    def from_str(self, value: str) -> bytes:
        self.__length = len(value)
        value = value + '0' * ((8 - self.__length) % 8)
        list_ = [value[count:(count + 8)] for count in range(0, self.__length, 8)]
        value = b''
        for byte in list_:
            value += int(byte, base=2).to_bytes(1, byteorder='little')
        return value

    def from_int(self, value: int) -> bytes:
        """ TODO: see like as Conformance """
        raise TypeError('not supported init from int')

    def from_bytearray(self, value: bytearray) -> bytes:
        self.__length = len(value) << 3
        return bytes(value)

    def set(self, value: BitString | bytes | bytearray | str | int | bool | float | datetime.date | None):
        """ TODO: partly copypast of SimpleDataType"""
        new_value = self._new_instance(value)
        if hasattr(self, 'cb_preset'):
            self.cb_preset(new_value)
        self.__dict__['contents'] = new_value.contents
        self.__length = len(new_value)
        if hasattr(self, 'cb_post_set'):
            self.cb_post_set()

    def __setitem__(self, key: int, value: int | bool):
        tmp = self.decode()
        tmp[key] = int(value)
        self.set(''.join(map(str, tmp)))

    def inverse(self, index: int):
        """ inverse one bit by index"""
        self[index] = not self.decode()[index]

    def __lshift__(self, other):
        for i in range(other):
            tmp: list[int] = self.decode()
            tmp.append(tmp.pop(0))
            self.set(''.join(map(str, tmp)))

    def __rshift__(self, other):
        for i in range(other):
            tmp: list[int] = self.decode()
            tmp.insert(0, tmp.pop())
            self.set(''.join(map(str, tmp)))

    def __len__(self):
        return self.__length

    def __setattr__(self, key, value):
        match key:
            case 'LENGTH' as prop: raise ValueError(F"Don't support set {prop}")
            case _:                super().__setattr__(key, value)

    def clear(self):
        """set all bits as 0"""
        for i in range(len(self)):
            self[i] = 0

    @property
    def encoding(self) -> bytes:
        return self.TAG + encode_length(len(self)) + self.contents

    def __str__(self):
        """ TODO: copypast FlagMixin"""
        return ''.join(map(str, self.decode()))

    def __getitem__(self, item) -> bytes:
        """ get bit from contents by index """
        return int(str(self)[item]).to_bytes(1, 'big')

    def decode(self) -> list[int]:
        """ TODO: copypast FlagMixin """
        ret = list()
        for byte_ in self.contents:
            ret.extend([(byte_ >> it) & 0b00000001 for it in range(7, -1, -1)])
        return ret[:len(self)]

    def validate_from(self, value: str, cursor_position: int) -> tuple[str, int]:
        """ return validated value and cursor position. TODO: copypast FlagMixin """
        type(self)(value=value)
        return value, cursor_position


class DoubleLong(Digital, SimpleDataType):
    """ Integer32 -2 147 483 648… 2 147 483 647 """
    TAG = b'\x05'
    NAME = tn.DOUBLE_LONG
    SIGNED = True
    LENGTH = 4


class DoubleLongUnsigned(Digital, SimpleDataType):
    """ Unsigned32 0…4 294 967 295 """
    TAG = b'\x06'
    NAME = tn.DOUBLE_LONG_UNSIGNED
    SIGNED = False
    LENGTH = 4


class OctetString(_String, SimpleDataType):
    """ An ordered sequence of octets (8 bit bytes) """
    TAG = b'\x09'
    NAME = tn.OCTET_STRING

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

    def validate_from(self, value: str, cursor_position=None) -> tuple[str, int]:
        try:
            correct = type(self)(value)
            return str(correct), cursor_position + (len(str(correct))-len(value))
        except ValueError:
            cursor_position: int = len(value)-1 if cursor_position is None else cursor_position
            type(self)(F'{value[:cursor_position]}0{value[cursor_position:]}')  # check possible
            return value, cursor_position

    # TODO: return value must be bytes or bytearray
    def decode(self) -> bytes:
        """ decode to build in bytes type """
        return bytes(self)

    def to_str(self, encoding: str = 'cp1251') -> str:
        """ decode to cp1251 by default, replace to '?' if unsupported """
        temp = list()
        for i in self.contents:
            temp.append(i if i > 32 else 63)
        return bytes(temp).decode(encoding)

    def __bytes__(self):
        return self.contents


class VisibleString(_String, SimpleDataType):
    """ An ordered sequence of octets (8 bit bytes) """
    TAG = b'\x0A'
    NAME = tn.VISIBLE_STRING

    def from_str(self, value: str) -> bytes:
        return bytes(value, 'cp1251')

    def from_int(self, value: int) -> bytes:
        return bytes(str(value), 'cp1251')

    def __str__(self):
        return bytes([char if char >= 0x20 else 63 for char in self.contents]).decode(encoding='cp1251')

    def __len__(self):
        return len(self.contents)

    def decode(self, encoding: str = 'cp1251') -> str:
        """ decode to cp1251 by default, replace to '?' if unsupported """
        temp = list()
        for i in self.contents:
            temp.append(i if i >= 32 else 63)
        return bytes(temp).decode(encoding)

    def to_str(self) -> str:
        return self.decode()


# TODO:  Utf8String will make differed from OctetString
class Utf8String(_String, SimpleDataType):
    """ An ordered sequence of characters encoded as UTF-8 """
    TAG = b'\x0c'
    NAME = tn.UTF8_STRING

    def from_str(self, value: str) -> bytes:
        return bytes(value, 'cp1251')

    def from_int(self, value: int) -> bytes:
        return bytes(str(value), 'cp1251')

    def __str__(self):
        return self.contents.decode('cp1251')

    def __len__(self):
        return len(self.contents)

    # TODO: make it
    def decode(self) -> int | list | None:
        raise ValueError("don't implement method")

# TODO: Bcd need more do here, now realisation like as Enum


class Bcd(SimpleDataType):
    """ binary coded decimal """
    TAG = b'\x0d'
    NAME = tn.BCD

    def __init__(self, value: bytes | bytearray | str | int | Bcd = None):
        match value:  # TODO: replace priority case
            case None: bytes(self.contents_length)
            case bytes():                                                    self.contents = self.from_bytes(value)
            case bytearray():                                                self.contents = bytes(value)
            case str():                                                      self.contents = self.from_str(value)
            case int():                                                      self.contents = self.from_int(value)
            case Bcd():                                                      self.contents = value.contents
            case _:                                                          raise ValueError(F'Error create {self.NAME} with value {value}')

    def from_bytes(self, encoding: bytes) -> bytes:
        """ Full encoding receiver: Tag+Length+Content """
        length_and_contents = encoding[1:]
        match encoding[:1], self.contents_length:
            case self.TAG, int() if self.contents_length <= len(length_and_contents): return length_and_contents[:self.contents_length]
            case self.TAG, _:                                                         raise ValueError(F'Length of contents for {self.NAME} must be at least '
                                                                                                       F'{self.contents_length}, but got {len(length_and_contents)}')
            case _ as wrong_tag, _:                                                   raise TypeError(F'Expected {self.NAME} type, got {get_common_data_type_from(wrong_tag).NAME}')

    @property
    def encoding(self) -> bytes:
        return self.TAG + self.contents

    def clear(self):
        self.contents = b'\x00'

    @property
    def contents_length(self) -> int: return 1

    def from_str(self, value: str) -> bytes:
        try:
            return int(value).to_bytes(1, 'little')
        except OverflowError:
            raise ValueError('Value out of range')

    def from_int(self, value: int) -> bytes:
        try:
            return value.to_bytes(1, 'little')
        except OverflowError:
            raise ValueError(F'value: {value} not in range')

    def __str__(self):
        return str(int.from_bytes(self.contents, byteorder='little'))

    # TODO: make it
    def decode(self) -> int | list | None:
        raise ValueError("don't implement method")


class Integer(Digital, SimpleDataType):
    """ Integer8 -128…127"""
    TAG = b'\x0f'
    NAME = tn.INTEGER
    SIGNED = True
    LENGTH = 1


class Long(Digital, SimpleDataType):
    """ Integer16 -32 768…32 767 """
    TAG = b'\x10'
    NAME = tn.LONG
    SIGNED = True
    LENGTH = 2


class Unsigned(Digital, SimpleDataType):
    """ Unsigned8 0…255 """
    TAG = b'\x11'
    NAME = tn.UNSIGNED
    SIGNED = False
    LENGTH = 1


class LongUnsigned(Digital, SimpleDataType):
    """ Unsigned16 0…65535"""
    TAG = b'\x12'
    NAME = tn.LONG_UNSIGNED
    SIGNED = False
    LENGTH = 2


class CompactArray(__Array, ComplexDataType):
    """ Provides an alternative, compact encoding of complex data. TODO: need test, may be don't work """
    TAG = b'\x13'
    NAME = tn.COMPACT_ARRAY

    def __init__(self, elements_type: Type[SimpleDataType | Structure],
                 elements: list[SimpleDataType | Structure] = None,
                 length: Optional[int] = None):
        super(CompactArray, self).__init__(elements_type, elements, length)
        dummy_type_instance = elements_type()
        self.__element_types = b'' if not len(dummy_type_instance) else \
            b''.join([dummy_type_instance.length] + [element.TAG for element in dummy_type_instance.ELEMENTS])

    @property
    def contents(self) -> bytes:
        return b''.join([element.complex_data for element in self.elements])

    @property
    def encoding(self) -> bytes:
        """ self encoding fof compact array """
        return self.TAG + self.__type.TAG + self.__element_types + encode_length(len(self.elements)) + self.contents

    # TODO: make it
    def decode(self) -> int | list | None:
        raise ValueError("don't implement method")


class Long64(Digital, SimpleDataType):
    """ Integer64 - 2**63…2**63-1 """
    TAG = b'\x14'
    NAME = tn.LONG64
    SIGNED = True
    LENGTH = 8


class Long64Unsigned(Digital, SimpleDataType):
    """ Unsigned64 0…2^64-1 """
    TAG = b'\x15'
    NAME = tn.LONG64_UNSIGNED
    SIGNED = False
    LENGTH = 8


class Enum(SimpleDataType, ABC):
    """ The elements of the enumeration type are defined in the “Attribute description” section of a COSEM interface class specification """
    contents: bytes
    TAG = b'\x16'
    NAME = tn.ENUM
    ELEMENTS: dict[bytes, str] = None
    __match_args__ = ('value', )

    def __init__(self, value: bytes | bytearray | str | int | Enum = None):
        match value:  # TODO: replace priority case
            case bytes() as encoding:
                match encoding[:1]:
                    case self.TAG if len(encoding) >= 2:                  self.contents = encoding[1:2]
                    case self.TAG:                                        raise ValueError(F'Length of contents for {self.NAME} must be at least 1, but got {len(encoding[1:])}')
                    case _ as wrong_tag:                                  raise TypeError(F'Expected {self.NAME} type, got {get_common_data_type_from(wrong_tag).NAME}')
            case bytearray():                                             self.contents = bytes(value)
            case None:                                                    self.contents = self.from_none()
            case str():                                                   self.contents = self.from_str(value)
            case int():                                                   self.contents = self.from_int(value)
            case self.__class__():                                        self.contents = value.contents
            case _:                                                       raise ValueError(F'Unknown type for {self.NAME} with value {value}<{value.__class__}>')
        if self.ELEMENTS is not None:
            self.validation()

    def from_int(self, value: int) -> bytes:
        try:
            return value.to_bytes(1, 'little')
        except OverflowError:
            raise ValueError(F'value: {value} not in range')

    def from_str(self, value: str) -> bytes:
        if value.isdigit():
            return self.from_int(int(value))
        else:
            for enum in self.ELEMENTS:
                if value == self.ELEMENTS[enum]:
                    return enum
            else:
                raise ValueError(F'Error create {self.NAME} with value {value}')

    def from_none(self):
        """first key value"""
        return next(iter(self.ELEMENTS))

    def validation(self):
        """ check value after inited. Maybe override """
        try:
            if self.contents not in self.ELEMENTS.keys():
                raise ValueError(F'Enum {self.NAME} has only {",".join([key.hex() for key in self.ELEMENTS])} key, '
                                 F'but got {self.contents[:1].hex()}')
        except AttributeError:
            logger.error("default enum values don't set. Look why...")

    def __init_subclass__(cls, elements: dict[bytes, str] = None, **kwargs):
        """ used for reinit elements of parent class """
        match elements:
            case dict():
                if issubclass(cls.__base__, Enum):
                    cls.ELEMENTS = cls.__base__.ELEMENTS.copy()
                    cls.ELEMENTS.update(elements)
                else:
                    ValueError(F'Error Init {cls=} with {cls.__base__=}')
            case _: pass

    @property
    def encoding(self) -> bytes:
        return self.TAG + self.contents

    def __setattr__(self, key, value):
        match key:
            case 'ELEMENTS' as prop: raise ValueError(F"Don't support set {prop}")
            case _: super().__setattr__(key, value)

    def __str__(self):
        return self.ELEMENTS[self.contents]

    @property
    def value(self) -> str:
        """ enum value name by according dlms """
        return str(self)

    def validate_from(self, value: str, cursor_position=None):
        """ return 'Ok' if string is valid else return valid Str """
        try:
            type(self)(value=value)
            return value, cursor_position
        except ValueError as e:
            for index in self.ELEMENTS:
                if self.ELEMENTS[index].startswith(value):
                    return value, cursor_position
            else:
                raise ValueError

    @classmethod
    def get_values(cls) -> List[str]:
        """ TODO: """
        return [values_dict for values_dict in cls.ELEMENTS.values()]

    def decode(self) -> int:
        """ return the build in integer type """
        return int(self)

    def __int__(self):
        return int.from_bytes(self.contents, 'big')

    def __gt__(self, other: Enum):
        return self.contents > other.contents

    def __hash__(self):
        return int(self)

    def clear(self):
        """ nothing do it. TODO: may be to default? """


class Float32(Float, SimpleDataType):
    """ Floating point number formats are defined in ISO/IEC/IEEE 60559:2011
    Format: <s><e{8}><F{23}>.  Where:
        - s is the sign bit;
        - e is the exponent; it is 8 bits wide and the exponent bias is +127;
        - f is the fraction, it is 23 bits.
        Value = (-1)**s * 2**(e-127) * 1.f """
    TAG = b'\x17'
    NAME = tn.FLOAT32

    @property
    def __len__(self): return 4

    @property
    def fraction_wide(self) -> int: return 23

    @property
    def exponent_wide(self) -> int: return 8

    # def validate_from(self, value: str, cursor_position=None) -> tuple[str, int]:
    #     value = self.additional_string_verification(value)
    #     return super(Float32, self).validate_from(value, cursor_position)


class Float64(Float, SimpleDataType):
    """ Floating point number formats are defined in ISO/IEC/IEEE 60559:2011
    Format: <s><e{11}><F{52}>.  Where:
        - s is the sign bit;
        - e is the exponent; it is 11 bits wide and the exponent bias is +1023;
        - f is the fraction, it is 52 bits.
        Value = (-1)**s * 2**(e-1023) * 1.f """
    TAG = b'\x18'
    NAME = tn.FLOAT64

    @property
    def __len__(self): return 8

    @property
    def fraction_wide(self) -> int: return 52

    @property
    def exponent_wide(self) -> int: return 11

    # def validate_from(self, value: str, cursor_position=None) -> tuple[str, int]:
    #     value = self.additional_string_verification(value)
    #     return super(Float64, self).validate_from(value, cursor_position)


class DateTime(__DateTime, __Date, __Time, SimpleDataType):
    # http://localhost:8081/Blue_Book_Ed14-2020.pdf
    """ DLMS BlueBook(IEC 62056-6-2) 13.0 4.1.5 Common data types
    OCTET STRING (SIZE(12))  { year highbyte, year lowbyte, month, day of month, day of week, hour,
        minute, second, hundredths of second, deviation highbyte, deviation lowbyte, clock status}
    The elements of date and time are encoded as defined above. Some may be set to “not specified” as defined above.
    In addition:
        deviation: interpreted as long range -720…+720 in minutes of local time to UTC 0x8000 = not specified
            Deviation highbyte and deviation lowbyte represent the 2 bytes of the long.
        Clock_status interpreted as unsigned. The bits are defined as follows:
            bit 0 (LSB): invalid value,
            bit 1: doubtful value,
            bit 2: different clock base,
            bit 3: invalid clock status,
            bit 4: reserved,
            bit 5: reserved,
            bit 6: reserved,
            bit 7 (MSB): daylight saving active
            0xFF = not specified
            Time could not be recovered after an incident. Detailed conditions are manufacturer specific (for example
                after the power to the clock has been interrupted). For a valid status, bit 0 shall not be set if bit 1
                is set.
            b Time could be recovered after an incident but the value cannot be guaranteed. Detailed conditions are
                manufacturer specific. For a valid status, bit 1 shall not be set if bit 0 is set.
            c Bit is set if the basic timing information for the clock at the actual moment is taken from a timing
                source different from the source specified in clock_base.
            d This bit indicates that at least one bit of the clock status is invalid. Some bits may be correct.
                The exact meaning shall be explained in the manufacturer’s documentation.
            e Flag set to true: the transmitted time contains the daylight saving deviation (summer time).
                Flag set to false: the transmitted time does not contain daylight saving deviation (normal time)."""
    TAG = b'\x19'
    NAME = tn.DATE_TIME
    _separators = ('.', '.', '-', ' ', ':', ':', '.', ' ')

    def __init__(self, value: datetime.datetime | datetime.date | bytearray | bytes | str = None):
        super(DateTime, self).__init__(value)
        self.check_date(self.contents[0:5])
        self.check_time()

    def __len__(self) -> int: return 12

    @property
    def DEFAULT(self): return b'\x07\xe4\x01\x01\xff\x00\x00\x00\x00\x00\xb4\xff'

    def from_str(self, value: str) -> bytes:
        def from_deviation() -> bytes:
            nonlocal dev
            match dev:
                case '':  return b'\x80\x00'
                case '-': return b'\x00\x00'
                case _ if dev.isdigit() and -720 <= int(dev) <= 720:   return pack('>H', int(dev))
                case _:           raise ValueError

        match value.split(sep=' ', maxsplit=2):
            case date, time, dev: return self.strpdate(date) + self.strptime(time) + from_deviation() + b'\xff'
            case date, time:      return self.strpdate(date) + self.strptime(time) + b'\x80\x00\xff'
            case date, :          return self.strpdate(date) + b'\xff\xff\xff\xff\x80\x00\xff'
            case ['']:            return b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\x80\x00\xff'
            case _:               raise ValueError(F'a lot of separators')

    def from_datetime(self, value: datetime.datetime) -> bytes:
        """ convert from build to DLMS datetime, weekday not set for uniquely datetime """
        match value.utcoffset():
            case None: deviation = 0x8000
            case _:    deviation = value.utcoffset().seconds // 60
        return pack('>HBBBBBBBH',
                    value.year,
                    value.month,
                    value.day,
                    255,
                    value.hour,
                    value.minute,
                    value.second,
                    value.microsecond//10_000,
                    deviation)+b'\xFF'

    def from_date(self, value: datetime.date) -> bytes:
        return bytes(((value.year >> 8) & 0xFF, value.year & 0xFF, value.month, value.day, value.weekday() + 1)) + b'\xFF\xFF\xFF\xFF\x80\x00\xFF'

    def from_time(self, value: datetime.time) -> bytes:
        return b'\xFF\xFF\xFF\xFF\xFF'+bytes((value.hour, value.minute, value.second, value.microsecond // 10_000)) + \
               b'\x80\x00\xFF'

    def set_clock_status(self, value: str | int):
        """ now only set value """
        self.contents = self.contents[:12] + int(value).to_bytes(1, 'big')

    def __str__(self):
        match unpack('>h', self.contents[9:11])[0]:
            case -0x8000:     deviation = ''
            case _ as value: deviation = str(value)
        return F'{self.strfdate} {self.strftime} {deviation}'

    def is_default_value(self) -> bool:
        return True if self.contents == b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\x80\x00\xff' else False

    def decode(self) -> datetime.datetime:
        year_highbyte, year_lowbyte, month, day_of_month, _, hour, minute, second, hundredths, deviation_highbyte, deviation_lowbyte, _ = self.contents
        year = year_highbyte*256+year_lowbyte
        deviation = deviation_highbyte*256 + deviation_lowbyte
        return datetime.datetime(year=year if year != 0xffff else datetime.MINYEAR,
                                 month=month if month not in {0xff, 0xfe, 0xfd} else 1,
                                 day=day_of_month if day_of_month not in {0xff, 0xfe, 0xfd} else 1,
                                 hour=hour if hour != 0xff else 0,
                                 minute=minute if minute != 0xff else 0,
                                 second=second if second != 0xff else 0,
                                 microsecond=hundredths*10000 if hundredths != 0xff else 0,
                                 tzinfo=datetime.timezone.utc if deviation == 0x8000 else datetime.timezone(datetime.timedelta(minutes=deviation)))

    @property
    def time_zone(self) -> Optional[datetime.timezone]:
        """ Return timezone from deviation """
        deviation = self.contents[9]*256 + self.contents[10]
        if deviation == 0x8000:
            return None
        elif -720 <= deviation >= 720:
            return datetime.timezone(datetime.timedelta(minutes=deviation))
        else:
            raise ValueError(F'Deviation must be from -720..720 got {deviation}')

    def get_left_nearest_date(self, point: datetime.datetime) -> Optional[datetime.datetime]:
        """ search and return date(datetime format) in left from point """
        l_point: datetime.datetime = self.decode()
        """ time in left from point """
        months = range(point.month, 0, -1) if self.month is None else (self.month,)
        """ months sequence from 12 to 1 with start from current month or self month """
        days = range(point.day, 0, -1) if self.day is None else (self.day,)
        """ days sequence from 31 to 1 with start from current day or self day """
        for year in range(point.year, datetime.MINYEAR, -1) if self.year is None else (self.year, ):
            l_point = l_point.replace(year=year)
            for month in months:
                l_point = l_point.replace(month=month)
                for day in days:
                    l_point = l_point.replace(day=day)
                    if l_point > point:
                        continue
                    elif self.weekday is not None and self.weekday != (l_point.weekday() + 1):
                        continue
                    else:
                        return l_point
                days = range(31, 0, -1) if self.day is None else point.day,
            months = range(12, 0, -1) if self.month is None else point.month,
        return None

    def get_left_nearest_datetime(self, point: datetime.datetime) -> Optional[datetime.datetime]:
        """ search and return datetime in left from point """
        l_point: datetime.datetime = self.get_left_nearest_date(point)
        """ time in left from point """
        is_this_day: bool = l_point.date() == point.date()
        """ flag of points equaling """
        if l_point is None:
            return None
        for hour in range(point.hour if is_this_day else 23, -1, -1) if self.hour is None else (self.hour,):
            l_point = l_point.replace(hour=hour)
            for minute in range(point.minute if is_this_day and l_point.hour == point.hour else 59, -1, -1) if self.minute is None else (self.minute,):
                l_point = l_point.replace(minute=minute)
                for second in range(point.second if is_this_day and l_point.hour == point.hour and
                                    l_point.minute == point.minute else 59, -1, -1) if self.second is None else (self.second,):
                    l_point = l_point.replace(second=second)
                    for microsecond in range(point.microsecond if is_this_day and l_point.hour == point.hour and
                                             l_point.minute == point.minute and
                                             l_point.second == point.second else 990000, -1, -10000) if self.hundredths is None else (self.hundredths * 10000,):
                        l_point = l_point.replace(microsecond=microsecond)
                        if l_point > point:
                            continue
                        else:
                            return l_point
        return None


class Date(__DateTime, __Date, SimpleDataType):
    """ DLMS BlueBook(IEC 62056-6-2) 13.0 4.1.5 Common data types
    OCTET STRING (SIZE(5)) {year high_byte, year low_byte, month, day of month, day of week} Where:
        year: interpreted as long-unsigned range 0…big 0xFFFF = not specified
            year high_byte and year low_byte represent the 2 bytes of the long-unsigned
        month: interpreted as unsigned range 1…12, 0xFD, 0xFE, 0xFF 1 is January
            0xFD = daylight_savings_end
            0xFE = daylight_savings_begin
            0xFF = not specified
        dayOfMonth: interpreted as unsigned range 1…31, 0xFD, 0xFE, 0xFF
            0xFD = 2nd last day of month
            0xFE = last day of month
            0xE0 to 0xFC = reserved
            0xFF = not specified
        dayOfWeek: interpreted as unsigned range 1…7, 0xFF 1 is Monday
            0xFF = not specified"""
    TAG = b'\x1a'
    NAME = tn.DATE
    _separators = ('.', '.', '-')

    def __init__(self, value: datetime.datetime | datetime.date | bytearray | bytes | str | int = None):
        super(Date, self).__init__(value)
        self.check_date(self.contents)

    @property
    def DEFAULT(self): return b'\x07\xe4\x01\x01\x03'

    def __len__(self) -> int: return 5

    def from_str(self, value: str) -> bytes:
        return self.strpdate(value)

    def from_datetime(self, value: datetime.datetime) -> bytes:
        return bytes(((value.year >> 8) & 0xFF, value.year & 0xFF, value.month, value.day, value.weekday() + 1))

    def from_date(self, value: datetime.date) -> bytes:
        return bytes(((value.year >> 8) & 0xFF, value.year & 0xFF, value.month, value.day, value.weekday() + 1))

    def decode(self) -> datetime.date:
        year_highbyte, year_lowbyte, month, day_of_month, _ = self.contents
        year = year_highbyte*256+year_lowbyte
        return datetime.date(year=year if year != 0xffff else datetime.MINYEAR,
                             month=month if month not in {0xff, 0xfe, 0xfd} else 1,
                             day=day_of_month if day_of_month not in {0xff, 0xfe, 0xfd} else 1)

    def __str__(self):
        return self.strfdate


class Time(__DateTime, __Time, SimpleDataType):
    """ DLMS BlueBook(IEC 62056-6-2) 13.0 4.1.5 Common data types
    {hour, minute, second, hundredths} Where:
    hour: interpreted as unsigned range 0…23, 0xFF,
    minute: interpreted as unsigned range 0…59, 0xFF,
    second: interpreted as unsigned range 0…59, 0xFF,
    hundredths: interpreted as unsigned range 0…99, 0xFF
    For hour, minute, second and hundredths: 0xFF = not specified.
    For repetitive times the unused parts shall be set to “not specified”."""
    TAG = b'\x1b'
    NAME = tn.TIME
    _separators = (':', ':', '.')

    def __init__(self, value: datetime.datetime | datetime.time | bytearray | bytes | str = None):
        super(Time, self).__init__(value)
        self.check_time()

    def __len__(self) -> int: return 4

    @property
    def DEFAULT(self): return b'\x00\x00\x00\x00'

    def from_str(self, value: str) -> bytes:
        return self.strptime(value)

    def from_datetime(self, value: datetime.datetime) -> bytes:
        return bytes((value.hour, value.minute, value.second, value.microsecond // 10_000))

    def from_time(self, value: datetime.time) -> bytes:
        return bytes((value.hour, value.minute, value.second, value.microsecond // 10_000))

    def __str__(self):
        return self.strftime

    def decode(self) -> datetime.time:
        """ return python time. Used 00 instead 'NOT SPECIFIED'  """
        hour, minute, second, hundredths = self.contents
        return datetime.time(hour=hour if hour != 0xff else 0,
                             minute=minute if minute != 0xff else 0,
                             second=second if second != 0xff else 0,
                             microsecond=hundredths*10000 if hundredths != 0xff else 0)

    def get_left_nearest_time(self, point: datetime.time) -> Optional[datetime.time]:
        """ search and return time in left from point """
        l_point: datetime.time = self.decode()
        """ time in left from point """
        for hour in range(point.hour, -1, -1) if self.hour is None else (self.hour,):
            l_point = l_point.replace(hour=hour)
            for minute in range(point.minute if l_point.hour == point.hour else 59, -1, -1) if self.minute is None else (self.minute,):
                l_point = l_point.replace(minute=minute)
                for second in range(point.second if l_point.hour == point.hour and
                                    l_point.minute == point.minute else 59, -1, -1) if self.second is None else (self.second,):
                    l_point = l_point.replace(second=second)
                    for microsecond in range(point.microsecond if l_point.hour == point.hour and
                                             l_point.minute == point.minute and
                                             l_point.second == point.second else 990000, -1, -10000) if self.hundredths is None else (self.hundredths * 10000,):
                        l_point = l_point.replace(microsecond=microsecond)
                        if l_point > point:
                            continue
                        else:
                            return l_point
        return None


__types: Dict[bytes, Type[CommonDataType]] = {dlms_type.TAG: dlms_type for dlms_type in chain(SimpleDataType.__subclasses__(), ComplexDataType.__subclasses__())}
""" Common data type dictionary """


CommonDataTypes: TypeAlias = NullData | Array | Structure | Boolean | BitString | DoubleLong | DoubleLongUnsigned | OctetString | VisibleString | Utf8String | Bcd | Integer | \
                             Long | Unsigned | LongUnsigned | CompactArray | Long64 | Long64Unsigned | Enum | Float32 | Float64 | DateTime | Date | Time


class Unit(Enum):
    ELEMENTS = {b'\x01': en.TIME_YEAR,
                b'\x02': en.TIME_MONTH,
                b'\x03': en.TIME_WEEK,
                b'\x04': en.TIME_DAY,
                b'\x05': en.TIME_HOUR,
                b'\x06': en.TIME_MINUTE,
                b'\x07': en.TIME_SECOND,
                b'\x08': en.PHASE_ANGLE_DEGREE,
                b'\x09': en.TEMPERATURE,
                b'\x0a': en.LOCAL_CURRENCY,
                b'\x0b': en.LENGTH_METRE,
                b'\x0c': en.SPEED_METRE_PER_SECOND,
                b'\x0d': en.VOLUME_VALUE_CUBIC_METRE,
                b'\x0e': en.CORRECTED_VOLUME_CUBIC_METRE,
                b'\x0f': en.VOLUME_FLUX_CUBIC_METRE_PER_HOUR,
                b'\x10': en.CORRECTED_VOLUME_FLUX_CUBIC_METRE_PER_HOUR,
                b'\x11': en.VOLUME_FLUX_CUBIC_METRE_PER_DAY,
                b'\x12': en.CORRECTED_VOLUME_FLUX_CUBIC_METRE_PER_DAY,
                b'\x13': en.VOLUME_LITRE,
                b'\x14': en.MASS_KILOGRAM,
                b'\x15': en.FORCE_NEWTON,
                b'\x16': en.ENERGY_NEWTON_METER,
                b'\x17': en.PRESSURE_PASCAL,
                b'\x18': en.PRESSURE_BAR,
                b'\x19': en.ENERGY_JOULE,
                b'\x1a': en.THERMAL_POWER_RATE_OF_CHANGE_JOULE_PER_HOUR,
                b'\x1b': en.ACTIVE_POWER_WATT,
                b'\x1c': en.APPARENT_POWER_VOLT_AMPERE,
                b'\x1d': en.REACTIVE_POWER_VAR,
                b'\x1e': en.ACTIVE_ENERGY_VALUE_WATT_HOUR,
                b'\x1f': en.APPARENT_ENERGY_VALUE_VOLT_AMPERE_HOUR,
                b'\x20': en.REACTIVE_ENERGY_VALUE_VAR_HOUR,
                b'\x21': en.CURRENT_AMPERE,
                b'\x22': en.ELECTRICAL_CHARGE_COULOMB,
                b'\x23': en.VOLTAGE_VOLT,
                b'\x24': en.ELECTRIC_FIELD_STRENGTH_VOLT_PER_METRE,
                b'\x25': en.CAPACITANCE_FARAD,
                b'\x26': en.RESISTANCE_OHM,
                b'\x27': en.RESISTIVITY,
                b'\x28': en.MAGNETIC_FLUX_WEBER,
                b'\x29': en.MAGNETIC_FLUX_DENSITY_TESLA,
                b'\x2a': en.MAGNETIC_FIELD_STRENGTH_AMPERE_PER_METRE,
                b'\x2b': en.INDUCTANCE_HENRY,
                b'\x2c': en.FREQUENCY_HERTZ,
                b'\x2d': en.RW_ACTIVE_ENERGY_VALUE,
                b'\x2e': en.RB_REACTIVE_ENERGY_VALUE,
                b'\x2f': en.RS_APPARENT_ENERGY_VALUE,
                b'\x30': en.VOLT_SQUARED_HOUR_VOLT_SQUARED_HOUR_METER,
                b'\x31': en.AMPERE_SQUARED_HOUR,
                b'\x32': en.MASS_FLUX_KILOGRAM_PER_SECOND,
                b'\x33': en.CONDUCTANCE_SIEMENS,
                b'\x34': en.TEMPERATURE_KELVIN,
                b'\x35': en.RU2H_VOLT_SQUARED_HOUR_METER,
                b'\x36': en.RI2H_AMPERE_SQUARED_HOUR_METER,
                b'\x37': en.RV_METER,
                b'\x38': en.PERCENTAGE,
                b'\x39': en.AMPERE_HOURS,
                b'\x3a': en.RESERVED,
                b'\x3b': en.RESERVED,
                b'\x3c': en.ENERGY_PER_VOLUME,
                b'\x3d': en.CALORIFIC_VALUE_WOBBE,
                b'\x3e': en.MOLAR_FRACTION_OF_GAS_COMPOSITION_MOLE_PERCENT,
                b'\x3f': en.MASS_DENSITY_QUANTITY_OF_MATERIAL,
                b'\x40': en.DYNAMIC_VISCOSITY_PASCAL_SECOND,
                b'\x41': en.SPECIFIC_ENERGY_JOULE_KILOGRAM,
                b'\x42': en.PRESSURE_GRAM_PER_SQUARE_CENTIMETER,
                b'\x43': en.PRESSURE_ATMOSPHERE,
                b'\x46': en.SIGNAL_STRENGTH_MILLIWATT,
                b'\x47': en.SIGNAL_STRENGTH_MICROVOLT,
                b'\x48': en.LOGARITHMIC_UNIT,
                b'\x49': en.RESERVED,
                b'\x4a': en.RESERVED,
                b'\x4b': en.RESERVED,
                b'\x4c': en.RESERVED,
                b'\x4d': en.RESERVED,
                b'\x4e': en.RESERVED,
                b'\x4f': en.RESERVED,
                b'\x50': en.RESERVED,
                b'\x51': en.RESERVED,
                b'\x52': en.RESERVED,
                b'\x53': en.RESERVED,
                b'\x54': en.RESERVED,
                b'\x55': en.RESERVED,
                b'\x56': en.RESERVED,
                b'\x57': en.RESERVED,
                b'\x58': en.RESERVED,
                b'\x59': en.RESERVED,
                b'\x5a': en.RESERVED,
                b'\x5b': en.RESERVED,
                b'\x5c': en.RESERVED,
                b'\x5d': en.RESERVED,
                b'\x5e': en.RESERVED,
                b'\x5f': en.RESERVED,
                b'\x60': en.RESERVED,
                b'\x61': en.RESERVED,
                b'\x62': en.RESERVED,
                b'\x63': en.RESERVED,
                b'\x64': en.RESERVED,
                b'\x65': en.RESERVED,
                b'\x66': en.RESERVED,
                b'\x67': en.RESERVED,
                b'\x68': en.RESERVED,
                b'\x69': en.RESERVED,
                b'\x6a': en.RESERVED,
                b'\x6b': en.RESERVED,
                b'\x6c': en.RESERVED,
                b'\x6d': en.RESERVED,
                b'\x6e': en.RESERVED,
                b'\x6f': en.RESERVED,
                b'\x70': en.RESERVED,
                b'\x71': en.RESERVED,
                b'\x72': en.RESERVED,
                b'\x73': en.RESERVED,
                b'\x74': en.RESERVED,
                b'\x75': en.RESERVED,
                b'\x76': en.RESERVED,
                b'\x77': en.RESERVED,
                b'\x78': en.RESERVED,
                b'\x79': en.RESERVED,
                b'\x7a': en.RESERVED,
                b'\x7b': en.RESERVED,
                b'\x7c': en.RESERVED,
                b'\x7d': en.RESERVED,
                b'\x7e': en.RESERVED,
                b'\x7f': en.RESERVED,
                b'\x80': en.LENGTH_INCH,
                b'\x81': en.LENGTH_FOOT,
                b'\x82': en.MASS_POUND,
                b'\x83': en.TEMPERATURE_FAHRENHEIT,
                b'\x84': en.TEMPERATURE_RANKINE,
                b'\x85': en.AREA_SQUARE_INCH,
                b'\x86': en.AREA_SQUARE_FOOT,
                b'\x87': en.AREA_ACRE,
                b'\x88': en.VOLUME_CUBIC_INCH,
                b'\x89': en.VOLUME_CUBIC_FOOT,
                b'\x8a': en.VOLUME_ACRE_FOOT,
                b'\x8b': en.VOLUME_GALLON_IMPERIAL,
                b'\x8c': en.VOLUME_GALLON_US,
                b'\x8d': en.FORCE_POUND_FORCE,
                b'\x8e': en.PRESSURE_POUND_FORCE_PER_SQUARE_INCH,
                b'\x8f': en.DENSITY_POUND_PER_CUBIC_FOOT,
                b'\x90': en.DYNAMIC_VISCOSITY,
                b'\x91': en.KINEMATIC_VISCOSITY_SQUARE_FOOT_PER_SECOND,
                b'\x92': en.ENERGY_BRITISH_THERMAL_UNIT,
                b'\x93': en.ENERGY_THERM_EU,
                b'\x94': en.ENERGY_THERM_US,
                b'\x95': en.CALORIFIC_VALUE_OF_MASS_LENTHALPY,
                b'\x96': en.CALORIFIC_VALUE_WOBBE,
                b'\x97': en.VOLUME_METER_CUBIC_FEET_RV,
                b'\x98': en.SPEED_FOOT_PER_SECOND,
                b'\x99': en.VOLUME_FLUX_CUBIC_FOOT_PER_SECOND,
                b'\x9a': en.VOLUME_FLUX_CUBIC_FOOT_PER_MIN,
                b'\x9b': en.VOLUME_FLUX_CUBIC_FOOT_PER_HOUR,
                b'\x9c': en.VOLUME_FLUX_CUBIC_FOOT_PER_DAY,
                b'\x9d': en.VOLUME_FLUX_ACRE_FOOT_PER_SECOND,
                b'\x9e': en.VOLUME_FLUX_ACRE_FOOT_PER_MIN,
                b'\x9f': en.VOLUME_FLUX_ACRE_FOOT_PER_HOUR,
                b'\xa0': en.VOLUME_FLUX_ACRE_FOOT_PER_DAY,
                b'\xa1': en.VOLUME_IMPERIAL_GALLON_METER_RV,
                b'\xa2': en.VOLUME_FLUX_IMPERIAL_GALLON_PER_SECOND,
                b'\xa3': en.VOLUME_FLUX_IMPERIAL_GALLON_PER_MIN,
                b'\xa4': en.VOLUME_FLUX_IMPERIAL_GALLON_PER_HOUR,
                b'\xa5': en.VOLUME_FLUX_IMPERIAL_GALLON_PER_DAY,
                b'\xa6': en.VOLUME_US_GALLON_RV,
                b'\xa7': en.VOLUME_FLUX_US_GALLON_PER_SECOND,
                b'\xa8': en.VOLUME_FLUX_US_GALLON_PER_MIN,
                b'\xa9': en.VOLUME_FLUX_US_GALLON_PER_HOUR,
                b'\xaa': en.VOLUME_FLUX_US_GALLON_PER_DAY,
                b'\xab': en.ENERGY_FLOW_BRITISH_THERMAL_UNIT_PER_SECOND,
                b'\xac': en.ENERGY_FLOW_BRITISH_THERMAL_UNIT_PER_MINUTE,
                b'\xad': en.ENERGY_FLOW_BRITISH_THERMAL_UNIT_PER_HOUR,
                b'\xae': en.ENERGY_FLOW_BRITISH_THERMAL_UNIT_PER_DAY,
                b'\xaf': en.RESERVED,
                b'\xb0': en.RESERVED,
                b'\xb1': en.RESERVED,
                b'\xb2': en.RESERVED,
                b'\xb3': en.RESERVED,
                b'\xb4': en.RESERVED,
                b'\xb5': en.RESERVED,
                b'\xb6': en.RESERVED,
                b'\xb7': en.RESERVED,
                b'\xb8': en.RESERVED,
                b'\xb9': en.RESERVED,
                b'\xba': en.RESERVED,
                b'\xbb': en.RESERVED,
                b'\xbc': en.RESERVED,
                b'\xbd': en.RESERVED,
                b'\xbe': en.RESERVED,
                b'\xbf': en.RESERVED,
                b'\xc0': en.RESERVED,
                b'\xc1': en.RESERVED,
                b'\xc2': en.RESERVED,
                b'\xc3': en.RESERVED,
                b'\xc4': en.RESERVED,
                b'\xc5': en.RESERVED,
                b'\xc6': en.RESERVED,
                b'\xc7': en.RESERVED,
                b'\xc8': en.RESERVED,
                b'\xc9': en.RESERVED,
                b'\xca': en.RESERVED,
                b'\xcb': en.RESERVED,
                b'\xcc': en.RESERVED,
                b'\xcd': en.RESERVED,
                b'\xce': en.RESERVED,
                b'\xcf': en.RESERVED,
                b'\xd0': en.RESERVED,
                b'\xd1': en.RESERVED,
                b'\xd2': en.RESERVED,
                b'\xd3': en.RESERVED,
                b'\xd4': en.RESERVED,
                b'\xd5': en.RESERVED,
                b'\xd6': en.RESERVED,
                b'\xd7': en.RESERVED,
                b'\xd8': en.RESERVED,
                b'\xd9': en.RESERVED,
                b'\xda': en.RESERVED,
                b'\xdb': en.RESERVED,
                b'\xdc': en.RESERVED,
                b'\xdd': en.RESERVED,
                b'\xde': en.RESERVED,
                b'\xdf': en.RESERVED,
                b'\xe0': en.RESERVED,
                b'\xe1': en.RESERVED,
                b'\xe2': en.RESERVED,
                b'\xe3': en.RESERVED,
                b'\xe4': en.RESERVED,
                b'\xe5': en.RESERVED,
                b'\xe6': en.RESERVED,
                b'\xe7': en.RESERVED,
                b'\xe8': en.RESERVED,
                b'\xe9': en.RESERVED,
                b'\xea': en.RESERVED,
                b'\xeb': en.RESERVED,
                b'\xec': en.RESERVED,
                b'\xed': en.RESERVED,
                b'\xee': en.RESERVED,
                b'\xef': en.RESERVED,
                b'\xf0': en.RESERVED,
                b'\xf1': en.RESERVED,
                b'\xf2': en.RESERVED,
                b'\xf3': en.RESERVED,
                b'\xf4': en.RESERVED,
                b'\xf5': en.RESERVED,
                b'\xf6': en.RESERVED,
                b'\xf7': en.RESERVED,
                b'\xf8': en.RESERVED,
                b'\xf9': en.RESERVED,
                b'\xfa': en.RESERVED,
                b'\xfb': en.RESERVED,
                b'\xfc': en.RESERVED,
                b'\xfd': en.EXTENDED_TABLE_OF_UNITS,
                b'\xfe': en.OTHER_UNIT,
                b'\xff': en.NO_UNIT_UNITLESS_COUNT}


class ScalUnitType(Structure):
    """ Provides information on the unit and the scaler of the value.
        scaler: This is the exponent (to the base of 10) of the multiplication factor. REMARK If the value is not numerical, then the scaler shall be set to 0.
        unit: Enumeration defining the physical unit; for details see Table 4 below"""
    values: tuple[Integer, Unit]
    __match_args__ = ('scaler', 'unit')
    ELEMENTS: tuple[StructElement, StructElement] = (StructElement(se.SCALER, Integer),
                                                     StructElement(se.UNIT, Unit))
    default = b'\x02\x02\x0f\x00\x16\xff'

    @property
    def scaler(self) -> Integer:
        return self.values[0]

    @property
    def unit(self) -> Unit:
        return self.values[1]


if __name__ == '__main__':
    a = ScalUnitType()
    b = a.scaler
    a = Integer()
    b = Integer(2)
    a.set(b)
    b = OctetString('12 43 00')
    a = b[0]
    b = SimpleDataType.__subclasses__()
    a = issubclass(Unsigned, SimpleDataType)
    # a = DateTime(datetime.datetime.now(tz=datetime.timezone(datetime.timedelta(hours=3))))
    a = DateTime(b'\x19\x07\xe4\x01\x01\xff\x00\x00\x00\x00\x80\x00\xff')
    c = str(a)
    b = a.hour
    a = BitString(b'\x04\x18\x00\x1E\x1D')
    one_bit = a[21]
    one_bit2 = a.decode()[21]
    a1 = Unsigned(2)
    # print(a > a1)
    b = a.decode()
    a, b = get_instance_and_pdu(OctetString, b'\x09\x02\x01\x01\x01\x07\x01\x01\x07\x01\x01\x07\x01\x01\x07\x01')
    logical_name = OctetString(a)
    a = OctetString(logical_name)
    print(__types)
    print(get_common_data_type_from(b'\x06'))
    a = NullData()
    if a:
        print(a)
    a = Array(b'\x01\x00', Boolean)
    print(a.TAG)
    a = Unsigned('121')
    print(a, len(a))
    a.contents = Integer(2)
    print(a)
    a = Unsigned('12')
    print(a.encoding)
    from widgets.entry import Entry
    import tkinter as tk

    class Test:
        def __init__(self, value):
            self.value = value

        def get(self, id_):
            return self.value

        def set(self, id_, value):
            self.value = value
            print(value)

    a = Float32(1.32)
    # a = Unsigned(34)
    b = isinstance(a, SimpleDataType)
    # a = DateTime('01.01')
    # a = Date('01.01')
    # a = Time('1:')
    # a = OctetString('0102')
    print(str(a))

    root = tk.Tk()
    test = Test(a)
    widget1 = Entry(font=None, master=root, id_=1, cb_set_to_source=test.set, cb_get_from_source=test.get)
    widget1.widget.grid()
    root.mainloop()

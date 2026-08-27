from typing import Self
import re
from ..types import common_data_types as cdt
import datetime


class LogicalName(cdt.ReportMixin, cdt.OctetString, size=6):
    """ Logical Name type. Default is CLock#1 """
    __pattern = re.compile("(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})\.(\d{1,3})")
    __match_args__ = ('a', 'b', 'c', 'd', 'e', 'f')
    DEFAULT = b'\x00\x00\x01\x00\x00\xff'

    @classmethod
    def parse(cls, value: str) -> Self:
        if value.count(".") == 5:
            return cls.from_obis(value)
        return super().parse(value)

    @classmethod
    def from_obis(cls, value: str) -> Self:
        """ create logical_name: octet_string from string type ddd.ddd.ddd.ddd.ddd.ddd, ex.: 0.0.1.0.0.255 """
        if (res := cls.__pattern.search(value)) is None:
            raise ValueError(F"got wrong obis: {value}")
        else:
            return cls(bytearray(map(int, res.groups())))

    def get_report(self) -> cdt.Report:
        return cdt.Report('.'.join(map(str, self.contents)))  # todo: add error handle

    def validate_from(self, value: str, cursor_position=None) -> tuple[str, int]:
        try:
            possible = type(self)(value)
            return value, cursor_position  # TODO: wrong position ???
        except ValueError:
            with_separator = F'{value[:-1]}.{value[-1]}'
            type(self)(with_separator)  # check possible
            return with_separator, cursor_position

    def __hash__(self) -> int:
        return int.from_bytes(self.contents, 'big')

    @property
    def a(self) -> int:
        """ group A """
        return self.contents[0]

    @property
    def b(self) -> int:
        """ group B """
        return self.contents[1]

    @property
    def c(self) -> int:
        """ group C """
        return self.contents[2]

    @property
    def d(self) -> int:
        """ group D """
        return self.contents[3]

    @property
    def e(self) -> int:
        """ group E """
        return self.contents[4]

    @property
    def f(self) -> int:
        """ group F """
        return self.contents[5]

    def __lt__(self, other: Self) -> bool:
        return self.contents < other.contents


class OctetStringDateTime(cdt.DateTime, tag=9, size=12):
    """ type Time in OctetString(SIZE(12)) """

    def __init__(self, value: bytes | bytearray | str | int | datetime.datetime | datetime.date | datetime.time = b'\x09\x0c\x07\xe4\x01\x01\xff\xff\xff\xff\xff\x80\x00\xff'):
        match value:  # TODO: common for all OctetDateTimes
            case bytes() if value[1] == len(self): super().__init__(self.TAG+value[2:])
            case bytes():                          raise ValueError(F'in create {self.__class__.__name__} got tag, size: {cdt.TAG(value[0])} {value[1]}, expected {self.TAG} {len(self)}')
            case _:                                super().__init__(value)

    @property
    def encoding(self) -> bytes:
        return b'\x09\x0c' + self.contents


class OctetStringDate(cdt.Date, tag=9, size=5):
    """ type Time in OctetString(SIZE(5)) """

    def __init__(self, value: bytes | bytearray | str | int | datetime.datetime | datetime.date = b'\x09\x05\x07\xe4\x01\x01\xff'):
        match value:  # TODO: replace priority case
            case bytes() if value[1] == len(self): super().__init__(self.TAG+value[2:])
            case bytes():                          raise ValueError(F'in create {self.__class__.__name__} got tag, size: {cdt.TAG(value[0])} {value[1]}, expected {self.TAG} {len(self)}')
            case _:                                super().__init__(value)

    @property
    def encoding(self) -> bytes:
        return b'\x09\x05' + self.contents


class OctetStringTime(cdt.Time, tag=9, size=4):
    """ type Time in OctetString(SIZE(4)) """

    def __init__(self, value: bytes | bytearray | str | int | datetime.datetime | datetime.time = b'\x09\x04\x00\x00\x00\x00'):
        match value:  # TODO: replace priority case
            case bytes() if value[1] == len(self): super().__init__(self.TAG+value[2:])
            case bytes():                          raise ValueError(F'in create {self.__class__.__name__} got tag, size: {cdt.TAG(value[0])} {value[1]}, expected {self.TAG} {len(self)}')
            case _:                                super().__init__(value)

    @property
    def encoding(self) -> bytes:
        return b'\x09\x04' + self.contents

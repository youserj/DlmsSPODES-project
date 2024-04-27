from typing import Self
from .useful_types import OctetString


class New(OctetString):
    """Cosem-Object-Instance-Id"""
    LENGTH = 6

    def __init__(self, value: bytes):
        if len(value) == self.LENGTH:
            super(New, self).__init__(value)
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


ASSOCIATION_LN0 = New.from_str("0.0.40.0.0.255")
LDN = New.from_str("0.0.42.0.0.255")

from typing import Self
from struct import pack
from COSEMpdu.data import DoubleLongUnsigned


class DoubleLongUnsignedSecond(DoubleLongUnsigned):
    """for second implementation"""


class IPAddress(DoubleLongUnsigned):
    """with string parser"""

    @classmethod
    def from_str(cls, value: str) -> Self:
        """ create ip: integer from string type ddd.ddd.ddd.ddd, ex.: 127.0.0.1 """
        raw_value = bytearray()
        for separator in "... ":
            try:
                element, value = value.split(separator, 1)
            except ValueError:
                element, value = value, ""
            raw_value.append(cls.__get_attr_element(element))
        return cls.parse(int.from_bytes(raw_value, "big"))

    @staticmethod
    def __get_attr_element(value: str) -> int:
        if value == "":
            return 0
        try:
            return int(value)
        except OverflowError:
            raise ValueError(f"Int too big to convert {value}")

    def __str__(self) -> str:
        return ".".join(map(str, pack(">L", self.normalize())))

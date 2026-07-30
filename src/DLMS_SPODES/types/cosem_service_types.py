from typing import Self
import re
from COSEMpdu.data import OctetString
from ..types.common_data_types import Report, Log
from logging import ERROR


class LogicalName(OctetString):
    __pattern = re.compile("(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})")
    __match_args__ = ("a", "b", "c", "d", "e", "f")

    @classmethod
    def from_obis(cls, value: str) -> Self:
        """ create logical_name: octet_string from string type ddd.ddd.ddd.ddd.ddd.ddd, ex.: 0.0.1.0.0.255 """
        if (res := cls.__pattern.search(value)) is None:
            raise ValueError(F"got wrong obis: {value}")
        return cls((bytes(map(int, res.groups()))))

    def get_report(self) -> Report:
        if len(self.value) != 6:
            return Report(
                str(self),
                log=Log(ERROR, f"got length: {len(self.value)}, expected 6")
            )
        return Report(".".join(map(str, self.value)))  # todo: add error handle

    def __hash__(self) -> int:
        return int.from_bytes(self.value, "big")

    @property
    def a(self) -> int:
        """ group A """
        return self.value[0] if len(self.value) >= 1 else -1

    @property
    def b(self) -> int:
        """ group B """
        return self.value[1] if len(self.value) >= 2 else -1

    @property
    def c(self) -> int:
        """ group C """
        return self.value[2] if len(self.value) >= 3 else -1

    @property
    def d(self) -> int:
        """ group D """
        return self.value[3] if len(self.value) >= 4 else -1

    @property
    def e(self) -> int:
        """ group E """
        return self.value[4] if len(self.value) >= 5 else -1

    @property
    def f(self) -> int:
        """ group F """
        return self.value[5] if len(self.value) >= 6 else -1

    def __lt__(self, other: Self) -> bool:
        return self.value < other.value


class OctetStringDateTime(OctetString):
    ...


class OctetStringDate(OctetString):
    ...


class OctetStringTime(OctetString):
    ...

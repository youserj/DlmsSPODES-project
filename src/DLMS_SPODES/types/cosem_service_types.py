from typing import Self
import datetime
import re
from COSEMpdu.x680.constrained_type import SizeConstraint
from COSEMpdu.types_used import CosemObjectInstanceId
from COSEMpdu.axdr import OctetStringType, ConstrainedOctetStringType, TaggedType
from COSEMpdu import axdr
from COSEMpdu.x680.tagged_type import TaggingMode
from COSEMpdu.x680.type import NamedType, OCTET_STRING
from COSEMpdu import data
from ..types import common_data_types as cdt
import datetime


class LogicalName(TaggedType[CosemObjectInstanceId]):
    """[9] IMPLICIT OCTET STRING (SIZE(6))"""
    tag = 9
    mode = TaggingMode.IMPLICIT
    __pattern = re.compile("(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})")
    __match_args__ = ("a", "b", "c", "d", "e", "f")

    @classmethod
    def from_obis(cls, value: str) -> Self:
        """ create logical_name: octet_string from string type ddd.ddd.ddd.ddd.ddd.ddd, ex.: 0.0.1.0.0.255 """
        if (res := cls.__pattern.search(value)) is None:
            raise ValueError(F"got wrong obis: {value}")
        return cls(CosemObjectInstanceId(OctetStringType(bytes(map(int, res.groups())))))

    def get_report(self) -> cdt.Report:
        return cdt.Report(".".join(map(str, self.value.value.value)))  # todo: add error handle

    def __hash__(self) -> int:
        return int.from_bytes(self.value.value.value, "big")

    @property
    def a(self) -> int:
        """ group A """
        return self.value.value.value[0]

    @property
    def b(self) -> int:
        """ group B """
        return self.value.value.value[1]

    @property
    def c(self) -> int:
        """ group C """
        return self.value.value.value[2]

    @property
    def d(self) -> int:
        """ group D """
        return self.value.value.value[3]

    @property
    def e(self) -> int:
        """ group E """
        return self.value.value.value[4]

    @property
    def f(self) -> int:
        """ group F """
        return self.value.value.value[5]

    def __lt__(self, other: Self) -> bool:
        return self.value.value.value < other.value.value.value


class OctetStringDateTime(data.OctetString):
    ...


class OctetStringDate(data.OctetString):
    ...


class OctetStringTime(data.OctetString, data.TimeMixin[axdr.OctetStringType]):
    def normalize(self) -> OCTET_STRING:
        return super().normalize()[:4].ljust(4, b"\xff")


z = OctetStringTime.parse(b"\x01")
x = z.normalize()
z1 = OctetStringTime.fromisoformat("10:00:01,01")
print(z.isoformat())

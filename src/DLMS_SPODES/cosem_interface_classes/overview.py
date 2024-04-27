"""DLMS UA 1000-1 Ed 14 4.2 Overview of the COSEM interface classes"""
from functools import lru_cache
from enum import IntEnum
from dataclasses import dataclass
from ..types import ut, cdt


@dataclass(frozen=True)
class Version:
    V0 = cdt.Unsigned(0)
    V1 = cdt.Unsigned(1)
    V2 = cdt.Unsigned(2)
    V3 = cdt.Unsigned(3)


class CountrySpecificIdentifiers(IntEnum):
    FINLAND = 0
    USA = 1
    CANADA = 2
    SERBIA = 3
    RUSSIA = 7
    CZECH_REPUBLIC = 10
    BULGARIA = 11
    CROATIA = 12
    IRELAND = 13
    ISRAEL = 14
    UKRAINE = 15
    YUGOSLAVIA = 16
    EGYPT = 20
    SOUTH_AFRICA = 27
    GREECE = 30
    NETHERLANDS = 31
    BELGIUM = 32
    FRANCE = 33
    SPAIN = 34
    PORTUGAL = 35
    HUNGARY = 36
    LITHUANIA = 37
    SLOVENIA = 38
    ITALY = 39
    ROMANIA = 40
    SWITZERLAND = 41
    SLOVAKIA = 42
    AUSTRIA = 43
    UNITED_KINGDOM = 44
    DENMARK = 45
    SWEDEN = 46
    NORWAY = 47
    POLAND = 48
    GERMANY = 49
    PERU = 51
    SOUGH_KOREA = 52
    CUBA = 53
    ARGENTINA = 54
    BRAZIL = 55
    CHILE = 56
    COLOMBIA = 57
    VENEZUELA = 58
    MALAYSIA = 60
    AUSTRALIA = 61
    INDONESIA = 62
    PHILIPPINES = 63
    NEW_ZEALAND = 64
    SINGAPORE = 65
    THAILAND = 66
    LATVIA = 71
    MOLDOVA = 73
    BELARUS = 75
    JAPAN = 81
    MEXICO = 82
    HONG_KONG = 85
    CHINA = 86
    BOSNIA_AND_HERZEGOVINA = 87
    TURKEY = 90
    INDIA = 91
    PAKISTAN = 92
    SAUDI_ARABIA = 96
    UNITED_ARAB_EMIRATES = 97
    IRAN = 98

    def __str__(self):
        return self.name

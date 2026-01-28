import re
from struct import Struct
from StructResult import result


type Obis = bytes  # bytes[6]
type Index = int    # 0..
type GruoupI = int  # group index of Obis 0..
type Attr = bytes  # bytes[7]
type Meth = bytes  # bytes[7]
type Encoding = bytes  # bytes[1..]
type LN = str  # logical name as "a.b.c.d.e.f"
type Tag = bytes  # bytes[1] CDT tag
type AttrDesc = bytes  # bytes[]

def attr2obis(attr: Attr) -> Obis:
    return attr[:6]


def attr2a(attr: Attr | Obis) -> GruoupI:
    return attr[0]


def attr2b(attr: Attr | Obis) -> GruoupI:
    return attr[1]


def attr2c(attr: Attr | Obis) -> GruoupI:
    return attr[2]


def attr2d(attr: Attr | Obis) -> GruoupI:
    return attr[3]


def attr2e(attr: Attr | Obis) -> GruoupI:
    return attr[4]


def attr2f(attr: Attr | Obis) -> GruoupI:
    return attr[5]


def attr2i(attr: Attr) -> Index:
    return attr[6]


obis2attr_pat = Struct(">6sB")


def unpack_attr(attr: Attr) -> tuple[Obis, Index]:
    return obis2attr_pat.unpack(attr)

def pack_attr(obis: Obis, i: Index) -> Attr:
    return obis2attr_pat.pack(obis, i)


ln_pattern = re.compile("(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})\\.(\\d{1,3})")


def ln2obis(ln: str) -> result.SimpleOrError[Obis]:
    """ create Obis from string type ddd.ddd.ddd.ddd.ddd.ddd, ex.: 0.0.1.0.0.255 """
    if (res := ln_pattern.search(ln)) is None:
        return result.Error.from_e(ValueError(F"got wrong {ln=}"), "ln2obis")
    return result.Simple(bytes(map(int, res.groups())))


def obis2ln(obis: Obis) -> str:
    return ".".join(map(str, obis))


__all__ = [
    "Obis",
    "Attr",
    "AttrDesc",
    "Encoding",
    "Index",
    "Tag"
]

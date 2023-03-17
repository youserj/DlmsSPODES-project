"""DLMS UA 1000-1 Ed. 14. 7.4 Abstract objects (Value group A = 0)"""
from struct import pack_into
from ..types import cst


_buf = bytearray(6)


def BILLING_PERIOD_COUNTER(b: int = 0, f: int = 255):
    return cst.LogicalName(bytes((0, b, 0, 1, 0, f)))


def SPODES3_DISPLAY_MODE():
    return cst.LogicalName(pack_into(">6B", _buf, 0, 0, 96, 4, 1, 255))


LDN = cst.LogicalName(pack_into(">6B", _buf, 0, 0, 42, 0, 0, 255))

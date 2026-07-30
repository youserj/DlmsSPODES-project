from dataclasses import dataclass
from COSEMpdu.data import Structure, LongUnsigned, Unsigned, Array
from ..types import cst
from ..types.type_alias import Attr
from .cosem_interface_class import ICAuto, ICAElement, ICMElement


@dataclass
class SpecDayEntry(Structure):
    """spec_day_entry"""
    index: LongUnsigned
    specialday_date: cst.OctetStringDate
    day_id: Unsigned


Entries = Array[SpecDayEntry]
"""attribute entries"""


class SpecialDaysTable(ICAuto):
    """4.5.4 Special days table"""
    CLASS_ID = 11
    VERSION = 0
    A_ELEMENTS = ICAElement(2, "entries", Entries),
    M_ELEMENTS = (
        ICMElement(1, "insert", SpecDayEntry),
        ICMElement(2, "delete", LongUnsigned))
    entries: Attr

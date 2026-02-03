from typing import Callable, Self
from .cosem_interface_class import ICAuto, ICAElement, ICMElement
from .Overview import class_id
from ..types import cdt, cst
from ..types.type_alias import Attr


class Index(cdt.MinDigital, cdt.MaxDigital, cdt.LongUnsigned):
    """ LongUnsigned type with validation """
    MIN = 1
    MAX = 9999
    __cb_get_indexes: Callable
    DEFAULT = 1

    def set_callback(self, cb: Callable):
        self.__cb_get_indexes = cb

    def get_indexes(self) -> list[int]:
        """ return indexes container """
        return self.__cb_get_indexes()

    def check(self, string: str):
        """ raise ValueError with message if string not is valid """
        instance = type(self)(value=string)
        if int(instance) in self.__cb_get_indexes():
            raise ValueError('New index not unique')

    @classmethod
    def with_cb(cls, value, cb: Callable) -> Self:
        """ get instance with callback """
        ret = cls(value)
        ret.set_callback(cb)
        return ret


class ScheduleTableEntry(cdt.Structure):
    """schedule_table_entry"""
    index: Index
    enable: cdt.Boolean
    script_logical_name: cst.LogicalName
    script_selector: cdt.LongUnsigned
    switch_time: cst.OctetStringTime
    validity_window: cdt.LongUnsigned
    exec_weekdays: cdt.BitString
    exec_specdays: cdt.BitString
    begin_date: cst.OctetStringDate
    end_date: cst.OctetStringDate


# TODO: rewrite to new API
class Entries(cdt.Array):
    """entries attribute"""
    TYPE = ScheduleTableEntry
    unique = True

    def __init__(self, value: bytes = None):
        super(Entries, self).__init__(value)
        # setting callback for validate schedule_table_entry index
        for schedule_table_entry in self:
            schedule_table_entry: ScheduleTableEntry
            schedule_table_entry.index.set_callback(self.get_indexes)

    def get_indexes(self) -> list[int]:
        """ getter for callback Index """
        return [entries_element.index.decode() for entries_element in self]


class DataED(cdt.Structure):
    """ enable/disable"""
    firstIndexA: Index
    lastIndexA: Index
    firstIndexB: Index
    lastIndexB: Index


class DataDelete(cdt.Structure):
    """delete"""
    firstIndex: Index
    lastIndex: Index


class Schedule(ICAuto):
    """4.5.3 Schedule"""
    CLASS_ID = class_id.SCHEDULE
    VERSION = 0
    A_ELEMENTS = ICAElement(2, "entries", Entries),
    M_ELEMENTS = (ICMElement(1, "enable_disable", DataED),
                  ICMElement(2, "insert", ScheduleTableEntry),
                  ICMElement(3, "delete", DataDelete))
    entries: Attr

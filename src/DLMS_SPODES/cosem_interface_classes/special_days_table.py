import datetime
from .__class_init__ import *
from .overview import VERSION_0


class SpecDayEntry(cdt.Structure):
    """ Specifies a special day identifier for a given date. The date may have wildcards for repeating special days like Christmas. """
    index: cdt.LongUnsigned
    specialday_date: cst.OctetStringDate
    day_id: cdt.Unsigned


class Entries(cdt.Array):
    """ Specifies the list of spec_day_entry """
    TYPE = SpecDayEntry
    values: list[SpecDayEntry]
    __getitem__: SpecDayEntry

    def new_element(self) -> SpecDayEntry:
        indexes: list[int] = [int(el.index) for el in self.values]
        for i in range(0x1_00_00):
            if i not in indexes:
                return SpecDayEntry((i, None, None))  # TODO: insert first DayID from ActiveCalendar as 3 element
        raise ValueError(F'in {self} all indexes is busy')

    def __check_index(self, value):
        """validate day_id from DayProfile"""
        if cdt.LongUnsigned(value) in (entry.index for entry in self.values):
            raise ValueError(F'{cdt.LongUnsigned(value)} already exist in {self}')
        else:
            """validate OK"""

    def validate_exist_index(self, value):
        """pass if value in indexes"""
        if cdt.LongUnsigned(value) not in (entry.index for entry in self.values):
            raise ValueError(F'{cdt.LongUnsigned(value)} not exist in {self}')
        else:
            """validate OK"""

    def get_indexes(self) -> list[int]:
        """ getter for callback Index """
        return [int(entries_element.index) for entries_element in self.values]


class SpecialDaysTable(ic.COSEMInterfaceClasses):
    """ The interface class allows defining dates, which will override normal switching behaviour for special days. The interface class works in
    conjunction with the class "Schedule" or "Activity calendar" and the linking data item is day_id """
    CLASS_ID = ClassID.SPECIAL_DAYS_TABLE
    VERSION = VERSION_0
    A_ELEMENTS = ic.ICAElement("entries", Entries),
    M_ELEMENTS = (ic.ICMElement("insert", SpecDayEntry),
                  ic.ICMElement("delete", cdt.LongUnsigned))  # Todo: was Delete.with_cb(None, self.entries.get_indexes)

    @property
    def entries(self) -> Entries:
        return self.get_attr(2)

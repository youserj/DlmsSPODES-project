import datetime
from .__class_init__ import *


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
        indexes: list[int] = [el.index.decode() for el in self.values]
        for i in range(0x1_00_00):
            if i not in indexes:
                return SpecDayEntry((i, None, None))  # TODO: insert first DayID from ActiveCalendar as 3 element
        raise ValueError(F'in {self} all indexes is busy')

    def append_validate(self, element: SpecDayEntry):
        """validate and insert callback for validate change SpecDayEntry"""
        self.__check_index(element.index)
        element.index.register_cb_preset(self.__check_index)

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
        return [entries_element.index.decode() for entries_element in self.values]


class SpecialDaysTable(ic.COSEMInterfaceClasses):
    """ The interface class allows defining dates, which will override normal switching behaviour for special days. The interface class works in
    conjunction with the class "Schedule" or "Activity calendar" and the linking data item is day_id """
    CLASS_ID = ClassID.SPECIAL_DAYS_TABLE
    VERSION = Version.V0
    A_ELEMENTS = ic.ICAElement("entries", Entries),
    M_ELEMENTS = (ic.ICMElement("insert", SpecDayEntry),
                  ic.ICMElement("delete", cdt.LongUnsigned))  # Todo: was Delete.with_cb(None, self.entries.get_indexes)

    def characteristics_init(self):
        self.cardinality = (0, 1)

        self._cbs_attr_post_init.update({2: self.__set_delete})
        self.set_attr(2, None)

    @property
    def entries(self) -> Entries:
        return self.get_attr(2)

    @property
    def insert(self) -> SpecDayEntry:
        return self.get_meth(1)

    @property
    def delete(self) -> cdt.LongUnsigned:
        return self.get_meth(2)

    def __set_delete(self):
        try:
            self.delete.register_cb_preset(self.entries.validate_exist_index)
            self.insert.index.register_cb_preset(self.entries.validate_exist_index)
        except KeyError:  # At init time
            print('set delete NO:')

    def __delete_entry(self):
        """remove one entry by according delete method index. Call after execute"""
        for entry in self.entries.values:
            if entry.index == self.delete:
                self.entries.values.remove(entry)
                return
        else:
            raise ValueError(F'not found entry with index {self.delete} for remove')

    def get_day_id_of_current_special_day(self, server_time: datetime.datetime = None) -> cdt.Unsigned | None:
        """ return day ID if special day if it in today else None """
        server_time = self.collection.current_time if server_time is None else server_time
        if self.entries is None:
            raise AttributeError('Special days table: attribute Entries is empty. Need receive it from server')
        else:
            current_date: datetime.date = server_time.date()
            for spec_day_entry in self.entries:
                if spec_day_entry.specialday_date.decode() == current_date:
                    return spec_day_entry.day_id
            else:
                return None

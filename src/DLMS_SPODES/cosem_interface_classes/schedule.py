from typing import Callable, Self
from itertools import count
from .__class_init__ import *


class Index(cdt.LongUnsigned, min=1, max=9999):
    """ LongUnsigned type with validation """
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
        if instance.decode() in self.__cb_get_indexes():
            raise ValueError('New index not unique')

    @classmethod
    def with_cb(cls, value, cb: Callable) -> Self:
        """ get instance with callback """
        ret = cls(value)
        ret.set_callback(cb)
        return ret


class ScheduleTableEntry(cdt.Structure):
    """ Specifies the scripts to be executed at given times. There is only one script that can be executed per entry. """
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
    """ Specifies the list of schedule_table_entry """
    TYPE = ScheduleTableEntry
    unique = True

    def __init__(self, value: bytes = None):
        super(Entries, self).__init__(value)
        # setting callback for validate schedule_table_entry index
        for schedule_table_entry in self:
            schedule_table_entry: ScheduleTableEntry
            schedule_table_entry.index.set_callback(self.get_indexes)

    def append(self, element: ScheduleTableEntry | None = None):
        """ append element to end with unique index """
        if element is None:
            element: ScheduleTableEntry = self.get_type()()
            indexes = self.get_indexes()
            count_ = count(1)
            while True:
                new_index = next(count_)
                if new_index not in indexes:
                    break
            element.index = Index.with_cb(new_index, self.get_indexes)
        if isinstance(element, self.get_type()):
            if self.unique:
                for i in self:
                    if i == element:
                        raise ValueError(F"Element {element.__class__.__name__} already exist in {self.__class__.__name__}")
            self.append(element)
        else:
            raise ValueError(F'Types not equal. Must be {self.TYPE.NAME} got {type(element).__name__}')

    def get_indexes(self) -> list[int]:
        """ getter for callback Index """
        return [entries_element.index.decode() for entries_element in self]


class DataED(cdt.Structure):
    """ Sets the disabled bit of range A entries to true and then enables the entries of range B.
    * firstIndexA/B < lastIndexA/B: all entries of the range A/B are disabled/enabled
    * firstIndexA/B == lastIndexA/B: one entry is disabled/enabled,
    * firstIndexA/B > lastIndexA/B: nothing disabled/enabled,
    * firstIndexA/B and lastIndexA/B > 9999: no entry is disabled/enabled """
    firstIndexA: Index
    lastIndexA: Index
    firstIndexB: Index
    lastIndexB: Index


class DataDelete(cdt.Structure):
    """ Deletes a range of entries in the table.
    * firstIndex < lastIndex: all entries of the range A/B are deleted,
    * firstIndex ::= lastIndex: one entry is deleted,
    * firstIndex > lastIndex: nothing deleted  """
    firstIndex: Index
    lastIndex: Index


class Schedule(ic.COSEMInterfaceClasses):
    """ The IC “Schedule” together with an object of the IC “Special days”  table handles time and date driven activities within a device.
    The following picture gives an overview and shows the interactions between them:
    Schedule:

    Index | enable | action | Switch_time | validity_window |     exec_weekdays    |  exec_specdays  | date range
          |        |(script)|             |                 | Mo Tu We Th Fr Sa Su | S1 S2 ... S8 S9 | begin_date | end_date
    120     Yes     xxxx:yy     06:00           0xFFFF        x  x  x  x  x  x                         xx-04-01     xx-09-30
    121     Yes     xxxx:yy     22:00            15           x  x  x  x  x                            xx-04-01     xx-09-30
    122     Yes     xxxx:yy     12:00             0                          x                         xx-04-01     xx-09-30
    200     No      xxxx:yy     06:30                         x  x  x  x  x  x                         xx-04-01     xx-09-30
    201     No      xxxx:yy     21:30                         x  x  x  x  x                            xx-04-01     xx-09-30
    202     No      xxxx:yy     11:00                                        x                         xx-04-01     xx-09-30

    Special days table:

    Index | special_day_date | day_id
     12         xx-12-24        S1
     33         xx-12-25        S3
     77         97-03-31        S3

     Recovery after power failure
     After a power failure, the whole schedule is processed to execute all the necessary scripts that would get lost during a power failure. For this,
     the entries that were not executed during the power failure must be detected. Depending on the validity window attribute they are executed in
     the correct order (as they would have been executed in normal operation).

     Handling of time changes
     There are four different "actions" of time changes:
        a) time setting forward; b) time setting backwards; c) time synchronization; d) daylight saving action.
     All these four actions need a different handling executed by the schedule in interaction with the time setting activity.

     Time setting forward*
     This is handled the same way as a power failure. All entries missed are executed depending on the validity window attribute.
     A (manufacturer specific defined) short time setting can be handled like time synchronization.
     * Writing to the attribute “time” of the “Clock” object.

     Time setting backward*
     This results in a repetition of those entries that are activated during the repeated time. A (manufacturer specific defined) short time setting
     can be handled like time synchronization.
     * Writing to the attribute “time” of the “Clock” object.

     Time synchronization*
     Time synchronization is used to correct small deviations between a master clock and the local clock. The algorithm is manufacturer specific.
     It shall guarantee that no entry of the schedule gets lost, or is executed twice. The validity window attribute has no effect, because all
     entries must be executed in normal operation.
     * Using the method “adjust_to_quarter” of the “Clock” object.

     Daylight saving
     If the clock is put forward, then all scripts, which fall into the forwarding interval (and would therefore get lost) are executed.
     If the clock is put back, re-execution of the scripts, which fall into the backwarding interval is suppressed. """
    CLASS_ID = ClassID.SCHEDULE
    VERSION = Version.V0
    A_ELEMENTS = ic.ICAElement("entries", Entries),
    M_ELEMENTS = (ic.ICMElement("enable_disable", DataED),
                  ic.ICMElement("insert", ScheduleTableEntry),
                  ic.ICMElement("delete", DataDelete))

    def characteristics_init(self):
        self.set_attr(2, None)
        self._cbs_attr_post_init.update({2: self.__set_index_cbs})

    @property
    def entries(self) -> Entries:
        return self.get_attr(2)

    @property
    def enable_disable(self) -> DataED:
        return self.get_meth(1)

    @property
    def insert(self) -> ScheduleTableEntry:
        return self.get_meth(2)

    @property
    def delete(self) -> DataDelete:
        return self.get_meth(3)

    def __set_index_cbs(self):
        """ set callbacks to methods """
        try:
            indexes: Callable = self.entries.get_indexes
            self.enable_disable.firstIndexA.set_callback(indexes)
            self.enable_disable.firstIndexB.set_callback(indexes)
            self.enable_disable.lastIndexA.set_callback(indexes)
            self.enable_disable.lastIndexB.set_callback(indexes)
            self.insert.index.set_callback(indexes)
            self.delete.firstIndex.set_callback(indexes)
            self.delete.lastIndex.set_callback(indexes)
            # print('set delete')
        except KeyError:  # At init time
            print('set delete NO:')


if __name__ == '__main__':

    a = b'\x01\x04\x02\n\x12\x00\x01\x03\x00\t\x06\x00\x00\n\x00d\xff\x12\x00\x01\t\x04\x00\x00\x00\xff\x12\x00\x01\x04\x07\xe2\x04\x01\x80\t\x05\xff\xff\x01\x01\xff\t\x05\xff\xff\x01\x01\xff\x02\n\x12\x00\x02\x03\x00\t\x06\x00\x00\n\x00d\xff\x12\x00\x02\t\x04\x00\x00\x00\xff\x12\x00\x01\x04\x07\xe2\x04\x02\x80\t\x05\xff\xff\x01\x01\xff\t\x05\xff\xff\x01\x01\xff\x02\n\x12\x00\x03\x03\x00\t\x06\x00\x00\n\x00d\xff\x12\x00\x03\t\x04\x00\x00\x00\xff\x12\x00\x01\x04\x07\xe2\x04\x02\xc0\t\x05\xff\xff\x01\x01\xff\t\x05\xff\xff\x01\x01\xff\x02\n\x12\x00\x04\x03\x00\t\x06\x00\x00\n\x00d\xff\x12\x00\x04\t\x04\x00\x00\x00\xff\x12\x00\x01\x04\x07\xe2\x04\x03\x80\t\x05\xff\xff\x01\x01\xff\t\x05\xff\xff\x01\x01\xff'
    b = Entries(a)

    a = Schedule('0.0.12.0.0.255')
    pass
    print(a)

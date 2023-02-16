from .__class_init__ import *
from ..types.implements import structs


class TYPE(cdt.Enum):
    ELEMENTS = {b'\x01': en.SCHEDULE_TYPE_1,
                b'\x02': en.SCHEDULE_TYPE_2,
                b'\x03': en.SCHEDULE_TYPE_3,
                b'\x04': en.SCHEDULE_TYPE_4,
                b'\x05': en.SCHEDULE_TYPE_5}


class ExecutionTimeDate(cdt.Structure):
    """ Specifies the time and teh date when the script is executed. The two octet-string s contain time and date, in this order; time and date are
     formatted as specified in DLMS UA 1000-1 Ed.12.0 4.1.6.1. Hundredths of second shall be zero. """
    values: tuple[cst.OctetStringTime, cst.OctetStringDate]
    ELEMENTS = (cdt.StructElement(cdt.se.TIME, cst.OctetStringTime),
                cdt.StructElement(cdt.se.DATE, cst.OctetStringDate))

    @property
    def time(self) -> cst.OctetStringTime:
        return self.values[0]

    @property
    def date(self) -> cst.OctetStringDate:
        return self.values[1]


class ExecutionTime(cdt.Array):
    """ Specifies the list of execution time and date """
    TYPE = ExecutionTimeDate


class SingleActionSchedule(ic.COSEMInterfaceClasses):
    """ This IC allows modelling the execution of periodic actions within a meter. Such actions are not necessarily linked to tariffication
    (see “Activity calendar” or “Schedule”).  """
    NAME = cn.SINGLE_ACTION_SCHEDULE
    CLASS_ID = ut.CosemClassId(class_id.SINGLE_ACTION_SCHEDULE)
    VERSION = cdt.Unsigned(0)
    A_ELEMENTS = (ic.ICAElement(an.EXECUTED_SCRIPT, structs.ActionItem),
                  ic.ICAElement(an.TYPE, TYPE),
                  ic.ICAElement(an.EXECUTION_TIME, ExecutionTime))

    def characteristics_init(self):
        """nothing do it"""

    @property
    def executed_script(self) -> structs.ActionItem:
        return self.get_attr(2)

    @property
    def type_(self) -> TYPE:
        return self.get_attr(3)

    @property
    def execution_time(self) -> ExecutionTime:
        return self.get_attr(4)


if __name__ == '__main__':
    a = ExecutionTimeDate(b'\x02\x02\t\x04\x12\x007\x00\t\x05\x07\xe5\x05\x1f\x01')
    a = SingleActionSchedule('0.0.15.0.0.255')
    print(a)

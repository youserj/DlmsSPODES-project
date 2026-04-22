from ..types.implementations import structs
from ..types import cdt, cst
from ..types.type_alias import Attr
from .cosem_interface_class import ICAuto, ICAElement


class TYPE(cdt.Enum, elements=(1, 2, 3, 4, 5)):
    """"""


class ExecutionTimeDate(cdt.Structure):
    """ Specifies the time and teh date when the script is executed. The two octet-string s contain time and date, in this order; time and date are
     formatted as specified in DLMS UA 1000-1 Ed.12.0 4.1.6.1. Hundredths of second shall be zero. """
    time: cst.OctetStringTime
    date: cst.OctetStringDate


class ExecutionTime(cdt.Array):
    """ Specifies the list of execution time and date """
    TYPE = ExecutionTimeDate


class SingleActionSchedule(ICAuto):
    """ This IC allows modelling the execution of periodic actions within a meter. Such actions are not necessarily linked to tariffication
    (see “Activity calendar” or “Schedule”).  """
    CLASS_ID = 22
    VERSION = 0
    A_ELEMENTS = (ICAElement(2, "executed_script", structs.ActionItem),
                  ICAElement(3, "type", TYPE),
                  ICAElement(4, "execution_time", ExecutionTime))
    executed_script: Attr
    type_: Attr
    execution_time: Attr

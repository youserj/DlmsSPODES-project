from typing import Final
from COSEMpdu.data import Enum, Structure, Array
from ..types.implementations import structs
from ..types import cst
from ..types.type_alias import Attr
from .cosem_interface_class import ICAuto, ICAElement


class Type(Enum):
    """attribute type"""
    SIZE_1_WILDCARD_IN_DATE_ALLOWED: Final = 1
    SIZE_N_ALL_TIME_VALUES_SAME_NO_WILDCARDS_IN_DATE: Final = 2
    SIZE_N_ALL_TIME_VALUES_SAME_WILDCARDS_IN_DATE: Final = 3
    SIZE_N_DIFFERENT_TIME_VALUES_NO_WILDCARDS_IN_DATE: Final = 4
    SIZE_N_DIFFERENT_TIME_VALUES_WILDCARDS_IN_DATE: Final = 5


class ExecutionTimeDate(Structure):
    """execution_time_date"""
    time: cst.OctetStringTime
    date: cst.OctetStringDate


ExecutionTime = Array[ExecutionTimeDate]
"""attribute execution_time"""


class SingleActionSchedule(ICAuto):
    """4.5.7 Single action schedule"""
    CLASS_ID = 22
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "executed_script", structs.ActionItem),
        ICAElement(3, "type", Type),
        ICAElement(4, "execution_time", ExecutionTime))
    executed_script: Attr
    type_: Attr
    execution_time: Attr

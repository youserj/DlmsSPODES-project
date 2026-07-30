from typing import Final
from dataclasses import dataclass
from ..types import cst
from COSEMpdu.data import Enum, LongUnsigned, Structure, Array, Integer, CommonDataType
from .cosem_interface_class import ICAuto, ICAElement, ICMElement
from ..types.type_alias import Attr


class ServiceId(Enum):
    """service_id"""
    WRITE_ATTRIBUTE: Final = 1
    EXECUTE_SPECIFIC_METHOD: Final = 2


@dataclass
class ActionSpecification(Structure):
    """action_specification"""
    service_id: ServiceId
    class_id: LongUnsigned
    logical_name: cst.LogicalName
    index: Integer
    parameter: CommonDataType


Actions = Array[ActionSpecification]
"""array action_specification"""


@dataclass
class Script(Structure):
    """script"""
    script_identifier: LongUnsigned
    actions: Actions


Scripts = Array[Script]
"""attribure script"""


class ScriptTable(ICAuto):
    """Script table"""
    CLASS_ID = 9
    VERSION = 0
    A_ELEMENTS = ICAElement(2, "scripts", Scripts),
    M_ELEMENTS = ICMElement(1, "execute", LongUnsigned),
    scripts: Attr

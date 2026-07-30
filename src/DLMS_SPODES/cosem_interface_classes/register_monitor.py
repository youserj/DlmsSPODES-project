from dataclasses import dataclass
from COSEMpdu.data import Array, Structure, CommonDataType
from ..types.implementations import structs
from .cosem_interface_class import ICAuto, ICAElement
from ..types.type_alias import Attr


Thresholds = Array[CommonDataType]


@dataclass
class ActionSet(Structure):
    """action_set"""
    action_up: structs.ActionItem
    action_down: structs.ActionItem


Actions = Array[ActionSet]
"""actions attribute"""


class RegisterMonitor(ICAuto):
    """4.5.6 Register monitor"""
    CLASS_ID = 21
    VERSION = 0
    A_ELEMENTS = (ICAElement(2, "thresholds", Thresholds),
                  ICAElement(3, "monitored_value", structs.ValueDefinition),
                  ICAElement(4, "actions", Actions))
    thresholds: Attr
    monitored_value: Attr
    threshold_normal: Attr

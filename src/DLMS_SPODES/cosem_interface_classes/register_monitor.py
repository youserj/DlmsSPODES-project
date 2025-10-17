from ..types.implementations import structs
from typing import Optional
from ..types import choices, cdt
from .cosem_interface_class import ICAuto, ICAElement
from .Overview import class_id


class Thresholds(cdt.Array):
    """thresholds attribute"""
    TYPE = choices.simple_dt


class ActionSet(cdt.Structure):
    """action_set"""
    action_up: structs.ActionItem
    action_down: structs.ActionItem


class Actions(cdt.Array):
    """actions attribute"""
    TYPE = ActionSet


class RegisterMonitor(ICAuto):
    """4.5.6 Register monitor"""
    CLASS_ID = class_id.REGISTER_MONITOR
    VERSION = 0
    A_ELEMENTS = (ICAElement(2, "thresholds", Thresholds),
                  ICAElement(3, "monitored_value", structs.ValueDefinition),
                  ICAElement(4, "actions", Actions))
    thresholds: Optional[Thresholds]
    monitored_value: Optional[structs.ValueDefinition]
    threshold_normal: Optional[Actions]

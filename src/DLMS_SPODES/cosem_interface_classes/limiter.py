from .. import exceptions as exc
from ..types import choices
from ..types.implementations import structs
from ..types.implementations import double_long_usingneds
from typing import Optional
from ..types import cdt, cst
from .cosem_interface_class import ICAElement, ICAuto, Classifier
from .Overview import class_id


threshold_scaler_unit = cdt.ScalUnitType(b'\x02\x02\x0f\x00\x16\x07')


class ValueDefinitionType(cdt.Structure):
    """ Defines an attribute of an object to be monitored. Only attributes with simple data types are allowed. """
    class_id: cdt.LongUnsigned
    logical_name: cst.LogicalName
    attribute_index: cdt.Integer


class EmergencyProfileType(cdt.Structure):
    """ An emergency_profile is defined by three elements: emergency_profile_id, emergency_activation_time and emergency_duration.
    An emergency profile is activated if the emergency_profile_id element matches one of the elements on the emergency_profile _group_id_list, and time matches the
    emergency_activation_time and emergency_duration element """
    emergency_profile_id: cdt.LongUnsigned
    emergency_activation_time: cst.OctetStringDateTime
    emergency_duration: double_long_usingneds.DoubleLongUnsignedSecond


class EmergencyProfileGroupIdList(cdt.Array):
    """ A list of group id-s of the emergency profile. The emergency profile can be activated only if emergency_profile_id element of the emergency_profile_type matches one of the
    elements on the emergency_profile_group_id list """
    TYPE = cdt.LongUnsigned


class ActionType(cdt.Structure):
    """ Defines the scripts to be executed when the monitored value crosses the threshold for minimal duration time. """
    action_over_threshold: structs.ActionItem
    action_under_threshold: structs.ActionItem


class Limiter(ICAuto):
    """4.5.9 Limiter"""
    CLASS_ID = class_id.LIMITER
    VERSION = 0
    A_ELEMENTS = (ICAElement(2, "monitored_value", structs.ValueDefinition),
                  ICAElement(3, "threshold_active", choices.simple_dt, classifier=Classifier.DYNAMIC),
                  ICAElement(4, "threshold_normal", choices.simple_dt),
                  ICAElement(5, "threshold_emergency", choices.simple_dt),
                  ICAElement(6, "min_over_threshold_duration", double_long_usingneds.DoubleLongUnsignedSecond),
                  ICAElement(7, "min_under_threshold_duration", double_long_usingneds.DoubleLongUnsignedSecond),
                  ICAElement(8, "emergency_profile", EmergencyProfileType),
                  ICAElement(9, "emergency_profile_group_id_list", EmergencyProfileGroupIdList),
                  ICAElement(10, "emergency_profile_active", cdt.Boolean, classifier=Classifier.DYNAMIC),
                  ICAElement(11, "actions", ActionType))
    monitored_value: Optional[structs.ValueDefinition]
    threshold_active: Optional[choices.simple_dt]
    threshold_normal: Optional[choices.simple_dt]
    threshold_emergency: Optional[choices.simple_dt]
    min_over_threshold_duration: Optional[double_long_usingneds.DoubleLongUnsignedSecond]
    min_under_threshold_duration: Optional[double_long_usingneds.DoubleLongUnsignedSecond]
    emergency_profile: Optional[EmergencyProfileType]
    emergency_profile_group_id_list: Optional[EmergencyProfileGroupIdList]
    emergency_profile_active: Optional[cdt.Boolean]
    actions: Optional[ActionType]

    def characteristics_init(self) -> None:
        self._cbs_attr_before_init.update({
            3: lambda value: self.__validate_threshold_scaler_unit(3, value),
            4: lambda value: self.__validate_threshold_scaler_unit(4, value),
            5: lambda value: self.__validate_threshold_scaler_unit(5, value)})

    def __validate_threshold_scaler_unit(self, index: int, value: cdt.CommonDataTypes) -> None:
        if self.monitored_value is not None:
            """let setup"""
        else:
            raise exc.EmptyObj(F"don't set attribute: {index} with {value=} because {self} monitored_value is empty")

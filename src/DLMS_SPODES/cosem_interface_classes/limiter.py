from __future__ import annotations
from .. import cosem_interface_classes
from .. import ITE_exceptions as exc
from .__class_init__ import *
from ..types import choices
from ..types.implementations import structs
threshold_scaler_unit = cdt.ScalUnitType(b'\x02\x02\x0f\x00\x16\x07')


class ValueDefinitionType(cdt.Structure):
    """ Defines an attribute of an object to be monitored. Only attributes with simple data types are allowed. """
    values: tuple[cdt.LongUnsigned, cst.LogicalName, cdt.Integer]
    ELEMENTS = (cdt.StructElement(cdt.se.CLASS_ID, cdt.LongUnsigned),
                cdt.StructElement(cdt.se.LOGICAL_NAME, cst.LogicalName),
                cdt.StructElement(cdt.se.ATTRIBUTE_INDEX, cdt.Integer))

    @property
    def class_id(self) -> cdt.LongUnsigned:
        return self.values[0]

    @property
    def logical_name(self) -> cst.LogicalName:
        return self.values[1]

    @property
    def attribute_index(self) -> cdt.Integer:
        return self.values[2]


class EmergencyProfileType(cdt.Structure):
    """ An emergency_profile is defined by three elements: emergency_profile_id, emergency_activation_time and emergency_duration.
    An emergency profile is activated if the emergency_profile_id element matches one of the elements on the emergency_profile _group_id_list, and time matches the
    emergency_activation_time and emergency_duration element """
    values: tuple[cdt.LongUnsigned, cst.OctetStringDateTime, cdt.DoubleLongUnsigned]
    ELEMENTS = (cdt.StructElement(cdt.se.EMERGENCY_PROFILE_ID, cdt.LongUnsigned),
                cdt.StructElement(cdt.se.EMERGENCY_ACTIVATION_TIME, cst.OctetStringDateTime),
                cdt.StructElement(cdt.se.EMERGENCY_DURATION, cdt.DoubleLongUnsigned))

    @property
    def emergency_profile_id(self) -> cdt.LongUnsigned:
        return self.values[0]

    @property
    def emergency_activation_time(self) -> cst.OctetStringDateTime:
        """defines the date and time when the emergency_profile activated"""
        return self.values[1]

    @property
    def emergency_duration(self) -> cdt.DoubleLongUnsigned:
        """defines the duration in seconds, for which the emergency_profile is activated"""
        return self.values[2]


class EmergencyProfileGroupIdList(cdt.Array):
    """ A list of group id-s of the emergency profile. The emergency profile can be activated only if emergency_profile_id element of the emergency_profile_type matches one of the
    elements on the emergency_profile_group_id list """
    TYPE = cdt.LongUnsigned


class ActionType(cdt.Structure):
    """ Defines the scripts to be executed when the monitored value crosses the threshold for minimal duration time. """
    values: tuple[structs.ActionItem, structs.ActionItem]
    ELEMENTS = (cdt.StructElement(cdt.se.ACTION_OVER_THRESHOLD, structs.ActionItem),
                cdt.StructElement(cdt.se.ACTION_UNDER_THRESHOLD, structs.ActionItem))

    @property
    def action_over_threshold(self) -> structs.ActionItem:
        """defines the action when the value of the attribute monitored crosses the threshold in upwards direction and remains over threshold
        for minimal over threshold duration time"""
        return self.values[0]

    def action_under_threshold(self) -> structs.ActionItem:
        """the action when the value of the attribute monitored crosses the threshold in the downwards direction and remains under threshold
        for minimal under threshold duration time."""
        return self.values[1]


class Limiter(ic.COSEMInterfaceClasses):
    """ Instances of the Limiter interface class allow defining a set of actions that are executed when the value of a value attribute of a monitored object “Data”, “Register”,
    “Extended Register”, “Demand Register”, etc. crosses the threshold value for at least minimal duration time.
        The threshold value can be normal or emergency threshold. The emergency threshold is activated via the emergency profile defined by emergency profile id, activation start
    time, and duration. The emergency profile id element is matched to an emergency profile group id: this mechanism enables the activation of the emergency threshold only
    for a specific emergency group. """
    NAME = cn.LIMITER
    CLASS_ID = ClassID.LIMITER
    VERSION = Version.V0
    A_ELEMENTS = (ic.ICAElement(an.MONITORED_VALUE, structs.ValueDefinition),
                  ic.ICAElement(an.THRESHOLD_ACTIVE, choices.simple_dt),
                  ic.ICAElement(an.THRESHOLD_NORMAL, choices.simple_dt),
                  ic.ICAElement(an.THRESHOLD_EMERGENCY, choices.simple_dt),
                  ic.ICAElement(an.MIN_OVER_THRESHOLD_DURATION, cdt.DoubleLongUnsigned),
                  ic.ICAElement(an.MIN_UNDER_THRESHOLD_DURATION, cdt.DoubleLongUnsigned),
                  ic.ICAElement(an.EMERGENCY_PROFILE, EmergencyProfileType),
                  ic.ICAElement(an.EMERGENCY_PROFILE_GROUP_ID_LIST, EmergencyProfileGroupIdList),
                  ic.ICAElement(an.EMERGENCY_PROFILE_ACTIVE, cdt.Boolean),
                  ic.ICAElement(an.ACTIONS, ActionType))

    def characteristics_init(self):
        self._cbs_attr_post_init.update({2: lambda: self.__set_threshold_scaler_unit((3, 4, 5)),
                                         3: lambda: self.__set_threshold_scaler_unit((3,)),
                                         4: lambda: self.__set_threshold_scaler_unit((4,)),
                                         5: lambda: self.__set_threshold_scaler_unit((5,)),
                                         6: lambda: self.__set_duration_scaler_unit(6),
                                         7: lambda: self.__set_duration_scaler_unit(7)})

    @property
    def monitored_value(self) -> structs.ValueDefinition:
        return self.get_attr(2)

    @property
    def threshold_active(self) -> choices.simple_dt:
        return self.get_attr(3)

    @property
    def threshold_normal(self) -> choices.simple_dt:
        return self.get_attr(4)

    @property
    def threshold_emergency(self) -> choices.simple_dt:
        return self.get_attr(5)

    @property
    def min_over_threshold_duration(self) -> cdt.DoubleLongUnsigned:
        return self.get_attr(6)

    @property
    def min_under_threshold_duration(self) -> cdt.DoubleLongUnsigned:
        return self.get_attr(7)

    @property
    def emergency_profile(self) -> EmergencyProfileType:
        return self.get_attr(8)

    @property
    def emergency_profile_group_id_list(self) -> EmergencyProfileGroupIdList:
        return self.get_attr(9)

    @property
    def emergency_profile_active(self) -> cdt.Boolean:
        return self.get_attr(10)

    @property
    def actions(self) -> ActionType:
        return self.get_attr(11)

    def __set_duration_scaler_unit(self, attr_index: int):
        self.get_attr(attr_index).SCALER_UNIT = threshold_scaler_unit

    def __set_threshold_scaler_unit(self, attr_indexes: tuple[int, ...]):
        if self.monitored_value is not None:
            try:
                match self.collection.get_object(self.monitored_value):
                    case cosem_interface_classes.register.Register() | cosem_interface_classes.extended_register.ExtendedRegister() as obj:
                        for index in attr_indexes:
                            if self.get_attr(index) is not None:
                                self.get_attr(index).SCALER_UNIT = obj.scaler_unit
                        print('set post name')
            except exc.NoObject as e:
                print(F'For {self} threshold Scaler-unit not set. {e}')
        else:
            print('monitored_value is empty')


if __name__ == '__main__':
    a = Limiter('0.0.0.0.0.0')
    print(a)

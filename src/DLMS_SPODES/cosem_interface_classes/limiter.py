from .. import cosem_interface_classes
from .. import ITE_exceptions as exc
from .__class_init__ import *
from ..types import choices
from ..types.implementations import structs, long_unsigneds, double_long_usingneds
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
                  ic.ICAElement(an.THRESHOLD_ACTIVE, choices.simple_dt, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement(an.THRESHOLD_NORMAL, choices.simple_dt),
                  ic.ICAElement(an.THRESHOLD_EMERGENCY, choices.simple_dt),
                  ic.ICAElement(an.MIN_OVER_THRESHOLD_DURATION, double_long_usingneds.DoubleLongUnsignedSecond),
                  ic.ICAElement(an.MIN_UNDER_THRESHOLD_DURATION, double_long_usingneds.DoubleLongUnsignedSecond),
                  ic.ICAElement(an.EMERGENCY_PROFILE, EmergencyProfileType),
                  ic.ICAElement(an.EMERGENCY_PROFILE_GROUP_ID_LIST, EmergencyProfileGroupIdList),
                  ic.ICAElement(an.EMERGENCY_PROFILE_ACTIVE, cdt.Boolean, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement(an.ACTIONS, ActionType))

    def characteristics_init(self):
        self.set_attr(6, None)
        self.set_attr(7, None)
        self._cbs_attr_post_init.update({2: self.__set_threshold_scaler_unit})
        self._cbs_attr_before_init.update({
            3: lambda value: self.__validate_threshold_scaler_unit(3, value),
            4: lambda value: self.__validate_threshold_scaler_unit(4, value),
            5: lambda value: self.__validate_threshold_scaler_unit(5, value)})

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

    def __set_threshold_scaler_unit(self):
        if self.monitored_value is not None:
            m_o: cosem_interface_classes.collection.Register = self.collection.get_object(self.monitored_value)  # todo: add ExtReg and Data types annotation
            """monitored object"""
            m_v: cdt.CommonDataTypes = m_o.get_attr(int(self.monitored_value.attribute_index))
            """monitored value"""
            if m_v is not None:
                for index in (3, 4, 5):
                    self.set_attr(index, m_v.encoding)
                    s_v: cdt.CommonDataTypes = self.get_attr(index)
                    """set value"""
                    s_v.clear()
                    if self.monitored_value.class_id == long_unsigneds.ClassIDCDT.REGISTER or long_unsigneds.ClassIDCDT.EXT_REGISTER:
                        s_v.SCALER_UNIT = m_o.scaler_unit
            else:
                raise exc.EmptyObj(F"monitored_value: {m_o} hasn't value")
        else:
            raise exc.EmptyObj(F"don't set attributes: 3, 4, 5 because {self} monitored_value is empty")

    def __validate_threshold_scaler_unit(self, index: int, value: cdt.CommonDataTypes):
        if self.monitored_value is not None:
            """let setup"""
        else:
            raise exc.EmptyObj(F"don't set attribute: {index} with {value=} because {self} monitored_value is empty")

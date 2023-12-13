from .__class_init__ import *
from ..types import choices
from ..types.implementations import structs
threshold_scaler_unit = cdt.ScalUnitType(b'\x02\x02\x0f\x00\x16\x07')


class Thresholds(cdt.Array):
    TYPE = choices.simple_dt


class ActionSet(cdt.Structure):
    """TODO:"""
    action_up: structs.ActionItem
    action_down: structs.ActionItem


class Actions(cdt.Array):
    """Defines the scripts to be executed when the monitored attribute of the referenced object crosses the corresponding threshold. The attribute actions has exactly
    the same number of elements as the attribute thresholds. The ordering of the action_items corresponds to the ordering of the thresholds (see above)."""
    TYPE = ActionSet


class RegisterMonitor(ic.COSEMInterfaceClasses):
    """ DLMS UA 1000-1 Ed.14. 4.5.6. This IC allows modelling the function of monitoring of values modelled by “Data”, “Register”, “Extended register” or “Demand register” objects.
    It allows specifying thresholds, the value monitored, and a set of scripts (see 4.5.2) that are executed when the value monitored crosses a threshold """
    CLASS_ID = ClassID.REGISTER_MONITOR
    VERSION = Version.V0
    A_ELEMENTS = (ic.ICAElement(an.THRESHOLDS, Thresholds),
                  ic.ICAElement(an.MONITORED_VALUE, structs.ValueDefinition),
                  ic.ICAElement(an.ACTIONS, Actions))

    def characteristics_init(self):
        self.set_attr(2, None)
        self._cbs_attr_post_init.update({3: self.__set_threshold_type})

    @property
    def thresholds(self) -> Thresholds:
        return self.get_attr(2)

    @property
    def monitored_value(self) -> structs.ValueDefinition:
        return self.get_attr(3)

    @property
    def threshold_normal(self) -> Actions:
        return self.get_attr(4)

    def __set_threshold_type(self):
        self.thresholds.set_type(self.collection.get_object(self.monitored_value.logical_name).get_attr(int(self.monitored_value.attribute_index)).__class__)

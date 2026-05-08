from typing import Final
from ..types.implementations import integers
from COSEMpdu.data import Enum, Boolean
from .cosem_interface_class import ICAElement, ICMElement, Classifier, ICAuto
from ..types.type_alias import Attr


class ControlState(Enum):
    """control_state"""
    DISCONNECTED: Final = 0
    CONNECTED: Final = 1
    READY_FOR_RECONNECTION: Final = 2


class ControlMode(Enum):
    """control_mode"""
    ALWAYS_CONNECTED: Final = 0
    BCFGDE: Final = 1
    BCFGAE: Final = 2
    BCGDE: Final = 3
    BCGAE: Final = 4
    BCFGDEH: Final = 5
    BCGDEH: Final = 6
    BCFMDE: Final = 129
    BCFMAE: Final = 130
    BCMDE: Final = 131
    BCMA: Final = 132
    BCMAK: Final = 133
    BCMSDEP: Final = 134


class DisconnectControl(ICAuto):
    """4.5.8 Disconnect control"""
    CLASS_ID = 70
    VERSION = 0
    A_ELEMENTS = (
        ICAElement(2, "output_state", Boolean, classifier=Classifier.DYNAMIC),
        ICAElement(3, "control_state", ControlState, classifier=Classifier.DYNAMIC),
        ICAElement(4, "control_mode", ControlMode))
    M_ELEMENTS = (
        ICMElement(1, "remote_disconnect", integers.IntegerValue0),
        ICMElement(2, "remote_reconnect", integers.IntegerValue0))
    output_state: Attr
    control_state: Attr
    control_mode: Attr

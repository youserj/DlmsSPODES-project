from itertools import chain
from ..config_parser import get_message
from ..types.implementations import integers
from typing import Optional
from ..types import cdt
from .cosem_interface_class import ICAElement, ICMElement, Classifier, ICAuto
from .Overview import class_id


class ControlState(cdt.Enum, elements=(0, 1, 2)):
    """ Shows the internal state of the disconnect control object. """


class ControlMode(cdt.Enum, elements=tuple(chain(range(7), range(129, 135)))):
    """ Configures the behaviour of the disconnect control object for all triggers. Local disconnection is always possible.
    To suppress local disconnection, the corresponding trigger must be inhibited. """

    @staticmethod
    def get_letters(value: int) -> str:
        """return transition litters"""
        match value:
            case 0:   return ""
            case 1:   return "bcfgde"
            case 2:   return "bcfgae"
            case 3:   return "bcgde"
            case 4:   return "bcgae"
            case 5:   return "bcfgdeh"
            case 6:   return "bcgdeh"
            case 129: return "bcfmde"
            case 130: return "bcfmae"
            case 131: return "bcmde"
            case 132: return "bcma"
            case 133: return "bcmak"
            case 134: return "bcmsdep"
            case _:   raise ValueError(F"unknown {value=}")


class OutputState(cdt.Boolean):
    """ Shows the actual physical state of the disconnect unit, i.e. if an electricity breaker or a gas valve is open or closed. TRUE = connected, FALSE = disconnected.
    In electricity metering, the supply is connected when the disconnector device is closed. In gas and water metering, the supply is connected when the valve is open """
    def __str__(self):
        return get_message("$disconnected$") if self.contents == b'\x00' else get_message("$connected$")


class DisconnectControl(ICAuto):
    """4.5.8 Disconnect control"""
    CLASS_ID = class_id.DISCONNECT_CONTROL
    VERSION = 0
    A_ELEMENTS = (ICAElement(2, "output_state", OutputState, classifier=Classifier.DYNAMIC),
                  ICAElement(3, "control_state", ControlState, classifier=Classifier.DYNAMIC),
                  ICAElement(4, "control_mode", ControlMode))
    M_ELEMENTS = (ICMElement(1, "remote_disconnect", integers.Only0),
                  ICMElement(2, "remote_reconnect", integers.Only0))
    output_state: Optional[cdt.Boolean]
    control_state: Optional[ControlState]
    control_mode: Optional[ControlMode]

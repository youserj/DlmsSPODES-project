from .__class_init__ import *
from ..types.implementations import integers
from itertools import chain
from ..config_parser import get_message
from .overview import VERSION_0


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


class DisconnectControl(ic.COSEMInterfaceClasses):
    """DLMS UA 1000-1 Ed. 14 4.5.8 Disconnect control"""
    CLASS_ID = ClassID.DISCONNECT_CONTROL
    VERSION = VERSION_0
    A_ELEMENTS = (ic.ICAElement("output_state", OutputState, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("control_state", ControlState, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement("control_mode", ControlMode))
    M_ELEMENTS = (ic.ICMElement("remote_disconnect", integers.Only0),
                  ic.ICMElement("remote_reconnect", integers.Only0))

    @property
    def output_state(self) -> cdt.Boolean:
        return self.get_attr(2)

    @property
    def control_state(self) -> ControlState:
        return self.get_attr(3)

    @property
    def control_mode(self) -> ControlMode:
        return self.get_attr(4)

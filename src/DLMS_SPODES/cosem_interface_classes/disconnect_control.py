from .__class_init__ import *
from ..types.implements import integers


class ControlState(cdt.Enum):
    """ Shows the internal state of the disconnect control object. """
    ELEMENTS = {b'\x00': en.DISCONNECTED,
                b'\x01': en.CONNECTED,
                b'\x02': en.READY_FOR_RECONNECTION}


class ControlMode(cdt.Enum):
    """ Configures the behaviour of the disconnect control object for all triggers. Local disconnection is always possible.
    To suppress local disconnection, the corresponding trigger must be inhibited. """
    ELEMENTS = {b'\x00':        F"0: {en.CONTROL_MODE_0}",
                b'\x01':        F"1: {en.CONTROL_MODE_1}",
                b'\x02':        F"2: {en.CONTROL_MODE_2}",
                b'\x03':        F"3: {en.CONTROL_MODE_3}",
                b'\x04':        F"4: {en.CONTROL_MODE_4}",
                b'\x05':        F"5: {en.CONTROL_MODE_5}",
                b'\x06':        F"6: {en.CONTROL_MODE_6}",
                bytes((129,)):  F"129: {en.RU_CONTROL_MODE_129}",
                bytes((130,)):  F"130: {en.RU_CONTROL_MODE_130}",
                bytes((131,)):  F"131: {en.RU_CONTROL_MODE_131}",
                bytes((132,)):  F"132: {en.RU_CONTROL_MODE_132}",
                bytes((133,)):  F"133: {en.RU_CONTROL_MODE_133}",
                bytes((134,)):  F"134: {en.RU_CONTROL_MODE_134}"}

    def get_letters(self) -> str:
        """return transition litters"""
        match int(self):
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
            case _:   raise ValueError(F"unknown {self=}")


class OutputState(cdt.Boolean):
    """ Shows the actual physical state of the disconnect unit, i.e. if an electricity breaker or a gas valve is open or closed. TRUE = connected, FALSE = disconnected.
    In electricity metering, the supply is connected when the disconnector device is closed. In gas and water metering, the supply is connected when the valve is open """
    def __str__(self):
        return en.DISCONNECTED if self.contents == b'\x00' else en.CONNECTED


class DisconnectControl(ic.COSEMInterfaceClasses):
    """ Instances of the Disconnect control interface class manage an internal or external disconnect unit of the meter (e.g. electricity breaker,
    gas valve) in order to connect or disconnect, partly or entirely, the premises of the consumer.
    Disconnect and reconnect can be requested:
        • Remotely, via a communication channel: remote_disconnect, remote_reconnect;
        • Manually, using e.g. a push button: manual_disconnect, manual_reconnect;
        • Locally, by a function of the meter, e.g. limiter, prepayment: local_disconnect. Local reconnection is not possible: reconnection after a
          local_disconnect always requires a manual intervention.
    The possible states and state transitions of the Disconnect control interface class are shown in DLMS UA 1000-1 Ed. 12.0 table 25.The Disconnect
    control object doesn't feature a memory, i.e. any commands are executed immediately
                                States:
    State number | State name            | State description
    0            |Disconnected           |The output_state is set to FALSE and the consumer is disconnected.
    1            |Connected              |The output_state is set to TRUE and the consumer is connected.
    2            |Ready_for_reconnection |The output_state is set to FALSE and the consumer is disconnected.Reconnection requires manual intervention.
                            State transitions:
    Transition |Transition name  | State description
    a          |remote_reconnect |Moves the Disconnect control object from the Disconnected (0) state directly to the Connected (1) state without
                                  manual intervention
    b          |remote_disconnect|Moves the Disconnect control object from the Connected (1) state to the Disconnected (0) state
    c          |remote_disconnect| Moves the Disconnect control object from the Ready_for_reconnection (2) state to the Disconnected (0) state
    d          |remote_reconnect | Moves the Disconnect control object from the Disconnected (0) state to the Ready_for_reconnection (2) state
                                   From this state, it is possible to move to the Connected (2) state via the manual_reconnect transition (e)
    e          |manual_reconnect | Moves the Disconnect control object from the Ready_for_connection (2) state to the Connected (1) state
    f          |manual_disconnect| Moves the Disconnect control object from the Connected (1) state to the Ready_for_connection (2) state From this
                                   state, it is possible to move back to the Connected (2) state via the manual_reconnect transition (e)
    g          |local_disconnect | Moves the Disconnect control object from the Connected (1) state to the Ready_for_connection (2) state From this
                                   state, it is possible to move back to the Connected (2) state via the manual_reconnect transition (e)
                                   NOTE Transitions f) and g) are essentially the same, but their trigger is different."""
    NAME = cn.DISCONNECT_CONTROL
    CLASS_ID = ut.CosemClassId(class_id.DISCONNECT_CONTROL)
    VERSION = cdt.Unsigned(0)
    A_ELEMENTS = (ic.ICAElement(an.OUTPUT_STATE, OutputState),
                  ic.ICAElement(an.CONTROL_STATE, ControlState),
                  ic.ICAElement(an.CONTROL_MODE, ControlMode))
    M_ELEMENTS = (ic.ICMElement(mn.REMOTE_DISCONNECT, integers.Only0),
                  ic.ICMElement(mn.REMOTE_RECONNECT, integers.Only0))

    def characteristics_init(self):
        """nothing do it"""

    @property
    def output_state(self) -> cdt.Boolean:
        return self.get_attr(2)

    @property
    def control_state(self) -> ControlState:
        return self.get_attr(3)

    @property
    def control_mode(self) -> ControlMode:
        return self.get_attr(4)

    @property
    def remote_disconnect(self) -> cdt.Integer:
        return self.get_meth(1)

    @property
    def remote_reconnect(self) -> cdt.Integer:
        return self.get_meth(2)

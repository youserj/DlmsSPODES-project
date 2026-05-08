from . import ver0
from typing import Final
from COSEMpdu.data import Enum
from ..cosem_interface_class import ICAElement, Classifier, update_collection, ICMElement
from ...types.implementations import integers


class Mode(Enum):
    """mode attribute"""
    NO_AUTO_DIALING: Final = 0
    AUTO_DIALING_ALLOWED_ANYTIME: Final = 1
    AUTO_DIALING_ALLOWED_WITHIN_CALLING_WINDOW: Final = 2
    REGULAR_AUTO_DIALING_ALLOWED_WITHIN_CALLING_WINDOW_ALARM_INITIATED_AUTO_DIALING_ALLOWED_ANYTIME: Final = 3
    SMS_SENDING_VIA_PUBLIC_LAND_MOBILE_NETWORK: Final = 4
    SMS_SENDING_VIA_PSTN: Final = 5
    EMAIL_SENDING: Final = 6
    PERMANENTLY_CONNECTED_TO_COMMUNICATION_NETWORK: Final = 101
    PERMANENTLY_CONNECTED_TO_COMMUNICATION_NETWORK_WITHIN_CALLING_WINDOW: Final = 102
    CONNECTED_TO_COMMUNICATION_NETWORK_ON_INVOCATION_WITHIN_CALLING_WINDOW: Final = 103
    CONNECTED_TO_COMMUNICATION_NETWORK_ON_INVOCATION: Final = 104


class AutoConnect(ver0.PSTNAutoDial):
    """4.7.6 Auto connect"""
    VERSION = 2
    A_ELEMENTS = update_collection(
        ver0.PSTNAutoDial.A_ELEMENTS,
        ICAElement(2, "mode", Mode, classifier=Classifier.STATIC)
    )
    M_ELEMENTS = ICMElement(1, "connect", integers.IntegerValue0),

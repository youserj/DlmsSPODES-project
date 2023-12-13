from ..__class_init__ import *
from ...types.implementations.enums import CommSpeed


class InitializationStringElement(cdt.Structure):
    """ Request - Response strings"""
    request: cdt.OctetString
    response: cdt.OctetString


class InitializationString(cdt.Array):
    """ This data contains all the necessary initialization commands to be sent to the modem in order to  configure it properly. This may include the configuration of special
    modem features.
    If the array contains more than one initialization string element, they are subsequently sent to the modem after receiving an answer matching the defined response.
    It is assumed that the modem is pre-configured so that it accepts the initialization_string . If no initialization is needed, the initialization string is empty."""
    TYPE=InitializationStringElement


class ModemProfileElement(cdt.OctetString):
    """ TODO: can be OK, CONNECT, RING, NO CARRIER, ERROR, CONNECT 1 200, NO DIAL TONE, BUSY, NO ANSWER, CONNECT 600, CONNECT 2 400, CONNECT 4 800, CONNECT 9 600, CONNECT 14 400,
    CONNECT 28 800, CONNECT 36 600, CONNECT 56 000"""

    def __init__(self, value: bytes = b'OK'.hex()):
        super(ModemProfileElement, self).__init__(value)
        if self.decode() not in self.get_validate_values():
            raise ValueError(F'Got modem profile element {self.decode()}, expected {b", ".join(self.get_validate_values())}')
        else:
            pass

    @staticmethod
    def get_validate_values() -> tuple[bytes, ...]:
        return b'OK', b'CONNECT', b'RING', b'NO CARRIER', b'ERROR', b'CONNECT 1 200', b'NO DIAL TONE', b'BUSY', b'NO ANSWER', b'CONNECT 600', b'CONNECT 2 400', b'CONNECT 4 800', \
               b'CONNECT 9 600', b'CONNECT 14 400', b'CONNECT 28 800', b'CONNECT 36 600', b'CONNECT 56 000'


class ModemProfile(cdt.Array):
    """ This data defines the mapping from Hayes standard commands/responses to modem specific strings. Shall contain the corresponding stings for the modem used in following 
    order"""
    TYPE = ModemProfileElement


class PSTNModemConfiguration(ic.COSEMInterfaceClasses):
    """ An  instance of the 'PSTN modem configuration' IC stores data related to the initialization of modems, which are used for data transfer from/to a device. Several modems
    can be configured."""
    CLASS_ID = ClassID.MODEM_CONFIGURATION
    VERSION = Version.V0
    A_ELEMENTS = (ic.ICAElement(an.COMM_SPEED, CommSpeed, 0, 9, 5),
                  ic.ICAElement(an.INITIALIZATION_STRING, InitializationString),
                  ic.ICAElement(an.MODEM_PROFILE, ModemProfile))

    def characteristics_init(self):
        """nothing do it"""

    @property
    def comm_speed(self) -> CommSpeed:
        return self.get_attr(2)

    @property
    def initialization_string(self) -> InitializationString:
        return self.get_attr(3)

    @property
    def modem_profile(self) -> ModemProfile:
        return self.get_attr(4)


if __name__ == '__main__':
    b = ModemProfileElement.get_validate_values().index('RING')
    a = ModemProfileElement(b'\x09\x04\x33\x45\x54\x33')

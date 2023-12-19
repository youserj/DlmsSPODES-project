from ..__class_init__ import *
from . import ver0


class InitializationStringElement(cdt.Structure):
    """ Request - Response strings"""
    request: cdt.OctetString
    response: cdt.OctetString
    delay_after_response: cdt.LongUnsigned


class InitializationString(cdt.Array):
    """ Contains all the necessary initialization commands to be sent to the modem in order to configure it properly. This may include the configuration of special modem
    features. If the array contains more than one initialization_string_element, the requests are set in a sequence.The next request is sent after the expected response matching
    the previous request and waiting a delay-after-response time [ms], to allow the modem toe execute teh request.
    It is assumed that the modem is per-configured so that it accepts the initialization-string. If no initialization is needed, the initialization string is empty. """
    TYPE = InitializationStringElement


class ModemConfigurationVer1(ic.COSEMInterfaceClasses):
    """ This IC allow modelling the configuration and initialisation of modems used for data transfer from/to a device. Several modems can be configured."""
    CLASS_ID = ut.CosemClassId(27)
    VERSION = Version.V1
    A_ELEMENTS = (ver0.PSTNModemConfiguration.get_attr_element(2),
                  ic.ICAElement("initialization_string", InitializationString),
                  ver0.PSTNModemConfiguration.get_attr_element(4))

    def characteristics_init(self):
        """nothing do it"""

    @property
    def initialization_string(self) -> InitializationString:
        return self.get_attr(3)


if __name__ == '__main__':
    a = ModemConfigurationVer1('0.0.2.0.0.255')
    print(a)

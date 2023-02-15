from ..__class_init__ import *
import ver0


class InitializationStringElement(cdt.Structure):
    """ Request - Response strings"""
    values: tuple[cdt.OctetString, cdt.OctetString, cdt.LongUnsigned]
    ELEMENTS = (cdt.StructElement(cdt.se.REQUEST, cdt.OctetString),
                cdt.StructElement(cdt.se.RESPONSE, cdt.OctetString),
                cdt.StructElement(cdt.se.DELAY_AFTER_RESPONSE, cdt.LongUnsigned))

    @property
    def request(self) -> cdt.OctetString:
        return self.values[0]

    @property
    def response(self) -> cdt.OctetString:
        return self.values[1]

    @property
    def delay_after_response(self) -> cdt.LongUnsigned:
        return self.values[2]


class InitializationString(cdt.Array):
    """ Contains all the necessary initialization commands to be sent to the modem in order to configure it properly. This may include the configuration of special modem
    features. If the array contains more than one initialization_string_element, the requests are set in a sequence.The next request is sent after the expected response matching
    the previous request and waiting a delay-after-response time [ms], to allow the modem toe execute teh request.
    It is assumed that the modem is per-configured so that it accepts the initialization-string. If no initialization is needed, the initialization string is empty. """
    TYPE = InitializationStringElement


class ModemConfigurationVer1(ic.COSEMInterfaceClasses):
    """ This IC allow modelling the configuration and initialisation of modems used for data transfer from/to a device. Several modems can be configured."""
    NAME = cn.MODEM_CONFIGURATION
    CLASS_ID = ut.CosemClassId(27)
    VERSION = cdt.Unsigned(1)
    A_ELEMENTS = (ver0.PSTNModemConfiguration.get_attr_element(2),
                  ic.ICAElement(an.INITIALIZATION_STRING, InitializationString),
                  ver0.PSTNModemConfiguration.get_attr_element(4))

    def characteristics_init(self):
        """nothing do it"""

    @property
    def initialization_string(self) -> InitializationString:
        return self.get_attr(3)


if __name__ == '__main__':
    a = ModemConfigurationVer1('0.0.2.0.0.255')
    print(a)

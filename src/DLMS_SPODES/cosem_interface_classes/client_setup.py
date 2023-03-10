from .__class_init__ import *


class CommunicationChannel(cdt.Enum):
    """ ONLY IN CLIENT. Current channel communication. Use with HDLC setup """
    ELEMENTS = {
        b'\x00': en.OPTICAL_PORT,
        b'\x01': en.RS485,
        b'\x02': en.TCP_IP}


class LocalPortNames(cdt.Structure):
    """ Consist names of optical_port and rs-485 by ordering of hdlc_setup """
    values: tuple[cdt.VisibleString, cdt.VisibleString]
    # values: tuple[cdt.Integer, cdt.Integer]
    ELEMENTS = (cdt.StructElement(cdt.se.ITE_OPTICAL_PORT_NAME, cdt.VisibleString),
                cdt.StructElement(cdt.se.ITE_RS485_NAME, cdt.VisibleString))

    @property
    def optical_port_name(self) -> cdt.VisibleString:
        return self.values[0]

    @property
    def rs485_name(self) -> cdt.VisibleString:
        return self.values[1]


class ClientSetup(ic.COSEMInterfaceClasses):
    """ For client setting options """
    NAME = cn.CLIENT_SETUP
    CLASS_ID = ClassID.CLIENT_SETUP
    VERSION = Version.V0
    A_ELEMENTS = (ic.ICAElement(an.CHANNEL_COMMUNICATION, CommunicationChannel, default=0),
                  ic.ICAElement(an.SERIAL_PORT_NAMES, LocalPortNames, default=('COM3', 'COM4')),
                  ic.ICAElement(an.CLIENT_NAME, cdt.VisibleString, default="new_device"))

    def characteristics_init(self):
        """nothing do it"""

    @property
    def channel_communication(self) -> CommunicationChannel:
        return self.get_attr(2)

    @property
    def serial_port_names(self) -> LocalPortNames:
        return self.get_attr(3)

    @property
    def client_name(self) -> cdt.VisibleString:
        return self.get_attr(4)


if __name__ == '__main__':
    a = cdt.VisibleString('счетчик №1')
    b = a.decode()
    a = ClientSetup('1.1.1.1.1.1')
    print(a)

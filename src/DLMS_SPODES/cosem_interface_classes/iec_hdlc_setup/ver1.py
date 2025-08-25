from collections import deque
from ..__class_init__ import *
from ...types.implementations.enums import CommSpeed
from ..overview import VERSION_0


class IECHDLCSetup(ic.COSEMInterfaceClasses):
    """ This IC allows modelling and configuring communication channels according to Clause 8 of DLMS UA 1000-2 Ed. 8.0:2014. Several communication cnannels can be configured. """
    CLASS_ID = ClassID.IEC_HDLC_SETUP
    VERSION = VERSION_0
    A_ELEMENTS = (ic.ICAElement("comm_speed", CommSpeed, 0, 9, 5),
                  ic.ICAElement("windows_size_transmit", cdt.Unsigned, 1, 7, 1),
                  ic.ICAElement("windows_size_receive", cdt.Unsigned, 1, 7, 1),
                  ic.ICAElement("max_info_field_length_transmit", cdt.LongUnsigned, 128, 32, 2030),
                  ic.ICAElement("max_info_field_length_receive", cdt.LongUnsigned, 128, 32, 2030),
                  ic.ICAElement("inter_octet_time_out", cdt.LongUnsigned, 20, 6000, 25),
                  ic.ICAElement("inactivity_time_out", cdt.LongUnsigned, 0, default=120),
                  ic.ICAElement("device_address", cdt.LongUnsigned, 0x0001, 0x3ffd, default=0x10))  # TODO: not according by BlueBook: need default, minimum is other

    def characteristics_init(self):
        """nothing do it"""

    @property
    def comm_speed(self) -> CommSpeed:
        return self.get_attr(2)

    @property
    def windows_size_transmit(self) -> cdt.Unsigned:
        return self.get_attr(3)

    @property
    def windows_size_receive(self) -> cdt.Unsigned:
        return self.get_attr(4)

    @property
    def max_info_field_length_transmit(self) -> cdt.LongUnsigned:
        return self.get_attr(5)

    @property
    def max_info_field_length_receive(self) -> cdt.LongUnsigned:
        return self.get_attr(6)

    @property
    def inter_octet_time_out(self) -> cdt.LongUnsigned:
        return self.get_attr(7)

    @property
    def inactivity_time_out(self) -> cdt.LongUnsigned:
        return self.get_attr(8)

    @property
    def device_address(self) -> cdt.LongUnsigned:
        return self.get_attr(9)

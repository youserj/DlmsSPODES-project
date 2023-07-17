from collections import deque
from ..__class_init__ import *
from ...types.implementations.enums import CommSpeed


class IECHDLCSetup(ic.COSEMInterfaceClasses):
    """ This IC allows modelling and configuring communication channels according to Clause 8 of DLMS UA 1000-2 Ed. 8.0:2014. Several communication cnannels can be configured. """
    NAME = cn.IEC_HDLC_SETUP
    CLASS_ID = ClassID.IEC_HDLC_SETUP
    VERSION = Version.V1
    A_ELEMENTS = (ic.ICAElement(an.COMM_SPEED, CommSpeed, 0, 9, 5),
                  ic.ICAElement(an.WINDOWS_SIZE_TRANSMIT, cdt.Unsigned, 1, 7, 1),
                  ic.ICAElement(an.WINDOWS_SIZE_RECEIVE, cdt.Unsigned, 1, 7, 1),
                  ic.ICAElement(an.MAX_INFO_FIELD_LENGTH_TRANSMIT, cdt.LongUnsigned, 128, 32, 2030),
                  ic.ICAElement(an.MAX_INFO_FIELD_LENGTH_RECEIVE, cdt.LongUnsigned, 128, 32, 2030),
                  ic.ICAElement(an.INTER_OCTET_TIME_OUT, cdt.LongUnsigned, 20, 6000, 25),
                  ic.ICAElement(an.INACTIVITY_TIME_OUT, cdt.LongUnsigned, 0, default=120),
                  ic.ICAElement(an.DEVICE_ADDRESS, cdt.LongUnsigned, 0x0001, 0x3ffd, default=0x10))  # TODO: not according by BlueBook: need default, minimum is other

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

    @property
    def max_info_transmit(self) -> bytes | None:
        """ return max_info_field_length_transmit if it not default """
        if self.max_info_field_length_transmit.decode() != self.get_attr_element(5).default:
            return self.max_info_field_length_transmit.contents

    @property
    def max_info_receive(self) -> bytes | None:
        """ return max_info_field_length_receive if it not default """
        if self.max_info_field_length_receive.decode() != self.get_attr_element(6).default:
            return self.max_info_field_length_receive.contents

    @property
    def window_transmit(self) -> bytes | None:
        """ return windows_size_transmit if it not default """
        if self.windows_size_transmit.decode() != self.get_attr_element(3).default:
            return self.windows_size_transmit.contents

    @property
    def window_receive(self) -> bytes | None:
        """ return windows_size_receive if it not default """
        if self.windows_size_receive.decode() != self.get_attr_element(4).default:
            return self.windows_size_receive.contents

    def set_from_info(self, info: bytes):
        """ negotiation from client """
        if info[:2] == b'\x81\x80':
            info = info.removeprefix(b'\x81\x80')
            length, info = info[0], info[1:]
            if length == len(info):
                while len(info) != 0:
                    tag, value_length, info = info[:1], info[1], info[2:]
                    value, info = info[:value_length], info[value_length:]
                    match tag:
                        case b'\x05': self.set_attr(5, cdt.LongUnsigned(int.from_bytes(value, 'big')))
                                      # self.max_info_field_length_transmit.contents = (bytes(2)+value)[-2:]
                        case b'\x06': self.set_attr(6, cdt.LongUnsigned(int.from_bytes(value, 'big')))
                        case b'\x07': self.set_attr(3, cdt.Unsigned(int.from_bytes(value, 'big')))
                        case b'\x08': self.set_attr(4, cdt.Unsigned(int.from_bytes(value, 'big')))
                        case _:       raise ValueError(F'Invalid UA response. Got {tag.hex(" ")} from supported 05, 06, 07, 08')
            else:
                raise ValueError(F'HDLS negotiation length wrong, must be {length}, got {len(info)}')
        elif len(info) == 0:
            deque(map(self.reset_attribute, (3, 4, 5, 6)))
        else:
            raise ValueError(F'HDLS negotiation header wrong, must be 81 80, got {info[:2].hex(" ")}')

    def get_device_address(self) -> int | None:
        """ return device address decoding if it used. Value is 0 not used """
        ret = self.device_address.decode()
        return ret if ret != 0 else None

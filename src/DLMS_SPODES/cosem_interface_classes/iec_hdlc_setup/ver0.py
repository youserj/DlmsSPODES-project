from COSEMpdu.data import Enum, Unsigned, LongUnsigned
from ..cosem_interface_class import ICAElement, ICAuto
from ...types.type_alias import Attr


class CommSpeed(Enum):
    _300_BAUD = 0
    _600_BAUD = 1
    _1200_BAUD = 2
    _2400_BAUD = 3
    _4800_BAUD = 4
    _9600_BAUD = 5
    _19200_BAUD = 6
    _38400_BAUD = 7
    _57600_BAUD = 8
    _115200_BAUD = 9


class IECHDLCSetup(ICAuto):
    """5.7.2 IEC HDLC setup"""
    VERSION = 0
    CLASS_ID = 23
    A_ELEMENTS = (
        ICAElement(2, "comm_speed", CommSpeed, 0, 9, 5),
        ICAElement(3, "windows_size_transmit", Unsigned, 1, 7, 1),
        ICAElement(4, "windows_size_receive", Unsigned, 1, 7, 1),
        ICAElement(5, "max_info_field_length_transmit", Unsigned, 32, 128, 128),
        ICAElement(6, "max_info_field_length_receive", Unsigned, 32, 128, 128),
        ICAElement(7, "inter_octet_time_out", LongUnsigned, 20, 1000, 25),
        ICAElement(8, "inactivity_time_out", LongUnsigned, 0, default=120),
        ICAElement(9, "device_address", LongUnsigned, 0x0001, 0x3ffd, default=0x10)    # TODO: not according by BlueBook: need default, minimum is other
    )
    M_ELEMENTS = ()
    comm_speed: Attr
    windows_size_transmit: Attr
    windows_size_receive: Attr
    max_info_field_length_transmit: Attr
    max_info_field_length_receive: Attr
    inter_octet_time_out: Attr
    inactivity_time_out: Attr
    device_address: Attr


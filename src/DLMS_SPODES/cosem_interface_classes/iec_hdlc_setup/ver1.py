from typing import Optional
from ...types import cdt
from ...types.implementations.enums import CommSpeed
from ..cosem_interface_class import ICAElement, ICAuto
from ..Overview import class_id


class IECHDLCSetup(ICAuto):
    """4.7.2 IEC HDLC setup"""
    CLASS_ID = class_id.IEC_HDLC_SETUP
    VERSION = 1
    A_ELEMENTS = (ICAElement(2, "comm_speed", CommSpeed, 0, 9, 5),
                  ICAElement(3, "windows_size_transmit", cdt.Unsigned, 1, 7, 1),
                  ICAElement(4, "windows_size_receive", cdt.Unsigned, 1, 7, 1),
                  ICAElement(5, "max_info_field_length_transmit", cdt.LongUnsigned, 128, 32, 2030),
                  ICAElement(6, "max_info_field_length_receive", cdt.LongUnsigned, 128, 32, 2030),
                  ICAElement(7, "inter_octet_time_out", cdt.LongUnsigned, 20, 6000, 25),
                  ICAElement(8, "inactivity_time_out", cdt.LongUnsigned, 0, default=120),
                  ICAElement(9, "device_address", cdt.LongUnsigned, 0x0001, 0x3ffd, default=0x10))  # TODO: not according by BlueBook: need default, minimum is other
    comm_speed: Optional[CommSpeed]
    windows_size_transmit: Optional[cdt.Unsigned]
    windows_size_receive: Optional[cdt.Unsigned]
    max_info_field_length_transmit: Optional[cdt.LongUnsigned]
    max_info_field_length_receive: Optional[cdt.LongUnsigned]
    inter_octet_time_out: Optional[cdt.LongUnsigned]
    inactivity_time_out: Optional[cdt.LongUnsigned]
    device_address: Optional[cdt.LongUnsigned]

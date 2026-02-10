from ...types import cdt
from ..cosem_interface_class import ICAElement, Classifier, ICAuto
from ...types.implementations.enums import CommSpeed
from ...types.type_alias import Attr
from ..Overview import class_id


class IECHDLCSetup(ICAuto):
    """5.7.2 IEC HDLC setup"""
    VERSION = 0
    CLASS_ID = class_id.IEC_HDLC_SETUP
    A_ELEMENTS = (
        ICAElement(2, "comm_speed", CommSpeed, 0, 9, 5),
        ICAElement(3, "windows_size_transmit", cdt.Unsigned, 1, 7, 1),
        ICAElement(4, "windows_size_receive", cdt.Unsigned, 1, 7, 1),
        ICAElement(5, "max_info_field_length_transmit", cdt.Unsigned, 32, 128, 128),
        ICAElement(6, "max_info_field_length_receive", cdt.Unsigned, 32, 128, 128),
        ICAElement(7, "inter_octet_time_out", cdt.LongUnsigned, 20, 1000, 25),
        ICAElement(8, "inactivity_time_out", cdt.LongUnsigned, 0, default=120),
        ICAElement(9, "device_address", cdt.LongUnsigned, 0x0001, 0x3ffd, default=0x10)    # TODO: not according by BlueBook: need default, minimum is other
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


from typing import Optional
from ...types import cdt
from ..cosem_interface_class import ICAElement
from ..Overview import class_id
from . import ver0


class IECHDLCSetup(ver0.IECHDLCSetup):
    """4.7.2 IEC HDLC setup"""
    CLASS_ID = class_id.IEC_HDLC_SETUP
    VERSION = 1
    A_ELEMENTS = (
        ver0.IECHDLCSetup.getAElement(2).unwrap(),
        ver0.IECHDLCSetup.getAElement(3).unwrap(),
        ver0.IECHDLCSetup.getAElement(4).unwrap(),
        ICAElement(5, "max_info_field_length_transmit", cdt.LongUnsigned, 32, 2030, 128),
        ICAElement(6, "max_info_field_length_receive", cdt.LongUnsigned, 32, 2030, 128),
        ver0.IECHDLCSetup.getAElement(7).unwrap(),
        ver0.IECHDLCSetup.getAElement(8).unwrap(),
        ver0.IECHDLCSetup.getAElement(9).unwrap(),
    )

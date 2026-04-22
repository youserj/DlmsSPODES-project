from COSEMpdu.data import LongUnsigned
from ..cosem_interface_class import ICAElement, update_collection
from . import ver0


class IECHDLCSetup(ver0.IECHDLCSetup):
    """4.7.2 IEC HDLC setup"""
    VERSION = 1
    A_ELEMENTS = update_collection(
        ver0.IECHDLCSetup.A_ELEMENTS,
        ICAElement(5, "max_info_field_length_transmit", LongUnsigned, 32, 2030, 128),
        ICAElement(6, "max_info_field_length_receive", LongUnsigned, 32, 2030, 128))

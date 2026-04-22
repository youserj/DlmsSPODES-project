from COSEMpdu.data import (
    Data as Data_, Enum, Array, Integer, NullData, Structure, Boolean, Unsigned, LongUnsigned, OctetString, EnumMixin
)
from ..types.implementations import double_long_usingneds, arrays
from typing import Optional
from ..types import cdt, cst
from .cosem_interface_class import ICAElement, ICAuto


class IPOptionsElement(cdt.Structure):
    IP_Option_Type: cdt.Unsigned
    IP_Option_Length: cdt.Unsigned
    IP_Option_Data: cdt.OctetString


class IPOptions(cdt.Array):
    TYPE = IPOptionsElement


MulticastIPAddress = Array[double_long_usingneds.IPAddress]


class IPv4Setup(ICAuto):
    """4.9.2 IPv4 setup"""
    CLASS_ID = 42
    VERSION = 0
    # TODO: more 3 methods
    A_ELEMENTS = (ICAElement(2, "DL_reference", cst.LogicalName),
                  ICAElement(3, "IP_address", double_long_usingneds.IPAddress),
                  ICAElement(4, "multicast_IP_address", MulticastIPAddress),
                  ICAElement(5, "IP_options", IPOptions),
                  ICAElement(6, "subnet_mask", double_long_usingneds.IPAddress),
                  ICAElement(7, "gateway_IP_address", double_long_usingneds.IPAddress),
                  ICAElement(8, "use_DHCP_flag", cdt.Boolean),
                  ICAElement(9, "primary_DNS_address", double_long_usingneds.IPAddress),
                  ICAElement(10, "secondary_DNS_address", double_long_usingneds.IPAddress),
                  # TODO: more 3 methods
                  )
    DL_reference: Optional[cdt.OctetString]
    IP_address: Optional[double_long_usingneds.IPAddress]
    multicast_IP_address: Optional[MulticastIPAddress]
    IP_options: Optional[IPOptions]
    subnet_mask: Optional[double_long_usingneds.IPAddress]
    gateway_IP_address: Optional[double_long_usingneds.IPAddress]
    use_DHCP_flag: Optional[cdt.Boolean]
    primary_DNS_address: Optional[double_long_usingneds.IPAddress]
    secondary_DNS_address: Optional[double_long_usingneds.IPAddress]

from COSEMpdu.data import Array, Structure, Boolean, Unsigned, OctetString
from ..types.implementations import double_long_usingneds
from ..types import cst
from .cosem_interface_class import ICAElement, ICAuto, ICMElement
from ..types.type_alias import Attr


class IPOptionsElement(Structure):
    """IP_options_element"""
    IP_Option_Type: Unsigned
    IP_Option_Length: Unsigned
    IP_Option_Data: OctetString


IPOptions = Array[IPOptionsElement]
"""IP_options"""


MulticastIPAddress = Array[double_long_usingneds.IPAddress]
"""multicast_IP_address"""


class IPv4Setup(ICAuto):
    """4.9.2 IPv4 setup"""
    CLASS_ID = 42
    VERSION = 0
    # TODO: more 3 methods
    A_ELEMENTS = (
        ICAElement(2, "DL_reference", cst.LogicalName),
        ICAElement(3, "IP_address", double_long_usingneds.IPAddress),
        ICAElement(4, "multicast_IP_address", MulticastIPAddress),
        ICAElement(5, "IP_options", IPOptions),
        ICAElement(6, "subnet_mask", double_long_usingneds.IPAddress),
        ICAElement(7, "gateway_IP_address", double_long_usingneds.IPAddress),
        ICAElement(8, "use_DHCP_flag", Boolean),
        ICAElement(9, "primary_DNS_address", double_long_usingneds.IPAddress),
        ICAElement(10, "secondary_DNS_address", double_long_usingneds.IPAddress))
    M_ELEMENTS = (
        ICMElement(1, "add_mc_IP_address", double_long_usingneds.IPAddress),
        ICMElement(2, "delete_mc_IP_address", double_long_usingneds.IPAddress),
        ICMElement(2, "get_nbof_mc_IP_addresses", Unsigned))
    DL_reference: Attr
    IP_address: Attr
    multicast_IP_address: Attr
    IP_options: Attr
    subnet_mask: Attr
    gateway_IP_address: Attr
    use_DHCP_flag: Attr
    primary_DNS_address: Attr
    secondary_DNS_address: Attr

from .__class_init__ import *
from ..types.implementations import double_long_usingneds, arrays


class IPOptionsElement(cdt.Structure):
    IP_Option_Type: cdt.Unsigned
    IP_Option_Length: cdt.Unsigned
    IP_Option_Data: cdt.OctetString


class IPOptions(cdt.Array):
    TYPE = IPOptionsElement


class IPv4Setup(ic.COSEMInterfaceClasses):
    """ This IC allows modelling the setup of teh IPv4 layer, handling all information related to the IP Address settings associated to a given device adn to a lower layer
    connection on which these settings are used. There shall be and instance of this IC in a device for each different network interface implemented. For example, if a device has
    two interfaces (using the TCP-UDP/ITv4 profile on both of them), there shall be two instances of the IPc4 setup IC in that device: one for each of these interfaces."""
    CLASS_ID = classID.IPV4_SETUP
    VERSION = Version.V0
    # TODO: more 7 attr and 3 methods
    A_ELEMENTS = (ic.ICAElement("DL_reference", cdt.OctetString),
                  ic.ICAElement("IP_address", double_long_usingneds.IPAddress),
                  ic.ICAElement("multicast_IP_address", arrays.MulticastIPAddress),
                  ic.ICAElement("IP_options", IPOptions),
                  ic.ICAElement("subnet_mask", double_long_usingneds.IPAddress),
                  ic.ICAElement("gateway_IP_address", double_long_usingneds.IPAddress),
                  ic.ICAElement("use_DHCP_flag", cdt.Boolean),
                  ic.ICAElement("primary_DNS_address", double_long_usingneds.IPAddress),
                  ic.ICAElement("secondary_DNS_address", double_long_usingneds.IPAddress),
                  # TODO: more 3 methods
                  )

    def characteristics_init(self):
        self.set_attr(3, 3232235521)

    @property
    def DL_reference(self) -> cdt.OctetString:
        return self.get_attr(2)

    @property
    def IP_address(self) -> double_long_usingneds.IPAddress:
        return self.get_attr(3)

    @property
    def multicast_IP_address(self) -> arrays.MulticastIPAddress:
        return self.get_attr(4)

    @property
    def IP_options(self) -> IPOptions:
        return self.get_attr(5)

    @property
    def subnet_mask(self) -> double_long_usingneds.IPAddress:
        return self.get_attr(6)

    @property
    def gateway_IP_address(self) -> double_long_usingneds.IPAddress:
        return self.get_attr(7)

    @property
    def use_DHCP_flag(self) -> cdt.Boolean:
        return self.get_attr(8)

    @property
    def primary_DNS_address(self) -> double_long_usingneds.IPAddress:
        return self.get_attr(9)

    @property
    def secondary_DNS_address(self) -> double_long_usingneds.IPAddress:
        return self.get_attr(10)

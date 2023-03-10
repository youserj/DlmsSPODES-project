from .__class_init__ import *


class IPAddress(cdt.DoubleLongUnsigned):

    def from_str(self, value: str) -> bytes:
        """ create ip: integer from string type ddd.ddd.ddd.ddd, ex.: 127.0.0.1 """
        raw_value = bytes()
        for separator in '... ':
            try:
                element, value = value.split(separator, 1)
            except ValueError:
                element, value = value, ''
            raw_value += self.__get_attr_element(element)
        return raw_value

    @staticmethod
    def __get_attr_element(value: str) -> bytes:
        if isinstance(value, str):
            if value == '':
                return b'\x00'
            try:
                return int(value).to_bytes(1, 'big')
            except OverflowError:
                raise ValueError(F'Int too big to convert {value}')
        else:
            raise TypeError(F'Unsupported type validation from string, got {value.__class__}')

    def __str__(self):
        return F'{self.contents[0]}.{self.contents[1]}.{self.contents[2]}.{self.contents[3]}'


class IPv4Setup(ic.COSEMInterfaceClasses):
    """ This IC allows modelling the setup of teh IPv4 layer, handling all information related to the IP Address settings associated to a given device adn to a lower layer
    connection on which these settings are used. There shall be and instance of this IC in a device for each different network interface implemented. For example, if a device has
    two interfaces (using the TCP-UDP/ITv4 profile on both of them), there shall be two instances of the IPc4 setup IC in that device: one for each of these interfaces."""
    NAME = cn.IPV4_SETUP
    CLASS_ID = ClassID.IPV4_SETUP
    VERSION = Version.V0
    # TODO: more 7 attr and 3 methods
    A_ELEMENTS = (ic.ICAElement(an.DL_REFERENCE, cdt.OctetString),
                  ic.ICAElement(an.IP_ADDRESS, IPAddress),
                  # TODO: more 7 attr and 3 methods
                  )

    def characteristics_init(self):
        self.set_attr(3, 3232235521)

    @property
    def DL_reference(self) -> cdt.OctetString:
        return self.get_attr(2)

    @property
    def IP_address(self) -> IPAddress:
        return self.get_attr(3)

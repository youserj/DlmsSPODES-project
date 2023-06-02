from ...types import common_data_types as cdt


class CommSpeed(cdt.Enum, elements=tuple(range(10))):
    """ The communication speed supported by the corresponding port. This communication speed can be overridden if the HDLC mode of a devive is entered through a special mode
    of another protocol. """

    def decode(self) -> int:
        """ override enum key to enum value"""
        match self.contents:
            case b'\x00':  return 300
            case b'\x01':  return 600
            case b'\x02':  return 1200
            case b'\x03':  return 2400
            case b'\x04':  return 4800
            case b'\x05':  return 9600
            case b'\x06':  return 19200
            case b'\x07':  return 38400
            case b'\x08':  return 57600
            case b'\x09':  return 115200
            case _ as err: raise ValueError(F'Wrong CommSpeed: {err}, expected {CommSpeed.ELEMENTS.keys()}')

    def from_int(self, value: int) -> bytes:
        """ additional cases with Speed Values"""
        match value:
            case 300:    return b'\x00'
            case 600:    return b'\x01'
            case 1200:   return b'\x02'
            case 2400:   return b'\x03'
            case 4800:   return b'\x04'
            case 9600:   return b'\x05'
            case 19200:  return b'\x06'
            case 38400:  return b'\x07'
            case 57600:  return b'\x08'
            case 115200: return b'\x09'
            case other:  return super(CommSpeed, self).from_int(other)


class RestrictionType(cdt.Enum, elements=(0, 1, 2)):
    """"""


class KeyInfoType(cdt.Enum, elements=(0, 1, 2)):
    """"""


class ProtectionType(cdt.Enum, elements=(0, 1, 2, 3)):
    """"""

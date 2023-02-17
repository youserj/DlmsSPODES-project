from ...types import common_data_types as cdt
from ...settings import get_current_language, Language

match get_current_language():
    case Language.ENGLISH: from ...Values.EN import enum_names as en
    case Language.RUSSIAN: from ...Values.RU import enum_names as en


class CommSpeed(cdt.Enum):
    """ The communication speed supported by the corresponding port. This communication speed can be overridden if the HDLC mode of a devive is entered through a special mode
    of another protocol. """
    ELEMENTS = {b'\x00': en.BAUD_300,
                b'\x01': en.BAUD_600,
                b'\x02': en.BAUD_1200,
                b'\x03': en.BAUD_2400,
                b'\x04': en.BAUD_4800,
                b'\x05': en.BAUD_9600,
                b'\x06': en.BAUD_19200,
                b'\x07': en.BAUD_38400,
                b'\x08': en.BAUD_57600,
                b'\x09': en.BAUD_115200}

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


class RestrictionType(cdt.Enum):
    ELEMENTS = {b'\x00': en.NONE,
                b'\x01': en.RESTRICTION_BY_DATE,
                b'\x02': en.RESTRICTION_BY_ENTRY}


class KeyInfoType(cdt.Enum):
    ELEMENTS = {b'\x00': en.IDENTIFIED_KEY,
                b'\x01': en.WRAPPED_KEY,
                b'\x02': en.AGREED_KEY}


class ProtectionType(cdt.Enum):
    ELEMENTS = {b'\x00': en.AUTHENTICATION,
                b'\x01': en.ENCRYPTED_REQUEST,
                b'\x02': en.WRAPPED_KEY,
                b'\x03': en.AGREED_KEY}

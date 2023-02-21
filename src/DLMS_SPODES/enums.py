from enum import Enum, IntEnum, auto
from typing import Self
from .settings import get_current_language, Language

match get_current_language():
    case Language.ENGLISH: from .Values.EN import enum_names as en
    case Language.RUSSIAN: from .Values.RU import enum_names as en


class ITEEnum(Enum):
    def is_ok(self) -> bool:
        match self:
            case self.OK: return True
            case _:       return False

    @property
    def value(self):
        return super(ITEEnum, self).value[1]

    @property
    def importance(self):
        return super(ITEEnum, self).value[0]


class Transmit(ITEEnum):
    """ error enumerator for transmit . Priority for status has biggest value """
    OK = 0, 'Успех'
    NO_PORT = 2, 'Отсутствует порт'
    TIMEOUT = 3, 'Таймаут'
    NO_ACCESS = 4, 'Нет доступа'
    NO_TRANSPORT = 5, 'Отсутствует транспортный интерфейс'
    WRITE_ERROR = 6, 'Ошибка записи'
    READ_ERROR = 7, 'Ошибка чтения'
    EXECUTE_ERROR = 8, 'Ошибка исполнения'
    ABORT = 9, 'Прерывание'
    """ Manual interrupt """
    UNKNOWN = 10, 'Неизвестная ошибка'


class Application(ITEEnum):
    """ error enumerator for application . Priority for status has biggest value """
    OK = 0, 'Успех'
    ID_ERROR = 2, 'Ошибка серийного номера'
    """ serial number identification error """
    VERSION_ERROR = 2, 'Ошибка версии'
    """ Any errors associated with version """
    MISSING_OBJ = 2, 'Отсутствует объект'
    """ requested object was missing in collection """
    EMPTY_OBJ = 2, 'Пустые данные'
    """ empty attribute in object """
    NO_CONFIG = 2, 'Конфигурация не найдена'
    VALUE_ERROR = 2, 'Ошибка значения'
    TYPE_ERROR = 2, 'Ошибка типа прибора'
    VERIFY_ERROR = 3, 'Ошибка верификации'
    ACTIVATION_ERROR = 3, 'Ошибка активации'
    RESULT_ERROR = 3, "Ошибка данных"  # COSEMpdu_GB83.asn


class TagsName(Enum):
    ROOT = 'Configure'
    LANGUAGE = 'Language'
    GROUP = 'group'
    DEVICE = 'device'
    NAME = 'name'
    ID = 'id'
    SERIAL_NUMBER = 'serial_number'
    SERIAL_NUMBER_AMOUNT = 'serial_number_amount'
    MECHANISM_ID = 'mechanism_id'
    INTERFACE = 'Interface'
    CHILD_ID = 'child_id'
    DEVICE_ROOT = 'Objects'
    TEMPLATE_ROOT = 'template.objects'


class DBOperation(IntEnum):
    WRITE_ATTR = 1
    WRITE_METH = auto()
    CREATE_DEV_TYPE = auto()


class Interface(IntEnum):
    NO_DEFINED = 0
    OPTO = 1
    RS485 = 2
    PLC = 3
    GSM = 4
    NBIO = 5
    ETHERNET = 6
    RF = 7
    LORA = 8
    WIFI = 9
    BLUETOOTH = 10
    ZIGBEE = 11
    RESERVED_12 = 12
    RESERVED_13 = 13
    RESERVED_14 = 14
    RESERVED_15 = 15
    RESERVED_16 = 16
    RESERVED_17 = 17
    RESERVED_18 = 18
    RESERVED_19 = 19
    RESERVED_20 = 20
    RESERVED_21 = 21
    RESERVED_22 = 22
    RESERVED_23 = 23
    RESERVED_24 = 24
    RESERVED_25 = 25
    RESERVED_26 = 26
    RESERVED_27 = 27
    RESERVED_28 = 28
    RESERVED_29 = 29
    MANUFACTURE_30 = 30
    MANUFACTURE_31 = 31

    @staticmethod
    def from_str(value: str) -> Self:
        return next(filter(lambda i: i.name == value, Interface))


class ChannelNumber(IntEnum):
    RESERVED = 0
    OPTO_P1 = 1
    P2 = 2
    P3 = 3
    P4 = 4
    OTHER = 5
    INNER = 6
    SERVER_KEY = 7

    @staticmethod
    def from_str(value: str) -> Self:
        return next(filter(lambda i: i.name == value, ChannelNumber))


class ConnectionType(IntEnum):
    NO_STATION = 0,
    CLIENT_MANAGEMENT_PROCESS = 1
    PUBLIC_CLIENT = 0x10
    METER_READER = 0x20
    UTILITY_SETTING = 0x30
    PUSH = 0x40
    FIRMWARE_UPDATE = 0x50
    IHD = 0x60

    def __str__(self):
        match self:
            case self.NO_STATION:                return en.NO_STATION
            case self.CLIENT_MANAGEMENT_PROCESS: return en.CLIENT_MANAGEMENT_PROCESS
            case self.PUBLIC_CLIENT:             return en.PUBLIC_CLIENT
            case self.METER_READER:              return en.METER_READER
            case self.UTILITY_SETTING:           return en.UTILITY_SETTING
            case self.PUSH:                      return en.PUSH
            case self.FIRMWARE_UPDATE:           return en.FIRMWARE_UPDATE
            case self.IHD:                       return en.IHD
            case _:                              return str(self)

    @classmethod
    def from_str(cls, value: str) -> Self:
        match value:
            case en.NO_STATION:                return cls.NO_STATION
            case en.CLIENT_MANAGEMENT_PROCESS: return cls.CLIENT_MANAGEMENT_PROCESS
            case en.PUBLIC_CLIENT:             return cls.PUBLIC_CLIENT
            case en.METER_READER:              return cls.METER_READER
            case en.UTILITY_SETTING:           return cls.UTILITY_SETTING
            case en.PUSH:                      return cls.PUSH
            case en.FIRMWARE_UPDATE:           return cls.FIRMWARE_UPDATE
            case en.IHD:                       return cls.IHD
            case _:                            return cls(int(value))


class MechanismId(IntEnum):
    NONE = 0
    LOW = 1
    HIGH = 2
    HIGH_MD5 = 3
    HIGH_SHA1 = 4
    HIGH_GMAC = 5
    HIGH_SHA256 = 6
    HIGH_ECDSA = 7

    @classmethod
    def from_str(cls, value: str) -> Self:
        return next(filter(lambda i: i.name == value, cls))


class ContextId(IntEnum):
    LN_NO_CIPHERING = 1
    SN_NO_CIPHERING = 2
    LN_CIPHERING = 3
    SN_CIPHERING = 4

    @classmethod
    def from_str(cls, value: str) -> Self:
        return next(filter(lambda i: i.name == value, cls))


if __name__ == '__main__':
    a = Transmit.OK
    print(a.name, a.value, a.importance)
    print(a.is_ok())
    match a:
        case Transmit.OK: print(a.value)
        case Application.ID_ERROR: print('id')



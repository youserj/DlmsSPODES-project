from enum import Enum, IntEnum, auto


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


if __name__ == '__main__':
    a = Transmit.OK
    print(a.name, a.value, a.importance)
    print(a.is_ok())
    match a:
        case Transmit.OK: print(a.value)
        case Application.ID_ERROR: print('id')

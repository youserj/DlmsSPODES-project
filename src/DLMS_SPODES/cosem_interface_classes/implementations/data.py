import re
import logging
from ...types import cdt, cst
from ..data import Data, ic, choices
from ... import enums as enu
from ...types import implementations as impl
from ...config_parser import get_message


class DataStatic(Data):
    A_ELEMENTS = Data.getAElement(2).unwrap().get_change(classifier=ic.Classifier.STATIC),


class DataDynamic(Data):
    A_ELEMENTS = Data.getAElement(2).unwrap().get_change(classifier=ic.Classifier.DYNAMIC),


class DataNotSpecific(Data):
    A_ELEMENTS = Data.getAElement(2).unwrap().get_change(classifier=ic.Classifier.NOT_SPECIFIC),


class LDN(DataStatic):
    """for ldn"""
    A_ELEMENTS = Data.getAElement(2).unwrap().get_change(data_type=impl.octet_string.LDN),

    @property
    def get_manufacturer(self) -> bytes:
        return self.value.contents[:3]


class ActiveFirmwareId(Data):
    """for keep version in collection"""
    def characteristics_init(self):
        """"""


class Unsigned(DataDynamic):
    """ with value type: Unsigned """
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=cdt.Unsigned),


class OctetStringDateTime(DataDynamic):
    """ with value type: Unsigned """
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=cst.OctetStringDateTime),


class OpeningBodyUnsigned(cdt.ReportMixin, cdt.Unsigned):  # todo: make as cdt.FlagEnum
    def get_report(self) -> cdt.Report:
        """ СПОДЭСv.3 Е.12.5"""
        match int(self) & 0b1:
            case 0: return cdt.Report(
                msg=get_message("$normal$"),
                log=cdt.INFO_LOG)
            case 1: return cdt.Report(
                msg=get_message("$case_is_opened$"),
                log=cdt.Log(logging.WARN))


class OpeningBody(DataDynamic):
    """ RU. 0.0.96.51.0.255. СТО_34.01-5.1-006-2019v3. E 12.1 """
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=OpeningBodyUnsigned),


class OpeningCoverUnsigned(cdt.ReportMixin, cdt.Unsigned):  # todo: make as cdt.FlagEnum
    def get_report(self) -> cdt.Report:
        """ СПОДЭСv.3 Е.12.5"""
        match int(self) & 0b1:
            case 0: return cdt.Report(
                msg=get_message("$normal$"),
                log=cdt.INFO_LOG)
            case 1: return cdt.Report(
                msg=get_message("$cover_is_opened$"),
                log=cdt.Log(logging.WARN))


class OpeningCover(DataDynamic):
    """ RU. 0.0.96.51.1.255. СТО_34.01-5.1-006-2019v3. E 12.2 """
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=OpeningCoverUnsigned),


class ExposureToFieldUnsigned(cdt.ReportMixin, cdt.Unsigned):  # todo: make as cdt.FlagEnum
    def get_report(self) -> cdt.Report:
        if (value := (int(self) & 0b101)) == 0:
            return cdt.Report(get_message("$normal$"), log=cdt.INFO_LOG)
        else:
            ret = ""
            if value & 0b001:
                ret += get_message("$fixed_field$")
            if value & 0b100:
                ret += get_message("$exist_field$")
            return cdt.Report(ret, log=cdt.Log(logging.WARN))


class ExposureToMagnet(DataDynamic):
    """ RU. 0.0.96.51.3.255. СТО_34.01-5.1-006-2019v3. E 12.3 """
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=ExposureToFieldUnsigned),


class ExposureToHSField(DataDynamic):
    """ RU. 0.0.96.51.4.255. СТО_34.01-5.1-006-2019v3. E 12.3 """
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=ExposureToFieldUnsigned),


class SealUnsigned(cdt.ReportMixin, cdt.Unsigned):  # todo: make as cdt.FlagEnum??
    def get_report(self) -> cdt.Report:
        def get_name(value: int):
            """ СПОДЭСv.3 Е.12.5"""
            match value & 0b11:
                case 0: return "$undefined$"
                case 1: return "$contentions$"
                case 2: return "$breaked_open$"
                case 3: return "$subsequent_autopsy$"
        return cdt.Report(
            msg=get_message(F"$for_cover$ - {get_name(int(self) & 0b11)}, $for_terminals_cover$ - {get_name((int(self) >> 2) & 0b11)}"),
            log=cdt.Log(logging.INFO if int(self) == 0b101 else logging.WARN))


class SealStatus(DataDynamic):
    """ RU. 0.0.96.51.5.255. СТО_34.01-5.1-006-2019v3. E 12.5 """
    A_ELEMENTS = DataDynamic.A_ELEMENTS[0].get_change(data_type=SealUnsigned),


class TerminalsCoverOpeningState(DataDynamic):
    """ RU. 0.0.96.51.1.255. СТО_34.01-5.1-006-2019v3. E 12.2 """
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=cdt.Unsigned),


class BitMapData(cdt.Structure):
    start_time: cst.OctetStringDateTime
    stop_time: cst.OctetStringDateTime
    bitmap_data: cdt.OctetString


class ITEBitMap(DataStatic):
    """ITE 0.128.96.13.1.255. Use for send struct lcd screen bitmap(BMP) with start/stop period to server"""
    A_ELEMENTS = Data.get_attr_element(2).get_change(data_type=BitMapData),


class ChannelNumberValue(cdt.ReportMixin, cdt.Unsigned):
    @property
    def channel(self) -> enu.ChannelNumber:
        return enu.ChannelNumber(int(self) & 0b0000_0111)

    @channel.setter
    def channel(self, value: enu.ChannelNumber):
        self.set((int(self) & 0b1111_1000) | value)

    @property
    def interface(self) -> enu.Interface:
        return enu.Interface((int(self) & 0b1111_1000) >> 3)

    @interface.setter
    def interface(self, value: enu.Interface):
        self.set((int(self) & 0b0001_1111) | (value << 3))

    def get_report(self) -> cdt.Report:
        return cdt.Report(F"({int(self)}) Номер канала связи: {self.channel.name}, Тип интерфейса: {self.interface.name}")


class CommunicationPortParameter(Data):
    """ RU. 0.0.96.12.4.255. СТО_34.01-5.1-006-2019v3. 13.10. Определение номера порта по которому установлено соединение"""
    A_ELEMENTS = ic.ICAElement("value", ChannelNumberValue, default=enu.ChannelNumber.OPTO_P1 + (enu.Interface.OPTO << 3), classifier=ic.Classifier.DYNAMIC),

    @property
    def value(self) -> ChannelNumberValue:
        """override returned type"""
        return self.get_attr(2)


class AnyDateTime(DataDynamic):
    """for a-anotation DLMS UA 1000-1 Ed. 14 Table 60"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=choices.any_date_time),


class SPODES3VoltageEventValues(cdt.IntegerEnum, cdt.LongUnsigned):
    pass


class SPODES3VoltageEvent(DataDynamic):
    """СТО_34.01-5.1-006-2019v3 Д.2 События, связанные с напряжением"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=SPODES3VoltageEventValues),


class SPODES3CurrentEventValues(cdt.IntegerEnum, cdt.LongUnsigned):
    pass

class SPODES3CurrentEvent(DataDynamic):
    """СТО_34.01-5.1-006-2019v3 Д.3 События, связанные с током"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=SPODES3CurrentEventValues),


class SPODES3CommutationEventValues(cdt.IntegerEnum, cdt.LongUnsigned):
    pass

class SPODES3CommutationEvent(DataDynamic):
    """СТО_34.01-5.1-006-2019v3 Д.4 События, связанные с вкл./выкл. ПУ, коммутации реле нагрузки"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=SPODES3CommutationEventValues),


class SPODES3ProgrammingEventValues(cdt.IntegerEnum, cdt.LongUnsigned):
    pass


class SPODES3ProgrammingEvent(DataDynamic):
    """СТО_34.01-5.1-006-2019v3 Д.5 События программирования параметров ПУ"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=SPODES3ProgrammingEventValues),


class SPODES3ExternalEventValues(cdt.IntegerEnum, cdt.LongUnsigned):
    pass


class SPODES3ExternalEvent(DataDynamic):
    """СТО_34.01-5.1-006-2019v3 Д.6 События внешних воздействий"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=SPODES3ExternalEventValues),


class SPODES3CommunicationEventValues(cdt.IntegerEnum, cdt.LongUnsigned):
    pass

class SPODES3CommunicationEvent(DataDynamic):
    """СТО_34.01-5.1-006-2019v3 Д.7 Коммуникационные события"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=SPODES3CommunicationEventValues),


class SPODES3AccessEventValues(cdt.IntegerEnum, cdt.LongUnsigned):
    pass

class SPODES3AccessEvent(DataDynamic):
    """СТО_34.01-5.1-006-2019v3 Д.8 События контроля доступа"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=SPODES3AccessEventValues),


class SPODES3SelfDiagnosticEventValues(cdt.IntegerEnum, cdt.LongUnsigned):
    pass

class SPODES3SelfDiagnosticEvent(DataDynamic):
    """СТО_34.01-5.1-006-2019v3 Д.9 Коды событий для журнала самодиагностики"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=SPODES3SelfDiagnosticEventValues),


class SPODES3ReactivePowerEventValues(cdt.IntegerEnum, cdt.LongUnsigned):
    pass

class SPODES3ReactivePowerEvent(DataDynamic):
    """СТО_34.01-5.1-006-2019v3 Д.10 События по превышению реактивной мощности"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=SPODES3ReactivePowerEventValues),


class SPODES3PowerQuality2EventValues(cdt.IntegerFlag, cdt.LongUnsigned):
    pass


class SPODES3PowerQuality2Event(DataNotSpecific):
    """СТО_34.01-5.1-006-2019v3 E.1 Статус качества сети (журнал качества сети)"""
    A_ELEMENTS = DataNotSpecific.get_attr_element(2).get_change(data_type=SPODES3PowerQuality2EventValues),


class LoadLockerValue(cdt.IntegerEnum, cdt.Unsigned):
    def __init_subclass__(cls, **kwargs):
        """not need"""

    def get_report(self) -> cdt.Report:
        match val := int(self):
            case 0:
                return cdt.Report(
                    msg=get_message(F"({val}) $lock$ $turn_off$"),
                    log=cdt.INFO_LOG)
            case 1:
                return cdt.Report(
                    msg=get_message(F"({val}) $lock$ $turn_on$"),
                    log=cdt.Log(logging.WARN))
            case _:
                return cdt.Report(
                    msg=get_message(F"({val})"),
                    log=cdt.Log(logging.ERROR, "unknown state"))


class SPODES3LoadLocker(DataStatic):
    """СТО 34.01-5.1-006-2023 E7. Блокиратор реле нагрузки"""
    A_ELEMENTS = DataNotSpecific.get_attr_element(2).get_change(data_type=LoadLockerValue),


class SPODES3PowerQuality1EventValues(cdt.IntegerFlag, cdt.LongUnsigned):
    pass


class SPODES3Alarm1Values(cdt.IntegerFlag, cdt.DoubleLongUnsigned):
    ...


class SPODES3Alarm1(DataStatic):
    """СТО_34.01-5.1-006-2019v3 9.8 Поддержка инициативного выхода"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=SPODES3Alarm1Values),


class KPZAlarm1Values(SPODES3Alarm1Values):
    ...


class KPZAlarm1(DataStatic):
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZAlarm1Values),


class SPODES3ControlAlarm1Values(cdt.IntegerFlag, cdt.DoubleLongUnsigned):
    ...


class SPODES3ControlAlarm1(DataDynamic):
    """СТО 34.01-5.1-006-2023v4 Таблица 13.5 Распределение событий отключения реле нагрузки по битам"""
    A_ELEMENTS = DataNotSpecific.get_attr_element(2).get_change(data_type=SPODES3ControlAlarm1Values),


class SPODES3PowerQuality1Event(DataNotSpecific):
    """СТО_34.01-5.1-006-2019v3 E.1 Статус качества сети (журнал качества сети)"""
    A_ELEMENTS = DataNotSpecific.get_attr_element(2).get_change(data_type=SPODES3PowerQuality1EventValues),


# KPZ implements
class KPZExternalEventValues(cdt.IntegerEnum, cdt.LongUnsigned):
    NAMES = SPODES3ExternalEventValues.NAMES


class KPZSPODES3ExternalEvent(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Д.6 События внешних воздействий"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZExternalEventValues),


class KPZ1VoltageEventValues(cdt.IntegerEnum, cdt.DoubleLongUnsigned):
    NAMES = SPODES3VoltageEventValues.NAMES


class KPZ1SPODES3VoltageEvent(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Д.2 События, связанные с напряжением with bag in value type"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZ1VoltageEventValues),


class KPZ1CurrentEventValues(cdt.IntegerEnum, cdt.DoubleLongUnsigned):
    NAMES = SPODES3CurrentEventValues.NAMES


class KPZ1SPODES3CurrentEvent(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Д.3 События, связанные с током"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZ1CurrentEventValues),


class KPZ1CommutationEventValues(cdt.IntegerEnum, cdt.DoubleLongUnsigned):
    NAMES = SPODES3CommutationEventValues.NAMES


class KPZ1SPODES3CommutationEvent(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Д.4 События, связанные с вкл./выкл. ПУ, коммутации реле нагрузки"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZ1CommutationEventValues),


class KPZ1ProgrammingEventValues(cdt.IntegerEnum, cdt.DoubleLongUnsigned):
    NAMES = SPODES3ProgrammingEventValues.NAMES


class KPZ1SPODES3ProgrammingEvent(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Д.5 События программирования параметров ПУ"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZ1ProgrammingEventValues),


class KPZ1ExternalEventValues(cdt.IntegerEnum, cdt.DoubleLongUnsigned):
    NAMES = SPODES3ExternalEventValues.NAMES


class KPZ1SPODES3ExternalEvent(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Д.6 События внешних воздействий"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZ1ExternalEventValues),


class KPZ1CommunicationEventValues(cdt.IntegerEnum, cdt.DoubleLongUnsigned):
    NAMES = SPODES3CommunicationEventValues.NAMES


class KPZ1SPODES3CommunicationEvent(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Д.7 Коммуникационные события"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZ1CommunicationEventValues),


class KPZ1AccessEventValues(cdt.IntegerEnum, cdt.DoubleLongUnsigned):
    NAMES = SPODES3AccessEventValues.NAMES


class KPZ1SPODES3AccessEvent(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Д.8 События контроля доступа"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZ1AccessEventValues),


class KPZ1SelfDiagnosticEventValues(cdt.IntegerEnum, cdt.DoubleLongUnsigned):
    NAMES = SPODES3SelfDiagnosticEventValues.NAMES


class KPZ1SPODES3SelfDiagnosticEvent(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Д.9 Коды событий для журнала самодиагностики"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZ1SelfDiagnosticEventValues),


class KPZ1ReactivePowerEventValues(cdt.IntegerEnum, cdt.DoubleLongUnsigned):
    NAMES = SPODES3ReactivePowerEventValues.NAMES


class KPZ1SPODES3ReactivePowerEvent(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Д.10 События по превышению реактивной мощности"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZ1ReactivePowerEventValues),


class SPODES3MeasurementPeriodValue(cdt.Unsigned):
    def validate(self):
        super(SPODES3MeasurementPeriodValue, self).validate()
        values: tuple[int, ...] = (1, 2, 3, 5, 10, 15, 20, 30, 60)
        if int(self) not in values:
            raise ValueError(F"for {self} got value: {int(self)}, expected: {values}")


class SPODES3MeasurementPeriod(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Г.2 Программируемые параметры и функции. Пункт 14"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=SPODES3MeasurementPeriodValue),


class DLMSDeviceIDObject(DataStatic):
    """DLMS UA 1000-1 Ed. 14. 6.2.42 Device ID objects"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=choices.device_id_object),


class SPODES3SPODESVersionValue(cdt.ReportMixin, cdt.OctetString):
    __pattern = re.compile(b"\\d{1,2}\\.\\d{1,2}")

    def get_report(self) -> cdt.Report:
        """custom string represent"""
        try:
            self.validate()
            msg = self.contents.decode("ascii", errors="ignore")
            log = cdt.INFO_LOG
        except ValueError as e:
            msg = str(self)
            log = cdt.Log(logging.ERROR, msg=e)
        return cdt.Report(
            msg=msg,
            log=log
        )

    def validate(self):
        if self.__pattern.fullmatch(self.contents) is None:
            raise ValueError(F"не соответствует СТО 34.01-5.1. Приложение Г")


class SPODES3SPODESVersion(DLMSDeviceIDObject):
    """СТО_34.01-5.1-006-2019v3 Г.1 Примечание 2"""
    A_ELEMENTS = DLMSDeviceIDObject.get_attr_element(2).get_change(data_type=SPODES3SPODESVersionValue),


class SPODES3IDNotSpecific(DLMSDeviceIDObject):
    """СТО_34.01-5.1-006-2019v3 13.1. Чтение расширенных паспортных данных ПУ. Для специфических идентификаторов"""
    A_ELEMENTS = DLMSDeviceIDObject.get_attr_element(2).get_change(classifier=ic.Classifier.NOT_SPECIFIC),


class KPZGSMPingIPValue(cdt.Structure):
    """Содержит настройки для проведения Ping теста"""
    enable: cdt.Unsigned
    multicast_IP_address: impl.arrays.MulticastIPAddress


class KPZGSMPingIP(DataStatic):
    """Проприетарный объект"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZGSMPingIPValue),


class AFERegister(cdt.Structure):
    name: cdt.VisibleString
    value: choices.common_dt


class AFERegisters(cdt.Array):
    TYPE = AFERegister
    values: list[AFERegister]


class AFEOffsets(cdt.Structure):
    identifier: cdt.VisibleString
    register_list: AFERegisters


class KPZAFEOffsets(DataDynamic):
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=AFEOffsets),

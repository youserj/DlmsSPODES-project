from ..data import Data, ic, cdt, cst, choices, ut
from ... import enums as enu
from .. import events as ev
from ...types import implementations as impl
from ...version import AppVersion
from ...config_parser import get_message
import logging
from ... import exceptions as exc


class DataStatic(Data):
    A_ELEMENTS = Data.get_attr_element(2).get_change(classifier=ic.Classifier.STATIC),


class DataDynamic(Data):
    A_ELEMENTS = Data.get_attr_element(2).get_change(classifier=ic.Classifier.DYNAMIC),


class DataNotSpecific(Data):
    A_ELEMENTS = Data.get_attr_element(2).get_change(classifier=ic.Classifier.NOT_SPECIFIC),


class LDN(DataStatic):
    """for ldn"""
    A_ELEMENTS = Data.get_attr_element(2).get_change(data_type=impl.octet_string.LDN),

    def characteristics_init(self):
        self._cbs_attr_post_init.update(
            {2: lambda: self.collection.set_manufacturer(self.value.contents[:3])}
        )

    @property
    def manufacturer(self) -> bytes:
        return self.value.contents[:3]


class ActiveFirmwareId(Data):
    """for keep version in collection"""
    def characteristics_init(self):
        self._cbs_attr_post_init.update({2: self.__register_value_preset})

    def __register_value_preset(self):
        """need for start control"""
        self.value.register_cb_post_set(self.__handle_value)
        self.__handle_value()

    def __handle_value(self):
        """check new version for more than current collection_version"""
        version = AppVersion.from_str(self.value.contents.decode("utf-8"))
        if (collection_ver := self.collection.server_ver.get(self.logical_name.b)) is not None:
            if version > collection_ver:
                raise exc.NeedUpdate(F"got {version}, but used {collection_ver}. need update server configuration")
            else:
                """ok validation"""
        else:
            """set without check"""


class Unsigned(DataDynamic):
    """ with value type: Unsigned """
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=cdt.Unsigned),


class OctetStringDateTime(DataDynamic):
    """ with value type: Unsigned """
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=cst.OctetStringDateTime),


class OpeningBodyUnsigned(cdt.ReportMixin, cdt.Unsigned):
    def get_report(self) -> cdt.Report:
        """ СПОДЭСv.3 Е.12.5"""
        match int(self) & 0b1:
            case 0: return cdt.Report(get_message("$normal$"), logging.INFO)
            case 1: return cdt.Report(get_message("$case_is_opened$"), logging.WARN)


class OpeningBody(DataDynamic):
    """ RU. 0.0.96.51.0.255. СТО_34.01-5.1-006-2019v3. E 12.1 """
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=OpeningBodyUnsigned),


class OpeningCoverUnsigned(cdt.ReportMixin, cdt.Unsigned):
    def get_report(self) -> cdt.Report:
        """ СПОДЭСv.3 Е.12.5"""
        match int(self) & 0b1:
            case 0: return cdt.Report(get_message("$normal$"), logging.INFO)
            case 1: return cdt.Report(get_message("$cover_is_opened$"), logging.WARN)


class OpeningCover(DataDynamic):
    """ RU. 0.0.96.51.1.255. СТО_34.01-5.1-006-2019v3. E 12.2 """
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=OpeningCoverUnsigned),


class ExposureToFieldUnsigned(cdt.ReportMixin, cdt.Unsigned):
    def get_report(self) -> cdt.Report:
        if (value := (int(self) & 0b101)) == 0:
            return cdt.Report(get_message("$normal$"), logging.INFO)
        else:
            ret = ""
            if value & 0b001:
                ret += get_message("$fixed_field$")
            if value & 0b100:
                ret += get_message("$exist_field$")
            return cdt.Report(ret, logging.WARN)


class ExposureToMagnet(DataDynamic):
    """ RU. 0.0.96.51.3.255. СТО_34.01-5.1-006-2019v3. E 12.3 """
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=ExposureToFieldUnsigned),


class ExposureToHSField(DataDynamic):
    """ RU. 0.0.96.51.4.255. СТО_34.01-5.1-006-2019v3. E 12.3 """
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=ExposureToFieldUnsigned),


class SealUnsigned(cdt.ReportMixin, cdt.Unsigned):
    def get_report(self) -> cdt.Report:
        def get_name(value: int):
            """ СПОДЭСv.3 Е.12.5"""
            match value & 0b11:
                case 0: return "$undefined$"
                case 1: return "$contentions$"
                case 2: return "$breaked_open$"
                case 3: return "$subsequent_autopsy$"
        return cdt.Report(
            mess=get_message(F"$for_cover$ - {get_name(int(self) & 0b11)}, $for_terminals_cover$ - {get_name((int(self) >> 2) & 0b11)}"),
            lev=logging.INFO if int(self) == 0b101 else logging.WARN)


class SealStatus(DataDynamic):
    """ RU. 0.0.96.51.5.255. СТО_34.01-5.1-006-2019v3. E 12.1 """
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
        return cdt.Report(F"Номер канала связи: {self.channel.name}, Тип интерфейса: {self.interface.name}")


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


class VoltageEventValues(cdt.ReportMixin, cdt.LongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.voltage_events.get_report(int(self)))


class SPODES3VoltageEvent(DataDynamic):
    """СТО_34.01-5.1-006-2019v3 Д.2 События, связанные с напряжением"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=VoltageEventValues),


class CurrentEventValues(cdt.ReportMixin, cdt.LongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.current_events.get_report(int(self)))


class SPODES3CurrentEvent(DataDynamic):
    """СТО_34.01-5.1-006-2019v3 Д.3 События, связанные с током"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=CurrentEventValues),


class CommutationEventValues(cdt.ReportMixin, cdt.LongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.commutation_events.get_report(int(self)))


class SPODES3CommutationEvent(DataDynamic):
    """СТО_34.01-5.1-006-2019v3 Д.4 События, связанные с вкл./выкл. ПУ, коммутации реле нагрузки"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=CommutationEventValues),


class ProgrammingEventValues(cdt.ReportMixin, cdt.LongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.programming_events.get_report(int(self)))


class SPODES3ProgrammingEvent(DataDynamic):
    """СТО_34.01-5.1-006-2019v3 Д.5 События программирования параметров ПУ"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=ProgrammingEventValues),


class ExternalEventValues(cdt.ReportMixin, cdt.LongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.external_impact_events.get_report(int(self)))


class SPODES3ExternalEvent(DataDynamic):
    """СТО_34.01-5.1-006-2019v3 Д.6 События внешних воздействий"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=ExternalEventValues),


class CommunicationEventValues(cdt.ReportMixin, cdt.LongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.communication_events.get_report(int(self)))


class SPODES3CommunicationEvent(DataDynamic):
    """СТО_34.01-5.1-006-2019v3 Д.7 Коммуникационные события"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=CommunicationEventValues),


class AccessEventValues(cdt.ReportMixin, cdt.LongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.access_events.get_report(int(self)))


class SPODES3AccessEvent(DataDynamic):
    """СТО_34.01-5.1-006-2019v3 Д.8 События контроля доступа"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=AccessEventValues),


class SelfDiagnosticEventValues(cdt.ReportMixin, cdt.LongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.self_diagnostics_events.get_report(int(self)))


class SPODES3SelfDiagnosticEvent(DataDynamic):
    """СТО_34.01-5.1-006-2019v3 Д.9 Коды событий для журнала самодиагностики"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=SelfDiagnosticEventValues),


class ReactivePowerEventValues(cdt.ReportMixin, cdt.LongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.reactive_power_events.get_report(int(self)))


class SPODES3ReactivePowerEvent(DataDynamic):
    """СТО_34.01-5.1-006-2019v3 Д.10 События по превышению реактивной мощности"""
    A_ELEMENTS = DataDynamic.get_attr_element(2).get_change(data_type=ReactivePowerEventValues),


class PowerQuality2EventValues(cdt.ReportMixin, cdt.LongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.power_quality_status_2.get_report(int(self)))


class SPODES3PowerQuality2Event(DataNotSpecific):
    """СТО_34.01-5.1-006-2019v3 E.1 Статус качества сети (журнал качества сети)"""
    A_ELEMENTS = DataNotSpecific.get_attr_element(2).get_change(data_type=PowerQuality2EventValues),


class PowerQuality1EventValues(cdt.ReportMixin, cdt.LongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.power_quality_status_1.get_report(int(self)))


class SPODES3PowerQuality1Event(DataNotSpecific):
    """СТО_34.01-5.1-006-2019v3 E.2 Статус качества сети (профиль суточных показаний)"""
    A_ELEMENTS = DataNotSpecific.get_attr_element(2).get_change(data_type=PowerQuality1EventValues),


# KPZ implements
class KPZ1VoltageEventValues(cdt.ReportMixin, cdt.DoubleLongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.voltage_events.get_report(int(self)))


class KPZ1SPODES3VoltageEvent(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Д.2 События, связанные с напряжением with bag in value type"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZ1VoltageEventValues),


class KPZ1CurrentEventValues(cdt.ReportMixin, cdt.DoubleLongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.current_events.get_report(int(self)))


class KPZ1SPODES3CurrentEvent(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Д.3 События, связанные с током"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZ1CurrentEventValues),


class KPZ1CommutationEventValues(cdt.ReportMixin, cdt.DoubleLongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.commutation_events.get_report(int(self)))


class KPZ1SPODES3CommutationEvent(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Д.4 События, связанные с вкл./выкл. ПУ, коммутации реле нагрузки"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZ1CommutationEventValues),


class KPZ1ProgrammingEventValues(cdt.ReportMixin, cdt.DoubleLongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.programming_events.get_report(int(self)))


class KPZ1SPODES3ProgrammingEvent(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Д.5 События программирования параметров ПУ"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZ1ProgrammingEventValues),


class KPZ1ExternalEventValues(cdt.ReportMixin, cdt.DoubleLongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.external_impact_events.get_report(int(self)))


class KPZ1SPODES3ExternalEvent(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Д.6 События внешних воздействий"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZ1ExternalEventValues),


class KPZ1CommunicationEventValues(cdt.ReportMixin, cdt.DoubleLongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.communication_events.get_report(int(self)))


class KPZ1SPODES3CommunicationEvent(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Д.7 Коммуникационные события"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZ1CommunicationEventValues),


class KPZ1AccessEventValues(cdt.ReportMixin, cdt.DoubleLongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.access_events.get_report(int(self)))


class KPZ1SPODES3AccessEvent(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Д.8 События контроля доступа"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZ1AccessEventValues),


class KPZ1SelfDiagnosticEventValues(cdt.ReportMixin, cdt.DoubleLongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.self_diagnostics_events.get_report(int(self)))


class KPZ1SPODES3SelfDiagnosticEvent(DataStatic):
    """СТО_34.01-5.1-006-2019v3 Д.9 Коды событий для журнала самодиагностики"""
    A_ELEMENTS = DataStatic.get_attr_element(2).get_change(data_type=KPZ1SelfDiagnosticEventValues),


class KPZ1ReactivePowerEventValues(cdt.ReportMixin, cdt.DoubleLongUnsigned):
    def get_report(self) -> cdt.Report:
        return cdt.Report(ev.reactive_power_events.get_report(int(self)))  # todo need refactoring


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


class SPODES3SPODESVersionValue(cdt.OctetString):
    def __init__(self, value="332e30"):
        super(SPODES3SPODESVersionValue, self).__init__(value)
        match AppVersion.from_str(self.contents.decode("utf-8")):
            case AppVersion(0, 0, 0): raise ValueError(F"got invalid SPODES VERSION VALUE with: {self}")
            case AppVersion(_, _, None): """valid version"""
            case _: raise ValueError(F"got invalid SPODES VERSION VALUE with: {self}")


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

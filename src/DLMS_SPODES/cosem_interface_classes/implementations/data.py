from ..data import Data, ic, an, cdt, cst, choices
from ... import enums as enu
from .. import events as ev


class Unsigned(Data):
    """ with value type: Unsigned """
    A_ELEMENTS = ic.ICAElement(an.VALUE, cdt.Unsigned, classifier=ic.Classifier.DYNAMIC),


class OctetStringDateTime(Data):
    """ with value type: Unsigned """
    A_ELEMENTS = ic.ICAElement(an.VALUE, cst.OctetStringDateTime, classifier=ic.Classifier.DYNAMIC),


class OpeningBody(Data):
    """ RU. 0.0.96.51.0.255. СТО_34.01-5.1-006-2019v3. E 12.1 """
    A_ELEMENTS = ic.ICAElement(an.VALUE, cdt.Unsigned, classifier=ic.Classifier.DYNAMIC),


class SealUnsigned(cdt.Unsigned):
    @property
    def report(self) -> str:
        def get_name(value: int):
            """ СПОДЭСv.3 Е.12.5"""
            match value & 0b11:
                case 0: return "Не определено"
                case 1: return "Обжата"
                case 2: return "Взломана"
                case 3: return "Последущие вскрытия"
        return F"Электронные пломбы: корпуса - {get_name(int(self) & 0b11)}, крышки клеммников - {get_name((int(self) >> 2) & 0b11)}"


class SealStatus(Data):
    """ RU. 0.0.96.51.5.255. СТО_34.01-5.1-006-2019v3. E 12.1 """
    A_ELEMENTS = ic.ICAElement(an.VALUE, SealUnsigned, classifier=ic.Classifier.DYNAMIC),


class TerminalsCoverOpeningState(Data):
    """ RU. 0.0.96.51.1.255. СТО_34.01-5.1-006-2019v3. E 12.2 """
    A_ELEMENTS = ic.ICAElement(an.VALUE, cdt.Unsigned, classifier=ic.Classifier.DYNAMIC),


class BitMapData(cdt.Structure):
    values: tuple[cst.OctetStringDateTime, cst.OctetStringDateTime, cdt.OctetString]
    ELEMENTS = (cdt.StructElement(cdt.se.START_TIME, cst.OctetStringDateTime),
                cdt.StructElement(cdt.se.STOP_TIME, cst.OctetStringDateTime),
                cdt.StructElement(cdt.se.ITE_BIT_MAP, cdt.OctetString))

    @property
    def start_time(self) -> cst.OctetStringDateTime:
        """time of start show bitmap"""
        return self.values[0]

    @property
    def stop_time(self) -> cst.OctetStringDateTime:
        """time of stop show bitmap"""
        return self.values[1]

    @property
    def bitmap_data(self) -> cdt.OctetString:
        """data with bitmap format"""
        return self.values[2]


class ITEBitMap(Data):
    """ITE 0.128.96.13.1.255. Use for send struct lcd screen bitmap(BMP) with start/stop period to server"""
    A_ELEMENTS = ic.ICAElement(an.VALUE, BitMapData, classifier=ic.Classifier.STATIC),


class ChannelNumberValue(cdt.Unsigned):
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

    @property
    def report(self) -> str:
        return F"Номер канала связи: {self.channel.name}, Тип интерфейса: {self.interface.name}"

    def __str__(self):
        return self.report


class CommunicationPortParameter(Data):
    """ RU. 0.0.96.12.4.255. СТО_34.01-5.1-006-2019v3. 13.10. Определение номера порта по которому установлено соединение"""
    A_ELEMENTS = ic.ICAElement(an.VALUE, ChannelNumberValue, default=enu.ChannelNumber.OPTO_P1 + (enu.Interface.OPTO << 3), classifier=ic.Classifier.DYNAMIC),

    @property
    def value(self) -> ChannelNumberValue:
        """override returned type"""
        return self.get_attr(2)


class AnyDateTime(Data):
    """for a-anotation DLMS UA 1000-1 Ed. 14 Table 60"""
    A_ELEMENTS = ic.ICAElement(an.VALUE, choices.any_date_time, classifier=ic.Classifier.STATIC),


class VoltageEventValues(cdt.LongUnsigned):
    @property
    def report(self) -> str:
        return ev.voltage_events.get_report(int(self))


class SPODES3VoltageEvent(Data):
    """СТО_34.01-5.1-006-2019v3 Д.2 События, связанные с напряжением"""
    A_ELEMENTS = ic.ICAElement(an.VALUE, VoltageEventValues, classifier=ic.Classifier.STATIC),


class CurrentEventValues(cdt.LongUnsigned):
    @property
    def report(self) -> str:
        return ev.current_events.get_report(int(self))


class SPODES3CurrentEvent(Data):
    """СТО_34.01-5.1-006-2019v3 Д.3 События, связанные с током"""
    A_ELEMENTS = ic.ICAElement(an.VALUE, CurrentEventValues, classifier=ic.Classifier.STATIC),


class CommutationEventValues(cdt.LongUnsigned):
    @property
    def report(self) -> str:
        return ev.commutation_events.get_report(int(self))


class SPODES3CommutationEvent(Data):
    """СТО_34.01-5.1-006-2019v3 Д.4 События, связанные с вкл./выкл. ПУ, коммутации реле нагрузки"""
    A_ELEMENTS = ic.ICAElement(an.VALUE, CommutationEventValues, classifier=ic.Classifier.STATIC),


class ProgrammingEventValues(cdt.LongUnsigned):
    @property
    def report(self) -> str:
        return ev.programming_events.get_report(int(self))


class SPODES3ProgrammingEvent(Data):
    """СТО_34.01-5.1-006-2019v3 Д.5 События программирования параметров ПУ"""
    A_ELEMENTS = ic.ICAElement(an.VALUE, ProgrammingEventValues, classifier=ic.Classifier.STATIC),


class ExternalEventValues(cdt.LongUnsigned):
    @property
    def report(self) -> str:
        return ev.external_impact_events.get_report(int(self))


class SPODES3ExternalEvent(Data):
    """СТО_34.01-5.1-006-2019v3 Д.6 События внешних воздействий"""
    A_ELEMENTS = ic.ICAElement(an.VALUE, ExternalEventValues, classifier=ic.Classifier.STATIC),


class CommunicationEventValues(cdt.LongUnsigned):
    @property
    def report(self) -> str:
        return ev.communication_events.get_report(int(self))


class SPODES3CommunicationEvent(Data):
    """СТО_34.01-5.1-006-2019v3 Д.7 Коммуникационные события"""
    A_ELEMENTS = ic.ICAElement(an.VALUE, CommunicationEventValues, classifier=ic.Classifier.STATIC),


class AccessEventValues(cdt.LongUnsigned):
    @property
    def report(self) -> str:
        return ev.access_events.get_report(int(self))


class SPODES3AccessEvent(Data):
    """СТО_34.01-5.1-006-2019v3 Д.8 События контроля доступа"""
    A_ELEMENTS = ic.ICAElement(an.VALUE, AccessEventValues, classifier=ic.Classifier.STATIC),


class SelfDiagnosticEventValues(cdt.LongUnsigned):
    @property
    def report(self) -> str:
        return ev.self_diagnostics_events.get_report(int(self))


class SPODES3SelfDiagnosticEvent(Data):
    """СТО_34.01-5.1-006-2019v3 Д.9 Коды событий для журнала самодиагностики"""
    A_ELEMENTS = ic.ICAElement(an.VALUE, SelfDiagnosticEventValues, classifier=ic.Classifier.STATIC),


class ReactivePowerEventValues(cdt.LongUnsigned):
    @property
    def report(self) -> str:
        return ev.reactive_power_events.get_report(int(self))


class SPODES3ReactivePowerEvent(Data):
    """СТО_34.01-5.1-006-2019v3 Д.10 События по превышению реактивной мощности"""
    A_ELEMENTS = ic.ICAElement(an.VALUE, ReactivePowerEventValues, classifier=ic.Classifier.STATIC),

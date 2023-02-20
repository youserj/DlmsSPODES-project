from ..types import common_data_types as cdt
from ..settings import get_current_language, Language


match get_current_language():
    case Language.ENGLISH: from ..Values.EN import events as e
    case Language.RUSSIAN: from ..Values.RU import events as e


class FlagEvents(dict):
    """ special class for flag events indication """
    def get_report(self, value: int) -> str:
        return '. '.join(filter(lambda it_: it_ is not None, map(lambda it: self.get(2 ** it, F"unknown bit: {it}"), filter(lambda it: value & 2 ** it, range(8)))))


class Events(dict):
    """ special class for enumerate events indication """
    def get_report(self, value: int) -> str:
        return self.get(value, "error enum")


voltage_events = Events(tuple((int(key.split('_')[-1]), e.__dict__[key]) for key in filter(lambda i: i.startswith("VOLTAGE"), e.__dict__)))
"""for 0.0.96.11.0.255 События, связанные с напряжением ГОСТ Р 58940—2020 таблица Д.1"""
current_events = Events(tuple((int(key.split('_')[-1]), e.__dict__[key]) for key in filter(lambda i: i.startswith("CURRENT"), e.__dict__)))
"""for current_events События, связанные с током ГОСТ Р 58940—2020 таблица Д.2"""
commutation_events = Events(tuple((int(key.split('_')[-1]), e.__dict__[key]) for key in filter(lambda i: i.startswith("COMMUTATION"), e.__dict__)))
"""for 0.0.96.11.2.255 События, связанные с включением/выключением ПУ. коммутации реле нагрузки ГОСТ Р 58940—2020 таблица Д.3"""
programming_events = Events(tuple((int(key.split('_')[-1]), e.__dict__[key]) for key in filter(lambda i: i.startswith("PROGRAMING"), e.__dict__)))
"""for 0.0.96.11.3.255 События программирования параметров ПУ ГОСТ Р 58940—2020 таблица Д.4"""
external_impact_events = Events(tuple((int(key.split('_')[-1]), e.__dict__[key]) for key in filter(lambda i: i.startswith("EXTERNAL_IMPACT"), e.__dict__)))
"""for 0.0.96.11.4.255 События внешних воздействий ГОСТ Р 58940—2020 таблица Д.5"""
communication_events = Events(tuple((int(key.split('_')[-1]), e.__dict__[key]) for key in filter(lambda i: i.startswith("COMMUNICATION"), e.__dict__)))
"""for 0.0.96.11.5.255 Коммуникационные события ГОСТ Р 58940—2020 таблица Д.6"""
access_events = Events(tuple((int(key.split('_')[-1]), e.__dict__[key]) for key in filter(lambda i: i.startswith("ACCESS"), e.__dict__)))
"""for 0.0.96.11.6.255 События контроля доступа ГОСТ Р 58940—2020 таблица Д.7"""
self_diagnostics_events = Events(tuple((int(key.split('_')[-1]), e.__dict__[key]) for key in filter(lambda i: i.startswith("SELF_DIAGNOSTIC"), e.__dict__)))
"""for 0.0.96.11.7.255 Коды событий для журнала самодиагностики ГОСТ Р 58940—2020 таблица Д.8"""
reactive_power_events = Events(tuple((int(key.split('_')[-1]), e.__dict__[key]) for key in filter(lambda i: i.startswith("REACTIVE_POWER"), e.__dict__)))
"""for 0.0.96.11.8.255 События по превышению реактивной мощности tg (ф) (тангенс сети) ГОСТ Р 58940—2020 таблица Д.9"""
power_quality_status_1 = FlagEvents(tuple((int(key.split('_')[-1], base=16), e.__dict__[key]) for key in filter(lambda i: i.startswith("POWER_QUALITY1"), e.__dict__)))
"""for 0.0.96.5.1.255 Статус качества сети (профиль суточных показаний) СТО 34.01-5.1-006-2021 таблица Е.2"""
power_quality_status_2 = FlagEvents(tuple((int(key.split('_')[-1], base=16), e.__dict__[key]) for key in filter(lambda i: i.startswith("POWER_QUALITY2"), e.__dict__)))
"""for 0.0.96.5.4.255 Статус качества сети (журнал качества сети) СТО 34.01-5.1-006-2021 таблица Е.1"""


def get_report(self, value=None, *args) -> str:
    """ get value of event code by value(attribute 2) in order to event codes table """
    value = self.value if value is None else value
    if isinstance(value, (cdt.Unsigned, cdt.LongUnsigned, cdt.DoubleLongUnsigned, cdt.Long64Unsigned)):
        try:
            return self.events[value.decode()]
        except KeyError:
            return F'Unknown event code: {value.decode()}'
    else:
        raise TypeError(F'For object {self} wrong value type, got {value.NAME}')

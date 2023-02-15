import settings
from types import common_data_types as cdt


class FlagEvents(dict):
    """ special class for flag events indication """
    def get_report(self, value: int) -> str:
        active_bites = filter(lambda it: value & 2 ** it, range(8))
        names_dict = filter(lambda it_: it_ is not None, map(lambda it: self.get(2 ** it), active_bites))
        language = settings.get_current_language()
        return '. '.join(map(lambda name_dict: name_dict[language], names_dict))


class Events(dict):
    """ special class for enumerate events indication """
    def get_report(self, value: int) -> str:
        match self.get(value):
            case None: return 'error enum'
            case _ as name:    return name[settings.get_current_language()]


# for 0.0.96.11.0.255 События, связанные с напряжением ГОСТ Р 58940—2020 таблица Д.1
voltage_events = Events((
    (1, {settings.Language.ENGLISH: F'Phase L1-voltage drop', settings.Language.RUSSIAN: F'Фаза А - пропадание напряжения'}),
    (2, {settings.Language.ENGLISH: F'Phase L1-voltage recovery', settings.Language.RUSSIAN: F'Фаза А - восстановление напряжения'}),
    (3, {settings.Language.ENGLISH: F'Phase L2-voltage drop', settings.Language.RUSSIAN: F'Фаза В - пропадание напряжения'}),
    (4, {settings.Language.ENGLISH: F'Phase L2-voltage recovery', settings.Language.RUSSIAN: F'Фаза В - восстановление напряжения'}),
    (5, {settings.Language.ENGLISH: F'Phase L3-voltage drop', settings.Language.RUSSIAN: F'Фаза С - пропадание напряжения'}),
    (6, {settings.Language.ENGLISH: F'Phase L3-voltage recovery', settings.Language.RUSSIAN: F'Фаза С - восстановление напряжения'}),
    (7, {settings.Language.ENGLISH: F'Exceeding the voltage of any phase', settings.Language.RUSSIAN: F'Превышение напряжения любой фазы'}),
    (8, {settings.Language.ENGLISH: F'End of over voltage of any phase', settings.Language.RUSSIAN: F'Окончание перенапряжения любой фазы'}),
    (9, {settings.Language.ENGLISH: F'Low voltage of any phase-start', settings.Language.RUSSIAN: F'Низкое напряжение любой фазы - начало'}),
    (10, {settings.Language.ENGLISH: F'Low voltage of any phase-end', settings.Language.RUSSIAN: F'Низкое напряжение любой фазы - окончание'}),
    (11, {settings.Language.ENGLISH: F'Excess of the voltage unbalance coefficient in the reverse sequence-the beginning',
          settings.Language.RUSSIAN: F'Превышение коэффициента несимметрии напряжений по обратной последовательности - начало'}),
    (12, {settings.Language.ENGLISH: F'Excess of the voltage unbalance coefficient in the reverse sequence - end',
          settings.Language.RUSSIAN: F'Превышение коэффициента несимметрии напряжений по обратной последовательности - окончание'}),
    (13, {settings.Language.ENGLISH: F'Phase L1-over voltage start', settings.Language.RUSSIAN: F'Фаза А - перенапряжение начало'}),
    (14, {settings.Language.ENGLISH: F'Phase L1-over voltage end', settings.Language.RUSSIAN: F'Фаза А - перенапряжение окончание'}),
    (15, {settings.Language.ENGLISH: F'Phase L2-over voltage start', settings.Language.RUSSIAN: F'Фаза В - перенапряжение начало'}),
    (16, {settings.Language.ENGLISH: F'Phase L2-over voltage end', settings.Language.RUSSIAN: F'Фаза В - перенапряжение окончание'}),
    (17, {settings.Language.ENGLISH: F'Phase L3-over voltage start', settings.Language.RUSSIAN: F'Фаза С - перенапряжение начало'}),
    (18, {settings.Language.ENGLISH: F'Phase L3-over voltage end', settings.Language.RUSSIAN: F'Фаза С - перенапряжение окончание'}),
    (19, {settings.Language.ENGLISH: F'Phase L1-failure start', settings.Language.RUSSIAN: F'Фаза А - провал начало'}),
    (20, {settings.Language.ENGLISH: F'Phase L1-failure ending', settings.Language.RUSSIAN: F'Фаза А - провал окончание'}),
    (21, {settings.Language.ENGLISH: F'Phase L2-failure start', settings.Language.RUSSIAN: F'Фаза В - провал начало'}),
    (22, {settings.Language.ENGLISH: F'Phase L2-failure ending', settings.Language.RUSSIAN: F'Фаза В - провал окончание'}),
    (23, {settings.Language.ENGLISH: F'Phase L3-failure start', settings.Language.RUSSIAN: F'Фаза С - провал начало'}),
    (24, {settings.Language.ENGLISH: F'Phase L3-failure ending', settings.Language.RUSSIAN: F'Фаза С - провал окончание'}),
    (25, {settings.Language.ENGLISH: F'Incorrect phase sequence start', settings.Language.RUSSIAN: F'Неправильная последовательность фаз начало'}),
    (26, {settings.Language.ENGLISH: F'Incorrect phase sequence ending', settings.Language.RUSSIAN: F'Неправильная последовательность фаз окончание'}),
    (27, {settings.Language.ENGLISH: F'Voltage interruption', settings.Language.RUSSIAN: F'Прерывание напряжения'}),
    (28, {settings.Language.ENGLISH: F'Voltage recovery', settings.Language.RUSSIAN: F'Восстановление напряжения'})))

# for current_events События, связанные с током ГОСТ Р 58940—2020 таблица Д.2
current_events = Events((
    (1, {settings.Language.ENGLISH: F'Phase L1-export start', settings.Language.RUSSIAN: F'Фаза А - экспорт начало'}),
    (2, {settings.Language.ENGLISH: F'Phase L1-Export end', settings.Language.RUSSIAN: F'Фаза А - экспорт окончание'}),
    (3, {settings.Language.ENGLISH: F'Phase L2-export start', settings.Language.RUSSIAN: F'Фаза В - экспорт начало'}),
    (4, {settings.Language.ENGLISH: F'Phase L2-Export end', settings.Language.RUSSIAN: F'Фаза В - экспорт окончание'}),
    (5, {settings.Language.ENGLISH: F'Phase L3-export start', settings.Language.RUSSIAN: F'Фаза С - экспорт начало'}),
    (6, {settings.Language.ENGLISH: F'Phase L3-Export end', settings.Language.RUSSIAN: F'Фаза С - экспорт окончание'}),
    (7, {settings.Language.ENGLISH: F'Phase L1 current transformer breakage', settings.Language.RUSSIAN: F'Обрыв трансформатора тока фазы А'}),
    (8, {settings.Language.ENGLISH: F'Restoring the Phase L1 current transformer', settings.Language.RUSSIAN: F'Восстановление трансформатора тока фазы А'}),
    (9, {settings.Language.ENGLISH: F'Phase L2 current transformer breakage', settings.Language.RUSSIAN: F'Обрыв трансформатора тока фазы В'}),
    (10, {settings.Language.ENGLISH: F'Restoring the Phase L2 current transformer', settings.Language.RUSSIAN: F'Восстановление трансформатора тока фазы В'}),
    (11, {settings.Language.ENGLISH: F'Phase L3 current transformer breakage', settings.Language.RUSSIAN: F'Обрыв трансформатора тока фазы С'}),
    (12, {settings.Language.ENGLISH: F'Restoring the Phase L3 current transformer', settings.Language.RUSSIAN: F'Восстановление трансформатора тока фазы С'}),
    (13, {settings.Language.ENGLISH: F'Current unbalance-the beginning', settings.Language.RUSSIAN: F'Разбаланс токов - начало'}),
    (14, {settings.Language.ENGLISH: F'Current unbalance-end', settings.Language.RUSSIAN: F'Разбаланс токов - окончание'}),
    (15, {settings.Language.ENGLISH: F'Current transformer short circuit-start', settings.Language.RUSSIAN: F'Замыкание трансформатора тока — начало'}),
    (16, {settings.Language.ENGLISH: F'Current transformer short circuit termination', settings.Language.RUSSIAN: F'Окончание замыкания трансформатора тока'}),
    (17, {settings.Language.ENGLISH: F'Exceeding the current of any phase-the beginning', settings.Language.RUSSIAN: F'Превышение тока любой фазы - начало'}),
    (18, {settings.Language.ENGLISH: F'End of excess current of any phase', settings.Language.RUSSIAN: F'Окончание превышения тока любой фазы'}),
    (19, {settings.Language.ENGLISH: F'Phase L1-the presence of current in the absence of voltage start', settings.Language.RUSSIAN: F'Фаза А-наличие тока при отсутствии напряжения начало'}),
    (20, {settings.Language.ENGLISH: F'Phase L1-the presence of current in the absence of voltage end', settings.Language.RUSSIAN: F'Фаза А-наличие тока при отсутствии напряжения окончание'}),
    (21, {settings.Language.ENGLISH: F'Phase L2-the presence of current in the absence of voltage start', settings.Language.RUSSIAN: F'Фаза В - наличие тока при отсутствии напряжения начало'}),
    (22, {settings.Language.ENGLISH: F'Phase L2-the presence of current in the absence of voltage end', settings.Language.RUSSIAN: F'Фаза В - наличие тока при отсутствии напряжения окончание'}),
    (23, {settings.Language.ENGLISH: F'Phase L3-the presence of current in the absence of voltage start', settings.Language.RUSSIAN: F'Фаза С - наличие тока при отсутствии напряжения начало'}),
    (24, {settings.Language.ENGLISH: F'Phase L3-the presence of current in the absence of voltage end', settings.Language.RUSSIAN: F'Фаза С - наличие тока при отсутствии напряжения окончание'}),
    (25, {settings.Language.ENGLISH: F'Phase L1-exceeding the maximum current start', settings.Language.RUSSIAN: F'Фаза А - превышение максимального тока начало'}),
    (26, {settings.Language.ENGLISH: F'Phase L1-exceeding the maximum current end', settings.Language.RUSSIAN: F'Фаза А - превышение максимального тока окончание'}),
    (27, {settings.Language.ENGLISH: F'Phase L2-exceeding the maximum current start', settings.Language.RUSSIAN: F'Фаза В - превышение максимального тока начало'}),
    (28, {settings.Language.ENGLISH: F'Phase L2-exceeding the maximum current end', settings.Language.RUSSIAN: F'Фаза В - превышение максимального тока окончание'}),
    (29, {settings.Language.ENGLISH: F'Phase L3-exceeding the maximum current start', settings.Language.RUSSIAN: F'Фаза С - превышение максимального тока начало'}),
    (30, {settings.Language.ENGLISH: F'Phase L3-exceeding the maximum current end', settings.Language.RUSSIAN: F'Фаза С - превышение максимального тока окончание'}),
    (31, {settings.Language.ENGLISH: F'The presence of current in the absence of voltage (neutral breakage). Begin',
          settings.Language.RUSSIAN: F'Наличие тока при отсутствии напряжения (обрыв нейтрали) – начало'}),
    (32, {settings.Language.ENGLISH: F"The presence of current in the absence of voltage (neutral breakage). End",
          settings.Language.RUSSIAN: F"Наличие тока при отсутствии напряжения (обрыв нейтрали) - окончание"}),
    (33, {settings.Language.ENGLISH: F"Reverse of the power (export of current) in a unidirectional counter. Begin",
          settings.Language.RUSSIAN: F"Обратный поток мощности (экспорт тока) в однонаправленном счётчике - начало"}),
    (34, {settings.Language.ENGLISH: F"Reverse of the power (export of current) in a unidirectional counter. End",
          settings.Language.RUSSIAN: F"Обратный поток мощности (экспорт тока) в однонаправленном счётчике - конец"}),
    (35, {settings.Language.ENGLISH: F"Unspressed phase power in a three -phase and single -phase two -element counter. Begin",
          settings.Language.RUSSIAN: F"Разнонаправленная мощность по фазам в трёхфазном и однофазном двухэлементном счётчике - начало"}),
    (36, {settings.Language.ENGLISH: F"Unspressed phase power in a three -phase and single -phase two -element counter. End",
          settings.Language.RUSSIAN: F"Разнонаправленная мощность по фазам в трёхфазном и однофазном двухэлементном счётчике - окончание"}),
    (37, {settings.Language.ENGLISH: F"The presence of current with the load relay is turned off. Begin",
          settings.Language.RUSSIAN: F"Наличие тока при выключенном реле нагрузки – начало"}),
    (38, {settings.Language.ENGLISH: F"The presence of current with the load relay is turned off. End",
          settings.Language.RUSSIAN: F"Наличие тока при выключенном реле нагрузки – окончание"})))


# for 0.0.96.11.2.255 События, связанные с включением/выключением ПУ. коммутации реле нагрузки ГОСТ Р 58940—2020 таблица Д.3
commutation_events = Events((
    (1, {settings.Language.ENGLISH: F'Power down of the device', settings.Language.RUSSIAN: F'Выключение питания ПУ'}),
    (2, {settings.Language.ENGLISH: F'Powering up the device', settings.Language.RUSSIAN: F'Включение питания ПУ'}),
    (3, {settings.Language.ENGLISH: F'Remote subscriber shutdown', settings.Language.RUSSIAN: F'Выключение абонента дистанционное'}),
    (4, {settings.Language.ENGLISH: F'Enabling the subscriber remotely', settings.Language.RUSSIAN: F'Включение абонента дистанционное'}),
    (5, {settings.Language.ENGLISH: F'Getting permission to enable the subscriber', settings.Language.RUSSIAN: F'Получение разрешения на включение абоненту'}),
    (6, {settings.Language.ENGLISH: F'Switching off the load relay by the subscriber', settings.Language.RUSSIAN: F'Выключение реле нагрузки абонентом'}),
    (7, {settings.Language.ENGLISH: F'Switching on the load relay by the subscriber', settings.Language.RUSSIAN: F'Включение реле нагрузки абонентом'}),
    (8, {settings.Language.ENGLISH: F'Local shutdown when the power limit is exceeded', settings.Language.RUSSIAN: F'Выключение локальное по превышению лимита мощности'}),
    (9, {settings.Language.ENGLISH: F'Local shutdown when the maximum current is exceeded', settings.Language.RUSSIAN: F'Выключение локальное по превышению максимального тока'}),
    (10, {settings.Language.ENGLISH: F'Local shutdown when exposed to a magnetic field', settings.Language.RUSSIAN: F'Выключение локальное при воздействии магнитного поля'}),
    (11, {settings.Language.ENGLISH: F'Local shutdown when the voltage is exceeded', settings.Language.RUSSIAN: F'Выключение локальное по превышению напряжения'}),
    (12, {settings.Language.ENGLISH: F'Switching on local when the voltage returns to normal', settings.Language.RUSSIAN: F'Включение локальное при возвращение напряжения в норму'}),
    (13, {settings.Language.ENGLISH: F'Local shutdown by the presence of current in the absence of voltage',
         settings.Language.RUSSIAN: F'Выключение локальное по наличию тока при отсутствии напряжения'}),
    (14, {settings.Language.ENGLISH: F'Local shutdown based on current unbalance', settings.Language.RUSSIAN: F'Выключение локальное по разбалансу токов'}),
    (15, {settings.Language.ENGLISH: F'Local temperature shutdown', settings.Language.RUSSIAN: F'Выключение локальное по температуре'}),
    (16, {settings.Language.ENGLISH: F'Enabling backup power', settings.Language.RUSSIAN: F'Включение резервного питания'}),
    (17, {settings.Language.ENGLISH: F'Switching off the backup power supply', settings.Language.RUSSIAN: F'Отключение резервного питания'}),
    (18, {settings.Language.ENGLISH: F'Local shutdown when opening the terminal cover or housing',
         settings.Language.RUSSIAN: F'Выключение локальное при вскрытии клеммной крышки или корпуса'})))


# for 0.0.96.11.3.255 События программирования параметров ПУ ГОСТ Р 58940—2020 таблица Д.4
programming_events = Events((
    (1, {settings.Language.ENGLISH: F'Changing the address or the RS-485-1 exchange rate', settings.Language.RUSSIAN: F'Изменение адреса или скорости обмена RS-485-1'}),
    (2, {settings.Language.ENGLISH: F'Changing the address or the RS-485-2 exchange rate', settings.Language.RUSSIAN: F'Изменение адреса или скорости обмена RS-485-2'}),
    (3, {settings.Language.ENGLISH: F'Setting the time', settings.Language.RUSSIAN: F'Установка времени'}),
    (4, {settings.Language.ENGLISH: F'Changing Daylight Saving time settings', settings.Language.RUSSIAN: F'Изменение параметров перехода на летнее время'}),
    (5, {settings.Language.ENGLISH: F'Changing the seasonal profile of the tariff schedule', settings.Language.RUSSIAN: F'Изменение сезонного профиля тарифного расписания (ТР)'}),
    (6, {settings.Language.ENGLISH: F'Changing the weekly profile of the tariff schedule', settings.Language.RUSSIAN: F'Изменение недельного профиля ТР'}),
    (7, {settings.Language.ENGLISH: F'Changing the day profile of the tariff schedule', settings.Language.RUSSIAN: F'Изменение суточного профиля ТР'}),
    (8, {settings.Language.ENGLISH: F'Changing the activation date of the tariff schedule', settings.Language.RUSSIAN: F'Изменение даты активации ТР'}),
    (9, {settings.Language.ENGLISH: F'Activation of the tariff schedule', settings.Language.RUSSIAN: F'Активация ТР'}),
    (10, {settings.Language.ENGLISH: F'Changing the billing day-hour', settings.Language.RUSSIAN: F'Изменение расчетного дня-часа (РДЧ)'}),
    (11, {settings.Language.ENGLISH: F'Changing the display mode (parameters)', settings.Language.RUSSIAN: F'Изменение режима индикации (параметры)'}),
    (12, {settings.Language.ENGLISH: F'Changing the display mode (auto-switch)', settings.Language.RUSSIAN: F'Изменение режима индикации (автопереключение)'}),
    (13, {settings.Language.ENGLISH: F'Changing a low-security (read-only) password)', settings.Language.RUSSIAN: F'Изменение пароля низкой секретности (на чтение)'}),
    (14, {settings.Language.ENGLISH: F'Changing the high-security password (on the record)', settings.Language.RUSSIAN: F'Изменение пароля высокой секретности (на запись)'}),
    (15, {settings.Language.ENGLISH: F'Changing accounting point data', settings.Language.RUSSIAN: F'Изменение данных точки учета'}),
    (16, {settings.Language.ENGLISH: F'Change in the current conversion factor', settings.Language.RUSSIAN: F'Изменение коэффициента трансформации по току'}),
    (17, {settings.Language.ENGLISH: F'Change in the voltage transformation coefficient', settings.Language.RUSSIAN: F'Изменение коэффициента трансформации по напряжению'}),
    (18, {settings.Language.ENGLISH: F'Changing the line parameters for calculating power line losses', settings.Language.RUSSIAN: F'Изменение параметров линии для вычисления потерь в ЛЭП'}),
    (19, {settings.Language.ENGLISH: F'Changing the power limit for disconnection', settings.Language.RUSSIAN: F'Изменение лимита мощности для отключения'}),
    (20, {settings.Language.ENGLISH: F'Changing the power-off time interval', settings.Language.RUSSIAN: F'Изменение интервала времени на отключение по мощности'}),
    (21, {settings.Language.ENGLISH: F'Changing the time interval for switching off when the maximum current is exceeded',
         settings.Language.RUSSIAN: F'Изменение интервала времени на отключение по превышению максимального тока'}),
    (22, {settings.Language.ENGLISH: F'Changing the time interval for switching off at the maximum voltage',
         settings.Language.RUSSIAN: F'Изменение интервала времени на отключение по максимальному напряжению'}),
    (23, {settings.Language.ENGLISH: F'Changing the time interval for switching off due to the influence of a magnetic field',
         settings.Language.RUSSIAN: F'Изменение интервала времени на отключение по воздействию магнитного поля'}),
    (24, {settings.Language.ENGLISH: F'Changing the threshold for fixing a power break', settings.Language.RUSSIAN: F'Изменение порога для фиксации перерыва в питании'}),
    (25, {settings.Language.ENGLISH: F'Changing the threshold for fixing the overvoltage', settings.Language.RUSSIAN: F'Изменение порога для фиксации перенапряжения'}),
    (26, {settings.Language.ENGLISH: F'Changing the threshold for fixing the voltage drop', settings.Language.RUSSIAN: F'Изменение порога для фиксации провала напряжения'}),
    (27, {settings.Language.ENGLISH: F'Changing the threshold for fixing the excess of the tangent', settings.Language.RUSSIAN: F'Изменение порога для фиксации превышения тангенса'}),
    (28, {settings.Language.ENGLISH: F'Changing the threshold for fixing the stress asymmetry coefficient',
         settings.Language.RUSSIAN: F'Изменение порога для фиксации коэффициента несимметрии напряжений'}),
    (29, {settings.Language.ENGLISH: F'Changing the matched voltage', settings.Language.RUSSIAN: F'Изменение согласованного напряжения'}),
    (30, {settings.Language.ENGLISH: F'Changing the peak power integration interval', settings.Language.RUSSIAN: F'Изменение интервала интегрирования пиковой мощности'}),
    (31, {settings.Language.ENGLISH: F'Changing the capture period of profile 1', settings.Language.RUSSIAN: F'Изменение периода захвата профиля 1'}),
    (32, {settings.Language.ENGLISH: F'Changing the capture period of profile 2', settings.Language.RUSSIAN: F'Изменение периода захвата профиля 2'}),
    (33, {settings.Language.ENGLISH: F'Changing the LCD backlight mode', settings.Language.RUSSIAN: F'Изменение режима подсветки LCD'}),
    (34, {settings.Language.ENGLISH: F'Changing the telemetry mode 1', settings.Language.RUSSIAN: F'Изменение режима телеметрии 1'}),
    (35, {settings.Language.ENGLISH: F'Cleaning the monthly log', settings.Language.RUSSIAN: F'Очистка месячного журнала'}),
    (36, {settings.Language.ENGLISH: F'Clearing the daily log', settings.Language.RUSSIAN: F'Очистка суточного журнала'}),
    (37, {settings.Language.ENGLISH: F'Clearing the voltage log', settings.Language.RUSSIAN: F'Очистка журнала напряжения'}),
    (38, {settings.Language.ENGLISH: F'Clearing the current log', settings.Language.RUSSIAN: F'Очистка журнала тока'}),
    (39, {settings.Language.ENGLISH: F'Clearing the on/off log', settings.Language.RUSSIAN: F'Очистка журнала вкл/выкл'}),
    (40, {settings.Language.ENGLISH: F'Clearing the external impact log', settings.Language.RUSSIAN: F'Очистка журнала внешних воздействий'}),
    (41, {settings.Language.ENGLISH: F'Clearing the connection log', settings.Language.RUSSIAN: F'Очистка журнала соединений'}),
    (42, {settings.Language.ENGLISH: F'Clearing the unauthorized access log', settings.Language.RUSSIAN: F'Очистка журнала несанкционированного доступа'}),
    (43, {settings.Language.ENGLISH: F'Clearing the network quality log', settings.Language.RUSSIAN: F'Очистка журнала качества сети'}),
    (44, {settings.Language.ENGLISH: F'Clearing the tangent log', settings.Language.RUSSIAN: F'Очистка журнала тангенса'}),
    (45, {settings.Language.ENGLISH: F'Clearing the I/O log', settings.Language.RUSSIAN: F'Очистка журнала входов/выходов'}),
    (46, {settings.Language.ENGLISH: F'Clearing profile 1', settings.Language.RUSSIAN: F'Очистка профиля 1'}),
    (47, {settings.Language.ENGLISH: F'Clearing profile 2', settings.Language.RUSSIAN: F'Очистка профиля 2'}),
    (48, {settings.Language.ENGLISH: F'Clearing profile 3', settings.Language.RUSSIAN: F'Очистка профиля 3'}),
    (49, {settings.Language.ENGLISH: F'Changing the special Days table', settings.Language.RUSSIAN: F'Изменение таблицы специальных дней'}),
    (50, {settings.Language.ENGLISH: F'Changing the relay control mode', settings.Language.RUSSIAN: F'Изменение режима управления реле'}),
    (51, {settings.Language.ENGLISH: F'Recording of readings in the monthly log', settings.Language.RUSSIAN: F'Фиксация показаний в месячном журнале'}),
    (52, {settings.Language.ENGLISH: F'Changing the initiative exit mode', settings.Language.RUSSIAN: F'Изменение режима инициативного выхода'}),
    (53, {settings.Language.ENGLISH: F'Changing the unicast key for low security', settings.Language.RUSSIAN: F'Изменение одноадресного ключа для низкой секретности'}),
    (54, {settings.Language.ENGLISH: F'Changing the broadcast encryption key for low security',
         settings.Language.RUSSIAN: F'Изменение широковещательного ключа шифрования для низкой секретности'}),
    (55, {settings.Language.ENGLISH: F'Changing the unicast key for high security', settings.Language.RUSSIAN: F'Изменение одноадресного ключа для высокой секретности'}),
    (56, {settings.Language.ENGLISH: F'Changing the broadcast key for high security', settings.Language.RUSSIAN: F'Изменение широковещательного ключа для высокой секретности'}),
    (57, {settings.Language.ENGLISH: F'Changing the authentication key for high security', settings.Language.RUSSIAN: F'Изменение ключа аутентификации для высокой секретности'}),
    (58, {settings.Language.ENGLISH: F'Changing the master key', settings.Language.RUSSIAN: F'Изменение мэстер-ключа'}),
    (59, {settings.Language.ENGLISH: F'Change the conversion level for low secrecy', settings.Language.RUSSIAN: F'Изменение уровня преобразования для низкой секретности'}),
    (60, {settings.Language.ENGLISH: F'Change the conversion level for high security', settings.Language.RUSSIAN: F'Изменение уровня преобразования для высокой секретности'}),
    (61, {settings.Language.ENGLISH: F'Changing the remote display number', settings.Language.RUSSIAN: F'Изменение номера дистанционного дисплея'}),
    (62, {settings.Language.ENGLISH: F'Changing the active energy metering mode (modulo or separately in two directions)',
         settings.Language.RUSSIAN: F'Изменение режима учета активной энергии (по модулю или раздельно в двух направлениях)'}),
    (63, {settings.Language.ENGLISH: F'Setting the time by GPS/GLONASS', settings.Language.RUSSIAN: F'Установка времени по GPS/ГЛОНАСС'}),
    (64, {settings.Language.ENGLISH: F'Changing the neutral break-off mode', settings.Language.RUSSIAN: F'Изменение режима отключения по обрыву нейтрали'}),
    (65, {settings.Language.ENGLISH: F'Software Update', settings.Language.RUSSIAN: F'Обновление ПО'}),
    (66, {settings.Language.ENGLISH: F'Changing the current unbalance shutdown mode', settings.Language.RUSSIAN: F'Изменение режима отключения по разбалансу токов'}),
    (67, {settings.Language.ENGLISH: F'Changing the temperature shutdown mode', settings.Language.RUSSIAN: F'Изменение режима отключения по температуре'}),
    (68, {settings.Language.ENGLISH: F'Time correction', settings.Language.RUSSIAN: F'Коррекция времени'}),
    (69, {settings.Language.ENGLISH: F'Changing the authentication key for low security', settings.Language.RUSSIAN: F'Изменение ключа аутентификации для низкой секретности'}),
    (70, {settings.Language.ENGLISH: F'Clearing Initiative exit flags', settings.Language.RUSSIAN: F'Очистка флагов инициативного выхода'}),
    (71, {settings.Language.ENGLISH: F'Changing the timeout for an HDLC connection', settings.Language.RUSSIAN: F'Изменение таймаута для HDLC-соединения'}),
    (72, {settings.Language.ENGLISH: F'Changing the hours of heavy loads', settings.Language.RUSSIAN: F'Изменение часов болъших нагрузок'}),
    (73, {settings.Language.ENGLISH: F'Changing the maximum monitoring hours', settings.Language.RUSSIAN: F'Изменение часов контроля максимума'}),
    (74, {settings.Language.ENGLISH: F'Changing the connection scheme', settings.Language.RUSSIAN: F'Изменение схемы подключения'}),
    (75, {settings.Language.ENGLISH: F'Changing the telemetry mode 2', settings.Language.RUSSIAN: F'Изменение режима телеметрии 2'}),
    (76, {settings.Language.ENGLISH: F'Changing the telemetry mode 3', settings.Language.RUSSIAN: F'Изменение режима телеметрии 3'}),
    (77, {settings.Language.ENGLISH: F'Changing the telemetry mode 4', settings.Language.RUSSIAN: F'Изменение режима телеметрии 4'}),
    (78, {settings.Language.ENGLISH: F'Changing the shutdown mode when opening the terminal cover or housing',
         settings.Language.RUSSIAN: F'Изменение режима отключения при вскрытии клеммной крышки или корпуса'}),
    (79, {settings.Language.ENGLISH: F'Changing the active communication profile setting for communication ports',
         settings.Language.RUSSIAN: F'Изменение настройки активного коммуникационного профиля для портов связи'}),
    (80, {settings.Language.ENGLISH: F'Clearing the network quality log on a monthly interval', settings.Language.RUSSIAN: F'Очистка журнала качества сети на месячном интервале'}),
    (81, {settings.Language.ENGLISH: F'Changing the interval for integrating network parameters', settings.Language.RUSSIAN: F'Изменение интервала интегрирования параметров сети'}),
    (82, {settings.Language.ENGLISH: F'Changing the threshold value over time. Reactive power factor (tg <p) average for all phases',
         settings.Language.RUSSIAN: F'Изменение порогового значения по времени. Коэффициент реактивной мощности (tg <р) средний по всем фазам'}),
    (83, {settings.Language.ENGLISH: F'Changing the threshold value over time. Differential current. % of the maximum current value',
         settings.Language.RUSSIAN: F'Изменение порогового значения по времени. Дифференциальньм ток. % от величины наибольшего ток'}),
    (84, {settings.Language.ENGLISH: F'Changing the threshold value over time. The coefficient of asymmetry in the reverse sequence',
         settings.Language.RUSSIAN: F'Изменение порогового значения по времени. Коэффициент несимметрии по обратной последовательности'}),
    (85, {settings.Language.ENGLISH: F'Changing the address or exchange rate (Optical port P1)', settings.Language.RUSSIAN: F'Изменение адреса или скорости обмена (Оптопорт Р1)'}),
    (86, {settings.Language.ENGLISH: F'Changing the address or exchange rate (Port P4)', settings.Language.RUSSIAN: F'Изменение адреса или скорости обмена (Порт Р4)'})))


# for 0.0.96.11.4.255 События внешних воздействий ГОСТ Р 58940—2020 таблица Д.5
external_impact_events = Events((
    (1, {settings.Language.ENGLISH: F'Magnetic field - the beginning', settings.Language.RUSSIAN: F'Магнитное поле - начало'}),
    (2, {settings.Language.ENGLISH: F'Magnetic field - ending', settings.Language.RUSSIAN: F'Магнитное поле - окончание'}),
    (3, {settings.Language.ENGLISH: F'Cleansing the electronic seal cover', settings.Language.RUSSIAN: F'Срабатывание электронной пломбы крышки клеммников'}),
    (4, {settings.Language.ENGLISH: F'Plugging of the electoral seal', settings.Language.RUSSIAN: F'Срабатывание электронной пломбы корпуса'})))


# for 0.0.96.11.5.255 Коммуникационные события ГОСТ Р 58940—2020 таблица Д.6
communication_events = Events((
    (1, {settings.Language.ENGLISH: F'Connection terminated (interface)', settings.Language.RUSSIAN: F'Разорвано соединение (интерфейс)'}),
    (2, {settings.Language.ENGLISH: F'Connection established (interface)', settings.Language.RUSSIAN: F'Установлено соединение (интерфейс)'})))

# for 0.0.96.11.6.255 События контроля доступа ГОСТ Р 58940—2020 таблица Д.7
access_events = Events((
    (1, {settings.Language.ENGLISH: F'Unauthorized access attempt (interface)', settings.Language.RUSSIAN: F'Попытка несанкционированного доступа (интерфейс)'}),
    (2, {settings.Language.ENGLISH: F'Violation of the protocol requirements', settings.Language.RUSSIAN: F'Нарушение требований протокола'})))

# for 0.0.96.11.7.255 Коды событий для журнала самодиагностики ГОСТ Р 58940—2020 таблица Д.8
self_diagnostics_events = Events((
    (1, {settings.Language.ENGLISH: F'Initializing the Device', settings.Language.RUSSIAN: F'Инициализация ПУ'}),
    (2, {settings.Language.ENGLISH: F'Measuring unit-error', settings.Language.RUSSIAN: F'Измерительный блок — ошибка'}),
    (3, {settings.Language.ENGLISH: F'Measuring unit-OK', settings.Language.RUSSIAN: F'Измерительный блок — норма'}),
    (4, {settings.Language.ENGLISH: F'Computing block-error', settings.Language.RUSSIAN: F'Вычислительный блок — ошибка'}),
    (5, {settings.Language.ENGLISH: F'Real-time clock-error', settings.Language.RUSSIAN: F'Часы реального времени — ошибка'}),
    (6, {settings.Language.ENGLISH: F'Real-time clock-OK', settings.Language.RUSSIAN: F'Часы реального времени — норма'}),
    (7, {settings.Language.ENGLISH: F'Power supply unit-error', settings.Language.RUSSIAN: F'Блок питания — ошибка'}),
    (8, {settings.Language.ENGLISH: F'Power supply unit-OK', settings.Language.RUSSIAN: F'Блок питания — норма'}),
    (9, {settings.Language.ENGLISH: F'Display-error', settings.Language.RUSSIAN: F'Дисплей — ошибка'}),
    (10, {settings.Language.ENGLISH: F'Display-OK', settings.Language.RUSSIAN: F'Дисплей — норма'}),
    (11, {settings.Language.ENGLISH: F'Memory block-error', settings.Language.RUSSIAN: F'Блок памяти — ошибка'}),
    (12, {settings.Language.ENGLISH: F'Memory block-OK', settings.Language.RUSSIAN: F'Блок памяти — норма'}),
    (13, {settings.Language.ENGLISH: F'Program memory block-error', settings.Language.RUSSIAN: F'Блок памяти программ — ошибка'}),
    (14, {settings.Language.ENGLISH: F'Program memory block-OK', settings.Language.RUSSIAN: F'Блок памяти программ — норма'}),
    (15, {settings.Language.ENGLISH: F'Core clocking system-error', settings.Language.RUSSIAN: F'Система тактирования ядра — ошибка'}),
    (16, {settings.Language.ENGLISH: F'Core clocking system-OK', settings.Language.RUSSIAN: F'Система тактирования ядра — норма'}),
    (17, {settings.Language.ENGLISH: F'Clock clocking system-error', settings.Language.RUSSIAN: F'Система тактирования часов — ошибка'}),
    (18, {settings.Language.ENGLISH: F'Clock clocking system-OK', settings.Language.RUSSIAN: F'Система тактирования часов — норма'}),
    (19, {settings.Language.ENGLISH: F'Computing unit-OK', settings.Language.RUSSIAN: F'Вычислительный блок — норма'}),))

# for 0.0.96.11.8.255 События по превышению реактивной мощности tg (ф) (тангенс сети) ГОСТ Р 58940—2020 таблица Д.9
reactive_power_events = Events((
    (1, {settings.Language.ENGLISH: F'Exceeding the set threshold is the beginning', settings.Language.RUSSIAN: F'Превышение установленного порога — начало'}),
    (2, {settings.Language.ENGLISH: F'Exceeding the set threshold — end', settings.Language.RUSSIAN: F'Превышение установленного порога — окончание'})))

# for 0.0.96.5.1.255 Статус качества сети (профиль суточных показаний)
power_quality_status_1 = FlagEvents((
    (0b00000001, {settings.Language.ENGLISH: F'Deviation of voltage by more than 10% of the nominal', settings.Language.RUSSIAN: F'Отклонение напряжения более чем на 10% от номинала'}),
    (0b00000010, {settings.Language.ENGLISH: F'Frequency deviation by more than 0.4 Hz from the nominal', settings.Language.RUSSIAN: F'Отклонение частоты более чем на 0,4 Гц от номинала'})))

# for 0.0.96.5.4.255 Статус качества сети (журнал качества сети)
power_quality_status_2 = FlagEvents((
    (0b00000001, {settings.Language.ENGLISH: F'Reducing the voltage of more than 10%', settings.Language.RUSSIAN: F'Снижение напряжения более, чем на 10%'}),
    (0b00001000, {settings.Language.ENGLISH: F'Raising voltage for more than 10%', settings.Language.RUSSIAN: F'Повышение напряжения более, чем на 10%'}),
    (0b00010000, {settings.Language.ENGLISH: F'Reducing the frequency of more than 0.4 Hz', settings.Language.RUSSIAN: F'Снижение частоты более, чем на 0,4 Гц'}),
    (0b00100000, {settings.Language.ENGLISH: F'Reducing the frequency of more than 0.2 Hz', settings.Language.RUSSIAN: F'Снижение частоты более, чем на 0,2 Гц'}),
    (0b01000000, {settings.Language.ENGLISH: F'Increase frequency more than 0.2 Hz', settings.Language.RUSSIAN: F'Увеличение частоты более, чем на 0,2 Гц'}),
    (0b10000000, {settings.Language.ENGLISH: F'Increase frequency more than 0.4 Hz', settings.Language.RUSSIAN: F'Увеличение частоты более, чем на 0,4 Гц'})))


def get_report(self, value=None, *args) -> str:
    """ get value of event code by value(attribute 2) in order to event codes table """
    value = self.value if value is None else value
    if isinstance(value, (cdt.Unsigned, cdt.LongUnsigned, cdt.DoubleLongUnsigned, cdt.Long64Unsigned)):
        try:
            return self.events[value.decode()][settings.get_current_language()]
        except KeyError:
            return F'Unknown event code: {value.decode()}'
    else:
        raise TypeError(F'For object {self} wrong value type, got {value.NAME}')

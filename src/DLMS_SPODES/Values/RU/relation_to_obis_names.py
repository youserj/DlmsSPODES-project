UNKNOWN = "Неизвестное имя класса"
FOR = "для"
BILLING_PERIOD = "За расчетный период"
OVER_VOLTAGE_COUNTER = "Количество перенапряжений"

# DLMS UA 1000-1 Ed 14 7.3.2 Value group B Table 56 
INSTANCE = "экземпляр"
CHANNEL = "канал"
UTILITY_SPECIFIC = "код утилиты"
MANUFACTURER_SPECIFIC = "код производителя"
RESERVED = "зарезервирован"

GLOBAL_METER_RESET_SCRIPT_TABLE = "Таблица сценариев сброса счетчика"
MDI_RESET_END_OF_BILLING_PERIOD_SCRIPT_TABLE = "Таблица сценариев. Конец расчетного периода"
TARIFFICATION_SCRIPT_TABLE = "Таблица сценариев. Тарификация"
SET_OUTPUT_SIGNALS_SCRIPT_TABLE = "Таблица сценариев. Управление выходами"
DISCONNECT_CONTROL_SCRIPT_TABLE = "Таблица сценариев управления отключением"
IMAGE_ACTIVATION_SCRIPT_TABLE = "Таблица сценариев. Активирование перепрошивки"
PUSH_SCRIPT_TABLE = "Таблица сценарие. Инициативный выход"
RU_STOP_FRAME_SCRIPT_TABLE = "Таблица сценариев. Стоп-кадр"
SPECIAL_DAYS_TABLE = "Таблица особых дней"
END_OF_BILLING_PERIOD_SINGLE_ACTION_SCHEDULE = "Расчетный день и час"
DISCONNECT_CONTROL_SINGLE_ACTION_SCHEDULE = "Управление отключением"
IMAGE_ACTIVATION_SINGLE_ACTION_SCHEDULE = "Активирование перепрошивки"
OUTPUT_CONTROL_SINGLE_ACTION_SCHEDULE = "Управление выходами"
PUSH_SINGLE_ACTION_SCHEDULE = "Инициативный выход"
LOAD_PROFILE_CONTROL_SINGLE_ACTION_SCHEDULE = "Load profile control Single action schedule"  # TODO: add RUSSIAN
M_BUS_PROFILE_CONTROL_SINGLE_ACTION_SCHEDULE = "M-Bus profile control Single action schedule"  # TODO: add RUSSIAN
FUNCTION_CONTROL_SINGLE_ACTION_SCHEDULE = "Function control Single action schedule"  # TODO: add RUSSIAN
RU_LIMITER_BY_POWER = "Ограничитель по мощности"
RU_LIMITER_BY_CURRENT = "Ограничитель по току"
RU_LIMITER_BY_VOLTAGE = "Ограничитель по напряжению"
RU_LIMITER_BY_MAGNETIC = "Ограничитель по воздействию магнитного поля"
RU_LIMITER_BY_DIFFERENCE_CURRENT = "Ограничитель по дифференциальному току"
RU_LIMITER_BY_TEMPERATURE = "Ограничитель по превышению температуры"
RU_IEC_HDLC_SETUP_OPTO = "Настройки HDLC Оптопорт"
RU_IEC_HDLC_SETUP_RS_485 = "Настройки HDLC RS-485"
RU_IEC_HDLC_SETUP_GSM = "Настройки HDLC GSM"
CURRENT_ASSOCIATION = "Текущее соединение"
RU_PUBLIC_CLIENT_ASSOCIATION = "Соединение типа <Публичный клиент>"
RU_METER_READER_ASSOCIATION = "Соединение типа <Считыватель показаний>"
RU_UTILITY_SETTING_ASSOCIATION = "Соединение типа <Конфигуратор>"
RU_PUSH = "Соединение типа <Инициативный>"
COSEM_LOGICAL_DEVICE_NAME = "Логическое имя устройства"
INVOCATION_COUNTER = "Счетчик вызовов"
RU_SPECIFIC_PASSPORT_DATA_PROFILE = "Профиль паспортных данных"
RU_DEVICE_FACTORY_NUMBER = "Серийный номер ПУ"
RU_DEVICE_TYPE = "Тип ПУ"
RU_DEVICE_METROLOGICAL_VERSION = "Версия метрологического ПО"
RU_PRODUCER_NAME = "Наименование производителя"
RU_DEVICE_RELEASE_DATE = "Дата выпуска ПУ"
RU_REMOTE_CONSOLE_SERIAL_NUMBER = "Серийный номер пульта"
RU_SPODES_VERSION = "Версия спецификации СПОДЭС"
RU_DEVICE_CONNECTION_SCHEME = "Схема подключения ПУ"
RU_DEVICE_NOT_METROLOGICAL_VERSION = "Версия метрологического не значимого ПО"
RU_DEVICE_ID = "Идентификатор исполнения счетчика"
RU_COUNTER_POINT_DATA = "данные точки учета"
I_O_CONTROL_SIGNAL_OBJECTS_GLOBAL = "Статус входов/выходов"
POWER_QUALITY_STATUS_DAILY = "Статус качества сети (профиль суточных показаний)"
POWER_QUALITY_STATUS_QUALITY_LOG = "Статус качества сети (журнал качества сети)"
TIME_OF_OPERATION = "Время работы ПУ"
RU_DURATION_OF_FAILURE_OVERSTRAIN = "Длительность провала/перенапряжения"
RU_AMBIENT_TEMPERATURE = "Температура"
EVENTS_RELATED_TO_VOLTAGE = "События, связанные с напряжением"
RU_EVENTS_RELATED_TO_CURRENT = "События, связанные с током"
RU_EVENTS_RELATED_TO_LOAD_RELAY = "События, связанные с вкл./выкл. ПУ, коммутации реле нагрузки"
RU_EVENTS_FOR_PROGRAMMING_DEVICE_PARAMETERS = "События программирования параметров ПУ"
RU_EXTERNAL_IMPACT_EVENTS = "События внешних воздействий"
RU_COMMUNICATION_EVENTS = "Коммуникационные события"
RU_ACCESS_CONTROL_EVENTS = "События контроля доступа"
RU_EVENT_CODES_FOR_THE_SELF_DIAGNOSIS_LOG = "Коды событий для журнала самодиагностики"
RU_EVENTS_FOR_EXCEEDING_THE_REACTIVE_POWER = "События по превышению реактивной мощности tg(ф)"
RU_CHANNEL_NUMBER_INTERFACE = "Номер канала (интерфейс)"
RU_CHANGE_LIMIT_LEVEL = "Изменение уровня лимита"
COMMUNICATION_ADDRESS = "Адрес (клиента)"
LOAD_PARAMETERS_PROFILE = "Параметры профиля нагрузки"
# 6.2.4 Other abstract general purpose OBIS codes
# Program entries Table 60
ACTIVE_FIRMWARE_IDENTIFIER = "Активный идентификатор прошивки"
ACTIVE_FIRMWARE_VERSION = "Активная версия прошивки"
ACTIVE_FIRMWARE_SIGNATURE = "Активная подпись прошивки"
# 6.2.13 Register monitor and alarm monitor objects
RU_ALARM_MONITOR_1 = "Монитор событий реле нагрузки"
# 6.2.19 Standard readout profile objects
GENERAL_DISPLAY_READOUT = "Профиль основного дисплея «в Автопрокрутке»"
ALTERNATE_DISPLAY_READOUT = "Профиль основного дисплея «по кнопке»"
# 6.2.44 Parameter changes and calibration objects
PARAMETER_CHANGES_AND_CALIBRATION_0 = "Счетчик коррекций(конфигурирований)"
# 6.2.48 Status of internal control signals objects
RU_LCD_BACKLIGHT_MODE = "Режим подсветки ЖКИ"
# 6.2.59 Event counter objects
RU_RELAY_TRIGGERING_METER_FOR_OPENING = "Счетчик срабатываний реле на размыкание"
# 6.2.62 Meter tamper event related objects
METER_OPEN_EVENT_COUNTER = "Счетчик вскрытий корпуса"
METER_OPEN_EVENT_TIME_STAMP = "Дата последнего вскрытия корпуса"
METER_OPEN_EVENT_DURATION = "Продолжительность последнего вскрытия корпуса"
METER_OPEN_EVENT_CUMULATIVE_DURATION = "Общая продолжительность вскрытия корпуса"
TERMINAL_COVER_OPEN_EVENT_COUNTER = "Счетчик вскрытий крышки клеммников"
TERMINAL_COVER_OPEN_EVENT_TIME_STAMP = "Дата последнего вскрытия крышки клеммников"
TERMINAL_COVER_OPEN_EVENT_DURATION = "Продолжительность последнего вскрытия крышки клеммников"
TERMINAL_COVER_OPEN_EVENT_CUMULATIVE = "Общая продолжительность вскрытия крышки клеммников"
TILT_EVENT_COUNTER = "Счетчик наклона"
TILT_EVENT_TIME_STAMP = "Дата последнего наклона"
TILT_EVENT_DURATION = "Продолжительность последнего наклона"
TILT_EVENT_CUMULATIVE_DURATION = "Общая продолжительность наклона"
STRONG_DC_MAGNETIC_FIELD_EVENT_COUNTER = "Счетчик срабатываний датчика магнитного поля"
STRONG_DC_MAGNETIC_FIELD_EVENT_TIME_STAMP = "Дата последнего воздействия датчика магнитного поля"
STRONG_DC_MAGNETIC_FIELD_EVENT_DURATION = "Продолжительность последнего воздействия магнитного поля"
STRONG_DC_MAGNETIC_FIELD_EVENT_CUMULATIVE_DURATION = "Общая продолжительность воздействия магнитного поля"
SUPPLY_CONTROL_SWITCH_VALVE_TAMPER_EVENT_COUNTER = "Счетчик вмешательства в работу реле/клапана"
SUPPLY_CONTROL_SWITCH_VALVE_TAMPER_EVENT_TIME_STAMP = "Дата последнего в работу реле/клапана"
SUPPLY_CONTROL_SWITCH_VALVE_TAMPER_EVENT_DURATION = "Продолжительность последнего в работу реле/клапана"
SUPPLY_CONTROL_SWITCH_VALVE_TAMPER_EVENT_CUMULATIVE_DURATION = "Общая продолжительность в работу реле/клапана"
METROLOGY_TAMPER_EVENT_COUNTER = "Счетчик вмешательства в метрологическую часть"
METROLOGY_TAMPER_EVENT_TIME_STAMP = "Дата последного вмешательства в метрологическую часть"
METROLOGY_TAMPER_EVENT_DURATION = "Продолжительность последнего вмешательства в метрологическую часть"
METROLOGY_TAMPER_EVENT_CUMULATIVE_DURATION = "Общая продолжительность вмешательства в метрологическую часть"
COMMUNICATION_TAMPER_EVENT_COUNTER = "Счетчик вмешательства в коммуникационный интерфейс"
COMMUNICATION_TAMPER_EVENT_TIME_STAMP = "Дата последного вмешательства в коммуникационный интерфейс"
COMMUNICATION_TAMPER_EVENT_DURATION = "Продолжительность последнего вмешательства в коммуникационный интерфейс"
COMMUNICATION_TAMPER_EVENT_CUMULATIVE_DURATION = "Общая продолжительность вмешательства в коммуникационный интерфейс"
# 6.2.64 Alarm register, Alarm filter and Alarm descriptor objects
RU_ALARM_REGISTER_1 = "Текущее состояние инициативного выхода"
RU_ALARM_FILTER_1 = "Фильтр инициативного выхода"
RU_ALARM_REGISTER_2 = "RU. Регистр тревоги. Реле нагрузки"
RU_ALARM_FILTER_2 = "RU. Фильтр тревоги. Реле нагрузки"
# СТО 34.01-5.1-006-2021 Д.11 Журналы событий и захватываемые параметры
RU_VOLTAGE_LOG = "Журнал напряжений"
RU_CURRENT_LOG = "Журнал токов"
RU_COMMUTATION_LOG = "Журнал включений/выключений"
RU_DATA_CORRECTION_LOG = "Журнал коррекций данных"
RU_EXTERNAL_IMPACT_LOG = "Журнал внешних воздействий"
RU_COMMUNICATION_LOG = "Журнал соединений"
RU_ACCESS_LOG = "Журнал несанкционированного доступа"
RU_SELF_DIAGNOSTIC_LOG = "Журнал самодиагностики"
RU_REACTIVE_POWER_LOG = "Журнал тангенса нагрузки"
RU_QUALITY_POWER_LOG = "Журнал качества энергии"
RU_STATUS_I_O_LOG = "Журнал состояний входов/выходов"
RU_REACTIVE_POWER_LIMIT_LOG = "Журнал выхода тангенса за порог на часовом интервале"
RU_TIME_CORRECTION_LOG = "Журнал коррекции времени"
RU_START_YEAR_LOG = "Журнал на начало года"
RU_QUALITY_FOR_CALCULATION_PERIOD_LOG = "Качества сети на расчётный период"
RU_CONTROL_POWER_LOG = "Контроль мощности"
RU_BATTERY_LOG = "Батареи"
RU_CONTROL_OF_LOAD_RELAY_BLOCKER_LOG = "Контроль блокиратора реле нагрузки"
RU_TEMPERATURE_CONTROL_LOG = "Контроль температуры"
RU_VOLTAGE_DEVIATION_LOG = "«Отклонение напряжения"
RU_LINEAR_VOLTAGE_DEVIATION_LOG = "Отклонение линейного напряжения"
RU_ABNORMAL_NETWORK_SITUATION_LOG = "Нештатная ситуация сети"
RU_VOLTAGE_INTERRUPTION_LOG = "Журнал: прерывание напряжения"
RU_OVER_VOLTAGE_LOG = "Журнал: превышения напряжения"
#
ITE_FIRMWARE_DESCRIPTOR = "ИТЭ. Описание прошивки"
ITE_MAGNETIC_SENSOR_STATUS = "ИТЭ. Магнитный датчик. Статус"
ITE_DISCRETE_OUTPUTS = "ИТЭ. Дискретные выходы. Статус"
ITE_SETTING_OF_RELAY_INCLUSION_PER_DAY = "ИТЭ. Уставка количества включения реле в сутки"
ITE_SETTINGS_MESSAGES = "ИТЭ. Сообщения для настройки"
ITE_CORE_REGISTERS = "ИТЭ. Дамп регистров"
ITE_BLE_ID = "ИТЭ. BLUETOOTHLE Идентификатор"
ITE_BITMAP = "ИТЭ. BITMAP загрузчик экрана"
ITE_ICCID = "ИТЭ. Уникальный серийный номер SIM-карты"
RU_BODY_OPENING_STATE = "Текущее состояние датчика вскрытия корпуса"
RU_TERMINALS_COVER_OPENING_STATE = "Текущее состояние датчика вскрытия крышки клеммников"
RU_MAGNETIC_FIELD_STATE = "Текущее состояние датчика магнитного поля"
RU_HF_FIELD_STATE = "Текущее состояние датчика ВЧ поля"
RU_ELECTRONIC_SEALS_FIXED_STATE_OF_EVENTS = "Зафиксированное состояние событий электронных пломб"
RU_PRESSING_ELECTRONIC_SEALS = "Обжатие электронных пломб"
RU_CLEAR_OF_ELECTRONIC_SEALS_FIXED_STATE = "Очистка зафиксированных событий (магнит и ВЧ поле)"
RU_FIRST_OPENING_TIME_OF_BODY = "Время первого вскрытия электронной пломбы корпуса"
RU_FIRST_OPENING_TIME_OF_TERMINALS_COVER = "Время первого вскрытия электронной пломбы крышки клеммников"

# 7.4. Abstract object
# 7.4.1 General and service entry object - Abstract
RU_RELAY_LOAD_ARBITRATOR = "Арбитр реле нагрузки"
# Communication port log parameters
ITE_USED_COMMUNICATION_INTERFACES = "ИТЭ. Используемые коммуникационные интерфейсы"
# Consumer messages
LOCAL_CONSUMER_MESSAGE = "Потребительское сообщение через локальный информационный порт потребителей"
DISPLAY_CONSUMER_MESSAGE = "Consumer message via the meter display and / or via consumer information port"
# 7.4.5 Data profile objects – Abstract
GSM_DIAGNOSTIC_PROFILE = "Профиль GSM диагностики"
# electricity
# 7.5.1 Value group C codes – Electricity
ACTIVE_POWER_PLUS = "Положительная активная мощность (QI+QIV)"
ACTIVE_POWER_MINUS = "Отрицательная активная мощность (QII+QIII)"
REACTIVE_POWER_PLUS = "Положительная реактивная мощность (QI+QII)"
REACTIVE_POWER_MINUS = "Отрицательная реактивная мощность (QIII+QIV)"
REACTIVE_POWER_QI = "Реактивная мощность QI"
REACTIVE_POWER_QII = "Реактивная мощность QII"
REACTIVE_POWER_QIII = "Реактивная мощность QIII"
REACTIVE_POWER_QIV = "Реактивная мощность QIV"
APPARENT_POWER_PLUS = "Положительная полная мощность (QI+QIV)"
APPARENT_POWER_MINUS = "Отрицательная полная мощность (QII+QIII)"
CURRENT = "Ток"
VOLTAGE = "Напряжение"
POWER_FACTOR = "Фактор мощности"
SUPPLY_FREQUENCY = "Частота сети"
ACTIVE_POWER_ABS_PLUS = "Модуль активной мощности для измерения гармоник (abs(QI+QIV)+abs(QII+QIII))"
ACTIVE_POWER_ABS_MINUS = "Сетевая мощность (abs(QI+QIV)-abs(QII+QIII))"
ACTIVE_POWER_QI = "Активная мощность QI"
ACTIVE_POWER_QII = "Активная мощность QII"
ACTIVE_POWER_QIII = "Активная мощность QIII"
ACTIVE_POWER_QIV = "Активная мощность QIV"
REACTIVE_FACTOR = "Реактивная мощность"
CUMULATIVE = ""
ANY_PHASE = "Межфазное"
ALL_PHASE = "Все фазы"
L1 = "Фаза A"
L2 = "Фаза B"
L3 = "Фаза C"
L1_L2 = "AB"
L2_L3 = "BC"
L3_L1 = "CA"
CUMULATIVE_AMPERE_SQUARED_HOURS = "Удельная энергия потерь в цепях тока"
CUMULATIVE_VOLT_SQUARED_HOURS = "Удельная энергия потерь в силовых трансформаторах"
L0_CURRENT_NEUTRAL = "Ток нулевого провода"
RU_DIFFERENTIAL_CURRENT = "Дифференциальный ток"
PERCENT = "Проценты"
RU_LINEAR_VOLTAGE = "Линейное напряжение"
RU_POSITIVE_DEVIATION = "Положительное отклонение"
RU_NEGATIVE_DEVIATION = "Отрицательное отклонение"
POWER_REACTIVE_FACTOR = "Тангенс нагрузки"
VOLTAGE_ASYMMETRY_COEFFICIENT = "Коэффициент несимметрии напряжений"
# 7.5.2 Value group D codes – Electricity
# 7.5.2.1 Processing of measurement values
BILLING_PERIOD_AVERAGE_SINCE_LAST_RESET = "Среднее значение за расчетный период (с момента последнего сброса)"
CUMULATIVE_MINIMUM_1 = "Общий минимум 1 (с начала эксплуатации)"
CUMULATIVE_MAXIMUM_1 = "Общий максимум 1 (с начала эксплуатации)"
MINIMUM_1 = "Минимум 1 (в течение расчетного периода)"
CURRENT_AVERAGE_1 = "Текущее среднее 1 (из регистров усреднения)"
LAST_AVERAGE_1 = "Последнее среднее 1 (из регистров усреднения)"
MAXIMUM_1 = "Максимум 1 (в течение расчетного периода)"
INSTANTANEOUS_VALUE = "Мгновенное значение"
TIME_INTEGRAL_1 = "Интеграл с начала эксплуатации до текущего момента"
TIME_INTEGRAL_2 = "Интеграл с начала текущего расчетного периода"
TIME_INTEGRAL_3 = "Интеграл превышения величиной установленного порога"
CUMULATIVE_MINIMUM_2 = "Общий минимум 2"
CUMULATIVE_MAXIMUM_2 = "Общий максимум 2"
MINIMUM_2 = "Минимум 2"
CURRENT_AVERAGE_2 = "Текущее среднее 2"
LAST_AVERAGE_2 = "Последнее среднее 2"
MAXIMUM_2 = "Максимум 2"
TIME_INTEGRAL_7 = "Интеграл с начала эксплуатации до конца последнего закончившегося периода записи спериодом 1"
TIME_INTEGRAL_8 = "Интеграл с начала эксплуатации до конца последнего закончившегося периода записи спериодом 2"
TIME_INTEGRAL_9 = "Интеграл с начала текущего расчетного периода до конца последнего периода записи спериодом 1"
TIME_INTEGRAL_10 = "Интеграл с начала текущего расчетного периода до конца последнего периода записи спериодом 2"
CUMULATIVE_MINIMUM_3 = "Общий минимум 3"
CUMULATIVE_MAXIMUM_3 = "Общий максимум 3"
MINIMUM_3 = "Минимум 3"
CURRENT_AVERAGE_3 = "Текущее среднее 3"
LAST_AVERAGE_3 = "Последнее среднее 3"
MAXIMUM_3 = "Максимум 3"
CURRENT_AVERAGE_5 = "Текущее среднее 5"
CURRENT_AVERAGE_6 = "Текущее среднее 6"
TIME_INTEGRAL_5 = "Интеграл от начала текущего периода записи профиля с периодом 1 до текущего момента"
TIME_INTEGRAL_6 = "Интеграл от начала текущего периода записи профиля с периодом 2 до текущего момента"
UNDER_LIMIT_THRESHOLD = "Порог нижнего предела (провала)"
UNDER_LIMIT_OCCURRENCE_COUNTER = "Счетчик провалов"
UNDER_LIMIT_DURATION = "Продолжительность провала"
UNDER_LIMIT_MAGNITUDE = "Величина провала"
OVER_LIMIT_THRESHOLD = "Порог верхнего предела (выброса)"
OVER_LIMIT_OCCURRENCE_COUNTER = "Счетчик выбросов"
OVER_LIMIT_DURATION = "Продолжительность выброса"
OVER_LIMIT_MAGNITUDE = "Величина выброса"
MISSING_THRESHOLD = "Порог пропадания"
MISSING_OCCURRENCE_COUNTER = "Счетчик пропаданий"
MISSING_DURATION = "Продолжительность пропадания"
MISSING_MAGNITUDE = "Величина пропадания"
TIME_THRESHOLD_FOR_UNDER_LIMIT = "Порог времени для фиксации провала"
TIME_THRESHOLD_FOR_OVER_LIMIT = "Порог времени для фиксации выбросов"
TIME_THRESHOLD_FOR_MISSING_MAGNITUDE = "Порог времени для фиксации пропаданий"
CONTRACTED_VALUE = "Согласованное значение"
AVERAGE_VALUE_FOR_RECORDING_INTERVAL_1 = "?"
AVERAGE_VALUE_FOR_RECORDING_INTERVAL_2 = "?"
MINIMUM_FOR_RECORDING_INTERVAL_1 = "Минимум для периода записи 1"
MINIMUM_FOR_RECORDING_INTERVAL_2 = "Минимум для периода записи 2"
MAXIMUM_FOR_RECORDING_INTERVAL_1 = "Максимум для периода записи 1"
MAXIMUM_FOR_RECORDING_INTERVAL_2 = "Максимум для периода записи 2"
TEST_AVERAGE = "Среднее за тест"
CURRENT_AVERAGE_4_FOR_HARMONICS_MEASUREMENT = "Интеграл за время теста"
TIME_INTEGRAL_4 = "?"
RU_TOTAL_DEVIATION_TIME = "Суммарное время отклонения"
# 7.5.3.2 Tariff rates
TOTAL = "Общее"
RATE = "Тариф"
MANUFACTURER_SPECIFIC_CODES = "Код производителя"

# 7.5.3.3 Harmonics
TOTAL_FUND_ALL = "Общее"
HARMONIC = "Гармоника"
THD = "Коэффициент нелинейных искажений(THD)"
TDD = "Отношение мощности высших гармоник к максимальной мощности(TDD)"
ALL_HARMONICS = "Сумма действующих значений всех высших гармоник"
ALL_HARMONICS_TO_NOMINAL_VALUE_RATIO = "Отношение суммы действующих всех высших гармоник к номинальному значению величины"

# 7.5.3.4 Phase angles
ANGLE_FROM = "угол между"
TO = "и"
U_L1 = "Ua"
U_L2 = "Ub"
U_L3 = "Uc"
ERROR = "ошибка"
I_L1 = "Ia"
I_L2 = "Ib"
I_L3 = "Ic"
I_L0 = "N"


# 7.5.5.1 General and service entry objects – Electricity
TRANSFORMER_RATIO = "Коэффициент трансформации"
COMPLETE_COMBINED_ELECTRICITY_ID = "Полный комбинированный электрический ID"


ACTIVE_ENERGY_OUTPUT_PULSE = "Постоянная ПУ для активной энергии"
REACTIVE_ENERGY_OUTPUT_PULSE = "Постоянная ПУ для реактивной энергии"
# Ratios
TRANSFORMER_RATIO_CURRENT = F"{TRANSFORMER_RATIO} по току"
TRANSFORMER_RATIO_VOLTAGE = F"{TRANSFORMER_RATIO} по напряжению"
# Nominal values
NOMINAL_VOLTAGE = "Номинальное напряжение"
NOMINAL_CURRENT = "Номинальный ток"
NOMINAL_FREQUENCY = "Номинальная частота"
MAXIMUM_CURRENT = "Максимальный ток"
REFERENCE_VOLTAGE_FOR_POWER_QUALITY_MEASUREMENT = "Согласованное напряжение электропитания"
REFERENCED_VOLTAGE_FOR_AUX_POWER_SUPPLY = "Опорное напряжение для AUX. электропитания"
# Measurement period- / recording interval- / billing period duration
RECORDING_INTERVAL_1_FOR_LOAD_PROFILE = "Период записи в профиль 1(энергия на интервале)"
RECORDING_INTERVAL_2_FOR_LOAD_PROFILE = "Период записи в профиль 2(параметры сети)"
# Coefficients
TRANSFORMER_MAGNETIC_LOSSES = "Потери в магнитопроводе"
TRANSFORMER_IRON_LOSSES = "Потери в линии"
LINE_RESISTANCE_LOSSES = "Активное сопротивление линии"
LINE_REACTANCE_LOSSES = "Реактивное сопротивление линии"
# 7.5.5.3 List objects – Electricity
RU_MONTHLY_PROFILE = "Ежемесячный профиль"
RU_DAILY_PROFILE = "Ежесуточный профиль"

# 7.5.5.4 Data profile objects – Electricity
RU_LOAD_PROFILE = "Профиль нагрузки"

# Country specific identifiers. Russian profiles
COUNTRY_SPECIFIC_IDENTIFIER = "Страновой идентификатор"
RU_PROFILE_OF_CURRENT_VALUES = "Профиль текущих значений"
RU_SCALE_PROFILE_FOR_THE_MAGAZINE_OF_MONTHLY_INDICATIONS = "Профиль масштаба для журнала ежемесячных  показаний"
RU_SCALE_PROFILE_FOR_A_JOURNAL_OF_DAILY_INDICATION = "Профиль масштаба для журнала ежесуточных показаний"
RU_SCALE_PROFILE_FOR_CURRENT_FRAMES_OF_CURRENT_VALUES = "Профиль масштаба для стоп-кадра текущих значени"
RU_SCALE_PROFILE_FOR_LOAD_PROFILES = "Профиль масштаба для профилей нагрузки"
RU_TELEMECHANICS_PROFILE_FOR_TELEVISION_MEASUREMENTS = "Профиль телеизмерений для задач телемеханики"
RU_TELEMECHANICS_PROFILE_OF_TELEVISION_SIGNALING = "Профиль телесигнализации для задач телемеханики"
# ITE
ITE_CALIBRATION_STATUS = "ИТЭ. Статус калибровки"
ITE_CALIBRATION_APPARENT_POWER = "ИТЭ. Калибровка. Полная мощность"
ITE_CALIBRATION_ACTIVE_POWER = "ИТЭ. Калибровка. Активная мощность"
ITE_CALIBRATION_REACTIVE_POWER = "ИТЭ. Калибровка. Реактивная мощность"
ITE_CALIBRATION_VOLTAGE = "ИТЭ. Калибровка. Напряжение"
ITE_CALIBRATION_CURRENT = "ИТЭ. Калибровка. Ток"
ITE_CALIBRATION_ANGLE = "ИТЭ. Калибровка. Угол"
ITE_DISPLAY_SETTING_1 = "ИТЭ. Настройка экранов №1"
ITE_DISPLAY_SETTING_2 = "ИТЭ. Настройка экранов №2. Подменю общая энергия"
ITE_CLOCK_OFFSET_SETTING = "ИТЭ. Подстройка хода часов"
ITE_FACTORY_SETTING_10 = " ИТЭ. Производственные установки №10"
ITE_FACTORY_SETTING_11 = " ИТЭ. Производственные установки №11"
ITE_FACTORY_SETTING_12 = " ИТЭ. Производственные установки №12"
ITE_FACTORY_SETTING_13 = " ИТЭ. Производственные установки №13"
ITE_FACTORY_SETTING_14 = " ИТЭ. Производственные установки №14"
ITE_FACTORY_SETTING_15 = " ИТЭ. Производственные установки №15"
ITE_FACTORY_SETTING_16 = " ИТЭ. Производственные установки №16"
ITE_FACTORY_SETTING_17 = " ИТЭ. Производственные установки №17"
ITE_FACTORY_SETTING_18 = " ИТЭ. Производственные установки №18"
ITE_FACTORY_SETTING_19 = " ИТЭ. Производственные установки №19"

# RU. Simple OBIS. СТО 34.01-5.1-006-2021.
RU_TOTAL_VOLTAGE_DEVIATION_TIME_FOR_CALCULATED_PERIOD = "Суммарное время отклонения напряжения за расчетный период"
RU_LOAD_LOCK_STATUS = "Блокиратор реле нагрузки"  # 13.5.6

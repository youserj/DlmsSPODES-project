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


class Unit(IntEnum):
    TIME_YEAR = 1
    TIME_MONTH = 2
    TIME_WEEK = 3
    TIME_DAY = 4
    TIME_HOUR = 5
    TIME_MINUTE = 6
    TIME_SECOND = 7
    PHASE_ANGLE_DEGREE = 8
    TEMPERATURE = 9
    LOCAL_CURRENCY = 10
    LENGTH_METRE = 11
    SPEED_METRE_PER_SECOND = 12
    VOLUME_VALUE_CUBIC_METRE = 13
    CORRECTED_VOLUME_CUBIC_METRE = 14
    VOLUME_FLUX_CUBIC_METRE_PER_HOUR = 15
    CORRECTED_VOLUME_FLUX_CUBIC_METRE_PER_HOUR = 16
    VOLUME_FLUX_CUBIC_METRE_PER_DAY = 17
    CORRECTED_VOLUME_FLUX_CUBIC_METRE_PER_DAY = 18
    VOLUME_LITRE = 19
    MASS_KILOGRAM = 20
    FORCE_NEWTON = 21
    ENERGY_NEWTON_METER = 22
    PRESSURE_PASCAL = 23
    PRESSURE_BAR = 24
    ENERGY_JOULE = 25
    THERMAL_POWER_RATE_OF_CHANGE_JOULE_PER_HOUR = 26
    ACTIVE_POWER_WATT = 27
    APPARENT_POWER_VOLT_AMPERE = 28
    REACTIVE_POWER_VAR = 29
    ACTIVE_ENERGY_VALUE_WATT_HOUR = 30
    APPARENT_ENERGY_VALUE_VOLT_AMPERE_HOUR = 31
    REACTIVE_ENERGY_VALUE_VAR_HOUR = 32
    CURRENT_AMPERE = 33
    ELECTRICAL_CHARGE_COULOMB = 34
    VOLTAGE_VOLT = 35
    ELECTRIC_FIELD_STRENGTH_VOLT_PER_METRE = 36
    CAPACITANCE_FARAD = 37
    RESISTANCE_OHM = 38
    RESISTIVITY = 39
    MAGNETIC_FLUX_WEBER = 40
    MAGNETIC_FLUX_DENSITY_TESLA = 41
    MAGNETIC_FIELD_STRENGTH_AMPERE_PER_METRE = 42
    INDUCTANCE_HENRY = 43
    FREQUENCY_HERTZ = 44
    RW_ACTIVE_ENERGY_VALUE = 45
    RB_REACTIVE_ENERGY_VALUE = 46
    RS_APPARENT_ENERGY_VALUE = 47
    VOLT_SQUARED_HOUR_VOLT_SQUARED_HOUR_METER = 48
    AMPERE_SQUARED_HOUR = 49
    MASS_FLUX_KILOGRAM_PER_SECOND = 50
    CONDUCTANCE_SIEMENS = 51
    TEMPERATURE_KELVIN = 52
    RU2H_VOLT_SQUARED_HOUR_METER = 53
    RI2H_AMPERE_SQUARED_HOUR_METER = 54
    RV_METER = 55
    PERCENTAGE = 56
    AMPERE_HOURS = 57
    RESERVED_58 = 58
    RESERVED_59 = 59
    ENERGY_PER_VOLUME = 60
    CALORIFIC_VALUE_WOBBE = 61
    MOLAR_FRACTION_OF_GAS_COMPOSITION_MOLE_PERCENT = 62
    MASS_DENSITY_QUANTITY_OF_MATERIAL = 63
    DYNAMIC_VISCOSITY_PASCAL_SECOND = 64
    SPECIFIC_ENERGY_JOULE_KILOGRAM = 65
    PRESSURE_GRAM_PER_SQUARE_CENTIMETER = 66
    PRESSURE_ATMOSPHERE = 67
    SIGNAL_STRENGTH_MILLIWATT = 70
    SIGNAL_STRENGTH_MICROVOLT = 71
    LOGARITHMIC_UNIT = 72
    RESERVED_73 = 73
    RESERVED_74 = 74
    RESERVED_75 = 75
    RESERVED_76 = 76
    RESERVED_77 = 77
    RESERVED_78 = 78
    RESERVED_79 = 79
    RESERVED_80 = 80
    RESERVED_81 = 81
    RESERVED_82 = 82
    RESERVED_83 = 83
    RESERVED_84 = 84
    RESERVED_85 = 85
    RESERVED_86 = 86
    RESERVED_87 = 87
    RESERVED_88 = 88
    RESERVED_89 = 89
    RESERVED_90 = 90
    RESERVED_91 = 91
    RESERVED_92 = 92
    RESERVED_93 = 93
    RESERVED_94 = 94
    RESERVED_95 = 95
    RESERVED_96 = 96
    RESERVED_97 = 97
    RESERVED_98 = 98
    RESERVED_99 = 99
    RESERVED_100 = 100
    RESERVED_101 = 101
    RESERVED_102 = 102
    RESERVED_103 = 103
    RESERVED_104 = 104
    RESERVED_105 = 105
    RESERVED_106 = 106
    RESERVED_107 = 107
    RESERVED_108 = 108
    RESERVED_109 = 109
    RESERVED_110 = 110
    RESERVED_111 = 111
    RESERVED_112 = 112
    RESERVED_113 = 113
    RESERVED_114 = 114
    RESERVED_115 = 115
    RESERVED_116 = 116
    RESERVED_117 = 117
    RESERVED_118 = 118
    RESERVED_119 = 119
    RESERVED_120 = 120
    RESERVED_121 = 121
    RESERVED_122 = 122
    RESERVED_123 = 123
    RESERVED_124 = 124
    RESERVED_125 = 125
    RESERVED_126 = 126
    RESERVED_127 = 127
    LENGTH_INCH = 128
    LENGTH_FOOT = 129
    MASS_POUND = 130
    TEMPERATURE_FAHRENHEIT = 131
    TEMPERATURE_RANKINE = 132
    AREA_SQUARE_INCH = 133
    AREA_SQUARE_FOOT = 134
    AREA_ACRE = 135
    VOLUME_CUBIC_INCH = 136
    VOLUME_CUBIC_FOOT = 137
    VOLUME_ACRE_FOOT = 138
    VOLUME_GALLON_IMPERIAL = 139
    VOLUME_GALLON_US = 140
    FORCE_POUND_FORCE = 141
    PRESSURE_POUND_FORCE_PER_SQUARE_INCH = 142
    DENSITY_POUND_PER_CUBIC_FOOT = 143
    DYNAMIC_VISCOSITY = 144
    KINEMATIC_VISCOSITY_SQUARE_FOOT_PER_SECOND = 145
    ENERGY_BRITISH_THERMAL_UNIT = 146
    ENERGY_THERM_EU = 147
    ENERGY_THERM_US = 148
    CALORIFIC_VALUE_OF_MASS_LENTHALPY = 149
    CALORIFIC_VALUE_OF_VOLUME_WOBBE = 150
    VOLUME_METER_CUBIC_FEET_RV = 151
    SPEED_FOOT_PER_SECOND = 152
    VOLUME_FLUX_CUBIC_FOOT_PER_SECOND = 153
    VOLUME_FLUX_CUBIC_FOOT_PER_MIN = 154
    VOLUME_FLUX_CUBIC_FOOT_PER_HOUR = 155
    VOLUME_FLUX_CUBIC_FOOT_PER_DAY = 156
    VOLUME_FLUX_ACRE_FOOT_PER_SECOND = 157
    VOLUME_FLUX_ACRE_FOOT_PER_MIN = 158
    VOLUME_FLUX_ACRE_FOOT_PER_HOUR = 159
    VOLUME_FLUX_ACRE_FOOT_PER_DAY = 160
    VOLUME_IMPERIAL_GALLON_METER_RV = 161
    VOLUME_FLUX_IMPERIAL_GALLON_PER_SECOND = 162
    VOLUME_FLUX_IMPERIAL_GALLON_PER_MIN = 163
    VOLUME_FLUX_IMPERIAL_GALLON_PER_HOUR = 164
    VOLUME_FLUX_IMPERIAL_GALLON_PER_DAY = 165
    VOLUME_US_GALLON_RV = 166
    VOLUME_FLUX_US_GALLON_PER_SECOND = 167
    VOLUME_FLUX_US_GALLON_PER_MIN = 168
    VOLUME_FLUX_US_GALLON_PER_HOUR = 169
    VOLUME_FLUX_US_GALLON_PER_DAY = 170
    ENERGY_FLOW_BRITISH_THERMAL_UNIT_PER_SECOND = 171
    ENERGY_FLOW_BRITISH_THERMAL_UNIT_PER_MINUTE = 172
    ENERGY_FLOW_BRITISH_THERMAL_UNIT_PER_HOUR = 173
    ENERGY_FLOW_BRITISH_THERMAL_UNIT_PER_DAY = 174
    RESERVED_175 = 175
    RESERVED_176 = 176
    RESERVED_177 = 177
    RESERVED_178 = 178
    RESERVED_179 = 179
    RESERVED_180 = 180
    RESERVED_181 = 181
    RESERVED_182 = 182
    RESERVED_183 = 183
    RESERVED_184 = 184
    RESERVED_185 = 185
    RESERVED_186 = 186
    RESERVED_187 = 187
    RESERVED_188 = 188
    RESERVED_189 = 189
    RESERVED_190 = 190
    RESERVED_191 = 191
    RESERVED_192 = 192
    RESERVED_193 = 193
    RESERVED_194 = 194
    RESERVED_195 = 195
    RESERVED_196 = 196
    RESERVED_197 = 197
    RESERVED_198 = 198
    RESERVED_199 = 199
    RESERVED_200 = 200
    RESERVED_201 = 201
    RESERVED_202 = 202
    RESERVED_203 = 203
    RESERVED_204 = 204
    RESERVED_205 = 205
    RESERVED_206 = 206
    RESERVED_207 = 207
    RESERVED_208 = 208
    RESERVED_209 = 209
    RESERVED_210 = 210
    RESERVED_211 = 211
    RESERVED_212 = 212
    RESERVED_213 = 213
    RESERVED_214 = 214
    RESERVED_215 = 215
    RESERVED_216 = 216
    RESERVED_217 = 217
    RESERVED_218 = 218
    RESERVED_219 = 219
    RESERVED_220 = 220
    RESERVED_221 = 221
    RESERVED_222 = 222
    RESERVED_223 = 223
    RESERVED_224 = 224
    RESERVED_225 = 225
    RESERVED_226 = 226
    RESERVED_227 = 227
    RESERVED_228 = 228
    RESERVED_229 = 229
    RESERVED_230 = 230
    RESERVED_231 = 231
    RESERVED_232 = 232
    RESERVED_233 = 233
    RESERVED_234 = 234
    RESERVED_235 = 235
    RESERVED_236 = 236
    RESERVED_237 = 237
    RESERVED_238 = 238
    RESERVED_239 = 239
    RESERVED_240 = 240
    RESERVED_241 = 241
    RESERVED_242 = 242
    RESERVED_243 = 243
    RESERVED_244 = 244
    RESERVED_245 = 245
    RESERVED_246 = 246
    RESERVED_247 = 247
    RESERVED_248 = 248
    RESERVED_249 = 249
    RESERVED_250 = 250
    RESERVED_251 = 251
    RESERVED_252 = 252
    EXTENDED_TABLE_OF_UNITS = 253
    OTHER_UNIT = 254
    NO_UNIT_UNITLESS_COUNT = 255


if __name__ == '__main__':
    a = Transmit.OK
    print(a.name, a.value, a.importance)
    print(a.is_ok())
    match a:
        case Transmit.OK: print(a.value)
        case Application.ID_ERROR: print('id')



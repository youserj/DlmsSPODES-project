from COSEMpdu.x680.type import INTEGER
from COSEMpdu.data import (
    NullData, BitString, DoubleLong, DoubleLongUnsigned, OctetString, VisibleString, Utf8String,
    Integer, Long, Unsigned, LongUnsigned, Long64, Long64Unsigned, Enum, Float32, Float64, Structure,
    Data, union2alternatives
)
from ..types.implementations import integers
from typing import Self, TypeAlias
from .cosem_interface_class import ICAuto, ICAElement, ICMElement, Classifier, Cardinality
from ..types.type_alias import Attr
Value: TypeAlias = NullData | BitString | DoubleLong | DoubleLongUnsigned | OctetString | VisibleString | Utf8String | \
    Integer | Long | Unsigned | LongUnsigned | Long64 | Long64Unsigned | Enum | Float32 | Float64


class ValueData(Data[Value]):
    """value"""
    alternatives = union2alternatives(Value)


class Unit(Enum):
    """"""
    # ========================================================================
    # Time Units (1-7)
    # ========================================================================
    YEAR = 1                      # time year
    MONTH = 2                     # time month
    WEEK = 3                      # time week 7*24*60*60 s
    DAY = 4                       # time day 24*60*60 s
    HOUR = 5                      # time hour 60*60 s
    MINUTE = 6                    # time minute 60 s
    SECOND = 7                    # time second s
    # ========================================================================
    # SI Units - Physical Quantities (8-57)
    # ========================================================================
    DEGREE = 8                    # (phase) angle degree rad*180/π
    DEGREE_CELSIUS = 9            # temperature (T) degree-celsius K-273.15
    CURRENCY = 10                 # currency (local)
    METRE = 11                    # length (l) metre m
    METRE_PER_SECOND = 12         # speed (v) metre per second m·s⁻¹
    CUBIC_METRE = 13              # volume (V) cubic metre m³
    CUBIC_METRE_CORRECTED = 14    # corrected volume cubic metre m³
    CUBIC_METRE_PER_HOUR = 15     # volume flux cubic metre per hour m³·h⁻¹
    CUBIC_METRE_PER_HOUR_CORRECTED = 16  # corrected volume flux m³·h⁻¹
    CUBIC_METRE_PER_DAY = 17      # volume flux cubic metre per day m³·d⁻¹
    CUBIC_METRE_PER_DAY_CORRECTED = 18   # corrected volume flux m³·d⁻¹
    LITRE = 19                    # volume litre 10⁻³ m³
    KILOGRAM = 20                 # mass (m) kilogram kg
    NEWTON = 21                   # force (F) newton N = kg·m·s⁻²
    NEWTON_METRE = 22             # energy newton meter J = Nm = Ws
    PASCAL = 23                   # pressure (p) pascal N/m²
    BAR = 24                      # pressure (p) bar 10⁵ N·m⁻²
    JOULE = 25                    # energy joule J = Nm = Ws
    JOULE_PER_HOUR = 26           # thermal power joule per hour J·h⁻¹
    WATT = 27                     # active power (P) watt W = J·s⁻¹
    VOLT_AMPERE = 28              # apparent power (S) volt-ampere VA
    VAR = 29                      # reactive power (Q) var
    WATT_HOUR = 30                # active energy watt-hour Wh
    VOLT_AMPERE_HOUR = 31         # apparent energy volt-ampere-hour VAh
    VAR_HOUR = 32                 # reactive energy var-hour varh
    AMPERE = 33                   # current (I) ampere A
    COULOMB = 34                  # electrical charge (Q) coulomb C = A·s
    VOLT = 35                     # voltage (U) volt V
    VOLT_PER_METRE = 36           # electric field strength (E) V·m⁻¹
    FARAD = 37                    # capacitance (C) farad F = C·V⁻¹
    OHM = 38                      # resistance (R) ohm Ω = V·A⁻¹
    OHM_METRE = 39                # resistivity (ρ) Ω·m
    WEBER = 40                    # magnetic flux (Φ) weber Wb = V·s
    TESLA = 41                    # magnetic flux density (B) tesla T = Wb·m⁻²
    AMPERE_PER_METRE = 42         # magnetic field strength (H) A·m⁻¹
    HENRY = 43                    # inductance (L) henry H = Wb·A⁻¹
    HERTZ = 44                    # frequency (f, ω) hertz Hz = s⁻¹
    PER_WATT_HOUR = 45            # active energy meter constant 1/(Wh)
    PER_VAR_HOUR = 46             # reactive energy meter constant 1/(varh)
    PER_VOLT_AMPERE_HOUR = 47     # apparent energy meter constant 1/(VAh)
    VOLT_SQUARED_HOUR = 48        # volt-squared hour V²·h
    AMPERE_SQUARED_HOUR = 49      # ampere-squared hour A²·h
    KILOGRAM_PER_SECOND = 50      # mass flux kg·s⁻¹
    SIEMENS = 51                  # conductance siemens S = Ω⁻¹
    KELVIN = 52                   # temperature (T) kelvin K
    PER_VOLT_SQUARED_HOUR = 53    # volt-squared hour meter constant 1/(V²·h)
    PER_AMPERE_SQUARED_HOUR = 54  # ampere-squared hour meter constant 1/(A²·h)
    PER_CUBIC_METRE = 55          # meter constant (volume) 1/m³
    PERCENTAGE = 56               # percentage %
    AMPERE_HOUR = 57              # ampere-hours Ah

    # ========================================================================
    # Reserved (58-59)
    # ========================================================================
    RESERVED_58 = 58
    RESERVED_59 = 59

    # ========================================================================
    # SI Units - Additional (60-67)
    # ========================================================================
    WATT_HOUR_PER_CUBIC_METRE = 60   # energy per volume Wh/m³
    JOULE_PER_CUBIC_METRE = 61       # calorific value, wobbe J/m³
    MOL_PERCENT = 62                 # molar fraction of gas composition Mol %
    GRAM_PER_CUBIC_METRE = 63        # mass density g/m³
    PASCAL_SECOND = 64               # dynamic viscosity Pa·s
    JOULE_PER_KILOGRAM = 65          # specific energy J/kg
    GRAM_PER_SQUARE_CENTIMETRE = 66  # pressure g/cm²
    ATMOSPHERE = 67                  # pressure atm

    # ========================================================================
    # Reserved (68-69, 73-127)
    # ========================================================================
    RESERVED_68 = 68
    RESERVED_69 = 69
    # 70-72 are defined below
    RESERVED_73_TO_127 = range(73, 128)

    # ========================================================================
    # Signal Strength (70-72)
    # ========================================================================
    DBM = 70                      # signal strength dB milliwatt
    DB_MICROVOLT = 71             # signal strength dB microvolt
    DB = 72                       # logarithmic unit (ratio)

    # ========================================================================
    # Non-SI Units (128-175)
    # ========================================================================
    INCH = 128                    # length (l) inch
    FOOT = 129                    # length (l) foot
    POUND = 130                   # mass (m) pound
    DEGREE_FAHRENHEIT = 131       # temperature °F
    DEGREE_RANKINE = 132          # temperature °R
    SQUARE_INCH = 133             # area square inch
    SQUARE_FOOT = 134             # area square foot
    ACRE = 135                    # area acre
    CUBIC_INCH = 136              # volume cubic inch
    CUBIC_FOOT = 137              # volume cubic foot
    ACRE_FOOT = 138               # volume acre-foot
    GALLON_IMPERIAL = 139         # volume gallon (imperial)
    GALLON_US = 140               # volume gallon (US)
    POUND_FORCE = 141             # force pound force
    PSI = 142                     # pressure pound force per square inch
    POUND_PER_CUBIC_FOOT = 143    # density pound per cubic foot
    POUND_PER_FOOT_SECOND = 144   # dynamic viscosity lb/(ft·s)
    SQUARE_FOOT_PER_SECOND = 145  # kinematic viscosity ft²/s
    BTU = 146                     # energy British thermal unit
    THERM_EC = 147                # energy Therm (EU)
    THERM_US = 148                # energy Therm (US)
    BTU_PER_POUND = 149           # calorific value of mass Btu/lb
    BTU_PER_CUBIC_FOOT = 150      # calorific value of volume Btu/ft³
    CUBIC_FOOT_METER = 151        # volume meter constant (volume) ft³
    FOOT_PER_SECOND = 152         # speed foot per second
    CUBIC_FOOT_PER_SECOND = 153   # volume flux ft³/s
    CUBIC_FOOT_PER_MINUTE = 154   # volume flux ft³/min
    CUBIC_FOOT_PER_HOUR = 155     # volume flux ft³/h
    CUBIC_FOOT_PER_DAY = 156      # volume flux ft³/d
    ACRE_FOOT_PER_SECOND = 157    # volume flux acre-ft/s
    ACRE_FOOT_PER_MINUTE = 158    # volume flux acre-ft/min
    ACRE_FOOT_PER_HOUR = 159      # volume flux acre-ft/h
    ACRE_FOOT_PER_DAY = 160       # volume flux acre-ft/d
    GALLON_IMPERIAL_METER = 161   # volume meter constant (imperial gallon)
    GALLON_IMPERIAL_PER_SECOND = 162   # volume flux imp gal/s
    GALLON_IMPERIAL_PER_MINUTE = 163   # volume flux imp gal/min
    GALLON_IMPERIAL_PER_HOUR = 164     # volume flux imp gal/h
    GALLON_IMPERIAL_PER_DAY = 165      # volume flux imp gal/d
    GALLON_US_METER = 166         # volume meter constant (US gallon)
    GALLON_US_PER_SECOND = 167    # volume flux US gal/s
    GALLON_US_PER_MINUTE = 168    # volume flux US gal/min
    GALLON_US_PER_HOUR = 169      # volume flux US gal/h
    GALLON_US_PER_DAY = 170       # volume flux US gal/d
    BTU_PER_SECOND = 171          # energy flow Btu/s
    BTU_PER_MINUTE = 172          # energy flow Btu/min
    BTU_PER_HOUR = 173            # energy flow Btu/h
    BTU_PER_DAY = 174             # energy flow Btu/d

    # ========================================================================
    # Reserved (175-252)
    # ========================================================================
    RESERVED_175_TO_252 = range(175, 253)

    # ========================================================================
    # Special Values (253-255)
    # ========================================================================
    EXTENDED_TABLE = 253          # extended table of units
    OTHER = 254                   # other unit
    COUNT = 255                   # no unit, unitless, count


class ScalUnitType(Structure):
    """scal_unit_type"""
    scaler: Integer
    unit: Unit

    @classmethod
    def create(cls, scaler: INTEGER, unit: INTEGER) -> Self:
        return cls.parse((scaler, unit))


class Register(ICAuto):
    """4.3.2 Register"""
    CLASS_ID = 3
    VERSION = 0
    CARDINALITY = Cardinality()
    A_ELEMENTS = (
        ICAElement(2, "value", ValueData, classifier=Classifier.NOT_SPECIFIC),
        ICAElement(3, "scaler_unit", ScalUnitType))
    M_ELEMENTS = ICMElement(1, "reset", integers.IntegerValue0),
    value: Attr
    scaler_unit: Attr

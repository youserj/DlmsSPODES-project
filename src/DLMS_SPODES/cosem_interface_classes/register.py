from typing import Self, TypeAlias, Final
from dataclasses import dataclass
from COSEMpdu.x680 import INTEGER
from COSEMpdu.data import (
    NullData, BitString, DoubleLong, DoubleLongUnsigned, OctetString, VisibleString, Utf8String,
    Integer, Long, Unsigned, LongUnsigned, Long64, Long64Unsigned, Enum, Float32, Float64, Structure,
    Data, union2alternatives
)
from ..types.implementations import integers
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
    YEAR: Final = 1                      # time year
    MONTH: Final = 2                     # time month
    WEEK: Final = 3                      # time week 7*24*60*60 s
    DAY: Final = 4                       # time day 24*60*60 s
    HOUR: Final = 5                      # time hour 60*60 s
    MINUTE: Final = 6                    # time minute 60 s
    SECOND: Final = 7                    # time second s
    # ========================================================================
    # SI Units - Physical Quantities (8-57)
    # ========================================================================
    DEGREE: Final = 8                    # (phase) angle degree rad*180/π
    DEGREE_CELSIUS: Final = 9            # temperature (T) degree-celsius K-273.15
    CURRENCY: Final = 10                 # currency (local)
    METRE: Final = 11                    # length (l) metre m
    METRE_PER_SECOND: Final = 12         # speed (v) metre per second m·s⁻¹
    CUBIC_METRE: Final = 13              # volume (V) cubic metre m³
    CUBIC_METRE_CORRECTED: Final = 14    # corrected volume cubic metre m³
    CUBIC_METRE_PER_HOUR: Final = 15     # volume flux cubic metre per hour m³·h⁻¹
    CUBIC_METRE_PER_HOUR_CORRECTED: Final = 16  # corrected volume flux m³·h⁻¹
    CUBIC_METRE_PER_DAY: Final = 17      # volume flux cubic metre per day m³·d⁻¹
    CUBIC_METRE_PER_DAY_CORRECTED: Final = 18   # corrected volume flux m³·d⁻¹
    LITRE: Final = 19                    # volume litre 10⁻³ m³
    KILOGRAM: Final = 20                 # mass (m) kilogram kg
    NEWTON: Final = 21                   # force (F) newton N = kg·m·s⁻²
    NEWTON_METRE: Final = 22             # energy newton meter J = Nm = Ws
    PASCAL: Final = 23                   # pressure (p) pascal N/m²
    BAR: Final = 24                      # pressure (p) bar 10⁵ N·m⁻²
    JOULE: Final = 25                    # energy joule J = Nm = Ws
    JOULE_PER_HOUR: Final = 26           # thermal power joule per hour J·h⁻¹
    WATT: Final = 27                     # active power (P) watt W = J·s⁻¹
    VOLT_AMPERE: Final = 28              # apparent power (S) volt-ampere VA
    VAR: Final = 29                      # reactive power (Q) var
    WATT_HOUR: Final = 30                # active energy watt-hour Wh
    VOLT_AMPERE_HOUR: Final = 31         # apparent energy volt-ampere-hour VAh
    VAR_HOUR: Final = 32                 # reactive energy var-hour varh
    AMPERE: Final = 33                   # current (I) ampere A
    COULOMB: Final = 34                  # electrical charge (Q) coulomb C = A·s
    VOLT: Final = 35                     # voltage (U) volt V
    VOLT_PER_METRE: Final = 36           # electric field strength (E) V·m⁻¹
    FARAD: Final = 37                    # capacitance (C) farad F = C·V⁻¹
    OHM: Final = 38                      # resistance (R) ohm Ω = V·A⁻¹
    OHM_METRE: Final = 39                # resistivity (ρ) Ω·m
    WEBER: Final = 40                    # magnetic flux (Φ) weber Wb = V·s
    TESLA: Final = 41                    # magnetic flux density (B) tesla T = Wb·m⁻²
    AMPERE_PER_METRE: Final = 42         # magnetic field strength (H) A·m⁻¹
    HENRY: Final = 43                    # inductance (L) henry H = Wb·A⁻¹
    HERTZ: Final = 44                    # frequency (f, ω) hertz Hz = s⁻¹
    PER_WATT_HOUR: Final = 45            # active energy meter constant 1/(Wh)
    PER_VAR_HOUR: Final = 46             # reactive energy meter constant 1/(varh)
    PER_VOLT_AMPERE_HOUR: Final = 47     # apparent energy meter constant 1/(VAh)
    VOLT_SQUARED_HOUR: Final = 48        # volt-squared hour V²·h
    AMPERE_SQUARED_HOUR: Final = 49      # ampere-squared hour A²·h
    KILOGRAM_PER_SECOND: Final = 50      # mass flux kg·s⁻¹
    SIEMENS: Final = 51                  # conductance siemens S = Ω⁻¹
    KELVIN: Final = 52                   # temperature (T) kelvin K
    PER_VOLT_SQUARED_HOUR: Final = 53    # volt-squared hour meter constant 1/(V²·h)
    PER_AMPERE_SQUARED_HOUR: Final = 54  # ampere-squared hour meter constant 1/(A²·h)
    PER_CUBIC_METRE: Final = 55          # meter constant (volume) 1/m³
    PERCENTAGE: Final = 56               # percentage %
    AMPERE_HOUR: Final = 57              # ampere-hours Ah

    # ========================================================================
    # Reserved (58-59)
    # ========================================================================
    # ========================================================================
    # SI Units - Additional (60-67)
    # ========================================================================
    WATT_HOUR_PER_CUBIC_METRE: Final = 60   # energy per volume Wh/m³
    JOULE_PER_CUBIC_METRE: Final = 61       # calorific value, wobbe J/m³
    MOL_PERCENT: Final = 62                 # molar fraction of gas composition Mol %
    GRAM_PER_CUBIC_METRE: Final = 63        # mass density g/m³
    PASCAL_SECOND: Final = 64               # dynamic viscosity Pa·s
    JOULE_PER_KILOGRAM: Final = 65          # specific energy J/kg
    GRAM_PER_SQUARE_CENTIMETRE: Final = 66  # pressure g/cm²
    ATMOSPHERE: Final = 67                  # pressure atm

    # ========================================================================
    # Signal Strength (70-72)
    # ========================================================================
    DBM: Final = 70                      # signal strength dB milliwatt
    DB_MICROVOLT: Final = 71             # signal strength dB microvolt
    DB: Final = 72                       # logarithmic unit (ratio)

    # ========================================================================
    # Non-SI Units (128-175)
    # ========================================================================
    INCH: Final = 128                    # length (l) inch
    FOOT: Final = 129                    # length (l) foot
    POUND: Final = 130                   # mass (m) pound
    DEGREE_FAHRENHEIT: Final = 131       # temperature °F
    DEGREE_RANKINE: Final = 132          # temperature °R
    SQUARE_INCH: Final = 133             # area square inch
    SQUARE_FOOT: Final = 134             # area square foot
    ACRE: Final = 135                    # area acre
    CUBIC_INCH: Final = 136              # volume cubic inch
    CUBIC_FOOT: Final = 137              # volume cubic foot
    ACRE_FOOT: Final = 138               # volume acre-foot
    GALLON_IMPERIAL: Final = 139         # volume gallon (imperial)
    GALLON_US: Final = 140               # volume gallon (US)
    POUND_FORCE: Final = 141             # force pound force
    PSI: Final = 142                     # pressure pound force per square inch
    POUND_PER_CUBIC_FOOT: Final = 143    # density pound per cubic foot
    POUND_PER_FOOT_SECOND: Final = 144   # dynamic viscosity lb/(ft·s)
    SQUARE_FOOT_PER_SECOND: Final = 145  # kinematic viscosity ft²/s
    BTU: Final = 146                     # energy British thermal unit
    THERM_EC: Final = 147                # energy Therm (EU)
    THERM_US: Final = 148                # energy Therm (US)
    BTU_PER_POUND: Final = 149           # calorific value of mass Btu/lb
    BTU_PER_CUBIC_FOOT: Final = 150      # calorific value of volume Btu/ft³
    CUBIC_FOOT_METER: Final = 151        # volume meter constant (volume) ft³
    FOOT_PER_SECOND: Final = 152         # speed foot per second
    CUBIC_FOOT_PER_SECOND: Final = 153   # volume flux ft³/s
    CUBIC_FOOT_PER_MINUTE: Final = 154   # volume flux ft³/min
    CUBIC_FOOT_PER_HOUR: Final = 155     # volume flux ft³/h
    CUBIC_FOOT_PER_DAY: Final = 156      # volume flux ft³/d
    ACRE_FOOT_PER_SECOND: Final = 157    # volume flux acre-ft/s
    ACRE_FOOT_PER_MINUTE: Final = 158    # volume flux acre-ft/min
    ACRE_FOOT_PER_HOUR: Final = 159      # volume flux acre-ft/h
    ACRE_FOOT_PER_DAY: Final = 160       # volume flux acre-ft/d
    GALLON_IMPERIAL_METER: Final = 161   # volume meter constant (imperial gallon)
    GALLON_IMPERIAL_PER_SECOND: Final = 162   # volume flux imp gal/s
    GALLON_IMPERIAL_PER_MINUTE: Final = 163   # volume flux imp gal/min
    GALLON_IMPERIAL_PER_HOUR: Final = 164     # volume flux imp gal/h
    GALLON_IMPERIAL_PER_DAY: Final = 165      # volume flux imp gal/d
    GALLON_US_METER: Final = 166         # volume meter constant (US gallon)
    GALLON_US_PER_SECOND: Final = 167    # volume flux US gal/s
    GALLON_US_PER_MINUTE: Final = 168    # volume flux US gal/min
    GALLON_US_PER_HOUR: Final = 169      # volume flux US gal/h
    GALLON_US_PER_DAY: Final = 170       # volume flux US gal/d
    BTU_PER_SECOND: Final = 171          # energy flow Btu/s
    BTU_PER_MINUTE: Final = 172          # energy flow Btu/min
    BTU_PER_HOUR: Final = 173            # energy flow Btu/h
    BTU_PER_DAY: Final = 174             # energy flow Btu/d
    # ========================================================================
    # Reserved (175-252)
    # ========================================================================
    # ========================================================================
    # Special Values (253-255)
    # ========================================================================
    EXTENDED_TABLE: Final = 253          # extended table of units
    OTHER: Final = 254                   # other unit
    UNITLESS: Final = 255                   # no unit, unitless, count


@dataclass
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

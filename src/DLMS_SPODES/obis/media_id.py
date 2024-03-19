from abc import ABC, abstractmethod
from itertools import count
from ..config_parser import config


_mid_names = config["DLMS"]["media_id_name"]


class MediaId(ABC):
    """DLMS UA 1000-1 Ed 14. Table 53 – OBIS code structure and use of value groups. For Group A"""
    _value: tuple[int]
    _inst = None

    @classmethod
    def from_int(cls, value: int):
        match value:
            case 0:     return Abstract()
            case 1:     return Electricity()
            case 4:     return Hca()
            case 5 | 6: return Thermal()
            case 7:     return Gas()
            case 8 | 9: return Water()
            case 15:    return Other()
            case int(): return Reserved(value)
            case _:     raise ValueError(F"can't create {cls.__name__} from {value=}")

    @abstractmethod
    def __eq__(self, other: int):
        """with integer"""

    @abstractmethod
    def __hash__(self):
        """for hashable"""

    def __str__(self):
        if _mid_names and (t := _mid_names.get(self.__class__.__name__)):
            return t
        else:
            return self.__class__.__name__

    def __init_subclass__(cls, **kwargs):
        def init_hash(self) -> int:
            return self.subgroup

        cls.subgroup = next(sub_group_hash)
        setattr(cls, "__hash__", init_hash)


class OneValueMixin:
    _value: int

    def __eq__(self, other: int):
        return True if other == self._value else False

    def __hash__(self):
        return self._value


class TwoValueMixin:
    _value: tuple[int, ...]

    def __eq__(self, other: int):
        return True if other in self._value else False

    def __hash__(self):
        return self._value[0]


class Singleton:
    _inst: MediaId | None

    def __new__(cls, *args, **kwargs):
        if cls._inst:
            return cls._inst
        else:
            return super().__new__(cls)


sub_group_hash = count()


class Abstract(OneValueMixin, MediaId):
    _value = 0
    __slots__ = tuple()


class Electricity(OneValueMixin, MediaId):
    _value = 1
    __slots__ = tuple()


class Hca(OneValueMixin, MediaId):
    _value = 4
    __slots__ = tuple()


class Thermal(TwoValueMixin, MediaId):
    _value = 5, 6
    __slots__ = tuple()


class Gas(OneValueMixin, MediaId):
    _value = 7
    __slots__ = tuple()


class Water(TwoValueMixin, MediaId):
    _value = 8, 9
    __slots__ = tuple()


class Other(OneValueMixin, MediaId):
    _value = 15
    __slots__ = tuple()


class Reserved(OneValueMixin, MediaId):
    __slots__ = ("_value",)

    def __init__(self, value: int):
        self._value = value


ABSTRACT = Abstract()
ELECTRICITY = Electricity()
HCA = Hca()
THERMAL = Thermal()
GAS = Gas()
WATER = Water()
OTHER_MEDIA = Other()
# abstract


class BillingPeriodValuesResetCounterEntries(Abstract):
    """6_2_3"""


class OtherAbstractGeneralPurposeObisCodes(Abstract):
    """6_2_4"""


class ClockObjects(Abstract):
    """6_2_5"""


class ModemConfigurationAndRelatedObjects(Abstract):
    """6_2_6"""


class ScriptTableObjects(Abstract):
    """6_2_7"""


class SpecialDaysTableObjects(Abstract):
    """6_2_8"""


class ScheduleObjects(Abstract):
    """6_2_9"""


class ActivityCalendarObjects(Abstract):
    """6_2_10"""


class RegisterActivationObjects(Abstract):
    """6_2_11"""


class SingleActionScheduleObjects(Abstract):
    """6_2_12"""


class RegisterObjectsMonitor(Abstract):
    """6_2_13"""


class ParameterMonitorObjects(Abstract):
    """6_2_14"""


class LimiterObjects(Abstract):
    """6_2_15"""


class ArrayManagerObject(Abstract):
    """6_2_16"""


class PaymentMeteringRelatedObjects(Abstract):
    """6_2_17"""


class IecLocalPortSetupObjects(Abstract):
    """6_2_18"""


class StandardReadoutProfileObjects(Abstract):
    """6_2_19"""


class IecHdlcSetupObjects(Abstract):
    """6_2_20"""


class IecTwistedPair1SetupObjects(Abstract):
    """6_2_21"""


class ObjectsRelatedToDataExchangeOverMBus(Abstract):
    """6_2_22"""


class ObjectsToSetUpDataExchangeOverTheInternet(Abstract):
    """6_2_23"""


class ObjectsToSetUpPushSetup(Abstract):
    """6_2_24"""


class ObjectsForSettingUpDataExchangeUsingSFskPlc(Abstract):
    """6_2_25"""


class ObjectsForSettingUpTheIsoIec88022LlcLayer(Abstract):
    """6_2_26"""


class ObjectsForDataExchangeUsingNarrowbandOfdmPlcForPrimeNetworks(Abstract):
    """6_2_27"""


class ObjectsForDataExchangeUsingNarrowBandOfdmPlcForG3PlcNetworks(Abstract):
    """6_2_28"""


class ZigbeeSetupObjects(Abstract):
    """6_2_29"""


class ObjectsForSettingUpAndManagingDataExchangeUsingIsoIec14908PlcNetworks(Abstract):
    """6_2_30"""


class ObjectsForDataExchangeUsingHsPlcIsoIec121391IsoEc121391Networks(Abstract):
    """6_2_31"""


class ObjectsForDataExchangeUsingWiSunNetworks(Abstract):
    """6_2_32"""


class AssociationObjects(Abstract):
    """6_2_33"""


class SapAssignmentObject(Abstract):
    """6_2_34"""


class CosemLogicalDeviceNameObject(Abstract):
    """6_2_35"""


class InformationSecurityRelatedObjects(Abstract):
    """6_2_36"""


class ImageTransferObjects(Abstract):
    """6_2_37"""


class FunctionControlObjects(Abstract):
    """6_2_38"""


class CommunicationPortProtectionObjects(Abstract):
    """6_2_39"""


class UtilityTableObjects(Abstract):
    """6_2_40"""


class CompactDataObjects(Abstract):
    """6_2_41"""


class DeviceIdObjects(Abstract):
    """6_2_42"""


class MeteringPointIdObjects(Abstract):
    """6_2_43"""


class ParameterChangesAndCalibrationObjects(Abstract):
    """6_2_44"""


class IOControlSignalObjects(Abstract):
    """6_2_45"""


class DisconnectControlObjects(Abstract):
    """6_2_46"""


class ArbitratorObjects(Abstract):
    """6_2_47"""


class StatusOfInternalControlSignalsObjects(Abstract):
    """6_2_48"""


class InternalOperatingStatusObjects(Abstract):
    """6_2_49"""


class BatteryEntriesObjects(Abstract):
    """6_2_50"""


class PowerFailureMonitoringObjects(Abstract):
    """6_2_51"""


class OperatingTimeObjects(Abstract):
    """6_2_52"""


class EnvironmentRelatedParametersObjects(Abstract):
    """6_2_53"""


class StatusRegisterObjects(Abstract):
    """6_2_54"""


class EventCodeObjects(Abstract):
    """6_2_55"""


class CommunicationPortLogParameterObjects(Abstract):
    """6_2_56"""


class ConsumerMessageObjects(Abstract):
    """6_2_57"""


class CurrentlyActiveTariffObjects(Abstract):
    """6_2_58"""


class EventCounterObjects(Abstract):
    """6_2_59"""


class ProfileEntryDigitalSignatureObjects(Abstract):
    """6_2_60"""


class ProfileEntryCounterObjects(Abstract):
    """6_2_61"""


class MeterTamperEventRelatedObjects(Abstract):
    """6_2_62"""


class ErrorRegisterObjects(Abstract):
    """6_2_63"""


class AlarmRegisterFilterDescriptorObjects(Abstract):
    """6_2_64"""


class GeneralListObjects(Abstract):
    """6_2_65"""


class EventLogObjects(Abstract):
    """6_2_66"""


class InactiveObjects(Abstract):
    """6_2_67"""


class AbstractManufacturerSpecific(Abstract):
    """7_4_1_0"""


class AbstractDataProfileObjects(Abstract):
    """7_4_5"""


BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES = BillingPeriodValuesResetCounterEntries()
OTHER_ABSTRACT_GENERAL_PURPOSE_OBIS_CODES = OtherAbstractGeneralPurposeObisCodes()
CLOCK_OBJECTS = ClockObjects()
MODEM_CONFIGURATION_AND_RELATED_OBJECTS = ModemConfigurationAndRelatedObjects()
SCRIPT_TABLE_OBJECTS = ScriptTableObjects()
SPECIAL_DAYS_TABLE_OBJECTS = SpecialDaysTableObjects()
SCHEDULE_OBJECTS = ScheduleObjects()
ACTIVITY_CALENDAR_OBJECTS = ActivityCalendarObjects()
REGISTER_ACTIVATION_OBJECTS = RegisterActivationObjects()
SINGLE_ACTION_SCHEDULE_OBJECTS = SingleActionScheduleObjects()
REGISTER_OBJECTS_MONITOR = RegisterObjectsMonitor()
PARAMETER_MONITOR_OBJECTS = ParameterMonitorObjects()
LIMITER_OBJECTS = LimiterObjects()
ARRAY_MANAGER_OBJECT = ArrayManagerObject()
PAYMENT_METERING_RELATED_OBJECTS = PaymentMeteringRelatedObjects()
IEC_LOCAL_PORT_SETUP_OBJECTS = IecLocalPortSetupObjects()
STANDARD_READOUT_PROFILE_OBJECTS = StandardReadoutProfileObjects()
IEC_HDLC_SETUP_OBJECTS = IecHdlcSetupObjects()
IEC_TWISTED_PAIR_1_SETUP_OBJECTS = IecTwistedPair1SetupObjects()
OBJECTS_RELATED_TO_DATA_EXCHANGE_OVER_M_BUS = ObjectsRelatedToDataExchangeOverMBus()
OBJECTS_TO_SET_UP_DATA_EXCHANGE_OVER_THE_INTERNET = ObjectsToSetUpDataExchangeOverTheInternet()
OBJECTS_TO_SET_UP_PUSH_SETUP = ObjectsToSetUpPushSetup()
OBJECTS_FOR_SETTING_UP_DATA_EXCHANGE_USING_S_FSK_PLC = ObjectsForSettingUpDataExchangeUsingSFskPlc()
OBJECTS_FOR_SETTING_UP_THE_ISO_IEC_8802_2_LLC_LAYER = ObjectsForSettingUpTheIsoIec88022LlcLayer()
OBJECTS_FOR_DATA_EXCHANGE_USING_NARROWBAND_OFDM_PLC_FOR_PRIME_NETWORKS = ObjectsForDataExchangeUsingNarrowbandOfdmPlcForPrimeNetworks()
OBJECTS_FOR_DATA_EXCHANGE_USING_NARROW_BAND_OFDM_PLC_FOR_G3_PLC_NETWORKS = ObjectsForDataExchangeUsingNarrowBandOfdmPlcForG3PlcNetworks()
ZIGBEE_SETUP_OBJECTS = ZigbeeSetupObjects()
OBJECTS_FOR_SETTING_UP_AND_MANAGING_DATA_EXCHANGE_USING_ISO_IEC_14908_PLC_NETWORKS = ObjectsForSettingUpAndManagingDataExchangeUsingIsoIec14908PlcNetworks()
OBJECTS_FOR_DATA_EXCHANGE_USING_HS_PLC_ISO_IEC_12139_1_ISO_EC_12139_1_NETWORKS = ObjectsForDataExchangeUsingHsPlcIsoIec121391IsoEc121391Networks()
OBJECTS_FOR_DATA_EXCHANGE_USING_WI_SUN_NETWORKS = ObjectsForDataExchangeUsingWiSunNetworks()
ASSOCIATION_OBJECTS = AssociationObjects()
SAP_ASSIGNMENT_OBJECT = SapAssignmentObject()
COSEM_LOGICAL_DEVICE_NAME_OBJECT = CosemLogicalDeviceNameObject()
INFORMATION_SECURITY_RELATED_OBJECTS = InformationSecurityRelatedObjects()
IMAGE_TRANSFER_OBJECTS = ImageTransferObjects()
FUNCTION_CONTROL_OBJECTS = FunctionControlObjects()
COMMUNICATION_PORT_PROTECTION_OBJECTS = CommunicationPortProtectionObjects()
UTILITY_TABLE_OBJECTS = UtilityTableObjects()
COMPACT_DATA_OBJECTS = CompactDataObjects()
DEVICE_ID_OBJECTS = DeviceIdObjects()
METERING_POINT_ID_OBJECTS = MeteringPointIdObjects()
PARAMETER_CHANGES_AND_CALIBRATION_OBJECTS = ParameterChangesAndCalibrationObjects()
I_O_CONTROL_SIGNAL_OBJECTS = IOControlSignalObjects()
DISCONNECT_CONTROL_OBJECTS = DisconnectControlObjects()
ARBITRATOR_OBJECTS = ArbitratorObjects()
STATUS_OF_INTERNAL_CONTROL_SIGNALS_OBJECTS = StatusOfInternalControlSignalsObjects()
INTERNAL_OPERATING_STATUS_OBJECTS = InternalOperatingStatusObjects()
BATTERY_ENTRIES_OBJECTS = BatteryEntriesObjects()
POWER_FAILURE_MONITORING_OBJECTS = PowerFailureMonitoringObjects()
OPERATING_TIME_OBJECTS = OperatingTimeObjects()
ENVIRONMENT_RELATED_PARAMETERS_OBJECTS = EnvironmentRelatedParametersObjects()
STATUS_REGISTER_OBJECTS = StatusRegisterObjects()
EVENT_CODE_OBJECTS = EventCodeObjects()
COMMUNICATION_PORT_LOG_PARAMETER_OBJECTS = CommunicationPortLogParameterObjects()
CONSUMER_MESSAGE_OBJECTS = ConsumerMessageObjects()
CURRENTLY_ACTIVE_TARIFF_OBJECTS = CurrentlyActiveTariffObjects()
EVENT_COUNTER_OBJECTS = EventCounterObjects()
PROFILE_ENTRY_DIGITAL_SIGNATURE_OBJECTS = ProfileEntryDigitalSignatureObjects()
PROFILE_ENTRY_COUNTER_OBJECTS = ProfileEntryCounterObjects()
METER_TAMPER_EVENT_RELATED_OBJECTS = MeterTamperEventRelatedObjects()
ERROR_REGISTER_OBJECTS = ErrorRegisterObjects()
ALARM_REGISTER_FILTER_DESCRIPTOR_OBJECTS = AlarmRegisterFilterDescriptorObjects()
GENERAL_LIST_OBJECTS = GeneralListObjects()
EVENT_LOG_OBJECTS = EventLogObjects()
INACTIVE_OBJECTS = InactiveObjects()
ABSTRACT_MANUFACTURER_SPECIFIC = AbstractManufacturerSpecific()
ABSTRACT_DATA_PROFILE_OBJECTS = AbstractDataProfileObjects()


# electricity
class IdNumbersElectricity(Electricity):
    """6_3_2"""


class BillingPeriodValuesResetCounterEntriesEl(Electricity):
    """6_3_3"""


class OtherElectricityRelatedGeneralPurposeObjects(Electricity):
    """6_3_4"""


class MeasurementAlgorithm(Electricity):
    """6_3_5"""


class MeteringPointId(Electricity):
    """6_3_6"""


class ElectricityRelatedStatusObjects(Electricity):
    """6_3_7"""


class ListObjectsElectricity(Electricity):
    """6_3_8"""


class ThresholdValues(Electricity):
    """6_3_9"""


class RegisterMonitorObjects(Electricity):
    """6_3_10"""


class ActivePowerPlus(Electricity):
    """7_5_1"""


class ActivePowerMinus(Electricity):
    """7_5_2"""


class ReactivePowerPlus(Electricity):
    """7_5_3"""


class ReactivePowerMinus(Electricity):
    """7_5_4"""


class ReactivePowerQi(Electricity):
    """7_5_4"""


class ReactivePowerQii(Electricity):
    """7_5_5"""


class ReactivePowerQiii(Electricity):
    """7_5_6"""


class ReactivePowerQiv(Electricity):
    """7_5_7"""


class ApparentPowerPlus(Electricity):
    """7_5_8"""


class ApparentPowerMinus(Electricity):
    """7_5_9"""


class Current(Electricity):
    """7_5_10"""


class Voltage(Electricity):
    """7_5_11"""


class PowerFactor(Electricity):
    """7_5_12"""


class SupplyFrequency(Electricity):
    """7_5_13"""


class ActivePowerSum(Electricity):
    """7_5_14"""


class ActivePowerDiff(Electricity):
    """7_5_15"""


class ActivePowerQi(Electricity):
    """7_5_14"""


class ActivePowerQii(Electricity):
    """7_5_15"""


class ActivePowerQiii(Electricity):
    """7_5_16"""


class ActivePowerQiv(Electricity):
    """7_5_17"""


class Angels(Electricity):
    """7_5_18"""


class UnitlessQuantity(Electricity):
    """7_5_19"""


class TransformerAndLineLossQuantities(Electricity):
    """7_5_20"""


class AllPowerFactor(Electricity):
    """7_5_21"""


class L1PowerFactor(Electricity):
    """7_5_22"""


class L2PowerFactor(Electricity):
    """7_5_23"""


class L3PowerFactor(Electricity):
    """7_5_24"""


class AmpereSquaredHours(Electricity):
    """7_5_25"""


class VoltSquaredHours(Electricity):
    """7_5_26"""


class AllCurrent(Electricity):
    """7_5_27"""


class L0Current(Electricity):
    """7_5_28"""


class L0Voltage(Electricity):
    """7_5_29"""


class ConsortiaSpecificIdentifiers(Electricity):
    """7_5_30"""


class CountrySpecificIdentifiers(Electricity):
    """7_5_31"""


class ElectricityGeneralAndServiceEntryObjects(Electricity):
    """7_5_32"""


class ElectricityErrorRegisterObjects(Electricity):
    """7_5_33"""


class ElectricityDataProfileObjects(Electricity):
    """7_5_35"""


class ReactivePowerInductive(Electricity):
    """7_5_36"""


class ReactivePowerCapacitive(Electricity):
    """7_5_37"""


class ElectricityReserved(Electricity):
    """7_5_38"""


class L1L2LineVoltage(Electricity):
    """7_5_39"""


class L2L3LineVoltage(Electricity):
    """7_5_40"""


class L3L1LineVoltage(Electricity):
    """7_5_41"""


class ElectricityManufacturerSpecific(Electricity):
    """7_5_42"""


class ElectricityMeteringPointIdObjects(Electricity):
    """6_2_43"""


BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES_EL = BillingPeriodValuesResetCounterEntriesEl()
ID_NUMBERS_ELECTRICITY = IdNumbersElectricity()
OTHER_ELECTRICITY_RELATED_GENERAL_PURPOSE_OBJECTS = OtherElectricityRelatedGeneralPurposeObjects()
MEASUREMENT_ALGORITHM = MeasurementAlgorithm()
METERING_POINT_ID = MeteringPointId()
ELECTRICITY_RELATED_STATUS_OBJECTS = ElectricityRelatedStatusObjects()
LIST_OBJECTS_ELECTRICITY = ListObjectsElectricity()
THRESHOLD_VALUES = ThresholdValues()
REGISTER_MONITOR_OBJECTS = RegisterMonitorObjects()
ACTIVE_POWER_PLUS = ActivePowerPlus()
ACTIVE_POWER_MINUS = ActivePowerMinus()
REACTIVE_POWER_PLUS = ReactivePowerPlus()
REACTIVE_POWER_MINUS = ReactivePowerMinus()
REACTIVE_POWER_QI = ReactivePowerQi()
REACTIVE_POWER_QII = ReactivePowerQii()
REACTIVE_POWER_QIII = ReactivePowerQiii()
REACTIVE_POWER_QIV = ReactivePowerQiv()
APPARENT_POWER_PLUS = ApparentPowerPlus()
APPARENT_POWER_MINUS = ApparentPowerMinus()
CURRENT = Current()
VOLTAGE = Voltage()
POWER_FACTOR = PowerFactor()
SUPPLY_FREQUENCY = SupplyFrequency()
ACTIVE_POWER_SUM = ActivePowerSum()
ACTIVE_POWER_DIFF = ActivePowerDiff()
ACTIVE_POWER_QI = ActivePowerQi()
ACTIVE_POWER_QII = ActivePowerQii()
ACTIVE_POWER_QIII = ActivePowerQiii()
ACTIVE_POWER_QIV = ActivePowerQiv()
ANGELS = Angels()
UNITLESS_QUANTITY = UnitlessQuantity()
TRANSFORMER_AND_LINE_LOSS_QUANTITIES = TransformerAndLineLossQuantities()
ALL_POWER_FACTOR = AllPowerFactor()
L1_POWER_FACTOR = L1PowerFactor()
L2_POWER_FACTOR = L2PowerFactor()
L3_POWER_FACTOR = L3PowerFactor()
AMPERE_SQUARED_HOURS = AmpereSquaredHours()
VOLT_SQUARED_HOURS = VoltSquaredHours()
ALL_CURRENT = AllCurrent()
L0_CURRENT = L0Current()
L0_VOLTAGE = L0Voltage()
CONSORTIA_SPECIFIC_IDENTIFIERS = ConsortiaSpecificIdentifiers()
COUNTRY_SPECIFIC_IDENTIFIERS = CountrySpecificIdentifiers()
ELECTRICITY_GENERAL_AND_SERVICE_ENTRY_OBJECTS = ElectricityGeneralAndServiceEntryObjects()
ELECTRICITY_ERROR_REGISTER_OBJECTS = ElectricityErrorRegisterObjects()
ELECTRICITY_DATA_PROFILE_OBJECTS = ElectricityDataProfileObjects()
REACTIVE_POWER_INDUCTIVE = ReactivePowerInductive()
REACTIVE_POWER_CAPACITIVE = ReactivePowerCapacitive()
ELECTRICITY_RESERVED = ElectricityReserved()
L1_L2_LINE_VOLTAGE = L1L2LineVoltage()
L2_L3_LINE_VOLTAGE = L2L3LineVoltage()
L3_L1_LINE_VOLTAGE = L3L1LineVoltage()
ELECTRICITY_MANUFACTURER_SPECIFIC = ElectricityManufacturerSpecific()
ELECTRICITY_METERING_POINT_ID_OBJECTS = ElectricityMeteringPointIdObjects()

# hca


class IdNumbersHca(Hca):
    """6_4_2"""


class BillingPeriodValuesResetCounterEntriesHca(Hca):
    """6_4_3"""


class GeneralPurposeObjectsHca(Hca):
    """6_4_4"""


class MeasuredValuesHcaConsumption(Hca):
    """6_4_5_1"""


class MeasuredValuesHcaTemperature(Hca):
    """6_4_5_2"""


class ErrorRegisterObjectsHca(Hca):
    """6_4_6"""


class ListObjectsHca(Hca):
    """6_4_7"""


class DataProfileObjectsHca(Hca):
    """6_4_8"""


ID_NUMBERS_HCA = IdNumbersHca()
BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES_HCA = BillingPeriodValuesResetCounterEntriesHca()
GENERAL_PURPOSE_OBJECTS_HCA = GeneralPurposeObjectsHca()
MEASURED_VALUES_HCA_CONSUMPTION = MeasuredValuesHcaConsumption()
MEASURED_VALUES_HCA_TEMPERATURE = MeasuredValuesHcaTemperature()
ERROR_REGISTER_OBJECTS_HCA = ErrorRegisterObjectsHca()
LIST_OBJECTS_HCA = ListObjectsHca()
DATA_PROFILE_OBJECTS_HCA = DataProfileObjectsHca()


# thermal


class IdNumbersThermal(Thermal):
    """6_5_2"""


class BillingPeriodValuesResetCounterEntriesThermal(Thermal):
    """6_5_3"""


class GeneralPurposeObjectsThermal(Thermal):
    """6_5_4"""


class MeasuredValuesThermalConsumption(Thermal):
    """6_5_5_1"""


class MeasuredValuesThermalEnergy(Thermal):
    """6_5_5_2"""


class ErrorRegisterObjectsThermal(Thermal):
    """6_5_6"""


class ListObjectsThermal(Thermal):
    """6_5_7"""


class DataProfileObjectsThermal(Thermal):
    """6_5_8"""


ID_NUMBERS_THERMAL = IdNumbersThermal()
BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES_THERMAL = BillingPeriodValuesResetCounterEntriesThermal()
GENERAL_PURPOSE_OBJECTS_THERMAL = GeneralPurposeObjectsThermal()
MEASURED_VALUES_THERMAL_CONSUMPTION = MeasuredValuesThermalConsumption()
MEASURED_VALUES_THERMAL_ENERGY = MeasuredValuesThermalEnergy()
ERROR_REGISTER_OBJECTS_THERMAL = ErrorRegisterObjectsThermal()
LIST_OBJECTS_THERMAL = ListObjectsThermal()
DATA_PROFILE_OBJECTS_THERMAL = DataProfileObjectsThermal()


# gas
class IdNumbersGas(Gas):
    """6_6_2"""


class BillingPeriodValuesResetCounterEntriesGas(Gas):
    """6_6_3"""


class GeneralPurposeObjectsGas(Gas):
    """6_6_4"""


class InternalOperatingStatusObjectsGas(Gas):
    """6_6_5"""


class MeasuredValuesGasIndexesAndIndexDifferences(Gas):
    """6_6_6_1"""


class MeasuredValuesGasFlowRate(Gas):
    """6_6_6_2"""


class MeasuredValuesGasProcessValues(Gas):
    """6_6_6_3"""


class ConversionRelatedFactorsAndCoefficientsGas(Gas):
    """6_6_7"""


class CalculationMethodsGas(Gas):
    """6_6_8"""


class NaturalGasAnalysis(Gas):
    """6_6_9"""


class ListObjectsGas(Gas):
    """6_6_10"""


ID_NUMBERS_GAS = IdNumbersGas()
BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES_GAS = BillingPeriodValuesResetCounterEntriesGas()
GENERAL_PURPOSE_OBJECTS_GAS = GeneralPurposeObjectsGas()
INTERNAL_OPERATING_STATUS_OBJECTS_GAS = InternalOperatingStatusObjectsGas()
MEASURED_VALUES_GAS_INDEXES_AND_INDEX_DIFFERENCES = MeasuredValuesGasIndexesAndIndexDifferences()
MEASURED_VALUES_GAS_FLOW_RATE = MeasuredValuesGasFlowRate()
MEASURED_VALUES_GAS_PROCESS_VALUES = MeasuredValuesGasProcessValues()
CONVERSION_RELATED_FACTORS_AND_COEFFICIENTS_GAS = ConversionRelatedFactorsAndCoefficientsGas()
CALCULATION_METHODS_GAS = CalculationMethodsGas()
NATURAL_GAS_ANALYSIS = NaturalGasAnalysis()
LIST_OBJECTS_GAS = ListObjectsGas()

# water


class IdNumbersWater(Water):
    """6_7_2"""


class BillingPeriodValuesResetCounterEntriesWater(Water):
    """6_7_3"""


class GeneralPurposeObjectsWater(Water):
    """6_7_4"""


class MeasuredValuesWaterConsumption(Water):
    """6_7_5_1"""


class MeasuredValuesWaterMonitoringValues(Water):
    """6_7_5_2"""


class ErrorRegisterObjectsWater(Water):
    """6_7_6"""


class ListObjectsWater(Water):
    """6_7_7"""


class DataProfileObjectsWater(Water):
    """6_7_8"""


ID_NUMBERS_WATER = IdNumbersWater()
BILLING_PERIOD_VALUES_RESET_COUNTER_ENTRIES_WATER = BillingPeriodValuesResetCounterEntriesWater()
GENERAL_PURPOSE_OBJECTS_WATER = GeneralPurposeObjectsWater()
MEASURED_VALUES_WATER_CONSUMPTION = MeasuredValuesWaterConsumption()
MEASURED_VALUES_WATER_MONITORING_VALUES = MeasuredValuesWaterMonitoringValues()
ERROR_REGISTER_OBJECTS_WATER = ErrorRegisterObjectsWater()
LIST_OBJECTS_WATER = ListObjectsWater()
DATA_PROFILE_OBJECTS_WATER = DataProfileObjectsWater()

"""DLMS UA 1000-1 Ed 14 4.2 Overview of the COSEM interface classes"""
from functools import lru_cache
from enum import IntEnum
from dataclasses import dataclass
from ..types import ut, cdt


@dataclass(frozen=True)
class ClassID:
    DATA = ut.CosemClassId(1)
    REGISTER = ut.CosemClassId(3)
    EXT_REGISTER = ut.CosemClassId(4)
    DEMAND_REGISTER = ut.CosemClassId(5)
    REGISTER_ACTIVATION = ut.CosemClassId(6)
    PROFILE_GENERIC = ut.CosemClassId(7)
    CLOCK = ut.CosemClassId(8)
    SCRIPT_TABLE = ut.CosemClassId(9)
    SCHEDULE = ut.CosemClassId(10)
    SPECIAL_DAYS_TABLE = ut.CosemClassId(11)
    ASSOCIATION_SN = ut.CosemClassId(12)
    ASSOCIATION_LN = ut.CosemClassId(15)
    SAP_ASSIGNMENT = ut.CosemClassId(17)
    IMAGE_TRANSFER = ut.CosemClassId(18)
    IEC_LOCAL_PORT_SETUP = ut.CosemClassId(19)
    ACTIVITY_CALENDAR = ut.CosemClassId(20)
    REGISTER_MONITOR = ut.CosemClassId(21)
    SINGLE_ACTION_SCHEDULE = ut.CosemClassId(22)
    IEC_HDLC_SETUP = ut.CosemClassId(23)
    IEC_TWISTED_PAIR_1_SETUP = ut.CosemClassId(24)
    M_BUS_SLAVE_PORT_SETUP = ut.CosemClassId(25)
    UTILITY_TABLES = ut.CosemClassId(26)
    MODEM_CONFIGURATION = ut.CosemClassId(27)
    AUTO_ANSWER = ut.CosemClassId(28)
    AUTO_CONNECT = ut.CosemClassId(29)
    COSEM_DATA_PROTECTION = ut.CosemClassId(30)
    PUSH_SETUP = ut.CosemClassId(40)
    TCP_UDP_SETUP = ut.CosemClassId(41)
    IPV4_SETUP = ut.CosemClassId(42)
    PRIME_NB_OFDM_PLC_MAC_ADDRESS_SETUP = ut.CosemClassId(43)
    PPP_SETUP = ut.CosemClassId(44)
    GPRS_MODEM_SETUP = ut.CosemClassId(45)
    SMTP_SETUP = ut.CosemClassId(46)
    GSM_DIAGNOSTIC = ut.CosemClassId(47)
    IPV6_SETUP = ut.CosemClassId(48)
    S_FSK_PHY_MAC_SET_UP = ut.CosemClassId(50)
    S_FSK_ACTIVE_INITIATOR = ut.CosemClassId(51)
    S_FSK_MAC_SYNCHRONIZATION_TIMEOUTS = ut.CosemClassId(52)
    S_FSK_MAC_COUNTERS = ut.CosemClassId(53)
    IEC_61334_4_32_LLC_SETUP = ut.CosemClassId(55)
    S_FSK_REPORTING_SYSTEM_LIST = ut.CosemClassId(56)
    ISO_IEC_8802_2_LLC_TYPE_1_SETUP = ut.CosemClassId(57)
    ISO_IEC_8802_2_LLC_TYPE_2_SETUP = ut.CosemClassId(58)
    ISO_IEC_8802_2_LLC_TYPE_3_SETUP = ut.CosemClassId(59)
    REGISTER_TABLE = ut.CosemClassId(61)
    COMPACT_DATA = ut.CosemClassId(62)
    STATUS_MAPPING = ut.CosemClassId(63)
    SECURITY_SETUP = ut.CosemClassId(64)
    PARAMETER_MONITOR = ut.CosemClassId(65)
    SENSOR_MANAGER_INTERFACE_CLASS = ut.CosemClassId(67)
    ARBITRATOR = ut.CosemClassId(68)
    DISCONNECT_CONTROL = ut.CosemClassId(70)
    LIMITER = ut.CosemClassId(71)
    M_BUS_CLIENT = ut.CosemClassId(72)
    WIRELESS_MODE_Q_CHANNEL = ut.CosemClassId(73)
    M_BUS_MASTER_PORT_SETUP = ut.CosemClassId(74)
    DLMS_COSEM_SERVER_M_BUS_PORT_SETUP = ut.CosemClassId(76)
    M_BUS_DIAGNOSTIC = ut.CosemClassId(77)
    _61334_4_32_LLC_SSCS_SETUP = ut.CosemClassId(80)
    PRIME_NB_OFDM_PLC_PHYSICAL_LAYER_COUNTERS = ut.CosemClassId(81)
    PRIME_NB_OFDM_PLC_MAC_SETUP = ut.CosemClassId(82)
    PRIME_NB_OFDM_PLC_MAC_FUNCTIONAL_PARAMETERS = ut.CosemClassId(83)
    PRIME_NB_OFDM_PLC_MAC_COUNTERS = ut.CosemClassId(84)
    PRIME_NB_OFDM_PLC_MAC_NETWORK_ADMINISTRATION_DATA = ut.CosemClassId(85)
    PRIME_NB_OFDM_PLC_APPLICATION_IDENTIFICATION = ut.CosemClassId(86)
    G3_PLC_MAC_LAYER_COUNTERS = ut.CosemClassId(90)
    G3_PLC_MAC_SETUP = ut.CosemClassId(91)
    G3_PLC_MAC_6LOWPAN_ADAPTATION_LAYER_SETUP = ut.CosemClassId(92)
    WI_SUN_SETUP = ut.CosemClassId(95)
    WI_SUN_DIAGNOSTIC = ut.CosemClassId(96)
    RPL_DIAGNOSTIC = ut.CosemClassId(97)
    MPL_DIAGNOSTIC = ut.CosemClassId(98)
    NTP_SETUP = ut.CosemClassId(100)
    ZIGBEE_SAS_STARTUP = ut.CosemClassId(101)
    ZIGBEE_SAS_JOIN = ut.CosemClassId(102)
    ZIGBEE_SAS_APS_FRAGMENTATION = ut.CosemClassId(103)
    ZIGBEE_NETWORK_CONTROL = ut.CosemClassId(104)
    ZIGBEE_TUNNEL_SETUP = ut.CosemClassId(105)
    ACCOUNT = ut.CosemClassId(111)
    CREDIT_INTERFACE_CLASS = ut.CosemClassId(112)
    CHARGE = ut.CosemClassId(113)
    TOKEN_GATEWAY = ut.CosemClassId(115)
    FUNCTION_CONTROL = ut.CosemClassId(122)
    ARRAY_MANAGER = ut.CosemClassId(123)
    COMMUNICATION_PORT_PROTECTION = ut.CosemClassId(124)
    SCHC_LPWAN_SETUP = ut.CosemClassId(126)
    SCHC_LPWAN_DIAGNOSTIC = ut.CosemClassId(127)
    LoRaWAN_SETUP = ut.CosemClassId(128)
    LoRaWAN_DIAGNOSTIC = ut.CosemClassId(129)
    ISO_IEC14908_IDENTIFICATION = ut.CosemClassId(130)
    ISO_IEC14908_PROTOCOL_SETUP = ut.CosemClassId(131)
    ISO_IEC14908_PROTOCOL_STATUS = ut.CosemClassId(132)
    ISO_IEC14908_PROTOCOL_DIAGNOSTIC = ut.CosemClassId(133)
    HS_PLC_ISO_IEC_12139_1_MAC_SETUP = ut.CosemClassId(140)
    HS_PLC_ISO_IEC_12139_1_CPAS_SETUP = ut.CosemClassId(141)
    HS_PLC_ISO_IEC_12139_1_IP_SSAS_SETUP = ut.CosemClassId(142)
    HS_PLC_ISO_IEC_12139_1_HDLC_SSAS_SETUP = ut.CosemClassId(143)
    LTE_MONITORING = ut.CosemClassId(151)
    CLIENT_SETUP = ut.CosemClassId(32767)  # TODO: remove in future

    @classmethod
    @lru_cache(1)
    def get_all_id(cls) -> tuple[int]:
        """return all id container in build-in <int>"""
        return tuple(map(int, filter(lambda it: isinstance(it, ut.CosemClassId), cls.__dict__.values())))


@dataclass(frozen=True)
class Version:
    V0 = cdt.Unsigned(0)
    V1 = cdt.Unsigned(1)
    V2 = cdt.Unsigned(2)
    V3 = cdt.Unsigned(3)


class CountrySpecificIdentifiers(IntEnum):
    FINLAND = 0
    USA = 1
    CANADA = 2
    SERBIA = 3
    RUSSIA = 7
    CZECH_REPUBLIC = 10
    BULGARIA = 11
    CROATIA = 12
    IRELAND = 13
    ISRAEL = 14
    UKRAINE = 15
    YUGOSLAVIA = 16
    EGYPT = 20
    SOUTH_AFRICA = 27
    GREECE = 30
    NETHERLANDS = 31
    BELGIUM = 32
    FRANCE = 33
    SPAIN = 34
    PORTUGAL = 35
    HUNGARY = 36
    LITHUANIA = 37
    SLOVENIA = 38
    ITALY = 39
    ROMANIA = 40
    SWITZERLAND = 41
    SLOVAKIA = 42
    AUSTRIA = 43
    UNITED_KINGDOM = 44
    DENMARK = 45
    SWEDEN = 46
    NORWAY = 47
    POLAND = 48
    GERMANY = 49
    PERU = 51
    SOUGH_KOREA = 52
    CUBA = 53
    ARGENTINA = 54
    BRAZIL = 55
    CHILE = 56
    COLOMBIA = 57
    VENEZUELA = 58
    MALAYSIA = 60
    AUSTRALIA = 61
    INDONESIA = 62
    PHILIPPINES = 63
    NEW_ZEALAND = 64
    SINGAPORE = 65
    THAILAND = 66
    LATVIA = 71
    MOLDOVA = 73
    BELARUS = 75
    JAPAN = 81
    MEXICO = 82
    HONG_KONG = 85
    CHINA = 86
    BOSNIA_AND_HERZEGOVINA = 87
    TURKEY = 90
    INDIA = 91
    PAKISTAN = 92
    SAUDI_ARABIA = 96
    UNITED_ARAB_EMIRATES = 97
    IRAN = 98

    def __str__(self):
        return self.name

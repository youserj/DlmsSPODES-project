"""DLMS UA 1000-1 Ed 14 4.2 Overview of the COSEM interface classes"""
from enum import IntEnum
from dataclasses import dataclass
from ..types import ut, cdt, implementations as impl


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
    ASSOCIATION_SN_CLASS = ut.CosemClassId(12)
    ASSOCIATION_LN_CLASS = ut.CosemClassId(15)
    SAP_ASSIGNMENT = ut.CosemClassId(17)
    IMAGE_TRANSFER = ut.CosemClassId(18)
    IEC_LOCAL_PORT_SETUP = ut.CosemClassId(19)
    ACTIVITY_CALENDAR = ut.CosemClassId(20)
    REGISTER_MONITOR = ut.CosemClassId(21)
    SINGLE_ACTION_SCHEDULE = ut.CosemClassId(22)
    IEC_HDLC_SETUP = ut.CosemClassId(23)
    IEC_TWISTED_PAIR__1__SETUP = ut.CosemClassId(24)
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
    def get_all_id(cls) -> tuple[int]:
        """return all id container in build-in <int>"""
        return tuple(map(int, filter(lambda it: isinstance(it, ut.CosemClassId), cls.__dict__.values())))


@dataclass(frozen=True)
class ClassIDCDT:
    DATA = impl.long_unsigneds.ClassId(int(ClassID.DATA))
    REGISTER = impl.long_unsigneds.ClassId(int(ClassID.REGISTER))
    EXT_REGISTER = impl.long_unsigneds.ClassId(int(ClassID.EXT_REGISTER))
    DEMAND_REGISTER = impl.long_unsigneds.ClassId(int(ClassID.DEMAND_REGISTER))
    REGISTER_ACTIVATION = impl.long_unsigneds.ClassId(int(ClassID.REGISTER_ACTIVATION))
    PROFILE_GENERIC = impl.long_unsigneds.ClassId(int(ClassID.PROFILE_GENERIC))
    CLOCK = impl.long_unsigneds.ClassId(int(ClassID.CLOCK))
    SCRIPT_TABLE = impl.long_unsigneds.ClassId(int(ClassID.SCRIPT_TABLE))
    SCHEDULE = impl.long_unsigneds.ClassId(int(ClassID.SCHEDULE))
    SPECIAL_DAYS_TABLE = impl.long_unsigneds.ClassId(int(ClassID.SPECIAL_DAYS_TABLE))
    ASSOCIATION_SN_CLASS = impl.long_unsigneds.ClassId(int(ClassID.ASSOCIATION_SN_CLASS))
    ASSOCIATION_LN_CLASS = impl.long_unsigneds.ClassId(int(ClassID.ASSOCIATION_LN_CLASS))
    SAP_ASSIGNMENT = impl.long_unsigneds.ClassId(int(ClassID.SAP_ASSIGNMENT))
    IMAGE_TRANSFER = impl.long_unsigneds.ClassId(int(ClassID.IMAGE_TRANSFER))
    IEC_LOCAL_PORT_SETUP = impl.long_unsigneds.ClassId(int(ClassID.IEC_LOCAL_PORT_SETUP))
    ACTIVITY_CALENDAR = impl.long_unsigneds.ClassId(int(ClassID.ACTIVITY_CALENDAR))
    REGISTER_MONITOR = impl.long_unsigneds.ClassId(int(ClassID.REGISTER_MONITOR))
    SINGLE_ACTION_SCHEDULE = impl.long_unsigneds.ClassId(int(ClassID.SINGLE_ACTION_SCHEDULE))
    IEC_HDLC_SETUP = impl.long_unsigneds.ClassId(int(ClassID.IEC_HDLC_SETUP))
    IEC_TWISTED_PAIR__1__SETUP = impl.long_unsigneds.ClassId(int(ClassID.IEC_TWISTED_PAIR__1__SETUP))
    M_BUS_SLAVE_PORT_SETUP = impl.long_unsigneds.ClassId(int(ClassID.M_BUS_SLAVE_PORT_SETUP))
    UTILITY_TABLES = impl.long_unsigneds.ClassId(int(ClassID.UTILITY_TABLES))
    MODEM_CONFIGURATION = impl.long_unsigneds.ClassId(int(ClassID.MODEM_CONFIGURATION))
    AUTO_ANSWER = impl.long_unsigneds.ClassId(int(ClassID.AUTO_ANSWER))
    AUTO_CONNECT = impl.long_unsigneds.ClassId(int(ClassID.AUTO_CONNECT))
    COSEM_DATA_PROTECTION = impl.long_unsigneds.ClassId(int(ClassID.COSEM_DATA_PROTECTION))
    PUSH_SETUP = impl.long_unsigneds.ClassId(int(ClassID.PUSH_SETUP))
    TCP_UDP_SETUP = impl.long_unsigneds.ClassId(int(ClassID.TCP_UDP_SETUP))
    IPV4_SETUP = impl.long_unsigneds.ClassId(int(ClassID.IPV4_SETUP))
    PRIME_NB_OFDM_PLC_MAC_ADDRESS_SETUP = impl.long_unsigneds.ClassId(int(ClassID.PRIME_NB_OFDM_PLC_MAC_ADDRESS_SETUP))
    PPP_SETUP = impl.long_unsigneds.ClassId(int(ClassID.PPP_SETUP))
    GPRS_MODEM_SETUP = impl.long_unsigneds.ClassId(int(ClassID.GPRS_MODEM_SETUP))
    SMTP_SETUP = impl.long_unsigneds.ClassId(int(ClassID.SMTP_SETUP))
    GSM_DIAGNOSTIC = impl.long_unsigneds.ClassId(int(ClassID.GSM_DIAGNOSTIC))
    IPV6_SETUP = impl.long_unsigneds.ClassId(int(ClassID.IPV6_SETUP))
    S_FSK_PHY_MAC_SET_UP = impl.long_unsigneds.ClassId(int(ClassID.S_FSK_PHY_MAC_SET_UP))
    S_FSK_ACTIVE_INITIATOR = impl.long_unsigneds.ClassId(int(ClassID.S_FSK_ACTIVE_INITIATOR))
    S_FSK_MAC_SYNCHRONIZATION_TIMEOUTS = impl.long_unsigneds.ClassId(int(ClassID.S_FSK_MAC_SYNCHRONIZATION_TIMEOUTS))
    S_FSK_MAC_COUNTERS = impl.long_unsigneds.ClassId(int(ClassID.S_FSK_MAC_COUNTERS))
    IEC_61334_4_32_LLC_SETUP = impl.long_unsigneds.ClassId(int(ClassID.IEC_61334_4_32_LLC_SETUP))
    S_FSK_REPORTING_SYSTEM_LIST = impl.long_unsigneds.ClassId(int(ClassID.S_FSK_REPORTING_SYSTEM_LIST))
    ISO_IEC_8802_2_LLC_TYPE_1_SETUP = impl.long_unsigneds.ClassId(int(ClassID.ISO_IEC_8802_2_LLC_TYPE_1_SETUP))
    ISO_IEC_8802_2_LLC_TYPE_2_SETUP = impl.long_unsigneds.ClassId(int(ClassID.ISO_IEC_8802_2_LLC_TYPE_2_SETUP))
    ISO_IEC_8802_2_LLC_TYPE_3_SETUP = impl.long_unsigneds.ClassId(int(ClassID.ISO_IEC_8802_2_LLC_TYPE_3_SETUP))
    REGISTER_TABLE = impl.long_unsigneds.ClassId(int(ClassID.REGISTER_TABLE))
    COMPACT_DATA = impl.long_unsigneds.ClassId(int(ClassID.COMPACT_DATA))
    STATUS_MAPPING = impl.long_unsigneds.ClassId(int(ClassID.STATUS_MAPPING))
    SECURITY_SETUP = impl.long_unsigneds.ClassId(int(ClassID.SECURITY_SETUP))
    PARAMETER_MONITOR = impl.long_unsigneds.ClassId(int(ClassID.PARAMETER_MONITOR))
    SENSOR_MANAGER_INTERFACE_CLASS = impl.long_unsigneds.ClassId(int(ClassID.SENSOR_MANAGER_INTERFACE_CLASS))
    ARBITRATOR = impl.long_unsigneds.ClassId(int(ClassID.ARBITRATOR))
    DISCONNECT_CONTROL = impl.long_unsigneds.ClassId(int(ClassID.DISCONNECT_CONTROL))
    LIMITER = impl.long_unsigneds.ClassId(int(ClassID.LIMITER))
    M_BUS_CLIENT = impl.long_unsigneds.ClassId(int(ClassID.M_BUS_CLIENT))
    WIRELESS_MODE_Q_CHANNEL = impl.long_unsigneds.ClassId(int(ClassID.WIRELESS_MODE_Q_CHANNEL))
    M_BUS_MASTER_PORT_SETUP = impl.long_unsigneds.ClassId(int(ClassID.M_BUS_MASTER_PORT_SETUP))
    DLMS_COSEM_SERVER_M_BUS_PORT_SETUP = impl.long_unsigneds.ClassId(int(ClassID.DLMS_COSEM_SERVER_M_BUS_PORT_SETUP))
    M_BUS_DIAGNOSTIC = impl.long_unsigneds.ClassId(int(ClassID.M_BUS_DIAGNOSTIC))
    _61334_4_32_LLC_SSCS_SETUP = impl.long_unsigneds.ClassId(int(ClassID._61334_4_32_LLC_SSCS_SETUP))
    PRIME_NB_OFDM_PLC_PHYSICAL_LAYER_COUNTERS = impl.long_unsigneds.ClassId(int(ClassID.PRIME_NB_OFDM_PLC_PHYSICAL_LAYER_COUNTERS))
    PRIME_NB_OFDM_PLC_MAC_SETUP = impl.long_unsigneds.ClassId(int(ClassID.PRIME_NB_OFDM_PLC_MAC_SETUP))
    PRIME_NB_OFDM_PLC_MAC_FUNCTIONAL_PARAMETERS = impl.long_unsigneds.ClassId(int(ClassID.PRIME_NB_OFDM_PLC_MAC_FUNCTIONAL_PARAMETERS))
    PRIME_NB_OFDM_PLC_MAC_COUNTERS = impl.long_unsigneds.ClassId(int(ClassID.PRIME_NB_OFDM_PLC_MAC_COUNTERS))
    PRIME_NB_OFDM_PLC_MAC_NETWORK_ADMINISTRATION_DATA = impl.long_unsigneds.ClassId(int(ClassID.PRIME_NB_OFDM_PLC_MAC_NETWORK_ADMINISTRATION_DATA))
    PRIME_NB_OFDM_PLC_APPLICATION_IDENTIFICATION = impl.long_unsigneds.ClassId(int(ClassID.PRIME_NB_OFDM_PLC_APPLICATION_IDENTIFICATION))
    G3_PLC_MAC_LAYER_COUNTERS = impl.long_unsigneds.ClassId(int(ClassID.G3_PLC_MAC_LAYER_COUNTERS))
    G3_PLC_MAC_SETUP = impl.long_unsigneds.ClassId(int(ClassID.G3_PLC_MAC_SETUP))
    G3_PLC_MAC_6LOWPAN_ADAPTATION_LAYER_SETUP = impl.long_unsigneds.ClassId(int(ClassID.G3_PLC_MAC_6LOWPAN_ADAPTATION_LAYER_SETUP))
    WI_SUN_SETUP = impl.long_unsigneds.ClassId(int(ClassID.WI_SUN_SETUP))
    WI_SUN_DIAGNOSTIC = impl.long_unsigneds.ClassId(int(ClassID.WI_SUN_DIAGNOSTIC))
    RPL_DIAGNOSTIC = impl.long_unsigneds.ClassId(int(ClassID.RPL_DIAGNOSTIC))
    MPL_DIAGNOSTIC = impl.long_unsigneds.ClassId(int(ClassID.MPL_DIAGNOSTIC))
    NTP_SETUP = impl.long_unsigneds.ClassId(int(ClassID.NTP_SETUP))
    ZIGBEE_SAS_STARTUP = impl.long_unsigneds.ClassId(int(ClassID.ZIGBEE_SAS_STARTUP))
    ZIGBEE_SAS_JOIN = impl.long_unsigneds.ClassId(int(ClassID.ZIGBEE_SAS_JOIN))
    ZIGBEE_SAS_APS_FRAGMENTATION = impl.long_unsigneds.ClassId(int(ClassID.ZIGBEE_SAS_APS_FRAGMENTATION))
    ZIGBEE_NETWORK_CONTROL = impl.long_unsigneds.ClassId(int(ClassID.ZIGBEE_NETWORK_CONTROL))
    ZIGBEE_TUNNEL_SETUP = impl.long_unsigneds.ClassId(int(ClassID.ZIGBEE_TUNNEL_SETUP))
    ACCOUNT = impl.long_unsigneds.ClassId(int(ClassID.ACCOUNT))
    CREDIT_INTERFACE_CLASS = impl.long_unsigneds.ClassId(int(ClassID.CREDIT_INTERFACE_CLASS))
    CHARGE = impl.long_unsigneds.ClassId(int(ClassID.CHARGE))
    TOKEN_GATEWAY = impl.long_unsigneds.ClassId(int(ClassID.TOKEN_GATEWAY))
    FUNCTION_CONTROL = impl.long_unsigneds.ClassId(int(ClassID.FUNCTION_CONTROL))
    ARRAY_MANAGER = impl.long_unsigneds.ClassId(int(ClassID.ARRAY_MANAGER))
    COMMUNICATION_PORT_PROTECTION = impl.long_unsigneds.ClassId(int(ClassID.COMMUNICATION_PORT_PROTECTION))
    SCHC_LPWAN_SETUP = impl.long_unsigneds.ClassId(int(ClassID.SCHC_LPWAN_SETUP))
    SCHC_LPWAN_DIAGNOSTIC = impl.long_unsigneds.ClassId(int(ClassID.SCHC_LPWAN_DIAGNOSTIC))
    LoRaWAN_SETUP = impl.long_unsigneds.ClassId(int(ClassID.LoRaWAN_SETUP))
    LoRaWAN_DIAGNOSTIC = impl.long_unsigneds.ClassId(int(ClassID.LoRaWAN_DIAGNOSTIC))
    ISO_IEC14908_IDENTIFICATION = impl.long_unsigneds.ClassId(int(ClassID.ISO_IEC14908_IDENTIFICATION))
    ISO_IEC14908_PROTOCOL_SETUP = impl.long_unsigneds.ClassId(int(ClassID.ISO_IEC14908_PROTOCOL_SETUP))
    ISO_IEC14908_PROTOCOL_STATUS = impl.long_unsigneds.ClassId(int(ClassID.ISO_IEC14908_PROTOCOL_STATUS))
    ISO_IEC14908_PROTOCOL_DIAGNOSTIC = impl.long_unsigneds.ClassId(int(ClassID.ISO_IEC14908_PROTOCOL_DIAGNOSTIC))
    HS_PLC_ISO_IEC_12139_1_MAC_SETUP = impl.long_unsigneds.ClassId(int(ClassID.HS_PLC_ISO_IEC_12139_1_MAC_SETUP))
    HS_PLC_ISO_IEC_12139_1_CPAS_SETUP = impl.long_unsigneds.ClassId(int(ClassID.HS_PLC_ISO_IEC_12139_1_CPAS_SETUP))
    HS_PLC_ISO_IEC_12139_1_IP_SSAS_SETUP = impl.long_unsigneds.ClassId(int(ClassID.HS_PLC_ISO_IEC_12139_1_IP_SSAS_SETUP))
    HS_PLC_ISO_IEC_12139_1_HDLC_SSAS_SETUP = impl.long_unsigneds.ClassId(int(ClassID.HS_PLC_ISO_IEC_12139_1_HDLC_SSAS_SETUP))
    LTE_MONITORING = impl.long_unsigneds.ClassId(int(ClassID.LTE_MONITORING))
    CLIENT_SETUP = impl.long_unsigneds.ClassId(int(ClassID.CLIENT_SETUP))

    @classmethod
    def get_all_id(cls) -> tuple[int]:
        """return all id container in build-in <int>"""
        return tuple(map(int, filter(lambda it: isinstance(it, impl.long_unsigneds.ClassId), cls.__dict__.values())))


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

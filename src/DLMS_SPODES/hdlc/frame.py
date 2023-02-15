from __future__ import annotations
from abc import ABC, abstractmethod
from struct import unpack, pack
from functools import cached_property
from typing import Deque
from enum import IntFlag
import logging

logger = logging.getLogger(__name__)
logger.level = logging.INFO

_FLAG: int = 0x7e


class NotEnoughDataError(Exception):
    """ Not enough data received, need more for parse full Frame """


class FormatDataError(Exception):
    """ Frame format is not Type 3 HDLC """


class Format:
    """ This optional field is present only when using the non-basic frame format. When present, it follows the opening flag sequence. The frame format field is 2 octets in length
    and consists of three subfields referred to as the format type subfield, the segmentation subfield and the frame length subfield. The format of the frame format field is as
    follows, ISO/IEC 13239:2002(E), 4.9 Frame format field, Type 3 :
        Type(4 bits) - Segmentation(1 bit) - Length(11 bit) """
    __content: bytes

    def __init__(self, content: bytes = None,
                 is_segmentation: bool = None,
                 length: int = None):
        if content is not None:
            if len(content) != 2:
                raise ValueError(F'Wrong length Frame format type, must be 2, got {len(content)}')
            else:
                self.__content = content
                if self.type != 0xA:
                    raise FormatDataError(F'Frame format type not according HDLC Type 3, must be 0xA, got {hex(self.type)}')
        else:
            if length.bit_length() <= 13:
                value = length
                if is_segmentation:
                    value |= 0b1010_1_00000000000
                else:
                    value |= 0b1010_0_00000000000
                self.__content = pack('>H', value)
            else:
                raise ValueError(F'Frame length overflow, max be 2048, got {length}')

    @property
    def content(self) -> bytes:
        return self.__content

    @cached_property
    def type(self) -> int:
        """ Must be 0b1010 in first 4 bits """
        return self.__content[0] >> 4

    @cached_property
    def length(self) -> int:
        """ return length of frame. Mask 11bit. """
        return unpack('>H', self.__content)[0] & 0b0000_0_111_11111111

    @cached_property
    def is_segmentation(self) -> bool:
        return bool(self.__content[0] & 0b00001000)

    def __str__(self):
        return F'Type 3: length-{self.length} {"segmentation" if self.is_segmentation else ""}'


class Address:
    __content: bytes

    def __init__(self, content: bytes = None,
                 upper_address: int = None,
                 lower_address: int = None):
        if content is not None:
            if len(content) not in (1, 2, 4):
                raise ValueError(F'Wrong length Frame format type, must be 1, 2 or 4 bytes, got {len(content)}')
            else:
                self.__content = content
        else:
            if lower_address is None:
                if upper_address <= 0x7f:
                    self.__content = pack('B', upper_address << 1 | 1)
                elif upper_address > 0x7f and lower_address is None:
                    self.__content = pack('BB',
                                          upper_address >> 6 & 0b00111110,
                                          upper_address << 1 & 0b11111110) + b'\x00\x01'
                else:
                    raise ValueError(F'Upper address wrong, expected 0..13383, got {upper_address}')
            else:
                if upper_address <= 0x7f and lower_address <= 0x7f:
                    self.__content = pack("BB", upper_address << 1, lower_address << 1 | 1)
                else:
                    self.__content = pack("BBBB",
                                          upper_address >> 6 & 0b11111110,
                                          upper_address << 1 & 0b11111110,
                                          lower_address >> 6 & 0b11111110,
                                          lower_address << 1 & 0b11111110 | 1)

    @classmethod
    def from_frame(cls, value: bytearray) -> Address:
        for it in (0, 1, 3):
            if value[it] % 2 == 1:
                match it:
                    case 0: new = cls(bytes(value[:1])); break
                    case 1: new = cls(bytes(value[:2])); break
                    case 3: new = cls(bytes(value[:4])); break
        else:
            raise ValueError('HDLC source address wrong, not found end bit')
        del value[:len(new)]
        return new

    @property
    def content(self) -> bytes:
        return self.__content

    def __eq__(self, other: Address):
        return self.__content == other.content

    @cached_property
    def upper(self) -> int:
        """ return of upper address with int type """
        if len(self.__content) in (1, 2):
            return self.__content[0] >> 1
        else:
            return (self.__content[0] >> 1)*128 + (self.__content[1] >> 1)

    @cached_property
    def lower(self) -> int | None:
        """ return of lower address with int type """
        if len(self.__content) == 1:
            return None
        elif len(self.__content) == 2:
            return self.__content[1] >> 1
        else:
            return (self.__content[2] >> 1)*128 + (self.__content[3] >> 1)

    def __str__(self):
        return F'{self.upper}{"/"+str(self.lower) if self.lower is not None else ""}'

    def __len__(self):
        return len(self.__content)

    def __hash__(self):
        return int.from_bytes(self.__content, "big")

    def __repr__(self):
        return F"{self.__class__.__name__}(upper_address={self.upper}, lower_address={self.lower})"


_type = ['Information', 'Supervisory', 'Information', 'Unnumbered']


class Control(IntFlag):
    """ ISO/IEC 13239:2002(E).  P/F = poll bit -- primary station or combined station command frame transmissions/final bit -- secondary station or combined station response
    frame transmissions (1 = poll/final) """
    # Information transfer command/ response (I format):
    # 1   2   3   4   5   6   7   8
    # 0 |    N(S)  | P/F |   N(R)
    S0_R0 = 0b000_0_000_0
    S1_R0 = 0b000_0_001_0
    S2_R0 = 0b000_0_010_0
    S3_R0 = 0b000_0_011_0
    S4_R0 = 0b000_0_100_0
    S5_R0 = 0b000_0_101_0
    S6_R0 = 0b000_0_110_0
    S7_R0 = 0b000_0_111_0

    S0_R1 = 0b001_0_000_0
    S1_R1 = 0b001_0_001_0
    S2_R1 = 0b001_0_010_0
    S3_R1 = 0b001_0_011_0
    S4_R1 = 0b001_0_100_0
    S5_R1 = 0b001_0_101_0
    S6_R1 = 0b001_0_110_0
    S7_R1 = 0b001_0_111_0

    S0_R2 = 0b010_0_000_0
    S1_R2 = 0b010_0_001_0
    S2_R2 = 0b010_0_010_0
    S3_R2 = 0b010_0_011_0
    S4_R2 = 0b010_0_100_0
    S5_R2 = 0b010_0_101_0
    S6_R2 = 0b010_0_110_0
    S7_R2 = 0b010_0_111_0

    S0_R3 = 0b011_0_000_0
    S1_R3 = 0b011_0_001_0
    S2_R3 = 0b011_0_010_0
    S3_R3 = 0b011_0_011_0
    S4_R3 = 0b011_0_100_0
    S5_R3 = 0b011_0_101_0
    S6_R3 = 0b011_0_110_0
    S7_R3 = 0b011_0_111_0

    S0_R4 = 0b100_0_000_0
    S1_R4 = 0b100_0_001_0
    S2_R4 = 0b100_0_010_0
    S3_R4 = 0b100_0_011_0
    S4_R4 = 0b100_0_100_0
    S5_R4 = 0b100_0_101_0
    S6_R4 = 0b100_0_110_0
    S7_R4 = 0b100_0_111_0

    S0_R5 = 0b101_0_000_0
    S1_R5 = 0b101_0_001_0
    S2_R5 = 0b101_0_010_0
    S3_R5 = 0b101_0_011_0
    S4_R5 = 0b101_0_100_0
    S5_R5 = 0b101_0_101_0
    S6_R5 = 0b101_0_110_0
    S7_R5 = 0b101_0_111_0

    S0_R6 = 0b110_0_000_0
    S1_R6 = 0b110_0_001_0
    S2_R6 = 0b110_0_010_0
    S3_R6 = 0b110_0_011_0
    S4_R6 = 0b110_0_100_0
    S5_R6 = 0b110_0_101_0
    S6_R6 = 0b110_0_110_0
    S7_R6 = 0b110_0_111_0

    S0_R7 = 0b111_0_000_0
    S1_R7 = 0b111_0_001_0
    S2_R7 = 0b111_0_010_0
    S3_R7 = 0b111_0_011_0
    S4_R7 = 0b111_0_100_0
    S5_R7 = 0b111_0_101_0
    S6_R7 = 0b111_0_110_0
    S7_R7 = 0b111_0_111_0

    S0_R0_PF = 0b000_1_000_0
    S1_R0_PF = 0b000_1_001_0
    S2_R0_PF = 0b000_1_010_0
    S3_R0_PF = 0b000_1_011_0
    S4_R0_PF = 0b000_1_100_0
    S5_R0_PF = 0b000_1_101_0
    S6_R0_PF = 0b000_1_110_0
    S7_R0_PF = 0b000_1_111_0

    S0_R1_PF = 0b001_1_000_0
    S1_R1_PF = 0b001_1_001_0
    S2_R1_PF = 0b001_1_010_0
    S3_R1_PF = 0b001_1_011_0
    S4_R1_PF = 0b001_1_100_0
    S5_R1_PF = 0b001_1_101_0
    S6_R1_PF = 0b001_1_110_0
    S7_R1_PF = 0b001_1_111_0

    S0_R2_PF = 0b010_1_000_0
    S1_R2_PF = 0b010_1_001_0
    S2_R2_PF = 0b010_1_010_0
    S3_R2_PF = 0b010_1_011_0
    S4_R2_PF = 0b010_1_100_0
    S5_R2_PF = 0b010_1_101_0
    S6_R2_PF = 0b010_1_110_0
    S7_R2_PF = 0b010_1_111_0

    S0_R3_PF = 0b011_1_000_0
    S1_R3_PF = 0b011_1_001_0
    S2_R3_PF = 0b011_1_010_0
    S3_R3_PF = 0b011_1_011_0
    S4_R3_PF = 0b011_1_100_0
    S5_R3_PF = 0b011_1_101_0
    S6_R3_PF = 0b011_1_110_0
    S7_R3_PF = 0b011_1_111_0

    S0_R4_PF = 0b100_1_000_0
    S1_R4_PF = 0b100_1_001_0
    S2_R4_PF = 0b100_1_010_0
    S3_R4_PF = 0b100_1_011_0
    S4_R4_PF = 0b100_1_100_0
    S5_R4_PF = 0b100_1_101_0
    S6_R4_PF = 0b100_1_110_0
    S7_R4_PF = 0b100_1_111_0

    S0_R5_PF = 0b101_1_000_0
    S1_R5_PF = 0b101_1_001_0
    S2_R5_PF = 0b101_1_010_0
    S3_R5_PF = 0b101_1_011_0
    S4_R5_PF = 0b101_1_100_0
    S5_R5_PF = 0b101_1_101_0
    S6_R5_PF = 0b101_1_110_0
    S7_R5_PF = 0b101_1_111_0

    S0_R6_PF = 0b110_1_000_0
    S1_R6_PF = 0b110_1_001_0
    S2_R6_PF = 0b110_1_010_0
    S3_R6_PF = 0b110_1_011_0
    S4_R6_PF = 0b110_1_100_0
    S5_R6_PF = 0b110_1_101_0
    S6_R6_PF = 0b110_1_110_0
    S7_R6_PF = 0b110_1_111_0

    S0_R7_PF = 0b111_1_000_0
    S1_R7_PF = 0b111_1_001_0
    S2_R7_PF = 0b111_1_010_0
    S3_R7_PF = 0b111_1_011_0
    S4_R7_PF = 0b111_1_100_0
    S5_R7_PF = 0b111_1_101_0
    S6_R7_PF = 0b111_1_110_0
    S7_R7_PF = 0b111_1_111_0
    # Supervisory commands/ responses (S format): S = supervisory function bit
    # 1   2   3   4   5   6   7   8
    # 1   0   S   S  P/F |   N(R)
    RR_R0 = 0b000_0_00_01
    """ Receive ready sequence=0 """
    RR_R1 = 0b001_0_00_01
    """ Receive ready sequence=1 """
    RR_R2 = 0b010_0_00_01
    """ Receive ready sequence=2 """
    RR_R3 = 0b011_0_00_01
    """ Receive ready sequence=3 """
    RR_R4 = 0b100_0_00_01
    """ Receive ready sequence=4 """
    RR_R5 = 0b101_0_00_01
    """ Receive ready sequence=5 """
    RR_R6 = 0b110_0_00_01
    """ Receive ready sequence=6 """
    RR_R7 = 0b111_0_00_01
    """ Receive ready sequence=7 """

    RR_R0_PF = 0b000_1_00_01
    """ Receive ready sequence=0 """
    RR_R1_PF = 0b001_1_00_01
    """ Receive ready sequence=1 """
    RR_R2_PF = 0b010_1_00_01
    """ Receive ready sequence=2 """
    RR_R3_PF = 0b011_1_00_01
    """ Receive ready sequence=3 """
    RR_R4_PF = 0b100_1_00_01
    """ Receive ready sequence=4 """
    RR_R5_PF = 0b101_1_00_01
    """ Receive ready sequence=5 """
    RR_R6_PF = 0b110_1_00_01
    """ Receive ready sequence=6 """
    RR_R7_PF = 0b111_1_00_01
    """ Receive ready sequence=7 """

    RNR_R0 = 0b000_0_01_01
    RNR_R1 = 0b001_0_01_01
    RNR_R2 = 0b010_0_01_01
    RNR_R3 = 0b011_0_01_01
    RNR_R4 = 0b100_0_01_01
    RNR_R5 = 0b101_0_01_01
    RNR_R6 = 0b110_0_01_01
    RNR_R7 = 0b111_0_01_01

    RNR_R0_PF = 0b000_1_01_01
    RNR_R1_PF = 0b001_1_01_01
    RNR_R2_PF = 0b010_1_01_01
    RNR_R3_PF = 0b011_1_01_01
    RNR_R4_PF = 0b100_1_01_01
    RNR_R5_PF = 0b101_1_01_01
    RNR_R6_PF = 0b110_1_01_01
    RNR_R7_PF = 0b111_1_01_01

    REJ_R0 = 0b000_0_10_01
    REJ_R1 = 0b001_0_10_01
    REJ_R2 = 0b010_0_10_01
    REJ_R3 = 0b011_0_10_01
    REJ_R4 = 0b100_0_10_01
    REJ_R5 = 0b101_0_10_01
    REJ_R6 = 0b110_0_10_01
    REJ_R7 = 0b111_0_10_01

    REJ_R0_PF = 0b000_1_10_01
    REJ_R1_PF = 0b001_1_10_01
    REJ_R2_PF = 0b010_1_10_01
    REJ_R3_PF = 0b011_1_10_01
    REJ_R4_PF = 0b100_1_10_01
    REJ_R5_PF = 0b101_1_10_01
    REJ_R6_PF = 0b110_1_10_01
    REJ_R7_PF = 0b111_1_10_01

    SREJ_R0 = 0b000_0_11_01
    SREJ_R1 = 0b001_0_11_01
    SREJ_R2 = 0b010_0_11_01
    SREJ_R3 = 0b011_0_11_01
    SREJ_R4 = 0b100_0_11_01
    SREJ_R5 = 0b101_0_11_01
    SREJ_R6 = 0b110_0_11_01
    SREJ_R7 = 0b111_0_11_01

    SREJ_R0_PF = 0b000_1_11_01
    SREJ_R1_PF = 0b001_1_11_01
    SREJ_R2_PF = 0b010_1_11_01
    SREJ_R3_PF = 0b011_1_11_01
    SREJ_R4_PF = 0b100_1_11_01
    SREJ_R5_PF = 0b101_1_11_01
    SREJ_R6_PF = 0b110_1_11_01
    SREJ_R7_PF = 0b111_1_11_01

    # Unnumbered commands/ responses (U format): M = modifier function bit
    # 11_MM_P/F_MMM
    UI_PF = 0b000_1_00_11
    """ Unnumbered Information with Poll """
    UI = 0b000_0_00_11
    """ Unnumbered Information with wait """
    XID_PF = 0b101_1_11_11
    """ Exchange identification with Poll. Used to Request/Report capabilities """
    XID = 0b101_0_11_11
    """ Exchange identification with wait. Used to Request/Report capabilities """
    TEST_PF = 0b111_1_00_11
    """ TEST with Poll. Exchange identical information fields for testing """
    TEST = 0b111_0_00_11
    """ TEST with wait. Exchange identical information fields for testing """
    UIH_PF = 0b111_1_11_11
    """ Unnumbered Information with Header check with Poll """
    UIH = 0b111_0_11_11
    """ Unnumbered Information with Header check with wait """

    # command ISO/IEC 13239:2002(E) 5.5.3.3
    # 11_MM_P_MMM
    SNRM_P = 0b100_1_00_11
    """ Set Normal Response Mode with Poll """
    SNRM = 0b100_0_00_11
    """ Set Normal Response Mode with wait """
    SARM_P = 0b000_1_11_11
    """ Set Asynchronous Response Mode with Poll """
    SARM = 0b000_0_11_11
    """ Set Asynchronous Response with wait """
    SABM_P = 0b001_1_11_11
    """ Set Asynchronous Balanced Mode with Poll """
    SABM = 0b001_0_11_11
    """ Set Asynchronous Balanced with wait """
    DISC_P = 0b010_1_00_11
    """ Disconnect with Poll """
    DISC = 0b010_0_00_11
    """ Disconnect with wait """
    SNRME_P = 0b110_1_11_11
    """ Set Normal Response Mode Extended with Poll """
    SNRME = 0b110_0_11_11
    """ Set Normal Response Mode Extended with wait """
    SARME_P = 0b010_1_11_11
    """ Set Asynchronous Response Mode Extended with Poll """
    SARME = 0b010_0_11_11
    """ Set Asynchronous Response Mode Extended with wait """
    SABME_P = 0b011_1_11_11
    """ Set Asynchronous Balanced Mode Extended with Poll """
    SABME = 0b011_0_11_11
    """ Set Asynchronous Balanced Mode Extended with wait """
    UP_P = 0b001_1_00_11
    """ Unnumbered Poll with Poll. Used to solicit control information"""
    UP = 0b001_0_00_11
    """ Unnumbered Poll with wait. Used to solicit control information"""
    SIM_P = 0b000_1_01_11
    """ Set Initialization Mode with Poll """
    SIM = 0b000_0_01_11
    """ Set Initialization Mode with wait """
    SM_P = 0b110_1_00_11
    """ Set Mode with Poll """
    SM = 0b110_0_00_11
    """ Set Mode with wait """
    RSET_P = 0b100_1_11_11
    """ ReSET with Poll. Used for recovery. Resets N(R) but not N(S) """
    RSET = 0b100_0_11_11
    """ ReSET with wait. Used for recovery. Resets N(R) but not N(S) """


    # responses ISO/IEC 13239:2002(E) 5.5.3.4.
    # 11_MM_F_MMM
    UA_F = 0b011_1_00_11
    """ Unnumbered Acknowledgement Final """
    UA = 0b011_0_00_11
    """ Unnumbered Acknowledgement """
    FRMR_F = 0b100_1_01_11
    """ FRaMe Reject Final """
    FRMR = 0b100_0_01_11
    """ FRaMe Reject """
    DM_F = 0b000_1_11_11
    """ Disconnected Mode Final """
    DM = 0b000_0_11_11
    """ Disconnected Mode """
    RD_F = 0b010_1_00_11
    """ Request Disconnect Final. Solicitation for DISC Command """
    RD = 0b010_0_00_11
    """ Request Disconnect. Solicitation for DISC Command """
    RIM_F = 0b000_1_01_11
    """ Request initialization mode Final """
    RIM = 0b000_0_01_11
    """ Request initialization mode """

    def __add__(self, other):
        return Control(self.value + other)

    def __or__(self, other):
        return Control(self.value | other)

    def __and__(self, other):
        return Control(self.value & other)

    def __str__(self):
        return F'{_type[self.value & 0b11]} {self.name}'

    @classmethod
    def from_frame(cls, value: bytearray) -> Control:
        return Control(value.pop(0))

    @property
    def content(self) -> bytes:
        return pack('B', self.value)

    def is_info(self) -> bool:
        """ check by information type """
        return self.value & 0b1 == 0b0

    def is_information(self) -> bool:
        """ check by information in frame """
        return self.is_info() or self == self.UI or self == self.UI_PF

    def is_supervisory(self) -> bool:
        """ check by supervisory type """
        return self.value & 0b11 == 0b01

    def is_unnumbered(self) -> bool:
        """ check by unnumbered type """
        return self.value & 0b11 == 0b11

    def is_receive_ready(self) -> bool:
        return self.value & 0b1111 == 0b0001

    def is_receive_not_ready(self) -> bool:
        return self.value & 0b1111 == 0b0101

    def is_reject(self) -> bool:
        return self.value & 0b1111 == 0b1001

    def is_selective_reject(self) -> bool:
        return self.value & 0b1111 == 0b1101

    @cached_property
    def is_poll(self) -> bool:
        """ 5.4.3 Poll/final (P/F) bit """
        return True if not self.is_unnumbered() and bool(self.value & 0b000_1_00_00) else False

    @classmethod
    def next_send_sequence(cls, value: Control) -> Control:
        return Control(((value & 0xF0 | (value + 0x2) & 0xE) & 0xFF) & 0xFF)
        # value &= 0b1111111_0  # make info from other TODO: is it a gurux bug???
        # if value.is_info():
        #     return Control(value & 0b11110001 | (value + 0x2) & 0b00001110)
        # else:
        #     raise ValueError(F'Increase sender supporting only for information type, got {value}')

    @classmethod
    def next_receiver_sequence(cls, value: Control) -> Control:
        return Control(((value & 0xFF) + 0x20 | 0x10 | value & 0xE) & 0xFF)
        # if value.is_info() or value.is_supervisory():
        #     return Control(value & 0b00011111 | 0x10 | (value + 0x20) & 0b11100000)
        # else:
        #     raise ValueError(F'Increase sender supporting only for information and supervisory type, got {value}')


_CCITT = (0x0000, 0x1189, 0x2312, 0x329B, 0x4624, 0x57AD, 0x6536, 0x74BF, 0x8C48, 0x9DC1, 0xAF5A, 0xBED3, 0xCA6C, 0xDBE5, 0xE97E, 0xF8F7,
          0x1081, 0x0108, 0x3393, 0x221A, 0x56A5, 0x472C, 0x75B7, 0x643E, 0x9CC9, 0x8D40, 0xBFDB, 0xAE52, 0xDAED, 0xCB64, 0xF9FF, 0xE876,
          0x2102, 0x308B, 0x0210, 0x1399, 0x6726, 0x76AF, 0x4434, 0x55BD, 0xAD4A, 0xBCC3, 0x8E58, 0x9FD1, 0xEB6E, 0xFAE7, 0xC87C, 0xD9F5,
          0x3183, 0x200A, 0x1291, 0x0318, 0x77A7, 0x662E, 0x54B5, 0x453C, 0xBDCB, 0xAC42, 0x9ED9, 0x8F50, 0xFBEF, 0xEA66, 0xD8FD, 0xC974,
          0x4204, 0x538D, 0x6116, 0x709F, 0x0420, 0x15A9, 0x2732, 0x36BB, 0xCE4C, 0xDFC5, 0xED5E, 0xFCD7, 0x8868, 0x99E1, 0xAB7A, 0xBAF3,
          0x5285, 0x430C, 0x7197, 0x601E, 0x14A1, 0x0528, 0x37B3, 0x263A, 0xDECD, 0xCF44, 0xFDDF, 0xEC56, 0x98E9, 0x8960, 0xBBFB, 0xAA72,
          0x6306, 0x728F, 0x4014, 0x519D, 0x2522, 0x34AB, 0x0630, 0x17B9, 0xEF4E, 0xFEC7, 0xCC5C, 0xDDD5, 0xA96A, 0xB8E3, 0x8A78, 0x9BF1,
          0x7387, 0x620E, 0x5095, 0x411C, 0x35A3, 0x242A, 0x16B1, 0x0738, 0xFFCF, 0xEE46, 0xDCDD, 0xCD54, 0xB9EB, 0xA862, 0x9AF9, 0x8B70,
          0x8408, 0x9581, 0xA71A, 0xB693, 0xC22C, 0xD3A5, 0xE13E, 0xF0B7, 0x0840, 0x19C9, 0x2B52, 0x3ADB, 0x4E64, 0x5FED, 0x6D76, 0x7CFF,
          0x9489, 0x8500, 0xB79B, 0xA612, 0xD2AD, 0xC324, 0xF1BF, 0xE036, 0x18C1, 0x0948, 0x3BD3, 0x2A5A, 0x5EE5, 0x4F6C, 0x7DF7, 0x6C7E,
          0xA50A, 0xB483, 0x8618, 0x9791, 0xE32E, 0xF2A7, 0xC03C, 0xD1B5, 0x2942, 0x38CB, 0x0A50, 0x1BD9, 0x6F66, 0x7EEF, 0x4C74, 0x5DFD,
          0xB58B, 0xA402, 0x9699, 0x8710, 0xF3AF, 0xE226, 0xD0BD, 0xC134, 0x39C3, 0x284A, 0x1AD1, 0x0B58, 0x7FE7, 0x6E6E, 0x5CF5, 0x4D7C,
          0xC60C, 0xD785, 0xE51E, 0xF497, 0x8028, 0x91A1, 0xA33A, 0xB2B3, 0x4A44, 0x5BCD, 0x6956, 0x78DF, 0x0C60, 0x1DE9, 0x2F72, 0x3EFB,
          0xD68D, 0xC704, 0xF59F, 0xE416, 0x90A9, 0x8120, 0xB3BB, 0xA232, 0x5AC5, 0x4B4C, 0x79D7, 0x685E, 0x1CE1, 0x0D68, 0x3FF3, 0x2E7A,
          0xE70E, 0xF687, 0xC41C, 0xD595, 0xA12A, 0xB0A3, 0x8238, 0x93B1, 0x6B46, 0x7ACF, 0x4854, 0x59DD, 0x2D62, 0x3CEB, 0x0E70, 0x1FF9,
          0xF78F, 0xE606, 0xD49D, 0xC514, 0xB1AB, 0xA022, 0x92B9, 0x8330, 0x7BC7, 0x6A4E, 0x58D5, 0x495C, 0x3DE3, 0x2C6A, 0x1EF1, 0x0F78)


class CRC:
    __content: bytes

    def __init__(self, content: bytes = None,
                 message: bytes = None):
        if content is not None:
            if len(content) != 2:
                raise ValueError(F'Wrong CRC length, must be 2, got {len(content)}')
            else:
                self.__content = content
        else:
            value = 0xFFFF
            for i in message:
                value = ((value >> 8) ^ _CCITT[(value ^ i) & 0xFF]) & 0xFFFF
            self.__content = pack('H', ~value & 0xFFFF)

    @classmethod
    def from_frame(cls, value: bytearray, message: bytes = None) -> CRC:
        new = cls(content=bytes(value[:2]))
        if message is not None and cls(message=message).content == new.content:
            del value[:2]
            return new
        else:
            raise ValueError('Wrong CRC')

    @property
    def content(self) -> bytes:
        return self.__content

    def __str__(self):
        return self.__content.hex(' ')


class Info(ABC):

    @property
    @abstractmethod
    def content(self) -> bytes:
        """ return content in bytes """

    @abstractmethod
    def __len__(self):
        """ return content length """

    @property
    @abstractmethod
    def info(self) -> bytes:
        """ return information in bytes """


class Frame:
    """ ISO/IEC 13239:2002(E), 4. In HDLC, all transmissions are in frames. Frames may be either in basic frame format or in non-basic frame format. Neither the basic nor the
    non-basic frame format structure includes bits inserted for bit-synchronization (i.e., start or stop elements see 4.3.2) or bits or octets inserted for transparency (see 4.3).
    Basic and non-basic frame formats can not be used simultaneously on the same media. See Clause 7.5 for the rules for negotiating from the basic frame format to the non-basic
    frame format. However, it is possible for different format types of the non-basic frame to exist simultaneously on the same media.  """
    __FLAG_content: bytes = pack('B', _FLAG)
    __format: Format
    __destination_address: Address
    __source_address: Address
    __control: Control
    __hcs: CRC | None
    __info: bytes
    __fcs: CRC

    def __init__(self, content: bytearray = None,
                 DA: Address = None,
                 SA: Address = None,
                 control: Control = None,
                 info: bytes = None,
                 is_segmentation: bool = None):
        if isinstance(content, bytearray):
            if content[0] != _FLAG:
                raise ValueError('Wrong start flag')
            self.__format = Format(bytes(content[1:3]))
            if self.__format.length + 2 > len(content):  # 2 is length of flags(7e) in begin and end of frame
                raise NotEnoughDataError(F'Frame length not according by it data: got frame with length {len(content)}, but length field is {self.__format.length}')
            else:
                content.pop(0)      # remove start flag
            if content[self.__format.length] != _FLAG:
                raise ValueError('Wrong length or HDLC end flag')
            else:
                remaining_frame_data: bytearray = content[2:self.__format.length]
                """ for parsing in part """
                self.__destination_address = Address.from_frame(remaining_frame_data)
                self.__source_address = Address.from_frame(remaining_frame_data)
                self.__control = Control.from_frame(remaining_frame_data)
                if len(remaining_frame_data) == 2:  # info is absence
                    self.__hcs = None
                    self.__info = bytes()
                else:
                    self.__hcs = CRC.from_frame(value=remaining_frame_data,
                                                message=self.__header_sequence)
                    self.__info = bytes(remaining_frame_data[:-2])
                self.__fcs = CRC.from_frame(value=remaining_frame_data[-2:],
                                            message=self.__frame_sequence)
                del content[:self.__format.length]
        else:
            self.__destination_address = DA
            self.__source_address = SA
            self.__control = control
            self.__info = info
            # Frames that do not have an information field, e.g., as with some supervisory frames, or an information field of zero length do not contain an HCS and an FCS,
            # only an FCS. ISO/IEC 13239:2002(E), H.4 Frame format type 3. 7:5 = format + control + HCS? + FCS
            if len(self.__info) == 0:
                self.__format = Format(is_segmentation=is_segmentation,
                                       length=len(self.__destination_address) + len(self.__source_address) + 5)
                self.__hcs = None
            else:
                self.__format = Format(is_segmentation=is_segmentation,
                                       length=len(self.__destination_address) + len(self.__source_address) + len(self.__info) + 7)
                self.__hcs = CRC(message=self.__header_sequence)
            self.__fcs = CRC(message=self.__frame_sequence)

    def get_header(self) -> tuple[Address, Address]:
        """ return SA, DA for reusing """
        return self.__destination_address, self.__source_address

    @classmethod
    def try_from(cls, value: bytearray) -> Frame | None:
        """ Search of HDLC start flag and return Frame and value remains for next searching. If wrong frame when return value with out start flag for parsing """
        while len(value) != 0 and value[0] != _FLAG:  # remove all bytes before flag
            value.pop(0)
        if len(value) < 9:  # where 9 is min length of HDLC frame type-3
            return None
        else:
            try:
                return cls(value)
            except ValueError as e:
                logger.info(F'Wrong Frame: {e.args[0]}')
                return None
            except NotEnoughDataError as e:
                logger.info(F'Frame Error: {e.args[0]}')
                return None
            except FormatDataError as e:
                logger.info(F'Frame Error: {e.args[0]}')
                value.pop(0)
                return None

    @staticmethod
    def flag() -> int:
        """ return flag frame """
        return _FLAG

    @property
    def __header_sequence(self) -> bytes:
        return self.__format.content + self.__destination_address.content + self.__source_address.content + self.__control.content

    @property
    def __frame_sequence(self) -> bytes:
        if self.__hcs is None:
            return self.__header_sequence
        else:
            return self.__header_sequence + self.__hcs.content + self.__info

    @cached_property
    def content(self) -> bytes:
        return Frame.__FLAG_content + self.__frame_sequence + self.__fcs.content + Frame.__FLAG_content

    def __str__(self):
        return F'{self.__control.name} DA:{self.__destination_address} SA:{self.__source_address} {" Info["+str(len(self.__info))+"]:"+self.__info.hex(" ") if len(self.__info) != 0 else ""}'

    def __len__(self):
        return self.__format.length

    def is_for_me(self, DA: Address, SA: Address) -> bool:
        """ compare by DA and SA received frame"""
        return DA == self.__source_address and SA == self.__destination_address

    @property
    def control(self):
        return self.__control

    @cached_property
    def is_segmentation(self) -> bool:
        return self.__format.is_segmentation

    @property
    def info(self) -> bytes:
        return self.__info

    def is_next(self, other: Frame) -> bool:
        """ return TRUE if frame is next information frame of current. Other must be previous. """
        return self.__control == Control.next_send_sequence(Control.next_receiver_sequence(other.control))

    def is_next_send(self, other: Frame) -> bool:
        """ return TRUE if frame is next information frame of current. Other must be previous. """
        return self.__control == Control.next_send_sequence(other.control)

    @staticmethod
    def join_info(frames: Deque[Frame]) -> bytearray:
        """ TODO: """
        while len(frames) != 0:
            frame: Frame = frames.popleft()
            if frame.control.is_info():
                info: bytearray = bytearray(frame.info)
                break
            else:
                logger.warning(F'Frame {frame} not handled and deleted')
        else:
            raise ValueError('Not found information Frame')
        while frame.is_segmentation:
            if len(frames) == 0:
                raise ValueError('Not found end information Frame')
            else:
                next_frame: Frame = frames.popleft()
                if next_frame.control.is_info() and next_frame.is_next_send(frame):
                    info.extend(next_frame.info)
                    frame = next_frame
                else:
                    logger.warning(F'Frame {frame} not handled and deleted')
        return info


if __name__ == '__main__':
    ad1 = Address(upper_address=0x3f,
                  lower_address=1)
    ad2 = Address(upper_address=0x3f,
                  lower_address=1)
    print(ad1)
    comp = ad1 == ad2
    comp2 = ad1 is ad2
    a = Frame(upper_destination_address=0x3f,
              upper_source_address=1,
              control=Control(0x10),
              info=bytes(),
              is_segmentation=False)
    head = a.get_header()
    a1 = Frame(upper_destination_address=0x3,
              upper_source_address=10,
              control=Control(0x10),
              info=bytes(),
              is_segmentation=False,
              header=head
              )
    comp3 = a1.is_for_me(head)
    print(a)
    # a1 = Frame(upper_destination_address=0x3f,
    #           upper_source_address=1,
    #           control=Control(0x32),
    #           info=bytes(),
    #           is_segmentation=False)
    # print(a1)
    # print(a1.is_next(a))

    # data = bytearray.fromhex('7e a0 38 21 02 21 30 84 d4 e6 e7 00 61 29 a1 09 06 07 60 85 74 05 08 01 01 a2 03 02 01 00 a3 05 a1 03 02 01 00 be 10 04 0e 08 00 06 5f 1f 04 00 00 18 18 04 00 00 07 4e 98 7e')
    # data = bytearray(b'~~\xa0\x1f!\x02!sV\xf4\x81\x80\x12\x05\x01\x80\x06\x01\x80\x07\x04\x00\x00\x00\x01\x08\x04\x00\x00\x00\x01S;~\xa0\x1f!\x02!sV\xf4\x81\x80\x12\x05\x01\x80\x06\x01\x80\x07\x04\x00\x00\x00\x01\x08\x04\x00\x00\x00\x01S;~')
    # data = bytearray.fromhex('7e a8 87 21 02 21 7a fa 2c 07 e4 01 01 03 02 1e ff ff 80 00 00 15 00 00 00 00 db 69 14 81 15 00 00 00 00 00 49 8b f0 15 00 00 00 00 08 99 89 25 15 00 00 00 00 07 a1 9a 16 15 00 00 00 00 00 b2 3e cb 15 00 00 00 00 00 00 00 00 15 00 00 00 00 00 03 7e')
    data = bytearray.fromhex('7E A8 01 41 02 21 52 99 A9 E6 E7 00 C4 02 C1 00 00 00 00 01 00 82 02 EA 01 81 9F 02 04 12 00 0F 11 01 09 06 00 00 28 00 00 FF 02 02 01 09 02 03 0F 01 16 01 00 02 03 0F 02 16 01 00 02 03 0F 03 16 01 00 02 03 0F 04 16 01 00 02 03 0F 05 16 01 00 02 03 0F 06 16 01 00 02 03 0F 07 16 01 00 02 03 0F 08 16 01 00 02 03 0F 09 16 01 00 01 04 02 02 0F 01 16 00 02 02 0F 02 16 00 02 02 0F 03 16 00 02 02 0F 04 16 00 02 04 12 00 08 11 00 09 06 00 00 01 00 00 FF 02 02 01 09 02 03 0F 01 16 01 00 02 03 0F 02 16 01 00 02 03 0F 03 16 01 00 02 03 0F 04 16 01 00 02 03 0F 05 16 01 00 02 03 0F 06 16 01 00 02 03 0F 07 16 01 00 02 03 0F 08 16 01 00 02 03 0F 09 16 01 00 01 06 02 02 0F 01 16 01 02 02 0F 02 16 01 02 02 0F 03 16 01 02 02 0F 04 16 01 02 02 0F 05 16 01 02 02 0F 06 16 01 02 1F FC 7E')
    # data = bytearray(b'~\xa8\x87!\x02!\x96\x98\x01\xe6\xe7\x00\xc4\x01\xc1\x00\x01\n\x02\t\t\x0c\x07\xe5\x08\x06\x05\x0b\x1e\xff\xff\x80\x00\x00\x15\x00\x00\x00\x00\xda\x85\x9e~')
    # data = bytearray(b'~\xa8\x89!\x03\x96\xae)\xe6\xe7\x00\xc4\x01\xc1\x00\x01\x07\x02\x02\x11\x00\x01\x05\x02\x03\t\x04\x00\x00\x00\xff\t\x06\x00\x00\n\x00d\xff\x12\x00\x01\x02\x03\t\x04\x01\x00\x00\xff\t\x06\x00\x00\n\x00d\xff\x12\x00\x02\x02\x03\t\x04\x0c\x17\x00\xff\t\x06\x00\x00\n\x00d\xff\x12\x00\x04\x02\x03\t\x04\x16\x1e\x00\xff\t\x06\x00\x00\n\x00d\xff\x12\x00\x04\x02\x03\t\x04\x17\x1e\x00\xff\t\x06\x00\x00\n\x00d\xff\x12\x00\x03\x02\x02\x11\x01\x01\x01\x02\x03\t\x04\x01\x00\x00\xff\t\x06\x00\x00\x19Q~')
    frame1 = Frame.try_from(data)
    print(frame1)
    a = Control.SNRM_P
    print(a)

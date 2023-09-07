from dataclasses import dataclass
from functools import cached_property
from ..hdlc.frame import Info
from struct import pack_into, unpack_from
from typing import ClassVar

MAX_CONTENT_LENGTH = 0x16
FORMAT_IDENTIFIER = 0x81
GROUP_IDENTIFIER = 0x80
MAX_INFO_DEFAULT = 128
WINDOW_DEFAULT = 1
MIN_MAX_INFO_FIELD_LENGTH = 32
MAX_MAX_INFO_FIELD_LENGTH = 2030
MIN_WINDOW_SIZE = 1
MAX_WINDOW_SIZE = 7


@dataclass
class Negotiation(Info):
    MAXIMUM_INFORMATION_FIELD_LENGTH_TRANSMIT: ClassVar[int] = 5
    MAXIMUM_INFORMATION_FIELD_LENGTH_RECEIVE: ClassVar[int] = 6
    WINDOW_SIZE_TRANSMIT: ClassVar[int] = 7
    WINDOW_SIZE_RECEIVE: ClassVar[int] = 8
    max_info_transmit: int = MAX_INFO_DEFAULT
    max_info_receive: int = MAX_INFO_DEFAULT
    window_transmit: int = WINDOW_DEFAULT
    window_receive: int = WINDOW_DEFAULT

    def set_from_UA(self, content: bytes):
        """set from UA info"""
        def get_max_information_field(data: memoryview) -> tuple[int, memoryview]:
            data_len = data[0]
            ret = int.from_bytes(data[1:1 + data_len], "big")
            if MIN_MAX_INFO_FIELD_LENGTH <= ret <= MAX_MAX_INFO_FIELD_LENGTH:
                return ret, memoryview(data[1 + data_len:])
            else:
                raise ValueError(F"got max information field {ret}, expected {MIN_MAX_INFO_FIELD_LENGTH}..{MAX_MAX_INFO_FIELD_LENGTH}")

        def get_window_size(data: memoryview) -> tuple[int, memoryview]:
            data_len = data[0]
            ret = int.from_bytes(data[1:1 + data_len], "big")
            if MIN_WINDOW_SIZE <= ret <= MAX_WINDOW_SIZE:
                return ret, memoryview(data[1 + data_len:])
            else:
                raise ValueError(F"got window_size {ret}, expected {MIN_WINDOW_SIZE}..{MAX_WINDOW_SIZE}")

        try:
            i_rx = i_tx = MAX_INFO_DEFAULT
            w_rx = w_tx = WINDOW_DEFAULT
            if len(content) == 0:
                """skip setting"""
            elif content[0] != FORMAT_IDENTIFIER:
                raise ValueError(F"got {content[0]=}, expected {FORMAT_IDENTIFIER}")
            else:
                if content[1] != GROUP_IDENTIFIER:
                    raise ValueError(F"got {content[1]=}, expected {GROUP_IDENTIFIER}")
                else:
                    if content[2] != len(content[3:]):
                        raise ValueError(F"got {content[2]=}, but content has length={len(content)}")
                    else:
                        data = memoryview(content[3:])
                        while data:
                            match data[0]:
                                case self.MAXIMUM_INFORMATION_FIELD_LENGTH_TRANSMIT:
                                    i_rx, data = get_max_information_field(data[1:])
                                case self.MAXIMUM_INFORMATION_FIELD_LENGTH_RECEIVE:
                                    i_tx, data = get_max_information_field(data[1:])
                                case self.WINDOW_SIZE_TRANSMIT:
                                    w_rx, data = get_window_size(data[1:])
                                case self.WINDOW_SIZE_RECEIVE:
                                    w_tx, data = get_window_size(data[1:])
                                case wrong_tag:
                                    raise ValueError(F"got {wrong_tag=}, expected ")
            self.max_info_receive, self.max_info_transmit, self.window_receive, self.window_transmit = i_rx, i_tx, w_rx, w_tx
            if hasattr(self, "SNRM"):
                del self.SNRM
        except IndexError as e:
            raise ValueError(F"got wrong UA {content.hex(' ')}")

    @cached_property
    def SNRM(self) -> memoryview:
        def small_pack(field: int, data: int):
            nonlocal buf, offset
            pack_into(">BBB", buf, offset,
                      field,
                      1,
                      data)
            offset += 3

        def big_pack(field: int, data: int):
            nonlocal buf, offset
            pack_into(">BBH", buf, offset,
                      field,
                      2,
                      data)
            offset += 4

        def window_pack(field: int, data: int):
            nonlocal buf, offset
            pack_into(">BBL", buf, offset,
                      field,
                      4,
                      data)
            offset += 6

        buf = bytearray(MAX_CONTENT_LENGTH)
        offset: int = 3
        if self.max_info_transmit == MAX_INFO_DEFAULT:
            """not send max_info_transmit"""
        elif self.max_info_transmit < 0x100:  # 1 byte length
            small_pack(self.MAXIMUM_INFORMATION_FIELD_LENGTH_TRANSMIT, self.max_info_transmit)
        else:
            big_pack(self.MAXIMUM_INFORMATION_FIELD_LENGTH_TRANSMIT, self.max_info_transmit)
        if self.max_info_receive == MAX_INFO_DEFAULT:
            """not send max_info_receive"""
        elif self.max_info_receive < 0x100:
            small_pack(self.MAXIMUM_INFORMATION_FIELD_LENGTH_RECEIVE, self.max_info_receive)
        else:
            big_pack(self.MAXIMUM_INFORMATION_FIELD_LENGTH_RECEIVE, self.max_info_receive)
        if self.window_transmit != WINDOW_DEFAULT:
            window_pack(self.WINDOW_SIZE_TRANSMIT, self.window_transmit)
        if self.window_receive != WINDOW_DEFAULT:
            window_pack(self.WINDOW_SIZE_RECEIVE, self.window_transmit)
        if offset == 3:
            offset = 0
        else:
            pack_into(">BBB", buf, 0,
                      FORMAT_IDENTIFIER,
                      GROUP_IDENTIFIER,
                      offset-3)
        return memoryview(buf[:offset])

    @property
    def info(self) -> bytes:
        return bytes(self.SNRM)

    @property
    def content(self) -> bytes:
        return bytes(self.SNRM)

    def __len__(self):
        return len(self.SNRM)

    def __str__(self):
        return F"NEGOTIATION: {self.max_info_transmit}->[info_size]->{self.max_info_receive} {self.window_transmit}->[window]->{self.window_receive}"

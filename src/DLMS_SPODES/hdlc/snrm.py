from __future__ import annotations
from functools import cached_property
from ..hdlc.frame import Info


class SNRM(Info):
    __max_info_transmit: bytes
    __max_info_receive: bytes
    __window_transmit: bytes
    __window_receive: bytes

    def __init__(self, max_info_transmit: bytes = None,
                 max_info_receive: bytes = None,
                 window_transmit: bytes = None,
                 window_receive: bytes = None):
        self.__max_info_transmit = max_info_transmit
        """ Maximum information field length - transmit """
        self.__max_info_receive = max_info_receive
        """ Maximum information field length - receive """
        self.__window_transmit = window_transmit
        """ Window size k - transmit """
        self.__window_receive = window_receive
        """ Window size k - receive """

    @cached_property
    def content(self) -> bytes:
        value = bytes()
        if self.__max_info_transmit is not None:
            value += b'\x05'
            value += b'\x02'+self.__max_info_transmit if self.__max_info_transmit[0] != 0 \
                else b'\x01' + self.__max_info_transmit[1:]
        if self.__max_info_receive is not None:
            value += b'\x06'  # tag max_value_transmit
            value += b'\x02'+self.__max_info_receive if self.__max_info_receive[0] != 0 \
                else b'\x01' + self.__max_info_receive[1:]
        if self.__window_transmit is not None:
            value += b'\x07\x01' + self.__window_transmit
        if self.__window_receive is not None:
            value += b'\x08\x01'+self.__window_receive
        if len(value) == 0:
            return bytes()
        else:
            return b'\x81\x80' + len(value).to_bytes(1, 'big') + value

    def info(self) -> bytes:
        return self.content

    def __len__(self):
        return len(self.content)

    def __str__(self):
        value: str = ''
        if self.__max_info_transmit:
            value += F'max_tr: {int.from_bytes(self.__max_info_transmit, "big")}'
        if self.__max_info_receive:
            value += F' max_rec: {int.from_bytes(self.__max_info_receive, "big")}'
        if self.__window_transmit:
            value += F' win_tr: {int.from_bytes(self.__window_transmit, "big")}'
        if self.__window_receive:
            value += F' max_rec: {int.from_bytes(self.__window_receive, "big")}'
        return value

    @classmethod
    def try_create(cls, max_info_transmit: bytes = None,
                   max_info_receive: bytes = None,
                   window_transmit: bytes = None,
                   window_receive: bytes = None) -> SNRM | None:
        """ create SNRM if exist as least one parameter """
        if any((max_info_transmit, max_info_receive, window_transmit, window_receive)):
            return cls(max_info_transmit=max_info_transmit,
                       max_info_receive=max_info_receive,
                       window_transmit=window_transmit,
                       window_receive=window_receive)
        else:
            return None

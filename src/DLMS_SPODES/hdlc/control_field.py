from __future__ import annotations
from enum import IntFlag, Enum


class Command(IntFlag):
    """DLMS commands."""

    NONE = 0x00
    """No command to execute."""

    INITIATE_REQUEST = 0x01
    """ Initiate request. """

    INITIATE_RESPONSE = 0x08
    """ Initiate response. """

    READ_REQUEST = 0x05
    """ Read request. """

    READ_RESPONSE = 0x0C
    """ Read response. """

    WRITE_REQUEST = 0x06
    """ Write request. """

    WRITE_RESPONSE = 0x0D
    """ Write response. """

    GET_REQUEST = 0xC0
    """ Get request. """

    GET_RESPONSE = 0xC4
    """ Get response. """

    SET_REQUEST = 0xC1
    """ Set request. """

    SET_RESPONSE = 0xC5
    """ Set response. """

    METHOD_REQUEST = 0xC3
    """ Action request. """

    ACTION_RESPONSE = 0xC7
    """ Action response. """

    DISCONNECT_MODE = 0x1F
    """ HDLC Disconnect Mode. """

    UNACCEPTABLE_FRAME = 0x97
    """ HDLC Unacceptable frame. """

    SNRM = 0x93
    """ HDLC SNRM request. """

    UA = 0x73
    """ HDLC UA request. """

    AARQ = 0x60
    """ AARQ request. """

    AARE = 0x61
    """ AARE request. """

    DISCONNECT_REQUEST = 0x53
    """ Disconnect request for HDLC framing. """

    RELEASE_REQUEST = 0x62
    """ Release request. """

    RELEASE_RESPONSE = 0x63
    """ Disconnect response. """

    CONFIRMED_SERVICE_ERROR = 0x0E
    """ Confirmed Service Error. """

    EXCEPTION_RESPONSE = 0xD8
    """ Exception Response. """

    GENERAL_BLOCK_TRANSFER = 0xE0
    """ General Block Transfer. """

    ACCESS_REQUEST = 0xD9
    """ Access Request. """

    ACCESS_RESPONSE = 0xDA
    """ Access Response. """

    DATA_NOTIFICATION = 0x0F
    """ Data Notification request. """

    GLO_GET_REQUEST = 0xC8
    """ Glo get request. """

    GLO_GET_RESPONSE = 0xCC
    """ Glo get response. """

    GLO_SET_REQUEST = 0xC9
    """ Glo set request. """

    GLO_SET_RESPONSE = 0xCD
    """ Glo set response. """

    GLO_EVENT_NOTIFICATION = 0xCA
    """ Glo event notification. """

    GLO_METHOD_REQUEST = 0xCB
    """ Glo method request. """

    GLO_METHOD_RESPONSE = 0xCF
    """ Glo method response. """

    GLO_INITIATE_REQUEST = 0x21
    """ Glo Initiate request. """

    GLO_READ_REQUEST = 0x37
    """ Glo read request. """

    GLO_WRITE_REQUEST = 0x38
    """ Glo write request. """

    GLO_INITIATE_RESPONSE = 0x40
    """ Glo Initiate response. """

    GLO_READ_RESPONSE = 0x44
    """ Glo read response. """

    GLO_WRITE_RESPONSE = 0x45
    """ Glo write response. """

    GENERAL_GLO_CIPHERING = 0xDB
    """ General GLO ciphering. """

    GENERAL_DED_CIPHERING = 0xDC
    """ General DED ciphering. """

    GENERAL_CIPHERING = 0xDD
    """ General ciphering. """

    INFORMATION_REPORT = 0x18
    """ Information Report request. """

    EVENT_NOTIFICATION = 0xC2
    """ Event Notification request. """

    DED_INITIATE_REQUEST = 0x65
    """ Ded initiate request. """

    DED_READ_REQUEST = 0x69
    """ Ded read request. """

    DED_WRITE_REQUEST = 0x70
    """ Ded write request. """

    DED_INITIATE_RESPONSE = 0x72
    """ Ded initiate response. """

    DED_READ_RESPONSE = 0x76
    """ Ded read response. """

    DED_WRITE_RESPONSE = 0x77
    """ Ded write response. """

    DED_CONFIRMED_SERVICE_ERROR = 0x78
    """ Ded confirmed service error. """

    DED_UNCONFIRMED_WRITE_REQUEST = 0x86
    """ Ded confirmed write request. """

    DED_INFORMATION_REPORT_REQUEST = 0x88
    """ Ded information report request. """

    DED_GET_REQUEST = 0xD0
    """ Ded get request. """

    DED_GET_RESPONSE = 0xD4
    """ Ded get response. """

    DED_SET_REQUEST = 0xD1
    """ Ded set request. """

    DED_SET_RESPONSE = 0xD5
    """ Ded set response. """

    DED_EVENT_NOTIFICATION = 0xD2
    """ Ded event notification request. """

    DED_METHOD_REQUEST = 0xD3
    """ Ded method request. """

    DED_METHOD_RESPONSE = 0xD7
    """ Ded method response. """

    GATEWAY_REQUEST = 0xE6
    """Request message from client to gateway."""

    GATEWAY_RESPONSE = 0xE7
    """ Response message from gateway to client. """


class HDLCInfo(Enum):
    MAX_INFO_TX = b'\x05'
    MAX_INFO_RX = b'\x06'
    WINDOW_SIZE_TX = b'\x07'
    WINDOW_SIZE_RX = b'\x08'


if __name__ == '__main__':
    a = Command.NONE
    b = Command.NONE
    print(a is b)

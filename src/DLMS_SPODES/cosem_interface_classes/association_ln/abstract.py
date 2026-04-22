from typing import Protocol, runtime_checkable, TypeAlias, Any
from COSEMpdu.x680.type import SEQUENCE_OF
from COSEMpdu.data import (
    NullData, Array, Data, DoubleLongUnsigned, Integer, Structure, LongUnsigned, CompactArray,
    DoubleLong, OctetString, Unsigned, Enum, VisibleString, Long, Long64Unsigned, Float32, Float64,
    Utf8String, DateTime, Date, Time, CDT
)
from ...types import cdt, cst, ut, choices
from ... import pdu_enums as pdu
from ...types.type_alias import Obis
from ...types.implementations import long_unsigneds
from ... import exceptions as exc


class AccessModeProto(Protocol):
    def is_writable(self) -> bool: ...
    def is_readable(self) -> bool: ...

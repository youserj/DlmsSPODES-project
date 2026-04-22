"""DLMS UA 1000-1 Ed. 14"""
from COSEMpdu.data import (
    Array, Data, DoubleLongUnsigned, Integer, Structure, LongUnsigned, CompactArray, 
    DoubleLong, OctetString, Unsigned, VisibleString, Long, Long64Unsigned, Float32, Float64,
    Utf8String, DateTime, Date, Time, union2alternatives
)
from COSEMpdu import types_used
from ...types.type_alias import Attr
from . import ver0
from typing import TypeAlias, Any
from ...types.implementations import structs
from ..cosem_interface_class import ICAElement, Classifier, update_collection


CaptureObjects = Array[structs.CaptureObjectDefinition]


class EntryDescriptor(Structure):
    """entry_descriptor"""
    from_entry: DoubleLongUnsigned
    to_entry: DoubleLongUnsigned
    from_selected_value: LongUnsigned
    to_selected_value: LongUnsigned


RangeValueType: TypeAlias = DoubleLong | DoubleLongUnsigned | OctetString | VisibleString | Utf8String | \
                    Integer | Unsigned | LongUnsigned | Long | Long64Unsigned | Float32 | Float64 | DateTime | Date | Time


class RangeValue(Data[RangeValueType]):
    alternatives = union2alternatives(RangeValueType)


class RangeDescriptor(Structure):
    """range_descriptor"""
    restricting_object: structs.CaptureObjectDefinition
    from_value: RangeValue
    to_value: RangeValue
    selected_values: CaptureObjects


BufferType: TypeAlias = Array[Any] | CompactArray


class Buffer(Data[BufferType]):
    alternatives = union2alternatives(BufferType)


class ParametersType(Data[EntryDescriptor | RangeDescriptor]):
    alternatives = union2alternatives(EntryDescriptor | RangeDescriptor)  # todo: don't work


class SelectiveAccessDescriptor(types_used.SelectiveAccessDescriptor): ...


class ProfileGeneric(ver0.ProfileGeneric):
    """4.3.6 Profile generic"""
    VERSION = 1
    A_ELEMENTS = update_collection(
        ver0.ProfileGeneric.A_ELEMENTS,
        ICAElement(2, "buffer", Buffer, classifier=Classifier.DYNAMIC, selective_access=SelectiveAccessDescriptor),
        ICAElement(3, "capture_objects", CaptureObjects),
        ICAElement(6, "sort_object", structs.CaptureObjectDefinition),
        ICAElement(7, "entries_in_use", DoubleLongUnsigned, 0, default=0, classifier=Classifier.DYNAMIC),
        ICAElement(8, "profile_entries", DoubleLongUnsigned, 1, default=1)
    )
    M_ELEMENTS = (
        ver0.ProfileGeneric.getMElement(1),
        ver0.ProfileGeneric.getMElement(2))
    buffer: Attr
    capture_objects: Attr
    sort_method: Attr
    sort_object: Attr

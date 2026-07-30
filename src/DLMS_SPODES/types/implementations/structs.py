""" COMMON Structs """
from dataclasses import dataclass
from COSEMpdu.data import DoubleLongUnsigned, Integer, Structure, LongUnsigned, Unsigned, VisibleString
from ...types import cosem_service_types as cst
from . import long_unsigneds


@dataclass
class ActionItem(Structure):
    """action_item"""
    script_logical_name: cst.LogicalName
    script_selector: LongUnsigned


@dataclass
class ValueDefinition(Structure):
    """value_definition"""
    class_id: long_unsigneds.ClassId
    logical_name: cst.LogicalName
    attribute_index: Integer


@dataclass
class RestrictionByDate(Structure):
    """restriction_by_date"""
    from_date: cst.OctetStringDate
    to_date: cst.OctetStringDate


@dataclass
class RestrictionByEntry(Structure):
    """restriction_by_entry"""
    from_entry: DoubleLongUnsigned
    to_entry: DoubleLongUnsigned


@dataclass
class CaptureObjectDefinition(Structure):
    """capture_object_definition"""
    class_id: long_unsigneds.ClassId
    logical_name: cst.LogicalName
    attribute_index: Integer
    data_index: LongUnsigned


@dataclass
class WindowElement(Structure):
    """window_element"""
    start_time: cst.OctetStringDateTime
    end_time: cst.OctetStringDateTime


@dataclass
class UserListEntry(Structure):
    """user_list_entry"""
    user_id:   Unsigned
    user_name: VisibleString

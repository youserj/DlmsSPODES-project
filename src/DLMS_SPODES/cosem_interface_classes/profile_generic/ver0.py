"""DLMS UA 1000-1 Ed 14"""
from COSEMpdu.data import Array, DoubleLongUnsigned, Integer, Enum, Structure
from ...types.type_alias import Attr
from ...types.implementations import long_unsigneds, integers
from ...types import cst
from ..cosem_interface_class import ICAuto, ICAElement, ICMElement, Classifier


class ObjectDefinition(Structure):
    """ObjectDefinition"""
    logical_name: cst.LogicalName
    class_id: long_unsigneds.ClassId
    attribute_index: Integer


CaptureObjects = Array[ObjectDefinition]


class SortMethod(Enum):
    """sort_method"""


class ProfileGeneric(ICAuto):
    """5.3.1 Profile generic"""
    CLASS_ID = 7
    VERSION = 0
    # todo: remove down following
    scaler_profile_key: bytes | None = None
    """ obis of scaler profile for this profile if need """

    A_ELEMENTS = (
        ICAElement(2, "buffer", Array, classifier=Classifier.DYNAMIC),
        ICAElement(3, "capture_objects", CaptureObjects),
        ICAElement(4, "capture_period", DoubleLongUnsigned),
        ICAElement(5, "sort_method", SortMethod),
        ICAElement(6, "sort_object", ObjectDefinition),
        ICAElement(7, "entries_in_use", DoubleLongUnsigned, 0, default=0, classifier=Classifier.DYNAMIC),
        ICAElement(8, "profile_entries", DoubleLongUnsigned, 1, default=1)
    )
    M_ELEMENTS = (
        ICMElement(1, "reset", integers.IntegerValue0),
        ICMElement(2, "capture", integers.IntegerValue0),
        # more 2 elements
    )
    buffer: Attr
    capture_objects: Attr
    capture_period: Attr
    sort_method: Attr
    sort_object: Attr
    entries_in_use: Attr
    profile_entries: Attr

"""DLMS UA 1000-1 Ed 14"""
from typing import Optional
from ...types.implementations import long_unsigneds, integers
from ...types import cdt, cst, ut
from ..cosem_interface_class import ICAuto, ICAElement, ICMElement, Classifier, Cardinality
from ..Overview import class_id

BUFFER = 2
CAPTURE_OBJECTS = 3
CAPTURE_PERIOD = 4
SORT_METHOD = 5
SORT_OBJECT = 6
ENTRIES_IN_USE = 7
PROFILE_ENTRIES = 8


class ObjectDefinition(cdt.Structure):
    """ObjectDefinition"""
    logical_name: cst.LogicalName
    class_id: long_unsigneds.ClassId
    attribute_index: cdt.Integer

    def __hash__(self):
        return hash((self.logical_name.contents, self.class_id.contents, self.attribute_index.contents))


class CaptureObjects(cdt.Array):
    """ Specifies the list of capture objects """
    TYPE = ObjectDefinition


class SortMethod(cdt.Enum, elements=(1, 2, 3, 4, 5, 6)):
    """sort_method"""


class ProfileGeneric(ICAuto):
    """5.3.1 Profile generic"""
    CLASS_ID = class_id.PROFILE_GENERIC
    VERSION = 0
    # todo: remove down following
    scaler_profile_key: bytes | None = None
    """ obis of scaler profile for this profile if need """
    buffer_capture_objects: CaptureObjects
    range_descriptor: type[cdt.Structure] = None
    attr_descriptor_with_selection: type[ut.CosemAttributeDescriptorWithSelection] = None

    A_ELEMENTS = (
        ICAElement(2, "buffer", cdt.Array, classifier=Classifier.DYNAMIC),
        ICAElement(3, "capture_objects", CaptureObjects),
        ICAElement(4, "capture_period", cdt.DoubleLongUnsigned),
        ICAElement(5, "sort_method", SortMethod),
        ICAElement(6, "sort_object", ObjectDefinition),
        ICAElement(7, "entries_in_use", cdt.DoubleLongUnsigned, 0, default=0, classifier=Classifier.DYNAMIC),
        ICAElement(8, "profile_entries", cdt.DoubleLongUnsigned, 1, default=1)
    )
    M_ELEMENTS = (
        ICMElement(1, "reset", integers.Only0),
        ICMElement(2, "capture", integers.Only0),
        # more 2 elements
    )
    buffer: Optional[cdt.Array]
    capture_objects: Optional[CaptureObjects]
    capture_period: Optional[cdt.DoubleLongUnsigned]
    sort_method: Optional[SortMethod]
    sort_object: Optional[ObjectDefinition]
    entries_in_use: Optional[cdt.DoubleLongUnsigned]
    profile_entries: Optional[cdt.DoubleLongUnsigned]

    def characteristics_init(self):
        self.set_attr(BUFFER, None)
        # todo remove it
        self.buffer.register_cb_preset(lambda _: self.__create_buffer_struct_type())  # value not used for creating struct type
        self._cbs_attr_post_init.update({CAPTURE_OBJECTS: self.__create_buffer_struct_type})
        self.buffer_capture_objects = self.capture_objects
        """ objects for buffer. Change with access_selection """

    def __create_buffer_struct_type(self):
        """ TODO: more refactoring !!! """
        # rename ObjectDefinition's and adding object if it absense in collection
        el_value: ObjectDefinition
        if self.capture_objects is None:
            raise ValueError(F"{self}: create buffer Struct type, not set <capture_object> attribute. Need initiate <capture_objects> before")
        for el_value in self.capture_objects:
            self.collection.add_if_missing(
                class_id=ut.CosemClassId(el_value.class_id.contents),
                version=None,
                logical_name=el_value.logical_name)
            el_value.set_name(self.collection.get_name_and_type(el_value)[0][-1])
        self.buffer_capture_objects = self.capture_objects
        self.buffer.set_type(self.capture_objects.__class__)

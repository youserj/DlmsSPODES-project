"""DLMS UA 1000-1 Ed 14"""
from typing import Type
from ..__class_init__ import *
from ...types.implementations import long_unsigneds, integers
from ..overview import VERSION_0


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


class GetBufferByIndex(cdt.Structure):
    """get_buffer_by_index"""
    from_index: cdt.DoubleLongUnsigned
    to_index: cdt.DoubleLongUnsigned
    selected_values: cdt.Array
    


class ProfileGeneric(ic.COSEMInterfaceClasses):
    """5.3.1 Profile generic"""
    CLASS_ID = ClassID.PROFILE_GENERIC
    VERSION = VERSION_0
    # todo: remove down following
    scaler_profile_key: bytes | None = None
    """ obis of scaler profile for this profile if need """
    buffer_capture_objects: CaptureObjects
    range_descriptor: Type[cdt.Structure] = None
    attr_descriptor_with_selection: Type[ut.CosemAttributeDescriptorWithSelection] = None

    A_ELEMENTS = (
        ic.ICAElement("buffer", cdt.Array, classifier=ic.Classifier.DYNAMIC),
        ic.ICAElement("capture_objects", CaptureObjects),
        ic.ICAElement("capture_period", cdt.DoubleLongUnsigned),  # 5.3.1 Profile generic. capture_period
        ic.ICAElement("sort_method", SortMethod),
        ic.ICAElement("sort_object", ObjectDefinition),
        ic.ICAElement("entries_in_use", cdt.DoubleLongUnsigned, 0, default=0, classifier=ic.Classifier.DYNAMIC),
        ic.ICAElement("profile_entries", cdt.DoubleLongUnsigned, 1, default=1)
    )
    M_ELEMENTS = (
        ic.ICMElement("reset", integers.Only0),
        ic.ICMElement("capture", integers.Only0),
        ic.ICMElement("write", cdt.Structure),  # todo: make anyhow
        ic.ICMElement("get_buffer_by_range", integers.Only0),
        ic.ICMElement("get_buffer_by_index", integers.Only0)
        # more 2 elements
    )

    def characteristics_init(self):
        self.set_attr(BUFFER, None)

        # todo remove it
        self.buffer.register_cb_preset(lambda _: self.__create_buffer_struct_type())  # value not used for creating struct type

        self._cbs_attr_post_init.update({CAPTURE_OBJECTS: self.__create_buffer_struct_type})

        self.buffer_capture_objects = self.capture_objects
        """ objects for buffer. Change with access_selection """

    @property
    def buffer(self) -> cdt.Array:
        return self.get_attr(2)

    @property
    def capture_objects(self) -> CaptureObjects:
        return self.get_attr(3)

    @property
    def capture_period(self) -> cdt.DoubleLongUnsigned:
        return self.get_attr(4)

    @property
    def sort_method(self) -> SortMethod:
        return self.get_attr(5)

    @property
    def sort_object(self) -> ObjectDefinition:
        return self.get_attr(6)

    @property
    def entries_in_use(self) -> cdt.DoubleLongUnsigned:
        return self.get_attr(7)

    @property
    def profile_entries(self) -> cdt.DoubleLongUnsigned:
        return self.get_attr(8)

    @property
    def reset(self) -> integers.Only0:
        return self.get_meth(1)

    @property
    def capture(self) -> integers.Only0:
        return self.get_meth(2)

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

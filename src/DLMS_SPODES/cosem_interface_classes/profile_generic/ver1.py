"""DLMS UA 1000-1 Ed. 14"""
from . import ver0
from typing import Iterator, Optional
from ... import cosem_interface_classes
from ...relation_to_OBIS import get_name
from ... import exceptions as exc
from ...types.implementations import arrays, structs
from ...types.choices import CommonDataTypeChoiceBase
from ...types import cdt, ut
from ..cosem_interface_class import ICAElement, Classifier


class CaptureObjects(cdt.Array):
    """ Specifies the list of capture objects """
    TYPE = structs.CaptureObjectDefinition


class FromEntry(cdt.DoubleLongUnsigned, min=1):
    """ Access selector value for selective access to the object_list attribute """


class EntryDescriptor(cdt.Structure):
    """ Only buffer elements corresponding to the entry_descriptor shall be returned in the response.
    NOTE: from_entry and to_entry identify the lines, from_selected_value to_selected_value identify the columns of the buffer to be retrieved. """
    DEFAULT = (1, 0, 1, 0)
    from_entry: FromEntry
    to_entry: cdt.DoubleLongUnsigned
    from_selected_value: cdt.LongUnsigned
    to_selected_value: cdt.LongUnsigned


class AccessSelector(ut.Unsigned8):
    """ Unsigned8 1..2. Default is 2 for read all buffer """
    def __init__(self, value: int | str | ut.Unsigned8 = 2):
        super(AccessSelector, self).__init__(value)
        if int(self) not in (1, 2):
            raise ValueError(F'The {self.__class__.__name__} got {int(self)}, expected 1..2')


class RangeDescriptorValueChoice(CommonDataTypeChoiceBase, types=(
        cdt.DoubleLong,
        cdt.DoubleLongUnsigned,
        cdt.OctetString,
        cdt.VisibleString,
        cdt.Utf8String,
        cdt.Integer,
        cdt.Unsigned,
        cdt.LongUnsigned,
        cdt.Long,
        cdt.Long64Unsigned,
        cdt.Float32,
        cdt.Float64,
        cdt.DateTime,
        cdt.Date,
        cdt.Time
)):
    """Types of range_descriptor.from_value/to_value"""


# class RangeDescriptor(cdt.Structure):
#     restricting_object: structs.CaptureObjectDefinition
#     from_value: RangeDescriptorValueChoice
#     to_value: RangeDescriptorValueChoice
#     selected_values: CaptureObjects
#
#     def __setattr__(self, key, value):
#         """Allow setting from_value and to_value with a CommonDataType of allowed types.
#         Other attributes remain immutable as per base Structure behavior."""
#         if key in ("from_value", "to_value"):
#             index = 1 if key == "from_value" else 2
#             # Accept only CommonDataType instances of allowed types
#             if isinstance(value, cdt.CommonDataType):
#                 # Build allowed types tuple from Choice definition
#                 allowed_types = tuple(el.TYPE if isinstance(el, ut.SequenceElement) else None for el in RangeDescriptorValueChoice.ELEMENTS.values())
#                 allowed_types = tuple(t for t in allowed_types if t is not None)
#                 if isinstance(value, allowed_types):
#                     self.values[index] = value
#                     return
#                 else:
#                     raise ValueError(F"Type got {value.__class__.__name__}, expected one of: "
#                                      + ", ".join(t.__name__ for t in allowed_types))
#             else:
#                 raise TypeError(F"Unsupported value type for {key}: {value.__class__.__name__}. Provide a CommonDataType instance.")
#         else:
#             super().__setattr__(key, value)
#
#
# class Data(ut.Data):
#     restricting_object: structs.CaptureObjectDefinition
#     from_value: cdt.SimpleDataType
#     to_value: cdt.SimpleDataType
#     selected_values: CaptureObjects
#     from_entry: FromEntry
#     to_entry: cdt.DoubleLongUnsigned
#     from_selected_value: cdt.LongUnsigned
#     to_selected_value: cdt.LongUnsigned
#     ELEMENTS = {1: ut.SequenceElement('range_descriptor', RangeDescriptor),
#                 2: ut.SequenceElement('entry_descriptor', EntryDescriptor)}
#
#
# class SelectiveAccessDescriptor(ut.SelectiveAccessDescriptor):
#     access_selector: AccessSelector
#     access_parameters: Data
#     ELEMENTS = (ut.SequenceElement('access_selector', AccessSelector),
#                 ut.SequenceElement('access_parameters', Data))
#
#
# class CosemAttributeDescriptorWithSelection(ut.CosemAttributeDescriptorWithSelection):
#     access_selection: SelectiveAccessDescriptor
#     ELEMENTS = (ut.SequenceElement('cosem_attribute_descriptor', ut.CosemAttributeDescriptor),
#                 ut.SequenceElement('access_selection', SelectiveAccessDescriptor))


class ProfileGeneric(ver0.ProfileGeneric):
    """4.3.6 Profile generic"""
    VERSION = 1
    A_ELEMENTS = (ICAElement(2, "buffer", arrays.SelectionAccess, classifier=Classifier.DYNAMIC),
                  ICAElement(3, "capture_objects", CaptureObjects),
                  ver0.ProfileGeneric.getAElement(4).unwrap(),
                  ver0.ProfileGeneric.getAElement(5).unwrap(),
                  ICAElement(6, "sort_object", structs.CaptureObjectDefinition),
                  ICAElement(7, "entries_in_use", cdt.DoubleLongUnsigned, 0, default=0, classifier=Classifier.DYNAMIC),
                  ICAElement(8, "profile_entries", cdt.DoubleLongUnsigned, 1, default=1))
    M_ELEMENTS = (
        ver0.ProfileGeneric.getMElement(1).unwrap(),
        ver0.ProfileGeneric.getMElement(2).unwrap())
    buffer: Optional[cdt.Array]
    capture_objects: Optional[CaptureObjects]
    sort_method: Optional[ver0.SortMethod]
    sort_object: Optional[structs.CaptureObjectDefinition]

    def characteristics_init(self):
        self.set_attr(ver0.BUFFER, None)

        # todo remove it
        self.buffer.register_cb_preset(lambda _: self.__create_buffer_struct_type())  # value not used for creating struct type

        self._cbs_attr_post_init.update({ver0.CAPTURE_OBJECTS: self.__create_buffer_struct_type,
                                         ver0.SORT_OBJECT: self.__create_selective_access_descriptor})

        self.buffer_capture_objects = self.capture_objects
        """ objects for buffer. Change with access_selection """

    # def get_attr_descriptor(self,
    #                         i: int,
    #                         with_selection: bool = False) -> ut.CosemAttributeDescriptor | ut.CosemAttributeDescriptorWithSelection:
    #     """ with selection for object_list. TODO: Copypast AssociationLN"""
    #     descriptor: ut.CosemAttributeDescriptor = super(ProfileGeneric, self).get_attr_descriptor(i)
    #     if value == ver0.BUFFER and with_selection:
    #         if self.attr_descriptor_with_selection is None:
    #             self.__create_selective_access_descriptor()
    #         return self.attr_descriptor_with_selection((descriptor.contents, self.buffer.selective_access.contents))
    #     else:
    #         return descriptor

    def __create_buffer_struct_type(self):
        """ TODO: more refactoring !!! """
        # rename CaptureObjectDefinition's and adding object if it absense in collection
        if self.buffer.selective_access is None:
            self.__create_selective_access_descriptor()
        if self.capture_objects is None:
            raise ValueError(F"{self}: create buffer Struct type, not set <capture_object> attribute. Need initiate <capture_objects> before")
        for el_value in self.capture_objects:
            el_value: structs.CaptureObjectDefinition
            obj = self.collection.add_if_missing(class_id=ut.CosemClassId(el_value.class_id.contents),
                                                 version=None,
                                                 logical_name=el_value.logical_name)
            el_value.set_name(self.collection.get_name_and_type(el_value)[0][-1])
        match self.buffer.selective_access:
            case ut.SelectiveAccessDescriptor() as desc:
                match int(desc.access_selector):
                    # case 0:                                                 self.buffer_capture_objects = self.capture_objects
                    case 1 if len(desc.access_parameters.selected_values) == 0: self.buffer_capture_objects = self.capture_objects
                    case 1:                                                     self.buffer_capture_objects = desc.access_parameters.selected_values
                    case 2:
                        from_selected_value = int(desc.access_parameters.from_selected_value)-1
                        to_selected_value = int(desc.access_parameters.to_selected_value)
                        if to_selected_value == 0:
                            to_selected_value = len(self.capture_objects)
                        self.buffer_capture_objects = self.capture_objects[from_selected_value:to_selected_value]
                    case _ as err:                                                raise ValueError(F'access_selection out of range, got {err}, must be (0..2)')
            case None:
                self.clear_attr(ver0.CAPTURE_OBJECTS)
                self._cbs_attr_post_init[ver0.CAPTURE_OBJECTS] = self.__create_buffer_struct_type
                raise exc.EmptyObj(F"need set <sort_object> before for {self}")
        buffer_elements: list[cdt.StructElement] = list()
        for el_value in self.buffer_capture_objects:
            names, type_ = self.collection.get_name_and_type(el_value)
            buffer_elements.append(cdt.StructElement(NAME=". ".join(names), TYPE=type_))

        class Entry(cdt.Structure):
            """4.3.6 Profile generic: entry"""
            ELEMENTS = tuple(buffer_elements)

        self.buffer.set_type(Entry)

    def __create_selective_access_descriptor(self):
        """ Available after got sort object. TODO: need rewrite. maybe replace to collection level. Wrong used sort_obj, it can be any element from capture_objects"""
        if self.sort_object is None:
            raise exc.EmptyObj(F"<sort object> is empty")
        sort_obj: ic.COSEMInterfaceClasses = self.collection.get_object(self.sort_object.logical_name)
        if sort_obj.CLASS_ID.contents == self.sort_object.class_id.contents:
            value_type: Type[cdt.CommonDataType] = sort_obj.get_attr_data_type(int(self.sort_object.attribute_index))
        else:
            exc.NoObject(F"got {self.sort_object.class_id=}, expected {sort_obj.CLASS_ID=} from collection")

        class RangeDescriptor(cdt.Structure):
            # cb_preset = TODO: make check 'selected_values' from self.capture_objects or
            # cb_post_set = TODO: make check 'selected_values' from self.capture_objects
            DEFAULT = b'\x02\x04\x02\x04\x12\x00\x01\x09\x06\x00\x00\x01\x00\x00\xff\x0f\x02\x12\x00\x00\x09\x0c\x07\xe4\x01\x01\xff\xff\xff\xff\xff\x80\x00\xff' \
                      b'\x09\x0c\x07\xe4\x01\x02\xff\xff\xff\xff\xff\x80\x00\xff\x01\x00'
            restricting_object: structs.CaptureObjectDefinition
            from_value: value_type
            to_value: value_type
            selected_values: CaptureObjects

        class Data(ut.Data):
            restricting_object: structs.CaptureObjectDefinition
            from_value: cdt.SimpleDataType
            to_value: cdt.SimpleDataType
            selected_values: CaptureObjects
            from_entry: FromEntry
            to_entry: cdt.DoubleLongUnsigned
            from_selected_value: cdt.LongUnsigned
            to_selected_value: cdt.LongUnsigned
            ELEMENTS = {1: ut.SequenceElement('range_descriptor', RangeDescriptor),
                        2: ut.SequenceElement('entry_descriptor', EntryDescriptor)}

        class SelectiveAccessDescriptor(ut.SelectiveAccessDescriptor):
            access_selector: AccessSelector
            access_parameters: Data
            ELEMENTS = (ut.SequenceElement('access_selector', AccessSelector),
                        ut.SequenceElement('access_parameters', Data))

        class CosemAttributeDescriptorWithSelection(ut.CosemAttributeDescriptorWithSelection):
            access_selection: SelectiveAccessDescriptor
            ELEMENTS = (ut.SequenceElement('cosem_attribute_descriptor', ut.CosemAttributeDescriptor),
                        ut.SequenceElement('access_selection', SelectiveAccessDescriptor))

        self.attr_descriptor_with_selection = CosemAttributeDescriptorWithSelection
        self.buffer.selective_access = SelectiveAccessDescriptor()

    def get_capture_object_names(self) -> list[str]:
        """ return all capture object names from collection """
        if self.capture_objects is None:
            raise ValueError(F'{self}: Empty capture objects')
        else:
            definition: structs.CaptureObjectDefinition
            ret = list()
            for definition in self.capture_objects:
                ret.append(get_name(definition.logical_name))
            return ret

    def get_buffer_objects(self) -> list[cosem_interface_classes.cosem_interface_class.IC]:
        """ get objects of current buffer container """
        return [self.collection.get(obj_def.logical_name.contents) for obj_def in self.buffer_capture_objects]

    # todo remove it
    def get_index_with_attributes(self, in_init_order: bool = False) -> Iterator[tuple[int, cdt.CommonDataType | None]]:
        """ override common method """
        return iter(((1, self.logical_name),
                    (6, self.sort_object),
                    (3, self.capture_objects),
                    (2, self.buffer),
                    (4, self.capture_period),
                    (5, self.sort_method),
                    (7, self.entries_in_use),
                    (8, self.profile_entries)))

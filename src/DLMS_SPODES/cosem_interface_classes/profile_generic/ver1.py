from __future__ import annotations
from abc import ABC, abstractmethod
from typing import Type
from ... import cosem_interface_classes
from ..register import Register
from ..clock import Clock
from ...relation_to_OBIS import get_name
from ... import ITE_exceptions as exc
from ..__class_init__ import *
from ...types.implementations import integers, arrays, structs

BUFFER = 2
CAPTURE_OBJECTS = 3
CAPTURE_PERIOD = 4
SORT_METHOD = 5
SORT_OBJECT = 6
ENTRIES_IN_USE = 7
PROFILE_ENTRIES = 8


class SortMethod(cdt.Enum):
    """ If the profile is unsorted, it works as a “first in first out” buffer (it is hence sorted by capturing, and not necessarily by the time
    maintained in the clock object). If the buffer is full, the next call to capture () will push out the first (oldest) entry of the buffer to make
    space for the new entry. If the profile is sorted, a call to capture () will store the new entry at the appropriate position in the buffer, moving
    all following entries and probably losing the least interesting entry. If the new entry would enter the buffer after the last entry and if the
    buffer is already full, the new entry will not be retained at all. """
    ELEMENTS = {b'\x01': en.FIFO,
                b'\x02': en.LIFO,
                b'\x03': en.LARGEST,
                b'\x04': en.SMALLEST,
                b'\x05': en.NEAREST_TO_ZERO,
                b'\x06': en.FAREST_FROM_ZERO}


class CaptureObjects(cdt.Array):
    """ Specifies the list of capture objects """
    TYPE = structs.CaptureObjectDefinition


class FromEntry(cdt.DoubleLongUnsigned):
    """ Access selector value for selective access to the object_list attribute """
    NAME = F'{cdt.tn.DOUBLE_LONG_UNSIGNED}(1..)'

    def validate(self):
        if int.from_bytes(self.contents, 'big') < 0x01:
            raise ValueError(F'Length of {self.__class__.__name__} must be 1, but got {self.contents.hex()}')


class EntryDescriptor(cdt.Structure):
    """ Only buffer elements corresponding to the entry_descriptor shall be returned in the response.
    NOTE: from_entry and to_entry identify the lines, from_selected_value to_selected_value identify the columns of the buffer to be retrieved. """
    values: tuple[FromEntry, cdt.DoubleLongUnsigned, cdt.LongUnsigned, cdt.LongUnsigned]
    default = (1, 0, 1, 0)
    ELEMENTS = (cdt.StructElement(cdt.se.FROM_ENTRY, FromEntry),
                cdt.StructElement(cdt.se.TO_ENTRY,  cdt.DoubleLongUnsigned),
                cdt.StructElement(cdt.se.FROM_SELECTED_VALUE, cdt.LongUnsigned),
                cdt.StructElement(cdt.se.TO_SELECTED_VALUE, cdt.LongUnsigned))

    @property
    def from_entry(self) -> FromEntry:
        """first entry to retrieve. TODO: make type from 1"""
        return self.values[0]

    @property
    def to_entry(self) ->  cdt.DoubleLongUnsigned:
        """last entry to retrieve to_entry == 0: highest possible entry"""
        return self.values[1]

    # index of first value to retrieve
    @property
    def from_selected_value(self) -> cdt.LongUnsigned:
        return self.values[2]

    @property
    def to_selected_value(self) -> cdt.LongUnsigned:
        """index of last value to retrieve to_selected_value == 0: highest possible selected_value"""
        return self.values[3]


class AccessSelector(ut.Unsigned8):
    """ Unsigned8 1..2. Default is 2 for read all buffer """
    def __init__(self, value: int | str | ut.Unsigned8 = 2):
        super(AccessSelector, self).__init__(value)
        if int(self) not in (1, 2):
            raise ValueError(F'The {self.__class__.__name__} got {int(self)}, expected 1..2')


class RangeDescriptorBase(cdt.Structure, ABC):
    """ Only buffer elements corresponding to the range_descriptor shall be returned in the response """
    values: tuple[structs.CaptureObjectDefinition, cdt.SimpleDataType, cdt.SimpleDataType, CaptureObjects]
    # cb_preset = TODO: make check 'selected_values' from self.capture_objects or
    # cb_post_set = TODO: make check 'selected_values' from self.capture_objects
    default = b'\x02\x04\x02\x04\x12\x00\x01\x09\x06\x00\x00\x01\x00\x00\xff\x0f\x02\x12\x00\x00\x09\x0c\x07\xe4\x01\x01\xff\xff\xff\xff\xff\x80\x00\xff' \
              b'\x09\x0c\x07\xe4\x01\x02\xff\xff\xff\xff\xff\x80\x00\xff\x01\x00'

    @abstractmethod
    def ELEMENTS(self) -> tuple[cdt.StructElement, ...]:
        """need definite in subclasses"""

    @property
    def restricting_object(self) -> structs.CaptureObjectDefinition:
        """Defines the capture_object restricting the range of entries to be retrieved. Only simple data types are allowed"""
        return self.values[0]

    @property
    def from_value(self) -> cdt.SimpleDataType:
        """Oldest or smallest entry to retrieve"""
        return self.values[1]

    @property
    def to_value(self) -> cdt.SimpleDataType:
        """Newest or largest entry to retrieve"""
        return self.values[2]

    @property
    def selected_values(self) -> CaptureObjects:
        """List of columns to retrieve. If the array is empty (has no entries), all captured data are returned. Otherwise, only the columns specified in
        the array are returned. The type capture_object_definition is specified above (capture_objects)"""
        return self.values[3]


class DataBase(ut.Data, ABC):
    restricting_object: structs.CaptureObjectDefinition
    from_value: cdt.SimpleDataType
    to_value: cdt.SimpleDataType
    selected_values: CaptureObjects
    from_entry: FromEntry
    to_entry:  cdt.DoubleLongUnsigned
    from_selected_value: cdt.LongUnsigned
    to_selected_value: cdt.LongUnsigned
    ELEMENTS = {1: ut.SequenceElement('range_descriptor', RangeDescriptorBase),
                2: ut.SequenceElement('entry_descriptor', EntryDescriptor)}


class SelectiveAccessDescriptorBase(ut.SelectiveAccessDescriptor, ABC):
    access_selector: AccessSelector
    access_parameters: DataBase
    ELEMENTS = (ut.SequenceElement('access_selector', AccessSelector),
                ut.SequenceElement('access_parameters', DataBase))


class ProfileGeneric(ic.COSEMInterfaceClasses):
    """ The “Profile generic” class defines a generalized concept to store dynamic process values of capture objects. Capture objects are appropriate
    attributes or element of (an) attribute(s) of COSEM objects. The capture objects are collected periodically or occasionally.
    A profile has a buffer to store the captured data. To retrieve only a part of the buffer, either a value range or an entry range may be specified,
    asking to retrieve all entries whose values or entry numbers fall within the given range.
    The list of capture objects defines the values to be stored in the buffer (using the method capture). The list is defined statically to ensure
    homogenous buffer entries (all entries have the same size and structure). If the list of capture objects is modified, the buffer is cleared. If
    the buffer is captured by other “Profile generic” objects, their buffer is cleared as well, to guarantee the homogeneity of their buffer entries.
    The buffer may be defined as sorted by one of the registers or by a clock, or the entries are stacked in a “last in first out” order. So for
    example, it is very easy to build a “maximum demand register” with a one entry deep sorted profile capturing and sorted by a demand register.
    It is just as simple to define a profile retaining the three largest values of some period.
    The size of profile data is determined by three parameters:
        a) the number of entries filled. This will be zero after clearing the profile;
        b) the maximum number of entries to retain. If all entries are filled and a capture () request occurs, the least important entry(according to
           the requested sorting method) will get lost.This maximum number of entries may be specified. Upon changing it, the buffer will be adjusted;
        c) the physical limit for the buffer. This limit typically depends on the objects to capture. The object will reject an attempt of setting
        the maximum number of entries that is larger than physically possible. """
    NAME = cn.PROFILE_GENERIC
    CLASS_ID = ClassID.PROFILE_GENERIC
    VERSION = Version.V1
    scaler_profile_key: bytes | None
    __buffer_capture_objects: CaptureObjects
    range_descriptor: Type[cdt.Structure] = None
    attr_descriptor_with_selection: Type[ut.CosemAttributeDescriptorWithSelection] = None
    A_ELEMENTS = (ic.ICAElement(an.BUFFER, arrays.SelectionAccess, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement(an.CAPTURE_OBJECTS, CaptureObjects),
                  ic.ICAElement(an.CAPTURE_PERIOD, cdt.DoubleLongUnsigned),
                  ic.ICAElement(an.SORT_METHOD, SortMethod),
                  ic.ICAElement(an.SORT_OBJECT, structs.CaptureObjectDefinition),
                  ic.ICAElement(an.ENTRIES_IN_USE, cdt.DoubleLongUnsigned, 0, default=0, classifier=ic.Classifier.DYNAMIC),
                  ic.ICAElement(an.PROFILE_ENTRIES, cdt.DoubleLongUnsigned, 1, default=1))
    M_ELEMENTS = (ic.ICMElement(mn.RESET, integers.Only0),
                  ic.ICMElement(mn.CAPTURE, integers.Only0))

    def characteristics_init(self):
        self.scaler_profile_key = None
        """ obis of scaler profile for this profile if need """

        self.set_attr(BUFFER, None)
        self.buffer.register_cb_preset(lambda _: self.__create_buffer_struct_type())  # value not used for creating struct type

        self._cbs_attr_post_init.update({CAPTURE_OBJECTS: self.__create_buffer_struct_type,
                                         SORT_OBJECT: self.__create_range_descriptor})

        self.__buffer_capture_objects = self.capture_objects
        """ objects for buffer. Change with access_selection """

    @property
    def buffer(self) -> arrays.SelectionAccess:
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
    def sort_object(self) -> structs.CaptureObjectDefinition:
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

    def get_attr_descriptor(self, value: int) -> ut.CosemAttributeDescriptor | ut.CosemAttributeDescriptorWithSelection:
        """ with selection for object_list. TODO: Copypast AssociationLN"""
        descriptor: ut.CosemAttributeDescriptor = super(ProfileGeneric, self).get_attr_descriptor(value)
        if value == BUFFER and bool(self.collection.current_association.xDLMS_context_info.conformance.decode()[21]):
            return self.attr_descriptor_with_selection((descriptor, self.buffer.selective_access))
        else:
            return descriptor

    def __create_buffer_struct_type(self):
        """ TODO: more refactoring !!! """
        # rename CaptureObjectDefinition's and adding object if it absense in collection
        for el_value in self.capture_objects:
            el_value: structs.CaptureObjectDefinition
            obj = self.collection.add_if_missing(class_id=ut.CosemClassId(el_value.class_id.contents),
                                                 version=None,
                                                 logical_name=el_value.logical_name)
            self.collection.raise_before(obj, self)
            el_value.set_name(self.collection.get_name_and_type(el_value)[0][-1])
        match self.buffer.selective_access:
            case ut.SelectiveAccessDescriptor() as desc:
                match int(desc.access_selector):
                    # case 0:                                                 self.__buffer_capture_objects = self.capture_objects
                    case 1 if len(desc.access_parameters.selected_values) == 0: self.__buffer_capture_objects = self.capture_objects
                    case 1:                                                     self.__buffer_capture_objects = desc.access_parameters.selected_values
                    case 2:
                        from_selected_value = int(desc.access_parameters.from_selected_value)-1
                        to_selected_value = int(desc.access_parameters.to_selected_value)
                        if to_selected_value == 0:
                            to_selected_value = len(self.capture_objects)
                        self.__buffer_capture_objects = self.capture_objects[from_selected_value:to_selected_value]
                    case _ as err:                                                raise ValueError(F'access_selection out of range, got {err}, must be (0..2)')
            case None:
                self.clear_attr(CAPTURE_OBJECTS)
                self._cbs_attr_post_init[CAPTURE_OBJECTS] = self.__create_buffer_struct_type
                raise exc.EmptyObj('Need set <sort_method> before')
        buffer_elements: list[cdt.StructElement] = list()
        for el_value in self.__buffer_capture_objects:
            names, type_ = self.collection.get_name_and_type(el_value)
            buffer_elements.append(cdt.StructElement(NAME=". ".join(names), TYPE=type_))

        class Entry(cdt.Structure):
            """ The number and the order of the elements of the structure holding the entries is the same as in the definition of the capture_objects.
                The buffer is filled by auto captures or by subsequent calls of the method (capture). The sequence of the entries within the array is ordered
                according to the sort method specified. Default: The buffer is empty after reset.
                REMARK 1 Reading the entire buffer delivers only those entries, which are “in use”.
                REMARK 2 The value of a captured object may be replaced by “null-data” if it can be unambiguously recovered from the previous value
                (e.g. for time: if it can be calculated from the previous value and capture_period; or for a value: if it is equal to the previous value). """
            ELEMENTS = tuple(buffer_elements)

        self.buffer.set_type(Entry)

    def __create_range_descriptor(self):
        """ Available after got sort object """
        sort_obj: ic.COSEMInterfaceClasses = self.collection.get_object(self.sort_object.logical_name)
        if int(sort_obj.CLASS_ID) == self.sort_object.class_id.decode():
            value_type: Type[cdt.CommonDataType] = sort_obj.get_attr_data_type(self.sort_object.attribute_index.decode())
        else:
            exc.NoObject(F'Got {self.sort_object.class_id=}, expected {sort_obj.CLASS_ID=} from collection')

        class RangeDescriptor(RangeDescriptorBase):
            # cb_preset = TODO: make check 'selected_values' from self.capture_objects or
            # cb_post_set = TODO: make check 'selected_values' from self.capture_objects
            default = b'\x02\x04\x02\x04\x12\x00\x01\x09\x06\x00\x00\x01\x00\x00\xff\x0f\x02\x12\x00\x00\x09\x0c\x07\xe4\x01\x01\xff\xff\xff\xff\xff\x80\x00\xff' \
                      b'\x09\x0c\x07\xe4\x01\x02\xff\xff\xff\xff\xff\x80\x00\xff\x01\x00'
            ELEMENTS = (cdt.StructElement(cdt.se.RESTRICTING_OBJECT, structs.CaptureObjectDefinition),
                        cdt.StructElement(cdt.se.FROM_VALUE, value_type),
                        cdt.StructElement(cdt.se.TO_VALUE, value_type),
                        cdt.StructElement(cdt.se.SELECTED_VALUES, CaptureObjects))

        self.range_descriptor = RangeDescriptor
        self.__set_attr_descriptor_with_selection()
        # if self.capture_objects is not None:  # if capture_objects was init before sort_object
        #     self.__create_buffer_struct_type()

    def __set_attr_descriptor_with_selection(self):
        class Data(DataBase):
            ELEMENTS = {1: ut.SequenceElement('range_descriptor', self.range_descriptor),
                        2: ut.SequenceElement('entry_descriptor', EntryDescriptor)}

        class SelectiveAccessDescriptor(SelectiveAccessDescriptorBase):
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
        match self.capture_objects:
            case CaptureObjects(): return list(map(lambda definition: get_name(self.collection.get_object(definition).logical_name), self.capture_objects))
            case _:                raise ValueError(F'{self}: Empty capture objects')

    def get_buffer_objects(self) -> list[cosem_interface_classes.collection.InterfaceClass]:
        """ get objects of current buffer container """
        return [self.collection.get(obj_def.logical_name.contents) for obj_def in self.__buffer_capture_objects]

    # TODO: remove use names created in create_buffer_struct_type
    def get_buffer_elements_names(self) -> list[str]:
        """ get class name + attribute name + unit if possible """
        ret: list[str] = list()
        for capture_obj in self.__buffer_capture_objects:
            try:
                capture_obj: structs.CaptureObjectDefinition
                obj: ic.COSEMInterfaceClasses = self.collection.get_object(capture_obj)  # Attention New API!!! remove after test
                match obj, capture_obj.attribute_index.decode():
                    case Register(), 2: additional = F', {obj.scaler_unit.unit if obj.scaler_unit is not None else "?"}'
                    case Register(), 3: additional = F'. {obj.get_attr_element(3).NAME}'
                    case Clock(), 2:    additional = ''
                    case _, index:      additional = F'. {obj.get_attr_element(index).NAME}'
                ret.append(F'{get_name(obj.logical_name)}{additional}')
            except KeyError:
                ret.append('?')
        return ret

    # TODO: Remove by set it in CaptureObjects.append
    def get_scaler_units_profile(self) -> list[cdt.ScalUnitType | None]:
        """ get container of possibles scalers and units from current or scaler_units profiles """
        result: list[cdt.ScalUnitType | None] = list()
        if isinstance(self.scaler_profile_key, bytes):
            scaler_profile = self.collection.get_object(self.scaler_profile_key)
            if not isinstance(scaler_profile.buffer, cdt.Array):
                raise ValueError(F'Загрузите буфер {scaler_profile}. Должен присутствовать в файле конфигурации')
            if len(scaler_profile.buffer) == 0:
                raise ValueError(F'Buffer of {scaler_profile} is empty')
            else:
                unit_scaler_profile = scaler_profile.buffer[0]
                for scaler_unit, capture_object in zip(unit_scaler_profile, self.capture_objects):
                    for buffer_capture_object in self.__buffer_capture_objects:
                        if capture_object == buffer_capture_object:
                            match scaler_unit:
                                case cdt.ScalUnitType(): result.append(scaler_unit)
                                case _:                  result.append(None)
                            break
        else:
            for definition in self.__buffer_capture_objects:
                definition: structs.CaptureObjectDefinition
                obj = self.collection.get_object(definition)
                match obj, definition.attribute_index.decode():
                    case Register(), 2: result.append(obj.scaler_unit)
                    case _:             result.append(None)
        return result

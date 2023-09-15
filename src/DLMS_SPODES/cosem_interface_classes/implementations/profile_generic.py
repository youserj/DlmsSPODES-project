from ..profile_generic import ver1
from ...types.implementations import structs, enums
from ...types import ut, cdt


class SPODES3ScalesProfile(ver1.ProfileGeneric):
    """Cosem3 Для профилей масштаба"""
    A_ELEMENTS = (
        ver1.ic.ICAElement(
            NAME=ver1.ProfileGeneric.A_ELEMENTS[0].NAME,
            DATA_TYPE=ver1.ProfileGeneric.A_ELEMENTS[0].DATA_TYPE),
        *ver1.ProfileGeneric.A_ELEMENTS[1:])
    """override buffer with STATIC classifier"""


class SPODES3CurrentProfile(ver1.ProfileGeneric):
    """Cosem3 Б.1 Текущие значения"""
    scaler_profile_key = bytes((1, 0, 94, 7, 3, 255))


class SPODES3MonthProfile(ver1.ProfileGeneric):
    """СПОДЭС3 В.4 Параметры ежемесячного профиля"""
    scaler_profile_key = bytes((1, 0, 94, 7, 1, 255))


class SPODES3DailyProfile(ver1.ProfileGeneric):
    """СПОДЭС3 В.3 Параметры ежесуточного профиля"""
    scaler_profile_key = bytes((1, 0, 94, 7, 2, 255))


class SPODES3LoadProfile(ver1.ProfileGeneric):
    """СПОДЭС3 В.2 Параметры профиля нагрузки"""
    scaler_profile_key = bytes((1, 0, 94, 7, 4, 255))


class SPODES3DisplayReadout(ver1.ProfileGeneric):
    """СПОДЭС3 13.12. Настройка индикации"""
    def characteristics_init(self):
        self.set_attr(ver1.BUFFER, None)
        self.buffer.register_cb_preset(lambda _: self.__create_buffer_struct_type())  # value not used for creating struct type

        self._cbs_attr_post_init.update({ver1.CAPTURE_OBJECTS: self.__create_buffer_struct_type})

        self.buffer_capture_objects = self.capture_objects
        """ objects for buffer. Change with access_selection """

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
        self.buffer_capture_objects = self.capture_objects
        buffer_elements: list[cdt.StructElement] = list()
        for el_value in self.buffer_capture_objects:
            names, type_ = self.collection.get_name_and_type(el_value)
            buffer_elements.append(cdt.StructElement(NAME=". ".join(names), TYPE=cdt.Boolean))

        class Entry(cdt.Structure):
            """ The number and the order of the elements of the structure holding the entries is the same as in the definition of the capture_objects.
                The buffer is filled by auto captures or by subsequent calls of the method (capture). The sequence of the entries within the array is ordered
                according to the sort method specified. Default: The buffer is empty after reset.
                REMARK 1 Reading the entire buffer delivers only those entries, which are “in use”.
                REMARK 2 The value of a captured object may be replaced by “null-data” if it can be unambiguously recovered from the previous value
                (e.g. for time: if it can be calculated from the previous value and capture_period; or for a value: if it is equal to the previous value). """
            ELEMENTS = tuple(buffer_elements)

        self.buffer.set_type(Entry)

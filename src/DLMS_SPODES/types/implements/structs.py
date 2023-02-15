""" COMMON Structs """
from types import common_data_types as cdt, cosem_service_types as cst


class ActionItem(cdt.Structure):
    values: tuple[cst.LogicalName, cdt.LongUnsigned]
    ELEMENTS = (cdt.StructElement(cdt.se.SCRIPT_LOGICAL_NAME, cst.LogicalName),
                cdt.StructElement(cdt.se.SCRIPT_SELECTOR, cdt.LongUnsigned))

    @property
    def script_logical_name(self) -> cst.LogicalName:
        return self.values[0]

    @property
    def script_selector(self) -> cdt.LongUnsigned:
        return self.values[1]


class ValueDefinition(cdt.Structure):
    """ Defines an attribute of an object to be monitored. Only attributes with simple data types are allowed. """
    values: tuple[cdt.LongUnsigned, cst.LogicalName, cdt.Integer]
    ELEMENTS = (cdt.StructElement(cdt.se.CLASS_ID, cdt.LongUnsigned),
                cdt.StructElement(cdt.se.LOGICAL_NAME, cst.LogicalName),
                cdt.StructElement(cdt.se.ATTRIBUTE_INDEX, cdt.Integer))

    @property
    def class_id(self) -> cdt.LongUnsigned:
        return self.values[0]

    @property
    def logical_name(self) -> cst.LogicalName:
        return self.values[1]

    @property
    def attribute_index(self) -> cdt.Integer:
        return self.values[2]


class RestrictionByDate(cdt.Structure):
    values: tuple[cst.OctetStringDate, cst.OctetStringDate]
    ELEMENTS = (cdt.StructElement(cdt.se.FROM_DATE, cst.OctetStringDate),
                cdt.StructElement(cdt.se.TO_DATE, cst.OctetStringDate))

    @property
    def from_date(self) -> cst.OctetStringDate:
        return self.values[0]

    @property
    def to_date(self) -> cst.OctetStringDate:
        return self.values[1]


class RestrictionByEntry(cdt.Structure):
    values: tuple[cdt.DoubleLongUnsigned, cdt.DoubleLongUnsigned]
    ELEMENTS = (cdt.StructElement(cdt.se.FROM_ENTRY, cdt.DoubleLongUnsigned),
                cdt.StructElement(cdt.se.TO_ENTRY, cdt.DoubleLongUnsigned))

    @property
    def from_entry(self) -> cdt.DoubleLongUnsigned:
        return self.values[0]

    @property
    def to_entry(self) -> cdt.DoubleLongUnsigned:
        return self.values[1]


class CaptureObjectDefinition(cdt.Structure):
    """ Capture objects that are assigned to the object instance. Upon a call of the capture (data) method or automatically
    in defined intervals, the selected attributes are copied into the buffer of the profile. """
    values: tuple[cdt.LongUnsigned, cst.LogicalName, cdt.Integer, cdt.LongUnsigned]
    default = b'\x02\x04\x12\x00\x08\x09\x06\x00\x00\x01\x00\x00\xff\x0f\x02\x12\x00\x00'
    ELEMENTS = (cdt.StructElement(cdt.se.CLASS_ID, cdt.LongUnsigned),
                cdt.StructElement(cdt.se.LOGICAL_NAME, cst.LogicalName),
                cdt.StructElement(cdt.se.ATTRIBUTE_INDEX, cdt.Integer),
                cdt.StructElement(cdt.se.DATA_INDEX, cdt.LongUnsigned))

    @property
    def class_id(self) -> cdt.LongUnsigned:
        return self.values[0]

    @property
    def logical_name(self) -> cst.LogicalName:
        return self.values[1]

    @property
    def attribute_index(self) -> cdt.Integer:
        """pointer to the attribute within the object. attribute_index 1 refers to the first attribute (i.e. the logical_name), attribute_index 2
        to the 2nd, etc.; attribute_index 0 refers to all public attributes"""
        return self.values[2]

    @property
    def data_index(self) -> cdt.LongUnsigned:
        """pointer selecting a specific element of the attribute. The first element in the attribute structure is identified by data_index 1. If the
        attribute is not a structure, then the data_index has no meaning. If the capture object is the buffer of a profile, then the data_index
        identifies the captured object of the buffer (i.e. the column) of the inner profile. data_index 0: references the whole attribute"""
        return self.values[3]


class WindowElement(cdt.Structure):
    values: tuple[cst.OctetStringDateTime, cst.OctetStringDateTime]
    ELEMENTS = (cdt.StructElement(cdt.se.START_TIME, cst.OctetStringDateTime),
                cdt.StructElement(cdt.se.END_TIME, cst.OctetStringDateTime))

    @property
    def start_time(self) -> cst.OctetStringDateTime:
        return self.values[0]

    @property
    def end_time(self) -> cst.OctetStringDateTime:
        return self.values[1]

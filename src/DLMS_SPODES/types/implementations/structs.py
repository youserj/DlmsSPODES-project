""" COMMON Structs """
from ...types import common_data_types as cdt, cosem_service_types as cst
from . import long_unsigneds


class ActionItem(cdt.Structure):
    script_logical_name: cst.LogicalName
    script_selector: cdt.LongUnsigned


class ValueDefinition(cdt.Structure):
    """ Defines an attribute of an object to be monitored. Only attributes with simple data types are allowed. """
    class_id: long_unsigneds.ClassId
    logical_name: cst.LogicalName
    attribute_index: cdt.Integer


class RestrictionByDate(cdt.Structure):
    from_date: cst.OctetStringDate
    to_date: cst.OctetStringDate


class RestrictionByEntry(cdt.Structure):
    from_entry: cdt.DoubleLongUnsigned
    to_entry: cdt.DoubleLongUnsigned


class CaptureObjectDefinition(cdt.Structure):
    """ Capture objects that are assigned to the object instance. Upon a call of the capture (data) method or automatically
    in defined intervals, the selected attributes are copied into the buffer of the profile. """
    DEFAULT = b'\x02\x04\x12\x00\x08\x09\x06\x00\x00\x01\x00\x00\xff\x0f\x02\x12\x00\x00'
    class_id: long_unsigneds.ClassId
    logical_name: cst.LogicalName
    attribute_index: cdt.Integer
    data_index: cdt.LongUnsigned

    def __hash__(self):
        return int.from_bytes(self.logical_name.contents+self.attribute_index.contents+self.data_index.contents, 'big')


class WindowElement(cdt.Structure):
    start_time: cst.OctetStringDateTime
    end_time: cst.OctetStringDateTime


class AccessRight(cdt.Structure):
    """ TODO: maybe more nested description"""
    attribute_access: cdt.Array
    method_access: cdt.Array


class ObjectListElement(cdt.Structure):
    """common for AssociationLN"""
    class_id: long_unsigneds.ClassId
    version: cdt.Unsigned
    logical_name: cst.LogicalName
    access_rights: AccessRight

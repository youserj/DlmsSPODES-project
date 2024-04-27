from dataclasses import dataclass
from . import useful_types as ut
from . import (
    cosemClassID as classID,
    cosemObjectInstanceId,
)


@dataclass
class New(ut.SEQUENCE):
    """COSEMpdu_GB83 Cosem-Attribute-Descriptor"""
    class_id: classID.CosemClassId
    instance_id: cosemObjectInstanceId.New
    attribute_id: ut.CosemObjectAttributeId


@dataclass
class SelectiveAccessDescriptor(ut.SEQUENCE):
    """COSEMpdu_GB83 Selective-Access-Descriptor"""
    access_selector: ut.Unsigned8
    access_parameters: ut.Data


# @dataclass
# class WithSelection(Base):
#     """COSEMpdu_GB83 Cosem-Attribute-Descriptor-With-Selection"""
#     access_selection:


OBJECT_LIST = New(
    class_id=classID.ASSOCIATION_LN,
    instance_id=cosemObjectInstanceId.ASSOCIATION_LN0,
    attribute_id=ut.CosemObjectAttributeId(2))
LDN_VALUE = New(
    class_id=classID.DATA,
    instance_id=cosemObjectInstanceId.LDN,
    attribute_id=ut.CosemObjectAttributeId(2))



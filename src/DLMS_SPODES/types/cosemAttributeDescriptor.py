from .useful_types import CosemAttributeDescriptor, CosemObjectAttributeId
from . import cosemClassID, cosemObjectAttributeId, cosemObjectInstanceId


OBJECT_LIST = CosemAttributeDescriptor(
    class_id=cosemClassID.ASSOCIATION_LN,
    instance_id=cosemObjectInstanceId.ASSOCIATION_LN0,
    attribute_id=cosemObjectAttributeId.OBJECT_LIST)
LDN_VALUE = CosemAttributeDescriptor(
    class_id=cosemClassID.DATA,
    instance_id=cosemObjectInstanceId.LDN,
    attribute_id=cosemObjectAttributeId.VALUE)

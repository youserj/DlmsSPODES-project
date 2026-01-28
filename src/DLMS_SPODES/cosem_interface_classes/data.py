from ..types import choices
from ..types.type_alias import Attr
from .cosem_interface_class import ICAuto, ICAElement, Classifier
from .Overview import class_id


class Data(ICAuto):
    """4.3.1 Data"""
    CLASS_ID = class_id.DATA
    VERSION = 0
    A_ELEMENTS = ICAElement(2, "value", choices.common_dt, classifier=Classifier.NOT_SPECIFIC),
    value: Attr

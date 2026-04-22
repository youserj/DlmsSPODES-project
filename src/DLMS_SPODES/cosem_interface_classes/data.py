from COSEMpdu import data
from ..types.type_alias import Attr
from .cosem_interface_class import ICAuto, ICAElement, Classifier


class Data(ICAuto):
    """4.3.1 Data"""
    CLASS_ID = 1
    VERSION = 0
    A_ELEMENTS = ICAElement(2, "value", data.Data, classifier=Classifier.NOT_SPECIFIC),
    value: Attr

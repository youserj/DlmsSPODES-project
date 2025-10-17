from ..cosem_interface_class import ICAuto, ICAElement, Classifier, Cardinality
from ..Overview import class_id


class AssociationSN(ICAuto):
    """dummy class"""
    VERSION = 0
    A_ELEMENTS = ()
    M_ELEMENTS = ()
    CLASS_ID = class_id.ASSOCIATION_SN
    CARDINALITY = Cardinality()

    def __new__(cls, *args, **kwargs):
        raise ValueError(F"version: {__name__[-1]} of {cls.__class__.__name__} not support framework")

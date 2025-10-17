from ..cosem_interface_class import ICAElement, ICAuto
from ..Overview import class_id


class PushSetup(ICAuto):
    """dummy class"""
    CLASS_ID = class_id.PUSH_SETUP
    VERSION = 0
    A_ELEMENTS = ()
    M_ELEMENTS = ()

    def __new__(cls, *args, **kwargs):
        raise ValueError(F"version: {__name__[-1]} of {cls.__class__.__name__} not support framework")

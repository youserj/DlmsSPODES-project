from . import ver0
from ..cosem_interface_class import ICAElement, ICAuto
from ..Overview import class_id


class PushSetup(ver0.PushSetup):
    """dummy class"""
    def __new__(cls, *args, **kwargs):
        raise ValueError(F"version: {__name__[-1]} of {cls.__class__.__name__} not support framework")

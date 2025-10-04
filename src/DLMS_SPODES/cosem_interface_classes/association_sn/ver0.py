from ..__class_init__ import *


class AssociationSN(ic.COSEMInterfaceClasses):
    """dummy class"""
    CLASS_ID = ClassID.ASSOCIATION_SN

    def __new__(cls, *args, **kwargs):
        raise ValueError(F"version: {__name__[-1]} of {cls.__class__.__name__} not support framework")

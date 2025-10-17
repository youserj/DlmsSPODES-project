from ..cosem_interface_class import ICAElement, Classifier, ICAuto
from ..Overview import class_id


class IECHDLCSetup(ICAuto):
    CLASS_ID = class_id.IEC_HDLC_SETUP
    A_ELEMENTS = ()
    M_ELEMENTS = ()

    def __new__(cls, *args, **kwargs):
        raise ValueError(F"version: {__name__[-1]} of {cls.__class__.__name__} not support framework")

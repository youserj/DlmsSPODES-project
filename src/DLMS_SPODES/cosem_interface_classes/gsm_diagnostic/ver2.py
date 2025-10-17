from . import ver1


class GSMDiagnostic(ver1.GSMDiagnostic):
    def __new__(cls, *args, **kwargs):
        raise ValueError(F"version: {__name__[-1]} of {cls.__class__.__name__} not support framework")

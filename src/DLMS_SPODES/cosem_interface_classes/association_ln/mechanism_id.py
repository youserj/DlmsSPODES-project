from ...types import cdt


class MechanismIdElement(cdt.Enum, elements=tuple(range(8))):
    TAG = b'\x11'


class ConstantMixin:
    """override raise for set"""
    def set(self, *args, **kwargs):
        raise AttributeError(F"not support <set> for {self.__class__.__name__} constant")


class MechanismIdElementConst(ConstantMixin, MechanismIdElement):
    """"""


NONE = MechanismIdElementConst(0)
LOW = MechanismIdElementConst(1)
HIGH = MechanismIdElementConst(2)
HIGH_MD5 = MechanismIdElementConst(3)
HIGH_SHA1 = MechanismIdElementConst(4)
HIGH_GMAC = MechanismIdElementConst(5)
HIGH_SHA256 = MechanismIdElementConst(6)
HIGH_ECDSA = MechanismIdElementConst(7)

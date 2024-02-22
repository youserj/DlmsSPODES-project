from ...types import cdt


class MechanismIdElement(cdt.Enum, elements=tuple(range(8))):
    TAG = b'\x11'


NONE = MechanismIdElement(0)
LOW = MechanismIdElement(1)
HIGH = MechanismIdElement(2)
HIGH_MD5 = MechanismIdElement(3)
HIGH_SHA1 = MechanismIdElement(4)
HIGH_GMAC = MechanismIdElement(5)
HIGH_SHA256 = MechanismIdElement(6)
HIGH_ECDSA = MechanismIdElement(7)

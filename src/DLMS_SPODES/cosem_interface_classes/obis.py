from typing_extensions import deprecated


@deprecated("use <bytes>")
class OBIS(bytes):
    """bytes[6]"""
    __slots__ = ()

    def validate(self):
        if (length := len(self)) != 6:
            return ValueError(f"got {length=}, expected 6")

    def __str__(self):
        return F"{".".join(map(str, self[:6]))}"


class AssociationLN(OBIS):
    def __new__(cls, e: int):
        return super().__new__(cls, (0, 0, 40, 0, e, 255))


CURRENT_ASSOCIATION = OBIS((0, 0, 40, 0, 0, 255))
PUBLIC_ASSOCIATION = OBIS((0, 0, 40, 0, 1, 255))
LDN = OBIS((0, 0, 42, 0, 0, 255))


# SPODES_3
SPODES3_DISPLAY_MODE = OBIS((0, 0, 96, 4, 1, 255))

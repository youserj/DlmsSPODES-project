from abc import ABC, abstractmethod
from itertools import count


class MediaId(ABC):
    """DLMS UA 1000-1 Ed 14. Table 53 – OBIS code structure and use of value groups. For Group A"""
    _value: tuple[int]
    _inst = None

    @classmethod
    def from_int(cls, value: int):
        match value:
            case 0:     return Abstract()
            case 1:     return Electricity()
            case 4:     return Hca()
            case 5 | 6: return Thermal()
            case 7:     return Gas()
            case 8 | 9: return Water()
            case 15:    return Other()
            case int(): return Reserved(value)
            case _:     raise ValueError(F"can't create {cls.__name__} from {value=}")

    @abstractmethod
    def __eq__(self, other: int):
        """with integer"""

    @abstractmethod
    def __hash__(self):
        """for hashable"""

    def __str__(self):
        return self.__class__.__name__

    def __init_subclass__(cls, **kwargs):
        def init_hash(self) -> int:
            return self.subgroup

        cls.subgroup = next(sub_group_hash)
        setattr(cls, "__hash__", init_hash)


class OneValueMixin:
    _value: int

    def __eq__(self, other: int):
        return True if other == self._value else False

    def __hash__(self):
        return self._value


class TwoValueMixin:
    _value: tuple[int, ...]

    def __eq__(self, other: int):
        return True if other in self._value else False

    def __hash__(self):
        return self._value[0]


class Singleton:
    _inst: MediaId | None

    def __new__(cls, *args, **kwargs):
        if cls._inst:
            return cls._inst
        else:
            return super().__new__(cls)


sub_group_hash = count()


class Abstract(OneValueMixin, MediaId):
    _value = 0
    __slots__ = tuple()


class Electricity(OneValueMixin, MediaId):
    _value = 1
    __slots__ = tuple()


class Hca(OneValueMixin, MediaId):
    _value = 4
    __slots__ = tuple()


class Thermal(TwoValueMixin, MediaId):
    _value = 5, 6
    __slots__ = tuple()


class Gas(OneValueMixin, MediaId):
    _value = 7
    __slots__ = tuple()


class Water(TwoValueMixin, MediaId):
    _value = 8, 9
    __slots__ = tuple()


class Other(OneValueMixin, MediaId):
    _value = 15
    __slots__ = tuple()


class Reserved(OneValueMixin, MediaId):
    __slots__ = ("_value",)

    def __init__(self, value: int):
        self._value = value


ABSTRACT = Abstract()
ELECTRICITY = Electricity()
HCA = Hca()
THERMAL = Thermal()
GAS = Gas()
WATER = Water()
OTHER_MEDIA = Other()

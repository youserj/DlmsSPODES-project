from abc import ABC, abstractmethod


class MediaId(ABC):
    """DLMS UA 1000-1 Ed 14. Table 53 – OBIS code structure and use of value groups. For Group A"""
    _value: tuple[int]
    _inst = None

    @classmethod
    def from_int(cls, value: int):
        match value:
            case 0:     return _Abstract()
            case 1:     return _Electricity()
            case 4:     return _HCA()
            case 5 | 6: return _Thermal()
            case 7:     return _Gas()
            case 8 | 9: return _Water()
            case 15:    return _Other()
            case int(): return _Reserved(value)
            case _:     raise ValueError(F"can't create {cls.__name__} from {value=}")

    @abstractmethod
    def __eq__(self, other: int):
        """with integer"""


class OneValueMixin:
    _value: int

    def __eq__(self, other: int):
        return True if other == self._value else False


class TwoValueMixin:
    _value: tuple[int, ...]

    def __eq__(self, other: int):
        return True if other in self._value else False


class Singleton:
    _inst: MediaId | None

    def __new__(cls, *args, **kwargs):
        if cls._inst:
            return cls._inst
        else:
            return super().__new__(cls)


class _Abstract(OneValueMixin, Singleton, MediaId):
    _value = 0
    __slots__ = tuple()


class _Electricity(OneValueMixin, Singleton, MediaId):
    _value = 1
    __slots__ = tuple()


class _HCA(OneValueMixin, Singleton, MediaId):
    _value = 4
    __slots__ = tuple()


class _Thermal(TwoValueMixin, Singleton, MediaId):
    _value = 5, 6
    __slots__ = tuple()


class _Gas(OneValueMixin, Singleton, MediaId):
    _value = 7
    __slots__ = tuple()


class _Water(TwoValueMixin, Singleton, MediaId):
    _value = 8, 9
    __slots__ = tuple()


class _Other(OneValueMixin, Singleton, MediaId):
    _value = 15
    __slots__ = tuple()


class _Reserved(OneValueMixin, MediaId):
    __slots__ = ("_value",)

    def __init__(self, value: int):
        self._value = value


ABSTRACT = _Abstract()
ELECTRICITY = _Electricity()
HCA = _HCA()
THERMAL = _Thermal()
GAS = _Gas()
WATER = _Water()
OTHER_MEDIA = _Other()

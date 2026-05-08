from typing_extensions import deprecated
from dataclasses import dataclass, field
import numpy as np
from StructResult.result import ValueOrError, Error
from struct import Struct, pack, unpack_from
from typing import Optional, cast, Iterator, Self
import re
from functools import cached_property
from .. import exceptions as exc
from ..types.type_alias import Obis, Attr



_pattern = re.compile("((?:\d{1,3}\.){5}\d{1,3})(?::(m?\d{1,3}))?")
Index = Struct("?B")


@dataclass(frozen=True)
class Parameter:
    """
     Parameter ::= SEQUENCE
     {
        ln          Cosem-Object-Instance-Id
        descriptor  OPTIONAL
    }

    index       Unsigned8
    nest_index  Unsigned16
    piece       Unsigned8

    descriptor :: = CHOICE
    {
        attribute   [0] IMPLICIT Desc
        method      [1] IMPLICIT Desc
    }

    Desc ::= SEQUENCE
    {
        index
        SEQUENCE (SIZE(255)) OF nest_index OPTIONAL
        piece OPTIONAL
    }
    """
    _value: bytes

    def __bytes__(self) -> bytes:
        return self._value

    @classmethod
    def parse(cls, value: str) -> Self:
        """create from string. Only LN, attr/meth type ddd.ddd.ddd.ddd.ddd.ddd:aaa, ex.: 0.0.1.0.0.255 """
        if (res := _pattern.fullmatch(value)) is None:
            raise ValueError(F"in {cls.__name__}.parse got wrong :{value:}")
        groups = iter(res.groups())
        ret = bytes(map(int, next(groups).split(".")))
        if (a := next(groups)) is not None:
            if a.startswith("m"):
                a = a[1:]
                g1 = 256
            else:
                g1 = 0
            ret += (g1 + int(a)).to_bytes(2)
        return cls(ret)

    @cached_property
    def logical_name(self) -> "Parameter":
        return self.get_attr(1)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Parameter):
            return cast("bool", self._value == other._value)
        return NotImplemented

    def __lt__(self, other: "Parameter") -> bool:
        """comparing for sort method"""
        if len(self._value) > len(other._value):
            return True
        else:
            return False

    def __str__(self) -> str:
        if (l := len(self._value)) < 6:
            return "No valid"
        elif l == 7:
            return "No valid Index"
        else:
            res = F"{".".join(map(str, self._value[:6]))}"
        if l > 6:
            res += F":{"m" if self.is_method() else ""}{self.i}"
        if l > 8:
            res += F" {"/".join(map(str, self.elements()))}"
        if self.has_piece():
            res += F"p{self.piece}"
        return res

    def validate(self) -> None:
        if (length := len(self._value)) < 6:
            raise exc.DLMSException(F"Parameter got {length=}, expected at least 6")
        if length == 7:
            raise exc.DLMSException(F"Parameter got wrong index")

    @property
    def has_index(self) -> bool:
        return len(self._value) > 6

    @property
    @deprecated("use obis")
    def ln(self) -> bytes:
        """Logical Name"""
        return self._value[:6]

    def is_method(self) -> bool:
        return self._value[6] == 1

    @property
    def i(self) -> int:
        """attribute or method index"""
        return self._value[7]

    def get_attr(self, i: int) -> Self:
        """get attribute"""
        val = Index.pack(0, i)
        return self.__class__(self._value[:6] + val)

    def get_meth(self, i: int) -> Self:
        """get method"""
        val = Index.pack(1, i)
        return self.__class__(self._value[:6] + val)

    def set_i(self, index: int, is_method: bool = False) -> "Parameter":
        val = Index.pack(is_method, index)
        if len(self._value) == 6:
            tmp = self._value + val
        else:
            tmp_ = bytearray(self._value)
            tmp_[6:8] = val
            tmp = bytes(tmp_)
        return self.__class__(tmp)

    def append_validate(self) -> None:
        if (l := len(self._value)) < 7:
            raise exc.DLMSException(F"Parameter must has index before")
        elif l % 2 != 0:
            raise exc.DLMSException(F"Can't append to Parameter with piece")

    def append(self, index: int) -> "Parameter":
        """add new sequence(array or struct) index element"""
        self.append_validate()
        return self.__class__(self._value + pack(">H", index))

    def extend(self, *indexes: int) -> "Parameter":
        self.append_validate()
        return self.__class__(self._value + pack(F">{len(indexes)}H", *indexes))

    def pop(self) -> tuple[Optional[int], int, "Parameter"]:
        """
        :return piece, last index and parent Parameter
        ex.: Parameter("0.0.0.0.0.0:2 1/1/1 p3") => (1, Parameter("0.0.0.0.0.0:2 1/1"))
        """
        if self.has_piece():
            return self._value[-1], int.from_bytes(self._value[-3:-1]), self.__class__(self._value[:-3])
        else:
            return None, int.from_bytes(self._value[-2:]), self.__class__(self._value[:-2])

    def set_piece(self, index: int) -> "Parameter":
        """add new sequence(array or struct) index element"""
        if len(self._value) >= 7:
            return self.__class__(self._value + pack("B", index))
        else:
            raise exc.DLMSException(F"Parameter must has index before")

    def has_piece(self) -> bool:
        return bool((l := len(self._value)) >= 9 and l % 2 != 0)

    @property
    def piece(self) -> Optional[int]:
        if self.has_piece():
            return self._value[-1]
        return None

    def clear_piece(self) -> "Parameter":
        if self.has_piece():
            return self.__class__(self._value[:-1])
        return self

    def elements(self, start: int = 0) -> Iterator[int]:
        """return: index elements nested in attribute, started with"""
        for i in range(8 + start, 8 + 2 * self.n_elements, 2):
            res = int.from_bytes(self._value[i:i + 2], "big")
            yield res

    def __iter__(self) -> Iterator[int]:
        for it in self._value[:6]:
            yield it
        if self._value[6] == 1:
            yield -self.i
        else:
            yield self.i

    @property
    def last_element(self) -> int:
        """:return last element index"""
        if self.n_elements == 0:
            raise ValueError("Parameter hasn't elements")
        if self.has_piece():
            val = self._value[-3: -1]
        else:
            val = self._value[-2:]
        return int.from_bytes(val, "big")

    @property
    def n_elements(self) -> int:
        """return: amount of elements nested in attribute"""
        return max(0, (len(self._value) - 8) // 2)

    def set(self,
            a: Optional[int] = None,
            b: Optional[int] = None,
            c: Optional[int] = None,
            d: Optional[int] = None,
            e: Optional[int] = None,
            f: Optional[int] = None
            ) -> "Parameter":
        val = bytearray(self._value)
        if a is not None:
            val[0] = a
        if b is not None:
            val[1] = b
        if c is not None:
            val[2] = c
        if d is not None:
            val[3] = d
        if e is not None:
            val[4] = e
        if f is not None:
            val[5] = f
        return self.__class__(bytes(val))

    def __contains__(self, item: "Parameter") -> bool:
        return item._value in self._value

    def __getitem__(self, item: int) -> Optional[int]:
        if self.n_elements > 0:
            return cast(int, unpack_from(">H", self._value, item * 2 + 8)[0])
        else:
            return None

    @property
    def a(self) -> int:
        return self._value[0]

    @property
    def b(self) -> int:
        return self._value[1]

    @property
    def c(self) -> int:
        return self._value[2]

    @property
    def d(self) -> int:
        return self._value[3]

    @property
    def e(self) -> int:
        return self._value[4]

    @property
    def f(self) -> int:
        return self._value[5]

    @property
    def attr(self) -> "Parameter":
        if self.has_index:
            return Parameter(self._value[:8])
        raise exc.DLMSException(F"Parameter must has index before")

    @property
    def obj(self) -> "Parameter":
        return Parameter(self._value[:6])

    @property
    def obis(self) -> Obis:
        return self._value[:6]


def par2Attr(par: Parameter) -> ValueOrError[Attr]:
    if par.has_index:
        return par.obis + par.i.to_bytes()
    return Error.from_e(ValueError(f"{par} hasn't index"))


RANGE64 = bytes(range(65))  # Предвычисленный диапазон 0-64


@dataclass(eq=False, frozen=True)
class ParPattern:
    value: bytes
    positions: tuple[int, ...]
    "7 elements , -1 is SKIP, last element is attribute index if positive and method index else negative"

    def __post_init__(self) -> None:
        if 6 > len(self.positions) > 7:
            raise ValueError(f"positions must have exactly 6 elements, got {len(self.positions)}")

    @classmethod
    def parse(cls, pattern: str) -> "ParPattern":
        """Парсинг строк вида:
        - "a.0.(1,2,3).(0-64).0.f" (6 элементов)
        - "a.0.1.0.0.f:2" (6 элементов + индекс через :)
        - "a.0.1.0.0.f:m2" (6 элементов + метод через :)
        """
        # Разделяем основную часть и индекс
        if ':' in pattern:
            main_part, index_part = pattern.rsplit(':', 1)
            is_method = index_part.startswith('m')
            if is_method:
                index_part = index_part[1:]
        else:
            main_part = pattern
            index_part = None

        # Парсим основную часть (6 элементов)
        parts = main_part.split('.', maxsplit=5)
        if len(parts) < 6:
            parts.extend(['f'] * (6 - len(parts)))  # Дополняем до 6 элементов

        value_parts = []
        positions = []
        current_pos = 0

        for i, part in enumerate(parts[:6]):  # Ровно 6 элементов
            if len(part)==1 and ord(part)==97 + i:  # a-f
                if part=='b':
                    value_parts.append(RANGE64)
                    positions.append(current_pos)
                    current_pos += len(RANGE64)
                else:
                    positions.append(-1)  # SKIP
                continue

            try:
                if part.isdigit():  # Простое число
                    num = int(part)
                    if not 0 <= num <= 255:
                        raise ValueError
                    value_parts.append(bytes([num]))
                    positions.append(current_pos)
                    current_pos += 1
                elif part.startswith(('(', '!(')) and part.endswith(')'):
                    elements = cls._parse_group(part[2 if part.startswith('!(') else 1:-1])
                    if part.startswith('!('):
                        elements = set(range(256)) - elements
                    value_parts.append(bytes(elements))
                    positions.append(current_pos)
                    current_pos += len(value_parts[-1])
                else:
                    raise ValueError
            except ValueError:
                raise ValueError(f"Invalid pattern part: {part} at position {i}")

        # Добавляем индекс (7-й элемент)
        if index_part is not None:
            try:
                index_val = int(index_part)
                if not 0 <= index_val <= 255:
                    raise ValueError
                # Упаковываем: старший бит = is_method, остальные 7 бит = значение
                packed = bytes([(0x80 if is_method else 0) | (index_val & 0x7F)])
                value_parts.append(packed)
                positions.append(current_pos)
            except ValueError:
                raise ValueError(f"Invalid index value: {index_part}")
        else:
            positions.append(-1)  # SKIP для 7-го элемента

        return cls(
            value=b''.join(value_parts),
            positions=tuple(positions)
        )

    @staticmethod
    def _parse_group(group_str: str) -> set[int]:
        """Парсинг групп вида '1,2,3' или '10-20'"""
        elements: set[int] = set()
        for item in group_str.split(','):
            item = item.strip()
            if '-' in item:
                start, end = map(int, item.split('-'))
                elements.update(range(start, end + 1))
            else:
                elements.add(int(item))
        return elements

    # @functools.cache
    def __hash__(self) -> int:
        print("hash")
        hash_parts: list[Optional[bytes]] = []
        for pos in self.positions:
            if pos == -1:
                hash_parts.append(None)
            else:
                hash_parts.append(self.value[pos:pos + 1])
        return hash(tuple(hash_parts))

    def __eq__(self, other: object) -> bool:
        print("eq")
        if not isinstance(other, ParPattern):
            return False

        for i in range(6):
            pos_self = self.positions[i]
            pos_other = other.positions[i]

            # Проверка соответствия схемы позиций
            if (pos_self == -1) != (pos_other == -1):
                return False

            if pos_self != -1:
                # Сравнение значений
                val_self = self.value[pos_self]
                val_other = other.value[pos_other]
                if val_self != val_other:
                    return False
        return True

    def __str__(self) -> str:
        parts = []
        group_chars = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f'}
        for i in range(6):
            pos = self.positions[i]
            if pos == -1:
                parts.append(group_chars[i])
                continue
            if i < 5:
                next_pos = self.positions[i + 1] if self.positions[i + 1] != -1 else len(self.value)
            else:
                next_pos = len(self.value)
            length = next_pos - pos
            val = self.value[pos]
            if (
                i == 1
                and length == 65
                and self.value[pos:pos + 65] == RANGE64
            ):
                parts.append('(0-64)')
                continue
            if length > 1:
                values = list(self.value[pos:next_pos])
                ranges = []
                start = values[0]
                prev = start
                for v in values[1:]:
                    if v != prev + 1:
                        if start == prev:
                            ranges.append(str(start))
                        else:
                            ranges.append(f"{start}-{prev}")
                        start = v
                    prev = v
                if start == prev:
                    ranges.append(str(start))
                else:
                    ranges.append(f"{start}-{prev}")
                if (
                    len(ranges) == 1
                    and '-' in ranges[0]
                ):
                    parts.append(f"({ranges[0]})")
                else:
                    parts.append(f"({','.join(ranges)})")
            else:
                parts.append(str(val))
        return '.'.join(parts)


@dataclass(frozen=True)
class PatternMatcher:
    """Класс для быстрого сопоставления Parameter с ParPattern"""
    patterns: dict['ParPattern', str]
    _masks: list[tuple[tuple[np.ndarray, ...], str]] = field(init=False)

    def __post_init__(self) -> None:
        # Предварительная обработка шаблонов
        masks = []
        for pattern, value in self.patterns.items():
            pattern_masks = []
            for i in range(7):  # Для всех 7 элементов
                if pattern.positions[i]==-1:  # SKIP
                    mask = np.ones(256, dtype=bool)  # Все значения подходят
                else:
                    start = pattern.positions[i]
                    if i < 6:  # Первые 6 элементов (a-f)
                        end = start + 1
                        values = pattern.value[start:end]
                    else:  # 7-й элемент (индекс)
                        end = start + 1
                        values = pattern.value[start:end]
                        # Для методов учитываем старший бит
                        if values[0] & 0x80:
                            values = bytes([values[0] & 0x7F])

                    mask = np.zeros(256, dtype=bool)
                    for v in values:
                        mask[v] = True
                pattern_masks.append(mask)
            masks.append((tuple(pattern_masks), value))
        object.__setattr__(self, '_masks', masks)

    def find_match(self, param: 'Parameter') -> Optional[str]:
        """Находит первое совпадение параметра с шаблоном"""
        param_values = (
            param.a, param.b, param.c, param.d, param.e, param.f,
            param.i if param.has_index else -1
        )

        for masks, value in self._masks:
            match = True
            for i in range(7):
                val = param_values[i]
                if val==-1:  # Нет значения (для 7-го элемента)
                    if masks[i].any():  # Если в шаблоне требуется конкретное значение
                        match = False
                        break
                elif not masks[i][val]:
                    match = False
                    break
            if match:
                return value
        return None


if __name__ == "__main__":
    # Создаем тестовые шаблоны
    patterns = {
        ParPattern.parse("a.0.(1,2,3).(0-64).0.f:2"): "Pattern1",
        ParPattern.parse("a.0.1.0.0.f:m2"): "Pattern2",
        # ... другие шаблоны
    }

    # Создаем матчер
    matcher = PatternMatcher(patterns)

    # Тестовый параметр
    param = Parameter.parse("0.0.1.0.0.255:2")

    # Поиск совпадения
    result = matcher.find_match(param)
    print(f"Found: {result}")  # Выведет "Pattern1"
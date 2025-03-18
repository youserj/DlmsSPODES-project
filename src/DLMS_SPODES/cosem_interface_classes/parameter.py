from dataclasses import dataclass
from struct import Struct, pack, unpack_from
from typing import Self, Optional
from .. import exceptions as exc


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
    value: bytes

    def __bytes__(self):
        return self.value

    def __lt__(self, other: Self):
        """comparing for sort method"""
        if len(self.value) > len(other.value):
            return True
        else:
            return False

    def __str__(self):
        if (l := len(self.value)) < 6:
            return "No valid"
        elif l == 7:
            return "No valid Index"
        else:
            res = F"{".".join(map(str, self.value[:6]))}"
        if l > 6:
            res += F":{"m" if self.is_method() else ""}{self.i}"
        if l > 8:
            res += F" {"/".join(map(str, self.elements()))}"
        if self.has_piece():
            res += F"p{self.piece}"
        return res

    def validate(self):
        if (length := len(self.value)) < 6:
            raise exc.DLMSException(F"Parameter got {length=}, expected at least 6")
        if length == 7:
            raise exc.DLMSException(F"Parameter got wrong index")

    @property
    def has_index(self) -> bool:
        return len(self.value) > 6

    @property
    def ln(self) -> bytes:
        """Logical Name"""
        return self.value[:6]

    def is_method(self) -> bool:
        return self.value[6] == 1

    @property
    def i(self) -> int:
        """attribute or method index"""
        return self.value[7]

    def set_i(self, index: int, is_method: bool = False) -> Self:
        val = Index.pack(is_method, index)
        if len(self.value) == 6:
            tmp = self.value + val
        else:
            tmp = bytearray(self.value)
            tmp[6:8] = val
            tmp = bytes(tmp)
        return self.__class__(tmp)

    def append_validate(self):
        if (l := len(self.value)) < 7:
            raise exc.DLMSException(F"Parameter must has index before")
        elif l % 2 != 0:
            raise exc.DLMSException(F"Can't append to Parameter with piece")

    def append(self, index: int) -> Self:
        """add new sequence(array or struct) index element"""
        self.append_validate()
        return self.__class__(self.value + pack(">H", index))

    def extend(self, *indexes: int):
        self.append_validate()
        return self.__class__(self.value + pack(F">{len(indexes)}H", *indexes))

    def pop(self) -> tuple[Optional[int], int, Self]:
        """
        :return piece, last index and parent Parameter
        ex.: Parameter("0.0.0.0.0.0:2 1/1/1 p3") => (1, Parameter("0.0.0.0.0.0:2 1/1"))
        """
        if self.has_piece():
            return self.value[-1], int.from_bytes(self.value[-3:-1]), self.__class__(self.value[:-3])
        else:
            return None, int.from_bytes(self.value[-2:]), self.__class__(self.value[:-2])

    def set_piece(self, index: int) -> Self:
        """add new sequence(array or struct) index element"""
        if len(self.value) >= 7:
            return self.__class__(self.value + pack("B", index))
        else:
            raise exc.DLMSException(F"Parameter must has index before")

    def has_piece(self) -> bool:
        if (
            (l := len(self.value)) >= 9
            and l % 2 != 0
        ):
            return True
        else:
            return False

    @property
    def piece(self) -> Optional[int]:
        if self.has_piece():
            return self.value[-1]

    def clear_piece(self) -> Self:
        if self.has_piece():
            return self.__class__(self.value[:-1])

    def elements(self, start: int = 0) -> iter:
        """return: index elements nested in attribute, started with"""
        for i in range(8 + start, 8 + 2 * self.n_elements, 2):
            res = int.from_bytes(self.value[i:i+2], "big")
            yield res

    @property
    def last_element(self) -> int:
        """:return last element index"""
        if self.n_elements == 0:
            raise ValueError("Parameter hasn't elements")
        if self.has_piece():
            val = self.value[-3: -1]
        else:
            val = self.value[-2:]
        return int.from_bytes(val, "big")

    @property
    def n_elements(self) -> int:
        """return: amount of elements nested in attribute"""
        return max(0, (len(self.value) - 8) // 2)

    def set(self,
            a: int = None,
            b: int = None,
            c: int = None,
            d: int = None,
            e: int = None,
            f: int = None
            ) -> Self:
        val = bytearray(self.value)
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

    def __contains__(self, item: Self):
        return item.value in self.value

    def __getitem__(self, item) -> Optional[int]:
        if self.n_elements > 0:
            return unpack_from(">H", self.value, item*2 + 8)[0]
        else:
            return None

    @property
    def a(self) -> int:
        return self.value[0]

    @property
    def b(self) -> int:
        return self.value[1]

    @property
    def c(self) -> int:
        return self.value[2]

    @property
    def d(self) -> int:
        return self.value[3]

    @property
    def e(self) -> int:
        return self.value[4]

    @property
    def f(self) -> int:
        return self.value[5]

    @property
    def attr(self) -> Self:
        if self.has_index:
            return Parameter(self.value[:8])
        else:
            raise exc.DLMSException(F"Parameter must has index before")

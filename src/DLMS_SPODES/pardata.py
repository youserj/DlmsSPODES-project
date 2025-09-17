from dataclasses import dataclass
from .cosem_interface_classes.parameter import Parameter
from typing import Optional, Iterator
from .types import cdt


@dataclass(frozen=True)
class ParValues[T]:
    par:  Parameter
    data: T

    def __iter__(self) -> Iterator[Parameter | T]:
        yield self.par
        yield self.data

    def __str__(self):
        return F"{self.par} - {self.data}"


@dataclass(frozen=True)
class ParData(ParValues[cdt.CommonDataType]):
    data: cdt.CommonDataType

from dataclasses import dataclass
from .cosem_interface_classes import Parameter
from typing import Optional, Iterator
from .types import cdt


@dataclass(frozen=True)
class ParValues[T]:
    par:  Parameter
    data: T

    def __getitem__(self, item):
        if item == 0:
            return self.par
        elif item == 1:
            return self.data
        else:
            raise StopIteration

    def __iter__(self) -> Iterator[Parameter | T]:
        return iter((self.par, self.data))

    def __str__(self):
        return F"{self.par} - {self.data}"


@dataclass(frozen=True)
class ParData(ParValues[cdt.CommonDataType]):
    data: Optional[cdt.CommonDataType]

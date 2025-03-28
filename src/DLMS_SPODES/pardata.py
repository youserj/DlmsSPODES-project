from dataclasses import dataclass
from typing import TypeVar, Generic
from .cosem_interface_classes import Parameter
from .types import cdt

T = TypeVar("T")


@dataclass
class ParValues(Generic[T]):
    par:  Parameter
    data: T

    def __getitem__(self, item):
        if item == 0:
            return self.par
        elif item == 1:
            return self.data
        else:
            raise StopIteration

    def __str__(self):
        return F"{self.par} - {self.data}"


@dataclass
class ParData(ParValues):
    data: cdt.CommonDataType

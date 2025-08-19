from dataclasses import dataclass
from typing import Protocol, ClassVar
from functools import cached_property
from .parameter import Parameter


@dataclass
class Base(Protocol):
    OBIS: Parameter

    @cached_property
    def LN(self) -> Parameter:
        return self.OBIS.set_i(1)


@dataclass
class Data(Base):
    @cached_property
    def VALUE(self) -> Parameter:
        return self.OBIS.set_i(2)

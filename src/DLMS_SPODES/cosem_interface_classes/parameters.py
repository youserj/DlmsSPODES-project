from typing import Protocol, ClassVar
from functools import cached_property
from .parameter import Parameter


class Base(Protocol):
    OBIS: ClassVar[Parameter]

    @cached_property
    def LN(self) -> Parameter:
        return self.OBIS.set_i(1)


class Data(Base, Protocol):

    @cached_property
    def VALUE(self) -> Parameter:
        return self.OBIS.set_i(2)

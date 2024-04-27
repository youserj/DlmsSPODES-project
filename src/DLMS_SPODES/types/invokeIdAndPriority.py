from dataclasses import dataclass
from typing import Self
from .useful_types import Unsigned8
from .serviceClass import ServiceClass
from .priority import Priority


@dataclass
class New(Unsigned8):
    invoke_id: int
    service_class: ServiceClass
    priority: Priority

    @classmethod
    def from_contents(cls, value: bytes) -> Self:
        if cls.LENGTH > len(value):  # todo: copypast from DigitalMixin
            raise ValueError(F"for {cls.__name__} got content length={len(value)}, expected at least {cls.LENGTH}")
        else:
            return cls(
                invoke_id=value[0] & 0b0000_1111,
                service_class=ServiceClass(bool(value[0] & 0b0100_0000)),
                priority=Priority(bool(value[0] & 0b0100_0000)))

    @property
    def contents(self) -> bytes:
        return int(self).to_bytes(1, "big")

    def __str__(self):
        return F"{self.priority} | {self.service_class} | {self.invoke_id}"

    @classmethod
    def from_str(cls, value: str):
        raise RuntimeError(F"for {cls.__name__} not implemented method <from_str>")

    def __int__(self):
        return self.invoke_id + int(self.service_class) + int(self.priority)

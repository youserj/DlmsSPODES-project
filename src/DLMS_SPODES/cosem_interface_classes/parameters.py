from dataclasses import dataclass
from functools import cached_property
from typing import Self
from .parameter import Parameter


@dataclass(frozen=True)
class Data(Parameter):
    @property
    def value(self) -> Parameter:
        return self.get_attr(2)


@dataclass(frozen=True)
class Register(Data):
    @property
    def scaler_unit(self) -> Parameter:
        return self.get_attr(3)


@dataclass(frozen=True)
class DisconnectControl(Parameter):

    @classmethod
    def from_b(cls, b: int) -> "DisconnectControl":
        return cls.parse(f"0.{b}.96.3.10.255")

    @property
    def output_state(self) -> "DisconnectControl":
        return self.get_attr(2)

    @property
    def control_state(self) -> "DisconnectControl":
        return self.get_attr(3)

    @property
    def control_mode(self) -> "DisconnectControl":
        return self.get_attr(4)


DISCONNECT_CONTROL_0 = DisconnectControl.from_b(0)

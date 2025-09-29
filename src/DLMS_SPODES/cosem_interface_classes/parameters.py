from dataclasses import dataclass
from functools import cached_property
from typing import Self
from .parameter import Parameter


@dataclass(frozen=True)
class Data(Parameter):
    @property
    def value(self) -> Parameter:
        return self.get_attr(2)


class ActiveFirmwareIdentifier(Data):

    @classmethod
    def from_b(cls, b: int = 0) -> "ActiveFirmwareIdentifier":
        return cls.parse(f"0.{b}.0.2.0.255")


LDN = Data.parse("0.0.42.0.0.255")
ACTIVE_FIRMWARE_IDENTIFIER_0 = ActiveFirmwareIdentifier.from_b()


@dataclass(frozen=True)
class Register(Data):
    @property
    def scaler_unit(self) -> Parameter:
        return self.get_attr(3)


@dataclass(frozen=True)
class Clock(Parameter):
    @classmethod
    def from_be(cls, b: int = 0, e: int = 0) -> "Clock":
        return cls.parse(f"0.{b}.1.0.{e}.255")

    @property
    def time(self) -> "Clock":
        return self.get_attr(2)

    @property
    def time_zone(self) -> "Clock":
        return self.get_attr(3)

    @property
    def status(self) -> "Clock":
        return self.get_attr(4)

    @property
    def daylight_savings_begin(self) -> "Clock":
        return self.get_attr(5)

    @property
    def daylight_savings_end(self) -> "Clock":
        return self.get_attr(6)

    @property
    def daylight_savings_deviation(self) -> "Clock":
        return self.get_attr(7)

    @property
    def daylight_savings_enabled(self) -> "Clock":
        return self.get_attr(8)

    @property
    def clock_base(self) -> "Clock":
        return self.get_attr(9)

    @property
    def adjust_to_quarter(self) -> "Clock":
        return self.get_meth(1)

    @property
    def adjust_to_measuring_period(self) -> "Clock":
        return self.get_meth(2)

    @property
    def adjust_to_minute(self) -> "Clock":
        return self.get_meth(3)

    @property
    def adjust_to_preset_time(self) -> "Clock":
        return self.get_meth(4)

    @property
    def preset_adjusting_time(self) -> "Clock":
        return self.get_meth(5)

    @property
    def shift_time(self) -> "Clock":
        return self.get_meth(6)


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

    @property
    def remote_disconnect(self) -> "DisconnectControl":
        return self.get_meth(1)

    @property
    def remote_reconnect(self) -> "DisconnectControl":
        return self.get_meth(2)


DISCONNECT_CONTROL_0 = DisconnectControl.from_b(0)


@dataclass(frozen=True)
class ImageTransfer(Parameter):
    @classmethod
    def from_e(cls, e: int = 0) -> "ImageTransfer":
        return cls.parse(f"0.0.44.0.{e}.255")

    @property
    def image_block_size(self) -> "ImageTransfer":
        return self.get_attr(2)

    @property
    def image_transferred_blocks_status(self) -> "ImageTransfer":
        return self.get_attr(3)

    @property
    def image_first_not_transferred_block_number(self) -> "ImageTransfer":
        return self.get_attr(4)

    @property
    def image_transfer_enabled(self) -> "ImageTransfer":
        return self.get_attr(5)

    @property
    def image_transfer_status(self) -> "ImageTransfer":
        return self.get_attr(6)

    @property
    def image_to_activate_info(self) -> "ImageTransfer":
        return self.get_attr(7)

    @property
    def image_transfer_initiate(self) -> "ImageTransfer":
        return self.get_meth(1)

    @property
    def image_block_transfer(self) -> "ImageTransfer":
        return self.get_meth(2)

    @property
    def image_verify(self) -> "ImageTransfer":
        return self.get_meth(3)

    @property
    def image_activate(self) -> "ImageTransfer":
        return self.get_meth(4)


